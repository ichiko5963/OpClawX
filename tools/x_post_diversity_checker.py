#!/usr/bin/env python3
"""
X Post Diversity Checker - 投稿の多様性・重複チェックツール
過去の投稿と新しい投稿を比較し、テーマの重複や表現の使い回しを検出する。
"""

import os
import re
import sys
from pathlib import Path
from datetime import datetime, timedelta
from collections import Counter, defaultdict
import json


WORKSPACE = Path(os.environ.get("WORKSPACE", "/Users/ai-driven-work/Documents/OpenClaw-Workspace"))
PROJECTS_DIR = WORKSPACE / "projects"


def extract_posts_from_file(filepath: Path) -> list[dict]:
    """マークダウンファイルからポストを抽出"""
    content = filepath.read_text(encoding="utf-8")
    posts = []
    
    pattern = r"## 投稿(\d+)[:：]\s*(.+?)(?=\n## 投稿|\n## ■|\Z)"
    matches = re.findall(pattern, content, re.DOTALL)
    
    for num, body in matches:
        body = body.strip()
        if body.endswith("---"):
            body = body[:-3].strip()
        
        # 型を判定
        post_type = "other"
        if body.startswith("【速報】"):
            post_type = "速報"
        elif body.startswith("【海外で大バズ】") or body.startswith("【海外で話題】"):
            post_type = "海外バズ"
        elif body.startswith("【結論から言います】"):
            post_type = "結論"
        elif body.startswith("【公式が答えを出してしまった】"):
            post_type = "公式"
        elif body.startswith("正直、") or body.startswith("正直，"):
            post_type = "正直"
        elif "欲しい人いますか" in body or "配布" in body:
            post_type = "配布"
        
        # キーワード抽出
        keywords = set()
        keyword_patterns = [
            r"Claude\s*Code", r"Cursor", r"Anthropic", r"OpenAI",
            r"Vercel", r"GitHub\s*Copilot", r"Gemini", r"GPT[-\d]*",
            r"AWS", r"MCP", r"vibe\s*cod", r"バイブコーディング",
            r"PLG", r"GTM", r"SaaS", r"SEO",
            r"Notion", r"Midjourney", r"Jasper", r"Slack",
            r"Windsurf", r"Devin", r"OpenClaw",
            r"AI\s*エージェント", r"スレッド", r"アルゴリズム",
        ]
        for kp in keyword_patterns:
            if re.search(kp, body, re.IGNORECASE):
                keywords.add(re.sub(r"\\s\*", " ", kp).replace("\\", ""))
        
        posts.append({
            "file": filepath.name,
            "num": int(num),
            "type": post_type,
            "body": body,
            "keywords": keywords,
            "char_count": len(body.replace("\n", "").replace(" ", "")),
        })
    
    return posts


def get_recent_post_files(account: str, days: int = 7) -> list[Path]:
    """直近N日分の投稿ファイルを取得"""
    files = []
    today = datetime.now()
    for i in range(days):
        date = today - timedelta(days=i)
        filename = f"x-posts-{date.strftime('%Y-%m-%d')}-{account}.md"
        filepath = PROJECTS_DIR / filename
        if filepath.exists():
            files.append(filepath)
    return files


def check_diversity(account: str, days: int = 7) -> dict:
    """投稿の多様性をチェック"""
    files = get_recent_post_files(account, days)
    if not files:
        return {"error": f"直近{days}日分の投稿ファイルが見つかりません"}
    
    all_posts = []
    for f in files:
        all_posts.extend(extract_posts_from_file(f))
    
    # 型の分布
    type_counts = Counter(p["type"] for p in all_posts)
    
    # キーワードの頻度
    keyword_counts = Counter()
    for p in all_posts:
        keyword_counts.update(p["keywords"])
    
    # 文字数の分布
    char_counts = [p["char_count"] for p in all_posts]
    avg_chars = sum(char_counts) / len(char_counts) if char_counts else 0
    
    # 日別投稿数
    daily_counts = Counter(p["file"] for p in all_posts)
    
    # 重複テーマ検出（同じキーワードが3つ以上一致する投稿ペア）
    duplicates = []
    for i, p1 in enumerate(all_posts):
        for j, p2 in enumerate(all_posts):
            if i >= j:
                continue
            overlap = p1["keywords"] & p2["keywords"]
            if len(overlap) >= 3:
                duplicates.append({
                    "post1": f"{p1['file']}#{p1['num']}",
                    "post2": f"{p2['file']}#{p2['num']}",
                    "overlap": list(overlap),
                })
    
    # 表現の使い回し検出
    phrase_counts = Counter()
    common_phrases = [
        "これ、何を意味するか",
        "これが超重要",
        "何ができるか",
        "何がすごいか",
        "対策",
        "結果",
        "教訓",
        "ポイントは",
        "つまり",
    ]
    for p in all_posts:
        for phrase in common_phrases:
            if phrase in p["body"]:
                phrase_counts[phrase] += 1
    
    return {
        "total_posts": len(all_posts),
        "files_analyzed": len(files),
        "type_distribution": dict(type_counts),
        "top_keywords": keyword_counts.most_common(15),
        "avg_char_count": round(avg_chars),
        "char_range": (min(char_counts), max(char_counts)) if char_counts else (0, 0),
        "daily_counts": dict(daily_counts),
        "potential_duplicates": duplicates[:10],
        "phrase_usage": dict(phrase_counts),
        "recommendations": generate_recommendations(type_counts, keyword_counts, phrase_counts, duplicates),
    }


def generate_recommendations(type_counts, keyword_counts, phrase_counts, duplicates):
    """改善提案を生成"""
    recs = []
    
    # 型の偏りチェック
    total = sum(type_counts.values())
    for typ, count in type_counts.items():
        ratio = count / total if total > 0 else 0
        if ratio > 0.4:
            recs.append(f"⚠️ 「{typ}」型が{ratio:.0%}と偏りすぎ。他の型も使おう。")
    
    # キーワードの偏り
    if keyword_counts:
        top_kw = keyword_counts.most_common(1)[0]
        if top_kw[1] > total * 0.5:
            recs.append(f"⚠️ 「{top_kw[0]}」が出現しすぎ（{top_kw[1]}回）。テーマを分散させよう。")
    
    # 表現の使い回し
    for phrase, count in phrase_counts.items():
        if count > total * 0.5:
            recs.append(f"⚠️ 「{phrase}」が{count}回使われてる。別の表現も使おう。")
    
    # 重複
    if duplicates:
        recs.append(f"⚠️ テーマが重複している投稿ペアが{len(duplicates)}件。差別化を意識しよう。")
    
    if not recs:
        recs.append("✅ 投稿の多様性は良好です！")
    
    return recs


def print_report(result: dict):
    """レポートを表示"""
    print("=" * 60)
    print("📊 X投稿 多様性チェックレポート")
    print("=" * 60)
    
    if "error" in result:
        print(f"\n❌ {result['error']}")
        return
    
    print(f"\n📝 分析対象: {result['files_analyzed']}ファイル / {result['total_posts']}投稿")
    print(f"📏 平均文字数: {result['avg_char_count']}文字 (範囲: {result['char_range'][0]}-{result['char_range'][1]})")
    
    print(f"\n🏷️ 型の分布:")
    for typ, count in sorted(result["type_distribution"].items(), key=lambda x: -x[1]):
        bar = "█" * count
        print(f"  {typ:12s} {bar} ({count})")
    
    print(f"\n🔑 頻出キーワード TOP10:")
    for kw, count in result["top_keywords"][:10]:
        print(f"  {kw}: {count}回")
    
    print(f"\n📢 よく使う表現:")
    for phrase, count in sorted(result["phrase_usage"].items(), key=lambda x: -x[1]):
        print(f"  「{phrase}」: {count}回")
    
    if result["potential_duplicates"]:
        print(f"\n⚠️ テーマ重複の可能性あり ({len(result['potential_duplicates'])}件):")
        for dup in result["potential_duplicates"][:5]:
            print(f"  {dup['post1']} ↔ {dup['post2']}")
            print(f"    共通キーワード: {', '.join(dup['overlap'])}")
    
    print(f"\n💡 改善提案:")
    for rec in result["recommendations"]:
        print(f"  {rec}")
    
    print("=" * 60)


def main():
    account = sys.argv[1] if len(sys.argv) > 1 else "aircle"
    days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
    
    result = check_diversity(account, days)
    print_report(result)
    
    # JSON保存
    output_file = PROJECTS_DIR / f"diversity-check-{account}-{datetime.now().strftime('%Y-%m-%d')}.json"
    
    # JSONシリアライズ用に変換
    json_result = result.copy()
    if "char_range" in json_result:
        json_result["char_range"] = list(json_result["char_range"])
    if "potential_duplicates" in json_result:
        for dup in json_result["potential_duplicates"]:
            if isinstance(dup.get("overlap"), set):
                dup["overlap"] = list(dup["overlap"])
    
    output_file.write_text(json.dumps(json_result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n✅ レポート保存: {output_file}")


if __name__ == "__main__":
    main()
