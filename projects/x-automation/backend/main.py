#!/usr/bin/env python3
"""
AirCle X Automation - Main Controller
每日自動実行: 投稿生成・トレンド監視・アカウント監視
"""

import os
import sys
import json
import asyncio
import subprocess
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from post_generator import PostGenerator, AIPostGenerator
from x_api_client import XAPIClient, MONITORED_ACCOUNTS, TRENDING_KEYWORDS

# Load environment
load_dotenv()

# Paths
PROJECT_DIR = Path(__file__).parent.parent
FRONTEND_DIR = PROJECT_DIR / "frontend"
PUBLIC_DIR = FRONTEND_DIR / "public"
DATA_DIR = PROJECT_DIR / "data"


class XAutomationController:
    def __init__(self):
        self.generator = PostGenerator()
        self.ai_generator = AIPostGenerator()
        self.x_client = XAPIClient()
        self.today = datetime.now().strftime("%Y-%m-%d")
    
    def generate_daily_posts(self, count: int = 60) -> list:
        """每日投稿生成"""
        print(f"📝 Generating {count} posts for {self.today}...")
        
        posts = self.ai_generator.generate_with_research(
            count=count,
            account="aircle"
        )
        
        # Save to JSON
        self._save_posts(posts, "generated")
        
        print(f"✅ Generated {len(posts)} posts")
        return posts
    
    def fetch_trending_posts(self) -> list:
        """トレンド投稿取得 (20:00用)"""
        print("🔥 Fetching trending posts...")
        
        trending = []
        for keyword in TRENDING_KEYWORDS:
            try:
                tweets = self.x_client.search_recent_tweets(
                    query=keyword,
                    max_results=20,
                    min_likes=1000,
                    hours_ahead=24
                )
                trending.extend(tweets)
                print(f"  - {keyword}: {len(tweets)} posts")
            except Exception as e:
                print(f"  - {keyword}: Error - {e}")
        
        # Remove duplicates
        seen = set()
        unique = []
        for t in trending:
            if t["id"] not in seen:
                seen.add(t["id"])
                unique.append(t)
        
        # Sort by likes
        unique.sort(key=lambda x: x["likes"], reverse=True)
        
        # Save
        self._save_posts(unique, "trending")
        
        print(f"✅ Found {len(unique)} unique trending posts")
        return unique
    
    def monitor_accounts(self) -> list:
        """アカウント監視 (15分間隔)"""
        print("👀 Monitoring accounts...")
        
        new_posts = []
        for account in MONITORED_ACCOUNTS:
            try:
                tweets = self.x_client.fetch_user_tweets(account, max_results=5)
                # Filter for new posts (last 15 minutes)
                # In production, store last check time
                new_posts.extend(tweets[:1])  # Just latest for now
                print(f"  - @{account}: {len(tweets)} tweets")
            except Exception as e:
                print(f"  - @{account}: Error - {e}")
        
        return new_posts
    
    def _save_posts(self, posts: list, category: str):
        """Save posts to JSON"""
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        
        filepath = DATA_DIR / f"{category}_posts.json"
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(posts, f, ensure_ascii=False, indent=2)
        
        # Also save to frontend public folder
        PUBLIC_DIR.mkdir(parents=True, exist_ok=True)
        public_filepath = PUBLIC_DIR / f"{category}.json"
        with open(public_filepath, "w", encoding="utf-8") as f:
            json.dump(posts, f, ensure_ascii=False, indent=2)
    
    def build_website(self):
        """Build and deploy website"""
        print("🌐 Building website...")
        
        # Copy data to frontend
        for category in ["generated", "trending"]:
            src = DATA_DIR / f"{category}_posts.json"
            dst = FRONTEND_DIR / "public" / f"{category}.json"
            if src.exists():
                import shutil
                shutil.copy(src, dst)
        
        # Build Next.js (in production)
        # subprocess.run(["npm", "run", "build"], cwd=FRONTEND_DIR)
        
        print("✅ Website ready")
    
    def run_daily(self):
        """每日実行 (6:00)"""
        print(f"\n{'='*50}")
        print(f"📅 Daily Run - {self.today}")
        print(f"{'='*50}\n")
        
        # 1. Generate posts
        self.generate_daily_posts(60)
        
        # 2. Build website
        self.build_website()
        
        # 3. Deploy (in production)
        # self.deploy()
        
        print("\n✅ Daily run complete!")
    
    def run_trending(self):
        """トレンド監視実行 (20:00)"""
        print(f"\n{'='*50}")
        print(f"🔥 Trending Run - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print(f"{'='*50}\n")
        
        # Fetch trending
        trending = self.fetch_trending_posts()
        
        # Build website
        self.build_website()
        
        # Notify Discord
        self.notify_discord_trending(trending)
        
        print("\n✅ Trending run complete!")
    
    def run_monitor(self):
        """アカウント監視実行 (15分間隔)"""
        new_posts = self.monitor_accounts()
        
        if new_posts:
            self.notify_discord_new_posts(new_posts)
        
        return new_posts
    
    def notify_discord_trending(self, posts: list):
        """Discordにトレンド投稿を通知"""
        # Implementation for Discord notification
        print(f"📢 Would notify Discord about {len(posts)} trending posts")
    
    def notify_discord_new_posts(self, posts: list):
        """Discordに新投稿を通知"""
        print(f"📢 Would notify Discord about {len(posts)} new posts")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="AirCle X Automation")
    parser.add_argument("--mode", choices=["daily", "trending", "monitor"], default="daily")
    parser.add_argument("--count", type=int, default=60, help="Number of posts to generate")
    
    args = parser.parse_args()
    
    controller = XAutomationController()
    
    if args.mode == "daily":
        controller.run_daily()
    elif args.mode == "trending":
        controller.run_trending()
    elif args.mode == "monitor":
        controller.run_monitor()


if __name__ == "__main__":
    main()
