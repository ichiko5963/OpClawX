#!/usr/bin/env python3
"""
承認フロー管理スクリプト（v2）
- 構造化ログ
- 各アクションタイプの実行
- Slack投稿サポート
"""

import json
import os
import sys
import urllib.request
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional

# ライブラリパス追加
SCRIPTS_PATH = Path("/Users/ai-driven-work/Library/Mobile Documents/com~apple~CloudDocs/OpenClaw-Shared/scripts")
sys.path.insert(0, str(SCRIPTS_PATH / "lib"))

from structured_logger import get_logger, log_action

# 設定
JST = timezone(timedelta(hours=9))
VAULT_PATH = Path("/Users/ai-driven-work/Library/Mobile Documents/com~apple~CloudDocs/OpenClaw-Shared/obsidian/Ichioka Obsidian")
ACTION_QUEUE_PATH = VAULT_PATH / "00_System/04_ActionQueue"
DRAFTS_PATH = VAULT_PATH / "00_System/06_Drafts"
TASKS_PATH = VAULT_PATH / "07-To Do/Tasks.md"

# ロガー
logger = get_logger("approval")


def get_slack_token() -> Optional[str]:
    """Slackトークンを取得"""
    env_file = Path.home() / ".config/openclaw/secrets/n8n.env"
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                if line.startswith("SLACK_BOT_TOKEN="):
                    return line.strip().split("=", 1)[1]
    return None


def load_pending_commands() -> List[Dict]:
    """pending のコマンドを読み込む"""
    pending_path = ACTION_QUEUE_PATH / "pending"
    commands = []
    
    if pending_path.exists():
        for f in sorted(pending_path.glob("*.json")):
            try:
                with open(f, encoding="utf-8") as fp:
                    cmd = json.load(fp)
                    cmd["_filepath"] = str(f)
                    commands.append(cmd)
            except Exception as e:
                logger.warn(f"Failed to load {f.name}", data={"error": str(e)})
    
    return commands


def approve_command(cmd_id: str, approved_by: str = "ichiko") -> bool:
    """コマンドを承認"""
    pending_path = ACTION_QUEUE_PATH / "pending"
    filepath = pending_path / f"{cmd_id}.json"
    
    if not filepath.exists():
        logger.warn(f"Command not found: {cmd_id}")
        return False
    
    with open(filepath, encoding="utf-8") as f:
        cmd = json.load(f)
    
    now = datetime.now(JST)
    cmd["status"] = "approved"
    cmd["approval"] = {
        "approved": True,
        "approved_by": approved_by,
        "approved_at": now.isoformat(),
    }
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(cmd, f, indent=2, ensure_ascii=False)
    
    log_action(cmd_id, cmd.get("type", "unknown"), "approved", f"Approved by {approved_by}")
    logger.info(f"Command approved", data={"cmd_id": cmd_id, "approved_by": approved_by})
    
    return True


def reject_command(cmd_id: str, reason: str = "", rejected_by: str = "ichiko") -> bool:
    """コマンドを却下"""
    pending_path = ACTION_QUEUE_PATH / "pending"
    processed_path = ACTION_QUEUE_PATH / "processed"
    processed_path.mkdir(parents=True, exist_ok=True)
    
    filepath = pending_path / f"{cmd_id}.json"
    
    if not filepath.exists():
        logger.warn(f"Command not found: {cmd_id}")
        return False
    
    with open(filepath, encoding="utf-8") as f:
        cmd = json.load(f)
    
    now = datetime.now(JST)
    cmd["status"] = "rejected"
    cmd["approval"] = {
        "approved": False,
        "approved_by": rejected_by,
        "approved_at": now.isoformat(),
        "reason": reason,
    }
    
    # processed に移動
    new_filepath = processed_path / f"{cmd_id}.json"
    with open(new_filepath, "w", encoding="utf-8") as f:
        json.dump(cmd, f, indent=2, ensure_ascii=False)
    
    filepath.unlink()
    
    log_action(cmd_id, cmd.get("type", "unknown"), "rejected", f"Rejected by {rejected_by}: {reason}")
    logger.info(f"Command rejected", data={"cmd_id": cmd_id, "reason": reason})
    
    return True


def execute_draft_reply_email(cmd: Dict) -> str:
    """メール返信下書きを作成"""
    DRAFTS_PATH.mkdir(parents=True, exist_ok=True)
    
    context = cmd.get("context", {})
    proposed = cmd.get("proposed_action", {})
    now = datetime.now(JST)
    
    draft_filename = f"email_{cmd['cmd_id']}_{now.strftime('%Y%m%d_%H%M%S')}.md"
    draft_path = DRAFTS_PATH / draft_filename
    
    sensitivity = context.get("sensitivity", "internal")
    
    content = f"""# Email Draft

**To:** {proposed.get('to', '')}
**Subject:** {proposed.get('subject', '')}
**Created:** {now.isoformat()}
**Sensitivity:** {sensitivity}

---

## Original Message

**From:** {context.get('from', '')}
**Subject:** {context.get('subject', '')}

{context.get('snippet', '')}

---

## Draft Reply

_[Write your reply here]_

---

> Note: This is a draft. To send, copy to Gmail and send manually.
> Routing reasons: {', '.join(context.get('routing_reasons', []))}
"""
    
    with open(draft_path, "w", encoding="utf-8") as f:
        f.write(content)
    
    return f"✓ Draft saved to {draft_filename}"


def execute_draft_slack(cmd: Dict) -> str:
    """Slackメッセージを投稿"""
    token = get_slack_token()
    if not token:
        return "✗ Slack token not found"
    
    proposed = cmd.get("proposed_action", {})
    channel = proposed.get("channel", "")
    text = proposed.get("text", "")
    
    if not channel or not text:
        return "✗ Channel or text missing"
    
    # Slack API呼び出し
    url = "https://slack.com/api/chat.postMessage"
    data = json.dumps({"channel": channel, "text": text}).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
    )
    
    try:
        with urllib.request.urlopen(req) as resp:
            result = json.load(resp)
            if result.get("ok"):
                return f"✓ Posted to {channel}"
            else:
                return f"✗ Slack error: {result.get('error', 'unknown')}"
    except Exception as e:
        return f"✗ Request failed: {e}"


def execute_create_calendar_event(cmd: Dict) -> str:
    """カレンダーイベント下書きを作成"""
    DRAFTS_PATH.mkdir(parents=True, exist_ok=True)
    
    proposed = cmd.get("proposed_action", {})
    now = datetime.now(JST)
    
    draft_filename = f"calendar_{cmd['cmd_id']}_{now.strftime('%Y%m%d_%H%M%S')}.md"
    draft_path = DRAFTS_PATH / draft_filename
    
    content = f"""# Calendar Event Draft

**Summary:** {proposed.get('summary', '')}
**Start:** {proposed.get('start', '')}
**End:** {proposed.get('end', '')}
**Location:** {proposed.get('location', '')}
**Description:** {proposed.get('description', '')}
**Created:** {now.isoformat()}

---

> Note: To create, manually add to Google Calendar.
"""
    
    with open(draft_path, "w", encoding="utf-8") as f:
        f.write(content)
    
    return f"✓ Calendar draft saved to {draft_filename}"


def execute_create_task(cmd: Dict) -> str:
    """Obsidianタスクを作成"""
    proposed = cmd.get("proposed_action", {})
    now = datetime.now(JST)
    
    text = proposed.get("text", "New Task")
    priority = proposed.get("priority", "P3")
    project = proposed.get("project", "")
    due_date = proposed.get("due_date", "")
    
    # タスク行を作成
    task_line = f"- [ ] [{priority}] {text}"
    if due_date:
        task_line += f" 📅 {due_date}"
    if project:
        task_line += f" #project/{project}"
    task_line += f" ➕ {now.strftime('%Y-%m-%d')}"
    
    # Tasks.md に追加
    tasks_path = Path(TASKS_PATH)
    tasks_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(tasks_path, "a", encoding="utf-8") as f:
        f.write(task_line + "\n")
    
    return f"✓ Task added to Tasks.md"


def execute_command(cmd: Dict) -> str:
    """コマンドを実行"""
    cmd_type = cmd.get("type", "")
    
    executors = {
        "draft_reply_email": execute_draft_reply_email,
        "draft_slack": execute_draft_slack,
        "create_calendar_event": execute_create_calendar_event,
        "create_task": execute_create_task,
    }
    
    executor = executors.get(cmd_type)
    if executor:
        return executor(cmd)
    else:
        return f"✗ Unknown command type: {cmd_type}"


def process_approved_commands():
    """承認済みコマンドを実行"""
    pending_path = ACTION_QUEUE_PATH / "pending"
    processed_path = ACTION_QUEUE_PATH / "processed"
    processed_path.mkdir(parents=True, exist_ok=True)
    
    commands = load_pending_commands()
    approved = [c for c in commands if c.get("approval", {}).get("approved") == True]
    
    processed_count = 0
    
    for cmd in approved:
        cmd_id = cmd.get("cmd_id", "unknown")
        filepath = Path(cmd.get("_filepath", ""))
        
        print(f"Executing: {cmd_id}")
        logger.info(f"Executing command", data={"cmd_id": cmd_id, "type": cmd.get("type")})
        
        result = execute_command(cmd)
        print(f"  Result: {result}")
        
        # 実行結果を記録
        now = datetime.now(JST)
        cmd["status"] = "executed"
        cmd["execution"] = {
            "executed": True,
            "executed_at": now.isoformat(),
            "result": result,
        }
        
        # ファイルパスを削除
        if "_filepath" in cmd:
            del cmd["_filepath"]
        
        # processed に移動
        new_filepath = processed_path / f"{cmd_id}.json"
        with open(new_filepath, "w", encoding="utf-8") as f:
            json.dump(cmd, f, indent=2, ensure_ascii=False)
        
        if filepath.exists():
            filepath.unlink()
        
        log_action(cmd_id, cmd.get("type", "unknown"), "executed", result)
        logger.info(f"Command executed", data={"cmd_id": cmd_id, "result": result})
        
        processed_count += 1
    
    return processed_count


def show_status():
    """ステータスを表示"""
    commands = load_pending_commands()
    
    waiting = [c for c in commands if c.get("approval", {}).get("approved") is None]
    approved = [c for c in commands if c.get("approval", {}).get("approved") == True]
    
    now = datetime.now(JST)
    print(f"=== 承認フロー管理 ===")
    print(f"Time: {now.isoformat()}")
    print()
    print(f"Pending commands: {len(commands)}")
    print(f"  - Waiting for approval: {len(waiting)}")
    print(f"  - Approved (ready to execute): {len(approved)}")
    
    if waiting:
        print()
        print(f"## 📋 承認待ちコマンド ({len(waiting)}件)")
        for cmd in waiting[:10]:
            cmd_id = cmd.get("cmd_id", "unknown")
            cmd_type = cmd.get("type", "unknown")
            priority = cmd.get("priority", "P3")
            context = cmd.get("context", {})
            snippet = context.get("snippet", "")[:50]
            sensitivity = context.get("sensitivity", "internal")
            
            print()
            print(f"### [{priority}] {cmd_id}")
            print(f"- **Type:** {cmd_type}")
            print(f"- **Status:** pending")
            print(f"- **Sensitivity:** {sensitivity}")
            print(f"- **Snippet:** {snippet}...")
        
        if len(waiting) > 10:
            print(f"\n... 他 {len(waiting) - 10} 件")
        
        print()
        print("---")
        print()
        print("承認するには: `approve_command('cmd_id')`")
        print("却下するには: `reject_command('cmd_id', reason='理由')`")
    
    return len(commands)


def main():
    """メイン処理"""
    logger.info("Approval flow started")
    
    # ステータス表示
    total = show_status()
    
    # 承認済みを処理
    commands = load_pending_commands()
    approved = [c for c in commands if c.get("approval", {}).get("approved") == True]
    
    if approved:
        print()
        print("Processing approved commands...")
        processed = process_approved_commands()
        print(f"✓ Processed {processed} commands")
    
    logger.info("Approval flow completed", data={"total": total, "processed": len(approved)})


if __name__ == "__main__":
    main()
