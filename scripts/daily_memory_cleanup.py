#!/usr/bin/env python3
"""
毎日のSync データを整理してObsidian Memoryを更新するスクリプト
23:00 JST に実行
"""

import json
import os
from pathlib import Path
from datetime import datetime, timezone, timedelta
from collections import defaultdict

# 設定
JST = timezone(timedelta(hours=9))
VAULT_PATH = Path("/Users/ai-driven-work/Library/Mobile Documents/com~apple~CloudDocs/OpenClaw-Shared/obsidian/Ichioka Obsidian")
SYNC_PATH = VAULT_PATH / "00_System/02_Ingest/normalized"
DAILY_DIGEST_PATH = VAULT_PATH / "00_System/03_Digest"

# プロジェクトキーワードマッピング
PROJECT_KEYWORDS = {
    "AirCle": ["aircle", "エアクル", "大学生ai", "ai団体"],
    "ClimbBeyond": ["climbbeyond", "クライムビヨンド", "climb beyond"],
    "SlideBox": ["slidebox", "スライドボックス"],
    "Genspark": ["genspark", "ゲンスパーク"],
    "ClientWork": ["クライアント", "案件", "受託"],
}

# いちさん関連のキーワード
OWNER_KEYWORDS = ["市岡", "いちおか", "ichioka", "直人", "naoto"]


def load_today_syncs():
    """今日のsyncファイルを全て読み込む"""
    today = datetime.now(JST).strftime("%Y-%m-%d")
    syncs = []
    
    for f in SYNC_PATH.glob(f"sync_{today}_*.json"):
        with open(f, encoding="utf-8") as fp:
            syncs.append(json.load(fp))
    
    return syncs


def extract_all_items(syncs):
    """全syncからアイテムを抽出"""
    gmail = []
    slack = []
    calendar = []
    
    seen_ids = set()
    
    for sync in syncs:
        for item in sync.get("gmail", []):
            if item.get("id") not in seen_ids:
                seen_ids.add(item.get("id"))
                gmail.append(item)
        
        for item in sync.get("slack", []):
            if item.get("id") not in seen_ids:
                seen_ids.add(item.get("id"))
                slack.append(item)
        
        for item in sync.get("calendar", []):
            if item.get("id") not in seen_ids:
                seen_ids.add(item.get("id"))
                calendar.append(item)
    
    return gmail, slack, calendar


def categorize_by_project(items):
    """アイテムをプロジェクトごとに分類"""
    categorized = defaultdict(list)
    uncategorized = []
    
    for item in items:
        text = " ".join([
            str(item.get("subject", "")),
            str(item.get("text", "")),
            str(item.get("snippet", "")),
            str(item.get("summary", "")),
            str(item.get("channel", "")),
        ]).lower()
        
        matched = False
        for project, keywords in PROJECT_KEYWORDS.items():
            if any(kw in text for kw in keywords):
                categorized[project].append(item)
                matched = True
                break
        
        if not matched:
            uncategorized.append(item)
    
    return dict(categorized), uncategorized


def extract_owner_mentions(items):
    """いちさん宛てのメッセージを抽出"""
    mentions = []
    
    for item in items:
        text = " ".join([
            str(item.get("subject", "")),
            str(item.get("text", "")),
            str(item.get("snippet", "")),
            str(item.get("from", "")),
        ]).lower()
        
        if any(kw in text for kw in OWNER_KEYWORDS):
            mentions.append(item)
    
    return mentions


def generate_daily_digest(gmail, slack, calendar, categorized, mentions):
    """Daily Digestを生成"""
    today = datetime.now(JST)
    
    digest = f"""# Daily Digest - {today.strftime("%Y-%m-%d")}

Generated at: {today.isoformat()}

## 📊 Summary

| Source | Count |
|--------|-------|
| Gmail | {len(gmail)} |
| Slack | {len(slack)} |
| Calendar | {len(calendar)} |
| **Total** | **{len(gmail) + len(slack) + len(calendar)}** |

## 📅 Today's Calendar Events

"""
    
    for evt in calendar[:10]:
        digest += f"- **{evt.get('summary', 'No title')}** @ {evt.get('start', 'TBD')}\n"
    
    if not calendar:
        digest += "_No events_\n"
    
    digest += "\n## 📧 Important Emails\n\n"
    
    important_gmail = [g for g in gmail if any(kw in str(g.get("snippet", "")).lower() for kw in OWNER_KEYWORDS)][:5]
    for mail in important_gmail:
        digest += f"- {mail.get('subject', '(no subject)')}: {mail.get('snippet', '')[:100]}...\n"
    
    if not important_gmail:
        digest += "_No important emails_\n"
    
    digest += "\n## 💬 Slack Highlights\n\n"
    
    for msg in slack[:10]:
        channel = msg.get("channel", "unknown")
        text = msg.get("text", "")[:150]
        digest += f"- **#{channel}**: {text}...\n"
    
    if not slack:
        digest += "_No Slack messages_\n"
    
    digest += "\n## 📁 By Project\n\n"
    
    for project, items in categorized.items():
        digest += f"### {project} ({len(items)} items)\n\n"
        for item in items[:3]:
            source = item.get("source", "unknown")
            text = item.get("text", item.get("snippet", item.get("summary", "")))[:100]
            digest += f"- [{source}] {text}...\n"
        digest += "\n"
    
    if not categorized:
        digest += "_No project-specific items_\n"
    
    digest += "\n## 👤 Mentions to Owner\n\n"
    
    for item in mentions[:5]:
        source = item.get("source", "unknown")
        text = item.get("text", item.get("snippet", ""))[:150]
        digest += f"- [{source}] {text}...\n"
    
    if not mentions:
        digest += "_No direct mentions_\n"
    
    return digest


def update_project_memories(categorized):
    """各プロジェクトのMEMORY.mdを更新"""
    today = datetime.now(JST).strftime("%Y-%m-%d")
    
    for project, items in categorized.items():
        memory_path = VAULT_PATH / f"03_Projects/_Active/{project}/MEMORY.md"
        
        if not memory_path.exists():
            continue
        
        # 既存の内容を読む
        with open(memory_path, encoding="utf-8") as f:
            content = f.read()
        
        # 新しいエントリを追加
        new_entry = f"\n\n## {today} Auto-captured\n\n"
        
        for item in items[:5]:  # 最大5件
            source = item.get("source", "unknown")
            text = item.get("text", item.get("snippet", item.get("summary", "")))[:200]
            new_entry += f"- [{source}] {text}\n"
        
        # ファイルに追記
        with open(memory_path, "a", encoding="utf-8") as f:
            f.write(new_entry)
        
        print(f"  Updated: {project}/MEMORY.md (+{len(items)} items)")


def save_daily_digest(digest):
    """Daily Digestを保存"""
    today = datetime.now(JST).strftime("%Y-%m-%d")
    
    DAILY_DIGEST_PATH.mkdir(parents=True, exist_ok=True)
    filepath = DAILY_DIGEST_PATH / f"digest_{today}.md"
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(digest)
    
    return filepath


def main():
    print("=== Daily Memory Cleanup ===")
    print(f"Time: {datetime.now(JST).isoformat()}")
    print()
    
    # 1. 今日のsyncを読み込み
    syncs = load_today_syncs()
    print(f"Loaded {len(syncs)} sync files")
    
    if not syncs:
        print("No sync files found for today. Exiting.")
        return
    
    # 2. アイテム抽出
    gmail, slack, calendar = extract_all_items(syncs)
    print(f"Extracted: Gmail={len(gmail)}, Slack={len(slack)}, Calendar={len(calendar)}")
    
    # 3. プロジェクト分類
    all_items = gmail + slack + calendar
    categorized, uncategorized = categorize_by_project(all_items)
    print(f"Categorized into {len(categorized)} projects, {len(uncategorized)} uncategorized")
    
    # 4. Owner mentions抽出
    mentions = extract_owner_mentions(all_items)
    print(f"Found {len(mentions)} owner mentions")
    
    # 5. Daily Digest生成
    digest = generate_daily_digest(gmail, slack, calendar, categorized, mentions)
    filepath = save_daily_digest(digest)
    print(f"Saved digest: {filepath.name}")
    
    # 6. プロジェクトメモリ更新
    print("\nUpdating project memories:")
    update_project_memories(categorized)
    
    print("\n✓ Daily memory cleanup complete!")


if __name__ == "__main__":
    main()
