#!/usr/bin/env python3
"""
X投稿自動生成・デプロイツール

機能:
1. 最新ニュースを検索してバズりそうなネタを収集
2. 過去のバズ投稿パターンを分析
3. HTMLを自動生成
4. Vercelにデプロイ
5. Discord/Telegramに通知

Usage:
    python x_posts_generator.py --account aircle --date 2026-02-07
    python x_posts_generator.py --account ichiaimarketer --date 2026-02-07
    python x_posts_generator.py --all --date 2026-02-07
"""

import argparse
import json
import subprocess
import os
from pathlib import Path
from datetime import datetime
from typing import Optional

# 設定
ACCOUNTS = {
    'aircle': {
        'name': 'AirCle',
        'handle': '@aircle_ai',
        'keywords': ['Claude Code', 'Cursor', 'Antigravity', 'Vercel', 'OpenClaw', 'Vibe Coding', 'AI Coding'],
        'target': '技術者、エンジニア、開発者',
        'accent_color': '#00d4ff',
        'gradient': 'linear-gradient(135deg, #00d4ff 0%, #7b2cbf 100%)',
        'emoji': '🚀'
    },
    'ichiaimarketer': {
        'name': 'いち@AIxマーケ',
        'handle': '@ichiaimarketer',
        'keywords': ['AI マーケティング', 'SaaS グロース', 'GTM戦略', 'X運用', 'SNSマーケ', 'プロダクトグロース'],
        'target': 'マーケター、ビジネス層、個人開発者',
        'accent_color': '#f093fb',
        'gradient': 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
        'emoji': '📈',
        'categories': [
            ('AIツールのグロース分析', 5),
            ('AI × マーケティング', 5),
            ('プロダクトグロース / GTM戦略', 5),
            ('X運用 / SNSマーケ', 5)
        ]
    },
    'openclaw': {
        'name': 'OpenClaw',
        'handle': '@openclaw',
        'keywords': ['OpenClaw', 'AI Agent', 'Automation', 'LLM', 'Self-hosted'],
        'target': 'エンジニア、開発者',
        'accent_color': '#ff6b6b',
        'gradient': 'linear-gradient(135deg, #ff6b6b 0%, #feca57 100%)',
        'emoji': '🦞'
    }
}

# バズる投稿パターン（MEMORY.mdより）
BUZZ_PATTERNS = [
    '【速報】〜が〜を公開',
    '【海外で大バズ】',
    '【海外で話題】',
    '【結論から言います】',
    '【公式が答えを出してしまった】',
    '正直、〜で始める',
    '〇〇欲しい人いますか？'
]

# 絵文字ルール
ALLOWED_EMOJI = ['🔥', '👇', '😳']
FORBIDDEN_EMOJI = ['📱', '📅', '🔗', '📰', '🚨']

# HTMLテンプレート（改良版）
HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>X投稿ネタ - {date} ({account_name})</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;700&family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
  <style>
    :root {{
      --bg-primary: #0a0a0f;
      --bg-secondary: #12121a;
      --bg-card: #1a1a24;
      --accent: {accent_color};
      --accent-glow: {accent_color}33;
      --text-primary: #f0f0f5;
      --text-secondary: #a0a0b0;
      --success: #10b981;
      --border: rgba(255,255,255,0.08);
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ 
      font-family: 'Inter', 'Noto Sans JP', sans-serif; 
      background: var(--bg-primary); 
      color: var(--text-primary); 
      min-height: 100vh; 
      line-height: 1.6; 
    }}
    .container {{ max-width: 720px; margin: 0 auto; padding: 40px 20px; }}
    .header {{ text-align: center; margin-bottom: 50px; }}
    .header-badge {{ 
      display: inline-block; 
      background: {gradient}; 
      padding: 6px 16px; 
      border-radius: 20px; 
      font-size: 0.75rem; 
      font-weight: 600; 
      margin-bottom: 16px; 
      color: #000; 
    }}
    h1 {{ 
      font-size: 2rem; 
      font-weight: 700; 
      background: {gradient}; 
      -webkit-background-clip: text; 
      -webkit-text-fill-color: transparent; 
      margin-bottom: 8px; 
    }}
    .subtitle {{ color: var(--text-secondary); font-size: 0.95rem; }}
    .section-title {{ 
      color: var(--accent); 
      font-size: 1.1rem; 
      font-weight: 600; 
      margin: 40px 0 20px; 
      padding-left: 12px; 
      border-left: 3px solid var(--accent); 
    }}
    .post {{ 
      background: var(--bg-card); 
      border-radius: 16px; 
      padding: 24px; 
      margin-bottom: 24px; 
      border: 1px solid var(--border); 
      transition: transform 0.2s, box-shadow 0.2s; 
    }}
    .post:hover {{ 
      transform: translateY(-2px); 
      box-shadow: 0 8px 30px rgba(0,0,0,0.3), 0 0 0 1px var(--accent-glow); 
    }}
    .post-header {{ 
      display: flex; 
      align-items: center; 
      gap: 12px; 
      margin-bottom: 16px; 
    }}
    .post-number {{ 
      background: {gradient}; 
      color: #000; 
      width: 32px; 
      height: 32px; 
      border-radius: 10px; 
      display: flex; 
      align-items: center; 
      justify-content: center; 
      font-weight: 700; 
      font-size: 0.85rem; 
    }}
    .post-title {{ font-weight: 600; font-size: 1rem; }}
    .source-section {{ 
      background: var(--bg-secondary); 
      border-radius: 12px; 
      padding: 14px 16px; 
      margin-bottom: 16px; 
      border-left: 3px solid var(--accent); 
    }}
    .source-link {{ 
      color: var(--accent); 
      text-decoration: none; 
      font-size: 0.85rem; 
      margin-bottom: 10px; 
      display: block; 
      word-break: break-all; 
    }}
    .source-link:hover {{ text-decoration: underline; }}
    .translation {{ 
      color: var(--text-secondary); 
      font-size: 0.9rem; 
      line-height: 1.5; 
    }}
    .post-content {{ 
      background: var(--bg-primary); 
      padding: 20px; 
      border-radius: 12px; 
      white-space: pre-wrap; 
      font-size: 0.95rem; 
      line-height: 1.7; 
      position: relative; 
      border: 1px solid var(--border); 
    }}
    .copy-btn {{ 
      position: absolute; 
      top: 12px; 
      right: 12px; 
      background: var(--accent); 
      color: #000; 
      border: none; 
      padding: 8px 16px; 
      border-radius: 8px; 
      cursor: pointer; 
      font-size: 0.8rem; 
      font-weight: 600; 
    }}
    .copy-btn:hover {{ opacity: 0.9; }}
    .copy-btn.copied {{ background: var(--success); color: #fff; }}
    .footer {{ 
      text-align: center; 
      padding: 40px 0; 
      color: var(--text-secondary); 
      font-size: 0.85rem; 
    }}
  </style>
</head>
<body>
  <div class="container">
    <header class="header">
      <div class="header-badge">{emoji} {account_name}</div>
      <h1>X投稿ネタ {formatted_date}</h1>
      <p class="subtitle">{target} | {post_count}投稿</p>
    </header>

{posts_html}

    <footer class="footer">
      <p>Generated by OpenClaw 🦞</p>
    </footer>
  </div>

  <script>
    function copyPost(btn) {{
      const postContent = btn.parentElement;
      const text = postContent.innerText.replace('コピー', '').trim();
      navigator.clipboard.writeText(text).then(() => {{
        btn.textContent = 'コピー完了!';
        btn.classList.add('copied');
        setTimeout(() => {{
          btn.textContent = 'コピー';
          btn.classList.remove('copied');
        }}, 2000);
      }});
    }}
  </script>
</body>
</html>'''

POST_TEMPLATE = '''    <div class="post">
      <div class="post-header">
        <span class="post-number">{num}</span>
        <span class="post-title">{title}</span>
      </div>
      <div class="source-section">
        <a class="source-link" href="{source_url}" target="_blank">{source_title}</a>
        <div class="translation">{translation}</div>
      </div>
      <div class="post-content">
        <button class="copy-btn" onclick="copyPost(this)">コピー</button>
{content}
      </div>
    </div>
'''

SECTION_TEMPLATE = '''    <h2 class="section-title">{icon} {title}</h2>

'''


def get_workspace_root() -> Path:
    """ワークスペースルートを取得"""
    return Path('/Users/ai-driven-work/Library/Mobile Documents/com~apple~CloudDocs/OpenClaw-Shared')


def generate_html(account_id: str, posts: list, date: str) -> str:
    """HTMLを生成"""
    account = ACCOUNTS[account_id]
    
    posts_html = []
    current_section = None
    
    for i, post in enumerate(posts, 1):
        # カテゴリセクション（ichiaimarketerの場合）
        if 'category' in post and post['category'] != current_section:
            current_section = post['category']
            section_icons = {'AIツールのグロース分析': '📊', 'AI × マーケティング': '🤖', 
                           'プロダクトグロース / GTM戦略': '🚀', 'X運用 / SNSマーケ': '📱'}
            icon = section_icons.get(current_section, '📌')
            posts_html.append(SECTION_TEMPLATE.format(icon=icon, title=current_section))
        
        posts_html.append(POST_TEMPLATE.format(
            num=i,
            title=post.get('title', f'投稿{i}'),
            source_url=post.get('source_url', '#'),
            source_title=post.get('source_title', 'Source'),
            translation=post.get('translation', ''),
            content=post.get('content', '')
        ))
    
    # 日付フォーマット
    formatted_date = datetime.strptime(date, '%Y-%m-%d').strftime('%Y/%m/%d')
    
    return HTML_TEMPLATE.format(
        date=date,
        formatted_date=formatted_date,
        account_name=account['name'],
        handle=account['handle'],
        target=account['target'],
        accent_color=account['accent_color'],
        gradient=account['gradient'],
        emoji=account['emoji'],
        post_count=len(posts),
        posts_html=''.join(posts_html)
    )


def save_html(html: str, account_id: str, date: str) -> Path:
    """HTMLをファイルに保存"""
    workspace = get_workspace_root()
    output_dir = workspace / 'public' / 'daily-posts'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_path = output_dir / f'{date}-{account_id}.html'
    output_path.write_text(html, encoding='utf-8')
    
    return output_path


def deploy_to_vercel() -> bool:
    """Vercelにデプロイ"""
    workspace = get_workspace_root()
    public_dir = workspace / 'public'
    
    try:
        result = subprocess.run(
            ['npx', 'vercel', '--prod', '--yes'],
            cwd=str(public_dir),
            capture_output=True,
            text=True,
            timeout=120
        )
        if result.returncode == 0:
            print(f"✅ Deployed successfully")
            return True
        else:
            print(f"❌ Deploy failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Deploy error: {e}")
        return False


def get_vercel_url(account_id: str, date: str) -> str:
    """VercelのURLを生成"""
    return f"https://public-kappa-weld.vercel.app/daily-posts/{date}-{account_id}.html"


def create_sample_posts(account_id: str) -> list:
    """サンプル投稿を生成（実際の運用ではAIが生成）"""
    return [
        {
            'title': 'サンプル投稿1',
            'source_url': 'https://example.com',
            'source_title': 'Example Source',
            'translation': 'これはサンプルの翻訳です。',
            'content': '''【速報】サンプル投稿

これはサンプルの投稿内容です。

実際の運用では、AIが最新ニュースを検索して
バズる投稿を自動生成します。

👇続きはこちら'''
        }
    ] * 20


def main():
    parser = argparse.ArgumentParser(description='X投稿自動生成ツール')
    parser.add_argument('--account', choices=['aircle', 'ichiaimarketer', 'openclaw'], help='対象アカウント')
    parser.add_argument('--all', action='store_true', help='全アカウント分を生成')
    parser.add_argument('--date', default=datetime.now().strftime('%Y-%m-%d'), help='対象日付 (YYYY-MM-DD)')
    parser.add_argument('--deploy', action='store_true', help='Vercelにデプロイ')
    parser.add_argument('--json', type=str, help='投稿データのJSONファイルパス')
    
    args = parser.parse_args()
    
    if not args.account and not args.all:
        print("Error: --account または --all を指定してください")
        return 1
    
    accounts = list(ACCOUNTS.keys()) if args.all else [args.account]
    
    generated_files = []
    
    for account_id in accounts:
        print(f"\n📝 {ACCOUNTS[account_id]['name']} の投稿を生成中...")
        
        # 投稿データを取得
        if args.json:
            with open(args.json, 'r', encoding='utf-8') as f:
                posts = json.load(f)
        else:
            # サンプル投稿（実際はAIが生成）
            posts = create_sample_posts(account_id)
        
        # HTML生成
        html = generate_html(account_id, posts, args.date)
        output_path = save_html(html, account_id, args.date)
        generated_files.append(output_path)
        
        print(f"✅ 生成完了: {output_path}")
        print(f"🔗 URL: {get_vercel_url(account_id, args.date)}")
    
    # デプロイ
    if args.deploy:
        print("\n🚀 Vercelにデプロイ中...")
        deploy_to_vercel()
    
    return 0


if __name__ == '__main__':
    exit(main())
