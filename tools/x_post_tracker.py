#!/usr/bin/env python3
"""
X投稿トラッカー
全投稿ファイルを横断的に管理し、日別・アカウント別のサマリーを生成

Usage:
    python3 x_post_tracker.py                    # 全体サマリー
    python3 x_post_tracker.py --date 2026-02-25  # 日別詳細
    python3 x_post_tracker.py --stats             # 統計情報
    python3 x_post_tracker.py --unused-hooks      # 使用頻度の低いフック型を提案
"""

import os
import re
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict, Counter

WORKSPACE = "/Users/ai-driven-work/Documents/OpenClaw-Workspace"
PROJECTS_DIR = os.path.join(WORKSPACE, "projects")


def parse_post_file(filepath: str) -> list[dict]:
    """投稿ファイルをパースして構造化データにする"""
    content = Path(filepath).read_text(encoding="utf-8")
    posts = []
    
    # ファイル名から日付とアカウントを抽出
    basename = os.path.basename(filepath)
    date_match = re.search(r"(\d{4}-\d{2}-\d{2})", basename)
    date = date_match.group(1) if date_match else "unknown"
    
    if "aircle" in basename.lower():
        account = "aircle"
    elif "ichiaimarketer" in basename.lower():
        account = "ichiaimarketer"
    else:
        account = "unknown"
    
    # 投稿抽出
    pattern = r"## 投稿(\d+)[:：]\s*(.+?)(?=\n## 投稿|\n## ■|\Z)"
    matches = re.findall(pattern, content, re.DOTALL)
    
    for num, body in matches:
        body = body.strip()
        if body.endswith("---"):
            body = body[:-3].strip()
        
        lines = body.split("\n")
        title = lines[0].strip() if lines else ""
        
        # フック型判定
        hook = "その他"
        if "速報" in title:
            hook = "速報"
        elif "海外で大バズ" in title or "海外で話題" in title:
            hook = "海外バズ"
        elif "結論から言います" in title:
            hook = "結論型"
        elif "公式が" in title:
            hook = "公式型"
        elif title.startswith("正直"):
            hook = "正直型"
        elif "欲しい人" in title:
            hook = "配布型"
        
        # 文字数
        char_count = len(body.replace("\n", "").replace(" ", ""))
        
        # 参考URL
        ref_match = re.search(r"参考:\s*(https?://\S+)", body)
        ref_url = ref_match.group(1) if ref_match else None
        
        # 箇条書き数
        bullet_count = body.count("• ") + body.count("・")
        
        posts.append({
            "date": date,
            "account": account,
            "num": int(num),
            "title": title,
            "hook": hook,
            "char_count": char_count,
            "has_ref": ref_url is not None,
            "ref_url": ref_url,
            "bullet_count": bullet_count,
            "body": body,
            "file": basename,
        })
    
    return posts


def get_all_posts() -> list[dict]:
    """全投稿ファイルから投稿を取得"""
    all_posts = []
    
    for f in sorted(os.listdir(PROJECTS_DIR)):
        if f.startswith("x-posts-") and f.endswith(".md"):
            filepath = os.path.join(PROJECTS_DIR, f)
            posts = parse_post_file(filepath)
            all_posts.extend(posts)
    
    return all_posts


def print_summary(posts: list[dict]):
    """全体サマリーを表示"""
    print("=" * 60)
    print(f"📊 X投稿トラッカー サマリー")
    print(f"   生成日時: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)
    
    # アカウント別
    by_account = defaultdict(list)
    for p in posts:
        by_account[p["account"]].append(p)
    
    for account, acct_posts in sorted(by_account.items()):
        label = "@aircle_ai" if account == "aircle" else "@ichiaimarketer"
        avg_chars = sum(p["char_count"] for p in acct_posts) // len(acct_posts) if acct_posts else 0
        
        print(f"\n{'─' * 40}")
        print(f"🏷️  {label}")
        print(f"   投稿数: {len(acct_posts)}")
        print(f"   平均文字数: {avg_chars}")
        print(f"   参考URL付き: {sum(1 for p in acct_posts if p['has_ref'])}/{len(acct_posts)}")
        
        # 日別
        by_date = defaultdict(int)
        for p in acct_posts:
            by_date[p["date"]] += 1
        
        print(f"   日別投稿数:")
        for date, count in sorted(by_date.items(), reverse=True)[:7]:
            print(f"     {date}: {count}投稿")
    
    # フック型集計
    print(f"\n{'─' * 40}")
    print("🎣 フック型分布（全体）")
    hook_counts = Counter(p["hook"] for p in posts)
    total = len(posts)
    for hook, count in hook_counts.most_common():
        pct = count / total * 100
        bar = "█" * int(pct / 2)
        print(f"   {hook:10s}: {count:3d} ({pct:4.1f}%) {bar}")


def print_date_detail(posts: list[dict], date: str):
    """日別詳細を表示"""
    day_posts = [p for p in posts if p["date"] == date]
    if not day_posts:
        print(f"❌ {date}の投稿が見つかりません")
        return
    
    print(f"\n📅 {date} の投稿詳細")
    print("=" * 60)
    
    for account in ["aircle", "ichiaimarketer"]:
        acct_posts = [p for p in day_posts if p["account"] == account]
        if not acct_posts:
            continue
        
        label = "@aircle_ai" if account == "aircle" else "@ichiaimarketer"
        print(f"\n🏷️  {label} ({len(acct_posts)}投稿)")
        print("─" * 40)
        
        for p in acct_posts:
            status = "✅" if p["char_count"] >= 200 else "⚠️"
            print(f"  {status} #{p['num']:2d} [{p['hook']:6s}] {p['char_count']:3d}文字 | {p['title'][:50]}")


def print_stats(posts: list[dict]):
    """統計情報を表示"""
    print("\n📈 統計情報")
    print("=" * 60)
    
    # 文字数分布
    char_counts = [p["char_count"] for p in posts]
    if char_counts:
        print(f"\n文字数統計:")
        print(f"  最小: {min(char_counts)}")
        print(f"  最大: {max(char_counts)}")
        print(f"  平均: {sum(char_counts) // len(char_counts)}")
        print(f"  中央: {sorted(char_counts)[len(char_counts) // 2]}")
    
    # 200文字未満の投稿（短すぎ）
    short = [p for p in posts if p["char_count"] < 200]
    if short:
        print(f"\n⚠️ 200文字未満の投稿: {len(short)}件")
        for p in short[:5]:
            print(f"  - [{p['date']}] #{p['num']} {p['char_count']}文字 {p['title'][:40]}")
    
    # 参考URL なしの投稿
    no_ref = [p for p in posts if not p["has_ref"]]
    print(f"\n📎 参考URLなし: {len(no_ref)}/{len(posts)}件")
    
    # フック型の日別トレンド
    print("\n🎣 フック型の日別使用（直近5日）")
    dates = sorted(set(p["date"] for p in posts), reverse=True)[:5]
    for date in dates:
        day_posts = [p for p in posts if p["date"] == date]
        hooks = Counter(p["hook"] for p in day_posts)
        hook_str = ", ".join(f"{h}:{c}" for h, c in hooks.most_common(3))
        print(f"  {date}: {len(day_posts)}投稿 | {hook_str}")


def suggest_unused_hooks(posts: list[dict]):
    """使用頻度の低いフック型を提案"""
    hook_counts = Counter(p["hook"] for p in posts)
    total = len(posts)
    
    all_hooks = ["速報", "海外バズ", "結論型", "公式型", "正直型", "配布型"]
    
    print("\n💡 フック型バランス提案")
    print("=" * 60)
    
    ideal_pct = 100 / len(all_hooks)
    
    for hook in all_hooks:
        count = hook_counts.get(hook, 0)
        pct = count / total * 100 if total > 0 else 0
        diff = pct - ideal_pct
        
        if diff < -5:
            status = "⬆️ もっと使おう"
        elif diff > 10:
            status = "⬇️ 使いすぎ"
        else:
            status = "✅ バランスOK"
        
        bar = "█" * int(pct / 2)
        print(f"  {hook:10s}: {pct:5.1f}% (理想{ideal_pct:.0f}%) {status} {bar}")


def main():
    parser = argparse.ArgumentParser(description="X投稿トラッカー")
    parser.add_argument("--date", help="日別詳細表示")
    parser.add_argument("--stats", action="store_true", help="統計情報")
    parser.add_argument("--unused-hooks", action="store_true", help="フック型提案")
    parser.add_argument("--json", action="store_true", help="JSON出力")
    args = parser.parse_args()
    
    posts = get_all_posts()
    
    if not posts:
        print("❌ 投稿が見つかりません")
        sys.exit(1)
    
    if args.json:
        # bodyは除外してJSON出力
        output = [{k: v for k, v in p.items() if k != "body"} for p in posts]
        print(json.dumps(output, ensure_ascii=False, indent=2))
        return
    
    if args.date:
        print_date_detail(posts, args.date)
    elif args.stats:
        print_stats(posts)
    elif args.unused_hooks:
        suggest_unused_hooks(posts)
    else:
        print_summary(posts)


if __name__ == "__main__":
    main()
