#!/usr/bin/env python3
"""
X投稿分析レポート生成ツール
CSVファイルから詳細な分析レポートをMarkdownで出力
（れあるさんの分析作業用）
"""

import os
import csv
import re
from datetime import datetime
from pathlib import Path
from collections import Counter, defaultdict

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

def categorize_tweet(text: str) -> list[str]:
    """投稿をカテゴリ分類"""
    categories = []
    
    text_lower = text.lower()
    
    # 技術系
    if any(kw in text_lower for kw in ['claude', 'gpt', 'ai', 'chatgpt', 'gemini']):
        categories.append('AI技術')
    if any(kw in text_lower for kw in ['cursor', 'vscode', 'code', 'github']):
        categories.append('開発ツール')
    if any(kw in text_lower for kw in ['vibe coding', 'バイブコーディング']):
        categories.append('Vibe Coding')
    
    # 形式
    if '【速報】' in text or '【速報 】' in text:
        categories.append('速報型')
    if any(kw in text for kw in ['無料配布', '無料公開', 'プレゼント']):
        categories.append('配布型')
    if '結論' in text:
        categories.append('結論型')
    if '①' in text or '1.' in text:
        categories.append('リスト型')
    
    if not categories:
        categories.append('その他')
    
    return categories

def extract_hook(text: str) -> str:
    """フック（冒頭）を抽出"""
    match = re.match(r'^【(.+?)】', text)
    if match:
        return f"【{match.group(1)}】"
    
    # 最初の行を取得
    first_line = text.split('\n')[0][:30]
    return first_line

def analyze_time_patterns(tweets: list[dict]) -> dict:
    """投稿時間のパターンを分析"""
    hour_engagement = defaultdict(lambda: {'count': 0, 'likes': 0, 'rts': 0})
    weekday_engagement = defaultdict(lambda: {'count': 0, 'likes': 0, 'rts': 0})
    
    for tweet in tweets:
        try:
            dt = datetime.strptime(tweet['datetime'], '%Y-%m-%d %H:%M:%S')
            hour = dt.hour
            weekday = dt.strftime('%A')
            
            hour_engagement[hour]['count'] += 1
            hour_engagement[hour]['likes'] += tweet['likes']
            hour_engagement[hour]['rts'] += tweet['retweets']
            
            weekday_engagement[weekday]['count'] += 1
            weekday_engagement[weekday]['likes'] += tweet['likes']
            weekday_engagement[weekday]['rts'] += tweet['retweets']
        except Exception:
            pass
    
    # 時間帯別の平均エンゲージメント
    best_hours = []
    for hour, data in sorted(hour_engagement.items()):
        if data['count'] > 0:
            avg_likes = data['likes'] / data['count']
            best_hours.append((hour, avg_likes, data['count']))
    
    best_hours.sort(key=lambda x: x[1], reverse=True)
    
    return {
        'by_hour': dict(hour_engagement),
        'by_weekday': dict(weekday_engagement),
        'best_hours': best_hours[:5],
    }

def generate_markdown_report(tweets: list[dict], output_path: Path):
    """Markdownレポートを生成"""
    
    report = []
    report.append("# AirCle X投稿分析レポート")
    report.append(f"\n生成日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"\n分析対象: {len(tweets)}件の投稿")
    report.append("\n---\n")
    
    # 基本統計
    total_likes = sum(t['likes'] for t in tweets)
    total_rts = sum(t['retweets'] for t in tweets)
    avg_likes = total_likes / len(tweets) if tweets else 0
    avg_rts = total_rts / len(tweets) if tweets else 0
    
    report.append("## 📊 基本統計\n")
    report.append("| 指標 | 値 |")
    report.append("|------|-----|")
    report.append(f"| 総投稿数 | {len(tweets)}件 |")
    report.append(f"| 総いいね | {total_likes:,}件 |")
    report.append(f"| 総RT | {total_rts:,}件 |")
    report.append(f"| 平均いいね | {avg_likes:.1f} |")
    report.append(f"| 平均RT | {avg_rts:.1f} |")
    report.append("")
    
    # カテゴリ別分析
    category_stats = defaultdict(lambda: {'count': 0, 'likes': 0, 'rts': 0})
    for tweet in tweets:
        cats = categorize_tweet(tweet['text'])
        for cat in cats:
            category_stats[cat]['count'] += 1
            category_stats[cat]['likes'] += tweet['likes']
            category_stats[cat]['rts'] += tweet['retweets']
    
    report.append("## 📂 カテゴリ別パフォーマンス\n")
    report.append("| カテゴリ | 投稿数 | 平均いいね | 平均RT |")
    report.append("|----------|--------|------------|--------|")
    
    for cat, data in sorted(category_stats.items(), key=lambda x: x[1]['likes']/max(x[1]['count'],1), reverse=True):
        avg_l = data['likes'] / data['count'] if data['count'] > 0 else 0
        avg_r = data['rts'] / data['count'] if data['count'] > 0 else 0
        report.append(f"| {cat} | {data['count']} | {avg_l:.1f} | {avg_r:.1f} |")
    report.append("")
    
    # トップ投稿
    top_tweets = sorted(tweets, key=lambda x: x['likes'], reverse=True)[:10]
    
    report.append("## 🏆 トップ10投稿\n")
    report.append("| 順位 | いいね | RT | フック | カテゴリ |")
    report.append("|------|--------|----|----|---------|")
    
    for i, t in enumerate(top_tweets, 1):
        hook = extract_hook(t['text']).replace('|', '/').replace('\n', ' ')
        cats = ', '.join(categorize_tweet(t['text']))
        report.append(f"| {i} | {t['likes']} | {t['retweets']} | {hook[:30]} | {cats} |")
    report.append("")
    
    # 時間帯分析
    time_analysis = analyze_time_patterns(tweets)
    
    report.append("## ⏰ ベスト投稿時間\n")
    report.append("| 時間帯 | 平均いいね | 投稿数 |")
    report.append("|--------|------------|--------|")
    
    for hour, avg_likes, count in time_analysis['best_hours']:
        report.append(f"| {hour}:00 | {avg_likes:.1f} | {count} |")
    report.append("")
    
    # フック分析
    hooks = Counter()
    for tweet in tweets:
        match = re.match(r'^【(.+?)】', tweet['text'])
        if match:
            hooks[f"【{match.group(1)}】"] += 1
    
    report.append("## 🎣 よく使われるフック\n")
    report.append("| フック | 使用回数 |")
    report.append("|--------|----------|")
    
    for hook, count in hooks.most_common(15):
        report.append(f"| {hook} | {count} |")
    report.append("")
    
    # 推奨事項
    report.append("## 💡 推奨事項\n")
    report.append("1. **高パフォーマンスカテゴリ**: ")
    top_cats = sorted(category_stats.items(), key=lambda x: x[1]['likes']/max(x[1]['count'],1), reverse=True)[:3]
    report.append(f"   {', '.join(c[0] for c in top_cats)}")
    report.append("")
    
    report.append("2. **最適投稿時間**: ")
    report.append(f"   {', '.join(f'{h[0]}:00' for h in time_analysis['best_hours'][:3])}")
    report.append("")
    
    report.append("3. **効果的なフック**: ")
    report.append(f"   {', '.join(h[0] for h in hooks.most_common(5))}")
    report.append("")
    
    # 出力
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
    
    # レポート出力
    output_path = workspace / 'projects' / 'x-analysis-report.md'
    generate_markdown_report(tweets, output_path)
    
    print(f"\n📊 分析完了！")
    print(f"   投稿数: {len(tweets)}件")
    print(f"   出力先: {output_path}")

if __name__ == '__main__':
    main()
