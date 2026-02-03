#!/usr/bin/env python3
"""
効率化提案ジェネレーター
ワークスペースの使用状況を分析し、効率化の提案を生成
"""

import os
from datetime import datetime, timedelta
from pathlib import Path
import re
from collections import Counter

def read_file_safe(path: Path) -> str:
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception:
        return ""

def analyze_memory_patterns(workspace: Path) -> list[dict]:
    """メモリファイルのパターンを分析"""
    memory_dir = workspace / 'memory'
    patterns = []
    
    if not memory_dir.exists():
        return patterns
    
    # 過去7日間のログを分析
    todo_patterns = Counter()
    completed_patterns = Counter()
    
    for i in range(7):
        date = datetime.now() - timedelta(days=i)
        log_file = memory_dir / f'{date.strftime("%Y-%m-%d")}.md'
        
        if log_file.exists():
            content = read_file_safe(log_file)
            
            # タスクの種類を抽出
            for line in content.split('\n'):
                if '投稿' in line or 'X' in line:
                    todo_patterns['X投稿'] += 1
                if 'ツール' in line or '開発' in line:
                    todo_patterns['ツール開発'] += 1
                if '整理' in line or 'inbox' in line.lower():
                    todo_patterns['整理作業'] += 1
                if 'Obsidian' in line:
                    todo_patterns['Obsidian'] += 1
    
    return todo_patterns

def check_automation_opportunities(workspace: Path) -> list[str]:
    """自動化の機会を検出"""
    opportunities = []
    
    # X投稿の自動化
    projects = workspace / 'projects'
    if projects.exists():
        x_files = list(projects.glob('x-posts-*.md'))
        if len(x_files) > 3:
            opportunities.append({
                'title': 'X投稿の自動スケジューリング',
                'description': 'BufferやTypefullyと連携して自動投稿を設定',
                'impact': '高',
                'effort': '中',
            })
    
    # Git自動同期
    bin_dir = workspace / 'bin'
    if (bin_dir / 'git-auto-sync.sh').exists():
        opportunities.append({
            'title': 'Git自動プッシュの強化',
            'description': 'リモートリポジトリへの自動pushを追加',
            'impact': '中',
            'effort': '低',
        })
    
    # デイリーレポートの自動生成
    opportunities.append({
        'title': 'デイリーレポートの自動Telegram送信',
        'description': '朝6時に昨日のサマリーを自動送信',
        'impact': '中',
        'effort': '低',
    })
    
    # Obsidian連携
    obsidian = workspace / 'obsidian' / 'Ichioka Obsidian'
    if obsidian.exists():
        opportunities.append({
            'title': 'Obsidian Inboxの自動整理',
            'description': '未整理ファイルを自動でカテゴリ分け',
            'impact': '高',
            'effort': '高',
        })
    
    return opportunities

def generate_suggestions() -> list[dict]:
    """提案を生成"""
    workspace = Path(__file__).parent.parent
    
    suggestions = []
    opportunities = check_automation_opportunities(workspace)
    
    for opp in opportunities:
        suggestions.append(opp)
    
    # 追加の提案
    suggestions.append({
        'title': 'SlackからObsidianへの自動保存',
        'description': 'AirCle Slackの重要メッセージを自動でObsidianに保存',
        'impact': '高',
        'effort': '中',
    })
    
    suggestions.append({
        'title': 'メール要約の自動生成',
        'description': '毎朝、未読メールの要約をDiscordに投稿',
        'impact': '中',
        'effort': '中',
    })
    
    suggestions.append({
        'title': 'カレンダーイベントのリマインダー強化',
        'description': 'イベント30分前にTelegramで通知',
        'impact': '中',
        'effort': '低',
    })
    
    return suggestions

def main():
    print("=" * 60)
    print("💡 効率化提案ジェネレーター")
    print(f"   {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    suggestions = generate_suggestions()
    
    # インパクト順にソート
    impact_order = {'高': 0, '中': 1, '低': 2}
    suggestions.sort(key=lambda x: (impact_order.get(x['impact'], 3), x['title']))
    
    print("\n📋 提案一覧")
    print("-" * 60)
    
    for i, s in enumerate(suggestions, 1):
        print(f"\n{i}. {s['title']}")
        print(f"   📝 {s['description']}")
        print(f"   🎯 インパクト: {s['impact']} | 🔧 工数: {s['effort']}")
    
    print("\n" + "=" * 60)
    print("実装したい提案があれば、番号を教えてください！")
    print("=" * 60)

if __name__ == '__main__':
    main()
