#!/usr/bin/env python3
"""
X投稿ダッシュボード生成ツール
全投稿ファイルを読み込み、品質スコア・統計情報を
一覧表示するHTMLダッシュボードを生成する
"""

import re
import os
import glob
from pathlib import Path
from datetime import datetime
import html
import json

WORKSPACE = "/Users/ai-driven-work/Documents/OpenClaw-Workspace"
PROJECTS_DIR = os.path.join(WORKSPACE, "projects")

# バズる型パターン
HOOK_PATTERNS = {
    "速報型": r"【速報】",
    "海外バズ型": r"【海外で(大バズ|話題)】",
    "結論型": r"【結論から言います】",
    "公式型": r"【公式が答えを出してしまった】",
    "正直型": r"^正直、",
    "配布型": r"欲しい人いますか",
}

# 禁止絵文字
BANNED_EMOJI = ["📱", "📅", "🔗", "📰", "🚨"]

# 許可絵文字
ALLOWED_EMOJI = ["🔥", "👇", "😳"]


def extract_posts_from_file(filepath: str) -> list[dict]:
    """投稿ファイルからポストを抽出"""
    content = Path(filepath).read_text(encoding="utf-8")
    posts = []
    
    pattern = r"## 投稿(\d+)[:：]\s*(.+?)(?=\n## 投稿|\n## ■|\n---\n\*生成日|\Z)"
    matches = re.findall(pattern, content, re.DOTALL)
    
    for num, body in matches:
        lines = body.strip().split("\n")
        title = lines[0].strip() if lines else ""
        full_text = "\n".join(lines).strip()
        
        if full_text.endswith("---"):
            full_text = full_text[:-3].strip()
        
        ref_match = re.search(r"参考:\s*(https?://\S+)", full_text)
        ref_url = ref_match.group(1) if ref_match else None
        post_body = re.sub(r"\n参考:\s*https?://\S+", "", full_text).strip()
        
        posts.append({
            "num": int(num),
            "title": title,
            "body": post_body,
            "ref_url": ref_url,
            "char_count": len(post_body.replace("\n", "").replace(" ", "")),
            "file": os.path.basename(filepath),
        })
    
    return posts


def score_post(post: dict) -> dict:
    """投稿のクオリティスコアを計算"""
    score = 0
    details = []
    body = post["body"]
    
    # 1. フックパターン (0-20点)
    hook_found = False
    for name, pattern in HOOK_PATTERNS.items():
        if re.search(pattern, body, re.MULTILINE):
            score += 20
            details.append(f"✅ フック: {name}")
            hook_found = True
            break
    if not hook_found:
        details.append("⚠️ フックパターンなし")
    
    # 2. 構造 - 箇条書き (0-15点)
    bullet_count = body.count("•") + body.count("→")
    if bullet_count >= 5:
        score += 15
        details.append(f"✅ 箇条書き: {bullet_count}個")
    elif bullet_count >= 3:
        score += 10
        details.append(f"⚠️ 箇条書き: {bullet_count}個（5個以上推奨）")
    else:
        details.append(f"❌ 箇条書き不足: {bullet_count}個")
    
    # 3. 具体的数字 (0-15点)
    numbers = re.findall(r"\d+[%％万億兆B$Kk]|\$[\d,.]+[BMK]?", body)
    if len(numbers) >= 3:
        score += 15
        details.append(f"✅ 具体的数字: {len(numbers)}個")
    elif len(numbers) >= 1:
        score += 8
        details.append(f"⚠️ 具体的数字: {len(numbers)}個（3個以上推奨）")
    else:
        details.append("❌ 具体的数字なし")
    
    # 4. 文字数 (0-15点)
    char_count = post["char_count"]
    if 200 <= char_count <= 400:
        score += 15
        details.append(f"✅ 文字数: {char_count}（適正範囲）")
    elif 150 <= char_count <= 500:
        score += 10
        details.append(f"⚠️ 文字数: {char_count}（200-400推奨）")
    else:
        score += 5
        details.append(f"❌ 文字数: {char_count}（範囲外）")
    
    # 5. 参考URL (0-10点)
    if post["ref_url"]:
        score += 10
        details.append("✅ 参考URL付き")
    else:
        details.append("⚠️ 参考URLなし")
    
    # 6. CTA・締め (0-10点)
    cta_patterns = [r"すべき", r"の時代", r"始めよう", r"やるべき", r"しろ", r"せよ", r"今すぐ"]
    cta_found = any(re.search(p, body) for p in cta_patterns)
    if cta_found:
        score += 10
        details.append("✅ CTA/締めあり")
    else:
        details.append("⚠️ CTA/締めが弱い")
    
    # 7. 禁止絵文字チェック (0 or -5点)
    banned_found = [e for e in BANNED_EMOJI if e in body]
    if banned_found:
        score -= 5
        details.append(f"❌ 禁止絵文字: {''.join(banned_found)}")
    
    # 8. 対比構造 (0-10点)
    contrast_patterns = [r"❌.*✅", r"今まで.*これから", r"従来.*現在", r"以前.*今"]
    if any(re.search(p, body, re.DOTALL) for p in contrast_patterns):
        score += 10
        details.append("✅ 対比構造あり")
    
    # 9. 👇の活用 (0-5点)
    if "👇" in body:
        score += 5
        details.append("✅ 👇で誘導あり")
    
    # グレード判定
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
        "score": min(score, 100),
        "grade": grade,
        "details": details,
    }


def find_post_files() -> list[str]:
    """x-posts-*.md ファイルを日付降順で取得"""
    pattern = os.path.join(PROJECTS_DIR, "x-posts-*.md")
    files = glob.glob(pattern)
    files.sort(reverse=True)
    return files


def generate_dashboard(all_data: list[dict]) -> str:
    """HTMLダッシュボードを生成"""
    
    # 統計計算
    total_posts = sum(len(d["posts"]) for d in all_data)
    all_scores = [p["score_data"]["score"] for d in all_data for p in d["posts"]]
    avg_score = sum(all_scores) / len(all_scores) if all_scores else 0
    grade_counts = {}
    for d in all_data:
        for p in d["posts"]:
            g = p["score_data"]["grade"]
            grade_counts[g] = grade_counts.get(g, 0) + 1
    
    # フックパターン使用率
    hook_usage = {}
    for d in all_data:
        for p in d["posts"]:
            for name, pattern in HOOK_PATTERNS.items():
                if re.search(pattern, p["body"], re.MULTILINE):
                    hook_usage[name] = hook_usage.get(name, 0) + 1
    
    # 日別スコア推移
    date_scores = {}
    for d in all_data:
        date = d["date"]
        scores = [p["score_data"]["score"] for p in d["posts"]]
        if scores:
            date_scores[date] = {
                "avg": sum(scores) / len(scores),
                "count": len(scores),
                "account": d["account"],
            }
    
    # ファイルごとのカード生成
    file_cards = []
    for d in all_data:
        scores = [p["score_data"]["score"] for p in d["posts"]]
        avg = sum(scores) / len(scores) if scores else 0
        grades = [p["score_data"]["grade"] for p in d["posts"]]
        s_count = grades.count("S")
        a_count = grades.count("A")
        
        grade_badge_color = "#238636" if avg >= 80 else "#d29922" if avg >= 60 else "#da3633"
        
        post_rows = []
        for p in d["posts"]:
            sd = p["score_data"]
            grade_color = {
                "S": "#238636", "A": "#2ea043", "B": "#d29922", "C": "#da3633", "D": "#f85149"
            }.get(sd["grade"], "#8b949e")
            
            post_rows.append(f'''
            <tr>
                <td>#{p["num"]}</td>
                <td class="post-title">{html.escape(p["title"][:50])}</td>
                <td>{p["char_count"]}</td>
                <td><span class="grade-badge" style="background:{grade_color}">{sd["grade"]}</span></td>
                <td><span class="score">{sd["score"]}</span></td>
            </tr>''')
        
        file_cards.append(f'''
        <div class="file-card">
            <div class="file-header">
                <div>
                    <h3>{html.escape(d["file"])}</h3>
                    <span class="file-meta">{d["date"]} | {d["account"]} | {len(d["posts"])}投稿</span>
                </div>
                <div class="file-score">
                    <span class="avg-score" style="color:{grade_badge_color}">{avg:.1f}</span>
                    <span class="score-label">平均</span>
                </div>
            </div>
            <div class="grade-summary">
                <span class="grade-pill s">S: {s_count}</span>
                <span class="grade-pill a">A: {a_count}</span>
                <span class="grade-pill b">B: {len(grades) - s_count - a_count}</span>
            </div>
            <table class="posts-table">
                <thead>
                    <tr><th>#</th><th>タイトル</th><th>文字</th><th>Grade</th><th>Score</th></tr>
                </thead>
                <tbody>{"".join(post_rows)}</tbody>
            </table>
        </div>''')
    
    # フックパターンチャート
    hook_items = sorted(hook_usage.items(), key=lambda x: x[1], reverse=True)
    max_hook = max(hook_usage.values()) if hook_usage else 1
    hook_bars = []
    for name, count in hook_items:
        width = (count / max_hook) * 100
        hook_bars.append(f'''
        <div class="bar-item">
            <span class="bar-label">{name}</span>
            <div class="bar-track">
                <div class="bar-fill" style="width:{width}%"></div>
            </div>
            <span class="bar-value">{count}</span>
        </div>''')
    
    return f'''<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>X投稿ダッシュボード</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0d1117;
            color: #c9d1d9;
            padding: 20px;
            max-width: 1200px;
            margin: 0 auto;
        }}
        h1 {{
            color: #58a6ff;
            font-size: 1.8rem;
            text-align: center;
            margin-bottom: 8px;
        }}
        .subtitle {{
            text-align: center;
            color: #8b949e;
            margin-bottom: 32px;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 16px;
            margin-bottom: 32px;
        }}
        .stat-card {{
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 12px;
            padding: 20px;
            text-align: center;
        }}
        .stat-value {{
            font-size: 2rem;
            font-weight: bold;
            color: #58a6ff;
        }}
        .stat-label {{
            color: #8b949e;
            font-size: 0.85rem;
            margin-top: 4px;
        }}
        .section-title {{
            color: #f0f6fc;
            font-size: 1.2rem;
            margin-bottom: 16px;
            padding-bottom: 8px;
            border-bottom: 1px solid #30363d;
        }}
        .two-col {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 24px;
            margin-bottom: 32px;
        }}
        .panel {{
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 12px;
            padding: 20px;
        }}
        .bar-item {{
            display: flex;
            align-items: center;
            margin-bottom: 12px;
        }}
        .bar-label {{
            width: 100px;
            font-size: 0.85rem;
            color: #c9d1d9;
        }}
        .bar-track {{
            flex: 1;
            height: 20px;
            background: #21262d;
            border-radius: 10px;
            overflow: hidden;
            margin: 0 12px;
        }}
        .bar-fill {{
            height: 100%;
            background: linear-gradient(90deg, #238636, #2ea043);
            border-radius: 10px;
            transition: width 0.5s;
        }}
        .bar-value {{
            width: 30px;
            text-align: right;
            font-size: 0.85rem;
            color: #58a6ff;
        }}
        .grade-dist {{
            display: flex;
            gap: 12px;
            justify-content: center;
            flex-wrap: wrap;
        }}
        .grade-item {{
            text-align: center;
        }}
        .grade-circle {{
            width: 50px;
            height: 50px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.2rem;
            font-weight: bold;
            margin: 0 auto 4px;
        }}
        .grade-circle.s {{ background: #238636; color: white; }}
        .grade-circle.a {{ background: #2ea043; color: white; }}
        .grade-circle.b {{ background: #d29922; color: white; }}
        .grade-circle.c {{ background: #da3633; color: white; }}
        .grade-circle.d {{ background: #f85149; color: white; }}
        .grade-count {{ font-size: 0.8rem; color: #8b949e; }}
        .file-card {{
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
        }}
        .file-header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 12px;
        }}
        .file-header h3 {{
            color: #f0f6fc;
            font-size: 1rem;
        }}
        .file-meta {{
            color: #8b949e;
            font-size: 0.8rem;
        }}
        .file-score {{
            text-align: right;
        }}
        .avg-score {{
            font-size: 1.5rem;
            font-weight: bold;
        }}
        .score-label {{
            display: block;
            color: #8b949e;
            font-size: 0.75rem;
        }}
        .grade-summary {{
            display: flex;
            gap: 8px;
            margin-bottom: 12px;
        }}
        .grade-pill {{
            padding: 2px 10px;
            border-radius: 12px;
            font-size: 0.8rem;
            font-weight: bold;
        }}
        .grade-pill.s {{ background: #238636; color: white; }}
        .grade-pill.a {{ background: #2ea043; color: white; }}
        .grade-pill.b {{ background: #d29922; color: white; }}
        .posts-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.85rem;
        }}
        .posts-table th {{
            text-align: left;
            color: #8b949e;
            padding: 8px 4px;
            border-bottom: 1px solid #30363d;
            font-weight: normal;
        }}
        .posts-table td {{
            padding: 8px 4px;
            border-bottom: 1px solid #21262d;
        }}
        .post-title {{
            max-width: 300px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }}
        .grade-badge {{
            display: inline-block;
            padding: 1px 8px;
            border-radius: 4px;
            font-weight: bold;
            font-size: 0.8rem;
            color: white;
        }}
        .score {{
            color: #58a6ff;
            font-weight: bold;
        }}
        @media (max-width: 768px) {{
            .two-col {{ grid-template-columns: 1fr; }}
            .stats-grid {{ grid-template-columns: repeat(2, 1fr); }}
        }}
    </style>
</head>
<body>
    <h1>📊 X投稿ダッシュボード</h1>
    <p class="subtitle">生成日: {datetime.now().strftime("%Y-%m-%d %H:%M")} JST</p>
    
    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-value">{total_posts}</div>
            <div class="stat-label">総投稿数</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{avg_score:.1f}</div>
            <div class="stat-label">平均スコア</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{grade_counts.get("S", 0)}</div>
            <div class="stat-label">Sグレード</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{len(all_data)}</div>
            <div class="stat-label">ファイル数</div>
        </div>
    </div>
    
    <div class="two-col">
        <div class="panel">
            <h3 class="section-title">📈 フックパターン使用頻度</h3>
            {"".join(hook_bars) if hook_bars else "<p style='color:#8b949e'>データなし</p>"}
        </div>
        <div class="panel">
            <h3 class="section-title">🏆 グレード分布</h3>
            <div class="grade-dist">
                {"".join(f'<div class="grade-item"><div class="grade-circle {g.lower()}">{g}</div><div class="grade-count">{grade_counts.get(g, 0)}件</div></div>' for g in ["S", "A", "B", "C", "D"])}
            </div>
        </div>
    </div>
    
    <h2 class="section-title">📁 ファイル別詳細</h2>
    {"".join(file_cards)}
</body>
</html>'''


def main():
    files = find_post_files()
    if not files:
        print("❌ x-posts-*.md ファイルが見つかりません")
        return
    
    print(f"📊 {len(files)}ファイルを分析中...")
    
    all_data = []
    for f in files:
        posts = extract_posts_from_file(f)
        if not posts:
            continue
        
        # スコア計算
        for p in posts:
            p["score_data"] = score_post(p)
        
        # 日付・アカウント抽出
        basename = os.path.basename(f)
        date_match = re.search(r"(\d{4}-\d{2}-\d{2})", basename)
        date = date_match.group(1) if date_match else "unknown"
        
        if "aircle" in basename.lower():
            account = "@aircle_ai"
        elif "ichiaimarketer" in basename.lower():
            account = "@ichiaimarketer"
        else:
            account = "不明"
        
        all_data.append({
            "file": basename,
            "date": date,
            "account": account,
            "posts": posts,
        })
    
    # HTML生成
    dashboard_html = generate_dashboard(all_data)
    output_path = os.path.join(PROJECTS_DIR, "x-post-dashboard.html")
    Path(output_path).write_text(dashboard_html, encoding="utf-8")
    
    # サマリー表示
    total = sum(len(d["posts"]) for d in all_data)
    all_scores = [p["score_data"]["score"] for d in all_data for p in d["posts"]]
    avg = sum(all_scores) / len(all_scores) if all_scores else 0
    
    print(f"\n✅ ダッシュボード生成完了: {output_path}")
    print(f"   ファイル数: {len(all_data)}")
    print(f"   総投稿数: {total}")
    print(f"   平均スコア: {avg:.1f}")
    
    # グレード分布
    grades = [p["score_data"]["grade"] for d in all_data for p in d["posts"]]
    for g in ["S", "A", "B", "C", "D"]:
        count = grades.count(g)
        if count > 0:
            print(f"   {g}グレード: {count}件 ({count/len(grades)*100:.0f}%)")


if __name__ == "__main__":
    main()
