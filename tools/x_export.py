#!/usr/bin/env python3
"""
X投稿エクスポートツール
投稿ファイルから投稿をコピペしやすい形式で出力
"""

import os
import re
from datetime import datetime
from pathlib import Path

def parse_posts_from_markdown(file_path: str) -> list[dict]:
    """マークダウンファイルから投稿を抽出"""
    posts = []
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    pattern = r'### 投稿(\d+): (.+?)\n(.+?)(?=\n---|\n### 投稿|\Z)'
    matches = re.findall(pattern, content, re.DOTALL)
    
    for match in matches:
        posts.append({
            'number': int(match[0]),
            'title': match[1].strip(),
            'body': match[2].strip(),
        })
    
    return posts

def export_plain_text(posts: list[dict], output_path: Path):
    """プレーンテキストで出力"""
    lines = []
    
    for post in posts:
        lines.append("=" * 60)
        lines.append(f"投稿 {post['number']}: {post['title']}")
        lines.append("=" * 60)
        lines.append("")
        lines.append(post['body'])
        lines.append("")
        lines.append("")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    print(f"出力完了: {output_path}")

def export_csv(posts: list[dict], output_path: Path):
    """CSV形式で出力"""
    import csv
    
    with open(output_path, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['番号', 'タイトル', '本文', '文字数'])
        
        for post in posts:
            writer.writerow([
                post['number'],
                post['title'],
                post['body'].replace('\n', '\\n'),
                len(post['body'])
            ])
    
    print(f"出力完了: {output_path}")

def main():
    workspace = Path(__file__).parent.parent
    projects_dir = workspace / 'projects'
    
    print("=" * 60)
    print("📤 X投稿エクスポートツール")
    print("=" * 60)
    
    today = datetime.now().strftime('%Y-%m-%d')
    
    for account in ['aircle', 'ichiaimarketer', 'extra']:
        if account == 'extra':
            post_file = projects_dir / f'x-posts-{today}-{account}.md'
        else:
            post_file = projects_dir / f'x-posts-{today}-{account}.md'
        
        if not post_file.exists():
            pattern = f'x-posts-*-{account}.md'
            files = list(projects_dir.glob(pattern))
            if files:
                post_file = sorted(files)[-1]
            else:
                continue
        
        posts = parse_posts_from_markdown(str(post_file))
        
        if posts:
            print(f"\n📱 {account}: {len(posts)}件")
            
            # プレーンテキスト出力
            txt_path = projects_dir / f'export-{account}-{today}.txt'
            export_plain_text(posts, txt_path)
            
            # CSV出力
            csv_path = projects_dir / f'export-{account}-{today}.csv'
            export_csv(posts, csv_path)
    
    print("\n" + "=" * 60)
    print("使い方:")
    print("  .txtファイル: そのままコピペ用")
    print("  .csvファイル: スプレッドシート用")
    print("=" * 60)

if __name__ == '__main__':
    main()
