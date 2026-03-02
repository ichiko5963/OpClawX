#!/usr/bin/env python3
"""
News Digest Generator v1.0
最新AI/テックニュースを整理してダイジェストを生成するツール。
深夜セッションやX投稿作成前のリサーチ支援。

Usage:
  python3 tools/news_digest_generator.py                    # 今日のダイジェスト表示
  python3 tools/news_digest_generator.py --save              # ファイルに保存
  python3 tools/news_digest_generator.py --format markdown   # Markdown出力
  python3 tools/news_digest_generator.py --days 3            # 過去3日分
"""

import sys
import json
import re
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from typing import Optional
from collections import Counter

WORKSPACE = Path("/Users/ai-driven-work/Documents/OpenClaw-Workspace")
MEMORY_DIR = WORKSPACE / "memory"
PROJECTS_DIR = WORKSPACE / "projects"

# ニュースカテゴリ定義
CATEGORIES = {
    "ai_coding": {
        "name": "AIコーディングツール",
        "keywords": ["cursor", "claude code", "copilot", "codex", "xcode", "vscode", "vs code",
                     "windsurf", "cline", "vibe coding", "openclaw"],
        "emoji": "💻",
    },
    "ai_agents": {
        "name": "AIエージェント",
        "keywords": ["agent", "エージェント", "cowork", "autonomous", "自律"],
        "emoji": "🤖",
    },
    "ai_business": {
        "name": "AI × ビジネス",
        "keywords": ["notion", "jasper", "copy.ai", "midjourney", "chatgpt", "enterprise",
                     "startup", "growth", "gtm", "revenue"],
        "emoji": "📊",
    },
    "ai_security": {
        "name": "AIセキュリティ",
        "keywords": ["security", "vulnerability", "hack", "exploit", "breach", "cve"],
        "emoji": "🔒",
    },
    "social_media": {
        "name": "SNS・マーケ",
        "keywords": ["twitter", "x algorithm", "grok", "engagement", "sns", "マーケ",
                     "premium", "フォロワー"],
        "emoji": "📱",
    },
    "ai_general": {
        "name": "AI全般",
        "keywords": ["anthropic", "openai", "google", "gemini", "gpt", "llm", "model"],
        "emoji": "🧠",
    },
}


@dataclass
class NewsItem:
    """ニュースアイテム"""
    title: str
    summary: str
    source: str = ""
    url: str = ""
    date: str = ""
    category: str = "ai_general"
    impact_score: int = 5  # 1-10
    used_in_posts: bool = False


@dataclass
class NewsDigest:
    """ニュースダイジェスト"""
    date: str
    items: list = field(default_factory=list)
    categories: dict = field(default_factory=dict)
    stats: dict = field(default_factory=dict)


def categorize_news(title: str, summary: str) -> str:
    """ニュースをカテゴリ分類"""
    text = (title + " " + summary).lower()
    scores = {}
    for cat_id, cat in CATEGORIES.items():
        score = sum(1 for kw in cat["keywords"] if kw.lower() in text)
        scores[cat_id] = score
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "ai_general"


def estimate_impact(title: str, summary: str) -> int:
    """ニュースのインパクトスコアを推定（1-10）"""
    text = (title + " " + summary).lower()
    score = 5  # baseline

    # 高インパクトシグナル
    high_signals = ["速報", "大バズ", "billion", "b評価", "vulnerability", "hack",
                    "outage", "障害", "ban", "acquisition", "買収", "launch", "リリース"]
    for sig in high_signals:
        if sig.lower() in text:
            score += 2

    # 数字が含まれる = 具体的 = 高インパクト
    if re.search(r'\$[\d.]+[BMK]|\d+%|\d+億|\d+万', text):
        score += 1

    # 有名企業
    big_names = ["anthropic", "openai", "google", "apple", "microsoft", "cursor", "notion"]
    for name in big_names:
        if name in text:
            score += 1

    return min(10, max(1, score))


def extract_news_from_memory(days: int = 1) -> list:
    """メモリファイルからニュースを抽出"""
    items = []
    today = datetime.now()

    for d in range(days):
        date = today - timedelta(days=d)
        date_str = date.strftime("%Y-%m-%d")
        file_path = MEMORY_DIR / f"{date_str}.md"

        if not file_path.exists():
            continue

        content = file_path.read_text(encoding="utf-8")

        # 「最新ニュース」セクションを探す
        news_section = False
        for line in content.split("\n"):
            if "最新ニュース" in line:
                news_section = True
                continue
            if news_section and line.startswith("## ") and "ニュース" not in line:
                news_section = False
                continue
            if news_section and line.startswith("- "):
                title = line.lstrip("- ").strip()
                if title:
                    cat = categorize_news(title, "")
                    impact = estimate_impact(title, "")
                    items.append(NewsItem(
                        title=title,
                        summary="",
                        date=date_str,
                        category=cat,
                        impact_score=impact,
                    ))

    return items


def check_used_in_posts(items: list, days: int = 3) -> list:
    """過去の投稿で使用済みかチェック"""
    today = datetime.now()
    post_content = ""

    for d in range(days):
        date = today - timedelta(days=d)
        date_str = date.strftime("%Y-%m-%d")
        for suffix in ["aircle", "ichiaimarketer"]:
            file_path = PROJECTS_DIR / f"x-posts-{date_str}-{suffix}.md"
            if file_path.exists():
                post_content += file_path.read_text(encoding="utf-8").lower()

    for item in items:
        # タイトルの主要キーワードが投稿に含まれるかチェック
        keywords = re.findall(r'[\w]+', item.title.lower())
        match_count = sum(1 for kw in keywords if len(kw) > 3 and kw in post_content)
        if match_count >= 3:
            item.used_in_posts = True

    return items


def generate_digest(items: list, date_str: str) -> NewsDigest:
    """ダイジェストを生成"""
    digest = NewsDigest(date=date_str)
    digest.items = sorted(items, key=lambda x: x.impact_score, reverse=True)

    # カテゴリ別集計
    for cat_id in CATEGORIES:
        cat_items = [i for i in items if i.category == cat_id]
        if cat_items:
            digest.categories[cat_id] = {
                "count": len(cat_items),
                "avg_impact": sum(i.impact_score for i in cat_items) / len(cat_items),
                "items": [i.title for i in cat_items],
            }

    # 統計
    digest.stats = {
        "total": len(items),
        "unused": len([i for i in items if not i.used_in_posts]),
        "high_impact": len([i for i in items if i.impact_score >= 7]),
        "categories": len(digest.categories),
    }

    return digest


def format_markdown(digest: NewsDigest) -> str:
    """Markdown形式で出力"""
    lines = [
        f"# ニュースダイジェスト ({digest.date})",
        "",
        f"**合計**: {digest.stats['total']}件 | "
        f"**未使用**: {digest.stats['unused']}件 | "
        f"**高インパクト**: {digest.stats['high_impact']}件",
        "",
    ]

    # カテゴリ別
    for cat_id, cat_data in sorted(digest.categories.items(),
                                    key=lambda x: x[1]["avg_impact"], reverse=True):
        cat_info = CATEGORIES[cat_id]
        lines.append(f"## {cat_info['emoji']} {cat_info['name']} ({cat_data['count']}件)")
        lines.append("")
        cat_items = [i for i in digest.items if i.category == cat_id]
        for item in cat_items:
            status = "✅" if item.used_in_posts else "🆕"
            impact_bar = "🔥" * min(5, item.impact_score // 2)
            lines.append(f"- {status} {item.title} {impact_bar}")
            if item.url:
                lines.append(f"  - {item.url}")
        lines.append("")

    # 投稿提案
    unused_high = [i for i in digest.items if not i.used_in_posts and i.impact_score >= 7]
    if unused_high:
        lines.append("## 🎯 投稿おすすめ（未使用 × 高インパクト）")
        lines.append("")
        for item in unused_high[:10]:
            lines.append(f"1. **{item.title}** (impact: {item.impact_score}/10)")
        lines.append("")

    return "\n".join(lines)


def format_json(digest: NewsDigest) -> str:
    """JSON形式で出力"""
    return json.dumps({
        "date": digest.date,
        "stats": digest.stats,
        "items": [asdict(i) for i in digest.items],
        "categories": digest.categories,
    }, ensure_ascii=False, indent=2)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="News Digest Generator")
    parser.add_argument("--save", action="store_true", help="ファイルに保存")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown")
    parser.add_argument("--days", type=int, default=1, help="対象日数")
    args = parser.parse_args()

    today = datetime.now().strftime("%Y-%m-%d")

    # ニュース収集
    items = extract_news_from_memory(days=args.days)

    if not items:
        print(f"⚠️ 過去{args.days}日間のニュースが見つかりません")
        print("memory/YYYY-MM-DD.md に「## 最新ニュース」セクションを追加してください")
        sys.exit(1)

    # 使用済みチェック
    items = check_used_in_posts(items)

    # ダイジェスト生成
    digest = generate_digest(items, today)

    # 出力
    if args.format == "json":
        output = format_json(digest)
    else:
        output = format_markdown(digest)

    if args.save:
        out_path = PROJECTS_DIR / f"news-digest-{today}.md"
        out_path.write_text(output, encoding="utf-8")
        print(f"✅ 保存: {out_path}")
    else:
        print(output)


if __name__ == "__main__":
    main()
