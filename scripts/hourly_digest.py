#!/usr/bin/env python3
"""
統合毎時通知スクリプト
- メール分析
- Slack/Calendar 更新
- タスク提案
- 全部まとめて1メッセージ
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional

# ライブラリパス追加
SCRIPTS_PATH = Path("/Users/ai-driven-work/Library/Mobile Documents/com~apple~CloudDocs/OpenClaw-Shared/scripts")
sys.path.insert(0, str(SCRIPTS_PATH / "lib"))

from structured_logger import get_logger

# 設定
JST = timezone(timedelta(hours=9))
VAULT_PATH = Path("/Users/ai-driven-work/Library/Mobile Documents/com~apple~CloudDocs/OpenClaw-Shared/obsidian/Ichioka Obsidian")
EVENTS_PATH = VAULT_PATH / "00_System/02_Ingest/normalized"
ACTION_QUEUE_PATH = VAULT_PATH / "00_System/04_ActionQueue"
STATE_PATH = VAULT_PATH / "00_System/01_State"

# ロガー
logger = get_logger("hourly_digest")


def load_today_events() -> List[Dict]:
    """今日のイベントを読み込む"""
    today = datetime.now(JST).strftime("%Y-%m-%d")
    events = []
    
    events_file = EVENTS_PATH / f"events_{today}.jsonl"
    if events_file.exists():
        with open(events_file, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try:
                        events.append(json.loads(line))
                    except:
                        continue
    
    return events


def load_pending_commands() -> List[Dict]:
    """承認待ちコマンドを読み込む"""
    pending_path = ACTION_QUEUE_PATH / "pending"
    commands = []
    
    if pending_path.exists():
        for f in pending_path.glob("*.json"):
            try:
                with open(f, encoding="utf-8") as fp:
                    commands.append(json.load(fp))
            except:
                continue
    
    return commands


def get_last_hour_events(events: List[Dict]) -> List[Dict]:
    """過去1時間のイベントを取得"""
    now = datetime.now(JST)
    one_hour_ago = now - timedelta(hours=1)
    
    recent = []
    for event in events:
        ingested_at = event.get("ingested_at", "")
        try:
            event_time = datetime.fromisoformat(ingested_at)
            if event_time >= one_hour_ago:
                recent.append(event)
        except:
            continue
    
    return recent


def extract_potential_tasks(events: List[Dict]) -> List[Dict]:
    """イベントからタスク候補を抽出"""
    task_keywords = [
        "やってほしい", "お願い", "確認して", "対応して",
        "返信して", "連絡して", "送って", "作って",
        "まとめて", "準備して", "調べて", "検討して",
        "TODO", "タスク", "宿題", "アクション"
    ]
    
    potential_tasks = []
    
    for event in events:
        signals = event.get("signals", {})
        
        # アクション必要なものはタスク候補
        if signals.get("action_required"):
            potential_tasks.append({
                "source": event.get("source"),
                "title": event.get("title", ""),
                "body": event.get("body", "")[:100],
                "reason": "action_required",
                "priority": signals.get("priority", "P3"),
                "event_id": event.get("event_id"),
            })
            continue
        
        # キーワードマッチ
        text = f"{event.get('title', '')} {event.get('body', '')}".lower()
        for kw in task_keywords:
            if kw in text:
                potential_tasks.append({
                    "source": event.get("source"),
                    "title": event.get("title", ""),
                    "body": event.get("body", "")[:100],
                    "reason": f"keyword: {kw}",
                    "priority": signals.get("priority", "P3"),
                    "event_id": event.get("event_id"),
                })
                break
    
    return potential_tasks


def get_today_calendar_events(events: List[Dict]) -> List[Dict]:
    """今日のカレンダーイベントを取得"""
    return [e for e in events if e.get("source") == "gcal"]


def generate_hourly_digest() -> Optional[str]:
    """毎時ダイジェストを生成"""
    now = datetime.now(JST)
    
    # データ読み込み
    all_events = load_today_events()
    recent_events = get_last_hour_events(all_events)
    pending_commands = load_pending_commands()
    potential_tasks = extract_potential_tasks(recent_events)
    calendar_events = get_today_calendar_events(all_events)
    
    # 統計
    gmail_count = len([e for e in recent_events if e.get("source") == "gmail"])
    slack_count = len([e for e in recent_events if e.get("source") == "slack"])
    p0_count = len([e for e in recent_events if e.get("signals", {}).get("priority") == "P0"])
    p1_count = len([e for e in recent_events if e.get("signals", {}).get("priority") == "P1"])
    action_required = len([e for e in recent_events if e.get("signals", {}).get("action_required")])
    
    # 何も報告することがなければNone
    if not recent_events and not pending_commands and not potential_tasks:
        return None
    
    # ダイジェスト生成
    digest = f"⏰ **{now.strftime('%H:%M')} 定期レポート**\n\n"
    
    # 新着
    if recent_events:
        digest += f"📥 **新着** (過去1時間)\n"
        digest += f"Gmail: {gmail_count} / Slack: {slack_count}\n"
        if p0_count > 0:
            digest += f"🔴 P0: {p0_count}件\n"
        if p1_count > 0:
            digest += f"🟡 P1: {p1_count}件\n"
        if action_required > 0:
            digest += f"📋 要対応: {action_required}件\n"
        digest += "\n"
    
    # タスク候補
    if potential_tasks:
        digest += f"📌 **タスク候補** ({len(potential_tasks)}件)\n"
        for task in potential_tasks[:5]:
            source = task.get("source", "")
            body = task.get("body", "")[:50]
            digest += f"- [{source}] {body}...\n"
        if len(potential_tasks) > 5:
            digest += f"  _... 他 {len(potential_tasks) - 5}件_\n"
        digest += "\n「これタスクに追加する？」と言ってくれたら追加するよ\n\n"
    
    # 承認待ち
    if pending_commands:
        digest += f"⏳ **承認待ち** ({len(pending_commands)}件)\n"
        for cmd in pending_commands[:3]:
            cmd_type = cmd.get("type", "")
            priority = cmd.get("priority", "P3")
            snippet = cmd.get("context", {}).get("snippet", "")[:40]
            digest += f"- [{priority}] {cmd_type}: {snippet}...\n"
        digest += "\n"
    
    # 今後の予定（次の3時間以内）
    if calendar_events:
        digest += f"📅 **今日の予定** ({len(calendar_events)}件)\n"
        for event in calendar_events[:5]:
            title = event.get("title", "(no title)")
            digest += f"- {title}\n"
        digest += "\n"
    
    return digest.strip()


def main():
    """メイン処理"""
    logger.info("Hourly digest started")
    
    digest = generate_hourly_digest()
    
    if digest:
        logger.info("Digest generated", data={"length": len(digest)})
        print(digest)
        return digest
    else:
        logger.info("Nothing to report")
        print("NO_REPORT")
        return None


if __name__ == "__main__":
    main()
