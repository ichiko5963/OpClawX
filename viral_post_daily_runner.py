#!/usr/bin/env python3
"""
Viral Post Daily Runner v3
毎日15個の高品質投稿を生成し、Web URLで配信
X Premiumデータ + 過去ナレッジ + 最新トレンドを融合
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict

# パス設定
WORKSPACE = Path.home() / "Documents/OpenClaw-Workspace"
VPA_DIR = WORKSPACE / "viral-post-automation"
OUTPUT_DIR = VPA_DIR / "web/public/daily-posts"
DATA_DIR = VPA_DIR / "data"

sys.path.insert(0, str(VPA_DIR / "core"))
from generator_v3 import ViralPatternDetector, PostGenerator

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

X_PREMIUM_DATA = DATA_DIR / "x_premium_analytics.json"


class XPremiumDataLoader:
    def load(self) -> List[Dict]:
        if X_PREMIUM_DATA.exists():
            with open(X_PREMIUM_DATA) as f:
                return json.load(f)
        return self._get_sample_data()
    
    def _get_sample_data(self) -> List[Dict]:
        return [
            {"text": "【速報】Claude Codeが新機能リリース 🔥\n\n・コーディング支援が大幅進化\n・エージェント機能が標準搭載\n\n詳細はスレッド👇", "likes": 1250, "retweets": 380, "replies": 95},
            {"text": "【保存版】Cursor AI完全活用ガイド 📌\n\n① ショートカット覚える\n② カスタムルール設定\n\nブックマーク推奨", "likes": 2100, "retweets": 890, "replies": 120},
        ]


class HTMLGenerator:
    def generate(self, posts: List[Dict], date_str: str) -> str:
        html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>Viral Posts {date_str}</title>
    <style>
        body {{ font-family: sans-serif; background: #0a0a0f; color: #fff; padding: 2rem; }}
        .post {{ background: #1a1a25; border-radius: 12px; padding: 1.5rem; margin: 1rem 0; }}
        .pattern {{ color: #6366f1; font-weight: bold; }}
    </style>
</head>
<body>
    <h1>🚀 Daily Viral Posts - {date_str}</h1>
"""
        for i, post in enumerate(posts, 1):
            html += f"""
    <div class="post">
        <div class="pattern">{i}. {post['pattern_name']}</div>
        <pre>{post['content']}</pre>
    </div>
"""
        html += "</body></html>"
        return html
    
    def save(self, posts: List[Dict], date_str: str) -> Path:
        html = self.generate(posts, date_str)
        filepath = OUTPUT_DIR / f"{date_str}.html"
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
        return filepath


def main():
    today = datetime.now().strftime("%Y-%m-%d")
    
    # 1. X Premiumデータ読み込み
    loader = XPremiumDataLoader()
    x_data = loader.load()
    
    # 2. パターン検出
    detector = ViralPatternDetector()
    patterns = detector.detect_patterns_from_x_premium(x_data)
    
    # 3. 投稿生成
    generator = PostGenerator()
    trends = [{"title": "AI最新情報"}]
    posts = generator.generate_posts(patterns, trends)
    
    # 4. HTML保存
    html_gen = HTMLGenerator()
    filepath = html_gen.save(posts, today)
    
    print(f"✅ Generated {len(posts)} posts")
    print(f"📄 Saved to: {filepath}")
    print(f"🔗 URL: https://vpa.opclaw.app/daily-posts/{today}.html")


if __name__ == "__main__":
    main()
