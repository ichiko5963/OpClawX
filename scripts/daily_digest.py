#!/usr/bin/env python3
"""
強化版 Daily Digest 生成スクリプト（v2）
- ルーティングエンジン統合
- 構造化ログ
- 機密情報のマスキング
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta
from collections import defaultdict
from typing import Dict, List, Tuple

# ライブラリパス追加
SCRIPTS_PATH = Path("/Users/ai-driven-work/Library/Mobile Documents/com~apple~CloudDocs/OpenClaw-Shared/scripts")
sys.path.insert(0, str(SCRIPTS_PATH / "lib"))

from structured_logger import get_logger
from routing_engine import get_routing_engine

# 設定
JST = timezone(timedelta(hours=9))
VAULT_PATH = Path("/Users/ai-driven-work/Library/Mobile Documents/com~apple~CloudDocs/OpenClaw-Shared/obsidian/Ichioka Obsidian")
EVENTS_PATH = VAULT_PATH / "00_System/02_Ingest/normalized"
DIGEST_PATH = VAULT_PATH / "00_System/03_Digest"
ACTION_QUEUE_PATH = VAULT_PATH / "00_System/04_ActionQueue"
TASKS_PATH = VAULT_PATH / "07-To Do"

# ロガー
logger = get_logger("digest")


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
                    except json.JSONDecodeError:
                        continue
    
    return events


def load_pending_commands() -> List[Dict]:
    """pending のコマンドを読み込む"""
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


def load_incomplete_tasks() -> List[str]:
    """未完了タスクを読み込む"""
    tasks = []
    tasks_file = TASKS_PATH / "Tasks.md"
    
    if tasks_file.exists():
        with open(tasks_file, encoding="utf-8") as f:
            for line in f:
                if line.strip().startswith("- [ ]"):
                    tasks.append(line.strip())
    
    return tasks


def categorize_events(events: List[Dict]) -> Dict[str, List[Dict]]:
    """イベントをソース別に分類"""
    categorized = defaultdict(list)
    for event in events:
        source = event.get("source", "unknown")
        categorized[source].append(event)
    return dict(categorized)


def categorize_by_project(events: List[Dict]) -> Dict[str, List[Dict]]:
    """プロジェクト別に分類（signalsから）"""
    categorized = defaultdict(list)
    
    for event in events:
        projects = event.get("targets", {}).get("projects", [])
        if projects:
            for project in projects:
                categorized[project].append(event)
        else:
            categorized["_uncategorized"].append(event)
    
    return dict(categorized)


def get_by_priority(events: List[Dict], priority: str) -> List[Dict]:
    """指定優先度のイベントを取得"""
    return [e for e in events if e.get("signals", {}).get("priority") == priority]


def get_action_required(events: List[Dict]) -> List[Dict]:
    """アクション必要なイベントを取得"""
    return [e for e in events if e.get("signals", {}).get("action_required")]


def mask_sensitive(text: str, sensitivity: str) -> str:
    """機密情報をマスク"""
    if sensitivity in ("confidential", "restricted"):
        engine = get_routing_engine()
        return engine.mask_pii(text)
    return text


def generate_executive_summary(
    events: List[Dict],
    by_source: Dict,
    by_project: Dict,
    pending_commands: List,
    tasks: List
) -> str:
    """Executive Summary を生成"""
    now = datetime.now(JST)
    
    total = len(events)
    gmail_count = len(by_source.get("gmail", []))
    slack_count = len(by_source.get("slack", []))
    gcal_count = len(by_source.get("gcal", []))
    
    p0_events = get_by_priority(events, "P0")
    p1_events = get_by_priority(events, "P1")
    action_required = get_action_required(events)
    
    # 機密情報の統計
    confidential_count = len([e for e in events if e.get("signals", {}).get("sensitivity") in ("confidential", "restricted")])
    
    summary = f"""**{now.strftime('%Y年%m月%d日')}のダイジェスト**

📊 本日の収集: **{total}件**（Gmail {gmail_count} / Slack {slack_count} / Calendar {gcal_count}）
🔴 緊急(P0): **{len(p0_events)}件** / 重要(P1): **{len(p1_events)}件**
📋 アクション必要: **{len(action_required)}件**
⏳ 承認待ち: **{len(pending_commands)}件**
☑️ 未完了タスク: **{len(tasks)}件**
🔒 機密情報: **{confidential_count}件**
"""
    
    if by_project:
        active_projects = sorted(
            [p for p in by_project.keys() if p != "_uncategorized"],
            key=lambda p: len(by_project[p]),
            reverse=True
        )[:3]
        if active_projects:
            summary += f"📁 アクティブ: {', '.join(active_projects)}\n"
    
    return summary


def format_event_item(event: Dict, include_routing: bool = False) -> str:
    """イベントを表示用にフォーマット"""
    source = event.get("source", "unknown")
    title = event.get("title", "") or "(no title)"
    body = event.get("body", "")[:100]
    sensitivity = event.get("signals", {}).get("sensitivity", "internal")
    
    # 機密情報をマスク
    title = mask_sensitive(title, sensitivity)
    body = mask_sensitive(body, sensitivity)
    
    item = f"- **[{source}]** {title}\n"
    if body:
        item += f"  - {body}...\n"
    
    if include_routing:
        reasons = event.get("routing_reasons", [])
        if reasons:
            item += f"  - _Routing: {'; '.join(reasons[:2])}_\n"
    
    return item


def generate_digest(events: List[Dict], pending_commands: List[Dict], tasks: List[str]) -> str:
    """完全な Daily Digest を生成"""
    now = datetime.now(JST)
    
    by_source = categorize_events(events)
    by_project = categorize_by_project(events)
    
    p0_events = get_by_priority(events, "P0")
    p1_events = get_by_priority(events, "P1")
    action_required = get_action_required(events)
    
    digest = f"""# 📋 Daily Digest - {now.strftime('%Y-%m-%d')}

Generated: {now.strftime('%Y-%m-%d %H:%M:%S')} JST

---

## 1️⃣ Executive Summary

{generate_executive_summary(events, by_source, by_project, pending_commands, tasks)}

---

## 2️⃣ 🔴 P0/P1 イベント

### P0 - 今日中に対応が必要

"""
    
    if p0_events:
        for event in p0_events[:5]:
            digest += format_event_item(event, include_routing=True)
    else:
        digest += "_なし_ ✅\n"
    
    digest += "\n### P1 - 24-72h以内に対応\n\n"
    
    if p1_events:
        for event in p1_events[:10]:
            digest += format_event_item(event, include_routing=True)
    else:
        digest += "_なし_ ✅\n"
    
    digest += "\n---\n\n## 3️⃣ 📧 要返信・要対応\n\n"
    
    if action_required:
        for event in action_required[:10]:
            digest += format_event_item(event)
    else:
        digest += "_要対応なし_ ✅\n"
    
    digest += "\n---\n\n## 4️⃣ 📅 今後の予定\n\n"
    
    calendar_events = by_source.get("gcal", [])
    if calendar_events:
        for event in calendar_events[:10]:
            summary = event.get("title", "(no title)")
            digest += f"- **{summary}**\n"
    else:
        digest += "_予定なし_\n"
    
    digest += "\n---\n\n## 5️⃣ ☑️ 未完了タスク\n\n"
    
    if tasks:
        for task in tasks[:10]:
            digest += f"{task}\n"
        if len(tasks) > 10:
            digest += f"\n_... 他 {len(tasks) - 10} 件_\n"
    else:
        digest += "_未完了タスクなし_ ✅\n"
    
    digest += "\n---\n\n## 6️⃣ 📁 プロジェクト別\n\n"
    
    sorted_projects = sorted(
        [(p, items) for p, items in by_project.items() if p != "_uncategorized"],
        key=lambda x: len(x[1]),
        reverse=True
    )
    
    if sorted_projects:
        for project, items in sorted_projects[:5]:
            digest += f"### {project} ({len(items)}件)\n\n"
            for item in items[:3]:
                digest += format_event_item(item)
            if len(items) > 3:
                digest += f"_... 他 {len(items) - 3} 件_\n"
            digest += "\n"
    else:
        digest += "_プロジェクト関連の更新なし_\n"
    
    digest += "\n---\n\n## 7️⃣ ⏳ 承認待ちアクション\n\n"
    
    if pending_commands:
        for cmd in pending_commands:
            cmd_id = cmd.get("cmd_id", "unknown")
            cmd_type = cmd.get("type", "unknown")
            priority = cmd.get("priority", "P3")
            context = cmd.get("context", {})
            
            digest += f"- **[{priority}]** {cmd_type}\n"
            digest += f"  - ID: `{cmd_id}`\n"
            snippet = context.get("snippet", "")[:80]
            if snippet:
                digest += f"  - {snippet}...\n"
    else:
        digest += "_承認待ちなし_ ✅\n"
    
    digest += f"""

---

## 📝 メモ

_今日の振り返りや気づきをここに記入_

---

> Generated by Context Curator v2 at {now.isoformat()}
> Routing Engine: routing_rules.yaml v1.0
> Sensitivity: sensitivity.yaml v1.0
"""
    
    return digest


def update_project_memories(events: List[Dict]):
    """プロジェクトのMEMORY.mdを更新"""
    today = datetime.now(JST).strftime("%Y-%m-%d")
    by_project = categorize_by_project(events)
    
    updated = []
    
    for project, items in by_project.items():
        if project == "_uncategorized":
            continue
        
        memory_path = VAULT_PATH / f"03_Projects/_Active/{project}/MEMORY.md"
        
        if not memory_path.exists():
            continue
        
        with open(memory_path, encoding="utf-8") as f:
            content = f.read()
        
        if f"## {today}" in content:
            continue
        
        new_entry = f"\n\n## {today} Auto-captured\n\n"
        
        for item in items[:5]:
            source = item.get("source", "unknown")
            body = item.get("body", "")[:150]
            sensitivity = item.get("signals", {}).get("sensitivity", "internal")
            body = mask_sensitive(body, sensitivity)
            new_entry += f"- [{source}] {body}\n"
        
        with open(memory_path, "a", encoding="utf-8") as f:
            f.write(new_entry)
        
        updated.append(project)
        logger.info(f"Updated project memory", data={"project": project, "items": len(items)})
    
    return updated


def save_digest(digest: str) -> Path:
    """Digestを保存"""
    today = datetime.now(JST).strftime("%Y-%m-%d")
    
    daily_path = DIGEST_PATH / "daily"
    daily_path.mkdir(parents=True, exist_ok=True)
    
    filepath = daily_path / f"{today}.md"
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(digest)
    
    return filepath


def main():
    logger.info("Daily Digest generation started")
    
    # データ読み込み
    with logger.timer("load_data"):
        events = load_today_events()
        pending_commands = load_pending_commands()
        tasks = load_incomplete_tasks()
    
    logger.info("Data loaded", data={
        "events": len(events),
        "pending_commands": len(pending_commands),
        "tasks": len(tasks)
    })
    
    # Digest生成
    with logger.timer("generate_digest"):
        digest = generate_digest(events, pending_commands, tasks)
    
    # 保存
    filepath = save_digest(digest)
    logger.info(f"Digest saved", data={"file": str(filepath)})
    
    # プロジェクトメモリ更新
    with logger.timer("update_project_memories"):
        updated_projects = update_project_memories(events)
    
    if updated_projects:
        logger.info(f"Project memories updated", data={"projects": updated_projects})
    
    # 統計
    by_source = categorize_events(events)
    p0 = len(get_by_priority(events, "P0"))
    p1 = len(get_by_priority(events, "P1"))
    action_required = len(get_action_required(events))
    
    print(f"✓ Daily Digest 生成完了")
    print(f"  Events: {len(events)} (Gmail: {len(by_source.get('gmail', []))}, Slack: {len(by_source.get('slack', []))}, Calendar: {len(by_source.get('gcal', []))})")
    print(f"  P0: {p0}, P1: {p1}, Action Required: {action_required}")
    print(f"  Pending commands: {len(pending_commands)}, Tasks: {len(tasks)}")
    print(f"  Updated projects: {updated_projects or 'None'}")
    print(f"  File: {filepath}")
    
    logger.info("Daily Digest generation completed")
    
    return digest


if __name__ == "__main__":
    main()
