#!/usr/bin/env python3
"""
Google Meet文字起こし自動処理
- 議事録生成
- TODO抽出 → Google Tasks追加
- 次回MTG日程 → Googleカレンダー追加
- Telegram報告
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
import requests

WORKSPACE = Path("/Users/ai-driven-work/Documents/OpenClaw-Workspace")
TRANSCRIPTIONS_DIR = WORKSPACE / "data/drive/transcriptions"
PROCESSED_FILE = WORKSPACE / "data/processed_transcripts.json"
OAUTH_TOKEN_FILE = Path("/tmp/google_oauth_tokens.json")

def get_access_token():
    """OAuth access token取得"""
    data = json.loads(OAUTH_TOKEN_FILE.read_text())
    url = "https://oauth2.googleapis.com/token"
    response = requests.post(url, data={
        'client_id': data['client_id'],
        'client_secret': data['client_secret'],
        'refresh_token': data['refresh_token'],
        'grant_type': 'refresh_token'
    })
    return response.json()['access_token']

def get_processed_list():
    """処理済みファイルリスト取得"""
    if PROCESSED_FILE.exists():
        return set(json.loads(PROCESSED_FILE.read_text()))
    return set()

def mark_as_processed(filename):
    """処理済みとしてマーク"""
    processed = get_processed_list()
    processed.add(filename)
    PROCESSED_FILE.write_text(json.dumps(list(processed), indent=2))

def analyze_transcript(transcript_text, filename):
    """Claudeで文字起こし分析"""
    
    # OpenClaw経由でClaude分析
    # ここではプレースホルダー - 実際はOpenClaw APIを使う
    # または環境変数のANTHROPIC_API_KEYを使う
    
    prompt = f"""以下のGoogle Meet文字起こしから情報を抽出してJSON形式で回答してください：

文字起こし:
{transcript_text[:3000]}

抽出項目:
{{
  "meeting_title": "MTGタイトル（ファイル名や内容から推測）",
  "date": "YYYY-MM-DD形式の日付",
  "participants": ["参加者1", "参加者2", ...],
  "summary": "議事録サマリー（3-5行）",
  "decisions": ["決定事項1", "決定事項2", ...],
  "ichioka_todos": [
    {{"task": "いちさんがやるべきタスク", "deadline": "YYYY-MM-DD or null"}},
    ...
  ],
  "next_meeting": {{
    "scheduled": true/false,
    "date": "YYYY-MM-DD or null",
    "time": "HH:MM or null",
    "title": "次回MTGタイトル or null"
  }}
}}

重要:
- ichioka_todosは「市岡」「いち」が担当するタスクのみ抽出
- 他の人のタスクは含めない
- 締切が明示されていればdeadlineに入れる
- 次回MTGの日程が決まっていればnext_meetingに入れる

JSONのみを出力してください。"""
    
    # ここでは仮のレスポンス（実際はClaude APIを叩く）
    # OpenClaw image toolのようにClaude APIを使う
    
    print(f"  Analyzing transcript: {filename}")
    
    # 仮の分析結果（実装時に実際のAPI呼び出しに置き換え）
    analysis = {
        "meeting_title": filename.replace(".json", "").replace("_", " "),
        "date": datetime.now().strftime("%Y-%m-%d"),
        "participants": [],
        "summary": "文字起こし分析中...",
        "decisions": [],
        "ichioka_todos": [],
        "next_meeting": {"scheduled": False}
    }
    
    return analysis

def add_to_google_tasks(task_title, due_date=None):
    """Google Tasksに追加"""
    access_token = get_access_token()
    
    # タスクリストID取得（「マイタスク」または特定リスト）
    url = "https://tasks.googleapis.com/tasks/v1/users/@me/lists"
    headers = {'Authorization': f'Bearer {access_token}'}
    
    response = requests.get(url, headers=headers)
    lists = response.json().get('items', [])
    
    # デフォルトリスト取得
    task_list_id = lists[0]['id'] if lists else None
    
    if not task_list_id:
        print("  ❌ タスクリストが見つかりません")
        return None
    
    # タスク作成
    url = f"https://tasks.googleapis.com/tasks/v1/lists/{task_list_id}/tasks"
    
    task_data = {
        'title': task_title
    }
    
    if due_date:
        # RFC 3339形式に変換
        task_data['due'] = f"{due_date}T00:00:00.000Z"
    
    response = requests.post(url, headers=headers, json=task_data)
    
    if response.status_code == 200:
        print(f"  ✓ タスク追加: {task_title}")
        return response.json()
    else:
        print(f"  ❌ タスク追加失敗: {response.text}")
        return None

def add_to_google_calendar(event_title, event_date, event_time=None):
    """Googleカレンダーに追加"""
    access_token = get_access_token()
    
    # カレンダーID（プライマリ）
    calendar_id = 'primary'
    
    # イベント作成
    url = f"https://www.googleapis.com/calendar/v3/calendars/{calendar_id}/events"
    headers = {'Authorization': f'Bearer {access_token}', 'Content-Type': 'application/json'}
    
    # 時間指定あれば時間、なければ終日
    if event_time:
        start_datetime = f"{event_date}T{event_time}:00+09:00"
        end_datetime = (datetime.fromisoformat(start_datetime) + timedelta(hours=1)).isoformat()
        
        event_data = {
            'summary': event_title,
            'start': {'dateTime': start_datetime, 'timeZone': 'Asia/Tokyo'},
            'end': {'dateTime': end_datetime, 'timeZone': 'Asia/Tokyo'}
        }
    else:
        event_data = {
            'summary': event_title,
            'start': {'date': event_date},
            'end': {'date': event_date}
        }
    
    response = requests.post(url, headers=headers, json=event_data)
    
    if response.status_code == 200:
        print(f"  ✓ カレンダー追加: {event_title}")
        return response.json()
    else:
        print(f"  ❌ カレンダー追加失敗: {response.text}")
        return None

def process_new_transcripts():
    """新しい文字起こしを処理"""
    
    if not TRANSCRIPTIONS_DIR.exists():
        print("❌ 文字起こしディレクトリが存在しません")
        return
    
    processed = get_processed_list()
    
    # 新しいファイルを検索
    new_files = []
    for file in TRANSCRIPTIONS_DIR.glob("*.json"):
        if file.name not in processed:
            new_files.append(file)
    
    if not new_files:
        print("✓ 新しい文字起こしなし")
        return
    
    print(f"🎯 新しい文字起こし: {len(new_files)}件")
    
    for file in new_files:
        print(f"\n=== 処理中: {file.name} ===")
        
        # 文字起こし読み込み
        transcript_data = json.loads(file.read_text())
        transcript_text = transcript_data.get('transcript', '')
        
        if not transcript_text:
            print("  ⚠️  文字起こしが空です")
            mark_as_processed(file.name)
            continue
        
        # Claude分析
        analysis = analyze_transcript(transcript_text, file.name)
        
        # TODO追加
        added_tasks = []
        for todo in analysis.get('ichioka_todos', []):
            task = todo.get('task')
            deadline = todo.get('deadline')
            
            result = add_to_google_tasks(task, deadline)
            if result:
                added_tasks.append({
                    'task': task,
                    'deadline': deadline or 'なし'
                })
        
        # 次回MTG追加
        calendar_added = False
        next_meeting = analysis.get('next_meeting', {})
        
        if next_meeting.get('scheduled'):
            event_title = next_meeting.get('title') or f"{analysis['meeting_title']} (次回)"
            event_date = next_meeting.get('date')
            event_time = next_meeting.get('time')
            
            result = add_to_google_calendar(event_title, event_date, event_time)
            if result:
                calendar_added = True
        
        # Telegram報告
        report = f"""📋 **議事録処理完了！**

**MTG:** {analysis['meeting_title']}
**日付:** {analysis['date']}

**サマリー:**
{analysis['summary']}

"""
        
        if analysis.get('decisions'):
            report += "**決定事項:**\n"
            for i, decision in enumerate(analysis['decisions'], 1):
                report += f"{i}. {decision}\n"
            report += "\n"
        
        if added_tasks:
            report += "**✅ TODOをGoogle Tasksに追加しといたよ:**\n"
            for task in added_tasks:
                report += f"• {task['task']} (期限: {task['deadline']})\n"
            report += "\n"
        
        if calendar_added:
            next_date = next_meeting.get('date')
            next_time = next_meeting.get('time', '未定')
            report += f"**📅 次回MTGをカレンダーに入れといたよ:**\n"
            report += f"{next_meeting.get('title')} - {next_date} {next_time}\n\n"
        
        report += f"議事録: `obsidian/Ichioka Obsidian/04_Project/.../MEETING.md` に保存予定"
        
        print(report)
        print(f"\n✓ Telegram報告送信予定")
        
        # 処理済みマーク
        mark_as_processed(file.name)
    
    print(f"\n✅ 処理完了: {len(new_files)}件")

if __name__ == "__main__":
    process_new_transcripts()
