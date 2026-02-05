#!/usr/bin/env python3
"""
X投稿 Markdown → HTML 変換ツール

Usage:
    python md_to_html.py projects/x-posts-2026-02-06-aircle.md

機能:
- Markdownファイルを読み込み
- 投稿を抽出してHTML生成
- Vercelにデプロイ可能な形式で出力
"""

import re
import sys
import os
from pathlib import Path
from datetime import datetime

def parse_md_posts(content: str) -> list[dict]:
    """Markdownから投稿を抽出"""
    posts = []
    
    # ### 投稿N: タイトル のパターンでマッチ
    pattern = r'### 投稿(\d+)[:：]([^\n]*)\n(.*?)(?=### 投稿|\Z|## カテゴリ)'
    matches = re.findall(pattern, content, re.DOTALL)
    
    for num, title, body in matches:
        # 本文からURLを抽出（ソースとして使用）
        url_match = re.search(r'https?://[^\s\)]+', body)
        source_url = url_match.group(0) if url_match else None
        
        # 投稿本文をクリーンアップ
        body = body.strip()
        # ---で区切られている場合は---以降を本文として使用
        if '---' in body:
            parts = body.split('---')
            if len(parts) >= 2:
                body = parts[-1].strip()
        
        posts.append({
            'num': int(num),
            'title': title.strip(),
            'content': body,
            'source_url': source_url
        })
    
    return posts

def detect_account(filename: str) -> tuple[str, str]:
    """ファイル名からアカウント情報を検出"""
    if 'aircle' in filename.lower():
        return 'AirCle', '@aircle_ai'
    elif 'ichiaimarketer' in filename.lower():
        return 'いち@AIxマーケ', '@ichiaimarketer'
    else:
        return 'Unknown', '@unknown'

def detect_date(filename: str) -> str:
    """ファイル名から日付を抽出"""
    match = re.search(r'(\d{4}-\d{2}-\d{2})', filename)
    if match:
        return match.group(1)
    return datetime.now().strftime('%Y-%m-%d')

def generate_html(posts: list[dict], account_name: str, handle: str, date: str, is_marketer: bool = False) -> str:
    """HTMLを生成"""
    
    # カラースキーム
    if is_marketer:
        primary_color = '#ff6b6b'
        secondary_color = '#feca57'
        gradient = 'linear-gradient(90deg, #ff6b6b, #feca57)'
    else:
        primary_color = '#1da1f2'
        secondary_color = '#7b2cbf'
        gradient = 'linear-gradient(90deg, #1da1f2, #7b2cbf)'
    
    # 投稿HTMLを生成
    posts_html = []
    for post in posts:
        source_html = ''
        if post.get('source_url'):
            source_html = f'<div class="source"><a href="{post["source_url"]}" target="_blank">🔗 参考記事</a></div>'
        
        posts_html.append(f'''        <div class="post">
            <div class="post-header">
                <span class="post-number">#{post["num"]}</span>
                <button class="copy-btn" onclick="copyPost(this, {post["num"]})">📋 コピー</button>
            </div>
            <div class="post-content" id="post-{post["num"]}">{post["content"]}</div>
            {source_html}
        </div>
''')
    
    html = f'''<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>X投稿 {date} - {account_name} ({handle})</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, sans-serif;
            background: #0a0a0f;
            color: #e0e0e0;
            padding: 2rem;
        }}
        .container {{ max-width: 800px; margin: 0 auto; }}
        h1 {{
            font-size: 1.8rem;
            margin-bottom: 0.5rem;
            background: {gradient};
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .meta {{ color: #666; margin-bottom: 2rem; }}
        .post {{
            background: rgba(255,255,255,0.03);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
        }}
        .post-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1rem;
        }}
        .post-number {{
            background: {primary_color};
            color: white;
            padding: 0.3rem 0.8rem;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 600;
        }}
        .copy-btn {{
            background: #333;
            color: #fff;
            border: none;
            padding: 0.4rem 1rem;
            border-radius: 6px;
            cursor: pointer;
            font-size: 0.85rem;
        }}
        .copy-btn:hover {{ background: #444; }}
        .copy-btn.copied {{ background: #00c853; }}
        .post-content {{
            white-space: pre-wrap;
            line-height: 1.6;
            margin-bottom: 1rem;
        }}
        .source {{
            font-size: 0.8rem;
            color: #888;
        }}
        .source a {{ color: {secondary_color}; text-decoration: none; }}
        .source a:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📝 X投稿 - {account_name} ({handle})</h1>
        <p class="meta">{date} | {len(posts)}投稿</p>

{''.join(posts_html)}
    </div>

    <script>
        function copyPost(btn, num) {{
            const text = document.getElementById('post-' + num).textContent;
            navigator.clipboard.writeText(text).then(() => {{
                btn.textContent = '✅ コピー完了';
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
    
    return html

def main():
    if len(sys.argv) < 2:
        print("Usage: python md_to_html.py <markdown_file>")
        sys.exit(1)
    
    md_path = Path(sys.argv[1])
    if not md_path.exists():
        print(f"Error: File not found: {md_path}")
        sys.exit(1)
    
    # Markdownを読み込み
    content = md_path.read_text(encoding='utf-8')
    
    # 投稿を抽出
    posts = parse_md_posts(content)
    print(f"Found {len(posts)} posts")
    
    # アカウント情報を検出
    account_name, handle = detect_account(md_path.name)
    date = detect_date(md_path.name)
    is_marketer = 'marketer' in md_path.name.lower()
    
    # HTML生成
    html = generate_html(posts, account_name, handle, date, is_marketer)
    
    # 出力ファイル名を決定
    output_name = date
    if 'aircle' in md_path.name.lower():
        output_name += '-aircle'
    elif 'ichiaimarketer' in md_path.name.lower():
        output_name += '-ichiaimarketer'
    output_name += '.html'
    
    # 出力先ディレクトリ
    output_dir = Path(__file__).parent.parent / 'public' / 'daily-posts'
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / output_name
    
    # 書き込み
    output_path.write_text(html, encoding='utf-8')
    print(f"Generated: {output_path}")
    
    return str(output_path)

if __name__ == '__main__':
    main()
