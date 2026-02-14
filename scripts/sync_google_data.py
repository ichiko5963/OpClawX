#!/usr/bin/env python3
"""
Google Data Sync Script
- Gmail, Calendar, Tasks, Drive, Sheets, Docs, Slidesを同期
- 初回: 1ヶ月分取得
- 以降: 1日分ずつ取得
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
import requests

WORKSPACE = Path(__file__).parent.parent
DATA_DIR = WORKSPACE / "data"
OAUTH_TOKEN_FILE = Path("/tmp/google_oauth_tokens.json")
STATE_FILE = DATA_DIR / "sync_state.json"

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

def get_sync_state():
    """同期状態取得"""
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {
        'last_sync': None,
        'initial_sync_done': False
    }

def update_sync_state(state):
    """同期状態更新"""
    STATE_FILE.write_text(json.dumps(state, indent=2))

def sync_gmail(access_token, days_back=1):
    """Gmail同期"""
    print(f"📧 Gmail同期中... (過去{days_back}日)")
    
    # 日付計算
    after_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y/%m/%d')
    
    url = "https://gmail.googleapis.com/gmail/v1/users/me/messages"
    headers = {'Authorization': f'Bearer {access_token}'}
    params = {
        'q': f'after:{after_date}',
        'maxResults': 100
    }
    
    response = requests.get(url, headers=headers, params=params)
    messages = response.json().get('messages', [])
    
    # 詳細取得
    gmail_data = []
    for msg in messages[:50]:  # 最大50件
        detail_url = f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{msg['id']}"
        detail = requests.get(detail_url, headers=headers).json()
        gmail_data.append(detail)
    
    # 保存
    output_dir = DATA_DIR / "gmail"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / f"{datetime.now().strftime('%Y-%m-%d')}.json"
    output_file.write_text(json.dumps(gmail_data, indent=2, ensure_ascii=False))
    
    print(f"  ✓ {len(gmail_data)}件取得")
    return len(gmail_data)

def sync_calendar(access_token, days_back=1):
    """Googleカレンダー同期"""
    print(f"📅 カレンダー同期中... (過去{days_back}日)")
    
    # 日付範囲
    time_min = (datetime.now() - timedelta(days=days_back)).isoformat() + 'Z'
    time_max = (datetime.now() + timedelta(days=30)).isoformat() + 'Z'
    
    url = "https://www.googleapis.com/calendar/v3/calendars/primary/events"
    headers = {'Authorization': f'Bearer {access_token}'}
    params = {
        'timeMin': time_min,
        'timeMax': time_max,
        'singleEvents': True,
        'orderBy': 'startTime'
    }
    
    response = requests.get(url, headers=headers, params=params)
    events = response.json().get('items', [])
    
    # 保存
    output_dir = DATA_DIR / "calendar"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / f"{datetime.now().strftime('%Y-%m-%d')}.json"
    output_file.write_text(json.dumps(events, indent=2, ensure_ascii=False))
    
    print(f"  ✓ {len(events)}件取得")
    return len(events)

def sync_tasks(access_token):
    """Google Tasks同期"""
    print(f"✅ Tasks同期中...")
    
    # タスクリスト取得
    url = "https://tasks.googleapis.com/tasks/v1/users/@me/lists"
    headers = {'Authorization': f'Bearer {access_token}'}
    
    response = requests.get(url, headers=headers)
    task_lists = response.json().get('items', [])
    
    all_tasks = []
    for task_list in task_lists:
        # 各リストのタスク取得
        tasks_url = f"https://tasks.googleapis.com/tasks/v1/lists/{task_list['id']}/tasks"
        tasks_response = requests.get(tasks_url, headers=headers)
        tasks = tasks_response.json().get('items', [])
        
        all_tasks.append({
            'list': task_list,
            'tasks': tasks
        })
    
    # 保存
    output_dir = DATA_DIR / "tasks"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / f"{datetime.now().strftime('%Y-%m-%d')}.json"
    output_file.write_text(json.dumps(all_tasks, indent=2, ensure_ascii=False))
    
    total_tasks = sum(len(t['tasks']) for t in all_tasks)
    print(f"  ✓ {total_tasks}件取得")
    return total_tasks

def sync_drive_transcriptions(access_token):
    """Google Drive文字起こし同期"""
    print(f"📁 Drive文字起こし同期中...")
    
    # Meet Recordingsフォルダ検索
    url = "https://www.googleapis.com/drive/v3/files"
    headers = {'Authorization': f'Bearer {access_token}'}
    params = {
        'q': "name='Meet Recordings' and mimeType='application/vnd.google-apps.folder'",
        'fields': 'files(id, name)'
    }
    
    response = requests.get(url, headers=headers, params=params)
    folders = response.json().get('files', [])
    
    if not folders:
        print("  ⚠️  Meet Recordingsフォルダが見つかりません")
        return 0
    
    folder_id = folders[0]['id']
    
    # フォルダ内の文字起こしファイル取得
    params = {
        'q': f"'{folder_id}' in parents and name contains 'transcript'",
        'fields': 'files(id, name, createdTime, mimeType)',
        'orderBy': 'createdTime desc'
    }
    
    response = requests.get(url, headers=headers, params=params)
    files = response.json().get('files', [])
    
    # 保存
    output_dir = DATA_DIR / "drive" / "transcriptions"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    count = 0
    for file in files[:10]:  # 最新10件
        try:
            # Google Docs形式ならExportで取得
            if 'google-apps' in file.get('mimeType', ''):
                # Docsとして取得
                export_url = f"https://www.googleapis.com/drive/v3/files/{file['id']}/export?mimeType=text/plain"
                content_response = requests.get(export_url, headers=headers)
            else:
                # バイナリファイルとして取得
                download_url = f"https://www.googleapis.com/drive/v3/files/{file['id']}?alt=media"
                content_response = requests.get(download_url, headers=headers)
            
            if content_response.status_code != 200:
                print(f"  ⚠️  {file['name']}: {content_response.status_code}")
                continue
            
            content = content_response.text
            
            output_file = output_dir / f"{file['name']}.json"
            output_file.write_text(json.dumps({
                'id': file['id'],
                'name': file['name'],
                'createdTime': file['createdTime'],
                'transcript': content
            }, indent=2, ensure_ascii=False))
            
            count += 1
            
        except Exception as e:
            print(f"  ❌ {file['name']}: {e}")
            continue
    
    print(f"  ✓ {count}件取得")
    return count

def main():
    """メイン処理"""
    print("=" * 50)
    print("🔄 Google Data Sync")
    print("=" * 50)
    
    # 初回同期チェック
    is_initial = os.getenv('INITIAL_SYNC', 'false').lower() == 'true'
    state = get_sync_state()
    
    if not state['initial_sync_done']:
        is_initial = True
        print("✨ 初回同期モード（1ヶ月分取得）")
    else:
        print("📅 通常同期モード（1日分取得）")
    
    days_back = 30 if is_initial else 1
    
    # OAuth token取得
    access_token = get_access_token()
    
    # 各サービス同期
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    stats = {}
    
    try:
        stats['gmail'] = sync_gmail(access_token, days_back)
    except Exception as e:
        print(f"  ❌ Gmail同期失敗: {e}")
        stats['gmail'] = 0
    
    try:
        stats['calendar'] = sync_calendar(access_token, days_back)
    except Exception as e:
        print(f"  ❌ Calendar同期失敗: {e}")
        stats['calendar'] = 0
    
    try:
        stats['tasks'] = sync_tasks(access_token)
    except Exception as e:
        print(f"  ❌ Tasks同期失敗: {e}")
        stats['tasks'] = 0
    
    try:
        stats['transcriptions'] = sync_drive_transcriptions(access_token)
    except Exception as e:
        print(f"  ❌ Drive同期失敗: {e}")
        stats['transcriptions'] = 0
    
    # 同期状態更新
    state['last_sync'] = datetime.now().isoformat()
    state['initial_sync_done'] = True
    state['last_stats'] = stats
    update_sync_state(state)
    
    print("\n" + "=" * 50)
    print("✅ 同期完了")
    print(f"Gmail: {stats['gmail']}件")
    print(f"Calendar: {stats['calendar']}件")
    print(f"Tasks: {stats['tasks']}件")
    print(f"Transcriptions: {stats['transcriptions']}件")
    print("=" * 50)

if __name__ == "__main__":
    main()
