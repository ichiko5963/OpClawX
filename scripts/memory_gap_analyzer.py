#!/usr/bin/env python3
"""
Memory Gap Analyzer

memory/*.md の日次ログと MEMORY.md の長期記憶のギャップを分析します。
- 記憶の重複検出
- 長期化すべき情報の提案
- 古い情報の削除提案

Usage:
    python scripts/memory_gap_analyzer.py
    python scripts/memory_gap_analyzer.py --days 7  # 過去7日分のみ分析
"""

import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
import re

WORKSPACE = Path.home() / "Documents/OpenClaw-Workspace"
MEMORY_DIR = WORKSPACE / "memory"
MEMORY_MD = WORKSPACE / "MEMORY.md"

class MemoryGapAnalyzer:
    def __init__(self, days=30):
        self.days = days
        self.daily_entries = []
        self.long_term_memory = ""
        self.findings = {
            "duplicates": [],
            "candidates_for_longterm": [],
            "stale_info": [],
            "coverage_gaps": []
        }
    
    def analyze(self):
        """分析実行"""
        print("🧠 Memory Gap Analysis")
        print("=" * 60)
        
        # 1. データ読み込み
        self._load_daily_memories()
        self._load_longterm_memory()
        
        # 2. 分析実行
        self._detect_duplicates()
        self._find_longterm_candidates()
        self._detect_stale_info()
        
        # 3. レポート出力
        self._print_report()
    
    def _load_daily_memories(self):
        """過去N日分のmemory/*.mdを読み込む"""
        print(f"📂 Loading daily memories (past {self.days} days)...")
        
        cutoff_date = datetime.now() - timedelta(days=self.days)
        
        for file in sorted(MEMORY_DIR.glob("*.md")):
            # ファイル名から日付抽出 (YYYY-MM-DD.md)
            match = re.match(r'(\d{4}-\d{2}-\d{2})\.md', file.name)
            if not match:
                continue
            
            file_date = datetime.strptime(match.group(1), "%Y-%m-%d")
            if file_date < cutoff_date:
                continue
            
            content = file.read_text(encoding="utf-8")
            self.daily_entries.append({
                "date": file_date,
                "file": file.name,
                "content": content
            })
        
        print(f"✅ Loaded {len(self.daily_entries)} daily files")
    
    def _load_longterm_memory(self):
        """MEMORY.mdを読み込む"""
        if MEMORY_MD.exists():
            self.long_term_memory = MEMORY_MD.read_text(encoding="utf-8")
            print(f"✅ Loaded MEMORY.md ({len(self.long_term_memory)} chars)")
        else:
            print("⚠️  MEMORY.md not found")
    
    def _detect_duplicates(self):
        """重複情報検出"""
        print("\n🔎 Detecting duplicates...")
        
        # MEMORY.mdのセクションをキーワードで抽出
        memory_keywords = self._extract_keywords(self.long_term_memory)
        
        for entry in self.daily_entries:
            daily_keywords = self._extract_keywords(entry["content"])
            
            # 重複キーワード検出（シンプルに50文字以上一致）
            for kw in daily_keywords:
                if len(kw) > 50 and kw in memory_keywords:
                    self.findings["duplicates"].append({
                        "date": entry["date"],
                        "keyword": kw[:60] + "...",
                        "file": entry["file"]
                    })
    
    def _find_longterm_candidates(self):
        """長期記憶候補の検出"""
        print("🎯 Finding candidates for long-term memory...")
        
        # 複数回言及されているトピックを検出
        topic_mentions = defaultdict(list)
        
        for entry in self.daily_entries:
            # プロジェクト名、人物名、重要キーワードを抽出
            projects = re.findall(r'\*\*([A-Z][a-zA-Z]+)\*\*', entry["content"])
            people = re.findall(r'([ぁ-ん]{2,}|[ァ-ヴ]{2,})', entry["content"])
            
            for topic in set(projects + people):
                if len(topic) >= 2:
                    topic_mentions[topic].append(entry["date"])
        
        # 3回以上言及されているトピックを候補に
        for topic, dates in topic_mentions.items():
            if len(dates) >= 3 and topic not in self.long_term_memory:
                self.findings["candidates_for_longterm"].append({
                    "topic": topic,
                    "mentions": len(dates),
                    "first_date": min(dates),
                    "last_date": max(dates)
                })
    
    def _detect_stale_info(self):
        """古い情報検出（60日以上前の記述）"""
        print("🕰️ Detecting stale information...")
        
        # MEMORY.mdから日付を含む行を抽出
        date_pattern = r'(\d{4}-\d{2}-\d{2})'
        for line in self.long_term_memory.splitlines():
            match = re.search(date_pattern, line)
            if match:
                date_str = match.group(1)
                try:
                    date = datetime.strptime(date_str, "%Y-%m-%d")
                    days_old = (datetime.now() - date).days
                    
                    if days_old > 60:
                        self.findings["stale_info"].append({
                            "line": line.strip(),
                            "days_old": days_old
                        })
                except ValueError:
                    pass
    
    def _extract_keywords(self, text: str) -> set:
        """文書からキーワード抽出（簡易版）"""
        # 箇条書き項目、太字テキストを抽出
        items = set()
        
        # 箇条書き
        for line in text.splitlines():
            if line.strip().startswith("-") or line.strip().startswith("*"):
                items.add(line.strip())
        
        # 太字
        bold_items = re.findall(r'\*\*(.+?)\*\*', text)
        items.update(bold_items)
        
        return items
    
    def _print_report(self):
        """分析レポート出力"""
        print("\n" + "=" * 60)
        print("📊 Analysis Report")
        print("=" * 60)
        
        # 重複
        if self.findings["duplicates"]:
            print(f"\n🔁 重複情報 ({len(self.findings['duplicates'])}件)")
            print("MEMORY.mdと重複している日次記録:")
            for dup in self.findings["duplicates"][:5]:
                print(f"  📅 {dup['date'].strftime('%Y-%m-%d')}: {dup['keyword']}")
            if len(self.findings["duplicates"]) > 5:
                print(f"  ... and {len(self.findings['duplicates']) - 5} more")
        
        # 長期記憶候補
        if self.findings["candidates_for_longterm"]:
            print(f"\n⭐ 長期記憶候補 ({len(self.findings['candidates_for_longterm'])}件)")
            print("複数回言及されているが、MEMORY.mdに未記載:")
            sorted_candidates = sorted(self.findings["candidates_for_longterm"], 
                                      key=lambda x: x["mentions"], reverse=True)
            for cand in sorted_candidates[:10]:
                print(f"  📌 {cand['topic']}: {cand['mentions']}回言及 "
                      f"({cand['first_date'].strftime('%m/%d')} 〜 {cand['last_date'].strftime('%m/%d')})")
        
        # 古い情報
        if self.findings["stale_info"]:
            print(f"\n🕰️ 古い情報 ({len(self.findings['stale_info'])}件)")
            print("60日以上前の記述（見直しの候補）:")
            for stale in sorted(self.findings["stale_info"], 
                              key=lambda x: x["days_old"], reverse=True)[:5]:
                print(f"  🗓️  {stale['days_old']}日前: {stale['line'][:70]}...")
        
        # サマリー
        print("\n" + "=" * 60)
        print("💡 推奨アクション:")
        if self.findings["candidates_for_longterm"]:
            print(f"  1. {len(self.findings['candidates_for_longterm'])}件の長期記憶候補をMEMORY.mdに追加")
        if self.findings["stale_info"]:
            print(f"  2. {len(self.findings['stale_info'])}件の古い情報を見直し")
        if self.findings["duplicates"]:
            print(f"  3. {len(self.findings['duplicates'])}件の重複を整理")
        
        if not any(self.findings.values()):
            print("✅ メモリ管理は良好です！")


def main():
    days = 30
    if "--days" in sys.argv:
        idx = sys.argv.index("--days")
        if idx + 1 < len(sys.argv):
            days = int(sys.argv[idx + 1])
    
    analyzer = MemoryGapAnalyzer(days=days)
    analyzer.analyze()


if __name__ == "__main__":
    main()
