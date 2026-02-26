#!/usr/bin/env python3
"""
X投稿パイプラインツール
MDファイルから投稿を読み込み → 品質チェック → HTML生成 → サマリーレポート を一括実行

使い方:
  python3 x_post_pipeline.py projects/x-posts-2026-02-27-aircle.md
  python3 x_post_pipeline.py projects/x-posts-2026-02-27-aircle.md projects/x-posts-2026-02-27-ichiaimarketer.md
  python3 x_post_pipeline.py --all  # projects/x-posts-*.md を全て処理
"""

import re
import sys
import os
import json
from pathlib import Path
from datetime import datetime
import html


# ====== 品質スコアリング ======

HOOK_PATTERNS = {
    "速報型": r"【速報】",
    "海外バズ型": r"【海外で(大バズ|話題)】",
    "結論型": r"【結論から言います】",
    "公式型": r"【公式が答えを出してしまった】",
    "正直型": r"^正直、",
    "配布型": r"欲しい人いますか",
}

BAD_EMOJI = ["📱", "📅", "🔗", "📰", "🚨", "📊", "💻", "🤖"]
GOOD_EMOJI = ["🔥", "👇", "😳"]


def score_post(body: str) -> dict:
    """投稿の品質スコアを計算"""
    score = 50  # ベーススコア
    feedback = []
    
    char_count = len(body.replace("\n", "").replace(" ", ""))
    
    # 文字数チェック (200-400が最適)
    if 200 <= char_count <= 400:
        score += 15
        feedback.append("✅ 文字数が最適範囲 (200-400)")
    elif 150 <= char_count < 200:
        score += 5
        feedback.append("⚠️ やや短い")
    elif 400 < char_count <= 500:
        score += 5
        feedback.append("⚠️ やや長い")
    elif char_count > 500:
        score -= 5
        feedback.append("❌ 長すぎる (500+)")
    else:
        score -= 10
        feedback.append("❌ 短すぎる (<150)")
    
    # フックパターンチェック
    hook_found = False
    for name, pattern in HOOK_PATTERNS.items():
        if re.search(pattern, body, re.MULTILINE):
            score += 15
            feedback.append(f"✅ {name}フック使用")
            hook_found = True
            break
    if not hook_found:
        feedback.append("⚠️ フックパターンなし")
    
    # 箇条書きチェック
    bullet_count = len(re.findall(r"^[•・→]", body, re.MULTILINE))
    if bullet_count >= 3:
        score += 10
        feedback.append(f"✅ 箇条書き{bullet_count}個")
    elif bullet_count >= 1:
        score += 5
        feedback.append(f"⚠️ 箇条書き少ない ({bullet_count}個)")
    
    # 参考URL
    if re.search(r"参考:\s*https?://", body):
        score += 5
        feedback.append("✅ 参考URL付き")
    
    # NG絵文字チェック
    bad_found = [e for e in BAD_EMOJI if e in body]
    if bad_found:
        score -= 5 * len(bad_found)
        feedback.append(f"❌ NG絵文字: {''.join(bad_found)}")
    
    # 締めの言葉チェック
    closing_patterns = [r"すべき", r"の時代", r"が正解", r"が来る", r"始まった", r"が勝つ", r"が最強"]
    closing_found = False
    for p in closing_patterns:
        if re.search(p, body):
            score += 5
            closing_found = True
            break
    if closing_found:
        feedback.append("✅ 強い締め")
    
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
        "score": min(100, max(0, score)),
        "grade": grade,
        "char_count": char_count,
        "feedback": feedback,
    }


# ====== 投稿抽出 ======

def extract_posts(filepath: str) -> tuple[str, list[dict]]:
    """MDファイルから投稿を抽出"""
    content = Path(filepath).read_text(encoding="utf-8")
    
    title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    page_title = title_match.group(1) if title_match else os.path.basename(filepath)
    
    pattern = r"## 投稿(\d+)[:：]\s*(.+?)(?=\n## 投稿|\n## ■|\Z)"
    matches = re.findall(pattern, content, re.DOTALL)
    
    posts = []
    for num, body in matches:
        lines = body.strip().split("\n")
        title = lines[0].strip() if lines else ""
        full_text = "\n".join(lines).strip()
        
        if full_text.endswith("---"):
            full_text = full_text[:-3].strip()
        
        ref_match = re.search(r"参考:\s*(https?://\S+)", full_text)
        ref_url = ref_match.group(1) if ref_match else None
        post_body = re.sub(r"\n参考:\s*https?://\S+", "", full_text).strip()
        
        quality = score_post(post_body)
        
        posts.append({
            "num": int(num),
            "title": title,
            "body": post_body,
            "ref_url": ref_url,
            **quality,
        })
    
    return page_title, posts


# ====== HTML生成 ======

def generate_html(page_title: str, posts: list[dict]) -> str:
    """ダークUIのHTMLを生成"""
    
    grade_colors = {
        "S": "#ffd700",
        "A": "#00e676",
        "B": "#42a5f5",
        "C": "#ff9800",
        "D": "#f44336",
    }
    
    post_cards = []
    for p in posts:
        escaped_body = html.escape(p["body"])
        color = grade_colors.get(p["grade"], "#aaa")
        ref_html = f'<a href="{html.escape(p["ref_url"])}" target="_blank" class="ref-link">📎 参考リンク</a>' if p.get("ref_url") else ""
        
        card = f"""
        <div class="post-card" data-grade="{p['grade']}">
            <div class="post-header">
                <span class="post-num">#{p['num']}</span>
                <span class="grade" style="background: {color}">{p['grade']}</span>
                <span class="score">{p['score']}pt</span>
                <span class="char-count">{p['char_count']}文字</span>
            </div>
            <div class="post-title">{html.escape(p['title'])}</div>
            <pre class="post-body" id="post-{p['num']}">{escaped_body}</pre>
            <div class="post-actions">
                <button class="copy-btn" onclick="copyPost({p['num']})">📋 コピー</button>
                {ref_html}
            </div>
        </div>
        """
        post_cards.append(card)
    
    # 統計
    total = len(posts)
    avg_score = sum(p["score"] for p in posts) / total if total else 0
    avg_chars = sum(p["char_count"] for p in posts) / total if total else 0
    grade_dist = {}
    for p in posts:
        grade_dist[p["grade"]] = grade_dist.get(p["grade"], 0) + 1
    
    grade_bars = ""
    for g in ["S", "A", "B", "C", "D"]:
        count = grade_dist.get(g, 0)
        pct = count / total * 100 if total else 0
        color = grade_colors.get(g, "#aaa")
        grade_bars += f'<div class="grade-bar"><span class="grade-label" style="color: {color}">{g}</span><div class="bar" style="width: {pct}%; background: {color}"></div><span class="grade-count">{count}</span></div>'
    
    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html.escape(page_title)}</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ background: #0d1117; color: #e6edf3; font-family: -apple-system, 'Segoe UI', sans-serif; padding: 20px; }}
.container {{ max-width: 800px; margin: 0 auto; }}
h1 {{ font-size: 1.5em; margin-bottom: 20px; color: #fff; }}
.stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 12px; margin-bottom: 24px; }}
.stat-card {{ background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 12px; text-align: center; }}
.stat-value {{ font-size: 1.8em; font-weight: bold; color: #58a6ff; }}
.stat-label {{ font-size: 0.85em; color: #8b949e; margin-top: 4px; }}
.grade-dist {{ background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 16px; margin-bottom: 24px; }}
.grade-bar {{ display: flex; align-items: center; gap: 8px; margin: 4px 0; }}
.grade-label {{ width: 20px; font-weight: bold; }}
.bar {{ height: 20px; border-radius: 4px; min-width: 2px; transition: width 0.5s; }}
.grade-count {{ font-size: 0.85em; color: #8b949e; }}
.filter-bar {{ display: flex; gap: 8px; margin-bottom: 16px; flex-wrap: wrap; }}
.filter-btn {{ background: #21262d; border: 1px solid #30363d; color: #e6edf3; padding: 6px 14px; border-radius: 20px; cursor: pointer; font-size: 0.85em; }}
.filter-btn.active {{ background: #58a6ff; color: #0d1117; border-color: #58a6ff; }}
.post-card {{ background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 16px; margin-bottom: 16px; }}
.post-card.hidden {{ display: none; }}
.post-header {{ display: flex; align-items: center; gap: 8px; margin-bottom: 8px; }}
.post-num {{ font-size: 0.85em; color: #8b949e; }}
.grade {{ color: #0d1117; font-weight: bold; font-size: 0.75em; padding: 2px 8px; border-radius: 4px; }}
.score {{ font-size: 0.85em; color: #8b949e; }}
.char-count {{ font-size: 0.75em; color: #6e7681; }}
.post-title {{ font-weight: bold; margin-bottom: 8px; color: #fff; }}
.post-body {{ white-space: pre-wrap; font-family: inherit; font-size: 0.95em; line-height: 1.6; color: #c9d1d9; background: none; border: none; padding: 0; }}
.post-actions {{ display: flex; gap: 8px; margin-top: 12px; }}
.copy-btn {{ background: #238636; color: #fff; border: none; padding: 6px 16px; border-radius: 6px; cursor: pointer; font-size: 0.85em; }}
.copy-btn:hover {{ background: #2ea043; }}
.copy-btn.copied {{ background: #58a6ff; }}
.ref-link {{ color: #58a6ff; text-decoration: none; font-size: 0.85em; padding: 6px 0; }}
.toast {{ position: fixed; bottom: 20px; right: 20px; background: #238636; color: #fff; padding: 12px 24px; border-radius: 8px; display: none; z-index: 999; }}
</style>
</head>
<body>
<div class="container">
<h1>{html.escape(page_title)}</h1>
<div class="stats">
  <div class="stat-card"><div class="stat-value">{total}</div><div class="stat-label">投稿数</div></div>
  <div class="stat-card"><div class="stat-value">{avg_score:.0f}</div><div class="stat-label">平均スコア</div></div>
  <div class="stat-card"><div class="stat-value">{avg_chars:.0f}</div><div class="stat-label">平均文字数</div></div>
  <div class="stat-card"><div class="stat-value">{grade_dist.get('S', 0) + grade_dist.get('A', 0)}</div><div class="stat-label">S+Aグレード</div></div>
</div>
<div class="grade-dist">{grade_bars}</div>
<div class="filter-bar">
  <button class="filter-btn active" onclick="filterGrade('all')">全て</button>
  <button class="filter-btn" onclick="filterGrade('S')">S</button>
  <button class="filter-btn" onclick="filterGrade('A')">A</button>
  <button class="filter-btn" onclick="filterGrade('B')">B</button>
  <button class="filter-btn" onclick="filterGrade('C')">C</button>
</div>
{''.join(post_cards)}
</div>
<div class="toast" id="toast">コピーしました！</div>
<script>
function copyPost(num) {{
  const el = document.getElementById('post-' + num);
  navigator.clipboard.writeText(el.textContent).then(() => {{
    const toast = document.getElementById('toast');
    toast.style.display = 'block';
    setTimeout(() => toast.style.display = 'none', 1500);
    const btn = el.parentElement.querySelector('.copy-btn');
    btn.textContent = '✅ コピー済';
    btn.classList.add('copied');
    setTimeout(() => {{ btn.textContent = '📋 コピー'; btn.classList.remove('copied'); }}, 2000);
  }});
}}
function filterGrade(grade) {{
  document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
  event.target.classList.add('active');
  document.querySelectorAll('.post-card').forEach(card => {{
    if (grade === 'all' || card.dataset.grade === grade) {{
      card.classList.remove('hidden');
    }} else {{
      card.classList.add('hidden');
    }}
  }});
}}
</script>
</body>
</html>"""


# ====== レポート生成 ======

def generate_report(files_data: list[tuple[str, str, list[dict]]]) -> str:
    """サマリーレポートを生成"""
    lines = ["# X投稿パイプライン レポート", f"生成日時: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ""]
    
    total_posts = 0
    total_score = 0
    all_grades = {}
    
    for filepath, title, posts in files_data:
        lines.append(f"## {title}")
        lines.append(f"- ファイル: `{filepath}`")
        lines.append(f"- 投稿数: {len(posts)}")
        
        avg = sum(p['score'] for p in posts) / len(posts) if posts else 0
        avg_chars = sum(p['char_count'] for p in posts) / len(posts) if posts else 0
        lines.append(f"- 平均スコア: {avg:.1f}")
        lines.append(f"- 平均文字数: {avg_chars:.0f}")
        
        grades = {}
        for p in posts:
            grades[p['grade']] = grades.get(p['grade'], 0) + 1
            all_grades[p['grade']] = all_grades.get(p['grade'], 0) + 1
        
        grade_str = ", ".join(f"{g}={grades.get(g,0)}" for g in ["S","A","B","C","D"] if grades.get(g,0))
        lines.append(f"- グレード分布: {grade_str}")
        
        # トップ3
        sorted_posts = sorted(posts, key=lambda x: x['score'], reverse=True)[:3]
        lines.append("- トップ3:")
        for p in sorted_posts:
            lines.append(f"  - [{p['grade']}] #{p['num']} ({p['score']}pt) {p['title'][:40]}")
        
        lines.append("")
        total_posts += len(posts)
        total_score += sum(p['score'] for p in posts)
    
    # 全体サマリー
    lines.insert(3, f"## 全体サマリー")
    lines.insert(4, f"- 合計投稿数: {total_posts}")
    lines.insert(5, f"- 全体平均スコア: {total_score / total_posts:.1f}" if total_posts else "- 全体平均スコア: N/A")
    grade_str = ", ".join(f"{g}={all_grades.get(g,0)}" for g in ["S","A","B","C","D"] if all_grades.get(g,0))
    lines.insert(6, f"- 全体グレード分布: {grade_str}")
    lines.insert(7, "")
    
    return "\n".join(lines)


# ====== メイン ======

def main():
    if len(sys.argv) < 2:
        print("使い方: python3 x_post_pipeline.py <MDファイル...> [--all]")
        sys.exit(1)
    
    workspace = Path(__file__).parent.parent
    
    if "--all" in sys.argv:
        md_files = sorted(workspace.glob("projects/x-posts-*.md"))
    else:
        md_files = [Path(f) for f in sys.argv[1:] if f.endswith(".md")]
    
    if not md_files:
        print("対象ファイルが見つかりません")
        sys.exit(1)
    
    files_data = []
    
    for md_file in md_files:
        print(f"\n📄 処理中: {md_file.name}")
        
        try:
            page_title, posts = extract_posts(str(md_file))
        except Exception as e:
            print(f"  ❌ 読み込みエラー: {e}")
            continue
        
        if not posts:
            print(f"  ⚠️ 投稿が見つかりません")
            continue
        
        print(f"  ✅ {len(posts)}投稿を抽出")
        
        # 品質サマリー
        avg_score = sum(p['score'] for p in posts) / len(posts)
        grades = {}
        for p in posts:
            grades[p['grade']] = grades.get(p['grade'], 0) + 1
        grade_str = " ".join(f"{g}:{grades.get(g,0)}" for g in ["S","A","B","C","D"] if grades.get(g,0))
        print(f"  📊 平均スコア: {avg_score:.1f} | {grade_str}")
        
        # HTML生成
        html_content = generate_html(page_title, posts)
        html_path = md_file.with_suffix(".html")
        html_path.write_text(html_content, encoding="utf-8")
        print(f"  🌐 HTML生成: {html_path.name}")
        
        files_data.append((str(md_file), page_title, posts))
    
    # レポート生成
    if files_data:
        report = generate_report(files_data)
        report_path = workspace / "projects" / f"x-pipeline-report-{datetime.now().strftime('%Y-%m-%d')}.md"
        report_path.write_text(report, encoding="utf-8")
        print(f"\n📋 レポート: {report_path.name}")
    
    print("\n✅ パイプライン完了！")


if __name__ == "__main__":
    main()
