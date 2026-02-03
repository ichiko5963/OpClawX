#!/usr/bin/env python3
"""
ワークスペースヘルスチェッカー
ワークスペースの状態を確認し、整理が必要なものを報告
"""

import os
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

def get_file_age(file_path: Path) -> timedelta:
    """ファイルの経過時間を取得"""
    mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
    return datetime.now() - mtime

def check_inbox(workspace: Path) -> list[str]:
    """inboxの状態をチェック"""
    issues = []
    inbox = workspace / 'pi' / 'inbox'
    
    if not inbox.exists():
        return ["inboxディレクトリが存在しません"]
    
    files = list(inbox.glob('*'))
    non_readme = [f for f in files if f.name.lower() != 'readme.md' and not f.name.startswith('.')]
    
    if non_readme:
        issues.append(f"inbox内に{len(non_readme)}個のファイルがあります: {[f.name for f in non_readme[:5]]}")
    
    return issues

def check_memory(workspace: Path) -> list[str]:
    """memoryの状態をチェック"""
    issues = []
    memory_dir = workspace / 'memory'
    
    if not memory_dir.exists():
        return ["memoryディレクトリが存在しません"]
    
    # 今日と昨日のログがあるか
    today = datetime.now().strftime('%Y-%m-%d')
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    if not (memory_dir / f'{today}.md').exists():
        issues.append(f"今日({today})の日次ログがありません")
    
    # 古いメモリファイル
    for f in memory_dir.glob('*.md'):
        age = get_file_age(f)
        if age > timedelta(days=30):
            issues.append(f"古いメモリファイル: {f.name} ({age.days}日前)")
    
    return issues

def check_projects(workspace: Path) -> list[str]:
    """projectsの状態をチェック"""
    issues = []
    projects = workspace / 'projects'
    
    if not projects.exists():
        return ["projectsディレクトリが存在しません"]
    
    # X投稿ファイルの確認
    x_posts = list(projects.glob('x-posts-*.md'))
    if not x_posts:
        issues.append("X投稿ファイルがありません")
    else:
        # 最新のファイルの日付を確認
        latest = sorted(x_posts)[-1]
        # ファイル名から日付を抽出
        import re
        match = re.search(r'x-posts-(\d{4}-\d{2}-\d{2})', latest.name)
        if match:
            file_date = datetime.strptime(match.group(1), '%Y-%m-%d')
            if (datetime.now() - file_date) > timedelta(days=3):
                issues.append(f"X投稿が3日以上更新されていません (最新: {match.group(1)})")
    
    return issues

def check_git_status(workspace: Path) -> list[str]:
    """Gitの状態をチェック"""
    issues = []
    import subprocess
    
    try:
        result = subprocess.run(
            ['git', 'status', '--porcelain'],
            cwd=workspace,
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            changed = result.stdout.strip().split('\n')
            changed = [c for c in changed if c]
            if len(changed) > 10:
                issues.append(f"コミットされていない変更が{len(changed)}個あります")
    except Exception as e:
        issues.append(f"Git状態の確認に失敗: {e}")
    
    return issues

def check_obsidian(workspace: Path) -> list[str]:
    """Obsidianの状態をチェック"""
    issues = []
    obsidian = workspace / 'obsidian' / 'Ichioka Obsidian'
    
    if not obsidian.exists():
        return ["Obsidian Vaultが見つかりません"]
    
    # Inboxをチェック
    inbox = obsidian / '00_Inbox'
    if inbox.exists():
        files = list(inbox.glob('*'))
        non_system = [f for f in files if not f.name.startswith('.')]
        if len(non_system) > 5:
            issues.append(f"Obsidian Inboxに{len(non_system)}個のファイルがあります")
    
    return issues

def main():
    workspace = Path(__file__).parent.parent
    
    print("=" * 60)
    print("🏥 ワークスペースヘルスチェック")
    print(f"   {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    all_issues = []
    
    # 各チェックを実行
    checks = [
        ("📥 Inbox", check_inbox),
        ("🧠 Memory", check_memory),
        ("📁 Projects", check_projects),
        ("🔧 Git", check_git_status),
        ("📝 Obsidian", check_obsidian),
    ]
    
    for name, check_func in checks:
        print(f"\n{name}")
        print("-" * 40)
        issues = check_func(workspace)
        if issues:
            for issue in issues:
                print(f"  ⚠️  {issue}")
            all_issues.extend(issues)
        else:
            print("  ✅ 問題なし")
    
    # サマリー
    print("\n" + "=" * 60)
    if all_issues:
        print(f"📊 合計 {len(all_issues)} 件の課題が見つかりました")
    else:
        print("✨ ワークスペースは健全です！")
    print("=" * 60)

if __name__ == '__main__':
    main()
