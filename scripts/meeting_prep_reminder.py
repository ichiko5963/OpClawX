#!/usr/bin/env python3
"""
カレンダー → 準備リマインダー
- MTG 2時間前に通知
- 参加者・議題から準備リスト生成
"""

import json
import re
import os
import sys
import urllib.request
import urllib.parse
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Optional

# 既存のカレンダー関数をインポート
SCRIPTS_PATH = Path(__file__).parent
sys.path.insert(0, str(SCRIPTS_PATH))

from google_calendar_direct import get_access_token as get_calendar_token

# 設定
JST = timezone(timedelta(hours=9))
WORKSPACE = Path("/Users/ai-driven-work/Library/Mobile Documents/com~apple~CloudDocs/OpenClaw-Shared")
OBSIDIAN_PATH = WORKSPACE / "obsidian/Ichioka Obsidian"
PEOPLE_PATH = OBSIDIAN_PATH / "10_People"
COMPANIES_PATH = OBSIDIAN_PATH / "11_Companies"
PROJECTS_PATH = OBSIDIAN_PATH / "03_Projects/_Active"

# リマインダー送信済みを記録
SENT_REMINDERS_PATH = WORKSPACE / "logs/sent_reminders.json"

def get_events(token: str, time_min: str = None, time_max: str = None, max_results: int = 10) -> List[Dict]:
    """イベントを取得"""
    params = [f"maxResults={max_results}", "singleEvents=true", "orderBy=startTime"]
    if time_min:
        params.append(f"timeMin={urllib.parse.quote(time_min)}")
    if time_max:
        params.append(f"timeMax={urllib.parse.quote(time_max)}")
    
    url = f"https://www.googleapis.com/calendar/v3/calendars/primary/events?{'&'.join(params)}"
    
    req = urllib.request.Request(url)
    req.add_header('Authorization', f'Bearer {token}')
    
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read())
            return result.get('items', [])
    except Exception as e:
        print(f"Calendar API error: {e}")
        return []

def load_sent_reminders() -> Dict:
    """送信済みリマインダーを読み込み"""
    try:
        if SENT_REMINDERS_PATH.exists():
            with open(SENT_REMINDERS_PATH, 'r') as f:
                return json.load(f)
    except:
        pass
    return {}

def save_sent_reminders(reminders: Dict):
    """送信済みリマインダーを保存"""
    try:
        SENT_REMINDERS_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(SENT_REMINDERS_PATH, 'w') as f:
            json.dump(reminders, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Save error: {e}")

def get_person_context(name: str) -> Optional[str]:
    """Obsidianから人物情報を取得"""
    try:
        for person_dir in PEOPLE_PATH.iterdir():
            if person_dir.is_dir() and name.lower() in person_dir.name.lower():
                profile = person_dir / "PROFILE.md"
                if profile.exists():
                    with open(profile, 'r') as f:
                        return f.read()[:500]
    except:
        pass
    return None

def get_company_context(name: str) -> Optional[str]:
    """Obsidianから企業情報を取得"""
    try:
        for company_dir in COMPANIES_PATH.iterdir():
            if company_dir.is_dir() and name.lower() in company_dir.name.lower():
                profile = company_dir / "PROFILE.md"
                if profile.exists():
                    with open(profile, 'r') as f:
                        return f.read()[:500]
    except:
        pass
    return None

def get_project_context(event_title: str) -> Optional[str]:
    """イベント名からプロジェクト情報を取得"""
    keywords = {
        "aircle": "AirCle",
        "エアクル": "AirCle",
        "climb": "ClimbBeyond",
        "クライム": "ClimbBeyond",
        "ポート": "ClimbBeyond",
        "genspark": "Genspark",
    }
    
    for keyword, project in keywords.items():
        if keyword.lower() in event_title.lower():
            project_dir = PROJECTS_PATH / project
            memory = project_dir / "MEMORY.md"
            if memory.exists():
                try:
                    with open(memory, 'r') as f:
                        return f.read()[:800]
                except:
                    pass
    return None

def generate_prep_list_with_ai(event: Dict, context: str) -> str:
    """AIで準備リストを生成"""
    openai_key = os.environ.get('OPENAI_API_KEY', '')
    if not openai_key:
        return generate_prep_list_simple(event)
    
    title = event.get('summary', '予定')
    description = event.get('description', '')
    attendees = event.get('attendees', [])
    attendee_names = [a.get('email', '').split('@')[0] for a in attendees]
    
    prompt = f"""以下のミーティングに向けて、いちさん（市岡）が準備すべきことリストを作成してください。

# ミーティング情報
タイトル: {title}
参加者: {', '.join(attendee_names)}
説明: {description[:500]}

# 関連情報
{context}

# 出力形式
箇条書きで3-5個、具体的なアクション。
例:
- 〇〇の資料を準備
- 〇〇について確認しておく
- 〇〇さんへの質問を整理"""

    body = json.dumps({
        "model": "gpt-4o",
        "messages": [
            {"role": "system", "content": "You are a meeting preparation assistant. Be concise and actionable."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 300,
        "temperature": 0.7
    }).encode()
    
    req = urllib.request.Request(
        'https://api.openai.com/v1/chat/completions',
        data=body, method='POST'
    )
    req.add_header('Authorization', f'Bearer {openai_key}')
    req.add_header('Content-Type', 'application/json')
    
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            result = json.loads(r.read())
            return result['choices'][0]['message']['content']
    except Exception as e:
        print(f"AI error: {e}")
        return generate_prep_list_simple(event)

def generate_prep_list_simple(event: Dict) -> str:
    """シンプルな準備リスト生成"""
    title = event.get('summary', '予定')
    
    items = [
        "- 議題を確認する",
        "- 前回の議事録があれば読み返す",
        "- 質問・確認事項を整理する",
    ]
    
    if "レビュー" in title or "確認" in title:
        items.append("- 該当資料・成果物を準備する")
    if "企画" in title or "ブレスト" in title:
        items.append("- アイデアをメモしておく")
    if "定例" in title:
        items.append("- 進捗状況をまとめる")
    
    return "\n".join(items)

def get_upcoming_meetings(hours_ahead: float = 2.5) -> List[Dict]:
    """指定時間内に始まるミーティングを取得"""
    token = get_calendar_token()
    if not token:
        return []
    
    now = datetime.now(JST)
    time_min = now.isoformat()
    time_max = (now + timedelta(hours=hours_ahead)).isoformat()
    
    events = get_events(token, time_min=time_min, time_max=time_max, max_results=10)
    
    upcoming = []
    for event in events:
        start_str = event.get('start', {}).get('dateTime')
        if not start_str:
            continue
        
        start = datetime.fromisoformat(start_str.replace('Z', '+00:00'))
        time_until = (start - now).total_seconds() / 60
        
        # 90分〜150分前（2時間前後）
        if 90 <= time_until <= 150:
            event['time_until_minutes'] = int(time_until)
            upcoming.append(event)
    
    return upcoming

def create_reminder(event: Dict) -> Dict:
    """ミーティング準備リマインダーを作成"""
    title = event.get('summary', '予定')
    start_str = event.get('start', {}).get('dateTime', '')
    attendees = event.get('attendees', [])
    location = event.get('location', '')
    hangout_link = event.get('hangoutLink', '')
    
    context_parts = []
    
    project_ctx = get_project_context(title)
    if project_ctx:
        context_parts.append(project_ctx)
    
    for attendee in attendees[:3]:
        email = attendee.get('email', '')
        name = email.split('@')[0]
        person_ctx = get_person_context(name)
        if person_ctx:
            context_parts.append(f"【{name}】\n{person_ctx}")
    
    context = "\n\n".join(context_parts)
    
    prep_list = generate_prep_list_with_ai(event, context)
    
    if start_str:
        start = datetime.fromisoformat(start_str.replace('Z', '+00:00'))
        start_formatted = start.astimezone(JST).strftime("%H:%M")
    else:
        start_formatted = "?"
    
    attendee_names = []
    for a in attendees[:5]:
        email = a.get('email', '')
        if 'ichioka' not in email.lower() and 'naoto' not in email.lower():
            attendee_names.append(email.split('@')[0])
    
    meeting_link = hangout_link or location or ""
    
    return {
        'event_id': event.get('id'),
        'title': title,
        'start_time': start_formatted,
        'attendees': attendee_names,
        'meeting_link': meeting_link,
        'prep_list': prep_list,
        'minutes_until': event.get('time_until_minutes', 120)
    }

def format_reminder_for_telegram(reminder: Dict) -> str:
    """リマインダーをTelegram用にフォーマット"""
    lines = [
        f"⏰ **{reminder['title']}** @ {reminder['start_time']}",
        f"（約{reminder['minutes_until']}分後）",
        "",
    ]
    
    if reminder['attendees']:
        lines.append(f"👥 参加者: {', '.join(reminder['attendees'][:5])}")
    
    if reminder['meeting_link']:
        lines.append(f"🔗 {reminder['meeting_link']}")
    
    lines.append("")
    lines.append("**📋 準備リスト**")
    lines.append(reminder['prep_list'])
    
    return "\n".join(lines)

def check_and_send_reminders(dry_run: bool = False) -> Dict:
    """リマインダーをチェックして送信"""
    upcoming = get_upcoming_meetings(hours_ahead=2.5)
    
    if not upcoming:
        return {"status": "no_meetings", "message": "2時間以内に始まるミーティングはありません"}
    
    sent = load_sent_reminders()
    today = datetime.now(JST).strftime("%Y-%m-%d")
    
    today_sent = sent.get(today, [])
    
    reminders = []
    for event in upcoming:
        event_id = event.get('id')
        
        if event_id in today_sent:
            continue
        
        reminder = create_reminder(event)
        reminders.append(reminder)
        
        if not dry_run:
            today_sent.append(event_id)
    
    if not dry_run and reminders:
        sent[today] = today_sent
        cutoff = (datetime.now(JST) - timedelta(days=7)).strftime("%Y-%m-%d")
        sent = {k: v for k, v in sent.items() if k >= cutoff}
        save_sent_reminders(sent)
    
    return {
        "status": "success" if reminders else "no_new",
        "count": len(reminders),
        "reminders": reminders
    }

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='カレンダー準備リマインダー')
    parser.add_argument('--check', action='store_true', help='リマインダーをチェック')
    parser.add_argument('--dry-run', action='store_true', help='送信せずに確認のみ')
    parser.add_argument('--force', action='store_true', help='送信済みを無視して再送信')
    
    args = parser.parse_args()
    
    if args.check:
        if args.force:
            save_sent_reminders({})
        
        result = check_and_send_reminders(dry_run=args.dry_run)
        
        if result['status'] == 'no_meetings':
            print("2時間以内に始まるミーティングはありません")
        elif result['status'] == 'no_new':
            print("新しいリマインダーはありません（既に送信済み）")
        else:
            for reminder in result['reminders']:
                print("\n" + "="*50)
                print(format_reminder_for_telegram(reminder))
                print("="*50)
    else:
        parser.print_help()
