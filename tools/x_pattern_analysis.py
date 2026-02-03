#!/usr/bin/env python3
"""
X投稿パターン分類ツール
投稿を型（パターン）別に分類し、各型のパフォーマンスを分析
れあるさんの分析シート作成を支援
"""

import os
import csv
import re
from datetime import datetime
from pathlib import Path
from collections import defaultdict

PATTERNS = {
    '結論型': {
        'keywords': ['結論', '結論から'],
        'description': '結論を先に述べて興味を引く',
    },
    '速報型': {
        'keywords': ['速報'],
        'description': 'ニュース速報形式',
    },
    '保存型': {
        'keywords': ['保存推奨', '保存版', '保存必須'],
        'description': 'ブックマーク促進',
    },
    '配布型': {
        'keywords': ['無料配布', '無料公開', 'プレゼント', '配布'],
        'description': '無料コンテンツ提供',
    },
    'リスト型': {
        'keywords': ['①', '❶', '1.', '選'],
        'description': '番号付きリスト形式',
    },
    '対比型': {
        'keywords': ['今まで', '従来', 'vs', 'VS', '→'],
        'description': 'Before/After対比',
    },
    '質問型': {
        'keywords': ['？', 'ですか', 'ありませんか'],
        'description': '問いかけで共感を誘う',
    },
    'HowTo型': {
        'keywords': ['方法', 'やり方', 'コツ', 'ポイント', 'Tips'],
        'description': 'ハウツー・ノウハウ共有',
    },
    '驚き型': {
        'keywords': ['衝撃', 'ヤバい', 'やばい', '神', 'すごい'],
        'description': '驚きを表現',
    },
}

def load_tweets_csv(csv_path: Path) -> list[dict]:
    tweets = []
    try:
        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                tweets.append({
                    'id': row.get('投稿ID', ''),
                    'datetime': row.get('投稿日時', ''),
                    'type': row.get('投稿タイプ', ''),
                    'char_count': int(row.get('文字数', 0)),
                    'likes': int(row.get('いいね数', 0)),
                    'retweets': int(row.get('リツイート数', 0)),
                    'text': row.get('投稿本文', ''),
                })
    except Exception as e:
        print(f"Error loading CSV: {e}")
    return tweets

def classify_tweet(text: str) -> list[str]:
    """投稿を型に分類"""
    matched = []
    
    for pattern_name, config in PATTERNS.items():
        for keyword in config['keywords']:
            if keyword in text:
                matched.append(pattern_name)
                break
    
    if not matched:
        matched.append('その他')
    
    return matched

def analyze_patterns(tweets: list[dict]) -> dict:
    """型別のパフォーマンスを分析"""
    pattern_stats = defaultdict(lambda: {
        'count': 0,
        'total_likes': 0,
        'total_rts': 0,
        'tweets': [],
    })
    
    for tweet in tweets:
        patterns = classify_tweet(tweet['text'])
        
        for pattern in patterns:
            pattern_stats[pattern]['count'] += 1
            pattern_stats[pattern]['total_likes'] += tweet['likes']
            pattern_stats[pattern]['total_rts'] += tweet['retweets']
            pattern_stats[pattern]['tweets'].append(tweet)
    
    return dict(pattern_stats)

def generate_pattern_report(tweets: list[dict], output_path: Path):
    """パターン分析レポートを生成"""
    stats = analyze_patterns(tweets)
    
    report = []
    report.append("# X投稿パターン分析レポート")
    report.append(f"\n生成日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"\n分析対象: {len(tweets)}件の投稿")
    report.append("\n---\n")
    
    # パターン別サマリー
    report.append("## 📊 パターン別パフォーマンス\n")
    report.append("| パターン | 投稿数 | 平均いいね | 平均RT | 説明 |")
    report.append("|----------|--------|------------|--------|------|")
    
    # 平均いいね順でソート
    sorted_patterns = sorted(
        stats.items(),
        key=lambda x: x[1]['total_likes'] / max(x[1]['count'], 1),
        reverse=True
    )
    
    for pattern, data in sorted_patterns:
        avg_likes = data['total_likes'] / data['count'] if data['count'] > 0 else 0
        avg_rts = data['total_rts'] / data['count'] if data['count'] > 0 else 0
        desc = PATTERNS.get(pattern, {}).get('description', '-')
        report.append(f"| {pattern} | {data['count']} | {avg_likes:.1f} | {avg_rts:.1f} | {desc} |")
    
    report.append("")
    
    # 各パターンのトップ投稿
    report.append("## 🏆 各パターンのベスト投稿\n")
    
    for pattern, data in sorted_patterns[:5]:
        report.append(f"### {pattern}")
        report.append("")
        
        # いいね数順でソート
        top_tweets = sorted(data['tweets'], key=lambda x: x['likes'], reverse=True)[:3]
        
        for i, t in enumerate(top_tweets, 1):
            preview = t['text'][:100].replace('\n', ' ')
            report.append(f"{i}. **{t['likes']}いいね** / {t['retweets']}RT")
            report.append(f"   > {preview}...")
            report.append("")
        
        report.append("")
    
    # 推奨パターン
    report.append("## 💡 推奨パターン（トップ3）\n")
    
    for i, (pattern, data) in enumerate(sorted_patterns[:3], 1):
        avg_likes = data['total_likes'] / data['count'] if data['count'] > 0 else 0
        desc = PATTERNS.get(pattern, {}).get('description', '-')
        report.append(f"{i}. **{pattern}** (平均{avg_likes:.1f}いいね)")
        report.append(f"   - {desc}")
        report.append("")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report))
    
    print(f"レポート生成完了: {output_path}")

def main():
    workspace = Path(__file__).parent.parent
    csv_path = Path('/Users/ai-driven-work/Library/Mobile Documents/com~apple~CloudDocs/tweets_cleaned（過去のもの）.csv')
    
    if not csv_path.exists():
        print(f"CSVファイルが見つかりません: {csv_path}")
        return
    
    tweets = load_tweets_csv(csv_path)
    
    if not tweets:
        print("投稿データを読み込めませんでした")
        return
    
    output_path = workspace / 'projects' / 'x-pattern-analysis.md'
    generate_pattern_report(tweets, output_path)
    
    print(f"\n📊 パターン分析完了！")
    print(f"   投稿数: {len(tweets)}件")
    print(f"   出力先: {output_path}")

if __name__ == '__main__':
    main()
