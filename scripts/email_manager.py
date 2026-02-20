#!/usr/bin/env python3
"""
高品質メール管理システム v3
- Gmail直接API接続
- Obsidian文脈統合
- 返信案生成
- 優先度自動判定
"""

import json
import urllib.request
import urllib.parse
import urllib.error
import base64
import hashlib
import sqlite3
import re
import subprocess
import signal
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Optional, Tuple
from Crypto.Cipher import AES

# タイムアウト設定（60秒に延長）
TIMEOUT_SECONDS = 60

# リトライ設定
MAX_RETRIES = 3
RETRY_BACKOFF_INITIAL = 2  # 秒

class TimeoutError(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutError("Email processing timed out")


def retry_with_backoff(func):
    """指数バックオフ付きで関数をリトライ"""
    import time
    def wrapper(*args, **kwargs):
        last_exception = None
        for attempt in range(MAX_RETRIES):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                if attempt < MAX_RETRIES - 1:
                    wait_time = RETRY_BACKOFF_INITIAL * (2 ** attempt)
                    print(f"Retry {attempt + 1}/{MAX_RETRIES} after {wait_time}s: {e}")
                    time.sleep(wait_time)
        raise last_exception
    return wrapper

# 設定
JST = timezone(timedelta(hours=9))
SCRIPTS_PATH = Path(__file__).parent
WORKSPACE = Path("/Users/ai-driven-work/Library/Mobile Documents/com~apple~CloudDocs/OpenClaw-Shared")
OBSIDIAN_PATH = WORKSPACE / "obsidian/Ichioka Obsidian"
PEOPLE_PATH = OBSIDIAN_PATH / "10_People"
COMPANIES_PATH = OBSIDIAN_PATH / "11_Companies"
PROJECTS_PATH = OBSIDIAN_PATH / "03_Projects/_Active"
STATE_PATH = OBSIDIAN_PATH / "00_System/01_State"

N8N_DB_PATH = Path("/tmp/n8n_db.sqlite")
N8N_ENCRYPTION_KEY = "effdc06a2c03977ec7f117f4e3f0841fb3f5817e18ba096b973b0fd6115c9ceb"
TOKEN_CACHE_PATH = Path("/tmp/gmail_token.json")

# 重要な送信者パターン（優先度高）
IMPORTANT_SENDERS = [
    r"@theport\.jp",  # ポート株式会社
    r"@port-inc\.co\.jp",  # ポート株式会社
    r"@genspark\.ai",  # Genspark
    r"@aircle",  # AirCle関連
    r"山本梨香子",  # ポート
    r"高橋",  # ポート
    r"浜村|濱村",  # ポート
    r"吉田",  # ポート
    r"なーぼ",  # ポート
    r"大山",  # AirCle
    r"さき",  # AirCle
    r"りょうせい",  # AirCle
    r"Read AI",  # 会議録
    r"Climb ?Beyond",  # ClimbBeyond
]

# 無視するパターン（ノイズ除去）
IGNORE_PATTERNS = [
    r"noreply@",
    r"no-reply@",
    r"no_reply@",
    r"notifications@",
    r"newsletter@",
    r"info@.*sendenkaigi",
    r"@sendenkaigi\.com",
    r"@peatix\.com",
    r"@zapier\.com",
    r"@gmo-office\.com",
    r"@suumo\.jp",
    r"@e\.suumo\.jp",
    r"@mail\.zapier\.com",
    r"@chat-work\.com",
    r"unsubscribe",
    r"配信停止",
    r"メールマガジン",
    r"おすすめ.*物件",
    r"限定公開",
    r"アーカイブ配信",
    r"セミナー事務局",
    r"教育講座事業部",
    r"OfferBox-plus@i-plug\.co\.jp",
    r"@sendenkaigi\.com",
    r"@.*\.sendenkaigi\.com",
    r"@.*\.mynavi\.jp",
    r"@.*\.asoview\.com",
    r"@.*\.chatwork\.com",
    r"@chat-work\.com",
    r"@speed-ma\.com",
    r"info@speed-ma\.com",
]

# 返信が必要なキーワード
REPLY_REQUIRED_KEYWORDS = [
    r"ご確認ください",
    r"お返事",
    r"ご連絡",
    r"ご回答",
    r"いつ.*都合",
    r"日程.*調整",
    r"ミーティング.*お願い",
    r"質問",
    r"\?|？",
    r"至急",
    r"urgent",
    r"ASAP",
]


def decrypt_n8n_credential(encrypted_data: str, encryption_key: str) -> dict:
    """n8nのcredentialを復号"""
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


def get_gmail_credentials() -> dict:
    """n8nからGmail認証情報を取得"""
    subprocess.run(
        ["docker", "cp", "n8n:/home/node/.n8n/database.sqlite", str(N8N_DB_PATH)],
        capture_output=True
    )
    
    conn = sqlite3.connect(N8N_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT data FROM credentials_entity WHERE type LIKE '%gmail%'")
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise ValueError("Gmail credentials not found")
    
    return decrypt_n8n_credential(row[0], N8N_ENCRYPTION_KEY)


def get_access_token() -> str:
    """有効なaccess tokenを取得"""
    if TOKEN_CACHE_PATH.exists():
        with open(TOKEN_CACHE_PATH) as f:
            cache = json.load(f)
        refreshed_at = datetime.fromisoformat(cache.get('refreshed_at', '2000-01-01T00:00:00+09:00'))
        if datetime.now(JST) - refreshed_at < timedelta(minutes=30):
            return cache['access_token']
    
    creds = get_gmail_credentials()
    
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
    
    cache = {
        'access_token': token_response['access_token'],
        'refreshed_at': datetime.now(JST).isoformat()
    }
    with open(TOKEN_CACHE_PATH, 'w') as f:
        json.dump(cache, f)
    
    return token_response['access_token']


@retry_with_backoff
def get_emails(max_results: int = 50, unread_only: bool = True) -> List[Dict]:
    """メールを取得"""
    access_token = get_access_token()
    
    # クエリ構築
    query = "in:inbox"
    if unread_only:
        query += " is:unread"
    
    # メッセージ一覧を取得
    url = f"https://gmail.googleapis.com/gmail/v1/users/me/messages?maxResults={max_results}&q={urllib.parse.quote(query)}"
    req = urllib.request.Request(url)
    req.add_header('Authorization', f'Bearer {access_token}')
    
    with urllib.request.urlopen(req) as response:
        messages = json.loads(response.read())
    
    emails = []
    for msg in messages.get('messages', []):
        email = get_email_detail(access_token, msg['id'])
        if email:
            emails.append(email)
    
    return emails


@retry_with_backoff
def get_email_detail(access_token: str, msg_id: str) -> Optional[Dict]:
    """メールの詳細を取得"""
    url = f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{msg_id}?format=full"
    req = urllib.request.Request(url)
    req.add_header('Authorization', f'Bearer {access_token}')
    
    try:
        with urllib.request.urlopen(req) as response:
            detail = json.loads(response.read())
    except urllib.error.HTTPError:
        return None
    
    headers = {h['name'].lower(): h['value'] for h in detail['payload'].get('headers', [])}
    
    # 本文を抽出
    body = extract_body(detail['payload'])
    
    return {
        'id': msg_id,
        'thread_id': detail.get('threadId', ''),
        'from': headers.get('from', ''),
        'to': headers.get('to', ''),
        'subject': headers.get('subject', ''),
        'date': headers.get('date', ''),
        'snippet': detail.get('snippet', ''),
        'body': body[:2000],  # 最大2000文字
        'labels': [l['name'] for l in detail.get('labelIds', []) if isinstance(l, dict)] or detail.get('labelIds', []),
        'is_unread': 'UNREAD' in detail.get('labelIds', []),
    }


def extract_body(payload: Dict) -> str:
    """メール本文を抽出"""
    body = ""
    
    if payload.get('body', {}).get('data'):
        body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8', errors='ignore')
    elif payload.get('parts'):
        for part in payload['parts']:
            if part.get('mimeType') == 'text/plain' and part.get('body', {}).get('data'):
                body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8', errors='ignore')
                break
            elif part.get('parts'):
                body = extract_body(part)
                if body:
                    break
    
    # HTMLタグを除去
    body = re.sub(r'<[^>]+>', '', body)
    body = re.sub(r'\s+', ' ', body).strip()
    
    return body


def extract_sender_info(from_header: str) -> Tuple[str, str]:
    """送信者の名前とメールアドレスを抽出"""
    match = re.match(r'"?([^"<]+)"?\s*<([^>]+)>', from_header)
    if match:
        return match.group(1).strip(), match.group(2).strip()
    return "", from_header.strip()


def search_obsidian_context(sender_name: str, sender_email: str, subject: str) -> Dict:
    """Obsidianから関連する文脈を検索"""
    context = {
        'person': None,
        'company': None,
        'projects': [],
        'history': [],
    }
    
    # 人物検索
    if PEOPLE_PATH.exists():
        for person_dir in PEOPLE_PATH.iterdir():
            if person_dir.is_dir():
                profile_path = person_dir / "PROFILE.md"
                if profile_path.exists():
                    content = profile_path.read_text(encoding='utf-8')
                    if sender_name.lower() in content.lower() or sender_email.lower() in content.lower():
                        context['person'] = {
                            'name': person_dir.name,
                            'path': str(profile_path),
                            'summary': content[:500]
                        }
                        break
    
    # 企業検索
    if COMPANIES_PATH.exists():
        # メールドメインから企業を推測
        domain = sender_email.split('@')[-1] if '@' in sender_email else ''
        for company_dir in COMPANIES_PATH.iterdir():
            if company_dir.is_dir():
                profile_path = company_dir / "PROFILE.md"
                if profile_path.exists():
                    content = profile_path.read_text(encoding='utf-8')
                    if domain in content.lower() or company_dir.name.lower() in sender_email.lower():
                        context['company'] = {
                            'name': company_dir.name,
                            'path': str(profile_path),
                            'summary': content[:500]
                        }
                        break
    
    # プロジェクト検索
    if PROJECTS_PATH.exists():
        keywords = subject.lower().split() + sender_name.lower().split()
        for project_dir in PROJECTS_PATH.iterdir():
            if project_dir.is_dir():
                project_name = project_dir.name.lower()
                for keyword in keywords:
                    if len(keyword) > 2 and keyword in project_name:
                        context['projects'].append(project_dir.name)
                        break
    
    return context


def classify_email(email: Dict, context: Dict) -> Dict:
    """メールを分類"""
    sender_name, sender_email = extract_sender_info(email['from'])
    subject = email['subject']
    body = email['body']
    full_text = f"{email['from']} {subject} {body}"
    
    # ノイズ判定（最初にチェック）
    is_noise = any(re.search(p, full_text, re.I) for p in IGNORE_PATTERNS)
    
    # ノイズなら即return
    if is_noise:
        return {
            'priority': "P4",
            'is_noise': True,
            'is_important': False,
            'needs_reply': False,
            'sender_name': sender_name,
            'sender_email': sender_email,
        }
    
    # 重要度判定
    is_important = any(re.search(p, full_text, re.I) for p in IMPORTANT_SENDERS)
    
    # 文脈があれば重要
    if context['person'] or context['company']:
        is_important = True
    
    # 返信必要判定（ノイズでない場合のみ）
    needs_reply = any(re.search(p, full_text, re.I) for p in REPLY_REQUIRED_KEYWORDS)
    
    # 優先度決定
    if is_important and needs_reply:
        priority = "P1"
    elif is_important:
        priority = "P2"
    elif needs_reply:
        priority = "P2"
    else:
        priority = "P3"
    
    return {
        'priority': priority,
        'is_noise': is_noise,
        'is_important': is_important,
        'needs_reply': needs_reply,
        'sender_name': sender_name,
        'sender_email': sender_email,
    }


def generate_reply_draft(email: Dict, context: Dict, classification: Dict) -> Optional[str]:
    """返信案を生成"""
    if not classification['needs_reply'] or classification['is_noise']:
        return None
    
    sender_name = classification['sender_name']
    subject = email['subject']
    
    # 文脈に基づいた返信案
    greeting = f"{sender_name}様" if sender_name else "ご担当者様"
    
    # プロジェクト文脈があれば追加
    project_context = ""
    if context['projects']:
        project_context = f"（{', '.join(context['projects'])}関連）"
    
    # 企業文脈があれば追加
    company_context = ""
    if context['company']:
        company_context = f"\n\n【文脈】{context['company']['name']}との関係あり"
    
    draft = f"""【返信案】

{greeting}

お世話になっております。市岡です。

{subject}についてご連絡いただきありがとうございます。{project_context}

[ここに返信内容を記載]

よろしくお願いいたします。

市岡{company_context}"""
    
    return draft


def load_seen_emails() -> set:
    """既読メールIDを読み込み"""
    seen_path = STATE_PATH / "seen_emails.json"
    if seen_path.exists():
        with open(seen_path) as f:
            return set(json.load(f))
    return set()


def save_seen_emails(seen: set):
    """既読メールIDを保存"""
    STATE_PATH.mkdir(parents=True, exist_ok=True)
    seen_path = STATE_PATH / "seen_emails.json"
    # 最新1000件のみ保持
    seen_list = list(seen)[-1000:]
    with open(seen_path, 'w') as f:
        json.dump(seen_list, f)


def process_emails(all_emails: bool = False) -> Dict:
    """メールを処理してレポートを生成"""
    emails = get_emails(max_results=50, unread_only=False)
    seen = load_seen_emails()
    
    results = {
        'timestamp': datetime.now(JST).isoformat(),
        'total': len(emails),
        'new': 0,
        'p1': [],
        'p2': [],
        'p3': [],
        'noise': [],
        'needs_reply': [],
    }
    
    for email in emails:
        # 既読スキップ（all_emails=Trueの場合はスキップしない）
        if not all_emails and email['id'] in seen:
            continue
        
        results['new'] += 1
        seen.add(email['id'])
        
        sender_name, sender_email = extract_sender_info(email['from'])
        context = search_obsidian_context(sender_name, sender_email, email['subject'])
        classification = classify_email(email, context)
        
        # デバッグ: カレンダー追加対象のメール本文を表示
        if "広報_制作1on1" in email['subject']:
            print(f"DEBUG: Found target email. Subject: {email['subject']}")
            print(f"Date: {email['date']}")
            print("Body:")
            print(email['body'])
            print("---")
        
        email_summary = {
            'id': email['id'],
            'from': email['from'][:60],
            'subject': email['subject'][:80],
            'date': email['date'],
            'snippet': email['snippet'][:100],
            'priority': classification['priority'],
            'needs_reply': classification['needs_reply'],
            'context': {
                'person': context['person']['name'] if context['person'] else None,
                'company': context['company']['name'] if context['company'] else None,
                'projects': context['projects'],
            },
            'reply_draft': None,
        }
        
        # 返信案生成
        if classification['needs_reply']:
            email_summary['reply_draft'] = generate_reply_draft(email, context, classification)
            results['needs_reply'].append(email_summary)
        
        # 優先度別に振り分け
        if classification['priority'] == 'P1':
            results['p1'].append(email_summary)
        elif classification['priority'] == 'P2':
            results['p2'].append(email_summary)
        elif classification['priority'] == 'P3':
            results['p3'].append(email_summary)
        else:
            results['noise'].append(email_summary)
    
    save_seen_emails(seen)
    
    return results


def format_report(results: Dict) -> str:
    """Telegram用レポートを生成"""
    lines = []
    
    if results['new'] == 0:
        return ""
    
    lines.append(f"📧 **新着メール {results['new']}件**\n")
    
    # P1（緊急）
    if results['p1']:
        lines.append("🔴 **P1（緊急）**")
        for email in results['p1'][:3]:
            lines.append(f"  • {email['from'][:30]}")
            lines.append(f"    「{email['subject'][:40]}」")
            if email['context']['company']:
                lines.append(f"    📁 {email['context']['company']}")
        lines.append("")
    
    # P2（重要）
    if results['p2']:
        lines.append("🟡 **P2（重要）**")
        for email in results['p2'][:5]:
            reply_mark = "💬" if email['needs_reply'] else ""
            lines.append(f"  • {email['from'][:30]} {reply_mark}")
            lines.append(f"    「{email['subject'][:40]}」")
        lines.append("")
    
    # 返信が必要
    if results['needs_reply']:
        lines.append("💬 **返信が必要**")
        for email in results['needs_reply'][:3]:
            lines.append(f"  • {email['subject'][:40]}")
            if email['reply_draft']:
                lines.append(f"    → 返信案あり")
        lines.append("")
    
    # P3（通常）
    p3_count = len(results['p3'])
    if p3_count > 0:
        lines.append(f"📋 P3（通常）: {p3_count}件")
    
    # ノイズ
    noise_count = len(results['noise'])
    if noise_count > 0:
        lines.append(f"🔇 ノイズ: {noise_count}件（スキップ）")
    
    return "\n".join(lines)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Email Manager")
    parser.add_argument("--check", action="store_true", help="Check emails and print report")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--all", action="store_true", help="Show all emails (not just new)")
    parser.add_argument("--reset", action="store_true", help="Reset seen emails")
    args = parser.parse_args()
    
    if args.reset:
        seen_path = STATE_PATH / "seen_emails.json"
        if seen_path.exists():
            seen_path.unlink()
        print("Seen emails reset")
        exit(0)
    
    # タイムアウト設定
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(TIMEOUT_SECONDS)
    
    try:
        results = process_emails(args.all)
        signal.alarm(0)  # タイムアウト解除
        
        if args.json:
            print(json.dumps(results, indent=2, ensure_ascii=False))
        elif args.check:
            report = format_report(results)
            if report:
                print(report)
            else:
                print("NO_NEW_EMAILS")
        else:
            print(f"Processed {results['total']} emails, {results['new']} new")
            print(f"P1: {len(results['p1'])}, P2: {len(results['p2'])}, P3: {len(results['p3'])}")
            print(f"Needs reply: {len(results['needs_reply'])}")
    except TimeoutError:
        print("ERROR: Email processing timed out after 60 seconds", file=__import__('sys').stderr)
        exit(124)  # タイムアウトエラーコード

