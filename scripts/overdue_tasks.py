#!/usr/bin/env python3
"""
期限超えタスク通知スクリプト
毎日15:00に期限超えのタスクを通知
"""

import json
import urllib.request
import urllib.error
import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Optional

# 設定
JST = timezone(timedelta(hours=9))
SCRIPTS_PATH = Path(__file__).parent
TOKEN_CACHE_PATH = Path("/tmp/google_tasks_token.json")

sys.path.insert(0, str(SCRIPTS_PATH))


def get_access_token() -> str:
    """トークンを取得"""
    from google_tasks_direct import get_access_token as _get_token
    return _get_token()


def parse_due_date(due_str: str) -> Optional[datetime]:
    """Google Tasksの期限をパース"""
    try:
        if due_str.endswith('Z'):
            due_str = due_str[:-1] + '+00:00'
        dt = datetime.fromisoformat(due_str.replace('Z', '+00:00'))
        return dt.astimezone(JST)
    except:
        return None


def get_overdue_tasks() -> List[Dict]:
    """期限超えの未完了タスクを取得"""
    access_token = get_access_token()
    now = datetime.now(JST)
    
    # タスクリストを取得
    lists_url = "https://tasks.googleapis.com/tasks/v1/users/@me/lists"
    req = urllib.request.Request(lists_url)
    req.add_header('Authorization', f'Bearer {access_token}')
    
    with urllib.request.urlopen(req) as response:
        lists = json.loads(response.read()).get('items', [])
    
    overdue_tasks = []
    
    for task_list in lists:
        list_id = task_list['id']
        list_name = task_list['title']
        
        tasks_url = f"https://tasks.googleapis.com/tasks/v1/lists/{list_id}/tasks"
        req = urllib.request.Request(tasks_url)
        req.add_header('Authorization', f'Bearer {access_token}')
        
        try:
            with urllib.request.urlopen(req) as response:
                tasks = json.loads(response.read()).get('items', [])
                
                for task in tasks:
                    if task.get('status') != 'needsAction':
                        continue
                    
                    due = parse_due_date(task.get('due', ''))
                    if not due:
                        continue
                    
                    # 期限超え
                    if due < now:
                        days_overdue = (now - due).days
                        overdue_tasks.append({
                            'id': task['id'],
                            'title': task.get('title', ''),
                            'notes': task.get('notes', ''),
                            'list_name': list_name,
                            'due': due.strftime('%Y-%m-%d'),
                            'days_overdue': days_overdue,
                        })
        except urllib.error.HTTPError:
            continue
    
    # 超過日数でソート（多い順）
    overdue_tasks.sort(key=lambda x: x['days_overdue'], reverse=True)
    
    return overdue_tasks


def format_overdue_message(tasks: List[Dict]) -> str:
    """うざめのメッセージを生成"""
    if not tasks:
        return ""
    
    lines = []
    
    if len(tasks) == 1:
        lines.append("🚨 **おい、タスク終わってないぞ！！** 🚨\n")
    else:
        lines.append(f"🚨 **{len(tasks)}個もタスク溜まってるぞ！！** 🚨\n")
    
    for t in tasks:
        days = t['days_overdue']
        if days == 0:
            overdue_text = "今日まで！"
        elif days == 1:
            overdue_text = "1日超過 😤"
        elif days <= 3:
            overdue_text = f"{days}日超過 😡"
        else:
            overdue_text = f"{days}日超過 💀やばいって"
        
        lines.append(f"❌ **{t['title']}**")
        lines.append(f"   📁 {t['list_name']} | 期限: {t['due']} ({overdue_text})")
        lines.append("")
    
    lines.append("早く片付けて！🔥")
    
    return "\n".join(lines)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Overdue Tasks Checker")
    parser.add_argument("--check", action="store_true", help="Check and print overdue tasks")
    parser.add_argument("--send", action="store_true", help="Format message for sending")
    args = parser.parse_args()
    
    tasks = get_overdue_tasks()
    
    if args.check:
        if tasks:
            print(f"Found {len(tasks)} overdue task(s):")
            for t in tasks:
                print(f"  - {t['title']} ({t['days_overdue']} days overdue)")
        else:
            print("No overdue tasks! 🎉")
    
    elif args.send:
        if tasks:
            print(format_overdue_message(tasks))
        else:
            print("NO_OVERDUE")
    
    else:
        print(json.dumps(tasks, indent=2, ensure_ascii=False))
