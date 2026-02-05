#!/usr/bin/env python3
"""
Google Tasks API直接連携スクリプト
n8nのOAuth認証情報を使用
"""

import json
import urllib.request
import urllib.parse
import urllib.error
import base64
import hashlib
import os
from pathlib import Path
from datetime import datetime, timezone, timedelta
from Crypto.Cipher import AES

# 設定
JST = timezone(timedelta(hours=9))
SCRIPTS_PATH = Path(__file__).parent
TOKEN_CACHE_PATH = Path("/tmp/google_tasks_token.json")
N8N_DB_PATH = Path("/tmp/n8n_db.sqlite")

# n8n暗号化キー
N8N_ENCRYPTION_KEY = "effdc06a2c03977ec7f117f4e3f0841fb3f5817e18ba096b973b0fd6115c9ceb"

# Google Tasks credential ID (n8nから)
GOOGLE_TASKS_CRED_ID = "BI656HsL3iDwHuul"


def decrypt_n8n_credential(encrypted_data: str, encryption_key: str) -> dict:
    """n8nのcredentialを復号"""
    data = base64.b64decode(encrypted_data)
    
    if data[:8] != b'Salted__':
        raise ValueError("Invalid encrypted data format")
    
    salt = data[8:16]
    ciphertext = data[16:]
    
    # Key derivation (OpenSSL EVP_BytesToKey)
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


def get_credentials_from_n8n() -> dict:
    """n8nのデータベースからGoogle Tasks認証情報を取得"""
    import subprocess
    import sqlite3
    
    # n8nのデータベースをコピー
    result = subprocess.run(
        ["docker", "cp", "n8n:/home/node/.n8n/database.sqlite", str(N8N_DB_PATH)],
        capture_output=True
    )
    
    if not N8N_DB_PATH.exists():
        raise FileNotFoundError("Could not copy n8n database")
    
    conn = sqlite3.connect(N8N_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT data FROM credentials_entity WHERE type='googleTasksOAuth2Api'")
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise ValueError("Google Tasks credential not found in n8n")
    
    return decrypt_n8n_credential(row[0], N8N_ENCRYPTION_KEY)


def refresh_access_token(creds: dict) -> str:
    """Access tokenをリフレッシュ"""
    client_id = creds['clientId']
    client_secret = creds['clientSecret']
    refresh_token = creds['oauthTokenData']['refresh_token']
    
    token_url = "https://oauth2.googleapis.com/token"
    data = urllib.parse.urlencode({
        'client_id': client_id,
        'client_secret': client_secret,
        'refresh_token': refresh_token,
        'grant_type': 'refresh_token'
    }).encode()
    
    req = urllib.request.Request(token_url, data=data)
    req.add_header('Content-Type', 'application/x-www-form-urlencoded')
    
    with urllib.request.urlopen(req) as response:
        token_response = json.loads(response.read())
    
    # キャッシュに保存
    token_cache = {
        'access_token': token_response['access_token'],
        'refresh_token': refresh_token,
        'client_id': client_id,
        'client_secret': client_secret,
        'refreshed_at': datetime.now(JST).isoformat()
    }
    with open(TOKEN_CACHE_PATH, 'w') as f:
        json.dump(token_cache, f)
    
    return token_response['access_token']


def get_access_token() -> str:
    """有効なaccess tokenを取得（キャッシュまたはリフレッシュ）"""
    # キャッシュをチェック
    if TOKEN_CACHE_PATH.exists():
        with open(TOKEN_CACHE_PATH) as f:
            cache = json.load(f)
        
        # 30分以内ならキャッシュを使用
        refreshed_at = datetime.fromisoformat(cache.get('refreshed_at', '2000-01-01T00:00:00+09:00'))
        if datetime.now(JST) - refreshed_at < timedelta(minutes=30):
            return cache['access_token']
    
    # リフレッシュが必要
    creds = get_credentials_from_n8n()
    return refresh_access_token(creds)


def get_task_lists() -> list:
    """タスクリストを取得"""
    access_token = get_access_token()
    url = "https://tasks.googleapis.com/tasks/v1/users/@me/lists"
    
    req = urllib.request.Request(url)
    req.add_header('Authorization', f'Bearer {access_token}')
    
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read()).get('items', [])


def get_list_id_for_task(title: str, context: str = "") -> str:
    """タスクのタイトルと文脈からルーティング先のリストIDを決定"""
    routing_config_path = Path(__file__).parent / "task_routing.json"
    
    if not routing_config_path.exists():
        return None
    
    with open(routing_config_path) as f:
        config = json.load(f)
    
    search_text = f"{title} {context}".lower()
    
    # ルーティングルールをチェック
    for rule in config.get('routing_rules', []):
        pattern = rule['pattern'].lower()
        if pattern in search_text:
            list_name = rule['list']
            return config['task_lists'].get(list_name, {}).get('id')
    
    # キーワードマッチをチェック
    for list_name, list_config in config['task_lists'].items():
        for keyword in list_config.get('keywords', []):
            if keyword.lower() in search_text:
                return list_config['id']
    
    # デフォルトリストを返す
    for list_name, list_config in config['task_lists'].items():
        if list_config.get('default'):
            return list_config['id']
    
    return None


def add_task(title: str, notes: str = "", list_id: str = None, context: str = "") -> dict:
    """タスクを追加"""
    access_token = get_access_token()
    
    if not list_id:
        # ルーティングを試みる
        list_id = get_list_id_for_task(title, context)
    
    if not list_id:
        lists = get_task_lists()
        list_id = lists[0]['id'] if lists else None
    
    if not list_id:
        raise ValueError("No task list found")
    
    url = f"https://tasks.googleapis.com/tasks/v1/lists/{list_id}/tasks"
    
    task_data = {"title": title}
    if notes:
        task_data["notes"] = notes
    
    req = urllib.request.Request(url, data=json.dumps(task_data).encode('utf-8'), method='POST')
    req.add_header('Authorization', f'Bearer {access_token}')
    req.add_header('Content-Type', 'application/json')
    
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read())


def add_tasks_batch(tasks: list, list_id: str = None) -> list:
    """複数のタスクを一括追加"""
    results = []
    for task in tasks:
        title = task.get('title', '')
        notes = task.get('notes', '')
        try:
            result = add_task(title, notes, list_id)
            results.append({'success': True, 'id': result['id'], 'title': title})
            print(f"✅ Added: {title}")
        except Exception as e:
            results.append({'success': False, 'title': title, 'error': str(e)})
            print(f"❌ Failed: {title} - {e}")
    return results


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python google_tasks_direct.py list")
        print("  python google_tasks_direct.py add 'Task title' 'Notes'")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "list":
        lists = get_task_lists()
        print("Task Lists:")
        for tl in lists:
            print(f"  - {tl['title']} (id: {tl['id']})")
    
    elif command == "add":
        title = sys.argv[2] if len(sys.argv) > 2 else "Test task"
        notes = sys.argv[3] if len(sys.argv) > 3 else ""
        result = add_task(title, notes)
        print(f"✅ Added: {result['title']} (id: {result['id']})")
