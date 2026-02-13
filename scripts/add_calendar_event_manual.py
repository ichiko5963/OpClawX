
import sys
import json
import urllib.request
import urllib.parse
import urllib.error
import base64
import hashlib
import sqlite3
import subprocess
from pathlib import Path
from datetime import datetime, timezone, timedelta
from Crypto.Cipher import AES

JST = timezone(timedelta(hours=9))
N8N_DB_PATH = Path("/tmp/n8n_db.sqlite")
N8N_ENCRYPTION_KEY = "effdc06a2c03977ec7f117f4e3f0841fb3f5817e18ba096b973b0fd6115c9ceb"

def decrypt_n8n_credential(encrypted_data: str, encryption_key: str) -> dict:
    data = base64.b64decode(encrypted_data)
    if data[:8] != b'Salted__':
        raise ValueError("Invalid format")
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
    subprocess.run(
        ["docker", "cp", "n8n:/home/node/.n8n/database.sqlite", str(N8N_DB_PATH)],
        capture_output=True
    )
    conn = sqlite3.connect(N8N_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT data FROM credentials_entity WHERE type = 'googleCalendarOAuth2Api'")
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise ValueError("Calendar credentials not found")
    return decrypt_n8n_credential(row[0], N8N_ENCRYPTION_KEY)

def get_access_token() -> str:
    creds = get_calendar_credentials()
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
    return token_response['access_token']

def add_event(summary, start_iso, end_iso, description, location=None, attendees=None):
    try:
        token = get_access_token()
    except Exception as e:
        print(f"Error getting token: {e}")
        return None

    url = "https://www.googleapis.com/calendar/v3/calendars/primary/events"
    
    event = {
        "summary": summary,
        "description": description,
        "start": {
            "dateTime": start_iso,
            "timeZone": "Asia/Tokyo"
        },
        "end": {
            "dateTime": end_iso,
            "timeZone": "Asia/Tokyo"
        },
    }
    if location:
        event["location"] = location
    if attendees:
        event["attendees"] = [{"email": email} for email in attendees]

    data = json.dumps(event).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type", "application/json")
    
    try:
        with urllib.request.urlopen(req) as res:
            result = json.loads(res.read())
            print(f"Event created: {result.get('htmlLink')}")
            return result
    except urllib.error.HTTPError as e:
        print(f"HTTP Error creating event: {e.code} {e.reason}")
        print(e.read().decode('utf-8'))
        return None
    except Exception as e:
        print(f"Error creating event: {e}")
        return None

if __name__ == "__main__":
    start_iso = "2026-02-09T20:00:00+09:00"
    end_iso = "2026-02-09T20:30:00+09:00"
    summary = "広報_制作1on1 (西山碧)"
    description = "招待メールからの自動追加\n\nGoogle Meet: https://meet.google.com/jff-waqw-bnr\n\n元のメール: 招待状（差出人不明）: 広報_制作1on1(15~30min) (市岡直人)"
    location = "https://meet.google.com/jff-waqw-bnr"
    attendees = ["nisya.039@gmail.com"]
    
    print(f"Adding event: {summary} ({start_iso} - {end_iso})")
    add_event(summary, start_iso, end_iso, description, location, attendees)
