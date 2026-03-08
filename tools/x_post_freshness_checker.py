#!/usr/bin/env python3
"""
X Post Freshness Checker
投稿で参照しているニュースやデータの鮮度をチェックする。
古いネタ（7日以上前）の投稿にはフラグを付ける。
"""

import re
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

# 鮮度判定の閾値
FRESH_DAYS = 3      # 3日以内 = フレッシュ
MODERATE_DAYS = 7    # 7日以内 = まあまあ
STALE_DAYS = 14      # 14日以上 = 古い

# 日付パターン
DATE_PATTERNS = [
    r'(\d{4})年(\d{1,2})月(\d{1,2})日',
    r'(\d{4})/(\d{1,2})/(\d{1,2})',
    r'(\d{4})-(\d{1,2})-(\d{1,2})',
    r'(\d{1,2})/(\d{1,2})',  # 月/日
]

# 鮮度に関連するキーワード
FRESHNESS_KEYWORDS = {
    'fresh': ['速報', '最新', '本日', '今日', 'just', 'breaking', 'now', 'today'],
    'recent': ['今週', '先日', '昨日', 'yesterday', 'this week', 'recently'],
    'dated': ['先月', '昨年', '去年', 'last month', 'last year'],
}

# AIツール・企業のバージョン追跡
TOOL_VERSIONS = {
    'GPT': {'latest': '5.4', 'date': '2026-03-05'},
    'Claude': {'latest': '4.6', 'date': '2026-02'},
    'Cursor': {'latest': 'Automations', 'date': '2026-03-04'},
    'Codex': {'latest': '0.111.0', 'date': '2026-03'},
    'Gemini': {'latest': '3.1 Pro', 'date': '2026-02'},
}


def check_post_freshness(post_text, check_date=None):
    """個別の投稿の鮮度をチェック"""
    if check_date is None:
        check_date = datetime.now()
    
    result = {
        'freshness_score': 100,  # 100 = 最新, 0 = 古い
        'issues': [],
        'suggestions': [],
        'keywords_found': {'fresh': [], 'recent': [], 'dated': []},
    }
    
    # キーワードチェック
    for category, keywords in FRESHNESS_KEYWORDS.items():
        for kw in keywords:
            if kw in post_text:
                result['keywords_found'][category].append(kw)
    
    # 古いキーワードが見つかったら減点
    if result['keywords_found']['dated']:
        result['freshness_score'] -= 30
        result['issues'].append(f"古い時間表現: {', '.join(result['keywords_found']['dated'])}")
    
    # バージョンチェック
    for tool, info in TOOL_VERSIONS.items():
        if tool.lower() in post_text.lower():
            latest = info['latest']
            # 投稿内にバージョン番号がある場合、最新かチェック
            if latest.lower() not in post_text.lower():
                result['suggestions'].append(
                    f"{tool}の最新バージョンは{latest}({info['date']})")
    
    # 「速報」と書いてあるのに古い内容の場合
    if '速報' in post_text and result['freshness_score'] < 70:
        result['issues'].append("「速報」と書いてあるが内容が古い可能性")
        result['freshness_score'] -= 20
    
    return result


def analyze_file(filepath, check_date=None):
    """投稿ファイル全体を分析"""
    path = Path(filepath)
    if not path.exists():
        print(f"❌ ファイルが見つかりません: {filepath}")
        return None
    
    content = path.read_text(encoding='utf-8')
    
    # ファイル名から日付を取得
    date_match = re.search(r'(\d{4}-\d{2}-\d{2})', path.stem)
    file_date = None
    if date_match:
        file_date = datetime.strptime(date_match.group(1), '%Y-%m-%d')
    
    if check_date is None:
        check_date = datetime.now()
    
    # ファイル自体の古さチェック
    if file_date:
        days_old = (check_date - file_date).days
        if days_old > STALE_DAYS:
            print(f"⚠️  ファイル自体が{days_old}日前のものです")
    
    # 投稿を分割
    posts = re.split(r'^## 投稿\d+', content, flags=re.MULTILINE)
    posts = [p.strip() for p in posts if p.strip()]
    
    results = []
    total_score = 0
    
    for i, post in enumerate(posts):
        result = check_post_freshness(post, check_date)
        result['post_number'] = i + 1
        result['preview'] = post[:80].replace('\n', ' ')
        results.append(result)
        total_score += result['freshness_score']
    
    avg_score = total_score / len(results) if results else 0
    
    return {
        'file': str(filepath),
        'file_date': file_date.isoformat() if file_date else None,
        'total_posts': len(results),
        'average_freshness': round(avg_score, 1),
        'posts': results,
    }


def print_report(analysis):
    """レポートを表示"""
    if not analysis:
        return
    
    print(f"\n📰 鮮度チェックレポート: {analysis['file']}")
    print(f"📅 ファイル日付: {analysis['file_date']}")
    print(f"📊 投稿数: {analysis['total_posts']}")
    print(f"🌡️  平均鮮度スコア: {analysis['average_freshness']}/100")
    print("=" * 60)
    
    for post in analysis['posts']:
        score = post['freshness_score']
        if score >= 80:
            emoji = "🟢"
        elif score >= 60:
            emoji = "🟡"
        else:
            emoji = "🔴"
        
        print(f"\n{emoji} 投稿{post['post_number']} (スコア: {score})")
        print(f"   {post['preview']}...")
        
        if post['issues']:
            for issue in post['issues']:
                print(f"   ⚠️  {issue}")
        
        if post['suggestions']:
            for sug in post['suggestions']:
                print(f"   💡 {sug}")
    
    print("\n" + "=" * 60)
    
    # サマリー
    stale_count = sum(1 for p in analysis['posts'] if p['freshness_score'] < 60)
    if stale_count > 0:
        print(f"🔴 {stale_count}個の投稿が鮮度低下の可能性あり")
    else:
        print("✅ 全投稿の鮮度OK")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python x_post_freshness_checker.py <file.md> [check_date: YYYY-MM-DD]")
        print("\nExample:")
        print("  python x_post_freshness_checker.py projects/x-posts-2026-03-09-aircle.md")
        print("  python x_post_freshness_checker.py projects/x-posts-2026-03-09-aircle.md 2026-03-10")
        sys.exit(1)
    
    filepath = sys.argv[1]
    check_date = None
    if len(sys.argv) >= 3:
        check_date = datetime.strptime(sys.argv[2], '%Y-%m-%d')
    
    analysis = analyze_file(filepath, check_date)
    if analysis:
        print_report(analysis)
        
        # JSON出力
        json_path = filepath.replace('.md', '.freshness.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, ensure_ascii=False, indent=2)
        print(f"\n📁 JSON保存: {json_path}")
