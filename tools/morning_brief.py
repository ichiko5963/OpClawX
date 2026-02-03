#!/usr/bin/env python3
"""
モーニングブリーフィング生成ツール
朝起きたときに確認すべき情報をまとめて表示
"""

import os
from datetime import datetime, timedelta
from pathlib import Path
import re

def read_file_safe(path: Path) -> str:
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception:
        return ""

def get_yesterday_summary(workspace: Path) -> dict:
    """昨日のサマリーを取得"""
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    log_file = workspace / 'memory' / f'{yesterday}.md'
    
    result = {
        'exists': False,
        'completed': [],
        'remaining': [],
    }
    
    if log_file.exists():
        result['exists'] = True
        content = read_file_safe(log_file)
        
        for line in content.split('\n'):
            if re.match(r'\s*-\s*\[x\]', line, re.IGNORECASE):
                task = re.sub(r'\s*-\s*\[x\]\s*', '', line)
                result['completed'].append(task.strip())
            elif re.match(r'\s*-\s*\[\s?\]', line):
                task = re.sub(r'\s*-\s*\[\s?\]\s*', '', line)
                result['remaining'].append(task.strip())
    
    return result

def get_x_posts_ready(workspace: Path) -> dict:
    """X投稿の準備状況を確認"""
    today = datetime.now().strftime('%Y-%m-%d')
    projects = workspace / 'projects'
    
    result = {
        'aircle': 0,
        'ichiaimarketer': 0,
    }
    
    for account in result.keys():
        post_file = projects / f'x-posts-{today}-{account}.md'
        if post_file.exists():
            content = read_file_safe(post_file)
            result[account] = len(re.findall(r'### 投稿\d+:', content))
    
    return result

def get_project_status(workspace: Path) -> list[dict]:
    """アクティブプロジェクトの状態を取得"""
    obsidian = workspace / 'obsidian' / 'Ichioka Obsidian'
    active = obsidian / '03_Projects' / '_Active'
    
    projects = []
    
    if not active.exists():
        return projects
    
    for project_dir in sorted(active.iterdir()):
        if not project_dir.is_dir() or project_dir.name.startswith('.'):
            continue
        
        status_file = project_dir / 'STATUS.md'
        if status_file.exists():
            content = read_file_safe(status_file)
            # 次のアクションを抽出
            action_match = re.search(r'\| ([^|]+) \|[^|]+\|[^|]+\|[^|]+\|', content)
            action = action_match.group(1).strip() if action_match else None
            if action and action not in ['アクション', '（要確認）', '---']:
                projects.append({
                    'name': project_dir.name,
                    'action': action,
                })
    
    return projects

def main():
    workspace = Path(__file__).parent.parent
    now = datetime.now()
    
    print("=" * 60)
    print(f"☀️ おはようございます！{now.strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)
    
    # 昨日のサマリー
    yesterday = get_yesterday_summary(workspace)
    print(f"\n📅 昨日の振り返り")
    print("-" * 40)
    if yesterday['exists']:
        print(f"  ✅ 完了タスク: {len(yesterday['completed'])}件")
        if yesterday['remaining']:
            print(f"  ⏳ 残りタスク: {len(yesterday['remaining'])}件")
            for task in yesterday['remaining'][:3]:
                print(f"      - {task[:40]}...")
    else:
        print("  （昨日のログなし）")
    
    # X投稿
    posts = get_x_posts_ready(workspace)
    print(f"\n📱 X投稿準備状況")
    print("-" * 40)
    print(f"  @aircle_ai: {posts['aircle']}件")
    print(f"  @ichiaimarketer: {posts['ichiaimarketer']}件")
    
    if posts['aircle'] == 0 and posts['ichiaimarketer'] == 0:
        print("  ⚠️ 今日の投稿がまだ準備されていません")
    
    # プロジェクト
    projects = get_project_status(workspace)
    if projects:
        print(f"\n🚀 プロジェクト次のアクション")
        print("-" * 40)
        for p in projects[:5]:
            print(f"  【{p['name']}】{p['action']}")
    
    # 今日の日付ファイル確認
    today_log = workspace / 'memory' / f"{now.strftime('%Y-%m-%d')}.md"
    print(f"\n📝 今日のログ")
    print("-" * 40)
    if today_log.exists():
        print(f"  ✅ {today_log.name} 作成済み")
    else:
        print(f"  📋 {today_log.name} を作成してください")
    
    print("\n" + "=" * 60)
    print("今日も頑張りましょう！🔥")
    print("=" * 60)

if __name__ == '__main__':
    main()
