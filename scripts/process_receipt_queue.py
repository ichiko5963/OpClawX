#!/usr/bin/env python3
"""
領収書キュー処理
GitHub Actionsが保存したキューを処理してスプレッドシート追加
"""

import sys
import json
from pathlib import Path

# expense_auto_v2.pyを使う
sys.path.insert(0, str(Path(__file__).parent.parent / 'tools'))

WORKSPACE = Path.home() / "Documents/OpenClaw-Workspace"
QUEUE_DIR = WORKSPACE / "data/receipt_queue"

def process_queue():
    """キューを処理"""
    print("=== 領収書キュー処理 ===")
    
    if not QUEUE_DIR.exists():
        print("キューディレクトリなし")
        return
    
    queue_files = sorted(QUEUE_DIR.glob("*.json"))
    
    if not queue_files:
        print("処理対象なし")
        return
    
    print(f"{len(queue_files)}件のキュー発見")
    
    processed = []
    failed = []
    
    for queue_file in queue_files:
        try:
            print(f"\n処理中: {queue_file.name}")
            
            # キュー読み込み
            receipt_info = json.loads(queue_file.read_text())
            
            print(f"  件名: {receipt_info.get('email_subject')}")
            print(f"  Drive: {receipt_info.get('drive_url')}")
            
            # TODO: Claudeで画像分析
            # 今はスキップして、手動処理待ちリストに追加
            
            print(f"  ✓ 処理待ちリストに追加")
            
            # 処理済みに移動
            processed_dir = QUEUE_DIR / "processed"
            processed_dir.mkdir(exist_ok=True)
            
            new_path = processed_dir / queue_file.name
            queue_file.rename(new_path)
            
            processed.append(queue_file.name)
            
        except Exception as e:
            print(f"  ❌ エラー: {e}")
            failed.append(queue_file.name)
    
    print(f"\n✅ 処理完了: {len(processed)}件")
    if failed:
        print(f"❌ 失敗: {len(failed)}件")

if __name__ == "__main__":
    process_queue()
