#!/usr/bin/env python3
"""
Gmail AI Auto-Reply Script
- Reads high priority emails (P1/P2)
- Generates AI reply drafts
- Auto-sends or saves as draft based on config

Usage:
    python email_auto_reply.py              # Run once
    python email_auto_reply.py --watch      # Run continuously with cron
    python email_auto_reply.py --install-cron  # Install cron job
"""

import json
import re
import sys
import os
import base64
import hashlib
import sqlite3
import subprocess
import argparse
import logging
import urllib.request
import urllib.parse
import urllib.error
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Optional, Tuple
from Crypto.Cipher import AES
import yaml

# Add lib path
SCRIPTS_PATH = Path(__file__).parent
sys.path.insert(0, str(SCRIPTS_PATH / "lib"))

# Configuration
JST = timezone(timedelta(hours=9))
WORKSPACE = Path("/Users/ai-driven-work/Documents/OpenClaw-Workspace")
CONFIG_PATH = WORKSPACE / "scripts/config/email_auto_reply.yaml"
TOKEN_CACHE_PATH = Path("/tmp/gmail_auto_reply_token.json")
STATE_PATH = WORKSPACE / "data/email_auto_reply_state.json"
LOG_PATH = WORKSPACE / "logs"

# n8n credentials (same as email_manager.py)
N8N_DB_PATH = Path("/tmp/n8n_db.sqlite")
N8N_ENCRYPTION_KEY = "effdc06a2c03977ec7f117f4e3f0841fb3f5817e18ba096b973b0fd6115c9ceb"

# Important senders (same as email_manager.py)
IMPORTANT_SENDERS = [
    r"@theport\.jp",
    r"@port-inc\.co\.jp",
    r"@genspark\.ai",
    r"@aircle",
    r"山本梨香子",
    r"高橋",
    r"浜村|濱村",
    r"吉田",
    r"なーぼ",
    r"大山",
    r"さき",
    r"りょうせい",
    r"Read AI",
    r"Climb ?Beyond",
]

# Ignore patterns
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
]


class Config:
    """Configuration manager"""
    
    def __init__(self, config_path: Path):
        self.config_path = config_path
        self._load()
    
    def _load(self):
        if self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
        else:
            data = {}
        
        self.auto_send_mode = data.get('auto_send_mode', False)
        self.process_priorities = data.get('process_priorities', ['P1', 'P2'])
        self.cron_schedule = data.get('cron_schedule', '0 * * * *')
        self.max_emails_per_run = data.get('max_emails_per_run', 10)
        self.ignore_patterns = data.get('ignore_patterns', [])
        self.ai_settings = data.get('ai_settings', {
            'temperature': 0.7,
            'max_tokens': 500,
            'language': 'ja'
        })
        self.log_level = data.get('log_level', 'INFO')
        self.log_file = data.get('log_file', 'logs/email_auto_reply.log')
        self.state_file = data.get('state_file', 'data/email_auto_reply_state.json')
    
    def save(self):
        """Save current config"""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            'auto_send_mode': self.auto_send_mode,
            'process_priorities': self.process_priorities,
            'cron_schedule': self.cron_schedule,
            'max_emails_per_run': self.max_emails_per_run,
            'ignore_patterns': self.ignore_patterns,
            'ai_settings': self.ai_settings,
            'log_level': self.log_level,
            'log_file': self.log_file,
            'state_file': self.state_file,
        }
        with open(self.config_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, allow_unicode=True, default_flow_style=False)


def setup_logging(config: Config):
    """Setup logging"""
    LOG_PATH.mkdir(parents=True, exist_ok=True)
    log_file = WORKSPACE / config.log_file
    
    logging.basicConfig(
        level=getattr(logging, config.log_level),
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)


class StateManager:
    """Manage processed email state"""
    
    def __init__(self, state_path: Path):
        self.state_path = state_path
        self._load()
    
    def _load(self):
        if self.state_path.exists():
            with open(self.state_path, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
        else:
            self.data = {
                'processed_ids': [],
                'draft_ids': [],
                'sent_ids': [],
                'last_run': None
            }
    
    def save(self):
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.state_path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
    
    def is_processed(self, email_id: str) -> bool:
        return email_id in self.data['processed_ids']
    
    def mark_processed(self, email_id: str):
        if email_id not in self.data['processed_ids']:
            self.data['processed_ids'].append(email_id)
    
    def mark_draft(self, email_id: str):
        if email_id not in self.data['draft_ids']:
            self.data['draft_ids'].append(email_id)
    
    def mark_sent(self, email_id: str):
        if email_id not in self.data['sent_ids']:
            self.data['sent_ids'].append(email_id)
    
    def update_last_run(self):
        self.data['last_run'] = datetime.now(JST).isoformat()


# Credentials helpers (from email_manager.py)
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
    # Try to use cached token first
    if TOKEN_CACHE_PATH.exists():
        try:
            with open(TOKEN_CACHE_PATH) as f:
                cache = json.load(f)
            refreshed_at = datetime.fromisoformat(cache.get('refreshed_at', '2000-01-01T00:00:00+09:00'))
            if datetime.now(JST) - refreshed_at < timedelta(minutes=30):
                return cache['access_token']
        except (json.JSONDecodeError, KeyError):
            # Invalid cache, remove and continue
            TOKEN_CACHE_PATH.unlink()
    
    try:
        creds = get_gmail_credentials()
    except Exception as e:
        raise RuntimeError(f"Failed to get Gmail credentials: {e}")
    
    token_url = "https://oauth2.googleapis.com/token"
    data = urllib.parse.urlencode({
        'client_id': creds['clientId'],
        'client_secret': creds['clientSecret'],
        'refresh_token': creds['oauthTokenData']['refresh_token'],
        'grant_type': 'refresh_token'
    }).encode()
    
    req = urllib.request.Request(token_url, data=data)
    req.add_header('Content-Type', 'application/x-www-form-urlencoded')
    
    try:
        with urllib.request.urlopen(req) as response:
            token_response = json.loads(response.read())
    except urllib.error.HTTPError as e:
        error_body = e.read().decode() if e.fp else ""
        if "invalid_grant" in error_body:
            raise RuntimeError("Gmail refresh token expired. Please re-authenticate in n8n.")
        raise RuntimeError(f"Failed to refresh token: {e}")
    
    cache = {
        'access_token': token_response['access_token'],
        'refreshed_at': datetime.now(JST).isoformat()
    }
    with open(TOKEN_CACHE_PATH, 'w') as f:
        json.dump(cache, f)
    
    return token_response['access_token']


def get_emails_by_priority(max_results: int = 50) -> List[Dict]:
    """優先度高(P1/P2)のメールを取得"""
    access_token = get_access_token()
    
    # Get all unread emails
    url = f"https://gmail.googleapis.com/gmail/v1/users/me/messages?maxResults={max_results}&q=is:unread"
    req = urllib.request.Request(url)
    req.add_header('Authorization', f'Bearer {access_token}')
    
    with urllib.request.urlopen(req) as response:
        messages = json.loads(response.read())
    
    emails = []
    for msg in messages.get('messages', []):
        email = get_email_detail(access_token, msg['id'])
        if email and is_important_email(email):
            emails.append(email)
    
    return emails


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
    
    body = extract_body(detail['payload'])
    
    return {
        'id': msg_id,
        'thread_id': detail.get('threadId', ''),
        'from': headers.get('from', ''),
        'to': headers.get('to', ''),
        'subject': headers.get('subject', ''),
        'date': headers.get('date', ''),
        'snippet': detail.get('snippet', ''),
        'body': body[:3000],
        'labels': detail.get('labelIds', []),
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
    
    body = re.sub(r'<[^>]+>', '', body)
    body = re.sub(r'\s+', ' ', body).strip()
    
    return body


def is_important_email(email: Dict) -> bool:
    """重要度判定（P1/P2）"""
    from_header = email.get('from', '')
    subject = email.get('subject', '')
    body = email.get('body', '')
    full_text = f"{from_header} {subject} {body}"
    
    # Check ignore patterns
    for pattern in IGNORE_PATTERNS:
        if re.search(pattern, full_text, re.I):
            return False
    
    # Check important senders
    if any(re.search(p, full_text, re.I) for p in IMPORTANT_SENDERS):
        priority = classify_priority(email)
        return priority in ['P1', 'P2']
    
    return False


def classify_priority(email: Dict) -> str:
    """優先度を判定"""
    subject = email.get('subject', '')
    body = email.get('body', '')
    full_text = f"{subject} {body}"
    
    # P1 keywords
    p1_keywords = [
        r"至急",
        r"urgent",
        r"ASAP",
        r"⚠",
        r"緊急",
        r"今日中",
        r"今日.*まで",
    ]
    
    # P2 keywords
    p2_keywords = [
        r"ご確認",
        r"お返事",
        r"ご質問",
        r"お願いします",
        r"ご確認ください",
        r"ご回答",
        r"日程",
        r"調整",
    ]
    
    if any(re.search(k, full_text) for k in p1_keywords):
        return 'P1'
    elif any(re.search(k, full_text) for k in p2_keywords):
        return 'P2'
    elif any(re.search(p, full_text, re.I) for p in IMPORTANT_SENDERS):
        return 'P2'
    
    return 'P3'


def generate_ai_reply(email: Dict, config: Config, logger) -> str:
    """AIを使用して返信を生成（OpenAI API直接呼び出し）"""
    import os
    
    # Get API key from environment
    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        logger.warning("OPENAI_API_KEY not set, using fallback reply")
        return generate_fallback_reply(email)
    
    # Build context
    sender_name, sender_email = extract_sender_info(email.get('from', ''))
    subject = email.get('subject', '')
    body = email.get('body', '')
    
    # Create prompt
    system_prompt = f"""あなたは{sender_name}さんへの返信メールを作成します。
以下の約束事を守ってください：
1. ビジネスメールとして適切な敬語を使用
2. 簡潔で明確に
3. {config.ai_settings.get('language', 'ja')}語で作成
4. まずお礼を書き、内容は短く
5. 署名なし（下の名前だけ）"""

    user_prompt = f"""差出人: {sender_name} <{sender_email}>
件名: {subject}
本文:
{body}

上記のメールへの返信を下書きしてください。"""

    # Direct API call
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": config.ai_settings.get('temperature', 0.7),
        "max_tokens": config.ai_settings.get('max_tokens', 500),
    }
    
    try:
        req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers)
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read())
        
        reply = result['choices'][0]['message']['content'].strip()
        logger.info(f"Generated AI reply for {sender_email}")
        return reply
        
    except Exception as e:
        logger.error(f"AI reply generation failed: {e}")
        return generate_fallback_reply(email)


def generate_fallback_reply(email: Dict) -> str:
    """フォールバック用の簡易返信"""
    sender_name, sender_email = extract_sender_info(email.get('from', ''))
    return f"""{sender_name}さん

ご確認ありがとうございます。
近日中にご返答いたします。

ichioka"""


def extract_sender_info(from_header: str) -> Tuple[str, str]:
    """送信者の名前とメールアドレスを抽出"""
    match = re.match(r'"?([^"<]+)"?\s*<([^>]+)>', from_header)
    if match:
        return match.group(1).strip(), match.group(2).strip()
    return "", from_header.strip()


def create_draft(access_token: str, email: Dict, reply_body: str) -> str:
    """下書きを作成"""
    sender_name, sender_email = extract_sender_info(email.get('from', ''))
    to_email = sender_email
    subject = f"Re: {email.get('subject', '')}"
    
    # Create MIME message
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    import email
    
    msg = MIMEMultipart()
    msg['to'] = to_email
    msg['subject'] = subject
    msg.attach(MIMEText(reply_body, 'plain', 'utf-8'))
    
    raw_message = base64.urlsafe_b64encode(msg.as_bytes()).decode('utf-8')
    
    url = "https://gmail.googleapis.com/gmail/v1/users/me/drafts"
    data = json.dumps({
        'message': {
            'raw': raw_message,
            'threadId': email.get('thread_id', '')
        }
    }).encode('utf-8')
    
    req = urllib.request.Request(url, data=data)
    req.add_header('Authorization', f'Bearer {access_token}')
    req.add_header('Content-Type', 'application/json')
    
    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read())
    
    return result.get('id', '')


def send_reply(access_token: str, email: Dict, reply_body: str) -> bool:
    """メールを送信"""
    sender_name, sender_email = extract_sender_info(email.get('from', ''))
    to_email = sender_email
    subject = f"Re: {email.get('subject', '')}"
    
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    
    msg = MIMEMultipart()
    msg['to'] = to_email
    msg['subject'] = subject
    msg.attach(MIMEText(reply_body, 'plain', 'utf-8'))
    
    raw_message = base64.urlsafe_b64encode(msg.as_bytes()).decode('utf-8')
    
    url = "https://gmail.googleapis.com/gmail/v1/users/me/messages/send"
    data = json.dumps({
        'raw': raw_message,
        'threadId': email.get('thread_id', '')
    }).encode('utf-8')
    
    req = urllib.request.Request(url, data=data)
    req.add_header('Authorization', f'Bearer {access_token}')
    req.add_header('Content-Type', 'application/json')
    
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read())
        return True
    except urllib.error.HTTPError as e:
        print(f"Send failed: {e}")
        return False


def mark_as_read(access_token: str, msg_id: str):
    """メールを既読にする"""
    url = f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{msg_id}/modify"
    data = json.dumps({
        'removeLabelIds': ['UNREAD']
    }).encode('utf-8')
    
    req = urllib.request.Request(url, data=data)
    req.add_header('Authorization', f'Bearer {access_token}')
    req.add_header('Content-Type', 'application/json')
    
    with urllib.request.urlopen(req):
        pass


def process_emails(config: Config, logger):
    """メールを処理"""
    logger.info("Starting email auto-reply process...")
    
    # Get emails
    emails = get_emails_by_priority(config.max_emails_per_run)
    logger.info(f"Found {len(emails)} priority emails")
    
    if not emails:
        logger.info("No priority emails to process")
        return
    
    # Get access token
    access_token = get_access_token()
    
    # Load state
    state = StateManager(WORKSPACE / config.state_file)
    
    # Process each email
    for email in emails:
        email_id = email['id']
        
        # Skip if already processed
        if state.is_processed(email_id):
            logger.debug(f"Skipping already processed: {email_id}")
            continue
        
        sender_name, sender_email = extract_sender_info(email.get('from', ''))
        priority = classify_priority(email)
        
        logger.info(f"Processing: {sender_email} (Priority: {priority})")
        
        # Generate AI reply
        reply_body = generate_ai_reply(email, config, logger)
        
        if config.auto_send_mode:
            # Send directly
            success = send_reply(access_token, email, reply_body)
            if success:
                state.mark_sent(email_id)
                logger.info(f"Sent reply to {sender_email}")
            else:
                logger.error(f"Failed to send to {sender_email}")
                state.mark_processed(email_id)
        else:
            # Save as draft
            draft_id = create_draft(access_token, email, reply_body)
            if draft_id:
                state.mark_draft(email_id)
                logger.info(f"Created draft for {sender_email}")
            else:
                logger.error(f"Failed to create draft for {sender_email}")
                state.mark_processed(email_id)
        
        # Mark as read
        mark_as_read(access_token, email_id)
    
    state.update_last_run()
    state.save()
    logger.info("Email auto-reply process completed")


def install_cron(config: Config):
    """Install cron job"""
    script_path = Path(__file__).absolute()
    cron_entry = f"{config.cron_schedule} /usr/bin/python3 {script_path}"
    
    # Get current crontab
    result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
    current_crontab = result.stdout if result.returncode == 0 else ""
    
    # Check if entry already exists
    if 'email_auto_reply.py' in current_crontab:
        print("Cron entry already exists. Removing old entry...")
        lines = [l for l in current_crontab.split('\n') if 'email_auto_reply.py' not in l]
        current_crontab = '\n'.join(lines)
    
    # Add new entry
    new_crontab = current_crontab.strip() + '\n' + cron_entry + '\n'
    
    # Install crontab
    proc = subprocess.Popen(['crontab', '-'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    proc.communicate(input=new_crontab.encode('utf-8'))
    
    print(f"Installed cron job: {cron_entry}")
    print(f"Config auto_send_mode: {config.auto_send_mode}")


def main():
    parser = argparse.ArgumentParser(description='Gmail AI Auto-Reply')
    parser.add_argument('--watch', action='store_true', help='Run continuously (for cron)')
    parser.add_argument('--install-cron', action='store_true', help='Install cron job')
    parser.add_argument('--config', type=str, help='Config file path')
    parser.add_argument('--auto-send', action='store_true', help='Enable auto-send mode')
    parser.add_argument('--no-auto-send', action='store_true', help='Disable auto-send mode')
    
    args = parser.parse_args()
    
    # Load config
    config_path = Path(args.config) if args.config else CONFIG_PATH
    config = Config(config_path)
    
    # Override auto_send_mode if specified
    if args.auto_send:
        config.auto_send_mode = True
        config.save()
    elif args.no_auto_send:
        config.auto_send_mode = False
        config.save()
    
    # Setup logging
    logger = setup_logging(config)
    
    if args.install_cron:
        install_cron(config)
        return
    
    # Process emails
    try:
        process_emails(config, logger)
    except RuntimeError as e:
        logger.error(str(e))
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.exception("Unexpected error")
        print(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
