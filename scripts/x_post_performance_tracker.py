#!/usr/bin/env python3
"""
X Post Performance Tracker

X投稿の効果測定を自動化します。
- 投稿後のエンゲージメント追跡（いいね、RT、インプレッション）
- パフォーマンス分析レポート生成
- 次回への改善提案

TODO: X APIまたはスクレイピングでデータ取得（現在はモックアップ）

Usage:
    python scripts/x_post_performance_tracker.py --account aircle_ai
    python scripts/x_post_performance_tracker.py --account ichiaimarketer
    python scripts/x_post_performance_tracker.py --all  # 全アカウント
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
import re

WORKSPACE = Path.home() / "Documents/OpenClaw-Workspace"
PROJECTS_DIR = WORKSPACE / "projects"

class XPostPerformanceTracker:
    def __init__(self, account=None):
        self.account = account
        self.posts_data = []
        self.stats = {
            "total_posts": 0,
            "avg_likes": 0,
            "avg_rts": 0,
            "avg_impressions": 0,
            "top_performing": [],
            "underperforming": []
        }
    
    def track(self):
        """パフォーマンス追跡実行"""
        print("📊 X Post Performance Tracker")
        print("=" * 60)
        
        # 1. 投稿データ読み込み
        self._load_posts()
        
        # 2. パフォーマンスデータ取得（TODO: 実装）
        self._fetch_performance_data()
        
        # 3. 分析実行
        self._analyze_performance()
        
        # 4. レポート出力
        self._print_report()
        
        # 5. 改善提案生成
        self._generate_suggestions()
    
    def _load_posts(self):
        """過去7日分の投稿ファイルを読み込む"""
        print(f"📂 Loading posts for account: {self.account or 'all'}...")
        
        cutoff_date = datetime.now() - timedelta(days=7)
        
        # x-posts-YYYY-MM-DD-{account}.md ファイルを探す
        pattern = f"x-posts-*-{self.account}.md" if self.account else "x-posts-*.md"
        
        for file in sorted(PROJECTS_DIR.glob(pattern)):
            # ファイル名から日付抽出
            match = re.match(r'x-posts-(\d{4}-\d{2}-\d{2})-(.+)\.md', file.name)
            if not match:
                continue
            
            file_date = datetime.strptime(match.group(1), "%Y-%m-%d")
            if file_date < cutoff_date:
                continue
            
            account_name = match.group(2)
            
            # ファイル内容から投稿を抽出
            content = file.read_text(encoding="utf-8")
            posts = self._parse_posts(content, file_date, account_name)
            self.posts_data.extend(posts)
        
        print(f"✅ Loaded {len(self.posts_data)} posts")
    
    def _parse_posts(self, content: str, date: datetime, account: str) -> list:
        """Markdownから投稿を抽出"""
        posts = []
        
        # 簡易パーサー: "## 投稿N" で区切られていると仮定
        sections = re.split(r'^## 投稿\d+', content, flags=re.MULTILINE)
        
        for i, section in enumerate(sections[1:], 1):
            # 投稿テキストを抽出（コードブロックまたは引用符）
            text_match = re.search(r'```(.+?)```|「(.+?)」', section, re.DOTALL)
            if text_match:
                text = text_match.group(1) or text_match.group(2)
                posts.append({
                    "id": f"{account}-{date.strftime('%Y%m%d')}-{i}",
                    "date": date,
                    "account": account,
                    "text": text.strip()[:100],
                    "url": None  # TODO: 実際のURL
                })
        
        return posts
    
    def _fetch_performance_data(self):
        """パフォーマンスデータ取得（TODO: X API実装）"""
        print("📡 Fetching performance data...")
        
        # TODO: 実際のX APIまたはスクレイピング
        # 現在はモックデータ
        import random
        for post in self.posts_data:
            post["likes"] = random.randint(10, 500)
            post["rts"] = random.randint(2, 100)
            post["impressions"] = random.randint(500, 10000)
        
        print("⚠️  Using mock data (X API not implemented)")
    
    def _analyze_performance(self):
        """パフォーマンス分析"""
        print("🔬 Analyzing performance...")
        
        if not self.posts_data:
            return
        
        self.stats["total_posts"] = len(self.posts_data)
        self.stats["avg_likes"] = sum(p["likes"] for p in self.posts_data) / len(self.posts_data)
        self.stats["avg_rts"] = sum(p["rts"] for p in self.posts_data) / len(self.posts_data)
        self.stats["avg_impressions"] = sum(p["impressions"] for p in self.posts_data) / len(self.posts_data)
        
        # トップパフォーマンス
        sorted_by_engagement = sorted(self.posts_data, 
                                      key=lambda x: x["likes"] + x["rts"] * 2, 
                                      reverse=True)
        self.stats["top_performing"] = sorted_by_engagement[:3]
        
        # アンダーパフォーマンス
        self.stats["underperforming"] = sorted_by_engagement[-3:]
    
    def _print_report(self):
        """レポート出力"""
        print("\n" + "=" * 60)
        print("📊 Performance Report")
        print("=" * 60)
        
        print(f"\n【サマリー】")
        print(f"  総投稿数: {self.stats['total_posts']}")
        print(f"  平均いいね: {self.stats['avg_likes']:.1f}")
        print(f"  平均RT: {self.stats['avg_rts']:.1f}")
        print(f"  平均インプレッション: {self.stats['avg_impressions']:.1f}")
        
        if self.stats["top_performing"]:
            print(f"\n🏆 トップパフォーマンス")
            for i, post in enumerate(self.stats["top_performing"], 1):
                engagement = post["likes"] + post["rts"] * 2
                print(f"  {i}. {post['account']} - {post['date'].strftime('%m/%d')}")
                print(f"     💚 {post['likes']} いいね | 🔁 {post['rts']} RT | 👁 {post['impressions']} views")
                print(f"     📝 {post['text'][:60]}...")
        
        if self.stats["underperforming"]:
            print(f"\n📉 要改善")
            for i, post in enumerate(self.stats["underperforming"], 1):
                print(f"  {i}. {post['account']} - {post['date'].strftime('%m/%d')}")
                print(f"     💚 {post['likes']} いいね | 🔁 {post['rts']} RT")
                print(f"     📝 {post['text'][:60]}...")
    
    def _generate_suggestions(self):
        """改善提案生成"""
        print("\n" + "=" * 60)
        print("💡 改善提案")
        print("=" * 60)
        
        # トップパフォーマンスの共通パターン分析
        print("\n【成功パターン】")
        print("  - トップ投稿の共通点を分析して次回に活かす")
        print("  - エンゲージメント率の高い時間帯を特定")
        
        print("\n【改善点】")
        print("  - アンダーパフォーマンス投稿の構造を見直す")
        print("  - 絵文字・画像の活用")
        print("  - ハッシュタグ戦略の最適化")
        
        print("\n【次回アクション】")
        print("  1. バズ投稿の型を使う（速報型、海外バズ型）")
        print("  2. 投稿時間を最適化（16:00, 0:00, 8:00）")
        print("  3. エンゲージメント追跡を継続")


def main():
    account = None
    if "--account" in sys.argv:
        idx = sys.argv.index("--account")
        if idx + 1 < len(sys.argv):
            account = sys.argv[idx + 1]
    
    tracker = XPostPerformanceTracker(account=account)
    tracker.track()


if __name__ == "__main__":
    main()
