#!/usr/bin/env python3
"""
OpenClaw データ同期スクリプト（修正版）
GitHub Actions用
"""

import os
import sys
import json
import subprocess
from datetime import datetime, timedelta

# 環境変数から認証情報を取得
def get_gog_auth():
    """gog CLIの認証情報を使用"""
    try:
        result = subprocess.run(
            ['gog', 'auth', 'list', '--json'],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            return json.loads(result.stdout)
    except Exception as e:
        print(f"認証エラー: {e}")
    return None

def sync_gmail():
    """Gmail同期"""
    print("📧 Gmail同期開始...")
    try:
        result = subprocess.run(
            ['gog', 'gmail', 'search', 'newer_than:1d', '--max', '50', '--json'],
            capture_output=True,
            text=True,
            timeout=60
        )
        if result.returncode == 0:
            emails = json.loads(result.stdout)
            print(f"  ✅ {len(emails)}件のメールを取得")
            return emails
    except Exception as e:
        print(f"  ⚠️  Gmail同期エラー: {e}")
    return []

def sync_calendar():
    """カレンダー同期"""
    print("📅 Calendar同期開始...")
    today = datetime.now().strftime('%Y-%m-%d')
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    try:
        result = subprocess.run(
            ['gog', 'calendar', 'events', 'primary', 
             '--from', today, '--to', tomorrow, '--json'],
            capture_output=True,
            text=True,
            timeout=60
        )
        if result.returncode == 0:
            events = json.loads(result.stdout)
            print(f"  ✅ {len(events)}件のイベントを取得")
            return events
    except Exception as e:
        print(f"  ⚠️  Calendar同期エラー: {e}")
    return []

def sync_tasks():
    """タスク同期"""
    print("✅ Tasks同期開始...")
    try:
        result = subprocess.run(
            ['gog', 'tasks', 'list', '--max', '100', '--json'],
            capture_output=True,
            text=True,
            timeout=60
        )
        if result.returncode == 0:
            tasks = json.loads(result.stdout)
            print(f"  ✅ {len(tasks)}件のタスクを取得")
            return tasks
    except Exception as e:
        print(f"  ⚠️  Tasks同期エラー: {e}")
    return []

def sync_drive():
    """Drive同期"""
    print("🎤 Drive同期開始...")
    try:
        result = subprocess.run(
            ['gog', 'drive', 'search', 'mimeType:audio/*', '--max', '10', '--json'],
            capture_output=True,
            text=True,
            timeout=60
        )
        if result.returncode == 0:
            files = json.loads(result.stdout)
            print(f"  ✅ {len(files)}件のファイルを取得")
            return files
    except Exception as e:
        print(f"  ⚠️  Drive同期エラー: {e}")
    return []

def sync_sheets():
    """Sheets同期"""
    print("📊 Sheets同期開始...")
    # 経費スプレッドシートIDを環境変数から取得
    sheet_id = os.getenv('EXPENSE_SHEET_ID', '')
    if not sheet_id:
        print("  ⚠️ スプレッドシートIDが設定されていません")
        return []
    try:
        result = subprocess.run(
            ['gog', 'sheets', 'get', sheet_id, '経費!A1:Z100', '--json'],
            capture_output=True,
            text=True,
            timeout=60
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            print(f"  ✅ シートデータを取得")
            return data
    except Exception as e:
        print(f"  ⚠️  Sheets同期エラー: {e}")
    return []

def sync_docs():
    """Docs同期"""
    print("📄 Docs同期開始...")
    try:
        # Drive経由で最近のDocsを検索
        result = subprocess.run(
            ['gog', 'drive', 'search', 'mimeType:application/vnd.google-apps.document', 
             '--max', '10', '--json'],
            capture_output=True,
            text=True,
            timeout=60
        )
        if result.returncode == 0:
            docs = json.loads(result.stdout)
            print(f"  ✅ {len(docs)}件のドキュメントを取得")
            return docs
    except Exception as e:
        print(f"  ⚠️  Docs同期エラー: {e}")
    return []

def sync_slides():
    """Slides同期"""
    print("🎨 Slides同期開始...")
    try:
        result = subprocess.run(
            ['gog', 'drive', 'search', 'mimeType:application/vnd.google-apps.presentation',
             '--max', '10', '--json'],
            capture_output=True,
            text=True,
            timeout=60
        )
        if result.returncode == 0:
            slides = json.loads(result.stdout)
            print(f"  ✅ {len(slides)}件のスライドを取得")
            return slides
    except Exception as e:
        print(f"  ⚠️  Slides同期エラー: {e}")
    return []

def sync_docs_content():
    """ドキュメント内容同期（新規追加）"""
    print("📄 Docs内容同期開始...")
    docs = sync_docs()
    contents = []
    for doc in docs[:5]:  # 最新5件のみ
        try:
            doc_id = doc.get('id')
            if doc_id:
                result = subprocess.run(
                    ['gog', 'docs', 'export', doc_id, '--format', 'txt'],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                if result.returncode == 0:
                    contents.append({
                        'id': doc_id,
                        'title': doc.get('name', 'Unknown'),
                        'content': result.stdout[:1000]  # 先頭1000文字のみ
                    })
        except Exception as e:
            print(f"  ⚠️  Doc {doc.get('id')} 取得エラー: {e}")
    print(f"  ✅ {len(contents)}件のドキュメント内容を取得")
    return contents

def main():
    """メイン処理"""
    print("=" * 60)
    print("🚀 OpenClaw データ同期開始（修正版 / gog CLI使用）")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} JST")
    print("=" * 60)
    
    # 認証確認
    auth = get_gog_auth()
    if not auth:
        print("⚠️  認証情報が見つかりません。'gog auth add'を実行してください。")
        return 1
    
    print(f"✅ 認証済み: {auth.get('email', 'unknown')}")
    print()
    
    # 各種同期
    results = {}
    
    try:
        results['gmail'] = sync_gmail()
    except Exception as e:
        print(f"  ⚠️  Gmail同期スキップ: {e}")
    
    try:
        results['calendar'] = sync_calendar()
    except Exception as e:
        print(f"  ⚠️  Calendar同期スキップ: {e}")
    
    try:
        results['tasks'] = sync_tasks()
    except Exception as e:
        print(f"  ⚠️  Tasks同期スキップ: {e}")
    
    try:
        results['drive'] = sync_drive()
    except Exception as e:
        print(f"  ⚠️  Drive同期スキップ: {e}")
    
    try:
        results['sheets'] = sync_sheets()
    except Exception as e:
        print(f"  ⚠️  Sheets同期スキップ: {e}")
    
    try:
        results['docs'] = sync_docs()
    except Exception as e:
        print(f"  ⚠️  Docs同期スキップ: {e}")
    
    try:
        results['slides'] = sync_slides()
    except Exception as e:
        print(f"  ⚠️  Slides同期スキップ: {e}")
    
    try:
        results['docs_content'] = sync_docs_content()
    except Exception as e:
        print(f"  ⚠️  Docs内容同期スキップ: {e}")
    
    # 結果保存
    output_dir = os.getenv('SYNC_OUTPUT_DIR', './sync_output')
    os.makedirs(output_dir, exist_ok=True)
    
    output_file = os.path.join(output_dir, f'sync_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print()
    print("=" * 60)
    print(f"✅ 同期完了: {output_file}")
    print("=" * 60)
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
