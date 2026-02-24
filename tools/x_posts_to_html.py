#!/usr/bin/env python3
"""
X投稿 → HTML変換ツール
投稿Markdownファイルを読み込んで、コピーボタン付きのダークUIなHTMLページを生成する
"""

import re
import sys
import os
from pathlib import Path
from datetime import datetime
import html


def extract_posts(filepath: str) -> list[dict]:
    """投稿ファイルからポストを抽出"""
    content = Path(filepath).read_text(encoding="utf-8")
    posts = []
    
    # タイトル行を抽出
    title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    page_title = title_match.group(1) if title_match else os.path.basename(filepath)
    
    # ## 投稿N: で分割
    pattern = r"## 投稿(\d+)[:：]\s*(.+?)(?=\n## 投稿|\n## ■|\Z)"
    matches = re.findall(pattern, content, re.DOTALL)
    
    for num, body in matches:
        lines = body.strip().split("\n")
        title = lines[0].strip() if lines else ""
        full_text = "\n".join(lines).strip()
        
        # ---で終わる場合は除去
        if full_text.endswith("---"):
            full_text = full_text[:-3].strip()
        
        # 参考URLを抽出
        ref_match = re.search(r"参考:\s*(https?://\S+)", full_text)
        ref_url = ref_match.group(1) if ref_match else None
        
        # 投稿本文（参考URL行を除去）
        post_body = re.sub(r"\n参考:\s*https?://\S+", "", full_text).strip()
        
        posts.append({
            "num": int(num),
            "title": title,
            "body": post_body,
            "ref_url": ref_url,
            "char_count": len(post_body.replace("\n", "").replace(" ", "")),
        })
    
    return posts, page_title


def generate_html(posts: list[dict], page_title: str, account_label: str = "") -> str:
    """HTMLページを生成"""
    
    posts_html = []
    for post in posts:
        escaped_body = html.escape(post["body"])
        # 箇条書きのフォーマットをHTMLに
        formatted_body = escaped_body.replace("\n", "<br>")
        # •の行をインデント付きに
        formatted_body = re.sub(r"•\s*", '<span class="bullet">•</span> ', formatted_body)
        
        ref_link = ""
        if post["ref_url"]:
            ref_link = f'<a href="{html.escape(post["ref_url"])}" target="_blank" rel="noopener" class="ref-link">📎 参考ソース</a>'
        
        # コピー用テキスト（改行をそのまま保持）
        copy_text = html.escape(post["body"]).replace("\n", "\\n").replace("'", "\\'")
        
        posts_html.append(f'''
        <div class="post-card" id="post-{post["num"]}">
            <div class="post-header">
                <span class="post-number">#{post["num"]}</span>
                <span class="char-count">{post["char_count"]}文字</span>
            </div>
            <div class="post-body">{formatted_body}</div>
            <div class="post-footer">
                {ref_link}
                <button class="copy-btn" onclick="copyPost('{copy_text}', this)">
                    📋 コピー
                </button>
            </div>
        </div>
        ''')
    
    all_posts = "\n".join(posts_html)
    date_str = datetime.now().strftime("%Y-%m-%d")
    
    return f'''<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html.escape(page_title)}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0d1117;
            color: #c9d1d9;
            padding: 20px;
            max-width: 800px;
            margin: 0 auto;
        }}
        h1 {{
            color: #58a6ff;
            font-size: 1.5rem;
            margin-bottom: 8px;
            text-align: center;
        }}
        .meta {{
            text-align: center;
            color: #8b949e;
            font-size: 0.85rem;
            margin-bottom: 24px;
        }}
        .summary {{
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 24px;
            text-align: center;
        }}
        .summary-stat {{
            display: inline-block;
            margin: 0 16px;
            font-size: 0.9rem;
        }}
        .summary-stat strong {{
            color: #58a6ff;
            font-size: 1.2rem;
        }}
        .post-card {{
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 16px;
            transition: border-color 0.2s;
        }}
        .post-card:hover {{
            border-color: #58a6ff;
        }}
        .post-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
        }}
        .post-number {{
            color: #58a6ff;
            font-weight: bold;
            font-size: 0.9rem;
        }}
        .char-count {{
            color: #8b949e;
            font-size: 0.8rem;
        }}
        .post-body {{
            line-height: 1.7;
            font-size: 0.95rem;
            white-space: pre-wrap;
            word-wrap: break-word;
        }}
        .bullet {{
            color: #58a6ff;
            margin-left: 8px;
        }}
        .post-footer {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: 16px;
            padding-top: 12px;
            border-top: 1px solid #30363d;
        }}
        .ref-link {{
            color: #8b949e;
            text-decoration: none;
            font-size: 0.8rem;
        }}
        .ref-link:hover {{
            color: #58a6ff;
        }}
        .copy-btn {{
            background: #21262d;
            color: #c9d1d9;
            border: 1px solid #30363d;
            border-radius: 6px;
            padding: 6px 12px;
            cursor: pointer;
            font-size: 0.85rem;
            transition: all 0.2s;
        }}
        .copy-btn:hover {{
            background: #30363d;
            border-color: #58a6ff;
        }}
        .copy-btn.copied {{
            background: #238636;
            border-color: #2ea043;
            color: white;
        }}
        .copy-all-btn {{
            display: block;
            width: 100%;
            background: #238636;
            color: white;
            border: none;
            border-radius: 8px;
            padding: 12px;
            font-size: 1rem;
            cursor: pointer;
            margin-bottom: 24px;
            transition: background 0.2s;
        }}
        .copy-all-btn:hover {{
            background: #2ea043;
        }}
        @media (max-width: 600px) {{
            body {{ padding: 12px; }}
            .post-card {{ padding: 14px; }}
            .summary-stat {{ display: block; margin: 4px 0; }}
        }}
    </style>
</head>
<body>
    <h1>{html.escape(page_title)}</h1>
    <div class="meta">{date_str} | {len(posts)}投稿 {account_label}</div>
    
    <div class="summary">
        <div class="summary-stat">投稿数: <strong>{len(posts)}</strong></div>
        <div class="summary-stat">平均文字数: <strong>{sum(p["char_count"] for p in posts) // len(posts) if posts else 0}</strong></div>
    </div>
    
    {all_posts}
    
    <script>
        function copyPost(text, btn) {{
            const decoded = text.replace(/\\\\n/g, '\\n');
            navigator.clipboard.writeText(decoded).then(() => {{
                btn.textContent = '✅ コピー済み';
                btn.classList.add('copied');
                setTimeout(() => {{
                    btn.textContent = '📋 コピー';
                    btn.classList.remove('copied');
                }}, 2000);
            }});
        }}
    </script>
</body>
</html>'''


def main():
    workspace = "/Users/ai-driven-work/Documents/OpenClaw-Workspace"
    
    if len(sys.argv) < 2:
        print("Usage: python3 x_posts_to_html.py <markdown_file> [output_dir]")
        print("Example: python3 x_posts_to_html.py projects/x-posts-2026-02-23-aircle.md")
        sys.exit(1)
    
    filepath = sys.argv[1]
    if not os.path.isabs(filepath):
        filepath = os.path.join(workspace, filepath)
    
    output_dir = sys.argv[2] if len(sys.argv) > 2 else os.path.dirname(filepath)
    
    posts, page_title = extract_posts(filepath)
    if not posts:
        print(f"❌ {filepath} から投稿を抽出できませんでした")
        sys.exit(1)
    
    # アカウントラベル推定
    basename = os.path.basename(filepath).lower()
    if "aircle" in basename:
        account_label = "| @aircle_ai"
    elif "ichiaimarketer" in basename:
        account_label = "| @ichiaimarketer"
    else:
        account_label = ""
    
    html_content = generate_html(posts, page_title, account_label)
    
    # ファイル名を生成
    base = os.path.splitext(os.path.basename(filepath))[0]
    output_path = os.path.join(output_dir, f"{base}.html")
    
    Path(output_path).write_text(html_content, encoding="utf-8")
    print(f"✅ HTMLファイル生成: {output_path}")
    print(f"   投稿数: {len(posts)}件")
    print(f"   平均文字数: {sum(p['char_count'] for p in posts) // len(posts) if posts else 0}文字")


if __name__ == "__main__":
    main()
