#!/usr/bin/env python3
"""
X Post Generator - AirCle投稿自动生成
 過去のバズった投稿の型を参考にした投稿生成
"""

import os
import json
import random
from datetime import datetime
from typing import List, Dict
from pathlib import Path

# バズの型定義
VIRAL_PATTERNS = {
    "結論型": {
        "hooks": [
            "【結論から言います】",
            "【結論】",
            "結論：",
            "で、結論としては"
        ],
        "structure": "フック → 結論 → 理由3選 → まとめ",
        "avg_likes": 306.7
    },
    "速報型": {
        "hooks": [
            "【速報】",
            "【緊急】",
            "【朗報】",
            "🔥 【新着】"
        ],
        "structure": "フック → 内容 → 出典 → 意義",
        "avg_likes": 173.2
    },
    "リスト型": {
        "hooks": [
            "【保存版】",
            "【必読】",
            "〇〇選",
            "〇選"
        ],
        "structure": "フック → リスト → 各説明 → まとめ",
        "avg_likes": 153.3
    },
    "海外バズ型": {
        "hooks": [
            "【海外で大バズ】",
            "【海外で話題】",
            "【世界中が驚愕】"
        ],
        "structure": "フック → 内容 → 海外反応 → 、日本での可能性",
        "avg_likes": 178.8
    },
    "正直型": {
        "hooks": [
            "正直、",
            "ぶっちゃけ",
            "本音言うと"
        ],
        "structure": "フック → 主張 → 経験則 → 結論",
        "avg_likes": 120.0
    },
    "配布型": {
        "hooks": [
            "〇〇欲しい人？",
            "無料で配る",
            "pless give away"
        ],
        "structure": "フック → 内容 → 条件 → まとめ",
        "avg_likes": 78.5
    }
}

# よく使われる絵文字
EMOJI_SET = {
    "fire": "🔥",
    "point_down": "👇",
    "shocked": "😳",
    "warning": "⚠️",
    "check": "✅",
    "rocket": "🚀",
    "lightbulb": "💡",
    "money": "💰",
    "tech": "🛠️",
    "ai": "🤖"
}

# 禁止絵文字（情報的な絵文字）
FORBIDDEN_EMOJI = ["📱", "📅", "🔗", "📰", "🚨", "📧", "📊", "📈", "📉", "🗓️", "🔔"]


class PostGenerator:
    def __init__(self, history_dir: str = None):
        self.history_dir = history_dir or "/Users/ai-driven-work/Documents/OpenClaw-Workspace/projects"
        self.viral_posts = self.load_viral_posts()
    
    def load_viral_posts(self) -> List[Dict]:
        """Load and analyze past viral posts"""
        viral = []
        
        # Load all post files
        for f in Path(self.history_dir).glob("x-posts-*.md"):
            try:
                with open(f) as fp:
                    content = fp.read()
                    # Extract post structure (simplified)
                    posts = self._parse_posts(content)
                    viral.extend(posts)
            except Exception as e:
                print(f"Error loading {f}: {e}")
        
        return viral
    
    def _parse_posts(self, content: str) -> List[Dict]:
        """Parse post content"""
        posts = []
        lines = content.split("\n")
        current_post = None
        
        for line in lines:
            line = line.strip()
            if line.startswith("## ") or line.startswith("### "):
                if current_post:
                    posts.append(current_post)
                current_post = {"title": line.lstrip("# ").strip(), "content": ""}
            elif current_post and line:
                current_post["content"] += line + "\n"
        
        if current_post:
            posts.append(current_post)
        
        return posts
    
    def generate_posts(
        self,
        count: int = 60,
        topic: str = None,
        account: str = "aircle"
    ) -> List[Dict]:
        """Generate new posts based on viral patterns"""
        generated = []
        
        for i in range(count):
            # Select pattern
            pattern = self._select_pattern()
            
            # Generate post
            post = self._create_post(pattern, topic, i + 1)
            generated.append(post)
        
        return generated
    
    def _select_pattern(self) -> Dict:
        """Select a viral pattern based on performance"""
        # Weighted random selection
        weights = [p["avg_likes"] for p in VIRAL_PATTERNS.values()]
        total = sum(weights)
        weights = [w / total for w in weights]
        
        patterns = list(VIRAL_PATTERNS.keys())
        selected = random.choices(patterns, weights=weights)[0]
        
        return {
            "name": selected,
            "hooks": VIRAL_PATTERNS[selected]["hooks"],
            "structure": VIRAL_PATTERNS[selected]["structure"]
        }
    
    def _create_post(self, pattern: Dict, topic: str, index: int) -> Dict:
        """Create a single post"""
        hook = random.choice(pattern["hooks"])
        
        # Generate content based on topic
        if topic:
            content = self._generate_topic_content(topic, pattern["name"])
        else:
            content = self._generate_generic_content(pattern["name"], index)
        
        # Add CTA
        cta = self._generate_cta(pattern["name"])
        
        post_text = f"{hook}\n\n{content}\n\n{cta}"
        
        return {
            "id": f"generated_{datetime.now().strftime('%Y%m%d')}_{index}",
            "pattern": pattern["name"],
            "text": post_text,
            "topic": topic or "general"
        }
    
    def _generate_topic_content(self, topic: str, pattern_name: str) -> str:
        """Generate content for specific topic"""
        # Placeholder - will use AI to generate actual content
        templates = {
            "結論型": f"关于{topic}，我得出以下{random.randint(3, 5)}个结论：\n" + "\n".join([f"{i+1}. " for i in range(3)]),
            "速報型": f"{topic}に関する驚くべきニュースがあります。",
            "リスト型": f"{topic}について、{random.randint(5, 10)}つの重要なポイントをまとめました：",
            "海外バズ型": f"海外で{topic}が大バズしています。",
            "正直型": f"正直、{topic}についてはこのように思います。",
            "配布型": f"{topic}についてもっと知りたい人はいますか？"
        }
        return templates.get(pattern_name, f"关于{topic}的内容。")
    
    def _generate_generic_content(self, pattern_name: str, index: int) -> str:
        """Generate generic content"""
        topics = [
            "AI開発の最前線",
            "Claude Codeの活用法",
            "CursorとAIコード生成",
            "Next.jsとAI",
            "Vibe Codingの未来",
            "Supabaseの便利機能",
            "OpenClawの自動化"
        ]
        topic = topics[index % len(topics)]
        return self._generate_topic_content(topic, pattern_name)
    
    def _generate_cta(self, pattern_name: str) -> str:
        """Generate call-to-action"""
        ctas = {
            "結論型": "你觉得怎么样？评论告诉我 👇",
            "速報型": "更多信息请关注后续报道。",
            "リスト型": "请保存以备后用 📌",
            "海外バズ型": "日本也很快就会普及吧？",
            "正直型": "你有不同的看法吗？",
            "配布型": "想要更多信息的话请告诉我！"
        }
        return ctas.get(pattern_name, "请告诉我你的想法。")


# AI-powered post generator with research
class AIPostGenerator(PostGenerator):
    """AI-powered post generator with web research"""
    
    def __init__(self, history_dir: str = None, openai_key: str = None):
        super().__init__(history_dir)
        self.openai_key = openai_key or os.getenv("OPENAI_API_KEY")
    
    def generate_with_research(
        self,
        count: int = 60,
        topic: str = None,
        account: str = "aircle"
    ) -> List[Dict]:
        """Generate posts with actual research"""
        # First, search for latest news
        news = self._search_latest_news(topic)
        
        # Then generate posts using viral patterns
        posts = self.generate_posts(count, topic, account)
        
        # Enrich with researched content
        for post in posts:
            if news:
                post["research"] = random.choice(news)
        
        return posts
    
    def _search_latest_news(self, topic: str = None) -> List[Dict]:
        """Search for latest news (placeholder)"""
        # Will integrate with web search
        return []


if __name__ == "__main__":
    generator = PostGenerator()
    posts = generator.generate_posts(5)
    
    for i, p in enumerate(posts, 1):
        print(f"\n=== Post {i} ({p['pattern']}) ===")
        print(p["text"][:200] + "...")
