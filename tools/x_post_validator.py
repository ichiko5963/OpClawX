#!/usr/bin/env python3
"""
X投稿バリデーター
投稿ファイルを読み込んで、品質チェック・フォーマット検証を行う。
"""

import re
import sys
from pathlib import Path
from collections import Counter


# 禁止絵文字リスト
BANNED_EMOJI = ["📱", "📅", "🔗", "📰", "🚨", "📊", "📈", "📉", "💼", "📋"]

# 許可絵文字リスト
ALLOWED_EMOJI = ["🔥", "👇", "😳"]

# バズ型パターン
BUZZ_PATTERNS = [
    r"【速報】",
    r"【海外で大バズ】",
    r"【海外で話題】",
    r"【結論から言います】",
    r"【公式が答えを出してしまった】",
    r"正直、",
    r"欲しい人いますか",
]

# 締めのパターン
CLOSING_PATTERNS = [
    r"すべき",
    r"の時代",
    r"の始まり",
    r"終了のお知らせ",
    r"準備できてる",
    r"忘れるな",
]


def extract_posts(filepath: str) -> list[dict]:
    """投稿ファイルからポストを抽出"""
    content = Path(filepath).read_text(encoding="utf-8")
    posts = []
    
    pattern = r"## 投稿(\d+)[:：]\s*(.+?)(?=\n## 投稿|\n## ■|\Z)"
    matches = re.findall(pattern, content, re.DOTALL)
    
    for num, body in matches:
        lines = body.strip().split("\n")
        full_text = "\n".join(lines).strip()
        
        if full_text.endswith("---"):
            full_text = full_text[:-3].strip()
        
        # 投稿本文（参考URL行を除去）
        post_body = re.sub(r"\n参考:\s*https?://\S+", "", full_text).strip()
        
        # 参考URLを抽出
        ref_match = re.search(r"参考:\s*(https?://\S+)", full_text)
        ref_url = ref_match.group(1) if ref_match else None
        
        posts.append({
            "num": int(num),
            "body": post_body,
            "ref_url": ref_url,
            "char_count": len(post_body.replace("\n", "")),
        })
    
    return posts


def check_banned_emoji(text: str) -> list[str]:
    """禁止絵文字チェック"""
    found = []
    for emoji in BANNED_EMOJI:
        if emoji in text:
            found.append(emoji)
    return found


def check_buzz_pattern(text: str) -> str | None:
    """バズ型パターンチェック"""
    for pattern in BUZZ_PATTERNS:
        if re.search(pattern, text):
            return pattern
    return None


def check_closing(text: str) -> bool:
    """締めのパターンチェック"""
    last_lines = text.strip().split("\n")[-3:]
    last_text = "\n".join(last_lines)
    for pattern in CLOSING_PATTERNS:
        if re.search(pattern, last_text):
            return True
    return False


def check_bullet_points(text: str) -> int:
    """箇条書きの数"""
    return len(re.findall(r"^[•・①②③④⑤⑥⑦⑧⑨⑩]", text, re.MULTILINE))


def check_numbered_lists(text: str) -> int:
    """番号リストの数"""
    return len(re.findall(r"^[①②③④⑤⑥⑦⑧⑨⑩]", text, re.MULTILINE))


def validate_post(post: dict) -> dict:
    """1つの投稿を検証"""
    issues = []
    warnings = []
    score = 100
    
    body = post["body"]
    char_count = post["char_count"]
    
    # 1. 文字数チェック
    if char_count < 100:
        issues.append(f"文字数が少なすぎる ({char_count}文字)")
        score -= 20
    elif char_count > 500:
        warnings.append(f"文字数が多め ({char_count}文字)")
        score -= 5
    
    # 2. 禁止絵文字チェック
    banned = check_banned_emoji(body)
    if banned:
        issues.append(f"禁止絵文字使用: {', '.join(banned)}")
        score -= 10 * len(banned)
    
    # 3. バズ型パターンチェック
    pattern = check_buzz_pattern(body)
    if pattern:
        score += 5  # ボーナス
    else:
        warnings.append("バズ型パターンが使われていない")
        score -= 5
    
    # 4. 箇条書きチェック
    bullets = check_bullet_points(body)
    if bullets == 0:
        warnings.append("箇条書きがない")
        score -= 5
    elif bullets > 8:
        warnings.append(f"箇条書きが多すぎる ({bullets}個)")
        score -= 3
    
    # 5. 番号リストチェック
    numbered = check_numbered_lists(body)
    if numbered > 5:
        warnings.append(f"番号リスト多用 ({numbered}個)")
        score -= 5
    
    # 6. 締めのパターンチェック
    has_closing = check_closing(body)
    if has_closing:
        score += 3  # ボーナス
    
    # 7. 参考URLチェック
    if post["ref_url"]:
        score += 2  # ボーナス
    
    # スコア上限
    score = max(0, min(100, score))
    
    return {
        "num": post["num"],
        "char_count": char_count,
        "score": score,
        "buzz_pattern": pattern,
        "has_closing": has_closing,
        "has_ref_url": post["ref_url"] is not None,
        "issues": issues,
        "warnings": warnings,
    }


def validate_file(filepath: str) -> dict:
    """ファイル全体を検証"""
    posts = extract_posts(filepath)
    results = []
    
    for post in posts:
        result = validate_post(post)
        results.append(result)
    
    # 全体統計
    scores = [r["score"] for r in results]
    avg_score = sum(scores) / len(scores) if scores else 0
    
    pattern_counts = Counter(r["buzz_pattern"] for r in results if r["buzz_pattern"])
    
    return {
        "filepath": filepath,
        "total_posts": len(posts),
        "avg_score": round(avg_score, 1),
        "min_score": min(scores) if scores else 0,
        "max_score": max(scores) if scores else 0,
        "pattern_distribution": dict(pattern_counts),
        "posts": results,
    }


def print_report(report: dict):
    """レポートを出力"""
    print(f"\n{'='*60}")
    print(f"📊 X投稿バリデーション結果")
    print(f"ファイル: {report['filepath']}")
    print(f"{'='*60}")
    print(f"投稿数: {report['total_posts']}")
    print(f"平均スコア: {report['avg_score']}/100")
    print(f"最低スコア: {report['min_score']} / 最高スコア: {report['max_score']}")
    print()
    
    if report["pattern_distribution"]:
        print("📝 バズ型パターン分布:")
        for pattern, count in report["pattern_distribution"].items():
            print(f"  {pattern}: {count}回")
        print()
    
    print("📋 投稿別結果:")
    for post in report["posts"]:
        status = "✅" if post["score"] >= 80 else "⚠️" if post["score"] >= 60 else "❌"
        print(f"  {status} 投稿{post['num']}: スコア{post['score']} ({post['char_count']}文字)")
        
        if post["issues"]:
            for issue in post["issues"]:
                print(f"     ❌ {issue}")
        
        if post["warnings"]:
            for warning in post["warnings"]:
                print(f"     ⚠️ {warning}")
    
    print(f"\n{'='*60}")


def main():
    if len(sys.argv) < 2:
        print("Usage: x_post_validator.py <filepath>")
        print("Example: x_post_validator.py projects/x-posts-2026-03-01-aircle.md")
        return
    
    filepath = sys.argv[1]
    if not Path(filepath).exists():
        print(f"File not found: {filepath}")
        return
    
    report = validate_file(filepath)
    print_report(report)


if __name__ == "__main__":
    main()
