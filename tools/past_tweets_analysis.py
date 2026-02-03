#!/usr/bin/env python3
"""
過去投稿分析ツール
CSVファイルから過去投稿を分析し、パターンを抽出
"""

import os
import csv
import re
from datetime import datetime
from pathlib import Path
from collections import Counter

def load_tweets_csv(csv_path: Path) -> list[dict]:
    """CSVファイルから投稿を読み込む"""
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

def analyze_engagement(tweets: list[dict]) -> dict:
    """エンゲージメントを分析"""
    if not tweets:
        return {}
    
    total_likes = sum(t['likes'] for t in tweets)
    total_rts = sum(t['retweets'] for t in tweets)
    avg_likes = total_likes / len(tweets)
    avg_rts = total_rts / len(tweets)
    
    # トップ投稿
    top_by_likes = sorted(tweets, key=lambda x: x['likes'], reverse=True)[:5]
    top_by_rts = sorted(tweets, key=lambda x: x['retweets'], reverse=True)[:5]
    
    return {
        'total_tweets': len(tweets),
        'total_likes': total_likes,
        'total_rts': total_rts,
        'avg_likes': avg_likes,
        'avg_rts': avg_rts,
        'top_by_likes': top_by_likes,
        'top_by_rts': top_by_rts,
    }

def analyze_patterns(tweets: list[dict]) -> dict:
    """投稿パターンを分析"""
    patterns = Counter()
    
    for tweet in tweets:
        text = tweet['text']
        
        # フック分析
        if re.match(r'^【.+?】', text):
            patterns['【】フック'] += 1
        if '🔥' in text:
            patterns['🔥絵文字'] += 1
        if '👇' in text:
            patterns['👇CTA'] += 1
        if re.search(r'\d+%', text):
            patterns['パーセント数字'] += 1
        if re.search(r'①|②|③', text):
            patterns['番号リスト'] += 1
        if 'ノート投稿' in tweet['type']:
            patterns['ノート投稿'] += 1
        if '速報' in text:
            patterns['速報系'] += 1
        if 'Claude' in text or 'claude' in text.lower():
            patterns['Claude言及'] += 1
        if 'AI' in text:
            patterns['AI言及'] += 1
    
    return dict(patterns.most_common(15))

def extract_top_tweet_features(tweets: list[dict], min_likes: int = 50) -> list[str]:
    """バズった投稿の特徴を抽出"""
    features = []
    
    for tweet in tweets:
        if tweet['likes'] >= min_likes:
            text = tweet['text']
            
            # 冒頭のフックを抽出
            hook_match = re.match(r'^【(.+?)】', text)
            if hook_match:
                features.append(f"【{hook_match.group(1)}】")
    
    return list(set(features))[:20]

def main():
    workspace = Path(__file__).parent.parent
    
    # CSVファイルを探す
    csv_path = Path('/Users/ai-driven-work/Library/Mobile Documents/com~apple~CloudDocs/tweets_cleaned（過去のもの）.csv')
    
    if not csv_path.exists():
        print(f"CSVファイルが見つかりません: {csv_path}")
        return
    
    print("=" * 60)
    print("📊 過去投稿分析レポート")
    print(f"   データソース: {csv_path.name}")
    print("=" * 60)
    
    tweets = load_tweets_csv(csv_path)
    
    if not tweets:
        print("投稿データを読み込めませんでした")
        return
    
    # エンゲージメント分析
    engagement = analyze_engagement(tweets)
    
    print(f"\n📈 基本統計")
    print("-" * 40)
    print(f"  総投稿数: {engagement['total_tweets']}件")
    print(f"  総いいね: {engagement['total_likes']}件")
    print(f"  総RT: {engagement['total_rts']}件")
    print(f"  平均いいね: {engagement['avg_likes']:.1f}")
    print(f"  平均RT: {engagement['avg_rts']:.1f}")
    
    # トップ投稿
    print(f"\n🏆 いいね数トップ5")
    print("-" * 40)
    for i, t in enumerate(engagement['top_by_likes'], 1):
        preview = t['text'][:50].replace('\n', ' ')
        print(f"  {i}. {t['likes']}いいね | {preview}...")
    
    # パターン分析
    patterns = analyze_patterns(tweets)
    
    print(f"\n📋 投稿パターン（頻度順）")
    print("-" * 40)
    for pattern, count in patterns.items():
        pct = count / len(tweets) * 100
        print(f"  {pattern}: {count}件 ({pct:.1f}%)")
    
    # バズった投稿のフック
    features = extract_top_tweet_features(tweets)
    
    if features:
        print(f"\n🔥 バズった投稿のフック例")
        print("-" * 40)
        for f in features[:10]:
            print(f"  {f}")
    
    print("\n" + "=" * 60)
    print("💡 分析結果を活用して次の投稿を作成しましょう！")
    print("=" * 60)

if __name__ == '__main__':
    main()
