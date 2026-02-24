#!/usr/bin/env python3
"""
X投稿 自動改善ツール
投稿ファイルを読み込んで、品質チェック → 改善提案 → レポート生成を行う

機能:
1. 投稿の構造分析（フック/本文/CTA）
2. 文字数最適化チェック
3. バズりやすさスコア（型マッチング）
4. 重複チェック（過去投稿との類似度）
5. 改善レポート生成
"""

import re
import sys
import os
import json
from pathlib import Path
from datetime import datetime
from collections import Counter

# バズる型パターン
HOOK_PATTERNS = {
    "速報型": [r"【速報】", r"速報"],
    "海外バズ型": [r"【海外で大バズ】", r"【海外で話題】", r"海外で"],
    "結論型": [r"【結論から言います】", r"結論から"],
    "公式型": [r"【公式が答えを出してしまった】", r"公式が"],
    "正直型": [r"^正直、", r"^正直"],
    "配布型": [r"欲しい人いますか", r"欲しい人"],
    "驚愕型": [r"エグ", r"ヤバ", r"やば"],
}

# 禁止絵文字
BANNED_EMOJI = ["📱", "📅", "🔗", "📰", "🚨", "📊", "📈", "📉", "💻", "🖥"]

# 推奨絵文字
GOOD_EMOJI = ["🔥", "👇", "😳"]

# 構造パターン
STRUCTURE_PATTERNS = {
    "箇条書き": r"[•·・]",
    "矢印展開": r"→",
    "ナンバリング": r"[①②③④⑤⑥⑦⑧⑨⑩]|\d+\.",
}

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
        
        ref_match = re.search(r"参考:\s*(https?://\S+)", full_text)
        ref_url = ref_match.group(1) if ref_match else None
        post_body = re.sub(r"\n参考:\s*https?://\S+", "", full_text).strip()
        
        posts.append({
            "num": int(num),
            "body": post_body,
            "ref_url": ref_url,
        })
    return posts


def analyze_hook(text: str) -> dict:
    """フック（冒頭）の型を判定"""
    first_line = text.split("\n")[0]
    matched_types = []
    for pattern_name, patterns in HOOK_PATTERNS.items():
        for p in patterns:
            if re.search(p, first_line):
                matched_types.append(pattern_name)
                break
    return {
        "first_line": first_line,
        "matched_types": matched_types,
        "has_hook": len(matched_types) > 0,
    }


def analyze_structure(text: str) -> dict:
    """投稿の構造を分析"""
    lines = text.split("\n")
    non_empty = [l for l in lines if l.strip()]
    
    structures_found = []
    for name, pattern in STRUCTURE_PATTERNS.items():
        if re.search(pattern, text):
            structures_found.append(name)
    
    # CTAチェック
    has_cta = False
    cta_keywords = ["時代", "すべき", "始める", "やるべき", "必見", "保存推奨", "RT"]
    last_lines = "\n".join(lines[-3:]) if len(lines) >= 3 else text
    for kw in cta_keywords:
        if kw in last_lines:
            has_cta = True
            break
    
    # 「これ、何を意味するか👇」パターン
    has_transition = "👇" in text or "何を意味するか" in text
    
    return {
        "line_count": len(non_empty),
        "structures": structures_found,
        "has_cta": has_cta,
        "has_transition": has_transition,
    }


def analyze_emoji(text: str) -> dict:
    """絵文字使用状況を分析"""
    import unicodedata
    banned_found = [e for e in BANNED_EMOJI if e in text]
    good_found = [e for e in GOOD_EMOJI if e in text]
    
    # 全絵文字カウント
    all_emoji = []
    for char in text:
        if unicodedata.category(char).startswith("So"):
            all_emoji.append(char)
    
    return {
        "total_emoji": len(all_emoji),
        "banned": banned_found,
        "good": good_found,
        "excessive": len(all_emoji) > 5,
    }


def analyze_char_count(text: str) -> dict:
    """文字数分析（X投稿として）"""
    clean = text.replace("\n", "").replace(" ", "").replace("　", "")
    # 参考URLは除外
    clean = re.sub(r"https?://\S+", "", clean)
    count = len(clean)
    
    if count < 100:
        rating = "短すぎ"
    elif count < 200:
        rating = "やや短い"
    elif count < 400:
        rating = "最適"
    elif count < 600:
        rating = "やや長い"
    else:
        rating = "長すぎ"
    
    return {
        "char_count": count,
        "rating": rating,
        "optimal": 200 <= count <= 400,
    }


def score_post(post: dict) -> dict:
    """投稿をスコアリング"""
    text = post["body"]
    
    hook = analyze_hook(text)
    structure = analyze_structure(text)
    emoji = analyze_emoji(text)
    chars = analyze_char_count(text)
    
    # スコア計算 (100点満点)
    score = 0
    details = []
    
    # フック (25点)
    if hook["has_hook"]:
        score += 25
        details.append(f"✅ フック: {', '.join(hook['matched_types'])}")
    else:
        score += 5
        details.append("⚠️ フック: 型なし（速報/結論/海外バズ等推奨）")
    
    # 構造 (25点)
    if structure["has_transition"]:
        score += 10
        details.append("✅ 展開: 👇トランジションあり")
    if structure["structures"]:
        score += 10
        details.append(f"✅ 構造: {', '.join(structure['structures'])}")
    if structure["has_cta"]:
        score += 5
        details.append("✅ CTA: 締めあり")
    else:
        details.append("⚠️ CTA: 締めが弱い（「〜の時代」「〜すべき」推奨）")
    
    # 文字数 (20点)
    if chars["optimal"]:
        score += 20
        details.append(f"✅ 文字数: {chars['char_count']}字 ({chars['rating']})")
    elif chars["rating"] in ["やや短い", "やや長い"]:
        score += 10
        details.append(f"⚠️ 文字数: {chars['char_count']}字 ({chars['rating']})")
    else:
        score += 0
        details.append(f"❌ 文字数: {chars['char_count']}字 ({chars['rating']})")
    
    # 絵文字 (15点)
    if emoji["banned"]:
        score += 0
        details.append(f"❌ 禁止絵文字: {', '.join(emoji['banned'])}")
    elif emoji["excessive"]:
        score += 5
        details.append("⚠️ 絵文字: 使いすぎ（5個以上）")
    else:
        score += 15
        details.append(f"✅ 絵文字: OK ({emoji['total_emoji']}個)")
    
    # 具体性 (15点)
    has_specifics = bool(re.search(r"\d+[%万億ドル$人社件]", text))
    has_tool_name = bool(re.search(r"(Claude|Cursor|ChatGPT|OpenAI|Anthropic|GitHub|Vercel|Figma|Notion|Stripe|AWS)", text))
    if has_specifics and has_tool_name:
        score += 15
        details.append("✅ 具体性: 数字+固有名詞あり")
    elif has_specifics or has_tool_name:
        score += 8
        details.append("⚠️ 具体性: 数字or固有名詞が片方のみ")
    else:
        details.append("❌ 具体性: 数字・固有名詞なし")
    
    # グレード
    if score >= 85:
        grade = "S"
    elif score >= 70:
        grade = "A"
    elif score >= 55:
        grade = "B"
    elif score >= 40:
        grade = "C"
    else:
        grade = "D"
    
    return {
        "num": post["num"],
        "score": score,
        "grade": grade,
        "details": details,
        "hook": hook,
        "structure": structure,
        "emoji": emoji,
        "chars": chars,
    }


def check_duplicates(posts: list[dict], threshold: float = 0.4) -> list[dict]:
    """投稿間の重複チェック（簡易的なキーワードベース）"""
    duplicates = []
    
    for i in range(len(posts)):
        for j in range(i + 1, len(posts)):
            words_i = set(re.findall(r"[\w]+", posts[i]["body"]))
            words_j = set(re.findall(r"[\w]+", posts[j]["body"]))
            
            if not words_i or not words_j:
                continue
            
            overlap = len(words_i & words_j) / min(len(words_i), len(words_j))
            if overlap > threshold:
                duplicates.append({
                    "post_a": posts[i]["num"],
                    "post_b": posts[j]["num"],
                    "similarity": round(overlap * 100, 1),
                })
    
    return duplicates


def generate_report(filepath: str) -> str:
    """分析レポート生成"""
    posts = extract_posts(filepath)
    if not posts:
        return "❌ 投稿が見つかりませんでした"
    
    results = [score_post(p) for p in posts]
    duplicates = check_duplicates(posts)
    
    # サマリー
    avg_score = sum(r["score"] for r in results) / len(results)
    grade_counts = Counter(r["grade"] for r in results)
    
    report = []
    report.append(f"# X投稿 品質レポート")
    report.append(f"ファイル: {os.path.basename(filepath)}")
    report.append(f"投稿数: {len(posts)}")
    report.append(f"平均スコア: {avg_score:.1f}/100")
    report.append(f"グレード分布: " + ", ".join(f"{g}={c}" for g, c in sorted(grade_counts.items())))
    report.append("")
    
    # 各投稿の詳細
    for r in results:
        report.append(f"## 投稿{r['num']} [{r['grade']}] {r['score']}点")
        for d in r["details"]:
            report.append(f"  {d}")
        report.append("")
    
    # 重複警告
    if duplicates:
        report.append("## ⚠️ 重複警告")
        for d in duplicates:
            report.append(f"  投稿{d['post_a']} ↔ 投稿{d['post_b']}: 類似度 {d['similarity']}%")
        report.append("")
    
    # 改善サマリー
    low_scores = [r for r in results if r["score"] < 70]
    if low_scores:
        report.append("## 🔧 改善が必要な投稿")
        for r in low_scores:
            issues = [d for d in r["details"] if d.startswith("⚠️") or d.startswith("❌")]
            report.append(f"  投稿{r['num']} ({r['score']}点): {'; '.join(issues)}")
    
    return "\n".join(report)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使い方: python x_post_auto_improver.py <投稿ファイル.md>")
        sys.exit(1)
    
    filepath = sys.argv[1]
    if not os.path.exists(filepath):
        print(f"❌ ファイルが見つかりません: {filepath}")
        sys.exit(1)
    
    report = generate_report(filepath)
    print(report)
