#!/usr/bin/env python3
"""
Google Tasks 管理スクリプト
- タスクの取得・追加・更新
- n8n経由または直接API
"""

import json
import os
import sys
import urllib.request
import urllib.error
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
TASKS_CACHE_PATH = VAULT_PATH / "00_System/01_State/google_tasks.json"
PENDING_TASKS_PATH = VAULT_PATH / "00_System/04_ActionQueue/pending_tasks"

# ロガー
logger = get_logger("google_tasks")


class GoogleTasksManager:
    """Google Tasks 管理クラス"""
    
    def __init__(self):
        self.tasks_cache = self._load_cache()
        self.pending_tasks = self._load_pending_tasks()
    
    def _load_cache(self) -> Dict:
        """キャッシュを読み込み"""
        if TASKS_CACHE_PATH.exists():
            with open(TASKS_CACHE_PATH, encoding="utf-8") as f:
                return json.load(f)
        return {"tasks": [], "last_sync": None, "task_lists": []}
    
    def _save_cache(self):
        """キャッシュを保存"""
        TASKS_CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(TASKS_CACHE_PATH, "w", encoding="utf-8") as f:
            json.dump(self.tasks_cache, f, indent=2, ensure_ascii=False)
    
    def _load_pending_tasks(self) -> List[Dict]:
        """追加待ちタスクを読み込み"""
        PENDING_TASKS_PATH.mkdir(parents=True, exist_ok=True)
        tasks = []
        for f in PENDING_TASKS_PATH.glob("*.json"):
            try:
                with open(f, encoding="utf-8") as fp:
                    tasks.append(json.load(fp))
            except:
                continue
        return tasks
    
    def add_pending_task(
        self,
        title: str,
        notes: str = "",
        due_date: Optional[str] = None,
        source_event_id: Optional[str] = None,
        priority: str = "P3",
    ) -> Dict:
        """タスクを追加待ちリストに追加"""
        now = datetime.now(JST)
        
        task = {
            "id": f"pending_{now.strftime('%Y%m%d_%H%M%S')}_{hash(title) % 10000:04d}",
            "title": title,
            "notes": notes,
            "due_date": due_date,
            "source_event_id": source_event_id,
            "priority": priority,
            "status": "pending_approval",
            "created_at": now.isoformat(),
        }
        
        filepath = PENDING_TASKS_PATH / f"{task['id']}.json"
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(task, f, indent=2, ensure_ascii=False)
        
        self.pending_tasks.append(task)
        logger.info(f"Added pending task", data={"id": task["id"], "title": title})
        
        return task
    
    def approve_task(self, task_id: str) -> bool:
        """タスクを承認（Google Tasksに追加）"""
        filepath = PENDING_TASKS_PATH / f"{task_id}.json"
        
        if not filepath.exists():
            return False
        
        with open(filepath, encoding="utf-8") as f:
            task = json.load(f)
        
        # TODO: 実際にGoogle Tasks APIに追加
        # 今は内部キャッシュに追加
        now = datetime.now(JST)
        task["status"] = "approved"
        task["approved_at"] = now.isoformat()
        
        # キャッシュに追加
        self.tasks_cache["tasks"].append({
            "id": task["id"],
            "title": task["title"],
            "notes": task.get("notes", ""),
            "due": task.get("due_date"),
            "status": "needsAction",
            "added_at": now.isoformat(),
        })
        self._save_cache()
        
        # pending から削除
        filepath.unlink()
        
        logger.info(f"Task approved", data={"id": task_id, "title": task["title"]})
        
        return True
    
    def reject_task(self, task_id: str, reason: str = "") -> bool:
        """タスクを却下"""
        filepath = PENDING_TASKS_PATH / f"{task_id}.json"
        
        if not filepath.exists():
            return False
        
        # 削除
        filepath.unlink()
        
        logger.info(f"Task rejected", data={"id": task_id, "reason": reason})
        
        return True
    
    def list_pending_tasks(self) -> List[Dict]:
        """承認待ちタスクを一覧"""
        return self._load_pending_tasks()
    
    def list_active_tasks(self) -> List[Dict]:
        """アクティブなタスクを一覧"""
        return [t for t in self.tasks_cache.get("tasks", []) if t.get("status") == "needsAction"]
    
    def complete_task(self, task_id: str) -> bool:
        """タスクを完了"""
        for task in self.tasks_cache.get("tasks", []):
            if task["id"] == task_id:
                task["status"] = "completed"
                task["completed_at"] = datetime.now(JST).isoformat()
                self._save_cache()
                logger.info(f"Task completed", data={"id": task_id})
                return True
        return False
    
    def extract_tasks_from_text(self, text: str) -> List[Dict]:
        """テキストからタスクを抽出"""
        task_patterns = [
            r"TODO[：:]\s*(.+)",
            r"タスク[：:]\s*(.+)",
            r"やること[：:]\s*(.+)",
            r"アクション[：:]\s*(.+)",
            r"- \[ \]\s*(.+)",  # Markdown checkbox
            r"□\s*(.+)",
        ]
        
        import re
        tasks = []
        
        for pattern in task_patterns:
            matches = re.findall(pattern, text, re.MULTILINE | re.IGNORECASE)
            for match in matches:
                tasks.append({
                    "title": match.strip(),
                    "extracted_from": pattern,
                })
        
        return tasks
    
    def suggest_tasks_from_events(self, events: List[Dict]) -> List[Dict]:
        """イベントからタスク候補を提案"""
        suggestions = []
        
        for event in events:
            signals = event.get("signals", {})
            
            # アクション必要なものはタスク候補
            if signals.get("action_required"):
                source = event.get("source", "")
                title = event.get("title", "") or event.get("body", "")[:50]
                
                suggestions.append({
                    "title": f"[{source}] {title}",
                    "notes": event.get("body", "")[:200],
                    "source_event_id": event.get("event_id"),
                    "priority": signals.get("priority", "P3"),
                    "reason": "action_required",
                })
        
        return suggestions


def show_status():
    """ステータスを表示"""
    manager = GoogleTasksManager()
    
    pending = manager.list_pending_tasks()
    active = manager.list_active_tasks()
    
    print("=== Google Tasks 状況 ===\n")
    
    print(f"📋 承認待ち: {len(pending)}件")
    for task in pending[:5]:
        print(f"  - [{task.get('priority', 'P3')}] {task['title']}")
    
    print(f"\n✅ アクティブ: {len(active)}件")
    for task in active[:5]:
        print(f"  - {task['title']}")
    
    if pending:
        print("\n---")
        print("承認: approve_task('task_id')")
        print("却下: reject_task('task_id')")


def main():
    """メイン処理"""
    show_status()


if __name__ == "__main__":
    main()
