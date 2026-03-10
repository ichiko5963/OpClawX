#!/usr/bin/env python3
"""タスクリマインダー (gog CLI対応版)"""
import subprocess
import json
from datetime import datetime, timedelta

def get_tasks():
    """タスクを取得"""
    try:
        result = subprocess.run(
            ['gog', 'tasks', 'list', '--max', '100', '--json'],
            capture_output=True, text=True, timeout=60
        )
        
        if result.returncode != 0:
            print(f"タスク取得エラー: {result.stderr}")
            return []
            
        tasks = json.loads(result.stdout) if result.stdout else []
        return tasks
    except Exception as e:
        print(f"タスク取得エラー: {e}")
        return []

def check_reminders():
    """リマインダーチェック"""
    tasks = get_tasks()
    
    if not tasks:
        print("タスクはありません")
        return
    
    print(f"{len(tasks)}件のタスクを確認")
    
    # 期限切れ・期限近いタスクを検出
    now = datetime.now()
    reminders = []
    
    for task in tasks:
        due = task.get('due')
        if due:
            # 期限チェック（簡易版）
            print(f"- {task.get('title', '無題')}: {due}")

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--send', action='store_true')
    args = parser.parse_args()
    
    check_reminders()
