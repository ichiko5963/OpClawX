#!/usr/bin/env python3
"""
engagement_optimizer.py - エンゲージメント最適化ツール
投稿の構造・CTA・フック・長さを分析してスコアリング

使い方:
  python3 engagement_optimizer.py --file projects/x-posts-2026-03-05-aircle.md
  python3 engagement_optimizer.py --text "投稿テキストをここに"
  python3 engagement_optimizer.py --batch --days 7
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path
from collections import Counter

WORKSPACE = Path(os.getenv("WORKSPACE", "/Users/ai-driven-work/Documents/OpenClaw-Workspace"))
PROJECTS_DIR = WORKSPACE / "projects"

# エンゲージメント要素と重み
ENGAGEMENT_RULES = {
    "hook_strength": {
        "weight": 25,
        "description": "冒頭のフック（引き込み力）",
        "patterns": {
            "excellent": [
                r"^【速報】", r"^【海外で大バズ】", r"^【結論から言います】",
                r"^【公式が答えを出してしまった】", r"^正直、",
                r"^【海外で話題】", r"^【経験から言います】",
            ],
            "good": [
                r"^\S+が\S+を", r"^今日の", r"^知ってました？",
                r"^実は", r"^これ、", r"^やばい",
            ],
            "weak": [
                r"^今回は", r"^本日は", r"^こんにちは",
                r"^お疲れ様", r"^みなさん",
            ],
        },
    },
    "cta_presence": {
        "weight": 15,
        "description": "CTA（行動喚起）の有無",
        "positive_patterns": [
            r"👇", r"欲しい人", r"いいね.*RT", r"リプ",
            r"フォロー", r"保存", r"ブックマーク", r"シェア",
            r"すべき", r"試してみて", r"使ってみろ",
        ],
    },
    "structure_quality": {
        "weight": 20,
        "description": "構造の質（箇条書き・改行・読みやすさ）",
    },
    "emotional_trigger": {
        "weight": 15,
        "description": "感情トリガー（驚き・危機感・共感）",
        "patterns": [
            r"やばい", r"ヤバい", r"すごい", r"最強",
            r"衝撃", r"驚き", r"まじで", r"本気で",
            r"終わった", r"変わる", r"革命", r"破壊",
            r"🔥", r"😳", r"💀",
        ],
    },
    "specificity": {
        "weight": 15,
        "description": "具体性（数字・固有名詞）",
        "patterns": [
            r"\d+%", r"\$[\d,.]+[MBK]?", r"¥[\d,.]+",
            r"\d+億", r"\d+万", r"\d+倍",
            r"Claude|Cursor|Copilot|ChatGPT|Gemini|Devin|Vercel",
            r"OpenAI|Anthropic|Google|Microsoft|GitHub",
        ],
    },
    "length_optimal": {
        "weight": 10,
        "description": "長さの最適性（140-280文字が最適）",
    },
}


def score_hook(text):
    """フックの強さをスコアリング"""
    first_line = text.strip().split("\n")[0]

    for pattern in ENGAGEMENT_RULES["hook_strength"]["patterns"]["excellent"]:
        if re.search(pattern, first_line):
            return 100, "excellent"

    for pattern in ENGAGEMENT_RULES["hook_strength"]["patterns"]["good"]:
        if re.search(pattern, first_line):
            return 70, "good"

    for pattern in ENGAGEMENT_RULES["hook_strength"]["patterns"]["weak"]:
        if re.search(pattern, first_line):
            return 30, "weak"

    return 50, "neutral"


def score_cta(text):
    """CTAスコアリング"""
    count = 0
    for pattern in ENGAGEMENT_RULES["cta_presence"]["positive_patterns"]:
        if re.search(pattern, text):
            count += 1
    return min(100, count * 35)


def score_structure(text):
    """構造スコアリング"""
    score = 50
    lines = text.strip().split("\n")

    # 箇条書きチェック
    bullet_count = sum(1 for l in lines if re.match(r"^[・・\-•①②③④⑤⑥⑦⑧⑨⑩]", l.strip()))
    if 3 <= bullet_count <= 7:
        score += 25
    elif bullet_count > 0:
        score += 10

    # 改行で読みやすさ
    if len(lines) >= 4:
        score += 15

    # 段落分け（空行）
    empty_lines = sum(1 for l in lines if l.strip() == "")
    if empty_lines >= 2:
        score += 10

    return min(100, score)


def score_emotion(text):
    """感情トリガースコアリング"""
    count = 0
    for pattern in ENGAGEMENT_RULES["emotional_trigger"]["patterns"]:
        if re.search(pattern, text):
            count += 1
    return min(100, count * 25)


def score_specificity(text):
    """具体性スコアリング"""
    count = 0
    for pattern in ENGAGEMENT_RULES["specificity"]["patterns"]:
        matches = re.findall(pattern, text)
        count += len(matches)
    return min(100, count * 20)


def score_length(text):
    """長さスコアリング"""
    # 投稿テキストのみ（見出し除く）
    clean = re.sub(r"^## .*$", "", text, flags=re.MULTILINE).strip()
    length = len(clean)

    if 140 <= length <= 280:
        return 100
    elif 100 <= length <= 400:
        return 75
    elif 50 <= length <= 500:
        return 50
    else:
        return 25


def analyze_post(text):
    """単一投稿を総合分析"""
    scores = {
        "hook": score_hook(text),
        "cta": score_cta(text),
        "structure": score_structure(text),
        "emotion": score_emotion(text),
        "specificity": score_specificity(text),
        "length": score_length(text),
    }

    weights = {
        "hook": 25,
        "cta": 15,
        "structure": 20,
        "emotion": 15,
        "specificity": 15,
        "length": 10,
    }

    hook_score, hook_level = scores["hook"]
    weighted_total = (
        hook_score * weights["hook"]
        + scores["cta"] * weights["cta"]
        + scores["structure"] * weights["structure"]
        + scores["emotion"] * weights["emotion"]
        + scores["specificity"] * weights["specificity"]
        + scores["length"] * weights["length"]
    ) / sum(weights.values())

    improvements = []
    if hook_score < 70:
        improvements.append("💡 フックを強化: 【速報】【海外で大バズ】等のテンプレを使う")
    if scores["cta"] < 50:
        improvements.append("💡 CTA追加: 👇や「〜すべき」で行動を促す")
    if scores["structure"] < 60:
        improvements.append("💡 構造改善: 箇条書き3-5個を追加")
    if scores["emotion"] < 50:
        improvements.append("💡 感情トリガー: 🔥や「やばい」「最強」を適切に使う")
    if scores["specificity"] < 50:
        improvements.append("💡 具体性UP: 数字・固有名詞・%を入れる")

    return {
        "total_score": round(weighted_total, 1),
        "hook": {"score": hook_score, "level": hook_level},
        "cta": scores["cta"],
        "structure": scores["structure"],
        "emotion": scores["emotion"],
        "specificity": scores["specificity"],
        "length": scores["length"],
        "improvements": improvements,
    }


def extract_posts(filepath):
    """ファイルから投稿を抽出"""
    with open(filepath) as f:
        content = f.read()

    posts = []
    sections = re.split(r"## 投稿\d+[：:]?\s*", content)
    for i, section in enumerate(sections[1:], 1):
        # --- で区切られている場合
        text = section.split("---")[0].strip()
        posts.append({"index": i, "text": text})
    return posts


def analyze_file(filepath):
    """ファイル全体を分析"""
    posts = extract_posts(filepath)
    results = []

    for post in posts:
        analysis = analyze_post(post["text"])
        analysis["index"] = post["index"]
        analysis["title"] = post["text"].split("\n")[0][:60]
        results.append(analysis)

    # サマリー
    avg_score = sum(r["total_score"] for r in results) / len(results) if results else 0
    best = max(results, key=lambda x: x["total_score"]) if results else None
    worst = min(results, key=lambda x: x["total_score"]) if results else None

    return {
        "file": str(filepath),
        "post_count": len(results),
        "average_score": round(avg_score, 1),
        "best_post": best,
        "worst_post": worst,
        "posts": results,
    }


def batch_analysis(days=7):
    """バッチ分析（複数日分）"""
    today = datetime.now()
    all_results = {}

    for account in ["aircle", "ichiaimarketer"]:
        account_results = []
        for i in range(days):
            date = today - timedelta(days=i)
            date_str = date.strftime("%Y-%m-%d")
            filepath = PROJECTS_DIR / f"x-posts-{date_str}-{account}.md"
            if filepath.exists():
                result = analyze_file(filepath)
                result["date"] = date_str
                account_results.append(result)
        all_results[account] = account_results

    return all_results


def print_analysis(result):
    """分析結果を表示"""
    print(f"\n📊 エンゲージメント分析: {result['file']}")
    print(f"投稿数: {result['post_count']} | 平均スコア: {result['average_score']}%")
    print("-" * 60)

    for post in result["posts"]:
        emoji = "🟢" if post["total_score"] >= 80 else "🟡" if post["total_score"] >= 60 else "🔴"
        print(f"\n{emoji} #{post['index']} [{post['total_score']}%] {post['title']}")
        print(f"   フック:{post['hook']['score']}({post['hook']['level']}) "
              f"CTA:{post['cta']} 構造:{post['structure']} "
              f"感情:{post['emotion']} 具体性:{post['specificity']} 長さ:{post['length']}")
        if post["improvements"]:
            for imp in post["improvements"]:
                print(f"   {imp}")

    if result["best_post"]:
        print(f"\n🏆 ベスト: #{result['best_post']['index']} [{result['best_post']['total_score']}%]")
    if result["worst_post"]:
        print(f"⚠️ 要改善: #{result['worst_post']['index']} [{result['worst_post']['total_score']}%]")


def main():
    parser = argparse.ArgumentParser(description="エンゲージメント最適化ツール")
    parser.add_argument("--file", help="分析するファイルパス")
    parser.add_argument("--text", help="分析するテキスト")
    parser.add_argument("--batch", action="store_true", help="バッチ分析")
    parser.add_argument("--days", type=int, default=7, help="分析日数")
    parser.add_argument("--json", action="store_true", help="JSON出力")

    args = parser.parse_args()

    if args.text:
        result = analyze_post(args.text)
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(f"スコア: {result['total_score']}%")
            for imp in result["improvements"]:
                print(f"  {imp}")
    elif args.file:
        filepath = Path(args.file)
        if not filepath.is_absolute():
            filepath = WORKSPACE / filepath
        result = analyze_file(filepath)
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print_analysis(result)
    elif args.batch:
        results = batch_analysis(args.days)
        for account, account_results in results.items():
            label = "AirCle" if account == "aircle" else "いち@AIxマーケ"
            print(f"\n{'='*60}")
            print(f"📈 {label} - 過去{args.days}日間のトレンド")
            print(f"{'='*60}")
            for r in account_results:
                print(f"  {r['date']}: {r['post_count']}投稿 | 平均{r['average_score']}%")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
