#!/usr/bin/env python3
"""
デイリーサマリー生成ツール
指定日のログを集約してサマリーを生成
"""

import os
from datetime import datetime, timedelta
from pathlib import Path
import re

def read_file_safe(path: Path) -> str:
    """安全にファイルを読み込む"""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception:
        return ""

def extract_completed_tasks(content: str) -> list[str]:
    """完了タスクを抽出"""
    tasks = []
    for line in content.split('\n'):
        if re.match(r'\s*-\s*\[x\]', line, re.IGNORECASE):
            task = re.sub(r'\s*-\s*\[x\]\s*', '', line)
            tasks.append(task.strip())
    return tasks

def extract_todos(content: str) -> list[str]:
    """未完了タスクを抽出"""
    todos = []
    for line in content.split('\n'):
        if re.match(r'\s*-\s*\[\s?\]', line):
            todo = re.sub(r'\s*-\s*\[\s?\]\s*', '', line)
            todos.append(todo.strip())
    return todos

def count_files_modified(workspace: Path, date: datetime) -> int:
    """指定日に更新されたファイル数をカウント"""
    count = 0
    target_date = date.date()
    
    for f in workspace.rglob('*'):
        if f.is_file() and not any(p.startswith('.') for p in f.parts):
            mtime = datetime.fromtimestamp(f.stat().st_mtime).date()
            if mtime == target_date:
                count += 1
    
    return count

def generate_summary(workspace: Path, date: datetime = None) -> str:
    """デイリーサマリーを生成"""
    if date is None:
        date = datetime.now()
    
    date_str = date.strftime('%Y-%m-%d')
    memory_file = workspace / 'memory' / f'{date_str}.md'
    
    summary = []
    summary.append(f"# デイリーサマリー {date_str}")
    summary.append("")
    
    # メモリファイルがある場合
    if memory_file.exists():
        content = read_file_safe(memory_file)
        
        completed = extract_completed_tasks(content)
        if completed:
            summary.append("## ✅ 完了したタスク")
            for task in completed[:10]:
                summary.append(f"- {task}")
            summary.append("")
        
        todos = extract_todos(content)
        if todos:
            summary.append("## 📋 残りのタスク")
            for todo in todos[:10]:
                summary.append(f"- {todo}")
            summary.append("")
    else:
        summary.append(f"⚠️ {date_str}のログファイルが見つかりません")
        summary.append("")
    
    # ファイル更新数
    modified = count_files_modified(workspace, date)
    summary.append("## 📊 統計")
    summary.append(f"- 更新されたファイル数: {modified}")
    summary.append("")
    
    # X投稿チェック
    projects = workspace / 'projects'
    for account in ['aircle', 'ichiaimarketer']:
        post_file = projects / f'x-posts-{date_str}-{account}.md'
        if post_file.exists():
            content = read_file_safe(post_file)
            post_count = len(re.findall(r'### 投稿\d+:', content))
            summary.append(f"- @{account} 投稿準備: {post_count}件")
    
    return '\n'.join(summary)

def main():
    workspace = Path(__file__).parent.parent
    
    print(generate_summary(workspace))
    print("\n" + "=" * 60)
    print("使い方:")
    print("  python3 daily_summary.py         # 今日のサマリー")
    print("  python3 daily_summary.py 2026-02-03  # 指定日のサマリー")
    print("=" * 60)

if __name__ == '__main__':
    import sys
    workspace = Path(__file__).parent.parent
    
    if len(sys.argv) > 1:
        try:
            date = datetime.strptime(sys.argv[1], '%Y-%m-%d')
            print(generate_summary(workspace, date))
        except ValueError:
            print(f"日付フォーマットエラー: {sys.argv[1]} (YYYY-MM-DD形式で指定)")
    else:
        print(generate_summary(workspace))
