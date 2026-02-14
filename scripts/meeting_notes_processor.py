#!/usr/bin/env python3
"""
議事録処理スクリプト
- 文字起こしから議事録を作成
- 参加者を照合
- タスクを抽出
- Google Tasks への追加を提案
"""

import json
import re
import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Tuple

# ライブラリパス追加
SCRIPTS_PATH = Path("/Users/ai-driven-work/Library/Mobile Documents/com~apple~CloudDocs/OpenClaw-Shared/scripts")
sys.path.insert(0, str(SCRIPTS_PATH / "lib"))

from structured_logger import get_logger

# 設定
JST = timezone(timedelta(hours=9))
VAULT_PATH = Path("/Users/ai-driven-work/Library/Mobile Documents/com~apple~CloudDocs/OpenClaw-Shared/obsidian/Ichioka Obsidian")
PEOPLE_PATH = VAULT_PATH / "10_People"
COMPANIES_PATH = VAULT_PATH / "11_Companies"
PROJECTS_PATH = VAULT_PATH / "03_Projects/_Active"

# ロガー
logger = get_logger("meeting_notes")


class MeetingNotesProcessor:
    """議事録処理クラス"""
    
    def __init__(self):
        self.people_profiles = self._load_people_profiles()
        self.company_profiles = self._load_company_profiles()
    
    def _load_people_profiles(self) -> Dict[str, Dict]:
        """人物プロファイルを読み込み"""
        profiles = {}
        if PEOPLE_PATH.exists():
            for folder in PEOPLE_PATH.iterdir():
                if folder.is_dir():
                    profile_path = folder / "PROFILE.md"
                    if profile_path.exists():
                        profiles[folder.name] = {
                            "name": folder.name,
                            "path": str(profile_path),
                        }
        return profiles
    
    def _load_company_profiles(self) -> Dict[str, Dict]:
        """企業プロファイルを読み込み"""
        profiles = {}
        if COMPANIES_PATH.exists():
            for folder in COMPANIES_PATH.iterdir():
                if folder.is_dir():
                    profile_path = folder / "PROFILE.md"
                    if profile_path.exists():
                        profiles[folder.name] = {
                            "name": folder.name,
                            "path": str(profile_path),
                        }
        return profiles
    
    def identify_participants(self, transcript: str) -> Tuple[List[str], List[str], List[str]]:
        """
        参加者を特定
        Returns: (known_people, known_companies, unknown_names)
        """
        known_people = []
        known_companies = []
        unknown_names = []
        
        # 名前パターンを抽出
        name_patterns = [
            r"([一-龯]{2,4})(?:さん|様|氏)",  # 日本語名
            r"([A-Z][a-z]+(?:\s[A-Z][a-z]+)?)",  # 英語名
        ]
        
        found_names = set()
        for pattern in name_patterns:
            matches = re.findall(pattern, transcript)
            found_names.update(matches)
        
        # 既知の人物と照合
        for name in found_names:
            if name in self.people_profiles:
                known_people.append(name)
            else:
                # 部分マッチ
                matched = False
                for known_name in self.people_profiles:
                    if name in known_name or known_name in name:
                        known_people.append(known_name)
                        matched = True
                        break
                if not matched:
                    unknown_names.append(name)
        
        # 企業名を抽出
        for company_name in self.company_profiles:
            if company_name in transcript:
                known_companies.append(company_name)
        
        return known_people, known_companies, unknown_names
    
    def extract_action_items(self, transcript: str) -> List[Dict]:
        """アクションアイテム（タスク）を抽出"""
        action_items = []
        
        # タスクパターン
        patterns = [
            (r"TODO[：:]\s*(.+?)(?:\n|$)", "TODO"),
            (r"タスク[：:]\s*(.+?)(?:\n|$)", "タスク"),
            (r"やること[：:]\s*(.+?)(?:\n|$)", "やること"),
            (r"アクション[：:]\s*(.+?)(?:\n|$)", "アクション"),
            (r"宿題[：:]\s*(.+?)(?:\n|$)", "宿題"),
            (r"次回まで[にに]\s*(.+?)(?:\n|$)", "次回まで"),
            (r"(.+?)(?:する|やる|対応する)(?:こと|必要)", "要対応"),
            (r"(.+?)をお願い", "依頼"),
        ]
        
        for pattern, source in patterns:
            matches = re.findall(pattern, transcript, re.IGNORECASE)
            for match in matches:
                if len(match) > 5 and len(match) < 200:  # 妥当な長さ
                    action_items.append({
                        "title": match.strip(),
                        "source": source,
                        "assignee": None,  # 後で特定
                        "due_date": None,
                    })
        
        return action_items
    
    def extract_decisions(self, transcript: str) -> List[str]:
        """決定事項を抽出"""
        decisions = []
        
        patterns = [
            r"決定[：:]\s*(.+?)(?:\n|$)",
            r"決まったこと[：:]\s*(.+?)(?:\n|$)",
            r"(?:ということで|結論として)[、,]\s*(.+?)(?:\n|$)",
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, transcript, re.IGNORECASE)
            decisions.extend([m.strip() for m in matches if len(m) > 5])
        
        return decisions
    
    def extract_next_meeting(self, transcript: str) -> Optional[str]:
        """次回予定を抽出"""
        patterns = [
            r"次回[はの]?\s*(.+?)(?:に|で)(?:行|開催|実施)",
            r"次のミーティング[はの]?\s*(.+)",
            r"(\d{1,2}月\d{1,2}日).+?(?:次回|ミーティング|MTG)",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, transcript)
            if match:
                return match.group(1).strip()
        
        return None
    
    def generate_meeting_notes(
        self,
        transcript: str,
        meeting_title: str = "",
        meeting_date: Optional[str] = None,
    ) -> Dict:
        """議事録を生成"""
        if meeting_date is None:
            meeting_date = datetime.now(JST).strftime("%Y-%m-%d")
        
        # 参加者特定
        known_people, known_companies, unknown_names = self.identify_participants(transcript)
        
        # アクションアイテム抽出
        action_items = self.extract_action_items(transcript)
        
        # 決定事項抽出
        decisions = self.extract_decisions(transcript)
        
        # 次回予定抽出
        next_meeting = self.extract_next_meeting(transcript)
        
        # 議事録構造
        notes = {
            "title": meeting_title or f"Meeting Notes {meeting_date}",
            "date": meeting_date,
            "participants": {
                "known_people": known_people,
                "known_companies": known_companies,
                "unknown": unknown_names,
            },
            "summary": "",  # 要約は別途生成
            "decisions": decisions,
            "action_items": action_items,
            "next_meeting": next_meeting,
            "raw_transcript": transcript[:500] + "..." if len(transcript) > 500 else transcript,
        }
        
        logger.info("Meeting notes generated", data={
            "title": notes["title"],
            "participants": len(known_people) + len(unknown_names),
            "action_items": len(action_items),
            "decisions": len(decisions),
        })
        
        return notes
    
    def format_as_markdown(self, notes: Dict) -> str:
        """Markdown形式にフォーマット"""
        md = f"""# {notes['title']}

**日付:** {notes['date']}

---

## 参加者

"""
        
        if notes['participants']['known_people']:
            md += "### 既知\n"
            for person in notes['participants']['known_people']:
                md += f"- [[{person}]]\n"
        
        if notes['participants']['known_companies']:
            md += "\n### 企業\n"
            for company in notes['participants']['known_companies']:
                md += f"- [[{company}]]\n"
        
        if notes['participants']['unknown']:
            md += "\n### 未登録（要確認）\n"
            for name in notes['participants']['unknown']:
                md += f"- {name}\n"
        
        md += "\n---\n\n## 要約\n\n_要約をここに記入_\n\n"
        
        md += "---\n\n## 決定事項\n\n"
        if notes['decisions']:
            for decision in notes['decisions']:
                md += f"- {decision}\n"
        else:
            md += "_なし_\n"
        
        md += "\n---\n\n## TODO / アクションアイテム\n\n"
        if notes['action_items']:
            for item in notes['action_items']:
                md += f"- [ ] {item['title']}\n"
        else:
            md += "_なし_\n"
        
        if notes['next_meeting']:
            md += f"\n---\n\n## 次回予定\n\n{notes['next_meeting']}\n"
        
        md += f"""

---

> Generated: {datetime.now(JST).isoformat()}
"""
        
        return md
    
    def determine_save_location(self, notes: Dict) -> Path:
        """保存先を決定"""
        # 企業が特定されていればそこに
        if notes['participants']['known_companies']:
            company = notes['participants']['known_companies'][0]
            return COMPANIES_PATH / company / f"MTG_{notes['date']}.md"
        
        # 人物が特定されていればプロジェクトを推測
        # デフォルトはプロジェクトフォルダ
        return PROJECTS_PATH / f"MTG_{notes['date']}_{notes['title'][:20]}.md"


def process_transcript(transcript: str, title: str = "") -> Dict:
    """文字起こしを処理して議事録を生成"""
    processor = MeetingNotesProcessor()
    notes = processor.generate_meeting_notes(transcript, title)
    
    return {
        "notes": notes,
        "markdown": processor.format_as_markdown(notes),
        "save_path": str(processor.determine_save_location(notes)),
        "needs_confirmation": {
            "unknown_participants": notes['participants']['unknown'],
            "action_items_to_add": notes['action_items'],
        }
    }


def main():
    """テスト用"""
    test_transcript = """
    今日は市岡さんとGenspark社の田中さんとミーティングしました。
    
    決定事項:
    - 来週からプロジェクト開始
    - 週次でミーティング実施
    
    TODO: 契約書の確認
    タスク: 見積もりの作成
    
    次回は2月10日に行います。
    """
    
    result = process_transcript(test_transcript, "Genspark キックオフ")
    
    print("=== 議事録処理結果 ===\n")
    print(f"保存先: {result['save_path']}\n")
    print("--- Markdown ---")
    print(result['markdown'])
    
    if result['needs_confirmation']['action_items_to_add']:
        print("\n--- タスク追加候補 ---")
        for item in result['needs_confirmation']['action_items_to_add']:
            print(f"  - {item['title']}")


if __name__ == "__main__":
    main()
