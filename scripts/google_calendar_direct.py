#!/usr/bin/env python3
"""
Google Calendar 連携スクリプト
- 予定の検索
- 予定の追加
"""

import json
import urllib.request
import urllib.parse
import urllib.error
import base64
import hashlib
import sqlite3
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Optional
from Crypto.Cipher import AES

# 設定
JST = timezone(timedelta(hours=9))
SCRIPTS_PATH = Path(__file__).parent
N8N_DB_PATH = Path("/tmp/n8n_db.sqlite")
N8N_ENCRYPTION_KEY = "effdc06a2c03977ec7f117f4e3f0841fb3f5817e18ba096b973b0fd6115c9ceb"
TOKEN_CACHE_PATH = Path("/tmp/google_calendar_token.json")


def decrypt_n8n_credential(encrypted_data: str, encryption_key: str) -> dict:
    """n8nのcredentialを復号"""
    data = base64.b64decode(encrypted_data)
    
    if data[:8] != b'Salted__':
        raise ValueError("Invalid encrypted data format")
    
    salt = data[8:16]
    ciphertext = data[16:]
    
    key_iv = b''
    prev = b''
    while len(key_iv) < 48:
        prev = hashlib.md5(prev + encryption_key.encode() + salt).digest()
        key_iv += prev
    
    key = key_iv[:32]
    iv = key_iv[32:48]
    
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted = cipher.decrypt(ciphertext)
    
    padding_len = decrypted[-1]
    decrypted = decrypted[:-padding_len]
    
    return json.loads(decrypted.decode('utf-8'))


def get_calendar_credentials() -> dict:
    """n8nからGoogle Calendar認証情報を取得"""
    import subprocess
    
    subprocess.run(
        ["docker", "cp", "n8n:/home/node/.n8n/database.sqlite", str(N8N_DB_PATH)],
        capture_output=True
    )
    
    conn = sqlite3.connect(N8N_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT data FROM credentials_entity WHERE type='googleCalendarOAuth2Api'")
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise ValueError("Google Calendar credential not found")
    
    return decrypt_n8n_credential(row[0], N8N_ENCRYPTION_KEY)


def refresh_token(creds: dict) -> str:
    """Access tokenをリフレッシュ"""
    token_url = "https://oauth2.googleapis.com/token"
    data = urllib.parse.urlencode({
        'client_id': creds['clientId'],
        'client_secret': creds['clientSecret'],
        'refresh_token': creds['oauthTokenData']['refresh_token'],
        'grant_type': 'refresh_token'
    }).encode()
    
    req = urllib.request.Request(token_url, data=data)
    req.add_header('Content-Type', 'application/x-www-form-urlencoded')
    
    with urllib.request.urlopen(req) as response:
        token_response = json.loads(response.read())
    
    # キャッシュ保存
    cache = {
        'access_token': token_response['access_token'],
        'refreshed_at': datetime.now(JST).isoformat()
    }
    with open(TOKEN_CACHE_PATH, 'w') as f:
        json.dump(cache, f)
    
    return token_response['access_token']


def get_access_token() -> str:
    """有効なaccess tokenを取得"""
    if TOKEN_CACHE_PATH.exists():
        with open(TOKEN_CACHE_PATH) as f:
            cache = json.load(f)
        refreshed_at = datetime.fromisoformat(cache.get('refreshed_at', '2000-01-01T00:00:00+09:00'))
        if datetime.now(JST) - refreshed_at < timedelta(minutes=30):
            return cache['access_token']
    
    creds = get_calendar_credentials()
    return refresh_token(creds)


def search_events(query: str, days_ahead: int = 30) -> List[Dict]:
    """キーワードで予定を検索"""
    access_token = get_access_token()
    
    now = datetime.now(JST)
    time_min = now.strftime('%Y-%m-%dT00:00:00') + '%2B09:00'
    time_max = (now + timedelta(days=days_ahead)).strftime('%Y-%m-%dT23:59:59') + '%2B09:00'
    
    url = f"https://www.googleapis.com/calendar/v3/calendars/primary/events?timeMin={time_min}&timeMax={time_max}&singleEvents=true&orderBy=startTime&q={urllib.parse.quote(query)}"
    
    req = urllib.request.Request(url)
    req.add_header('Authorization', f'Bearer {access_token}')
    
    with urllib.request.urlopen(req) as response:
        events = json.loads(response.read())
    
    results = []
    for event in events.get('items', []):
        start = event.get('start', {})
        start_time = start.get('dateTime', start.get('date', ''))
        
        results.append({
            'id': event['id'],
            'summary': event.get('summary', ''),
            'start': start_time,
            'end': event.get('end', {}).get('dateTime', event.get('end', {}).get('date', '')),
            'location': event.get('location', ''),
        })
    
    return results


def add_event(
    summary: str,
    start_time: str,
    end_time: str = None,
    description: str = "",
    attendees: List[str] = None,
    location: str = ""
) -> Dict:
    """予定を追加"""
    access_token = get_access_token()
    
    # 終了時間がなければ1時間後
    if not end_time:
        start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        end_dt = start_dt + timedelta(hours=1)
        end_time = end_dt.isoformat()
    
    event = {
        'summary': summary,
        'start': {'dateTime': start_time, 'timeZone': 'Asia/Tokyo'},
        'end': {'dateTime': end_time, 'timeZone': 'Asia/Tokyo'},
    }
    
    if description:
        event['description'] = description
    if location:
        event['location'] = location
    if attendees:
        event['attendees'] = [{'email': email} for email in attendees]
    
    url = "https://www.googleapis.com/calendar/v3/calendars/primary/events"
    
    req = urllib.request.Request(url, data=json.dumps(event).encode(), method='POST')
    req.add_header('Authorization', f'Bearer {access_token}')
    req.add_header('Content-Type', 'application/json')
    
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read())


def find_next_event(keyword: str) -> Optional[Dict]:
    """次回の該当イベントを検索"""
    events = search_events(keyword)
    now = datetime.now(JST)
    
    for event in events:
        start = event['start']
        if 'T' in start:
            start_dt = datetime.fromisoformat(start.replace('Z', '+00:00')).astimezone(JST)
        else:
            start_dt = datetime.strptime(start, '%Y-%m-%d').replace(tzinfo=JST)
        
        if start_dt > now:
            return event
    
    return None


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Google Calendar Manager")
    parser.add_argument("--search", type=str, help="Search events by keyword")
    parser.add_argument("--next", type=str, help="Find next event matching keyword")
    parser.add_argument("--add", action="store_true", help="Add event (use with --summary, --start)")
    parser.add_argument("--summary", type=str, help="Event summary/title")
    parser.add_argument("--start", type=str, help="Start time (ISO format)")
    parser.add_argument("--end", type=str, help="End time (ISO format)")
    parser.add_argument("--desc", type=str, help="Description")
    args = parser.parse_args()
    
    if args.search:
        events = search_events(args.search)
        print(f"Found {len(events)} event(s):")
        for e in events:
            print(f"  - {e['summary']} ({e['start']})")
    
    elif args.next:
        event = find_next_event(args.next)
        if event:
            print(f"Next event: {event['summary']}")
            print(f"  Start: {event['start']}")
        else:
            print(f"No upcoming event matching '{args.next}'")
    
    elif args.add and args.summary and args.start:
        result = add_event(
            summary=args.summary,
            start_time=args.start,
            end_time=args.end,
            description=args.desc or ""
        )
        print(f"✅ Added: {result['summary']}")
        print(f"   Link: {result.get('htmlLink', '')}")
