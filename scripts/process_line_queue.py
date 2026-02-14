#!/usr/bin/env python3
"""
LINEキュー処理（OpenClaw経由）
定期的にキューをチェック → Claude分析 → Sheet追記 → LINE通知
"""

import sys
import json
from pathlib import Path

WORKSPACE = Path.home() / "Documents/OpenClaw-Workspace"
QUEUE_DIR = WORKSPACE / "data/line_queue"

def process_line_queue():
    """キュー処理メイン"""
    print("=== LINEキュー処理開始 ===")
    
    if not QUEUE_DIR.exists():
        print("キューディレクトリなし")
        return
    
    queue_files = sorted(QUEUE_DIR.glob("*.json"))
    pending_files = [f for f in queue_files if 'pending' in f.read_text()]
    
    if not pending_files:
        print("処理対象なし")
        return
    
    print(f"{len(pending_files)}件のキュー発見")
    
    for queue_file in pending_files:
        try:
            print(f"\n処理中: {queue_file.name}")
            
            # キュー読み込み
            queue_data = json.loads(queue_file.read_text())
            
            print(f"  Drive URL: {queue_data['drive_url']}")
            print(f"  画像パス: {queue_data['image_path']}")
            
            # ここでOpenClawのimageツールを使って画像分析を依頼
            # OpenClawが実行するので、このスクリプト自体は「処理待ち」をマーク
            
            # ステータス更新
            queue_data['status'] = 'processing'
            queue_file.write_text(json.dumps(queue_data, ensure_ascii=False, indent=2))
            
            print(f"  → Claude分析待ちにマーク")
            
        except Exception as e:
            print(f"  ❌ エラー: {e}")
    
    print("\n✅ キューチェック完了")
    print("Claude分析が必要なファイルがあります")
    print("OpenClawのメインセッションで処理してください")

if __name__ == "__main__":
    process_line_queue()
