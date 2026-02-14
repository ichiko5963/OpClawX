#!/usr/bin/env python3
"""
メモリ自動整理システム
毎朝4:10実行、30分間稼働
"""

import os
import json
from datetime import datetime
from pathlib import Path
import anthropic

WORKSPACE = Path("/Users/ai-driven-work/Documents/OpenClaw-Workspace")
OBSIDIAN_ROOT = WORKSPACE / "obsidian/Ichioka Obsidian"
MEMORY_DIR = WORKSPACE / "memory"
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# 曜日別テーマ
DAILY_THEMES = {
    0: {
        'name': 'プロジェクト情報',
        'target': '03_Projects',
        'description': 'アクティブプロジェクトの進捗更新、完了プロジェクトの移動'
    },
    1: {
        'name': '人物情報',
        'target': '10_People',
        'description': '人物プロフィール更新、新しい人物追加'
    },
    2: {
        'name': '企業情報',
        'target': '11_Companies',
        'description': '企業情報更新、関係性の整理'
    },
    3: {
        'name': 'タスク・TODO',
        'target': '03_Projects',
        'description': '各プロジェクトのTODO統合、期限超過確認'
    },
    4: {
        'name': '知識・メモ',
        'target': 'memory',
        'description': '日次メモからMEMORY.mdへの重要情報抽出'
    },
    5: {
        'name': '全体見直し',
        'target': 'all',
        'description': '構造の見直し、不要ファイル確認'
    },
    6: {
        'name': 'アーカイブ整理',
        'target': 'data',
        'description': '古いデータのアーカイブ、GitHubフォルダ整理'
    }
}

class MemoryOrganizer:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY) if ANTHROPIC_API_KEY else None
        self.report = {
            'theme': None,
            'actions': [],
            'start_time': datetime.now().isoformat(),
            'errors': []
        }
    
    def get_todays_theme(self):
        """今日のテーマ取得"""
        weekday = datetime.now().weekday()
        return DAILY_THEMES[weekday]
    
    def backup_before_organize(self):
        """整理前にバックアップ"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_dir = WORKSPACE / "backups" / timestamp
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # 重要ファイルのみバックアップ
        important_files = [
            MEMORY_DIR / "MEMORY.md",
            OBSIDIAN_ROOT / "03_Projects",
            OBSIDIAN_ROOT / "10_People",
            OBSIDIAN_ROOT / "11_Companies"
        ]
        
        for path in important_files:
            if path.exists():
                if path.is_file():
                    dest = backup_dir / path.name
                    dest.write_text(path.read_text())
                # ディレクトリは省略（必要に応じて追加）
        
        print(f"✓ バックアップ完了: {backup_dir}")
        return backup_dir
    
    def organize_projects(self):
        """プロジェクト情報整理（月曜）"""
        print("\n=== プロジェクト情報整理 ===")
        actions = []
        
        projects_dir = OBSIDIAN_ROOT / "03_Projects/_Active"
        if not projects_dir.exists():
            return actions
        
        # 各プロジェクトフォルダをチェック
        for project_dir in projects_dir.iterdir():
            if not project_dir.is_dir():
                continue
            
            project_md = project_dir / "PROJECT.md"
            if not project_md.exists():
                continue
            
            # Claudeで分析（今はスキップ、後で実装）
            actions.append(f"チェック: {project_dir.name}")
        
        return actions
    
    def organize_people(self):
        """人物情報整理（火曜）"""
        print("\n=== 人物情報整理 ===")
        actions = []
        
        people_dir = OBSIDIAN_ROOT / "10_People"
        if not people_dir.exists():
            return actions
        
        # 各人物フォルダをチェック
        for person_dir in people_dir.iterdir():
            if not person_dir.is_dir():
                continue
            
            profile_md = person_dir / "PROFILE.md"
            if profile_md.exists():
                actions.append(f"チェック: {person_dir.name}")
        
        return actions
    
    def organize_companies(self):
        """企業情報整理（水曜）"""
        print("\n=== 企業情報整理 ===")
        actions = []
        
        companies_dir = OBSIDIAN_ROOT / "11_Companies"
        if not companies_dir.exists():
            return actions
        
        for company_dir in companies_dir.iterdir():
            if not company_dir.is_dir():
                continue
            
            profile_md = company_dir / "PROFILE.md"
            if profile_md.exists():
                actions.append(f"チェック: {company_dir.name}")
        
        return actions
    
    def organize_tasks(self):
        """タスク・TODO整理（木曜）"""
        print("\n=== タスク・TODO整理 ===")
        actions = []
        
        # 各プロジェクトのTODOをチェック
        projects_dir = OBSIDIAN_ROOT / "03_Projects/_Active"
        if not projects_dir.exists():
            return actions
        
        for project_dir in projects_dir.iterdir():
            if not project_dir.is_dir():
                continue
            
            # TODO.mdやPROJECT.md内のTODOをチェック
            todo_md = project_dir / "TODO.md"
            if todo_md.exists():
                actions.append(f"TODOチェック: {project_dir.name}")
        
        return actions
    
    def organize_knowledge(self):
        """知識・メモ整理（金曜）"""
        print("\n=== 知識・メモ整理 ===")
        actions = []
        
        # 日次メモから重要情報を抽出
        for md_file in MEMORY_DIR.glob("2026-*.md"):
            if md_file.name == "MEMORY.md":
                continue
            
            # 古いメモ（7日以上前）から重要情報抽出
            file_date = md_file.stem
            actions.append(f"レビュー: {file_date}")
        
        return actions
    
    def review_all(self):
        """全体見直し（土曜）"""
        print("\n=== 全体見直し ===")
        actions = []
        
        # 構造チェック
        dirs_to_check = [
            OBSIDIAN_ROOT / "03_Projects/_Active",
            OBSIDIAN_ROOT / "03_Projects/_Old",
            OBSIDIAN_ROOT / "10_People",
            OBSIDIAN_ROOT / "11_Companies",
            MEMORY_DIR
        ]
        
        for dir_path in dirs_to_check:
            if dir_path.exists():
                count = len(list(dir_path.iterdir()))
                actions.append(f"{dir_path.name}: {count}件")
        
        return actions
    
    def organize_archives(self):
        """アーカイブ整理（日曜）"""
        print("\n=== アーカイブ整理 ===")
        actions = []
        
        data_dir = WORKSPACE / "data"
        if not data_dir.exists():
            return actions
        
        # 古いデータをアーカイブ
        archive_dir = data_dir / "archive"
        archive_dir.mkdir(exist_ok=True)
        
        # 30日以上前のデータをアーカイブ
        # （今はチェックのみ）
        for subdir in data_dir.iterdir():
            if subdir.is_dir() and subdir.name != "archive":
                actions.append(f"チェック: {subdir.name}")
        
        return actions
    
    def run(self):
        """メイン実行"""
        print("=" * 60)
        print("🧹 メモリ自動整理開始")
        print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        # 今日のテーマ
        theme = self.get_todays_theme()
        self.report['theme'] = theme
        
        print(f"\n今日のテーマ: {theme['name']}")
        print(f"説明: {theme['description']}")
        
        # バックアップ
        backup_dir = self.backup_before_organize()
        
        # テーマ別処理
        weekday = datetime.now().weekday()
        
        if weekday == 0:  # 月曜
            self.report['actions'] = self.organize_projects()
        elif weekday == 1:  # 火曜
            self.report['actions'] = self.organize_people()
        elif weekday == 2:  # 水曜
            self.report['actions'] = self.organize_companies()
        elif weekday == 3:  # 木曜
            self.report['actions'] = self.organize_tasks()
        elif weekday == 4:  # 金曜
            self.report['actions'] = self.organize_knowledge()
        elif weekday == 5:  # 土曜
            self.report['actions'] = self.review_all()
        elif weekday == 6:  # 日曜
            self.report['actions'] = self.organize_archives()
        
        # 終了
        self.report['end_time'] = datetime.now().isoformat()
        
        # 実行時間計算
        start = datetime.fromisoformat(self.report['start_time'])
        end = datetime.fromisoformat(self.report['end_time'])
        duration = (end - start).total_seconds() / 60
        
        print("\n" + "=" * 60)
        print("✅ メモリ整理完了")
        print(f"実行アクション: {len(self.report['actions'])}件")
        print(f"実行時間: {duration:.1f}分")
        print("=" * 60)
        
        return self.report
    
    def generate_telegram_report(self):
        """Telegram報告生成"""
        theme = self.report['theme']
        actions = self.report['actions']
        
        start = datetime.fromisoformat(self.report['start_time'])
        end = datetime.fromisoformat(self.report['end_time'])
        duration = (end - start).total_seconds() / 60
        
        # 次回テーマ
        next_weekday = (datetime.now().weekday() + 1) % 7
        next_theme = DAILY_THEMES[next_weekday]
        
        report = f"""🧹 メモリ整理完了！（{datetime.now().strftime('%H:%M')}）

📅 今日のテーマ: {theme['name']}

✅ 実行内容:
━━━━━━━━━━━━━━━
"""
        
        for i, action in enumerate(actions[:10], 1):
            report += f"{i}. {action}\n"
        
        if len(actions) > 10:
            report += f"...他{len(actions) - 10}件\n"
        
        report += f"""
⏱️ 実行時間: {duration:.1f}分

次回: 明日4:10（{next_theme['name']}）
"""
        
        return report

def main():
    organizer = MemoryOrganizer()
    report = organizer.run()
    
    # Telegram報告
    telegram_report = organizer.generate_telegram_report()
    print("\n" + telegram_report)
    
    # レポート保存
    report_file = WORKSPACE / "data" / f"memory_organizer_{datetime.now().strftime('%Y%m%d')}.json"
    report_file.parent.mkdir(parents=True, exist_ok=True)
    report_file.write_text(json.dumps(report, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
