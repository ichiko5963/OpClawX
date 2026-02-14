# メモリ自動整理システム 完全設計書

## 🎯 目的

NotionやGitHubから取得した大量の情報を、AIが毎朝自動で整理し、
いちさんが使いやすい構造に保つ。

---

## 🔄 全体フロー

```
【毎日 4:00】Notion/GitHub情報収集
      ↓
【毎日 4:10】メモリ整理開始（30分間）
      ↓
  AI分析・分類
      ↓
  適切な場所に配置
      ↓
  GitHubフォルダ整理
      ↓
【毎日 4:30】Telegram報告
```

---

## 📂 情報の流れ

### 1. 情報源
```
Notion (大量の情報源)
  ├── プロジェクトノート
  ├── ミーティングメモ
  ├── タスクリスト
  ├── 人物情報
  └── 知識ベース
       ↓
GitHub (一時保存)
  data/notion/YYYY-MM-DD.json
       ↓
Claude分析（AI整理）
       ↓
構造化データ
       ↓
適切な場所に配置
```

### 2. 配置先（既存構造を崩さない）

```
obsidian/Ichioka Obsidian/
├── 00_System/          # システム・設定
├── 03_Projects/
│   ├── _Active/        # アクティブプロジェクト
│   └── _Old/           # 完了・休止
├── 10_People/          # 人物情報
│   └── [人物名]/
│       └── PROFILE.md
├── 11_Companies/       # 企業情報
│   └── [企業名]/
│       └── PROFILE.md
└── memory/
    ├── YYYY-MM-DD.md   # 日次メモ
    └── MEMORY.md       # 長期記憶
```

---

## 🧠 AI整理ロジック

### Phase 1: 情報分類（10分）

```python
def classify_notion_content(content):
    """Notionコンテンツを分類"""
    
    categories = {
        'project': {
            'keywords': ['プロジェクト', 'マイルストーン', '進捗'],
            'destination': '03_Projects/_Active/'
        },
        'person': {
            'keywords': ['連絡先', '人物', 'プロフィール'],
            'destination': '10_People/'
        },
        'company': {
            'keywords': ['企業', '会社', '組織'],
            'destination': '11_Companies/'
        },
        'meeting': {
            'keywords': ['MTG', 'ミーティング', '会議'],
            'destination': '03_Projects/[プロジェクト名]/'
        },
        'knowledge': {
            'keywords': ['メモ', '知識', '学習'],
            'destination': 'memory/'
        }
    }
    
    # Claude APIで分類
    # タイトル、内容、メタデータから判断
    # 複数カテゴリにまたがる場合は分割
```

### Phase 2: 既存情報とマージ（10分）

```python
def merge_with_existing(new_info, existing_file):
    """既存ファイルと賢くマージ"""
    
    # 1. 重複チェック
    # 2. 新情報の追加箇所を判断
    # 3. セクション単位で追加
    # 4. 既存内容は基本的に保持
    
    # 例：
    # 人物情報 → PROFILE.mdの適切なセクションに追加
    # プロジェクト → PROJECT.mdの進捗セクションに追加
```

### Phase 3: GitHubフォルダ整理（10分）

```python
def organize_github_folders():
    """GitHubデータフォルダを整理"""
    
    # 1. 古いデータをアーカイブ
    # data/gmail/2026-01-*.json → data/archive/2026-01/gmail/
    
    # 2. 重複ファイル削除
    
    # 3. インデックス作成
    # data/INDEX.md に全データの概要
```

---

## 📅 日替わり整理戦略

### 曜日別テーマ

**月曜：プロジェクト情報整理**
- 03_Projects/_Active/ を重点整理
- 進捗更新
- 完了プロジェクト → _Old/ 移動

**火曜：人物情報整理**
- 10_People/ を重点整理
- 新しい人物追加
- プロフィール更新

**水曜：企業情報整理**
- 11_Companies/ を重点整理
- 関係性更新

**木曜：タスク・TODO整理**
- 各プロジェクトのTODO統合
- 期限超過タスク確認

**金曜：知識・メモ整理**
- memory/ を重点整理
- 日次メモから重要情報をMEMORY.mdへ

**土曜：全体見直し**
- 構造の見直し
- 不要ファイル削除

**日曜：アーカイブ整理**
- 古いデータの整理
- GitHubフォルダ整理

---

## 🛠️ 実装

### 1. Notion同期スクリプト

```python
# scripts/sync_notion.py
import os
import json
import requests
from datetime import datetime
from pathlib import Path

NOTION_TOKEN = os.getenv('NOTION_TOKEN')
NOTION_API = 'https://api.notion.com/v1'

def sync_notion_pages():
    """Notionページを全取得"""
    headers = {
        'Authorization': f'Bearer {NOTION_TOKEN}',
        'Notion-Version': '2022-06-28'
    }
    
    # 検索APIで全ページ取得
    url = f'{NOTION_API}/search'
    data = {'filter': {'property': 'object', 'value': 'page'}}
    
    all_pages = []
    has_more = True
    start_cursor = None
    
    while has_more:
        if start_cursor:
            data['start_cursor'] = start_cursor
        
        response = requests.post(url, headers=headers, json=data)
        result = response.json()
        
        all_pages.extend(result.get('results', []))
        has_more = result.get('has_more', False)
        start_cursor = result.get('next_cursor')
    
    # 保存
    output_dir = Path('data/notion')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    today = datetime.now().strftime('%Y-%m-%d')
    output_file = output_dir / f'{today}.json'
    output_file.write_text(json.dumps(all_pages, indent=2, ensure_ascii=False))
    
    return len(all_pages)
```

### 2. メモリ整理エンジン

```python
# scripts/memory_organizer.py
import os
import json
from datetime import datetime
from pathlib import Path
import anthropic

ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
WORKSPACE = Path('obsidian/Ichioka Obsidian')

# 曜日別テーマ
DAILY_THEMES = {
    0: 'プロジェクト情報',  # 月曜
    1: '人物情報',
    2: '企業情報',
    3: 'タスク・TODO',
    4: '知識・メモ',
    5: '全体見直し',
    6: 'アーカイブ整理'
}

def get_todays_theme():
    """今日のテーマ"""
    weekday = datetime.now().weekday()
    return DAILY_THEMES[weekday]

def organize_memory():
    """メモリ整理メイン"""
    
    theme = get_todays_theme()
    print(f"今日のテーマ: {theme}")
    
    report = {
        'theme': theme,
        'actions': [],
        'start_time': datetime.now().isoformat()
    }
    
    # Notionデータ読み込み
    notion_data = load_latest_notion_data()
    
    if theme == 'プロジェクト情報':
        report['actions'] = organize_projects(notion_data)
    
    elif theme == '人物情報':
        report['actions'] = organize_people(notion_data)
    
    elif theme == '企業情報':
        report['actions'] = organize_companies(notion_data)
    
    elif theme == 'タスク・TODO':
        report['actions'] = organize_tasks(notion_data)
    
    elif theme == '知識・メモ':
        report['actions'] = organize_knowledge(notion_data)
    
    elif theme == '全体見直し':
        report['actions'] = review_all()
    
    elif theme == 'アーカイブ整理':
        report['actions'] = organize_archives()
    
    report['end_time'] = datetime.now().isoformat()
    
    return report

def organize_projects(notion_data):
    """プロジェクト情報整理"""
    actions = []
    
    # Notionからプロジェクト関連ページ抽出
    project_pages = [
        p for p in notion_data 
        if any(kw in p.get('properties', {}).get('Name', {}).get('title', [{}])[0].get('text', {}).get('content', '').lower()
               for kw in ['プロジェクト', 'project', 'pj'])
    ]
    
    for page in project_pages:
        # Claudeで分析
        # 適切なプロジェクトフォルダに配置
        # 進捗情報を更新
        pass
    
    return actions

def organize_people(notion_data):
    """人物情報整理"""
    actions = []
    
    # 人物関連ページ抽出
    # PROFILE.md更新
    
    return actions

# ... 他の整理関数 ...
```

### 3. cronジョブ設定

```python
# 毎日4:10実行
job = {
    'name': 'daily-memory-organizer',
    'schedule': {'kind': 'cron', 'expr': '10 4 * * *', 'tz': 'Asia/Tokyo'},
    'sessionTarget': 'isolated',
    'payload': {
        'kind': 'agentTurn',
        'message': '''メモリ整理開始（30分間稼働）

1. Notionデータ読み込み
2. 今日のテーマで整理実行
3. GitHubフォルダ整理
4. 報告書生成

完了後、Telegramに報告。

今日のテーマ: {曜日別}
'''
    },
    'delivery': {
        'mode': 'announce',
        'channel': 'telegram',
        'bestEffort': True
    }
}
```

---

## 📊 Telegram報告フォーマット

```
🧹 メモリ整理完了！（4:30）

📅 今日のテーマ: プロジェクト情報

✅ 実行内容:
━━━━━━━━━━━━━━━
1. Notionから5件のプロジェクト情報取得
2. 「ClimbBeyond」の進捗を更新
   → 03_Projects/_Active/ClimbBeyond/PROJECT.md
3. 「VideoPocket」を完了プロジェクトへ移動
   → 03_Projects/_Old/VideoPocket/
4. 新プロジェクト「Genspark協業」を追加
   → 03_Projects/_Active/Genspark/

📁 GitHub整理:
- data/gmail/2026-01-*.json → archive/2026-01/
- 重複ファイル3件削除

⏱️ 実行時間: 28分

次回: 明日4:10（火曜：人物情報整理）
```

---

## 🔒 安全機能

### 1. バックアップ
```python
# 整理前に必ずバックアップ
def backup_before_organize():
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = Path(f'backups/{timestamp}')
    # 全ファイルコピー
```

### 2. Dry Run
```python
# テストモード
def organize_memory(dry_run=True):
    if dry_run:
        print("変更内容をシミュレート（実際には変更しない）")
```

### 3. 変更履歴
```python
# 全変更をログ
changes_log = Path('memory/CHANGES_LOG.md')
# 何をいつどう変更したか記録
```

---

## 🚀 実装スケジュール

**今すぐ（深夜）:**
1. Notion API設定
2. 基本スクリプト実装
3. テスト実行

**明日朝4:10:**
初回実行（月曜：プロジェクト整理）

**1週間後:**
全曜日テーマ完成

---

**この設計でいい？実装開始する？🎯**
