#!/usr/bin/env python3
"""
深夜セッションレポート生成ツール

機能:
1. 深夜セッション中に生成/更新されたファイルを検出
2. Git diffから変更内容を分析
3. 成果サマリーをMarkdownで生成
4. Discord/Telegramへの報告用テキストを生成

Usage:
    python session_reporter.py --session-start "2026-02-07 01:00"
    python session_reporter.py --hours 5  # 過去5時間分
"""

import argparse
import subprocess
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, List, Dict
import json

def get_workspace_root() -> Path:
    """ワークスペースルートを取得"""
    return Path('/Users/ai-driven-work/Library/Mobile Documents/com~apple~CloudDocs/OpenClaw-Shared')


def get_modified_files(since: datetime) -> List[Dict]:
    """指定時刻以降に変更されたファイルを取得"""
    workspace = get_workspace_root()
    since_timestamp = since.timestamp()
    
    modified_files = []
    
    for path in workspace.rglob('*'):
        if path.is_file():
            # 隠しファイル・ディレクトリをスキップ
            if any(part.startswith('.') for part in path.parts):
                continue
            # node_modulesをスキップ
            if 'node_modules' in path.parts:
                continue
            
            try:
                mtime = path.stat().st_mtime
                if mtime >= since_timestamp:
                    modified_files.append({
                        'path': path.relative_to(workspace),
                        'mtime': datetime.fromtimestamp(mtime),
                        'size': path.stat().st_size,
                        'extension': path.suffix
                    })
            except:
                pass
    
    # 更新時刻でソート
    modified_files.sort(key=lambda x: x['mtime'], reverse=True)
    return modified_files


def get_git_diff(since: datetime) -> str:
    """Git diffを取得"""
    workspace = get_workspace_root()
    since_str = since.strftime('%Y-%m-%d %H:%M:%S')
    
    try:
        result = subprocess.run(
            ['git', 'diff', '--stat', f'--since={since_str}', 'HEAD'],
            cwd=str(workspace),
            capture_output=True,
            text=True
        )
        return result.stdout
    except:
        return ""


def get_git_log(since: datetime) -> List[Dict]:
    """Gitログを取得"""
    workspace = get_workspace_root()
    since_str = since.strftime('%Y-%m-%d %H:%M:%S')
    
    try:
        result = subprocess.run(
            ['git', 'log', f'--since={since_str}', '--pretty=format:%H|%s|%ai', '--no-merges'],
            cwd=str(workspace),
            capture_output=True,
            text=True
        )
        
        commits = []
        for line in result.stdout.strip().split('\n'):
            if line:
                parts = line.split('|')
                if len(parts) >= 3:
                    commits.append({
                        'hash': parts[0][:7],
                        'message': parts[1],
                        'date': parts[2]
                    })
        return commits
    except:
        return []


def categorize_files(files: List[Dict]) -> Dict[str, List[Dict]]:
    """ファイルをカテゴリ別に分類"""
    categories = {
        'scripts': [],      # Pythonスクリプト
        'tools': [],        # ツール
        'html': [],         # HTML（X投稿など）
        'markdown': [],     # ドキュメント
        'memory': [],       # メモリファイル
        'config': [],       # 設定ファイル
        'other': []         # その他
    }
    
    for f in files:
        path_str = str(f['path'])
        ext = f['extension'].lower()
        
        if path_str.startswith('scripts/'):
            categories['scripts'].append(f)
        elif path_str.startswith('tools/'):
            categories['tools'].append(f)
        elif path_str.startswith('public/') or ext == '.html':
            categories['html'].append(f)
        elif path_str.startswith('memory/') or 'MEMORY' in path_str:
            categories['memory'].append(f)
        elif ext == '.md':
            categories['markdown'].append(f)
        elif ext in ['.json', '.yaml', '.yml', '.toml']:
            categories['config'].append(f)
        else:
            categories['other'].append(f)
    
    return categories


def generate_report(
    session_start: datetime,
    session_end: datetime,
    modified_files: List[Dict],
    commits: List[Dict]
) -> str:
    """セッションレポートを生成"""
    
    categories = categorize_files(modified_files)
    
    report = f"""# 🌙 深夜セッションレポート

**セッション時間**: {session_start.strftime('%Y-%m-%d %H:%M')} - {session_end.strftime('%H:%M')} JST
**稼働時間**: {(session_end - session_start).seconds // 3600}時間{((session_end - session_start).seconds % 3600) // 60}分
**変更ファイル数**: {len(modified_files)}件
**コミット数**: {len(commits)}件

---

## 📊 成果サマリー

"""
    
    # カテゴリ別サマリー
    if categories['scripts']:
        report += f"### 🐍 スクリプト ({len(categories['scripts'])}件)\n"
        for f in categories['scripts'][:10]:
            report += f"- `{f['path']}` ({f['size']} bytes)\n"
        report += "\n"
    
    if categories['tools']:
        report += f"### 🔧 ツール ({len(categories['tools'])}件)\n"
        for f in categories['tools'][:10]:
            report += f"- `{f['path']}` ({f['size']} bytes)\n"
        report += "\n"
    
    if categories['html']:
        report += f"### 🌐 HTML/X投稿 ({len(categories['html'])}件)\n"
        for f in categories['html'][:10]:
            report += f"- `{f['path']}`\n"
        report += "\n"
    
    if categories['markdown']:
        report += f"### 📝 ドキュメント ({len(categories['markdown'])}件)\n"
        for f in categories['markdown'][:10]:
            report += f"- `{f['path']}`\n"
        report += "\n"
    
    if categories['memory']:
        report += f"### 🧠 メモリ更新 ({len(categories['memory'])}件)\n"
        for f in categories['memory'][:10]:
            report += f"- `{f['path']}`\n"
        report += "\n"
    
    # コミット履歴
    if commits:
        report += "## 📚 コミット履歴\n\n"
        for commit in commits[:10]:
            report += f"- `{commit['hash']}` {commit['message']}\n"
        report += "\n"
    
    return report


def generate_discord_message(
    session_start: datetime,
    session_end: datetime,
    modified_files: List[Dict],
    x_posts_urls: List[str] = None
) -> str:
    """Discord用のメッセージを生成"""
    
    categories = categorize_files(modified_files)
    duration_hours = (session_end - session_start).seconds // 3600
    duration_mins = ((session_end - session_start).seconds % 3600) // 60
    
    message = f"""🌙 **深夜セッション完了** ({session_start.strftime('%H:%M')} - {session_end.strftime('%H:%M')} JST)

⏱️ **稼働時間**: {duration_hours}時間{duration_mins}分
📁 **変更ファイル**: {len(modified_files)}件

---

**📊 今夜の成果:**
"""
    
    if categories['scripts']:
        message += f"\n🐍 **スクリプト**: {len(categories['scripts'])}件更新"
    if categories['tools']:
        message += f"\n🔧 **ツール**: {len(categories['tools'])}件更新"
    if categories['html']:
        message += f"\n🌐 **X投稿HTML**: {len(categories['html'])}件生成"
    if categories['markdown']:
        message += f"\n📝 **ドキュメント**: {len(categories['markdown'])}件更新"
    
    if x_posts_urls:
        message += "\n\n**🔗 X投稿リンク:**\n"
        for url in x_posts_urls:
            message += f"<{url}>\n"
    
    return message


def main():
    parser = argparse.ArgumentParser(description='深夜セッションレポート生成')
    parser.add_argument('--session-start', type=str, help='セッション開始時刻 (YYYY-MM-DD HH:MM)')
    parser.add_argument('--hours', type=int, default=5, help='過去何時間分をレポートするか')
    parser.add_argument('--output', type=str, help='レポート出力先')
    parser.add_argument('--discord', action='store_true', help='Discord用メッセージを出力')
    
    args = parser.parse_args()
    
    # セッション開始時刻を決定
    if args.session_start:
        session_start = datetime.strptime(args.session_start, '%Y-%m-%d %H:%M')
    else:
        session_start = datetime.now() - timedelta(hours=args.hours)
    
    session_end = datetime.now()
    
    print(f"📊 セッション分析中: {session_start.strftime('%H:%M')} - {session_end.strftime('%H:%M')}")
    
    # 変更ファイルを取得
    modified_files = get_modified_files(session_start)
    print(f"   変更ファイル: {len(modified_files)}件")
    
    # コミット履歴を取得
    commits = get_git_log(session_start)
    print(f"   コミット: {len(commits)}件")
    
    if args.discord:
        # Discord用メッセージを出力
        message = generate_discord_message(session_start, session_end, modified_files)
        print("\n" + message)
    else:
        # フルレポートを生成
        report = generate_report(session_start, session_end, modified_files, commits)
        
        if args.output:
            Path(args.output).write_text(report, encoding='utf-8')
            print(f"\n✅ レポート保存: {args.output}")
        else:
            print("\n" + report)
    
    return 0


if __name__ == '__main__':
    exit(main())
