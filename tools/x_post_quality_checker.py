#!/usr/bin/env python3
"""
X投稿クオリティチェッカー
投稿ファイルを読み込んで品質スコアリング & 改善提案を出す
"""

import re
import sys
import os
from pathlib import Path
from datetime import datetime

# スコアリング基準
HOOK_PATTERNS = {
    "【速報】": 15,
    "【海外で大バズ】": 15,
    "【海外で話題】": 12,
    "【結論から言います】": 18,  # 最強パターン
    "【公式が答えを出してしまった】": 14,
    "正直、": 10,
    "正直，": 10,
}

STRUCTURE_PATTERNS = {
    "箇条書き（•）": (r"•", 5),
    "箇条書き（・）": (r"・", 3),
    "絵文字（👇）": (r"👇", 5),
    "参考リンク": (r"参考:", 3),
    "結び文": (r"(の時代|すべき|が勝つ|始めよう|が正解)", 5),
}

FORBIDDEN_EMOJI = ["📱", "📅", "🔗", "📰", "🚨"]
ALLOWED_EMOJI = ["🔥", "👇", "😳"]

def extract_posts(filepath: str) -> list[dict]:
    """投稿ファイルからポストを抽出"""
    content = Path(filepath).read_text(encoding="utf-8")
    posts = []
    
    # ## 投稿N: で分割
    pattern = r"## 投稿(\d+)[:：]\s*(.+?)(?=\n## 投稿|\n## ■|\Z)"
    matches = re.findall(pattern, content, re.DOTALL)
    
    for num, body in matches:
        # タイトル行を抽出
        lines = body.strip().split("\n")
        title = lines[0].strip() if lines else ""
        full_text = "\n".join(lines).strip()
        
        # ---で終わる場合は除去
        if full_text.endswith("---"):
            full_text = full_text[:-3].strip()
        
        posts.append({
            "num": int(num),
            "title": title,
            "body": full_text,
            "char_count": len(full_text.replace("\n", "").replace(" ", "")),
        })
    
    return posts


def score_post(post: dict) -> dict:
    """個別投稿をスコアリング"""
    body = post["body"]
    scores = {}
    total = 0
    issues = []
    strengths = []
    
    # 1. フックパターンチェック (max 18)
    hook_score = 0
    hook_found = False
    for pattern, score in HOOK_PATTERNS.items():
        if pattern in body:
            hook_score = max(hook_score, score)
            hook_found = True
    scores["フック"] = hook_score
    total += hook_score
    if not hook_found:
        issues.append("⚠️ フックパターン未使用（【速報】【結論から言います】等）")
    else:
        strengths.append(f"✅ フックパターン使用済み (+{hook_score})")
    
    # 2. 構造チェック (max 23)
    struct_score = 0
    for name, (pattern, score) in STRUCTURE_PATTERNS.items():
        if re.search(pattern, body):
            struct_score += score
            strengths.append(f"✅ {name} (+{score})")
    scores["構造"] = struct_score
    total += struct_score
    
    # 3. 具体的数字チェック (max 10)
    numbers = re.findall(r"\$[\d,.]+[MBK]?|[\d,.]+[%％]|[\d,.]+万|[\d,.]+億|[\d,.]+円", body)
    num_score = min(len(numbers) * 3, 10)
    scores["具体性"] = num_score
    total += num_score
    if numbers:
        strengths.append(f"✅ 具体的数字 {len(numbers)}個 (+{num_score})")
    else:
        issues.append("⚠️ 具体的な数字がない")
    
    # 4. 文字数チェック (max 10)
    char_count = post["char_count"]
    if 150 <= char_count <= 500:
        char_score = 10
        strengths.append(f"✅ 文字数 {char_count}文字（適正範囲）")
    elif 100 <= char_count < 150 or 500 < char_count <= 800:
        char_score = 7
        issues.append(f"⚠️ 文字数 {char_count}文字（やや短い/長い）")
    elif char_count < 100:
        char_score = 3
        issues.append(f"❌ 文字数 {char_count}文字（短すぎる）")
    else:
        char_score = 5
        issues.append(f"⚠️ 文字数 {char_count}文字（長すぎる）")
    scores["文字数"] = char_score
    total += char_score
    
    # 5. 禁止絵文字チェック (max 5, 減点方式)
    emoji_score = 5
    for emoji in FORBIDDEN_EMOJI:
        if emoji in body:
            emoji_score -= 2
            issues.append(f"❌ 禁止絵文字 {emoji} 使用")
    emoji_score = max(emoji_score, 0)
    scores["絵文字"] = emoji_score
    total += emoji_score
    
    # 6. CTA (max 5)
    cta_patterns = [r"始めよう", r"学ぼう", r"やるべき", r"やれ", r"使え", r"作れ", r"試せ", r"参考:"]
    cta_score = 0
    for pat in cta_patterns:
        if re.search(pat, body):
            cta_score = 5
            strengths.append("✅ CTA（行動喚起）あり")
            break
    scores["CTA"] = cta_score
    total += cta_score
    if cta_score == 0:
        issues.append("⚠️ CTA（行動喚起）がない")
    
    # 7. 対比構造 (max 5)
    contrast_patterns = [r"今まで.*→", r"Before.*After", r"従来.*→", r"じゃない.*だ", r"ではなく"]
    contrast_score = 0
    for pat in contrast_patterns:
        if re.search(pat, body, re.DOTALL):
            contrast_score = 5
            strengths.append("✅ 対比構造あり")
            break
    scores["対比"] = contrast_score
    total += contrast_score
    
    # 判定
    if total >= 55:
        grade = "S"
    elif total >= 45:
        grade = "A"
    elif total >= 35:
        grade = "B"
    elif total >= 25:
        grade = "C"
    else:
        grade = "D"
    
    return {
        "scores": scores,
        "total": total,
        "max": 76,
        "grade": grade,
        "issues": issues,
        "strengths": strengths,
    }


def analyze_file(filepath: str) -> str:
    """ファイル全体の分析レポートを生成"""
    posts = extract_posts(filepath)
    if not posts:
        return f"❌ {filepath} から投稿を抽出できませんでした"
    
    filename = os.path.basename(filepath)
    report = []
    report.append(f"# 📊 X投稿クオリティレポート")
    report.append(f"**ファイル**: {filename}")
    report.append(f"**投稿数**: {len(posts)}件")
    report.append(f"**分析日時**: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    report.append("")
    
    total_score = 0
    grades = {"S": 0, "A": 0, "B": 0, "C": 0, "D": 0}
    
    for post in posts:
        result = score_post(post)
        total_score += result["total"]
        grades[result["grade"]] += 1
        
        report.append(f"## 投稿{post['num']}: {post['title'][:30]}...")
        report.append(f"**スコア**: {result['total']}/{result['max']} ({result['grade']})")
        report.append(f"**文字数**: {post['char_count']}文字")
        report.append("")
        
        # スコア内訳
        for key, val in result["scores"].items():
            report.append(f"  - {key}: {val}")
        report.append("")
        
        if result["strengths"]:
            for s in result["strengths"][:3]:
                report.append(f"  {s}")
        if result["issues"]:
            for i in result["issues"][:3]:
                report.append(f"  {i}")
        report.append("")
    
    # サマリー
    avg_score = total_score / len(posts) if posts else 0
    report.insert(4, f"**平均スコア**: {avg_score:.1f}/76")
    report.insert(5, f"**グレード分布**: S={grades['S']} A={grades['A']} B={grades['B']} C={grades['C']} D={grades['D']}")
    report.insert(6, "")
    
    return "\n".join(report)


if __name__ == "__main__":
    workspace = "/Users/ai-driven-work/Documents/OpenClaw-Workspace"
    
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
    else:
        # 最新のX投稿ファイルを探す
        projects_dir = os.path.join(workspace, "projects")
        x_files = sorted(
            [f for f in os.listdir(projects_dir) if f.startswith("x-posts-")],
            reverse=True
        )
        if x_files:
            filepath = os.path.join(projects_dir, x_files[0])
        else:
            print("❌ X投稿ファイルが見つかりません")
            sys.exit(1)
    
    print(analyze_file(filepath))
