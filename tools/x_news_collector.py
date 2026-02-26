#!/usr/bin/env python3
"""
X投稿ネタ自動収集ツール
最新AIニュースを収集し、投稿ネタとしてフォーマットする

Usage:
    python3 x_news_collector.py [--account aircle|ichiaimarketer] [--count 20]
"""

import json
import sys
import os
import re
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

WORKSPACE = "/Users/ai-driven-work/Documents/OpenClaw-Workspace"

# AirCle向けキーワード（技術者・エンジニア向け）
AIRCLE_KEYWORDS = [
    "Claude Code", "Cursor AI", "GitHub Copilot", "VS Code AI",
    "Vibe Coding", "AI Coding", "OpenClaw", "Antigravity",
    "Vercel AI", "Codex", "Devin AI", "Windsurf",
    "AI agent coding", "AI developer tools",
    "open source AI", "LLM coding",
]

# いちさん向けキーワード（マーケター・ビジネス向け）
ICHIAIMARKETER_KEYWORDS = {
    "growth": [
        "AI tool growth", "PLG strategy AI", "AI SaaS growth",
        "Notion AI growth", "Canva AI", "ChatGPT growth",
        "AI startup revenue", "AI tool ARR",
    ],
    "marketing": [
        "AI marketing", "AI content marketing", "AI SEO",
        "AI advertising", "AI copywriting", "AI personalization",
    ],
    "gtm": [
        "go to market strategy AI", "product led growth 2026",
        "AI startup launch", "AI product market fit",
    ],
    "x_ops": [
        "X algorithm 2026", "Twitter growth strategy",
        "social media AI", "engagement rate optimization",
    ],
}

# バズる型テンプレート
HOOK_TEMPLATES = [
    "【速報】{topic}",
    "【海外で大バズ】{topic}",
    "【結論から言います】{topic}",
    "【公式が答えを出してしまった】{topic}",
    "正直、{topic}",
]

# 過去使用したネタを記録するJSON
USED_TOPICS_FILE = os.path.join(WORKSPACE, "tools/.x_used_topics.json")


def load_used_topics() -> set:
    """過去使用したネタを読み込む"""
    try:
        with open(USED_TOPICS_FILE, "r") as f:
            data = json.load(f)
            # 30日以上前のものは削除
            cutoff = (datetime.now() - timedelta(days=30)).isoformat()
            return {t["topic"] for t in data if t.get("date", "") > cutoff}
    except (FileNotFoundError, json.JSONDecodeError):
        return set()


def save_used_topic(topic: str):
    """使用したネタを記録"""
    try:
        with open(USED_TOPICS_FILE, "r") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = []
    
    data.append({
        "topic": topic,
        "date": datetime.now().isoformat(),
    })
    
    # 30日以上前のものを削除
    cutoff = (datetime.now() - timedelta(days=30)).isoformat()
    data = [t for t in data if t.get("date", "") > cutoff]
    
    with open(USED_TOPICS_FILE, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def analyze_past_posts(account: str) -> dict:
    """過去の投稿を分析して使用済みネタを把握"""
    projects_dir = os.path.join(WORKSPACE, "projects")
    used_topics = set()
    hook_counts = defaultdict(int)
    
    for f in os.listdir(projects_dir):
        if f.endswith(".md") and account in f.lower() and f.startswith("x-posts-"):
            filepath = os.path.join(projects_dir, f)
            content = Path(filepath).read_text(encoding="utf-8")
            
            # フックパターン集計
            for hook in ["速報", "海外で大バズ", "結論から言います", "公式が", "正直"]:
                count = content.count(hook)
                hook_counts[hook] += count
            
            # トピック抽出（## 投稿N: の後のテキスト）
            topics = re.findall(r"## 投稿\d+[:：]\s*(.+)", content)
            used_topics.update(topics)
    
    return {
        "used_topics": used_topics,
        "hook_counts": dict(hook_counts),
        "total_files": len([f for f in os.listdir(projects_dir) 
                          if f.endswith(".md") and account in f.lower()]),
    }


def score_news_item(item: dict, account: str, used_topics: set) -> float:
    """ニュースアイテムのスコアを計算"""
    score = 50.0  # ベーススコア
    
    title = item.get("title", "").lower()
    snippet = item.get("snippet", "").lower()
    text = f"{title} {snippet}"
    
    # キーワードマッチ
    if account == "aircle":
        for kw in AIRCLE_KEYWORDS:
            if kw.lower() in text:
                score += 15
    else:
        for category, keywords in ICHIAIMARKETER_KEYWORDS.items():
            for kw in keywords:
                if kw.lower() in text:
                    score += 12
                    break
    
    # 数字があるとバズりやすい
    if re.search(r"\$[\d.]+[BMK]|\d+%|\d+億|\d+万", text):
        score += 20
    
    # 速報性（最新であるほど高スコア）
    if "2026" in text or "today" in text or "just" in text:
        score += 10
    
    # 既出チェック
    for used in used_topics:
        if any(word in title for word in used.split()[:3] if len(word) > 3):
            score -= 30
            break
    
    # ネガティブ要素
    if any(word in text for word in ["lawsuit", "layoff", "controversy"]):
        score += 5  # 議論を呼ぶネタはエンゲージメント高い
    
    return min(100, max(0, score))


def format_as_post_seed(items: list[dict], account: str) -> list[dict]:
    """ニュースアイテムを投稿ネタとしてフォーマット"""
    seeds = []
    
    for i, item in enumerate(items, 1):
        # 適切なフック型を選択
        hook_idx = i % len(HOOK_TEMPLATES)
        hook = HOOK_TEMPLATES[hook_idx]
        
        seeds.append({
            "num": i,
            "title": item.get("title", ""),
            "url": item.get("url", ""),
            "snippet": item.get("snippet", ""),
            "score": item.get("score", 50),
            "suggested_hook": hook.format(topic=item.get("title", "")[:30]),
            "category": item.get("category", "general"),
        })
    
    return seeds


def generate_seed_markdown(seeds: list[dict], account: str, date: str) -> str:
    """投稿ネタをMarkdownファイルとして生成"""
    account_label = "@aircle_ai" if account == "aircle" else "@ichiaimarketer"
    
    lines = [
        f"# X投稿ネタ {date} ({account_label})",
        "",
        f"収集日時: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"ネタ数: {len(seeds)}件",
        "",
        "---",
        "",
    ]
    
    for seed in seeds:
        lines.extend([
            f"## ネタ{seed['num']}: {seed['title']}",
            f"**スコア**: {seed['score']:.0f}/100",
            f"**カテゴリ**: {seed['category']}",
            f"**推奨フック**: {seed['suggested_hook']}",
            f"**参考URL**: {seed['url']}",
            "",
            f"> {seed['snippet']}",
            "",
            "---",
            "",
        ])
    
    return "\n".join(lines)


def generate_report(aircle_analysis: dict, ichi_analysis: dict) -> str:
    """分析レポートを生成"""
    report = [
        "# X投稿ネタ収集レポート",
        f"生成日時: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "## AirCle (@aircle_ai)",
        f"- 過去投稿ファイル数: {aircle_analysis['total_files']}",
        f"- 使用済みトピック数: {len(aircle_analysis['used_topics'])}",
        "- フック使用頻度:",
    ]
    
    for hook, count in sorted(aircle_analysis["hook_counts"].items(), 
                               key=lambda x: x[1], reverse=True):
        report.append(f"  - {hook}: {count}回")
    
    report.extend([
        "",
        "## いち@AIxマーケ (@ichiaimarketer)",
        f"- 過去投稿ファイル数: {ichi_analysis['total_files']}",
        f"- 使用済みトピック数: {len(ichi_analysis['used_topics'])}",
        "- フック使用頻度:",
    ])
    
    for hook, count in sorted(ichi_analysis["hook_counts"].items(),
                               key=lambda x: x[1], reverse=True):
        report.append(f"  - {hook}: {count}回")
    
    return "\n".join(report)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="X投稿ネタ自動収集ツール")
    parser.add_argument("--account", choices=["aircle", "ichiaimarketer", "both"], 
                       default="both", help="対象アカウント")
    parser.add_argument("--count", type=int, default=25, help="収集するネタ数")
    parser.add_argument("--analyze-only", action="store_true", help="分析のみ（収集しない）")
    args = parser.parse_args()
    
    date_str = datetime.now().strftime("%Y-%m-%d")
    
    # 過去投稿分析
    print("📊 過去投稿を分析中...")
    aircle_analysis = analyze_past_posts("aircle")
    ichi_analysis = analyze_past_posts("ichiaimarketer")
    
    report = generate_report(aircle_analysis, ichi_analysis)
    print(report)
    
    if args.analyze_only:
        return
    
    print("\n" + "=" * 60)
    print("💡 ネタ収集は外部検索が必要なため、OpenClawエージェントから実行してください")
    print("   このツールは分析・フォーマット・スコアリングを担当します")
    print("=" * 60)
    
    # 使用済みトピック保存
    all_used = aircle_analysis["used_topics"] | ichi_analysis["used_topics"]
    print(f"\n📝 使用済みトピック: {len(all_used)}件")
    
    # 推奨キーワード出力
    if args.account in ("aircle", "both"):
        print("\n🔍 AirCle推奨検索キーワード:")
        for kw in AIRCLE_KEYWORDS[:5]:
            print(f"   - {kw} 2026")
    
    if args.account in ("ichiaimarketer", "both"):
        print("\n🔍 いち@AIxマーケ推奨検索キーワード:")
        for cat, kws in ICHIAIMARKETER_KEYWORDS.items():
            print(f"   [{cat}]")
            for kw in kws[:2]:
                print(f"   - {kw} 2026")


if __name__ == "__main__":
    main()
