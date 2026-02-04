"""
ルーティングエンジン
- routing_rules.yaml を読み込んでイベントを分類
- sensitivity.yaml を読み込んで機密判定
- 設定ファイルドリブンで動作
"""

import re
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta

# 設定
JST = timezone(timedelta(hours=9))
CONFIG_PATH = Path("/Users/ai-driven-work/Library/Mobile Documents/com~apple~CloudDocs/OpenClaw-Shared/obsidian/Ichioka Obsidian/00_System/00_Config")


@dataclass
class RoutingResult:
    """ルーティング結果"""
    projects: List[str] = field(default_factory=list)
    people: List[str] = field(default_factory=list)
    companies: List[str] = field(default_factory=list)
    priority: str = "P3"
    action_required: bool = False
    no_reply: bool = False
    sensitivity: str = "internal"
    confidence: float = 0.5
    match_reasons: List[str] = field(default_factory=list)


class RoutingEngine:
    """ルーティングエンジン"""
    
    def __init__(self, config_path: Path = CONFIG_PATH):
        self.config_path = config_path
        self.routing_rules = self._load_yaml("routing_rules.yaml")
        self.sensitivity_rules = self._load_yaml("sensitivity.yaml")
        
        # キャッシュ
        self._compiled_patterns: Dict[str, re.Pattern] = {}
    
    def _load_yaml(self, filename: str) -> Dict:
        """YAMLファイルを読み込み"""
        filepath = self.config_path / filename
        if filepath.exists():
            with open(filepath, encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        return {}
    
    def _compile_pattern(self, pattern: str) -> re.Pattern:
        """正規表現パターンをコンパイル（キャッシュ付き）"""
        if pattern not in self._compiled_patterns:
            try:
                self._compiled_patterns[pattern] = re.compile(pattern, re.IGNORECASE)
            except re.error:
                # 無効なパターンは空マッチ
                self._compiled_patterns[pattern] = re.compile(r"^$")
        return self._compiled_patterns[pattern]
    
    def _text_from_event(self, event: Dict) -> str:
        """イベントから検索用テキストを抽出"""
        parts = [
            str(event.get("title", "")),
            str(event.get("body", "")),
            str(event.get("actor", {}).get("email", "")),
            str(event.get("actor", {}).get("name", "")),
        ]
        return " ".join(parts).lower()
    
    def _match_keywords(self, text: str, keywords: List[str]) -> List[str]:
        """キーワードマッチ"""
        matched = []
        text_lower = text.lower()
        for kw in keywords:
            if kw.lower() in text_lower:
                matched.append(kw)
        return matched
    
    def _match_patterns(self, text: str, patterns: List[str]) -> List[str]:
        """パターンマッチ"""
        matched = []
        for pattern in patterns:
            compiled = self._compile_pattern(pattern)
            if compiled.search(text):
                matched.append(pattern)
        return matched
    
    def route_to_projects(self, event: Dict) -> List[Tuple[str, float, str]]:
        """プロジェクトにルーティング
        Returns: [(project_name, confidence, reason), ...]
        """
        results = []
        text = self._text_from_event(event)
        source = event.get("source", "")
        
        projects_config = self.routing_rules.get("projects", {})
        
        for project_name, config in projects_config.items():
            if not config.get("active", True):
                continue
            
            confidence = 0.0
            reasons = []
            
            # キーワードマッチ
            keywords = config.get("keywords", [])
            matched_kw = self._match_keywords(text, keywords)
            if matched_kw:
                confidence += 0.3 * len(matched_kw)
                reasons.append(f"keywords: {matched_kw[:3]}")
            
            # Slackチャンネルマッチ
            if source == "slack":
                channel = str(event.get("targets", {}).get("channel", ""))
                slack_channels = config.get("slack_channels", [])
                if channel and any(ch.lower() in channel.lower() for ch in slack_channels):
                    confidence += 0.5
                    reasons.append(f"slack_channel: {channel}")
            
            # メールドメインマッチ
            if source == "gmail":
                email = str(event.get("actor", {}).get("email", ""))
                email_domains = config.get("email_domains", [])
                for domain in email_domains:
                    if domain.lower() in email.lower():
                        confidence += 0.4
                        reasons.append(f"email_domain: {domain}")
                
                email_patterns = config.get("email_patterns", [])
                matched_patterns = self._match_keywords(email, email_patterns)
                if matched_patterns:
                    confidence += 0.3
                    reasons.append(f"email_pattern: {matched_patterns}")
            
            if confidence > 0:
                # 優先度による調整
                priority = config.get("priority", 10)
                confidence = min(1.0, confidence / priority * 5)
                results.append((project_name, confidence, "; ".join(reasons)))
        
        # 信頼度順にソート
        results.sort(key=lambda x: x[1], reverse=True)
        return results
    
    def determine_priority(self, event: Dict) -> Tuple[str, str]:
        """優先度を判定
        Returns: (priority, reason)
        """
        text = self._text_from_event(event)
        priority_rules = self.routing_rules.get("priority_rules", {})
        
        # P0チェック
        p0_rules = priority_rules.get("P0", {})
        p0_keywords = p0_rules.get("keywords", [])
        matched = self._match_keywords(text, p0_keywords)
        if matched:
            return "P0", f"keywords: {matched[:2]}"
        
        p0_patterns = p0_rules.get("subject_patterns", [])
        matched_patterns = self._match_patterns(event.get("title", ""), p0_patterns)
        if matched_patterns:
            return "P0", f"subject_pattern: {matched_patterns[0]}"
        
        # P1チェック
        p1_rules = priority_rules.get("P1", {})
        p1_keywords = p1_rules.get("keywords", [])
        matched = self._match_keywords(text, p1_keywords)
        if matched:
            return "P1", f"keywords: {matched[:2]}"
        
        p1_patterns = p1_rules.get("patterns", [])
        matched_patterns = self._match_patterns(text, p1_patterns)
        if matched_patterns:
            return "P1", f"pattern: {matched_patterns[0]}"
        
        # P2チェック
        p2_rules = priority_rules.get("P2", {})
        p2_keywords = p2_rules.get("keywords", [])
        matched = self._match_keywords(text, p2_keywords)
        if matched:
            return "P2", f"keywords: {matched[:2]}"
        
        # デフォルト: P3
        return "P3", "default"
    
    def check_no_reply(self, event: Dict) -> Tuple[bool, str]:
        """返信不要かどうかを判定"""
        text = self._text_from_event(event)
        no_reply_rules = self.routing_rules.get("no_reply_rules", {})
        
        # 送信者パターン
        email = str(event.get("actor", {}).get("email", "")).lower()
        sender_patterns = no_reply_rules.get("sender_patterns", [])
        for pattern in sender_patterns:
            if pattern.lower() in email:
                return True, f"sender: {pattern}"
        
        # キーワード
        keywords = no_reply_rules.get("keywords", [])
        matched = self._match_keywords(text, keywords)
        if matched:
            return True, f"keywords: {matched[:2]}"
        
        # 件名パターン
        subject = event.get("title", "")
        subject_patterns = no_reply_rules.get("subject_patterns", [])
        matched_patterns = self._match_patterns(subject, subject_patterns)
        if matched_patterns:
            return True, f"subject: {matched_patterns[0]}"
        
        return False, ""
    
    def check_action_required(self, event: Dict) -> Tuple[bool, str]:
        """アクション必要かどうかを判定"""
        text = self._text_from_event(event)
        action_rules = self.routing_rules.get("action_required_rules", {})
        
        # キーワード
        keywords = action_rules.get("keywords", [])
        for kw in keywords:
            pattern = self._compile_pattern(kw)
            if pattern.search(text):
                return True, f"keyword: {kw}"
        
        # オーナー宛て
        if action_rules.get("mentions_owner", False):
            people_config = self.routing_rules.get("people", {}).get("owner", {})
            owner_names = people_config.get("names", [])
            for name in owner_names:
                if name.lower() in text:
                    return True, f"mentions_owner: {name}"
        
        return False, ""
    
    def classify_sensitivity(self, event: Dict) -> Tuple[str, str]:
        """機密レベルを判定"""
        text = self._text_from_event(event)
        classification_rules = self.sensitivity_rules.get("classification_rules", {})
        
        # Restricted チェック
        restricted_rules = classification_rules.get("restricted", {})
        keywords = restricted_rules.get("keywords", [])
        matched = self._match_keywords(text, keywords)
        if matched:
            return "restricted", f"keywords: {matched[:2]}"
        
        patterns = restricted_rules.get("patterns", [])
        matched_patterns = self._match_patterns(text, patterns)
        if matched_patterns:
            return "restricted", f"pattern detected"
        
        # Confidential チェック
        confidential_rules = classification_rules.get("confidential", {})
        keywords = confidential_rules.get("keywords", [])
        matched = self._match_keywords(text, keywords)
        if matched:
            return "confidential", f"keywords: {matched[:2]}"
        
        # Public チェック
        public_rules = classification_rules.get("public", {})
        keywords = public_rules.get("keywords", [])
        matched = self._match_keywords(text, keywords)
        if matched:
            return "public", f"keywords: {matched[:2]}"
        
        # デフォルト
        source = event.get("source", "")
        defaults = self.sensitivity_rules.get("defaults", {}).get("by_source", {})
        default_level = defaults.get(source, "internal")
        return default_level, "default"
    
    def mask_pii(self, text: str) -> str:
        """PIIをマスク"""
        pii_config = self.sensitivity_rules.get("pii_detection", {})
        if not pii_config.get("enabled", True):
            return text
        
        patterns = pii_config.get("patterns", {})
        masked_text = text
        
        for pii_type, config in patterns.items():
            pattern = config.get("pattern", "")
            mask_with = config.get("mask_with", f"[{pii_type}]")
            
            try:
                compiled = self._compile_pattern(pattern)
                masked_text = compiled.sub(mask_with, masked_text)
            except:
                pass
        
        return masked_text
    
    def route(self, event: Dict) -> RoutingResult:
        """イベントを完全にルーティング"""
        result = RoutingResult()
        
        # プロジェクトルーティング
        project_results = self.route_to_projects(event)
        if project_results:
            # 信頼度0.3以上のみ採用
            result.projects = [p[0] for p in project_results if p[1] >= 0.3]
            result.match_reasons.extend([f"project:{p[0]}({p[2]})" for p in project_results[:2]])
            result.confidence = max(result.confidence, project_results[0][1] if project_results else 0.5)
        
        # 優先度判定
        priority, priority_reason = self.determine_priority(event)
        result.priority = priority
        if priority_reason != "default":
            result.match_reasons.append(f"priority:{priority}({priority_reason})")
        
        # 返信不要判定
        no_reply, no_reply_reason = self.check_no_reply(event)
        result.no_reply = no_reply
        if no_reply:
            result.match_reasons.append(f"no_reply({no_reply_reason})")
        
        # アクション必要判定
        action_required, action_reason = self.check_action_required(event)
        result.action_required = action_required and not no_reply
        if action_required and not no_reply:
            result.match_reasons.append(f"action_required({action_reason})")
        
        # 機密レベル判定
        sensitivity, sensitivity_reason = self.classify_sensitivity(event)
        result.sensitivity = sensitivity
        if sensitivity_reason != "default":
            result.match_reasons.append(f"sensitivity:{sensitivity}({sensitivity_reason})")
        
        return result


# シングルトンインスタンス
_engine: Optional[RoutingEngine] = None


def get_routing_engine() -> RoutingEngine:
    """ルーティングエンジンを取得"""
    global _engine
    if _engine is None:
        _engine = RoutingEngine()
    return _engine


def route_event(event: Dict) -> RoutingResult:
    """イベントをルーティング（便利関数）"""
    return get_routing_engine().route(event)


# テスト用
if __name__ == "__main__":
    engine = RoutingEngine()
    
    # テストイベント
    test_events = [
        {
            "source": "gmail",
            "title": "【緊急】本日中にご確認ください",
            "body": "市岡様、至急ご確認をお願いいたします。",
            "actor": {"email": "test@example.com", "name": "Test User"},
        },
        {
            "source": "slack",
            "title": "",
            "body": "AirCleの次回イベントについて相談があります",
            "actor": {"email": "", "name": "member"},
            "targets": {"channel": "1-運営からの連絡"},
        },
        {
            "source": "gmail",
            "title": "ニュースレター: 今週のお知らせ",
            "body": "配信停止はこちらから",
            "actor": {"email": "noreply@newsletter.com", "name": ""},
        },
        {
            "source": "gmail",
            "title": "契約書の送付について",
            "body": "見積書と契約書を添付いたします。",
            "actor": {"email": "sales@genspark.ai", "name": "Genspark Sales"},
        },
    ]
    
    print("=== ルーティングエンジン テスト ===\n")
    
    for i, event in enumerate(test_events, 1):
        result = engine.route(event)
        print(f"--- Event {i} ---")
        print(f"Source: {event['source']}")
        print(f"Title: {event.get('title', '')[:40]}")
        print(f"Result:")
        print(f"  Projects: {result.projects}")
        print(f"  Priority: {result.priority}")
        print(f"  Action Required: {result.action_required}")
        print(f"  No Reply: {result.no_reply}")
        print(f"  Sensitivity: {result.sensitivity}")
        print(f"  Confidence: {result.confidence:.2f}")
        print(f"  Reasons: {result.match_reasons}")
        print()
    
    print("✓ テスト完了")
