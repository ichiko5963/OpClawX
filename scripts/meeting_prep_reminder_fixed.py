#!/usr/bin/env python3
"""MTG準備リマインダー (gog CLI対応版)"""
import subprocess
import json
from datetime import datetime, timedelta, timezone

def check_and_send_reminders(dry_run=False):
    """MTG準備リマインダーチェック"""
    try:
        now = datetime.now(timezone.utc)
        time_min = now.strftime('%Y-%m-%dT%H:%M:%S')
        time_max = (now + timedelta(hours=2.5)).strftime('%Y-%m-%dT%H:%M:%S')
        
        result = subprocess.run(
            ['gog', 'calendar', 'events', 'primary', 
             '--from', time_min, '--to', time_max, '--json'],
            capture_output=True, text=True, timeout=60
        )
        
        if result.returncode != 0:
            print(f"カレンダー取得エラー: {result.stderr}")
            return False
            
        events = json.loads(result.stdout) if result.stdout else []
        
        if not events:
            print("2時間以内のMTGはありません")
            return True
            
        print(f"{len(events)}件のMTGが見つかりました")
        for event in events:
            print(f"- {event.get('summary', '無題')}: {event.get('start', {}).get('dateTime', '時間不明')}")
            
        return True
        
    except Exception as e:
        print(f"MTG準備チェックエラー: {e}")
        return False

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    
    if args.check:
        check_and_send_reminders(dry_run=args.dry_run)
