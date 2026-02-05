#!/usr/bin/env python3
"""
X投稿品質スコアリングツール

投稿の品質を分析し、改善提案を行う

Usage:
    python x_quality_scorer.py projects/x-posts-2026-02-06-aircle.md
"""

import re
import sys
from pathlib import Path
from dataclasses import dataclass

@dataclass
class PostScore:
    num: int
    title: str
    content: str
    scores: dict
    total_score: float
    suggestions: list

def analyze_post(num: int, title: str, content: str) -> PostScore:
    """投稿を分析してスコアを計算"""
    scores = {}
    suggestions = []
    
    # 1. 文字数チェック (理想: 100-280文字)
    char_count = len(content)
    if 100 <= char_count <= 280:
        scores['length'] = 10
    elif 80 <= char_count < 100 or 280 < char_count <= 350:
        scores['length'] = 7
        suggestions.append("文字数を100-280文字に調整すると読みやすい")
    else:
        scores['length'] = 4
        if char_count < 80:
            suggestions.append("もう少し詳しく書くとエンゲージメントUP")
        else:
            suggestions.append("長すぎる。要約して280文字以内に")
    
    # 2. フック（最初の行）
    first_line = content.split('\n')[0]
    hook_patterns = [
        r'【[^】]+】',  # 【速報】など
        r'[0-9]+[%％]',  # 数字+%
        r'[0-9]+[倍万億円時間]',  # 数字+単位
        r'\$[0-9]',  # ドル表記
        r'衝撃|速報|注目|警告|革命|比較|解説|実践',  # パワーワード
    ]
    hook_count = sum(1 for p in hook_patterns if re.search(p, first_line))
    if hook_count >= 2:
        scores['hook'] = 10
    elif hook_count >= 1:
        scores['hook'] = 7
    else:
        scores['hook'] = 4
        suggestions.append("最初の行に【】や具体的数字を入れるとCTR向上")
    
    # 3. 具体性（数字・固有名詞）
    numbers = re.findall(r'[0-9]+', content)
    proper_nouns = re.findall(r'[A-Z][a-z]+|Claude|Cursor|OpenAI|Anthropic|Apple|Google', content)
    specificity = len(numbers) + len(proper_nouns)
    if specificity >= 5:
        scores['specificity'] = 10
    elif specificity >= 3:
        scores['specificity'] = 7
    else:
        scores['specificity'] = 4
        suggestions.append("具体的な数字やサービス名を追加すると説得力UP")
    
    # 4. 構造（箇条書き・改行）
    bullet_points = content.count('・') + content.count('→') + content.count('①')
    line_count = len([l for l in content.split('\n') if l.strip()])
    if bullet_points >= 3 and line_count >= 5:
        scores['structure'] = 10
    elif bullet_points >= 1 or line_count >= 4:
        scores['structure'] = 7
    else:
        scores['structure'] = 4
        suggestions.append("箇条書きを使うと視認性UP")
    
    # 5. CTA（Call to Action）
    cta_patterns = [
        r'Tips[:：]?',
        r'まとめ',
        r'結論',
        r'使って',
        r'試して',
        r'始め',
        r'選べ',
    ]
    has_cta = any(re.search(p, content) for p in cta_patterns)
    if has_cta:
        scores['cta'] = 10
    else:
        scores['cta'] = 5
        suggestions.append("最後にTipsやアクションを追加すると保存率UP")
    
    # 6. 絵文字（適度に使用）
    emoji_pattern = r'[\U0001F300-\U0001F9FF]|[👇✅❌🔥💪📝🚀]'
    emoji_count = len(re.findall(emoji_pattern, content))
    if 1 <= emoji_count <= 4:
        scores['emoji'] = 10
    elif emoji_count == 0:
        scores['emoji'] = 6
        suggestions.append("絵文字を1-2個追加すると視認性UP")
    else:
        scores['emoji'] = 6
        suggestions.append("絵文字が多すぎ。1-4個に減らす")
    
    # 総合スコア計算
    total = sum(scores.values()) / len(scores) * 10
    
    return PostScore(
        num=num,
        title=title,
        content=content,
        scores=scores,
        total_score=total,
        suggestions=suggestions
    )

def parse_posts(content: str) -> list[tuple]:
    """Markdownから投稿を抽出"""
    pattern = r'### 投稿(\d+)[:：]([^\n]*)\n(.*?)(?=### 投稿|\Z|## カテゴリ)'
    matches = re.findall(pattern, content, re.DOTALL)
    return [(int(m[0]), m[1].strip(), m[2].strip()) for m in matches]

def main():
    if len(sys.argv) < 2:
        print("Usage: python x_quality_scorer.py <markdown_file>")
        sys.exit(1)
    
    md_path = Path(sys.argv[1])
    if not md_path.exists():
        print(f"Error: File not found: {md_path}")
        sys.exit(1)
    
    content = md_path.read_text(encoding='utf-8')
    posts = parse_posts(content)
    
    print(f"\n📊 X投稿品質スコアリング: {md_path.name}")
    print("=" * 60)
    
    results = []
    for num, title, body in posts:
        result = analyze_post(num, title, body)
        results.append(result)
    
    # スコア順にソート
    results.sort(key=lambda x: x.total_score, reverse=True)
    
    # 結果表示
    print("\n🏆 スコアランキング")
    print("-" * 60)
    for i, r in enumerate(results[:5]):
        emoji = "🥇🥈🥉④⑤"[i]
        print(f"{emoji} #{r.num} {r.title[:20]}... - {r.total_score:.1f}点")
    
    print("\n⚠️ 改善が必要な投稿")
    print("-" * 60)
    for r in results[-3:]:
        print(f"  #{r.num} ({r.total_score:.1f}点): {r.title[:30]}")
        for s in r.suggestions[:2]:
            print(f"    💡 {s}")
    
    # 全体統計
    avg_score = sum(r.total_score for r in results) / len(results)
    print(f"\n📈 全体統計")
    print("-" * 60)
    print(f"  投稿数: {len(results)}")
    print(f"  平均スコア: {avg_score:.1f}点")
    print(f"  最高: {results[0].total_score:.1f}点 (#{results[0].num})")
    print(f"  最低: {results[-1].total_score:.1f}点 (#{results[-1].num})")
    
    # 改善が多い項目
    from collections import Counter
    all_suggestions = []
    for r in results:
        all_suggestions.extend(r.suggestions)
    
    if all_suggestions:
        print(f"\n💡 よくある改善点")
        print("-" * 60)
        for suggestion, count in Counter(all_suggestions).most_common(3):
            print(f"  [{count}件] {suggestion}")

if __name__ == '__main__':
    main()
