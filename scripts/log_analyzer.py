#!/usr/bin/env python3
"""
ログ分析・レポートツール
- 構造化ログの集計
- エラーレポート
- パフォーマンス分析
"""

import json
from pathlib import Path
from datetime import datetime, timezone, timedelta
from collections import defaultdict
from typing import Dict, List, Optional

# 設定
JST = timezone(timedelta(hours=9))
LOGS_PATH = Path("/Users/ai-driven-work/Library/Mobile Documents/com~apple~CloudDocs/OpenClaw-Shared/obsidian/Ichioka Obsidian/00_System/05_Logs")


def load_logs(logger_name: str, date_str: Optional[str] = None) -> List[Dict]:
    """ログを読み込む"""
    if date_str is None:
        date_str = datetime.now(JST).strftime("%Y-%m-%d")
    
    filepath = LOGS_PATH / f"{logger_name}_{date_str}.jsonl"
    logs = []
    
    if filepath.exists():
        with open(filepath, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try:
                        logs.append(json.loads(line))
                    except:
                        continue
    
    return logs


def load_errors(date_str: Optional[str] = None) -> List[Dict]:
    """エラーログを読み込む"""
    if date_str is None:
        date_str = datetime.now(JST).strftime("%Y-%m-%d")
    
    filepath = LOGS_PATH / f"errors_{date_str}.jsonl"
    errors = []
    
    if filepath.exists():
        with open(filepath, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try:
                        errors.append(json.loads(line))
                    except:
                        continue
    
    return errors


def analyze_ingest(date_str: Optional[str] = None) -> Dict:
    """Ingestログを分析"""
    logs = load_logs("ingest", date_str)
    
    stats = {
        "total_entries": len(logs),
        "sync_count": 0,
        "events_ingested": 0,
        "by_source": {"gmail": 0, "slack": 0, "calendar": 0},
        "duplicates": 0,
        "priority_counts": {"P0": 0, "P1": 0},
        "action_required": 0,
        "avg_duration_ms": 0,
        "errors": 0,
    }
    
    durations = []
    
    for log in logs:
        level = log.get("level", "")
        message = log.get("message", "")
        data = log.get("data", {})
        
        if level == "ERROR":
            stats["errors"] += 1
        
        if "Sync completed" in message:
            stats["sync_count"] += 1
            stats["events_ingested"] += data.get("new_events", 0)
            stats["by_source"]["gmail"] += data.get("gmail", 0)
            stats["by_source"]["slack"] += data.get("slack", 0)
            stats["by_source"]["calendar"] += data.get("calendar", 0)
            stats["duplicates"] += data.get("duplicates", 0)
            stats["priority_counts"]["P0"] += data.get("p0", 0)
            stats["priority_counts"]["P1"] += data.get("p1", 0)
            stats["action_required"] += data.get("action_required", 0)
        
        if "duration_ms" in data:
            durations.append(data["duration_ms"])
    
    if durations:
        stats["avg_duration_ms"] = sum(durations) / len(durations)
    
    return stats


def analyze_actions(date_str: Optional[str] = None) -> Dict:
    """Actionsログを分析"""
    logs = load_logs("actions", date_str)
    
    stats = {
        "total_entries": len(logs),
        "pending": 0,
        "approved": 0,
        "rejected": 0,
        "executed": 0,
        "failed": 0,
        "by_type": defaultdict(int),
        "by_priority": defaultdict(int),
    }
    
    for log in logs:
        context = log.get("context", {})
        action_type = context.get("action_type", "unknown")
        
        stats["by_type"][action_type] += 1
        
        message = log.get("message", "").lower()
        if "pending" in message:
            stats["pending"] += 1
        elif "approved" in message:
            stats["approved"] += 1
        elif "rejected" in message:
            stats["rejected"] += 1
        elif "executed" in message:
            stats["executed"] += 1
        elif "failed" in message:
            stats["failed"] += 1
    
    return stats


def generate_daily_report(date_str: Optional[str] = None) -> str:
    """日次レポートを生成"""
    if date_str is None:
        date_str = datetime.now(JST).strftime("%Y-%m-%d")
    
    ingest_stats = analyze_ingest(date_str)
    actions_stats = analyze_actions(date_str)
    errors = load_errors(date_str)
    
    report = f"""# 📊 Daily Log Report - {date_str}

Generated: {datetime.now(JST).strftime('%Y-%m-%d %H:%M:%S')} JST

---

## 📥 Ingest Summary

- **Sync runs:** {ingest_stats['sync_count']}
- **Events ingested:** {ingest_stats['events_ingested']}
  - Gmail: {ingest_stats['by_source']['gmail']}
  - Slack: {ingest_stats['by_source']['slack']}
  - Calendar: {ingest_stats['by_source']['calendar']}
- **Duplicates skipped:** {ingest_stats['duplicates']}
- **High priority:** P0={ingest_stats['priority_counts']['P0']}, P1={ingest_stats['priority_counts']['P1']}
- **Action required:** {ingest_stats['action_required']}
- **Avg duration:** {ingest_stats['avg_duration_ms']:.2f}ms
- **Errors:** {ingest_stats['errors']}

---

## ✅ Actions Summary

- **Total actions:** {actions_stats['total_entries']}
- **Pending:** {actions_stats['pending']}
- **Approved:** {actions_stats['approved']}
- **Rejected:** {actions_stats['rejected']}
- **Executed:** {actions_stats['executed']}
- **Failed:** {actions_stats['failed']}

### By Type
"""
    
    for action_type, count in actions_stats['by_type'].items():
        report += f"- {action_type}: {count}\n"
    
    report += f"""
---

## ⚠️ Errors ({len(errors)})

"""
    
    if errors:
        for error in errors[:10]:
            timestamp = error.get("timestamp", "")[:19]
            logger = error.get("logger", "unknown")
            message = error.get("message", "")
            error_info = error.get("error", {})
            error_type = error_info.get("type", "")
            
            report += f"### [{timestamp}] {logger}\n\n"
            report += f"- **Message:** {message}\n"
            if error_type:
                report += f"- **Type:** {error_type}\n"
            report += "\n"
        
        if len(errors) > 10:
            report += f"_... 他 {len(errors) - 10} 件_\n"
    else:
        report += "_エラーなし_ ✅\n"
    
    report += """
---

## 📈 Performance

"""
    
    # パフォーマンス分析
    ingest_logs = load_logs("ingest", date_str)
    digest_logs = load_logs("digest", date_str)
    
    for name, logs in [("ingest", ingest_logs), ("digest", digest_logs)]:
        durations = []
        for log in logs:
            d = log.get("data", {}).get("duration_ms")
            if d:
                durations.append(d)
        
        if durations:
            report += f"### {name.title()}\n"
            report += f"- Min: {min(durations):.2f}ms\n"
            report += f"- Max: {max(durations):.2f}ms\n"
            report += f"- Avg: {sum(durations)/len(durations):.2f}ms\n\n"
    
    return report


def main():
    """メイン処理"""
    date_str = datetime.now(JST).strftime("%Y-%m-%d")
    
    print(f"=== ログ分析 - {date_str} ===\n")
    
    # Ingest分析
    ingest_stats = analyze_ingest(date_str)
    print("📥 Ingest:")
    print(f"  Sync runs: {ingest_stats['sync_count']}")
    print(f"  Events: {ingest_stats['events_ingested']}")
    print(f"  P0/P1: {ingest_stats['priority_counts']['P0']}/{ingest_stats['priority_counts']['P1']}")
    print(f"  Action required: {ingest_stats['action_required']}")
    print()
    
    # Actions分析
    actions_stats = analyze_actions(date_str)
    print("✅ Actions:")
    print(f"  Total: {actions_stats['total_entries']}")
    print(f"  Pending/Approved/Executed: {actions_stats['pending']}/{actions_stats['approved']}/{actions_stats['executed']}")
    print()
    
    # エラー
    errors = load_errors(date_str)
    print(f"⚠️ Errors: {len(errors)}")
    if errors:
        for error in errors[:3]:
            print(f"  - [{error.get('logger', '')}] {error.get('message', '')[:50]}")
    
    print()
    print("詳細レポートを生成するには: generate_daily_report()")


if __name__ == "__main__":
    main()
