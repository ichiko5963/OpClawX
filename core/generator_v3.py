#!/usr/bin/env python3
"""
Viral Post Generator v3 - X Premium連携・動的パターン検出・15投稿生成
毎日最新トレンド + 過去ナレッジを分析し、15個の高品質投稿案を生成
"""

import json
import os
import sys
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import subprocess

# パス設定
WORKSPACE = Path.home() / "Documents/OpenClaw-Workspace"
VPA_DIR = WORKSPACE / "viral-post-automation"
OUTPUT_DIR = VPA_DIR / "web/public/daily-posts"
MEMORY_DIR = WORKSPACE / "memory"
DATA_DIR = VPA_DIR / "data"

# 出力ディレクトリ作成
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

# X Premium分析データのパス
X_PREMIUM_DATA = DATA_DIR / "x_premium_analytics.json"
PATTERN_HISTORY = DATA_DIR / "pattern_history.json"
TREND_CACHE = DATA_DIR / "trend_cache.json"


class ViralPatternDetector:
    """X Premiumデータから動的にバズ型を検出"""
    
    def __init__(self):
        self.patterns = []
        self.load_history()
    
    def load_history(self):
        """過去のパターンデータを読み込み"""
        if PATTERN_HISTORY.exists():
            with open(PATTERN_HISTORY) as f:
                self.history = json.load(f)
        else:
            self.history = {"patterns": [], "last_updated": None}
    
    def save_history(self):
        """パターンデータを保存"""
        with open(PATTERN_HISTORY, 'w') as f:
            json.dump(self.history, f, indent=2, ensure_ascii=False)
    
    def detect_patterns_from_x_premium(self, data: List[Dict]) -> List[Dict]:
        """
        X Premium分析データからバズ型を検出
        
        検出ロジック:
        1. エンゲージメント率が高い投稿を抽出
        2. テキストの構造パターンを分析
        3. 既存15型 + カスタム型を統合
        """
        patterns = []
        
        # 基本型（参考用に保持）
        base_patterns = {
            'breaking_news': {
                'name': '速報型',
                'indicators': ['【速報】', 'ついに', 'Breaking', 'リリース', '発表'],
                'weight': 1.8
            },
            'save_for_later': {
                'name': '保存版型',
                'indicators': ['【保存版】', 'まとめ', 'Complete', 'Guide', '📌'],
                'weight': 2.5
            },
            'global_trend': {
                'name': '海外バズ型',
                'indicators': ['【海外で話題】', '海外バズ', 'Trending', '世界が'],
                'weight': 1.5
            },
            'conclusion_first': {
                'name': '結論型',
                'indicators': ['【結論】', '要するに', 'Conclusion', '答え'],
                'weight': 2.0
            },
            'honest_opinion': {
                'name': '正直型',
                'indicators': ['正直', '本音', 'Honestly', 'ぶっちゃけ'],
                'weight': 1.4
            },
            'comparison': {
                'name': '比較型',
                'indicators': [' vs ', '比較', 'どっち', 'VS', '⚔️'],
                'weight': 1.5
            },
            'experience': {
                'name': '体験記型',
                'indicators': ['使ってみた', 'レビュー', '体験', 'Tried', '感想'],
                'weight': 1.3
            },
            'data_driven': {
                'name': 'データ型',
                'indicators': ['📊', '％', '倍', 'データ', '統計', 'Numbers'],
                'weight': 1.6
            },
            'insight': {
                'name': '洞察型',
                'indicators': ['実は', '秘密', '真相', '本質', '知られていない'],
                'weight': 1.5
            },
            'free_resource': {
                'name': '配布型',
                'indicators': ['【配布】', '無料', 'プレゼント', '🎁', '欲しい人'],
                'weight': 3.0
            },
            'pro_tips': {
                'name': '裏技型',
                'indicators': ['裏技', '知ってると差', 'Tips', '💎', 'プロ技'],
                'weight': 1.4
            },
            'warning': {
                'name': '警告型',
                'indicators': ['⚠️', '【注意】', '危険', '警告', '気をつけて'],
                'weight': 1.7
            },
            'storytelling': {
                'name': 'ストーリー型',
                'indicators': ['だった私が', '経験', '話', 'Journey', 'なった'],
                'weight': 1.2
            },
            'complete_guide': {
                'name': '完全解説型',
                'indicators': ['完全', '徹底', 'マスター', '全て', 'Complete'],
                'weight': 1.8
            },
            'prediction': {
                'name': '予測型',
                'indicators': ['年後', '未来', '予測', '来る', 'Future', '変わる'],
                'weight': 1.4
            }
        }
        
        # X Premiumデータから実際のパフォーマンスを分析
        pattern_performance = {}
        
        for post in data:
            text = post.get('text', '')
            engagement = post.get('likes', 0) + post.get('retweets', 0) * 2 + post.get('replies', 0) * 3
            
            for pid, pattern in base_patterns.items():
                score = 0
                for indicator in pattern['indicators']:
                    if indicator.lower() in text.lower():
                        score += 1
                
                if score > 0:
                    if pid not in pattern_performance:
                        pattern_performance[pid] = {
                            'total_engagement': 0,
                            'count': 0,
                            'name': pattern['name'],
                            'weight': pattern['weight']
                        }
                    pattern_performance[pid]['total_engagement'] += engagement
                    pattern_performance[pid]['count'] += 1
        
        # 平均エンゲージメントでソート
        for pid, stats in pattern_performance.items():
            avg_eng = stats['total_engagement'] / stats['count'] if stats['count'] > 0 else 0
            patterns.append({
                'id': pid,
                'name': stats['name'],
                'avg_engagement': avg_eng,
                'count': stats['count'],
                'weight': stats['weight'],
                'score': avg_eng * stats['weight']  # 重み付けスコア
            })
        
        # スコア順にソート
        patterns.sort(key=lambda x: x['score'], reverse=True)
        
        # トップ15を返す
        return patterns[:15]
    
    def get_trending_keywords(self) -> List[str]:
        """最新トレンドキーワードを取得"""
        keywords = [
            'ClaudeCode', 'Cursor', 'Antigravity', 'Gemini CLI', 
            'OpenAI Codex', 'Vercel', 'vibe coding', 'AI agent',
            'OpenClaw', 'multi agent', 'Claude', 'GPT-5',
            'AI coding', ' autonomous', 'agent framework'
        ]
        
        # キャッシュがあれば更新
        if TREND_CACHE.exists():
            with open(TREND_CACHE) as f:
                cache = json.load(f)
                cache_time = datetime.fromisoformat(cache.get('timestamp', '2000-01-01'))
                if datetime.now() - cache_time < timedelta(hours=6):
                    return cache.get('keywords', keywords)
        
        return keywords


class PostGenerator:
    """15個の高品質投稿を生成"""
    
    def __init__(self):
        self.detector = ViralPatternDetector()
        self.posts = []
    
    def generate_posts(self, patterns: List[Dict], trends: List[Dict]) -> List[Dict]:
        """
        15個の投稿を生成
        
        各投稿に含める要素:
        1. パターンに基づく構成
        2. 最新トレンド情報
        3. 過去ナレッジの活用
        """
        posts = []
        
        for i, pattern in enumerate(patterns[:15]):  # 最大15個
            post = self._generate_single_post(pattern, trends, i)
            posts.append(post)
        
        return posts
    
    def _generate_single_post(self, pattern: Dict, trends: List[Dict], index: int) -> Dict:
        """1つの投稿を生成"""
        
        # トレンドからトピックを選択
        topic = self._select_topic(trends, index)
        
        # パターンに基づく構造を生成
        structure = self._get_structure_for_pattern(pattern['id'])
        
        # 投稿テキスト生成
        content = self._generate_content(pattern, topic, structure)
        
        return {
            'id': f"post_{datetime.now().strftime('%Y%m%d')}_{index+1:02d}",
            'pattern_id': pattern['id'],
            'pattern_name': pattern['name'],
            'topic': topic,
            'content': content,
            'structure': structure,
            'score': pattern['score'],
            'created_at': datetime.now().isoformat()
        }
    
    def _select_topic(self, trends: List[Dict], index: int) -> str:
        """トレンドからトピックを選択"""
        if trends and index < len(trends):
            return trends[index].get('title', 'AI最新情報')
        
        default_topics = [
            'Claude Code最新機能',
            'Cursor AI効率化術',
            'Vibe Coding実践法',
            'AIエージェント設計',
            'マルチエージェント連携',
            'OpenClaw活用術',
            'AI開発最前線',
            '自動化ワークフロー',
            'AIツール比較',
            '生産性向上テクニック'
        ]
        return default_topics[index % len(default_topics)]
    
    def _get_structure_for_pattern(self, pattern_id: str) -> Dict:
        """パターンに応じた構造を返す"""
        structures = {
            'breaking_news': {
                'hook': '【速報】{topic}が登場 🔥',
                'body': '・\n・\n・',
                'cta': '詳細はスレッド👇'
            },
            'save_for_later': {
                'hook': '【保存版】{topic}完全ガイド 📌',
                'body': '① \n② \n③',
                'cta': 'ブックマーク推奨'
            },
            'global_trend': {
                'hook': '【海外で話題】{topic}が世界的バズ 🌎',
                'body': '海外の反応:\n・\n・\n・',
                'cta': '日本での活用方法👇'
            },
            'conclusion_first': {
                'hook': '【結論】{topic}の最適解はこれ 💡',
                'body': '理由:\n・\n・\n・',
                'cta': '具体的手法は👇'
            },
            'honest_opinion': {
                'hook': '正直、{topic}について言うと...',
                'body': '本音:\n・\n・\n・',
                'cta': '続きは👇'
            },
            'comparison': {
                'hook': '【比較】A vs B ⚔️',
                'body': 'Aの強み:\n・\nBの強み:\n・',
                'cta': '結論👇'
            },
            'experience': {
                'hook': '【体験記】{topic}を使ってみた',
                'body': '期待 → 現実:\n・\n・\n・',
                'cta': '総評👇'
            },
            'data_driven': {
                'hook': '【データ】{topic}の驚くべき事実 📊',
                'body': '・XX%\n・XX倍\n・XX分',
                'cta': '意味するもの👇'
            },
            'insight': {
                'hook': '実は、{topic}でこれが本質',
                'body': '真実:\n・\n・\n・',
                'cta': '洞察👇'
            },
            'free_resource': {
                'hook': '【配布】{topic}テンプレート 🎁',
                'body': '含まれるもの:\n・\n・\n・',
                'cta': '入手方法👇'
            },
            'pro_tips': {
                'hook': '知ってると差がつく{topic}の裏技 💎',
                'body': '① \n② \n③',
                'cta': '効果👇'
            },
            'warning': {
                'hook': '⚠️ {topic}で気をつけるべき点',
                'body': 'リスク:\n・\n・\n・',
                'cta': '対策👇'
            },
            'storytelling': {
                'hook': '{topic}だった私が変わった話',
                'body': 'Before → After:\n・\n・\n・',
                'cta': '学び👇'
            },
            'complete_guide': {
                'hook': '【完全版】{topic}マスターガイド 📚',
                'body': '基礎 → 応用:\n・\n・\n・',
                'cta': '次のステップ👇'
            },
            'prediction': {
                'hook': '3年後の{topic}はこうなる',
                'body': '根拠:\n・\n・\n・',
                'cta': '今やるべきこと👇'
            }
        }
        
        return structures.get(pattern_id, structures['breaking_news'])
    
    def _generate_content(self, pattern: Dict, topic: str, structure: Dict) -> str:
        """実際の投稿テキストを生成"""
        hook = structure['hook'].format(topic=topic)
        body = structure['body']
        cta = structure['cta']
        
        return f"{hook}\n\n{body}\n\n{cta}"

