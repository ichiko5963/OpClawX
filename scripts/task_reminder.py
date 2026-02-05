#!/usr/bin/env python3
"""
Google Tasks リマインダースクリプト
期限の3日前、1日前、12時間前にリマインドを送信
"""

import json
import urllib.request
import urllib.error
import os
import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Optional

# 設定
JST = timezone(timedelta(hours=9))
SCRIPTS_PATH = Path(__file__).parent
TOKEN_CACHE_PATH = Path("/tmp/google_tasks_token.json")
REMINDER_STATE_PATH = SCRIPTS_PATH / "reminder_state.json"

# リマインドタイミング（時間単位）
REMINDER_THRESHOLDS = [
    {"hours": 72, "label": "3日前"},
    {"hours": 24, "label": "1日前"},
    {"hours": 12, "label": "12時間前"},
]


def load_reminder_state() -> Dict:
    """リマインダー送信状態を読み込み"""
    if REMINDER_STATE_PATH.exists():
        with open(REMINDER_STATE_PATH) as f:
            return json.load(f)
    return {"sent_reminders": {}}


def save_reminder_state(state: Dict):
    """リマインダー送信状態を保存"""
    with open(REMINDER_STATE_PATH, "w") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


def get_access_token() -> str:
    """トークンを取得（リフレッシュが必要なら実行）"""
    # google_tasks_direct.pyのget_access_token()を使用
    sys.path.insert(0, str(SCRIPTS_PATH))
    from google_tasks_direct import get_access_token as _get_token
    return _get_token()


def get_all_tasks() -> List[Dict]:
    """全リストから未完了タスクを取得"""
    access_token = get_access_token()
    
    # タスクリストを取得
    lists_url = "https://tasks.googleapis.com/tasks/v1/users/@me/lists"
    req = urllib.request.Request(lists_url)
    req.add_header('Authorization', f'Bearer {access_token}')
    
    with urllib.request.urlopen(req) as response:
        lists = json.loads(response.read()).get('items', [])
    
    all_tasks = []
    
    for task_list in lists:
        list_id = task_list['id']
        list_name = task_list['title']
        
        # タスクを取得
        tasks_url = f"https://tasks.googleapis.com/tasks/v1/lists/{list_id}/tasks"
        req = urllib.request.Request(tasks_url)
        req.add_header('Authorization', f'Bearer {access_token}')
        
        try:
            with urllib.request.urlopen(req) as response:
                tasks = json.loads(response.read()).get('items', [])
                
                for task in tasks:
                    # 未完了かつ期限ありのタスクのみ
                    if task.get('status') == 'needsAction' and task.get('due'):
                        task['list_name'] = list_name
                        task['list_id'] = list_id
                        all_tasks.append(task)
        except urllib.error.HTTPError:
            continue
    
    return all_tasks


def parse_due_date(due_str: str) -> Optional[datetime]:
    """Google Tasksの期限をパース（RFC 3339形式）"""
    try:
        # Google Tasksは "2026-02-13T00:00:00.000Z" 形式
        if due_str.endswith('Z'):
            due_str = due_str[:-1] + '+00:00'
        dt = datetime.fromisoformat(due_str.replace('Z', '+00:00'))
        return dt.astimezone(JST)
    except:
        return None


def check_and_send_reminders() -> List[Dict]:
    """期限が近いタスクをチェックしてリマインド対象を返す"""
    now = datetime.now(JST)
    state = load_reminder_state()
    sent = state.get("sent_reminders", {})
    
    tasks = get_all_tasks()
    reminders_to_send = []
    
    for task in tasks:
        task_id = task['id']
        due = parse_due_date(task.get('due', ''))
        
        if not due:
            continue
        
        # 過去の期限はスキップ
        if due < now:
            continue
        
        hours_until_due = (due - now).total_seconds() / 3600
        
        for threshold in REMINDER_THRESHOLDS:
            threshold_hours = threshold['hours']
            threshold_label = threshold['label']
            reminder_key = f"{task_id}_{threshold_hours}"
            
            # まだ送信していない & しきい値を下回っている
            if reminder_key not in sent and hours_until_due <= threshold_hours:
                reminders_to_send.append({
                    "task_id": task_id,
                    "title": task.get('title', ''),
                    "notes": task.get('notes', ''),
                    "list_name": task.get('list_name', ''),
                    "due": due.strftime('%Y-%m-%d %H:%M'),
                    "hours_until": round(hours_until_due, 1),
                    "threshold_label": threshold_label,
                    "reminder_key": reminder_key,
                })
                break  # 一番近いしきい値のみ
    
    return reminders_to_send


def mark_reminder_sent(reminder_key: str):
    """リマインダーを送信済みとしてマーク"""
    state = load_reminder_state()
    state["sent_reminders"][reminder_key] = datetime.now(JST).isoformat()
    save_reminder_state(state)


def format_reminder_message(reminders: List[Dict]) -> str:
    """リマインダーメッセージを整形"""
    if not reminders:
        return ""
    
    lines = ["⏰ **タスクリマインダー**\n"]
    
    for r in reminders:
        lines.append(f"📌 **{r['title']}**")
        lines.append(f"   📁 {r['list_name']}")
        lines.append(f"   ⏳ 期限: {r['due']}（{r['threshold_label']}）")
        if r['notes']:
            lines.append(f"   📝 {r['notes'][:50]}...")
        lines.append("")
    
    return "\n".join(lines)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Google Tasks Reminder")
    parser.add_argument("--check", action="store_true", help="Check and print reminders")
    parser.add_argument("--send", action="store_true", help="Send reminders via stdout (for OpenClaw)")
    parser.add_argument("--reset", action="store_true", help="Reset reminder state")
    args = parser.parse_args()
    
    if args.reset:
        save_reminder_state({"sent_reminders": {}})
        print("Reminder state reset.")
        sys.exit(0)
    
    reminders = check_and_send_reminders()
    
    if args.check:
        if reminders:
            print(f"Found {len(reminders)} reminder(s) to send:")
            for r in reminders:
                print(f"  - {r['title']} ({r['threshold_label']}, due: {r['due']})")
        else:
            print("No reminders to send.")
    
    elif args.send:
        if reminders:
            message = format_reminder_message(reminders)
            print(message)
            
            # 送信済みとしてマーク
            for r in reminders:
                mark_reminder_sent(r['reminder_key'])
        else:
            print("NO_REMINDER")
    
    else:
        # デフォルト: チェックのみ
        print(json.dumps(reminders, indent=2, ensure_ascii=False))
