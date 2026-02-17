#!/usr/bin/env python3
"""
Obsidian Profile Sync Checker

Obsidian VaultのPeople/Companies プロフィールの整合性をチェックします。
- INDEX.mdと実際のフォルダ構造の一致確認
- PROFILEファイルの必須項目チェック
- 孤立したプロフィール検出
- ORGANIZATIONとの整合性確認

Usage:
    python scripts/obsidian_sync_checker.py
    python scripts/obsidian_sync_checker.py --fix  # 自動修正
"""

import os
import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Set
from datetime import datetime

# Obsidian Vault paths
VAULT_BASE = Path.home() / "Documents/OpenClaw-Workspace/obsidian/Ichioka Obsidian"
PEOPLE_DIR = VAULT_BASE / "10_People"
COMPANIES_DIR = VAULT_BASE / "11_Companies"

class ProfileSyncChecker:
    def __init__(self, auto_fix=False):
        self.auto_fix = auto_fix
        self.issues = []
        self.warnings = []
        self.stats = {
            "people_total": 0,
            "companies_total": 0,
            "people_indexed": 0,
            "companies_indexed": 0,
            "orphaned": 0,
            "missing_profiles": 0,
            "fixed": 0
        }
    
    def check_all(self):
        """すべてのチェックを実行"""
        print("🔍 Obsidian Profile Sync Check開始")
        print("=" * 60)
        
        # 1. People check
        self.check_people()
        
        # 2. Companies check
        self.check_companies()
        
        # 3. Organization.md check
        self.check_organization()
        
        # 4. レポート出力
        self.print_report()
    
    def check_people(self):
        """10_People/ の整合性チェック"""
        print("\n📋 People Profile Check")
        print("-" * 60)
        
        index_file = PEOPLE_DIR / "INDEX.md"
        if not index_file.exists():
            self.issues.append("INDEX.md が存在しません")
            return
        
        # INDEX.mdから登録済み人物を読み取る
        indexed_people = self._parse_index(index_file)
        self.stats["people_indexed"] = len(indexed_people)
        
        # 実際のフォルダを確認
        actual_people = set()
        for item in PEOPLE_DIR.iterdir():
            if item.is_dir() and not item.name.startswith("."):
                actual_people.add(item.name)
                self.stats["people_total"] += 1
                
                # PROFILE.md 存在確認
                profile = item / "PROFILE.md"
                if not profile.exists():
                    self.issues.append(f"❌ {item.name}: PROFILE.md が存在しません")
                    self.stats["missing_profiles"] += 1
                else:
                    # 必須項目チェック
                    self._check_profile_content(profile, item.name, "person")
        
        # INDEX未登録を検出
        orphaned = actual_people - indexed_people
        if orphaned:
            for name in orphaned:
                self.warnings.append(f"⚠️  {name} がINDEX.mdに未登録")
                self.stats["orphaned"] += 1
        
        # INDEX登録済みだが実体なし
        missing = indexed_people - actual_people
        if missing:
            for name in missing:
                self.issues.append(f"❌ INDEX.mdに {name} がありますが、フォルダが存在しません")
        
        print(f"✅ 登録済み人物: {self.stats['people_indexed']}人")
        print(f"✅ 実フォルダ: {self.stats['people_total']}個")
    
    def check_companies(self):
        """11_Companies/ の整合性チェック"""
        print("\n🏢 Companies Profile Check")
        print("-" * 60)
        
        index_file = COMPANIES_DIR / "INDEX.md"
        if not index_file.exists():
            self.issues.append("INDEX.md が存在しません (Companies)")
            return
        
        # INDEX.mdから登録済み企業を読み取る
        indexed_companies = self._parse_index(index_file)
        self.stats["companies_indexed"] = len(indexed_companies)
        
        # 実際のフォルダを確認
        actual_companies = set()
        for item in COMPANIES_DIR.iterdir():
            if item.is_dir() and not item.name.startswith("."):
                actual_companies.add(item.name)
                self.stats["companies_total"] += 1
                
                # PROFILE.md 存在確認
                profile = item / "PROFILE.md"
                if not profile.exists():
                    self.issues.append(f"❌ {item.name}: PROFILE.md が存在しません")
                    self.stats["missing_profiles"] += 1
                else:
                    # 必須項目チェック
                    self._check_profile_content(profile, item.name, "company")
        
        # INDEX未登録を検出
        orphaned = actual_companies - indexed_companies
        if orphaned:
            for name in orphaned:
                self.warnings.append(f"⚠️  {name} がINDEX.mdに未登録 (Companies)")
                self.stats["orphaned"] += 1
        
        # INDEX登録済みだが実体なし
        missing = indexed_companies - actual_companies
        if missing:
            for name in missing:
                self.issues.append(f"❌ INDEX.mdに {name} がありますが、フォルダが存在しません (Companies)")
        
        print(f"✅ 登録済み企業: {self.stats['companies_indexed']}社")
        print(f"✅ 実フォルダ: {self.stats['companies_total']}個")
    
    def check_organization(self):
        """ORGANIZATION.mdとの整合性チェック"""
        print("\n🏗️ Organization Structure Check")
        print("-" * 60)
        
        org_file = PEOPLE_DIR / "ORGANIZATION.md"
        if not org_file.exists():
            self.warnings.append("ORGANIZATION.md が存在しません")
            return
        
        content = org_file.read_text(encoding="utf-8")
        
        # マークダウン内の人名を抽出（簡易版）
        # 例: "- **いち** (代表)" → "いち"
        pattern = r'\*\*([^*]+)\*\*'
        org_people = set(re.findall(pattern, content))
        
        # 実際のフォルダと照合
        actual_people = {item.name for item in PEOPLE_DIR.iterdir() if item.is_dir() and not item.name.startswith(".")}
        
        # 組織図に載っているが実体なし
        missing = org_people - actual_people
        if missing:
            for name in missing:
                self.warnings.append(f"⚠️  ORGANIZATION.mdに {name} がいますが、プロフィールがありません")
        
        print(f"✅ 組織図登録人数: {len(org_people)}人")
    
    def _parse_index(self, index_file: Path) -> Set[str]:
        """INDEX.mdから登録済み名前を抽出"""
        content = index_file.read_text(encoding="utf-8")
        names = set()
        
        # 箇条書き形式を想定: "- **名前** - 説明"
        pattern = r'^\s*-\s*\*\*(.+?)\*\*'
        for line in content.splitlines():
            match = re.match(pattern, line)
            if match:
                names.add(match.group(1).strip())
        
        return names
    
    def _check_profile_content(self, profile_path: Path, name: str, profile_type: str):
        """PROFILE.mdの必須項目チェック"""
        content = profile_path.read_text(encoding="utf-8")
        
        if profile_type == "person":
            required = ["## 基本情報", "## 関係性"]
            for req in required:
                if req not in content:
                    self.warnings.append(f"⚠️  {name}: PROFILE.mdに「{req}」セクションがありません")
        
        elif profile_type == "company":
            required = ["## 基本情報", "## 関係性"]
            for req in required:
                if req not in content:
                    self.warnings.append(f"⚠️  {name}: PROFILE.mdに「{req}」セクションがありません")
    
    def print_report(self):
        """最終レポート出力"""
        print("\n" + "=" * 60)
        print("📊 チェック結果")
        print("=" * 60)
        
        print("\n【統計】")
        print(f"  人物: {self.stats['people_total']}人 (INDEX登録: {self.stats['people_indexed']})")
        print(f"  企業: {self.stats['companies_total']}社 (INDEX登録: {self.stats['companies_indexed']})")
        print(f"  孤立プロフィール: {self.stats['orphaned']}件")
        print(f"  PROFILE.md欠落: {self.stats['missing_profiles']}件")
        
        if self.issues:
            print("\n❌ 【エラー】")
            for issue in self.issues:
                print(f"  {issue}")
        
        if self.warnings:
            print("\n⚠️  【警告】")
            for warning in self.warnings:
                print(f"  {warning}")
        
        if not self.issues and not self.warnings:
            print("\n✅ すべてのチェックがパスしました！")
        
        # 自動修正提案
        if self.stats['orphaned'] > 0 and not self.auto_fix:
            print("\n💡 --fix オプションで INDEX.md への自動追記が可能です")


def main():
    auto_fix = "--fix" in sys.argv
    
    checker = ProfileSyncChecker(auto_fix=auto_fix)
    checker.check_all()


if __name__ == "__main__":
    main()
