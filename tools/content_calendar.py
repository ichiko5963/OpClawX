#!/usr/bin/env python3
"""
content_calendar.py - コンテンツカレンダー管理ツール
投稿スケジュール・テーマ分散・ネタ被り防止を一元管理

使い方:
  python3 content_calendar.py --account aircle --days 7
  python3 content_calendar.py --account ichiaimarketer --add "テーマ: AI x マーケ"
  python3 content_calendar.py --check-overlap
  python3 content_calendar.py --weekly-report
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path
from collections import Counter, defaultdict

WORKSPACE = Path(os.getenv("WORKSPACE", "/Users/ai-driven-work/Documents/OpenClaw-Workspace"))
PROJECTS_DIR = WORKSPACE / "projects"
CALENDAR_FILE = WORKSPACE / "memory" / "content-calendar.json"

# テーマカテゴリ定義
AIRCLE_THEMES = {
    "速報": ["速報", "リリース", "公開", "発表", "ローンチ"],
    "海外バズ": ["海外で大バズ", "海外で話題", "海外", "バズ"],
    "ツール比較": ["vs", "比較", "対決", "どっち"],
    "開発Tips": ["使い方", "活用", "Tips", "テクニック", "やり方"],
    "業界分析": ["意味する", "変わる", "時代", "未来", "トレンド"],
    "結論型": ["結論から", "正直", "経験から"],
    "配布型": ["欲しい人", "配布", "テンプレ", "まとめ"],
}

ICHIAIMARKETER_THEMES = {
    "AIグロース分析": ["グロース", "成長", "ユーザー獲得", "ARR", "売上"],
    "AI×マーケ": ["マーケティング", "マーケ", "広告", "コンバージョン"],
    "GTM戦略": ["GTM", "Go-To-Market", "ローンチ", "PLG", "プロダクト"],
    "X運用": ["X運用", "アルゴリズム", "エンゲージメント", "フォロワー", "SNS"],
    "個人開発": ["個人開発", "indie", "ソロ", "サイドプロジェクト"],
}


def load_calendar():
    """カレンダーデータをロード"""
    if CALENDAR_FILE.exists():
        with open(CALENDAR_FILE) as f:
            return json.load(f)
    return {"entries": [], "themes_used": {}, "last_updated": None}


def save_calendar(data):
    """カレンダーデータを保存"""
    data["last_updated"] = datetime.now().isoformat()
    CALENDAR_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CALENDAR_FILE, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def extract_posts_from_file(filepath):
    """投稿ファイルからテーマ・内容を抽出"""
    posts = []
    with open(filepath) as f:
        content = f.read()

    # ## 投稿N: で分割
    sections = re.split(r"## 投稿\d+[：:]?\s*", content)
    for i, section in enumerate(sections[1:], 1):
        title = section.strip().split("\n")[0]
        posts.append({
            "index": i,
            "title": title,
            "content": section.strip()[:500],
            "length": len(section.strip()),
        })
    return posts


def classify_theme(post_content, account):
    """投稿のテーマを自動分類"""
    themes = AIRCLE_THEMES if account == "aircle" else ICHIAIMARKETER_THEMES
    matched = []
    for theme, keywords in themes.items():
        for kw in keywords:
            if kw in post_content:
                matched.append(theme)
                break
    return matched if matched else ["未分類"]


def analyze_theme_distribution(account, days=7):
    """テーマの分散度を分析"""
    theme_counts = Counter()
    daily_themes = defaultdict(list)

    today = datetime.now()
    for i in range(days):
        date = today - timedelta(days=i)
        date_str = date.strftime("%Y-%m-%d")
        filepath = PROJECTS_DIR / f"x-posts-{date_str}-{account}.md"
        if filepath.exists():
            posts = extract_posts_from_file(filepath)
            for post in posts:
                themes = classify_theme(post["content"], account)
                for t in themes:
                    theme_counts[t] += 1
                    daily_themes[date_str].append(t)

    return theme_counts, daily_themes


def check_overlap(days=3):
    """直近のネタ被りチェック"""
    overlaps = []
    all_titles = defaultdict(list)

    today = datetime.now()
    for account in ["aircle", "ichiaimarketer"]:
        for i in range(days):
            date = today - timedelta(days=i)
            date_str = date.strftime("%Y-%m-%d")
            filepath = PROJECTS_DIR / f"x-posts-{date_str}-{account}.md"
            if filepath.exists():
                posts = extract_posts_from_file(filepath)
                for post in posts:
                    # タイトルのキーワードを抽出
                    keywords = set(re.findall(r"[A-Za-z]{3,}|[ぁ-んァ-ヶ一-龥]{2,}", post["title"]))
                    for existing_key, existing_entries in all_titles.items():
                        common = keywords & set(existing_key.split("|"))
                        if len(common) >= 2:
                            overlaps.append({
                                "post1": f"{account}/{date_str}/#{post['index']}",
                                "post2": existing_entries[0],
                                "common_keywords": list(common),
                            })
                    all_titles["|".join(keywords)].append(f"{account}/{date_str}/#{post['index']}")

    return overlaps


def weekly_report():
    """週間レポート生成"""
    report = []
    report.append("# 📅 週間コンテンツカレンダーレポート")
    report.append(f"生成日: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    report.append("")

    for account in ["aircle", "ichiaimarketer"]:
        account_label = "AirCle (@aircle_ai)" if account == "aircle" else "いち@AIxマーケ (@ichiaimarketer)"
        report.append(f"## {account_label}")

        theme_counts, daily_themes = analyze_theme_distribution(account, 7)

        if theme_counts:
            report.append("### テーマ分布（過去7日間）")
            total = sum(theme_counts.values())
            for theme, count in theme_counts.most_common():
                pct = count / total * 100
                bar = "█" * int(pct / 5)
                report.append(f"  {theme}: {count}件 ({pct:.0f}%) {bar}")

            # 偏りチェック
            max_pct = max(c / total * 100 for c in theme_counts.values())
            if max_pct > 40:
                report.append(f"  ⚠️ テーマ偏り警告: 1テーマが{max_pct:.0f}%を占めています")

            report.append("")
            report.append("### 日別投稿数")
            for date_str in sorted(daily_themes.keys(), reverse=True):
                themes = daily_themes[date_str]
                report.append(f"  {date_str}: {len(themes)}投稿")
        else:
            report.append("  データなし")

        report.append("")

    # ネタ被りチェック
    overlaps = check_overlap(7)
    if overlaps:
        report.append("## ⚠️ ネタ被り検出")
        for o in overlaps[:10]:
            report.append(f"  - {o['post1']} ↔ {o['post2']} (共通: {', '.join(o['common_keywords'][:3])})")
    else:
        report.append("## ✅ ネタ被りなし")

    return "\n".join(report)


def suggest_themes(account):
    """テーマ提案（不足テーマを推奨）"""
    theme_counts, _ = analyze_theme_distribution(account, 7)
    themes = AIRCLE_THEMES if account == "aircle" else ICHIAIMARKETER_THEMES

    suggestions = []
    for theme in themes:
        count = theme_counts.get(theme, 0)
        if count < 3:
            suggestions.append(f"📌 {theme}: {count}件（もっと増やすべき）")

    return suggestions


def main():
    parser = argparse.ArgumentParser(description="コンテンツカレンダー管理")
    parser.add_argument("--account", choices=["aircle", "ichiaimarketer"], help="アカウント")
    parser.add_argument("--days", type=int, default=7, help="分析日数")
    parser.add_argument("--check-overlap", action="store_true", help="ネタ被りチェック")
    parser.add_argument("--weekly-report", action="store_true", help="週間レポート")
    parser.add_argument("--suggest", action="store_true", help="テーマ提案")
    parser.add_argument("--analyze", action="store_true", help="テーマ分布分析")

    args = parser.parse_args()

    if args.weekly_report:
        print(weekly_report())
    elif args.check_overlap:
        overlaps = check_overlap(args.days)
        if overlaps:
            print(f"⚠️ {len(overlaps)}件のネタ被りを検出:")
            for o in overlaps:
                print(f"  {o['post1']} ↔ {o['post2']}")
                print(f"    共通: {', '.join(o['common_keywords'])}")
        else:
            print("✅ ネタ被りなし")
    elif args.suggest and args.account:
        suggestions = suggest_themes(args.account)
        if suggestions:
            print(f"📋 {args.account}のテーマ提案:")
            for s in suggestions:
                print(f"  {s}")
        else:
            print("✅ バランス良好")
    elif args.analyze and args.account:
        theme_counts, daily_themes = analyze_theme_distribution(args.account, args.days)
        print(f"📊 {args.account}のテーマ分布（過去{args.days}日）:")
        total = sum(theme_counts.values()) or 1
        for theme, count in theme_counts.most_common():
            pct = count / total * 100
            print(f"  {theme}: {count}件 ({pct:.0f}%)")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
