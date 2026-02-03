#!/usr/bin/env python3
"""
X投稿スケジューラー
投稿ファイルからランダムに投稿を選択し、最適な時間に投稿を提案する
"""

import os
import re
import random
from datetime import datetime, timedelta
from pathlib import Path

# 最適投稿時間 (JST)
OPTIMAL_TIMES = [
    (7, 0),   # 朝の通勤時間
    (12, 0),  # 昼休み
    (18, 0),  # 帰宅時間
    (21, 0),  # 夜のゴールデンタイム
]

def parse_posts_from_markdown(file_path: str) -> list[dict]:
    """マークダウンファイルから投稿を抽出"""
    posts = []
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # ### 投稿N: で始まるセクションを抽出
    pattern = r'### 投稿(\d+): (.+?)\n(.+?)(?=\n---|\n### 投稿|\Z)'
    matches = re.findall(pattern, content, re.DOTALL)
    
    for match in matches:
        post_num = int(match[0])
        title = match[1].strip()
        body = match[2].strip()
        posts.append({
            'number': post_num,
            'title': title,
            'body': body,
            'char_count': len(body)
        })
    
    return posts

def get_next_optimal_times(count: int = 4) -> list[datetime]:
    """次の最適投稿時間を取得"""
    now = datetime.now()
    times = []
    
    for day_offset in range(7):  # 1週間分
        for hour, minute in OPTIMAL_TIMES:
            candidate = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            candidate += timedelta(days=day_offset)
            if candidate > now:
                times.append(candidate)
                if len(times) >= count:
                    return times
    
    return times

def select_posts_for_schedule(posts: list[dict], count: int = 4) -> list[dict]:
    """スケジュール用に投稿を選択"""
    if len(posts) <= count:
        return posts
    return random.sample(posts, count)

def format_post_preview(post: dict, max_chars: int = 100) -> str:
    """投稿プレビューをフォーマット"""
    body = post['body'][:max_chars]
    if len(post['body']) > max_chars:
        body += '...'
    return f"[{post['number']}] {post['title']}\n{body}\n({post['char_count']}文字)"

def main():
    # 投稿ファイルのパス
    workspace = Path(__file__).parent.parent
    projects_dir = workspace / 'projects'
    
    print("=" * 60)
    print("X投稿スケジューラー")
    print("=" * 60)
    
    # 今日の日付のファイルを検索
    today = datetime.now().strftime('%Y-%m-%d')
    
    for account in ['aircle', 'ichiaimarketer']:
        post_file = projects_dir / f'x-posts-{today}-{account}.md'
        
        if not post_file.exists():
            # 最新のファイルを検索
            pattern = f'x-posts-*-{account}.md'
            files = list(projects_dir.glob(pattern))
            if files:
                post_file = sorted(files)[-1]
            else:
                print(f"\n⚠️  {account}: 投稿ファイルが見つかりません")
                continue
        
        print(f"\n📱 アカウント: @{account}")
        print(f"📄 ファイル: {post_file.name}")
        print("-" * 40)
        
        posts = parse_posts_from_markdown(str(post_file))
        print(f"📝 投稿数: {len(posts)}件")
        
        # 次の投稿スケジュールを提案
        selected = select_posts_for_schedule(posts)
        optimal_times = get_next_optimal_times(len(selected))
        
        print("\n📅 推奨スケジュール:")
        for i, (post, time) in enumerate(zip(selected, optimal_times), 1):
            print(f"\n{i}. {time.strftime('%m/%d %H:%M')}")
            print(format_post_preview(post))
    
    print("\n" + "=" * 60)
    print("使い方:")
    print("1. 上記の推奨スケジュールを参考に投稿")
    print("2. Buffer/Typefullyで予約投稿も可")
    print("=" * 60)

if __name__ == '__main__':
    main()
