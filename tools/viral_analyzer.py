#!/usr/bin/env python3
"""
X投稿バイラル度分析ツール
投稿の構造を分析し、改善ポイントを提案
"""

import os
import re
from datetime import datetime
from pathlib import Path

# バイラル要素のチェック項目
VIRAL_ELEMENTS = {
    'hook': {
        'patterns': [
            r'^【.+?】',  # 【速報】【衝撃】など
            r'^▼',
            r'^\d+[.．]',
        ],
        'weight': 2,
        'description': 'フック（注目を引く冒頭）'
    },
    'numbers': {
        'patterns': [
            r'\d+%',
            r'\$\d+',
            r'\d+万',
            r'\d+億',
            r'\d+倍',
            r'\d+件',
            r'\d+個',
        ],
        'weight': 1.5,
        'description': '具体的な数字'
    },
    'emoji': {
        'patterns': [
            r'[👇👆🔥⚡✅❌🎁💡📝📊🚨⭕]',
        ],
        'weight': 1,
        'description': '効果的な絵文字'
    },
    'structure': {
        'patterns': [
            r'①.+②',  # 番号付きリスト
            r'・.+・',  # 箇条書き
            r'→',  # 矢印による展開
        ],
        'weight': 1.5,
        'description': '読みやすい構造'
    },
    'cta': {
        'patterns': [
            r'👇',
            r'こちら',
            r'詳細は',
            r'チェック',
            r'保存推奨',
        ],
        'weight': 1,
        'description': 'CTA（行動喚起）'
    },
    'contrast': {
        'patterns': [
            r'今まで.+今',
            r'従来.+今',
            r'以前.+現在',
            r'vs',
            r'VS',
        ],
        'weight': 1.5,
        'description': '対比構造'
    },
}

def analyze_post(text: str) -> dict:
    """投稿を分析"""
    result = {
        'char_count': len(text),
        'line_count': len(text.split('\n')),
        'elements_found': [],
        'score': 0,
        'suggestions': [],
    }
    
    # 各要素をチェック
    for element_name, config in VIRAL_ELEMENTS.items():
        for pattern in config['patterns']:
            if re.search(pattern, text, re.DOTALL):
                result['elements_found'].append(config['description'])
                result['score'] += config['weight']
                break
    
    # 文字数チェック
    if result['char_count'] < 100:
        result['suggestions'].append('⚠️ 短すぎる可能性あり（100文字以上推奨）')
    elif result['char_count'] > 280:
        result['suggestions'].append('⚠️ 長文のためノート投稿として使用')
    
    # フックがない場合
    if 'フック（注目を引く冒頭）' not in result['elements_found']:
        result['suggestions'].append('💡 【速報】【衝撃】などのフックを追加')
    
    # 数字がない場合
    if '具体的な数字' not in result['elements_found']:
        result['suggestions'].append('💡 具体的な数字を追加すると説得力UP')
    
    # CTAがない場合
    if 'CTA（行動喚起）' not in result['elements_found']:
        result['suggestions'].append('💡 👇やリンクでCTAを追加')
    
    return result

def parse_posts_from_markdown(file_path: str) -> list[dict]:
    """マークダウンファイルから投稿を抽出"""
    posts = []
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    pattern = r'### 投稿(\d+): (.+?)\n(.+?)(?=\n---|\n### 投稿|\Z)'
    matches = re.findall(pattern, content, re.DOTALL)
    
    for match in matches:
        posts.append({
            'number': int(match[0]),
            'title': match[1].strip(),
            'body': match[2].strip(),
        })
    
    return posts

def get_score_label(score: float) -> str:
    """スコアに応じたラベル"""
    if score >= 6:
        return "🔥 バイラル期待大"
    elif score >= 4:
        return "⚡ 良い"
    elif score >= 2:
        return "📝 普通"
    else:
        return "⚠️ 改善推奨"

def main():
    workspace = Path(__file__).parent.parent
    projects_dir = workspace / 'projects'
    
    print("=" * 60)
    print("🔍 X投稿バイラル度分析")
    print("=" * 60)
    
    today = datetime.now().strftime('%Y-%m-%d')
    
    for account in ['aircle', 'ichiaimarketer']:
        post_file = projects_dir / f'x-posts-{today}-{account}.md'
        
        if not post_file.exists():
            pattern = f'x-posts-*-{account}.md'
            files = list(projects_dir.glob(pattern))
            if files:
                post_file = sorted(files)[-1]
            else:
                continue
        
        print(f"\n📱 @{account}")
        print(f"📄 {post_file.name}")
        print("-" * 60)
        
        posts = parse_posts_from_markdown(str(post_file))
        
        total_score = 0
        high_potential = []
        needs_improvement = []
        
        for post in posts:
            analysis = analyze_post(post['body'])
            total_score += analysis['score']
            
            if analysis['score'] >= 5:
                high_potential.append(post['number'])
            elif analysis['score'] < 3:
                needs_improvement.append((post['number'], analysis['suggestions']))
        
        avg_score = total_score / len(posts) if posts else 0
        
        print(f"\n📊 統計")
        print(f"  投稿数: {len(posts)}件")
        print(f"  平均スコア: {avg_score:.1f} {get_score_label(avg_score)}")
        
        if high_potential:
            print(f"\n🔥 バイラル期待大の投稿: {high_potential}")
        
        if needs_improvement:
            print(f"\n📝 改善推奨の投稿:")
            for num, suggestions in needs_improvement[:3]:
                print(f"  投稿{num}: {suggestions[0] if suggestions else '確認推奨'}")
    
    print("\n" + "=" * 60)

if __name__ == '__main__':
    main()
