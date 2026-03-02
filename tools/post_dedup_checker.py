#!/usr/bin/env python3
"""
Post Deduplication Checker v1.0
X投稿の重複・類似チェックツール。
過去の投稿と比較して、ネタ被りや類似表現を検出する。

Usage:
  python3 tools/post_dedup_checker.py <new_posts.md>                     # 新投稿ファイルをチェック
  python3 tools/post_dedup_checker.py <new_posts.md> --days 7            # 過去7日分と比較
  python3 tools/post_dedup_checker.py <new_posts.md> --threshold 0.6     # 類似度閾値
"""

import sys
import re
import json
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Optional
from collections import Counter
import unicodedata

WORKSPACE = Path("/Users/ai-driven-work/Documents/OpenClaw-Workspace")
PROJECTS_DIR = WORKSPACE / "projects"


def normalize_text(text: str) -> str:
    """テキストを正規化（比較用）"""
    text = unicodedata.normalize("NFKC", text)
    text = text.lower()
    text = re.sub(r'https?://\S+', '', text)
    text = re.sub(r'[【】「」『』（）()\[\]{}]', ' ', text)
    text = re.sub(r'[・、。！？!?.,;:\-—]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def extract_keywords(text: str, min_len: int = 2) -> set:
    """テキストからキーワードを抽出"""
    normalized = normalize_text(text)
    # 日本語単語（カタカナ、漢字）と英数字を抽出
    words = set()
    # カタカナ語
    words.update(re.findall(r'[ァ-ヶー]{2,}', normalized))
    # 英語語
    words.update(w for w in re.findall(r'[a-z]{3,}', normalized))
    # 数字含む
    words.update(re.findall(r'\d+[a-z]+|\$[\d.]+[bm]', normalized))
    # 特定の重要語
    important = re.findall(r'cursor|claude|openai|anthropic|google|notion|vscode|copilot|'
                          r'vercel|openclaw|grok|perplexity|midjourney|jasper|chatgpt|'
                          r'gemini|xcode|github|agent|エージェント|コンパイラ|障害|'
                          r'脆弱性|セキュリティ|アルゴリズム|マーケティング', normalized)
    words.update(important)
    return {w for w in words if len(w) >= min_len}


def jaccard_similarity(set_a: set, set_b: set) -> float:
    """Jaccard類似度を計算"""
    if not set_a or not set_b:
        return 0.0
    intersection = set_a & set_b
    union = set_a | set_b
    return len(intersection) / len(union)


def extract_posts_from_file(filepath: Path) -> list:
    """ファイルから投稿を抽出"""
    if not filepath.exists():
        return []
    content = filepath.read_text(encoding="utf-8")
    posts = []
    current_title = ""
    current_body = []

    for line in content.split("\n"):
        if line.startswith("## 投稿"):
            if current_title and current_body:
                posts.append({
                    "title": current_title,
                    "body": "\n".join(current_body).strip(),
                    "source": str(filepath),
                })
            current_title = line.replace("## ", "").strip()
            current_body = []
        elif line.startswith("---"):
            if current_title and current_body:
                posts.append({
                    "title": current_title,
                    "body": "\n".join(current_body).strip(),
                    "source": str(filepath),
                })
                current_title = ""
                current_body = []
        elif current_title:
            current_body.append(line)

    # 最後の投稿
    if current_title and current_body:
        posts.append({
            "title": current_title,
            "body": "\n".join(current_body).strip(),
            "source": str(filepath),
        })

    return posts


def load_past_posts(days: int = 7) -> list:
    """過去の投稿を読み込み"""
    all_posts = []
    today = datetime.now()

    for d in range(1, days + 1):
        date = today - timedelta(days=d)
        date_str = date.strftime("%Y-%m-%d")
        for suffix in ["aircle", "ichiaimarketer"]:
            filepath = PROJECTS_DIR / f"x-posts-{date_str}-{suffix}.md"
            posts = extract_posts_from_file(filepath)
            all_posts.extend(posts)

    return all_posts


@dataclass
class DupResult:
    new_title: str
    similar_title: str
    similarity: float
    shared_keywords: set
    source: str


def check_duplicates(new_file: Path, days: int = 7, threshold: float = 0.35) -> list:
    """重複チェック実行"""
    new_posts = extract_posts_from_file(new_file)
    past_posts = load_past_posts(days)

    if not new_posts:
        print(f"⚠️ {new_file} から投稿が見つかりません")
        return []

    results = []

    for new_post in new_posts:
        new_kw = extract_keywords(new_post["body"])

        for past_post in past_posts:
            past_kw = extract_keywords(past_post["body"])
            sim = jaccard_similarity(new_kw, past_kw)

            if sim >= threshold:
                shared = new_kw & past_kw
                results.append(DupResult(
                    new_title=new_post["title"],
                    similar_title=past_post["title"],
                    similarity=sim,
                    shared_keywords=shared,
                    source=past_post["source"],
                ))

    return sorted(results, key=lambda x: x.similarity, reverse=True)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Post Deduplication Checker")
    parser.add_argument("file", help="チェック対象ファイル")
    parser.add_argument("--days", type=int, default=7, help="比較対象の日数")
    parser.add_argument("--threshold", type=float, default=0.35, help="類似度閾値")
    args = parser.parse_args()

    filepath = Path(args.file)
    if not filepath.exists():
        print(f"❌ ファイルが見つかりません: {filepath}")
        sys.exit(1)

    print(f"🔍 重複チェック: {filepath.name}")
    print(f"   比較対象: 過去{args.days}日分 | 閾値: {args.threshold}")
    print()

    results = check_duplicates(filepath, args.days, args.threshold)

    if not results:
        print("✅ 重複・類似投稿なし！全投稿オリジナルです。")
        return

    print(f"⚠️ {len(results)}件の類似投稿を検出:")
    print()

    for r in results:
        sim_pct = r.similarity * 100
        bar = "🟥" if sim_pct > 60 else "🟧" if sim_pct > 45 else "🟨"
        print(f"  {bar} 類似度 {sim_pct:.0f}%")
        print(f"     新: {r.new_title}")
        print(f"     旧: {r.similar_title}")
        print(f"     共通: {', '.join(list(r.shared_keywords)[:8])}")
        source_name = Path(r.source).name
        print(f"     ソース: {source_name}")
        print()


if __name__ == "__main__":
    main()
