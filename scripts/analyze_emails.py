#!/usr/bin/env python3
"""
メール分析スクリプト（v2）
- ルーティングエンジン統合
- 構造化ログ
- 機密判定
- ActionQueue連携
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Tuple

# ライブラリパス追加
SCRIPTS_PATH = Path("/Users/ai-driven-work/Library/Mobile Documents/com~apple~CloudDocs/OpenClaw-Shared/scripts")
sys.path.insert(0, str(SCRIPTS_PATH / "lib"))

from structured_logger import get_logger, log_action
from routing_engine import get_routing_engine, route_event

# 設定
JST = timezone(timedelta(hours=9))
VAULT_PATH = Path("/Users/ai-driven-work/Library/Mobile Documents/com~apple~CloudDocs/OpenClaw-Shared/obsidian/Ichioka Obsidian")
EVENTS_PATH = VAULT_PATH / "00_System/02_Ingest/normalized"
ACTION_QUEUE_PATH = VAULT_PATH / "00_System/04_ActionQueue"

# ロガー
logger = get_logger("email_analysis")


def load_today_emails() -> List[Dict]:
    """今日のGmailイベントを読み込む"""
    today = datetime.now(JST).strftime("%Y-%m-%d")
    emails = []
    
    events_file = EVENTS_PATH / f"events_{today}.jsonl"
    if events_file.exists():
        with open(events_file, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try:
                        event = json.loads(line)
                        if event.get("source") == "gmail":
                            emails.append(event)
                    except json.JSONDecodeError:
                        continue
    
    return emails


def load_existing_commands() -> set:
    """既存のコマンドIDを取得"""
    existing = set()
    
    for folder in ["pending", "processed"]:
        folder_path = ACTION_QUEUE_PATH / folder
        if folder_path.exists():
            for f in folder_path.glob("*.json"):
                try:
                    with open(f) as fp:
                        cmd = json.load(fp)
                        # source_event_idで重複チェック
                        source_id = cmd.get("source_event_id")
                        if source_id:
                            existing.add(source_id)
                except:
                    continue
    
    return existing


def analyze_email(email: Dict) -> Tuple[bool, str, Dict]:
    """
    メールを分析して返信が必要かどうかを判定
    Returns: (needs_reply, reason, analysis)
    """
    signals = email.get("signals", {})
    
    # ルーティングエンジンの結果を使用
    action_required = signals.get("action_required", False)
    no_reply = signals.get("no_reply", False)
    priority = signals.get("priority", "P3")
    sensitivity = signals.get("sensitivity", "internal")
    
    # 返信不要の場合
    if no_reply:
        return False, "no_reply_pattern", {
            "priority": priority,
            "sensitivity": sensitivity,
            "routing_reasons": email.get("routing_reasons", [])
        }
    
    # アクション必要の場合
    if action_required:
        return True, "action_required", {
            "priority": priority,
            "sensitivity": sensitivity,
            "routing_reasons": email.get("routing_reasons", [])
        }
    
    # P0/P1は要確認
    if priority in ("P0", "P1"):
        return True, f"high_priority_{priority}", {
            "priority": priority,
            "sensitivity": sensitivity,
            "routing_reasons": email.get("routing_reasons", [])
        }
    
    return False, "default_no_reply", {
        "priority": priority,
        "sensitivity": sensitivity,
        "routing_reasons": email.get("routing_reasons", [])
    }


def create_pending_command(email: Dict, analysis: Dict) -> Dict:
    """返信が必要なメールのコマンドを作成"""
    now = datetime.now(JST)
    event_id = email.get("event_id", "")
    
    cmd = {
        "cmd_id": f"cmd_email_{now.strftime('%Y%m%d_%H%M%S')}_{hash(event_id) % 10000:04d}",
        "type": "draft_reply_email",
        "created_at": now.isoformat(),
        "status": "pending",
        "priority": analysis.get("priority", "P3"),
        "needs_approval": True,
        "source_event_id": event_id,
        "context": {
            "from": email.get("actor", {}).get("email", ""),
            "subject": email.get("title", ""),
            "snippet": email.get("body", "")[:200],
            "reason": analysis.get("reason", ""),
            "routing_reasons": analysis.get("routing_reasons", []),
            "sensitivity": analysis.get("sensitivity", "internal"),
        },
        "proposed_action": {
            "action": "draft_reply",
            "to": email.get("actor", {}).get("email", ""),
            "subject": f"Re: {email.get('title', '')}",
            "body_draft": "",  # 承認時に作成
        },
        "approval": {
            "approved": None,
            "approved_by": None,
            "approved_at": None,
        },
        "execution": {
            "executed": False,
            "executed_at": None,
            "result": None,
        }
    }
    
    return cmd


def save_command(cmd: Dict):
    """コマンドを保存"""
    pending_path = ACTION_QUEUE_PATH / "pending"
    pending_path.mkdir(parents=True, exist_ok=True)
    
    filepath = pending_path / f"{cmd['cmd_id']}.json"
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(cmd, f, indent=2, ensure_ascii=False)
    
    return filepath


def main():
    logger.info("Email analysis started")
    
    # データ読み込み
    emails = load_today_emails()
    existing_commands = load_existing_commands()
    
    logger.info(f"Loaded emails", data={
        "total": len(emails),
        "existing_commands": len(existing_commands)
    })
    
    # 分析
    stats = {
        "analyzed": 0,
        "needs_reply": 0,
        "no_reply": 0,
        "skipped_existing": 0,
        "by_priority": {"P0": 0, "P1": 0, "P2": 0, "P3": 0},
    }
    
    new_commands = []
    
    for email in emails:
        event_id = email.get("event_id", "")
        
        # 既存コマンドはスキップ
        if event_id in existing_commands:
            stats["skipped_existing"] += 1
            continue
        
        stats["analyzed"] += 1
        
        needs_reply, reason, analysis = analyze_email(email)
        priority = analysis.get("priority", "P3")
        stats["by_priority"][priority] = stats["by_priority"].get(priority, 0) + 1
        
        if needs_reply:
            stats["needs_reply"] += 1
            cmd = create_pending_command(email, {**analysis, "reason": reason})
            filepath = save_command(cmd)
            new_commands.append(cmd)
            
            log_action(
                cmd["cmd_id"],
                "draft_reply_email",
                "pending",
                f"Created pending command for {email.get('actor', {}).get('email', '')}",
                data={
                    "priority": priority,
                    "reason": reason,
                    "sensitivity": analysis.get("sensitivity")
                }
            )
            
            logger.info(f"Created pending command", data={
                "cmd_id": cmd["cmd_id"],
                "priority": priority,
                "reason": reason
            })
        else:
            stats["no_reply"] += 1
    
    # 結果
    logger.info("Email analysis completed", data=stats)
    
    print(f"=== メール分析完了 ===")
    print(f"分析対象: {stats['analyzed']} 件")
    print(f"返信必要: {stats['needs_reply']} 件")
    print(f"返信不要: {stats['no_reply']} 件")
    print(f"既存スキップ: {stats['skipped_existing']} 件")
    print(f"優先度別: P0={stats['by_priority']['P0']}, P1={stats['by_priority']['P1']}, P2={stats['by_priority']['P2']}, P3={stats['by_priority']['P3']}")
    
    if new_commands:
        print(f"\n新規コマンド:")
        for cmd in new_commands[:5]:
            context = cmd.get("context", {})
            print(f"  [{cmd['priority']}] {context.get('from', '')[:30]} - {context.get('subject', '')[:40]}")
        if len(new_commands) > 5:
            print(f"  ... 他 {len(new_commands) - 5} 件")
    
    return stats


if __name__ == "__main__":
    main()
