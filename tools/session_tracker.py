#!/usr/bin/env python3
"""
深夜セッション進捗トラッカー
セッションのフェーズごとの進捗を管理し、レポートを生成する。
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

WORKSPACE = Path(os.getenv("WORKSPACE", "/Users/ai-driven-work/Documents/OpenClaw-Workspace"))
TRACKER_DIR = WORKSPACE / "memory" / "session-tracker"
TRACKER_DIR.mkdir(parents=True, exist_ok=True)


def create_session(session_date: str = None) -> dict:
    """新しいセッションを作成"""
    if session_date is None:
        session_date = datetime.now().strftime("%Y-%m-%d")
    
    session = {
        "date": session_date,
        "start_time": datetime.now().isoformat(),
        "end_time": None,
        "phases": {
            "phase1_organize": {
                "name": "整理作業",
                "status": "pending",
                "tasks": [],
                "start_time": None,
                "end_time": None,
            },
            "phase2_tools": {
                "name": "ツール開発",
                "status": "pending",
                "tasks": [],
                "start_time": None,
                "end_time": None,
            },
            "phase3_xposts": {
                "name": "X投稿作成",
                "status": "pending",
                "tasks": [],
                "start_time": None,
                "end_time": None,
            },
            "phase4_extra": {
                "name": "追加タスク",
                "status": "pending",
                "tasks": [],
                "start_time": None,
                "end_time": None,
            },
        },
        "summary": {
            "files_created": [],
            "files_modified": [],
            "tools_built": [],
            "posts_created": {"aircle": 0, "ichiaimarketer": 0},
            "lessons_learned": [],
        },
    }
    
    save_session(session_date, session)
    return session


def save_session(session_date: str, session: dict):
    """セッションを保存"""
    filepath = TRACKER_DIR / f"session-{session_date}.json"
    filepath.write_text(json.dumps(session, ensure_ascii=False, indent=2))


def load_session(session_date: str) -> dict:
    """セッションを読み込み"""
    filepath = TRACKER_DIR / f"session-{session_date}.json"
    if filepath.exists():
        return json.loads(filepath.read_text())
    return None


def update_phase(session_date: str, phase_key: str, status: str, task: str = None):
    """フェーズを更新"""
    session = load_session(session_date)
    if session is None:
        print(f"Session not found: {session_date}")
        return
    
    phase = session["phases"].get(phase_key)
    if phase is None:
        print(f"Phase not found: {phase_key}")
        return
    
    if status == "in_progress" and phase["start_time"] is None:
        phase["start_time"] = datetime.now().isoformat()
    
    if status == "completed":
        phase["end_time"] = datetime.now().isoformat()
    
    phase["status"] = status
    
    if task:
        phase["tasks"].append({
            "task": task,
            "completed_at": datetime.now().isoformat(),
        })
    
    save_session(session_date, session)


def add_file(session_date: str, filepath: str, action: str = "created"):
    """ファイル操作を記録"""
    session = load_session(session_date)
    if session is None:
        return
    
    key = f"files_{action}"
    if key in session["summary"]:
        session["summary"][key].append(filepath)
    
    save_session(session_date, session)


def set_post_count(session_date: str, account: str, count: int):
    """投稿数を設定"""
    session = load_session(session_date)
    if session is None:
        return
    
    session["summary"]["posts_created"][account] = count
    save_session(session_date, session)


def generate_report(session_date: str) -> str:
    """レポートを生成"""
    session = load_session(session_date)
    if session is None:
        return f"No session found for {session_date}"
    
    lines = [f"# 深夜セッションレポート - {session_date}", ""]
    
    # フェーズ進捗
    lines.append("## フェーズ進捗")
    for key, phase in session["phases"].items():
        status_emoji = {"pending": "⏳", "in_progress": "🔄", "completed": "✅", "skipped": "⏭️"}
        emoji = status_emoji.get(phase["status"], "❓")
        lines.append(f"- {emoji} **{phase['name']}**: {phase['status']}")
        
        if phase["tasks"]:
            for task in phase["tasks"]:
                lines.append(f"  - ✔ {task['task']}")
    
    lines.append("")
    
    # 成果物
    lines.append("## 成果物")
    posts = session["summary"]["posts_created"]
    lines.append(f"- AirCle投稿: {posts.get('aircle', 0)}個")
    lines.append(f"- ichiaimarketer投稿: {posts.get('ichiaimarketer', 0)}個")
    
    if session["summary"]["files_created"]:
        lines.append(f"- 作成ファイル: {len(session['summary']['files_created'])}個")
    
    if session["summary"]["tools_built"]:
        lines.append(f"- 作成ツール: {', '.join(session['summary']['tools_built'])}")
    
    lines.append("")
    
    # 学び
    if session["summary"]["lessons_learned"]:
        lines.append("## 学んだこと")
        for lesson in session["summary"]["lessons_learned"]:
            lines.append(f"- {lesson}")
    
    return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        print("Usage: session_tracker.py <command> [args]")
        print("Commands: create, update, report, add-file, set-posts")
        return
    
    cmd = sys.argv[1]
    date = sys.argv[2] if len(sys.argv) > 2 else datetime.now().strftime("%Y-%m-%d")
    
    if cmd == "create":
        session = create_session(date)
        print(f"Session created for {date}")
    
    elif cmd == "update":
        if len(sys.argv) < 5:
            print("Usage: session_tracker.py update <date> <phase> <status> [task]")
            return
        phase = sys.argv[3]
        status = sys.argv[4]
        task = sys.argv[5] if len(sys.argv) > 5 else None
        update_phase(date, phase, status, task)
        print(f"Phase {phase} updated to {status}")
    
    elif cmd == "report":
        print(generate_report(date))
    
    elif cmd == "set-posts":
        if len(sys.argv) < 5:
            print("Usage: session_tracker.py set-posts <date> <account> <count>")
            return
        account = sys.argv[3]
        count = int(sys.argv[4])
        set_post_count(date, account, count)
        print(f"Post count for {account}: {count}")
    
    else:
        print(f"Unknown command: {cmd}")


if __name__ == "__main__":
    main()
