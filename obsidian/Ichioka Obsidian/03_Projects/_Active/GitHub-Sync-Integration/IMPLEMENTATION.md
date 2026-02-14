# GitHub情報一元管理システム - 実装詳細

## 🔧 技術スタック

- **GitHub Actions**: データ収集
- **Python 3.11**: 同期スクリプト
- **Google APIs**: Gmail, Calendar, Tasks, Drive
- **Notion API**: Notionデータ取得
- **Slack API**: Slackメッセージ取得
- **Anthropic Claude**: 議事録生成
- **Obsidian Git Plugin**: ローカル同期
- **OpenClaw**: 全処理・学習

---

## 📂 データ構造

### ichioka-vault/data/

```
data/
├── gmail/
│   ├── YYYY-MM-DD.json          # 日別受信メール
│   │   {
│   │     "messages": [...],
│   │     "historyId": "12345"
│   │   }
│   └── metadata.json
│       {
│         "last_history_id": "12345",
│         "last_sync": "2026-02-14T12:00:00Z"
│       }
│
├── calendar/
│   ├── YYYY-MM.json             # 月別イベント
│   │   {
│   │     "events": [
│   │       {
│   │         "id": "evt123",
│   │         "summary": "MTG with ポート",
│   │         "start": "2026-02-14T15:00:00+09:00",
│   │         "attendees": [...]
│   │       }
│   │     ]
│   │   }
│   └── metadata.json
│
├── tasks/
│   ├── YYYY-MM-DD.json          # 日別タスク状態
│   │   {
│   │     "taskLists": [
│   │       {
│   │         "id": "list123",
│   │         "title": "AirCle",
│   │         "tasks": [...]
│   │       }
│   │     ]
│   │   }
│   └── metadata.json
│
├── drive/
│   ├── transcriptions/
│   │   └── 2026-02-14T15-30.txt  # Google Meet文字起こし（生テキスト）
│   ├── changes.json              # ファイル変更履歴
│   └── metadata.json
│       {
│         "processed_transcriptions": [
│           "2026-02-14T15-30.txt"
│         ],
│         "last_change_id": "67890"
│       }
│
├── notion/
│   ├── YYYY-MM-DD.json          # ページスナップショット
│   └── metadata.json
│
└── slack/
    ├── YYYY-MM-DD.json          # メッセージ履歴
    └── metadata.json
```

---

## 🔐 認証フロー

### Google OAuth Refresh Token取得（初回のみ）

```python
# scripts/get_google_refresh_token.py
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/calendar.readonly',
    'https://www.googleapis.com/auth/tasks',
    'https://www.googleapis.com/auth/drive.readonly'
]

flow = InstalledAppFlow.from_client_secrets_file(
    'client_secret.json',  # Google Cloud Consoleからダウンロード
    SCOPES
)

creds = flow.run_local_server(port=0)
print(f'Refresh Token: {creds.refresh_token}')
# このトークンをGitHub Secretsに保存
```

### GitHub Actionsでの認証

```python
from google.oauth2.credentials import Credentials

creds = Credentials(
    token=None,  # access_tokenは不要（自動取得）
    refresh_token=os.environ['GOOGLE_REFRESH_TOKEN'],
    client_id=os.environ['GOOGLE_CLIENT_ID'],
    client_secret=os.environ['GOOGLE_CLIENT_SECRET'],
    token_uri='https://oauth2.googleapis.com/token'
)

# これでbuild()時に自動的にaccess_tokenが取得される
service = build('gmail', 'v1', credentials=creds)
```

---

## 🤖 議事録生成ロジック

### OpenClaw cronジョブ

```python
# scripts/process_transcriptions.py
import anthropic
from pathlib import Path
import json

def process_new_transcriptions():
    transcriptions_dir = Path('obsidian/Ichioka Obsidian/00_System/External/data/drive/transcriptions/')
    metadata_path = Path('obsidian/Ichioka Obsidian/00_System/External/data/drive/metadata.json')
    
    metadata = json.loads(metadata_path.read_text())
    processed = set(metadata.get('processed_transcriptions', []))
    
    for txt_file in transcriptions_dir.glob('*.txt'):
        if txt_file.name in processed:
            continue
        
        transcription = txt_file.read_text()
        
        # 議事録生成
        minutes = generate_minutes(transcription)
        
        # プロジェクト判定
        project = identify_project(minutes)
        
        # 保存
        save_minutes(minutes, project)
        
        # TODO抽出→Google Tasks追加
        todos = extract_todos(minutes)
        add_to_google_tasks(todos, project)
        
        # 処理済みマーク
        processed.add(txt_file.name)
    
    metadata['processed_transcriptions'] = list(processed)
    metadata_path.write_text(json.dumps(metadata, indent=2))

def generate_minutes(transcription: str) -> str:
    client = anthropic.Anthropic()
    
    prompt = f"""以下の文字起こしから議事録を作成してください。

# 要件
1. 参加者を特定（名前を抽出）
2. 要約（3-5行）
3. 決定事項（箇条書き）
4. TODO（いちさんのTODOのみ。担当者・期限付き）
5. 次回予定

# 参考情報
Obsidian 10_People/にある人物: [ここでディレクトリ一覧を挿入]
Obsidian 11_Companies/にある企業: [ここでディレクトリ一覧を挿入]
進行中プロジェクト: ClimbBeyond, AirCle, SlideBox, ClientWork, Genspark

# 出力形式
Markdown形式、Obsidian準拠

# 文字起こし
{transcription}
"""
    
    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.content[0].text

def identify_project(minutes: str) -> str:
    """議事録からプロジェクトを判定"""
    if any(word in minutes for word in ['ポート', 'ClimbBeyond', '就活ボックス']):
        return 'ClimbBeyond'
    elif 'AirCle' in minutes or '大山' in minutes:
        return 'AirCle'
    elif 'SlideBox' in minutes:
        return 'SlideBox'
    elif 'Genspark' in minutes:
        return 'Genspark'
    else:
        return 'Unknown'

def save_minutes(minutes: str, project: str):
    """議事録を適切な場所に保存"""
    from datetime import datetime
    today = datetime.now().strftime('%Y-%m-%d')
    
    if project != 'Unknown':
        path = Path(f'obsidian/Ichioka Obsidian/03_Projects/_Active/{project}/MTG/{today}_議事録.md')
    else:
        path = Path(f'obsidian/Ichioka Obsidian/00_System/External/meetings/{today}_議事録.md')
    
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(minutes)

def extract_todos(minutes: str) -> list:
    """TODOセクションを抽出"""
    # 簡易パース（実際はもっと洗練が必要）
    todos = []
    in_todo_section = False
    
    for line in minutes.split('\n'):
        if '## TODO' in line or '## タスク' in line:
            in_todo_section = True
            continue
        if in_todo_section and line.startswith('##'):
            break
        if in_todo_section and line.strip().startswith('-'):
            todos.append(line.strip('- '))
    
    return todos

def add_to_google_tasks(todos: list, project: str):
    """Google Tasksに追加"""
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    
    creds = get_google_credentials()
    service = build('tasks', 'v1', credentials=creds)
    
    # タスクリスト判定
    task_list_map = {
        'ClimbBeyond': 'ClimbBeyondリストID',
        'AirCle': 'AircleリストID',
        'Unknown': '@defaultリストID'
    }
    task_list_id = task_list_map.get(project, task_list_map['Unknown'])
    
    for todo in todos:
        task = {
            'title': todo,
            'due': determine_due_date(todo)  # 期限推測ロジック
        }
        service.tasks().insert(tasklist=task_list_id, body=task).execute()
```

---

## 🔄 差分取得ロジック（効率化）

### Gmail History API

```python
def sync_gmail_incremental(metadata: dict) -> dict:
    """差分のみ取得"""
    service = build('gmail', 'v1', credentials=creds)
    
    if metadata.get('last_history_id'):
        # 差分取得
        results = service.users().history().list(
            userId='me',
            startHistoryId=metadata['last_history_id'],
            historyTypes=['messageAdded']
        ).execute()
    else:
        # 初回は直近100件
        results = service.users().messages().list(
            userId='me',
            maxResults=100
        ).execute()
    
    return {
        'messages': results.get('messages', []),
        'historyId': results.get('historyId')
    }
```

### Google Drive Changes API

```python
def sync_drive_changes(metadata: dict) -> dict:
    """ファイル変更の差分取得"""
    service = build('drive', 'v3', credentials=creds)
    
    if metadata.get('last_change_id'):
        changes = service.changes().list(
            pageToken=metadata['last_change_id'],
            spaces='drive',
            fields='nextPageToken,changes(file(id,name,mimeType,createdTime))'
        ).execute()
    else:
        # 初回は現在のstartPageTokenを取得
        start_token = service.changes().getStartPageToken().execute()
        changes = {'nextPageToken': start_token['startPageToken'], 'changes': []}
    
    return changes
```

---

## 📊 モニタリング＆ログ

### GitHub Actions実行ログ

- リポジトリ → Actions → 最新実行を確認
- エラーがあればログで詳細確認

### OpenClaw cronジョブログ

```bash
# cronジョブの実行履歴確認
openclaw sessions_list --kinds isolated --limit 10

# 特定セッションの詳細
openclaw sessions_history --sessionKey [sessionKey]
```

### Obsidian Gitログ

- Obsidian → Command Palette → "Obsidian Git: View git log"

---

## 🛡️ エラーハンドリング

### GitHub Actions

```yaml
- name: Sync with error handling
  run: |
    python scripts/sync_all.py || {
      echo "Sync failed, but continuing..."
      exit 0
    }
```

### Python スクリプト

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

try:
    sync_gmail()
except Exception as e:
    logging.error(f'Gmail sync failed: {e}')
    # 他のサービスは継続
```

---

## 🔒 セキュリティ

1. **GitHubリポジトリはPrivate必須**
2. **Secretsは絶対にコミットしない**（`.gitignore`に追加）
3. **OAuth Scopeは必要最小限**
4. **定期的なトークンローテーション**（年1回）
5. **2FAを有効化**（GitHub, Google）

---

## 次のステップ

[[TASKS]]に戻って実装開始。
