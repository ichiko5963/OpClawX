#!/usr/bin/env python3
"""
議事録 → TODO自動連携
- 議事録テキストからTODOを抽出
- 自動でGoogle Tasksに追加
- 確認なしで追加、通知のみ
"""

import json
import re
import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Optional, Tuple

# Google Tasks API
SCRIPTS_PATH = Path(__file__).parent
sys.path.insert(0, str(SCRIPTS_PATH))
from google_tasks_direct import get_access_token as get_tasks_token, get_task_lists, add_task

def create_task(token: str, list_id: str, title: str, due: datetime = None) -> Dict:
    """タスクを作成"""
    import urllib.request
    
    url = f"https://tasks.googleapis.com/tasks/v1/lists/{list_id}/tasks"
    
    body = {"title": title}
    if due:
        body["due"] = due.strftime("%Y-%m-%dT%H:%M:%S.000Z")
    
    data = json.dumps(body).encode()
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header('Authorization', f'Bearer {token}')
    req.add_header('Content-Type', 'application/json')
    
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.loads(response.read())

# 設定
JSTの = timezone(timedelta(hours=9))
WORKSPACE = Path("/Users/ai-driven-work/Library/Mobile Documents/com~apple~CloudDocs/OpenClaw-Shared")

# タスクルーティング
ROUTING_RULES = {
    "aircle": ["aircle", "エアクル", "大山", "さき", "りょうせい", "れある", "x運用", "投稿"],
    "climbbeyond": ["climbbeyond", "クライムビヨンド", "ポート", "就活", "mountain", "求人"],
    "genspark": ["genspark", "ジェンスパーク", "インフルエンサー", "tiktok", "ちぃたん"],
    "外部案件": ["案件", "クライアント", "受注", "納品", "請求"],
}

def extract_todos_from_text(text: str) -> List[Dict]:
    """
    テキストからTODOを抽出
    パターン:
    - □ タスク内容
    - - [ ] タスク内容
    - TODO: タスク内容
    - 【TODO】タスク内容
    - ・〇〇する
    - 担当者名: やること
    """
    todos = []
    
    # パターン定義
    patterns = [
        r'^[□☐]\s*(.+)$',
        r'^-\s*\[\s*\]\s*(.+)$',
        r'^TODO[:：]\s*(.+)$',
        r'^【TODO】\s*(.+)$',
        r'^・\s*(.+(?:する|やる|確認|作成|送る|連絡))$',
        r'^(?:いち|市岡|自分)[:：]\s*(.+)$',
    ]
    
    lines = text.split('\n')
    for line in lines:
        line = line.strip()
        for pattern in patterns:
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                task_text = match.group(1).strip()
                if len(task_text) > 2:
                    todos.append({
                        'title': task_text,
                        'source_line': line
                    })
                break
    
    return todos

def extract_todos_with_ai(text: str, openai_key: str) -> List[Dict]:
    """
    GPT-4oでTODOを抽出（より高精度）
    """
    import urllib.request
    
    prompt = f"""以下の議事録・テキストから、いちさん（市岡）がやるべきTODOを抽出してください。

# ルール
1. いちさん本人がやるべきことのみ抽出
2. 他の人の担当は除外
3. 曖昧なものは具体的なアクションに変換
4. 期限があれば含める

# 出力形式（JSON）
[
  {{"title": "タスク内容", "deadline": "YYYY-MM-DD or null", "project": "AirCle/ClimbBeyond/Genspark/その他"}}
]

# テキスト
{text[:4000]}

JSON出力:"""

    body = json.dumps({
        "model": "gpt-4o",
        "messages": [
            {"role": "system", "content": "You are a task extraction assistant. Output only valid JSON."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 1000,
        "temperature": 0
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
            content = result['choices'][0]['message']['content']
            # JSONを抽出
            content = content.strip()
            if content.startswith('```'):
                content = re.sub(r'^```json?\n?', '', content)
                content = re.sub(r'\n?```$', '', content)
            return json.loads(content)
    except Exception as e:
        print(f"AI extraction error: {e}")
        return []

def route_task_to_list(task_title: str, project: str = None) -> str:
    """タスクを適切なリストにルーティング"""
    task_lower = task_title.lower()
    project_lower = (project or "").lower()
    
    # プロジェクト名から判定
    if "aircle" in project_lower or "エアクル" in project_lower:
        return "Aircle"
    if "climbbeyond" in project_lower or "climb" in project_lower:
        return "ClimbBeyond"
    if "genspark" in project_lower:
        return "外部案件"  # Gensparkは外部案件リストへ
    
    # タスク内容から判定
    for list_name, keywords in ROUTING_RULES.items():
        for keyword in keywords:
            if keyword.lower() in task_lower:
                if list_name == "aircle":
                    return "Aircle"
                elif list_name == "climbbeyond":
                    return "ClimbBeyond"
                elif list_name in ["genspark", "外部案件"]:
                    return "外部案件"
    
    return "マイタスク"

def add_todos_to_google_tasks(todos: List[Dict], dry_run: bool = False) -> List[Dict]:
    """
    TODOをGoogle Tasksに追加
    """
    if not todos:
        return []
    
    token = get_tasks_token()
    if not token:
        print("Error: Could not get Google Tasks token")
        return []
    
    # タスクリスト取得
    lists = get_task_lists()
    list_map = {l['title']: l['id'] for l in lists}
    
    results = []
    for todo in todos:
        title = todo.get('title', '')
        deadline = todo.get('deadline')
        project = todo.get('project', '')
        
        # ルーティング
        target_list = route_task_to_list(title, project)
        list_id = list_map.get(target_list) or list_map.get("マイタスク") or list(list_map.values())[0]
        
        if dry_run:
            results.append({
                'title': title,
                'list': target_list,
                'deadline': deadline,
                'status': 'dry_run'
            })
            continue
        
        # タスク作成
        try:
            due_date = None
            if deadline:
                due_date = datetime.strptime(deadline, "%Y-%m-%d").replace(hour=20, minute=0, tzinfo=JSTの)
            
            result = create_task(token, list_id, title, due=due_date)
            results.append({
                'title': title,
                'list': target_list,
                'deadline': deadline,
                'status': 'created',
                'task_id': result.get('id')
            })
        except Exception as e:
            results.append({
                'title': title,
                'list': target_list,
                'status': 'error',
                'error': str(e)
            })
    
    return results

def process_meeting_notes(text: str, use_ai: bool = True, dry_run: bool = False) -> Dict:
    """
    議事録を処理してTODOを自動追加
    """
    import os
    openai_key = os.environ.get('OPENAI_API_KEY', '')
    
    # TODO抽出
    if use_ai and openai_key:
        todos = extract_todos_with_ai(text, openai_key)
    else:
        todos = extract_todos_from_text(text)
    
    if not todos:
        return {
            'status': 'no_todos',
            'message': 'TODOが見つかりませんでした'
        }
    
    # Google Tasksに追加
    results = add_todos_to_google_tasks(todos, dry_run=dry_run)
    
    # サマリー生成
    created = [r for r in results if r.get('status') == 'created']
    errors = [r for r in results if r.get('status') == 'error']
    
    return {
        'status': 'success',
        'total': len(todos),
        'created': len(created),
        'errors': len(errors),
        'tasks': results
    }

def format_result_for_telegram(result: Dict) -> str:
    """結果をTelegram用にフォーマット"""
    if result['status'] == 'no_todos':
        return "📋 TODOが見つかりませんでした"
    
    lines = [f"✅ **{result['created']}件のTODOを自動追加しました**\n"]
    
    for task in result.get('tasks', []):
        status_icon = "✅" if task.get('status') == 'created' else "❌"
        deadline_str = f" (期限: {task['deadline']})" if task.get('deadline') else ""
        lines.append(f"{status_icon} {task['title']}\n   → {task['list']}{deadline_str}")
    
    if result.get('errors'):
        lines.append(f"\n⚠️ {result['errors']}件のエラーがありました")
    
    lines.append("\n_修正が必要な場合はGoogle Tasksで直接編集してください_")
    
    return "\n".join(lines)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='議事録からTODO自動抽出・追加')
    parser.add_argument('--file', '-f', help='議事録ファイルパス')
    parser.add_argument('--text', '-t', help='議事録テキスト（直接入力）')
    parser.add_argument('--dry-run', action='store_true', help='追加せずに確認のみ')
    parser.add_argument('--no-ai', action='store_true', help='AI抽出を使わない')
    
    args = parser.parse_args()
    
    text = ""
    if args.file:
        with open(args.file, 'r') as f:
            text = f.read()
    elif args.text:
        text = args.text
    else:
        # 標準入力から読み取り
        print("議事録テキストを入力してください（Ctrl+D で終了）:")
        text = sys.stdin.read()
    
    if not text.strip():
        print("テキストが空です")
        sys.exit(1)
    
    result = process_meeting_notes(text, use_ai=not args.no_ai, dry_run=args.dry_run)
    
    print("\n" + "="*50)
    print(format_result_for_telegram(result))
    print("="*50)
    
    # JSON出力も
    print("\nJSON:")
    print(json.dumps(result, ensure_ascii=False, indent=2))
