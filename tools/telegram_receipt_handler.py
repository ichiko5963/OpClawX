#!/usr/bin/env python3
"""
Telegram画像受信 → 領収書OCR自動処理
OpenClaw経由で呼び出される想定
"""

import sys
import os
from pathlib import Path

# receipt_ocr.pyをインポート
sys.path.insert(0, str(Path(__file__).parent))
from receipt_ocr import ReceiptProcessor

def process_telegram_image(image_path):
    """Telegramから受信した画像を処理"""
    print("=== Telegram画像受信 ===")
    print(f"画像: {image_path}")
    
    if not Path(image_path).exists():
        print(f"❌ 画像が見つかりません: {image_path}")
        return False
    
    try:
        processor = ReceiptProcessor()
        processor.process_receipt(image_path)
        return True
    except Exception as e:
        print(f"❌ エラー: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: telegram_receipt_handler.py <image_path>")
        sys.exit(1)
    
    image_path = sys.argv[1]
    success = process_telegram_image(image_path)
    
    sys.exit(0 if success else 1)
