#!/usr/bin/env python3
"""
Weekly Report Generator
週次レポートを自動生成する。深夜セッションの成果物、X投稿数、メモリ更新、ツール開発等をまとめる。
"""

import os
import re
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

WORKSPACE = os.environ.get(
    'OPENCLAW_WORKSPACE',
    '/Users/ai-driven-work/Documents/OpenClaw-Workspace'
)


def get_week_dates(target_date=None):
    """対象週の月曜〜日曜の日付リストを取得"""
    if target_date is None:
        target_date = datetime.now()
    
    # 月曜日を起点にする
    monday = target_date - timedelta(days=target_date.weekday())
    return [monday + timedelta(days=i) for i in range(7)]


def count_x_posts(week_dates):
    """週のX投稿ファイルと投稿数を集計"""
    projects_dir = Path(WORKSPACE) / 'projects'
    if not projects_dir.exists():
        return {'aircle': 0, 'ichiaimarketer': 0, 'files': []}
    
    aircle_count = 0
    ichi_count = 0
    files = []
    
    for date in week_dates:
        date_str = date.strftime('%Y-%m-%d')
        
        for account in ['aircle', 'ichiaimarketer']:
            md_file = projects_dir / f'x-posts-{date_str}-{account}.md'
            html_file = projects_dir / f'x-posts-{date_str}-{account}.html'
            
            if md_file.exists():
                content = md_file.read_text(encoding='utf-8')
                # 投稿数をカウント（## 投稿N パターン）
                posts = len(re.findall(r'^## 投稿\d+', content, re.MULTILINE))
                if posts == 0:
                    # 別パターンもチェック
                    posts = len(re.findall(r'^## ■|^##\s+\d+\.', content, re.MULTILINE))
                
                if account == 'aircle':
                    aircle_count += posts
                else:
                    ichi_count += posts
                
                files.append({
                    'file': str(md_file.name),
                    'account': account,
                    'posts': posts,
                    'has_html': html_file.exists(),
                })
    
    return {
        'aircle': aircle_count,
        'ichiaimarketer': ichi_count,
        'total': aircle_count + ichi_count,
        'files': files,
    }


def analyze_memory_updates(week_dates):
    """週のメモリ更新を分析"""
    memory_dir = Path(WORKSPACE) / 'memory'
    if not memory_dir.exists():
        return {'days_logged': 0, 'entries': []}
    
    entries = []
    for date in week_dates:
        date_str = date.strftime('%Y-%m-%d')
        md_file = memory_dir / f'{date_str}.md'
        
        if md_file.exists():
            content = md_file.read_text(encoding='utf-8')
            # セクション数をカウント
            sections = len(re.findall(r'^##\s', content, re.MULTILINE))
            word_count = len(content)
            
            entries.append({
                'date': date_str,
                'sections': sections,
                'chars': word_count,
            })
    
    return {
        'days_logged': len(entries),
        'entries': entries,
    }


def check_tools_created(week_dates):
    """週に作成/更新されたツールをチェック"""
    tools_dir = Path(WORKSPACE) / 'tools'
    if not tools_dir.exists():
        return []
    
    start = week_dates[0]
    end = week_dates[-1] + timedelta(days=1)
    
    new_tools = []
    for f in tools_dir.iterdir():
        if f.suffix == '.py':
            mtime = datetime.fromtimestamp(f.stat().st_mtime)
            if start <= mtime <= end:
                new_tools.append({
                    'name': f.stem,
                    'modified': mtime.strftime('%Y-%m-%d %H:%M'),
                    'size': f.stat().st_size,
                })
    
    return sorted(new_tools, key=lambda x: x['modified'], reverse=True)


def check_git_activity(week_dates):
    """週のgitコミット数をチェック"""
    start_date = week_dates[0].strftime('%Y-%m-%d')
    end_date = (week_dates[-1] + timedelta(days=1)).strftime('%Y-%m-%d')
    
    try:
        import subprocess
        result = subprocess.run(
            ['git', 'log', f'--since={start_date}', f'--until={end_date}',
             '--oneline', '--no-merges'],
            capture_output=True, text=True, cwd=WORKSPACE
        )
        commits = [line.strip() for line in result.stdout.strip().split('\n') if line.strip()]
        return len(commits)
    except Exception:
        return -1  # git利用不可


def check_obsidian_updates(week_dates):
    """週のObsidian更新をチェック"""
    vault_dir = Path(WORKSPACE) / 'obsidian' / 'Ichioka Obsidian'
    if not vault_dir.exists():
        return {'updated_files': 0}
    
    start = week_dates[0]
    end = week_dates[-1] + timedelta(days=1)
    
    count = 0
    for f in vault_dir.rglob('*.md'):
        try:
            mtime = datetime.fromtimestamp(f.stat().st_mtime)
            if start <= mtime <= end:
                count += 1
        except Exception:
            pass
    
    return {'updated_files': count}


def generate_report(target_date=None):
    """週次レポートを生成"""
    week_dates = get_week_dates(target_date)
    start_str = week_dates[0].strftime('%Y-%m-%d')
    end_str = week_dates[-1].strftime('%Y-%m-%d')
    
    # データ収集
    x_posts = count_x_posts(week_dates)
    memory = analyze_memory_updates(week_dates)
    tools = check_tools_created(week_dates)
    git_commits = check_git_activity(week_dates)
    obsidian = check_obsidian_updates(week_dates)
    
    # レポート生成
    report = []
    report.append(f"# 📊 週次レポート ({start_str} 〜 {end_str})")
    report.append("")
    report.append("## 📈 サマリー")
    report.append(f"- X投稿作成: **{x_posts['total']}投稿**")
    report.append(f"  - AirCle: {x_posts['aircle']}投稿")
    report.append(f"  - いち@AIxマーケ: {x_posts['ichiaimarketer']}投稿")
    report.append(f"- メモリ記録: **{memory['days_logged']}日分**")
    report.append(f"- ツール作成/更新: **{len(tools)}個**")
    report.append(f"- Gitコミット: **{git_commits}回**")
    report.append(f"- Obsidian更新: **{obsidian['updated_files']}ファイル**")
    report.append("")
    
    # X投稿詳細
    if x_posts['files']:
        report.append("## 🐦 X投稿ファイル")
        for f in x_posts['files']:
            html_mark = "📄" if f['has_html'] else "📝"
            report.append(f"- {html_mark} `{f['file']}` ({f['posts']}投稿)")
        report.append("")
    
    # ツール詳細
    if tools:
        report.append("## 🔧 ツール作成/更新")
        for t in tools:
            report.append(f"- `{t['name']}.py` ({t['modified']}, {t['size']}B)")
        report.append("")
    
    # メモリ詳細
    if memory['entries']:
        report.append("## 📝 メモリログ")
        for e in memory['entries']:
            report.append(f"- {e['date']}: {e['sections']}セクション, {e['chars']}文字")
        report.append("")
    
    return '\n'.join(report)


def main():
    target_date = None
    if len(sys.argv) >= 2:
        target_date = datetime.strptime(sys.argv[1], '%Y-%m-%d')
    
    report = generate_report(target_date)
    print(report)
    
    # ファイルに保存
    week_dates = get_week_dates(target_date)
    start_str = week_dates[0].strftime('%Y-%m-%d')
    output_path = Path(WORKSPACE) / 'memory' / f'weekly-report-{start_str}.md'
    output_path.write_text(report, encoding='utf-8')
    print(f"\n📁 保存: {output_path}")


if __name__ == '__main__':
    main()
