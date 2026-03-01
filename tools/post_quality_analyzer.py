#!/usr/bin/env python3
"""
Post Quality Analyzer v1.0
X投稿の品質を自動分析し、改善提案を出力するツール。
過去のバズ投稿パターンとの類似度をスコアリングする。

Usage:
  python3 tools/post_quality_analyzer.py <post_file.md>
  python3 tools/post_quality_analyzer.py <post_file.md> --format json
  python3 tools/post_quality_analyzer.py <post_file.md> --verbose
"""

import sys
import re
import json
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Optional


# === バズ投稿パターン定義 ===

BUZZ_PATTERNS = {
    "速報型": {
        "triggers": ["【速報】", "【速報｜"],
        "avg_likes": 173.2,
        "description": "ニュース速報形式。タイムリーな情報をいち早く届ける",
    },
    "海外バズ型": {
        "triggers": ["【海外で大バズ】", "【海外で話題】"],
        "avg_likes": 120.0,
        "description": "海外の話題を日本語で紹介。翻訳価値を提供",
    },
    "結論型": {
        "triggers": ["【結論から言います】", "結論から言う"],
        "avg_likes": 306.7,
        "description": "結論ファースト。最もエンゲージメントが高い型",
    },
    "公式型": {
        "triggers": ["【公式が答えを出してしまった】", "【公式発表】"],
        "avg_likes": 200.0,
        "description": "公式ソースからの情報。信頼性が高い",
    },
    "正直型": {
        "triggers": ["正直、", "正直に言うと"],
        "avg_likes": 150.0,
        "description": "率直な意見を述べる。共感を呼ぶ",
    },
    "配布型": {
        "triggers": ["欲しい人いますか", "配布します", "無料公開", "プレゼント"],
        "avg_likes": 100.0,
        "avg_rts": 35.1,
        "description": "コンテンツ配布。RT数が最も高い型",
    },
}

# 禁止絵文字リスト
BANNED_EMOJIS = ["📱", "📅", "🔗", "📰", "🚨", "📊", "💻", "🤖", "📢"]
ALLOWED_EMOJIS = ["🔥", "👇", "😳"]

# 構成パターン
STRUCTURE_PATTERNS = {
    "hook_to_list": re.compile(r"(何を意味するか|どういうことか|これがやばい).*(👇|↓)"),
    "closing_phrase": re.compile(r"(すべき|の時代|始まった|終了).*[。！]?$", re.MULTILINE),
    "bullet_points": re.compile(r"[•·①②③④⑤⑥⑦⑧⑨⑩]"),
    "reference_link": re.compile(r"https?://\S+"),
}


@dataclass
class PostAnalysis:
    """1投稿の分析結果"""
    title: str = ""
    text: str = ""
    char_count: int = 0
    pattern_type: str = "不明"
    pattern_score: float = 0.0
    structure_score: float = 0.0
    emoji_score: float = 0.0
    hook_score: float = 0.0
    closing_score: float = 0.0
    reference_score: float = 0.0
    total_score: float = 0.0
    issues: list = field(default_factory=list)
    suggestions: list = field(default_factory=list)


def detect_pattern(text: str) -> tuple[str, float]:
    """投稿のパターン型を検出"""
    for name, pattern in BUZZ_PATTERNS.items():
        for trigger in pattern["triggers"]:
            if trigger in text:
                return name, 1.0
    return "不明", 0.0


def check_emojis(text: str) -> tuple[float, list]:
    """絵文字の使用状況をチェック"""
    issues = []
    score = 1.0

    for emoji in BANNED_EMOJIS:
        if emoji in text:
            issues.append(f"禁止絵文字 {emoji} が使われています")
            score -= 0.15

    emoji_count = sum(1 for c in text if ord(c) > 0x1F600)
    if emoji_count > 5:
        issues.append(f"絵文字が多すぎます（{emoji_count}個）→ 3個以下推奨")
        score -= 0.2

    return max(0, score), issues


def check_structure(text: str) -> tuple[float, list, list]:
    """投稿の構成をチェック"""
    score = 0.0
    issues = []
    suggestions = []

    # フック → リスト構成チェック
    if STRUCTURE_PATTERNS["hook_to_list"].search(text):
        score += 0.3
    else:
        suggestions.append("「これ、何を意味するか👇」でリストに繋げると効果的")

    # 箇条書きチェック
    bullets = len(STRUCTURE_PATTERNS["bullet_points"].findall(text))
    if bullets >= 3:
        score += 0.3
    elif bullets > 0:
        score += 0.15
    else:
        suggestions.append("箇条書き（•）を3つ以上使うと読みやすい")

    # 番号リスト（①②③）の多用チェック
    numbered = len(re.findall(r"[①②③④⑤⑥⑦⑧⑨⑩]", text))
    if numbered > 5:
        issues.append(f"番号リスト({numbered}個)が多すぎます → 箇条書き(•)推奨")

    # クロージングフレーズチェック
    if STRUCTURE_PATTERNS["closing_phrase"].search(text):
        score += 0.2
    else:
        suggestions.append("「〜すべき」「〜の時代」で締めると印象に残る")

    # 参考URLチェック
    if STRUCTURE_PATTERNS["reference_link"].search(text):
        score += 0.2
    else:
        suggestions.append("参考URLを追加すると信頼性UP")

    return score, issues, suggestions


def check_hook(text: str) -> float:
    """冒頭のフック力をチェック"""
    first_line = text.strip().split("\n")[0] if text.strip() else ""
    score = 0.0

    # 【】で始まるかチェック
    if re.match(r"【.+】", first_line):
        score += 0.5

    # 感情的な表現
    emotion_words = ["やばい", "衝撃", "異常", "革命", "崩壊", "終了", "パニック", "戦争"]
    if any(w in first_line for w in emotion_words):
        score += 0.3

    # 具体的な数字
    if re.search(r"\d+", first_line):
        score += 0.2

    return min(1.0, score)


def check_closing(text: str) -> float:
    """締めの力をチェック"""
    lines = [l.strip() for l in text.strip().split("\n") if l.strip()]
    if not lines:
        return 0.0

    last_lines = "\n".join(lines[-3:])
    score = 0.0

    closing_patterns = [
        "の時代", "すべき", "が始まった", "終了のお知らせ",
        "さあ、", "やらない理由", "もう遅い", "覚悟しろ",
    ]
    if any(p in last_lines for p in closing_patterns):
        score += 0.6

    # CTA（行動喚起）チェック
    cta_patterns = ["フォロー", "RT", "リツイート", "いいね", "チェック"]
    if any(p in last_lines for p in cta_patterns):
        score += 0.4

    return min(1.0, score)


def analyze_post(text: str, title: str = "") -> PostAnalysis:
    """1投稿を分析"""
    analysis = PostAnalysis()
    analysis.title = title
    analysis.text = text
    analysis.char_count = len(text)

    # パターン検出
    analysis.pattern_type, analysis.pattern_score = detect_pattern(text)

    # 絵文字チェック
    analysis.emoji_score, emoji_issues = check_emojis(text)
    analysis.issues.extend(emoji_issues)

    # 構成チェック
    analysis.structure_score, struct_issues, struct_suggestions = check_structure(text)
    analysis.issues.extend(struct_issues)
    analysis.suggestions.extend(struct_suggestions)

    # フックチェック
    analysis.hook_score = check_hook(text)
    if analysis.hook_score < 0.5:
        analysis.suggestions.append("冒頭に【速報】【結論から言います】などのフックを追加")

    # クロージングチェック
    analysis.closing_score = check_closing(text)
    if analysis.closing_score < 0.5:
        analysis.suggestions.append("「〜の時代」「〜すべき」で締めると余韻が残る")

    # 参考URLチェック
    if STRUCTURE_PATTERNS["reference_link"].search(text):
        analysis.reference_score = 1.0

    # 文字数チェック
    if analysis.char_count < 100:
        analysis.issues.append(f"短すぎます（{analysis.char_count}文字）→ 200文字以上推奨")
    elif analysis.char_count > 600:
        analysis.suggestions.append(f"長文（{analysis.char_count}文字）→ ノート投稿推奨")

    # 総合スコア計算（重み付き）
    weights = {
        "pattern": 0.20,
        "hook": 0.25,
        "structure": 0.20,
        "closing": 0.15,
        "emoji": 0.10,
        "reference": 0.10,
    }
    analysis.total_score = (
        analysis.pattern_score * weights["pattern"]
        + analysis.hook_score * weights["hook"]
        + analysis.structure_score * weights["structure"]
        + analysis.closing_score * weights["closing"]
        + analysis.emoji_score * weights["emoji"]
        + analysis.reference_score * weights["reference"]
    )

    return analysis


def parse_posts_from_md(filepath: str) -> list[tuple[str, str]]:
    """Markdownファイルから投稿を抽出"""
    content = Path(filepath).read_text(encoding="utf-8")
    posts = []

    # "## 投稿N:" パターンで分割
    sections = re.split(r"(?=##\s*投稿\d+)", content)

    for section in sections:
        title_match = re.match(r"##\s*(投稿\d+[^\n]*)", section)
        if title_match:
            title = title_match.group(1).strip()
            # タイトル行を除いた本文
            body = section[title_match.end():].strip()
            # 次のセクション区切り（---）まで
            body = re.split(r"\n---\s*$", body, maxsplit=1)[0].strip()
            if body:
                posts.append((title, body))

    return posts


def print_report(analyses: list[PostAnalysis], verbose: bool = False):
    """分析レポートを出力"""
    print("=" * 60)
    print("📊 X投稿 品質分析レポート")
    print("=" * 60)

    total_score_sum = 0
    issue_count = 0

    for i, a in enumerate(analyses, 1):
        stars = "⭐" * max(1, round(a.total_score * 5))
        grade = (
            "S" if a.total_score >= 0.85
            else "A" if a.total_score >= 0.70
            else "B" if a.total_score >= 0.55
            else "C" if a.total_score >= 0.40
            else "D"
        )

        print(f"\n{'─' * 50}")
        print(f"📝 {a.title}")
        print(f"   スコア: {a.total_score:.0%} [{grade}] {stars}")
        print(f"   型: {a.pattern_type} | 文字数: {a.char_count}")

        if verbose:
            print(f"   📌 フック: {a.hook_score:.0%} | 構成: {a.structure_score:.0%} | 締め: {a.closing_score:.0%}")
            print(f"   🎨 絵文字: {a.emoji_score:.0%} | 参考URL: {a.reference_score:.0%}")

        if a.issues:
            for issue in a.issues:
                print(f"   ⚠️  {issue}")
            issue_count += len(a.issues)

        if a.suggestions and verbose:
            for sug in a.suggestions:
                print(f"   💡 {sug}")

        total_score_sum += a.total_score

    avg_score = total_score_sum / len(analyses) if analyses else 0

    print(f"\n{'=' * 60}")
    print(f"📈 サマリー")
    print(f"   投稿数: {len(analyses)}")
    print(f"   平均スコア: {avg_score:.0%}")
    print(f"   問題点: {issue_count}件")

    # パターン分布
    pattern_counts = {}
    for a in analyses:
        pattern_counts[a.pattern_type] = pattern_counts.get(a.pattern_type, 0) + 1
    print(f"   パターン分布:")
    for p, c in sorted(pattern_counts.items(), key=lambda x: -x[1]):
        print(f"     {p}: {c}投稿")
    print("=" * 60)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    filepath = sys.argv[1]
    verbose = "--verbose" in sys.argv or "-v" in sys.argv
    as_json = "--format" in sys.argv and "json" in sys.argv

    if not Path(filepath).exists():
        print(f"❌ ファイルが見つかりません: {filepath}")
        sys.exit(1)

    posts = parse_posts_from_md(filepath)
    if not posts:
        print("❌ 投稿が見つかりません。フォーマットを確認してください。")
        sys.exit(1)

    analyses = [analyze_post(body, title) for title, body in posts]

    if as_json:
        output = [asdict(a) for a in analyses]
        print(json.dumps(output, ensure_ascii=False, indent=2))
    else:
        print_report(analyses, verbose)


if __name__ == "__main__":
    main()
