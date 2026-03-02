#!/usr/bin/env python3
"""
Session Progress Tracker v1.0
深夜セッションの進捗をトラッキングし、レポートを生成するツール。
各フェーズの完了状況と時間管理を支援。

Usage:
  python3 tools/session_progress.py init                    # セッション開始
  python3 tools/session_progress.py phase <name> start      # フェーズ開始
  python3 tools/session_progress.py phase <name> done       # フェーズ完了
  python3 tools/session_progress.py task <phase> <desc>     # タスク完了記録
  python3 tools/session_progress.py report                  # 進捗レポート
  python3 tools/session_progress.py final                   # 最終レポート
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Optional

WORKSPACE = Path("/Users/ai-driven-work/Documents/OpenClaw-Workspace")
STATE_FILE = WORKSPACE / "memory" / "session-tracker" / "current_session.json"


def ensure_dir():
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)


def load_state() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    return {}


def save_state(state: dict):
    ensure_dir()
    STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def init_session():
    """新しいセッションを初期化"""
    now = datetime.now()
    state = {
        "session_date": now.strftime("%Y-%m-%d"),
        "started_at": now.isoformat(),
        "phases": {},
        "tasks_completed": [],
        "total_tasks": 0,
        "artifacts": [],
    }
    save_state(state)
    print(f"🌙 深夜セッション開始: {now.strftime('%Y-%m-%d %H:%M')}")
    return state


def start_phase(name: str):
    """フェーズを開始"""
    state = load_state()
    now = datetime.now()
    state["phases"][name] = {
        "started_at": now.isoformat(),
        "completed_at": None,
        "tasks": [],
        "status": "in_progress",
    }
    save_state(state)
    print(f"▶️ Phase [{name}] 開始: {now.strftime('%H:%M')}")


def complete_phase(name: str):
    """フェーズを完了"""
    state = load_state()
    if name not in state["phases"]:
        print(f"⚠️ Phase [{name}] が見つかりません")
        return
    now = datetime.now()
    state["phases"][name]["completed_at"] = now.isoformat()
    state["phases"][name]["status"] = "completed"
    save_state(state)

    started = datetime.fromisoformat(state["phases"][name]["started_at"])
    duration = (now - started).total_seconds() / 60
    print(f"✅ Phase [{name}] 完了: {now.strftime('%H:%M')} ({duration:.0f}分)")


def add_task(phase: str, description: str):
    """タスク完了を記録"""
    state = load_state()
    now = datetime.now()
    task = {
        "phase": phase,
        "description": description,
        "completed_at": now.isoformat(),
    }
    state["tasks_completed"].append(task)
    state["total_tasks"] += 1

    if phase in state["phases"]:
        state["phases"][phase]["tasks"].append(description)

    save_state(state)
    print(f"  ✓ [{phase}] {description}")


def add_artifact(name: str, path: str):
    """成果物を記録"""
    state = load_state()
    state["artifacts"].append({
        "name": name,
        "path": path,
        "created_at": datetime.now().isoformat(),
    })
    save_state(state)
    print(f"  📦 成果物: {name} → {path}")


def generate_report() -> str:
    """進捗レポート生成"""
    state = load_state()
    if not state:
        return "⚠️ セッションが初期化されていません"

    now = datetime.now()
    started = datetime.fromisoformat(state["started_at"])
    elapsed = (now - started).total_seconds() / 60

    lines = [
        f"# 深夜セッション進捗 ({state['session_date']})",
        f"",
        f"**経過時間**: {elapsed:.0f}分 | **完了タスク**: {state['total_tasks']}",
        "",
        "## フェーズ状況",
    ]

    for name, phase in state["phases"].items():
        if phase["status"] == "completed":
            started_at = datetime.fromisoformat(phase["started_at"])
            completed_at = datetime.fromisoformat(phase["completed_at"])
            duration = (completed_at - started_at).total_seconds() / 60
            lines.append(f"- ✅ **{name}** ({duration:.0f}分, {len(phase['tasks'])}タスク)")
        elif phase["status"] == "in_progress":
            started_at = datetime.fromisoformat(phase["started_at"])
            running = (now - started_at).total_seconds() / 60
            lines.append(f"- ▶️ **{name}** (実行中 {running:.0f}分, {len(phase['tasks'])}タスク)")
        else:
            lines.append(f"- ⬜ **{name}** (未開始)")

    if state["artifacts"]:
        lines.append("")
        lines.append("## 成果物")
        for art in state["artifacts"]:
            lines.append(f"- {art['name']}: `{art['path']}`")

    return "\n".join(lines)


def generate_final_report() -> str:
    """最終レポート生成（朝の報告用）"""
    state = load_state()
    if not state:
        return "⚠️ セッションデータなし"

    now = datetime.now()
    started = datetime.fromisoformat(state["started_at"])
    total_hours = (now - started).total_seconds() / 3600

    lines = [
        f"# 🌙 深夜セッション最終レポート",
        f"**日付**: {state['session_date']}",
        f"**稼働時間**: {total_hours:.1f}時間",
        f"**完了タスク**: {state['total_tasks']}件",
        "",
    ]

    # フェーズサマリー
    for name, phase in state["phases"].items():
        if phase["status"] == "completed":
            lines.append(f"### ✅ {name}")
            for task in phase["tasks"]:
                lines.append(f"- {task}")
            lines.append("")

    # 成果物
    if state["artifacts"]:
        lines.append("### 📦 成果物")
        for art in state["artifacts"]:
            lines.append(f"- **{art['name']}**: `{art['path']}`")
        lines.append("")

    return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "init":
        init_session()
    elif cmd == "phase":
        if len(sys.argv) < 4:
            print("Usage: session_progress.py phase <name> start|done")
            sys.exit(1)
        name = sys.argv[2]
        action = sys.argv[3]
        if action == "start":
            start_phase(name)
        elif action == "done":
            complete_phase(name)
        else:
            print(f"Unknown phase action: {action}")
    elif cmd == "task":
        if len(sys.argv) < 4:
            print("Usage: session_progress.py task <phase> <description>")
            sys.exit(1)
        phase = sys.argv[2]
        desc = " ".join(sys.argv[3:])
        add_task(phase, desc)
    elif cmd == "artifact":
        if len(sys.argv) < 4:
            print("Usage: session_progress.py artifact <name> <path>")
            sys.exit(1)
        add_artifact(sys.argv[2], sys.argv[3])
    elif cmd == "report":
        print(generate_report())
    elif cmd == "final":
        print(generate_final_report())
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)


if __name__ == "__main__":
    main()
