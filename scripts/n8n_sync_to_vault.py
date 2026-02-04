#!/usr/bin/env python3
"""
n8n実行結果をObsidian Vaultに保存するスクリプト（v2）
- 構造化ログ
- ルーティングエンジン統合
- 機密判定
"""

import json
import sqlite3
import urllib.request
import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Tuple, Optional

# ライブラリパス追加
SCRIPTS_PATH = Path("/Users/ai-driven-work/Library/Mobile Documents/com~apple~CloudDocs/OpenClaw-Shared/scripts")
sys.path.insert(0, str(SCRIPTS_PATH / "lib"))

from structured_logger import get_logger, log_ingest_event
from routing_engine import get_routing_engine, route_event

# 設定
N8N_URL = "http://localhost:5678"
WORKFLOW_ID = "88rZ4qDhYvrct3Nl"
VAULT_PATH = Path("/Users/ai-driven-work/Library/Mobile Documents/com~apple~CloudDocs/OpenClaw-Shared/obsidian/Ichioka Obsidian")
STATE_PATH = VAULT_PATH / "00_System/01_State"
SYNC_PATH = VAULT_PATH / "00_System/02_Ingest/normalized"
JST = timezone(timedelta(hours=9))

# ロガー
logger = get_logger("ingest")


def get_api_key() -> Optional[str]:
    """APIキーを取得"""
    env_file = Path.home() / ".config/openclaw/secrets/n8n.env"
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                if line.startswith("N8N_API_KEY="):
                    return line.strip().split("=", 1)[1]
    return None


def get_latest_execution_id(api_key: str) -> Optional[str]:
    """最新の成功した実行IDを取得"""
    url = f"{N8N_URL}/api/v1/executions?limit=1&status=success&workflowId={WORKFLOW_ID}"
    req = urllib.request.Request(url, headers={"X-N8N-API-KEY": api_key})
    with urllib.request.urlopen(req) as resp:
        data = json.load(resp)
        if data.get("data"):
            return data["data"][0]["id"]
    return None


def get_execution_data(api_key: str, exec_id: str) -> Tuple[List, List, List, List]:
    """実行データを取得してマージ"""
    url = f"{N8N_URL}/api/v1/executions/{exec_id}?includeData=true"
    req = urllib.request.Request(url, headers={"X-N8N-API-KEY": api_key})
    with urllib.request.urlopen(req) as resp:
        d = json.load(resp)
    
    run_data = d.get("data", {}).get("resultData", {}).get("runData", {})
    format_outputs = run_data.get("Format Output", [])
    
    gmail, slack, calendar = [], [], []
    for exec_data in format_outputs:
        items = exec_data.get("data", {}).get("main", [[]])[0]
        for item in items:
            output = item.get("json", {})
            gmail.extend(output.get("gmail", []))
            slack.extend(output.get("slack", []))
            calendar.extend(output.get("calendar", []))
    
    # Google Tasks を取得（Tag Tasks ノードから）
    gtasks = []
    tag_tasks_outputs = run_data.get("Tag Tasks", [])
    for exec_data in tag_tasks_outputs:
        items = exec_data.get("data", {}).get("main", [[]])[0]
        for item in items:
            output = item.get("json", {})
            if output.get("source") == "gtasks" and output.get("gtasks"):
                gtasks.append(output.get("gtasks"))
    
    return gmail, slack, calendar, gtasks


def check_duplicate(conn: sqlite3.Connection, event_id: str) -> bool:
    """重複チェック"""
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM events WHERE event_id = ?", (event_id,))
    return cursor.fetchone() is not None


def mark_as_ingested(conn: sqlite3.Connection, event_id: str, source: str):
    """イベントを記録"""
    cursor = conn.cursor()
    now = datetime.now(JST).isoformat()
    cursor.execute(
        "INSERT OR IGNORE INTO events (event_id, source, ingested_at) VALUES (?, ?, ?)",
        (event_id, source, now)
    )
    conn.commit()


def normalize_event(item: Dict, source: str) -> Dict:
    """共通イベントスキーマに正規化（ルーティングエンジン統合）"""
    now = datetime.now(JST).isoformat()
    
    # イベントID生成
    raw_id = item.get("id") or item.get("ts") or item.get("iid") or str(hash(str(item)))
    event_id = f"{source}:{raw_id}"
    
    # 発生日時
    occurred_at = item.get("date") or item.get("ts") or item.get("start") or now
    
    # アクター
    actor = {
        "name": item.get("from") or item.get("user") or item.get("username") or "",
        "id": item.get("user") or "",
        "email": item.get("from") or ""
    }
    
    # タイトルと本文
    title = item.get("subject") or item.get("summary") or ""
    body = item.get("snippet") or item.get("text") or ""
    
    # 基本イベント構造
    event = {
        "event_id": event_id,
        "source": source,
        "occurred_at": occurred_at,
        "ingested_at": now,
        "actor": actor,
        "participants": [],
        "title": title,
        "body": body[:500],
        "links": [{"label": "permalink", "url": item.get("permalink", "")}] if item.get("permalink") else [],
        "attachments": [],
        "targets": {
            "projects": [],
            "people": [],
            "companies": [],
            "channel": item.get("channel", {}).get("name") if isinstance(item.get("channel"), dict) else item.get("channel", "")
        },
        "signals": {
            "priority": "P3",
            "action_required": False,
            "confidence": 0.5,
            "sensitivity": "internal"
        },
        "proposed_actions": [],
        "provenance": {
            "raw_ref": raw_id,
            "notes": ""
        }
    }
    
    # ルーティングエンジンで分類
    try:
        routing_result = route_event(event)
        event["targets"]["projects"] = routing_result.projects
        event["signals"]["priority"] = routing_result.priority
        event["signals"]["action_required"] = routing_result.action_required
        event["signals"]["no_reply"] = routing_result.no_reply
        event["signals"]["sensitivity"] = routing_result.sensitivity
        event["signals"]["confidence"] = routing_result.confidence
        event["routing_reasons"] = routing_result.match_reasons
    except Exception as e:
        logger.warn(f"Routing failed for {event_id}", data={"error": str(e)})
    
    return event


def save_google_tasks(tasks: List[Dict]):
    """Google Tasks をキャッシュに保存"""
    cache_path = STATE_PATH / "google_tasks.json"
    now = datetime.now(JST).isoformat()
    
    cache = {
        "tasks": tasks,
        "last_sync": now,
        "task_lists": ["@default"]
    }
    
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2, ensure_ascii=False)
    
    return len(tasks)


def save_events(events: List[Dict], date_str: str):
    """正規化イベントをJSONLで保存"""
    SYNC_PATH.mkdir(parents=True, exist_ok=True)
    filepath = SYNC_PATH / f"events_{date_str}.jsonl"
    
    with open(filepath, "a", encoding="utf-8") as f:
        for event in events:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")
    
    return filepath


def update_cursors(gmail_count: int, slack_count: int, calendar_count: int):
    """カーソルを更新"""
    cursors_path = STATE_PATH / "cursors.json"
    now = datetime.now(JST).isoformat()
    
    with open(cursors_path) as f:
        cursors = json.load(f)
    
    if gmail_count > 0:
        cursors["gmail"]["last_sync_at"] = now
    if slack_count > 0:
        cursors["slack"]["last_sync_at"] = now
    if calendar_count > 0:
        cursors["gcal"]["last_sync_at"] = now
    
    with open(cursors_path, "w") as f:
        json.dump(cursors, f, indent=2)


def main():
    logger.info("Sync started")
    
    api_key = get_api_key()
    if not api_key:
        logger.error("API key not found")
        print("ERROR: API key not found")
        return
    
    exec_id = get_latest_execution_id(api_key)
    if not exec_id:
        logger.error("No successful execution found")
        print("ERROR: No successful execution found")
        return
    
    logger.info(f"Processing execution {exec_id}")
    
    # データ取得
    with logger.timer("fetch_data"):
        gmail, slack, calendar, gtasks = get_execution_data(api_key, exec_id)
    
    logger.info(f"Fetched: Gmail={len(gmail)}, Slack={len(slack)}, Calendar={len(calendar)}, Tasks={len(gtasks)}")
    
    # 重複チェック用DB接続
    db_path = STATE_PATH / "dedupe.sqlite"
    conn = sqlite3.connect(db_path)
    
    # 正規化と重複排除
    new_events = []
    stats = {"gmail": 0, "slack": 0, "calendar": 0, "duplicates": 0, "p0": 0, "p1": 0, "action_required": 0}
    
    with logger.timer("normalize_events"):
        for item in gmail:
            event = normalize_event(item, "gmail")
            if not check_duplicate(conn, event["event_id"]):
                new_events.append(event)
                mark_as_ingested(conn, event["event_id"], "gmail")
                stats["gmail"] += 1
                if event["signals"]["priority"] == "P0":
                    stats["p0"] += 1
                if event["signals"]["priority"] == "P1":
                    stats["p1"] += 1
                if event["signals"]["action_required"]:
                    stats["action_required"] += 1
            else:
                stats["duplicates"] += 1
        
        for item in slack:
            event = normalize_event(item, "slack")
            if not check_duplicate(conn, event["event_id"]):
                new_events.append(event)
                mark_as_ingested(conn, event["event_id"], "slack")
                stats["slack"] += 1
                if event["signals"]["priority"] == "P0":
                    stats["p0"] += 1
                if event["signals"]["priority"] == "P1":
                    stats["p1"] += 1
                if event["signals"]["action_required"]:
                    stats["action_required"] += 1
            else:
                stats["duplicates"] += 1
        
        for item in calendar:
            event = normalize_event(item, "gcal")
            if not check_duplicate(conn, event["event_id"]):
                new_events.append(event)
                mark_as_ingested(conn, event["event_id"], "gcal")
                stats["calendar"] += 1
            else:
                stats["duplicates"] += 1
    
    conn.close()
    
    # Google Tasks を保存
    gtasks_count = 0
    if gtasks:
        gtasks_count = save_google_tasks(gtasks)
    
    # 保存
    if new_events:
        now = datetime.now(JST)
        date_str = now.strftime("%Y-%m-%d")
        filepath = save_events(new_events, date_str)
        update_cursors(stats["gmail"], stats["slack"], stats["calendar"])
        
        logger.info("Sync completed", data={
            "new_events": len(new_events),
            "gmail": stats["gmail"],
            "slack": stats["slack"],
            "calendar": stats["calendar"],
            "gtasks": gtasks_count,
            "duplicates": stats["duplicates"],
            "p0": stats["p0"],
            "p1": stats["p1"],
            "action_required": stats["action_required"],
            "file": str(filepath)
        })
        
        print(f"✓ Saved {len(new_events)} new events")
        print(f"  Gmail: {stats['gmail']}, Slack: {stats['slack']}, Calendar: {stats['calendar']}, Tasks: {gtasks_count}")
        print(f"  P0: {stats['p0']}, P1: {stats['p1']}, Action Required: {stats['action_required']}")
        print(f"  Duplicates skipped: {stats['duplicates']}")
        print(f"  File: {filepath.name}")
    else:
        logger.info("No new events", data={"duplicates": stats["duplicates"], "gtasks": gtasks_count})
        print(f"✓ No new events (all {stats['duplicates']} were duplicates)")
        if gtasks_count:
            print(f"  Google Tasks synced: {gtasks_count}")


if __name__ == "__main__":
    main()
