#!/usr/bin/env python3
"""
セッション振り返りツール
指定期間のセッションログを分析し、学びとパターンを抽出
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

def extract_keywords(content: str) -> list[str]:
    """キーワードを抽出"""
    # よく出てくる技術キーワード
    tech_keywords = [
        'Claude', 'Claude Code', 'Cursor', 'Vercel', 'Next.js', 'React',
        'API', 'Git', 'GitHub', 'OpenClaw', 'Supabase', 'AI', 'LLM',
        'Vibe Coding', 'MCP', 'TTS', 'ElevenLabs', 'Gemini', 'GPT',
        'Python', 'JavaScript', 'TypeScript', 'Node.js', 'Docker',
        'Obsidian', 'Telegram', 'Discord', 'Slack'
    ]
    
    found = []
    content_lower = content.lower()
    for kw in tech_keywords:
        if kw.lower() in content_lower:
            found.append(kw)
    
    return found

def extract_completed_tasks(content: str) -> list[str]:
    """完了タスクを抽出"""
    tasks = []
    for line in content.split('\n'):
        if re.match(r'\s*-\s*\[x\]', line, re.IGNORECASE):
            task = re.sub(r'\s*-\s*\[x\]\s*', '', line)
            tasks.append(task.strip())
    return tasks

def analyze_session_logs(workspace: Path, days: int = 7) -> dict:
    """過去N日間のセッションログを分析"""
    memory_dir = workspace / 'memory'
    results = {
        'total_days': 0,
        'total_tasks': 0,
        'keywords': Counter(),
        'tasks_by_day': {},
    }
    
    for i in range(days):
        date = datetime.now() - timedelta(days=i)
        date_str = date.strftime('%Y-%m-%d')
        log_file = memory_dir / f'{date_str}.md'
        
        if log_file.exists():
            content = read_file_safe(log_file)
            results['total_days'] += 1
            
            # タスク抽出
            tasks = extract_completed_tasks(content)
            results['tasks_by_day'][date_str] = len(tasks)
            results['total_tasks'] += len(tasks)
            
            # キーワード抽出
            keywords = extract_keywords(content)
            for kw in keywords:
                results['keywords'][kw] += 1
    
    return results

def main():
    workspace = Path(__file__).parent.parent
    
    print("=" * 60)
    print("📈 セッション振り返り分析")
    print(f"   分析期間: 過去7日間")
    print("=" * 60)
    
    results = analyze_session_logs(workspace)
    
    print(f"\n📊 基本統計")
    print("-" * 40)
    print(f"  ログのある日数: {results['total_days']}日")
    print(f"  完了タスク総数: {results['total_tasks']}件")
    if results['total_days'] > 0:
        avg = results['total_tasks'] / results['total_days']
        print(f"  1日平均タスク: {avg:.1f}件")
    
    print(f"\n📅 日別タスク数")
    print("-" * 40)
    for date, count in sorted(results['tasks_by_day'].items(), reverse=True):
        bar = '█' * min(count, 20)
        print(f"  {date}: {bar} {count}件")
    
    print(f"\n🔑 よく使われた技術")
    print("-" * 40)
    for keyword, count in results['keywords'].most_common(10):
        print(f"  {keyword}: {count}回")
    
    print("\n" + "=" * 60)
    print("💡 振り返りのポイント")
    print("-" * 40)
    
    if results['total_tasks'] > 20:
        print("  ✅ 高い生産性を維持しています")
    elif results['total_tasks'] > 10:
        print("  ⚡ 安定したペースです")
    else:
        print("  📝 タスクのログ記録を増やしましょう")
    
    top_tech = results['keywords'].most_common(1)
    if top_tech:
        print(f"  🔧 最も多く使った技術: {top_tech[0][0]}")
    
    print("=" * 60)

if __name__ == '__main__':
    main()
