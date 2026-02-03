#!/usr/bin/env python3
"""
Obsidianプロジェクトステータス確認ツール
全プロジェクトの状態をサマリー表示
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

def parse_status_file(content: str) -> dict:
    """STATUS.mdをパース"""
    result = {
        'phase': '不明',
        'actions': [],
        'blockers': [],
    }
    
    # フェーズ抽出
    phase_match = re.search(r'## 現在のフェーズ\n(.+)', content)
    if phase_match:
        result['phase'] = phase_match.group(1).strip()
    
    # アクション抽出
    action_section = re.search(r'## 次のアクション\n(.+?)(?=\n## |\Z)', content, re.DOTALL)
    if action_section:
        for line in action_section.group(1).split('\n'):
            if line.startswith('|') and not line.startswith('| アクション') and not line.startswith('|--'):
                parts = line.split('|')
                if len(parts) >= 3:
                    action = parts[1].strip()
                    if action and action != '（要確認）':
                        result['actions'].append(action)
    
    # ブロッカー抽出
    blocker_section = re.search(r'## ブロッカー\n(.+?)(?=\n## |\Z)', content, re.DOTALL)
    if blocker_section:
        text = blocker_section.group(1).strip()
        if text and text.lower() != 'なし':
            result['blockers'].append(text)
    
    return result

def parse_memory_file(content: str) -> dict:
    """MEMORY.mdをパース"""
    result = {
        'summary': '',
        'people': [],
        'last_update': None,
    }
    
    # 最終更新日
    update_match = re.search(r'最終更新: (\d{4}-\d{2}-\d{2})', content)
    if update_match:
        result['last_update'] = update_match.group(1)
    
    # 概要
    summary_match = re.search(r'## 概要\n(.+?)(?=\n## |\Z)', content, re.DOTALL)
    if summary_match:
        result['summary'] = summary_match.group(1).strip()[:100]
    
    # 関連人物
    people_section = re.search(r'## 関連人物\n(.+?)(?=\n## |\Z)', content, re.DOTALL)
    if people_section:
        for line in people_section.group(1).split('\n'):
            if line.startswith('-'):
                person = re.sub(r'\[\[(.+?)\]\]', r'\1', line.replace('-', '').strip())
                if person:
                    result['people'].append(person.split(' - ')[0])
    
    return result

def get_project_mtg_count(project_path: Path) -> int:
    """ミーティング議事録の数をカウント"""
    count = 0
    # MTGフォルダ内
    mtg_dir = project_path / 'MTG'
    if mtg_dir.exists():
        count += len(list(mtg_dir.glob('*.md')))
    # 直下のMTG_*.md
    count += len(list(project_path.glob('MTG_*.md')))
    return count

def main():
    workspace = Path(__file__).parent.parent
    obsidian = workspace / 'obsidian' / 'Ichioka Obsidian'
    active = obsidian / '03_Projects' / '_Active'
    old = obsidian / '03_Projects' / '_Old'
    
    print("=" * 70)
    print("📊 Obsidian プロジェクトステータス")
    print(f"   {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    if not active.exists():
        print("⚠️  プロジェクトディレクトリが見つかりません")
        return
    
    # アクティブプロジェクト
    print("\n🟢 Active Projects")
    print("-" * 70)
    
    for project_dir in sorted(active.iterdir()):
        if not project_dir.is_dir() or project_dir.name.startswith('.'):
            continue
        
        status_file = project_dir / 'STATUS.md'
        memory_file = project_dir / 'MEMORY.md'
        
        status = parse_status_file(read_file_safe(status_file))
        memory = parse_memory_file(read_file_safe(memory_file))
        mtg_count = get_project_mtg_count(project_dir)
        
        print(f"\n📁 {project_dir.name}")
        print(f"   フェーズ: {status['phase']}")
        if memory['summary']:
            print(f"   概要: {memory['summary'][:50]}...")
        if memory['people']:
            print(f"   関係者: {', '.join(memory['people'][:3])}")
        if memory['last_update']:
            print(f"   最終更新: {memory['last_update']}")
        print(f"   議事録: {mtg_count}件")
        
        if status['actions']:
            print(f"   ⚡ 次のアクション: {status['actions'][0]}")
        if status['blockers']:
            print(f"   🚧 ブロッカー: {status['blockers'][0]}")
    
    # 古いプロジェクト
    if old.exists():
        old_projects = [p.name for p in old.iterdir() if p.is_dir() and not p.name.startswith('.')]
        if old_projects:
            print("\n\n⚪ Archived Projects")
            print("-" * 70)
            for name in old_projects:
                print(f"   📦 {name}")
    
    print("\n" + "=" * 70)

if __name__ == '__main__':
    main()
