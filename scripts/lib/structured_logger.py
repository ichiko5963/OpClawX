"""
構造化ログライブラリ
- JSON Lines形式
- ログレベル対応
- 自動ローテーション
- コンテキスト追跡
"""

import json
import os
import traceback
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional
from contextlib import contextmanager
import time

# 設定
JST = timezone(timedelta(hours=9))
DEFAULT_LOGS_PATH = Path("/Users/ai-driven-work/Library/Mobile Documents/com~apple~CloudDocs/OpenClaw-Shared/obsidian/Ichioka Obsidian/00_System/05_Logs")

# ログレベル
LOG_LEVELS = {
    "DEBUG": 10,
    "INFO": 20,
    "WARN": 30,
    "ERROR": 40,
    "CRITICAL": 50,
}


class StructuredLogger:
    """構造化ログを出力するロガー"""
    
    def __init__(
        self,
        name: str,
        logs_path: Path = DEFAULT_LOGS_PATH,
        min_level: str = "INFO",
        max_file_size_mb: int = 10,
        rotate_daily: bool = True,
    ):
        self.name = name
        self.logs_path = logs_path
        self.min_level = LOG_LEVELS.get(min_level.upper(), 20)
        self.max_file_size_bytes = max_file_size_mb * 1024 * 1024
        self.rotate_daily = rotate_daily
        self.context: Dict[str, Any] = {}
        
        # ログディレクトリ作成
        self.logs_path.mkdir(parents=True, exist_ok=True)
    
    def _get_log_file(self, level: str) -> Path:
        """ログファイルパスを取得（ローテーション考慮）"""
        if self.rotate_daily:
            today = datetime.now(JST).strftime("%Y-%m-%d")
            filename = f"{self.name}_{today}.jsonl"
        else:
            filename = f"{self.name}.jsonl"
        
        filepath = self.logs_path / filename
        
        # サイズチェック（ローテーション）
        if filepath.exists() and filepath.stat().st_size > self.max_file_size_bytes:
            # 古いファイルをリネーム
            timestamp = datetime.now(JST).strftime("%H%M%S")
            archived = self.logs_path / f"{self.name}_{today}_{timestamp}.jsonl"
            filepath.rename(archived)
        
        return filepath
    
    def _format_entry(
        self,
        level: str,
        message: str,
        data: Optional[Dict] = None,
        error: Optional[Exception] = None,
    ) -> Dict:
        """ログエントリを構造化"""
        now = datetime.now(JST)
        
        entry = {
            "timestamp": now.isoformat(),
            "level": level,
            "logger": self.name,
            "message": message,
        }
        
        # コンテキスト追加
        if self.context:
            entry["context"] = self.context.copy()
        
        # 追加データ
        if data:
            entry["data"] = data
        
        # エラー情報
        if error:
            entry["error"] = {
                "type": type(error).__name__,
                "message": str(error),
                "traceback": traceback.format_exc(),
            }
        
        return entry
    
    def _write(self, level: str, entry: Dict):
        """ログを書き込み"""
        if LOG_LEVELS.get(level, 20) < self.min_level:
            return
        
        filepath = self._get_log_file(level)
        
        with open(filepath, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    
    def set_context(self, **kwargs):
        """コンテキストを設定"""
        self.context.update(kwargs)
    
    def clear_context(self):
        """コンテキストをクリア"""
        self.context = {}
    
    @contextmanager
    def context_scope(self, **kwargs):
        """一時的なコンテキストスコープ"""
        old_context = self.context.copy()
        self.context.update(kwargs)
        try:
            yield
        finally:
            self.context = old_context
    
    @contextmanager
    def timer(self, operation: str):
        """処理時間を計測"""
        start = time.time()
        try:
            yield
        finally:
            duration_ms = (time.time() - start) * 1000
            self.info(f"{operation} completed", data={"duration_ms": round(duration_ms, 2)})
    
    def debug(self, message: str, data: Optional[Dict] = None):
        """DEBUGログ"""
        entry = self._format_entry("DEBUG", message, data)
        self._write("DEBUG", entry)
    
    def info(self, message: str, data: Optional[Dict] = None):
        """INFOログ"""
        entry = self._format_entry("INFO", message, data)
        self._write("INFO", entry)
    
    def warn(self, message: str, data: Optional[Dict] = None):
        """WARNログ"""
        entry = self._format_entry("WARN", message, data)
        self._write("WARN", entry)
    
    def error(self, message: str, error: Optional[Exception] = None, data: Optional[Dict] = None):
        """ERRORログ"""
        entry = self._format_entry("ERROR", message, data, error)
        self._write("ERROR", entry)
        
        # エラーは専用ファイルにも記録
        error_file = self.logs_path / f"errors_{datetime.now(JST).strftime('%Y-%m-%d')}.jsonl"
        with open(error_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    
    def critical(self, message: str, error: Optional[Exception] = None, data: Optional[Dict] = None):
        """CRITICALログ"""
        entry = self._format_entry("CRITICAL", message, data, error)
        self._write("CRITICAL", entry)
        
        # エラーファイルにも記録
        error_file = self.logs_path / f"errors_{datetime.now(JST).strftime('%Y-%m-%d')}.jsonl"
        with open(error_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")


# シングルトンロガーインスタンス
_loggers: Dict[str, StructuredLogger] = {}


def get_logger(name: str, **kwargs) -> StructuredLogger:
    """ロガーを取得（シングルトン）"""
    if name not in _loggers:
        _loggers[name] = StructuredLogger(name, **kwargs)
    return _loggers[name]


# 便利なデフォルトロガー
ingest_logger = get_logger("ingest")
actions_logger = get_logger("actions")
errors_logger = get_logger("errors", min_level="ERROR")


def log_ingest_event(
    source: str,
    event_id: str,
    status: str,
    message: str = "",
    data: Optional[Dict] = None,
):
    """Ingestイベントをログ"""
    with ingest_logger.context_scope(source=source, event_id=event_id):
        if status == "success":
            ingest_logger.info(message or "Event ingested", data)
        elif status == "skipped":
            ingest_logger.debug(message or "Event skipped", data)
        elif status == "error":
            ingest_logger.error(message or "Ingest error", data=data)


def log_action(
    cmd_id: str,
    action_type: str,
    status: str,
    message: str = "",
    data: Optional[Dict] = None,
    error: Optional[Exception] = None,
):
    """アクションをログ"""
    with actions_logger.context_scope(cmd_id=cmd_id, action_type=action_type):
        if status == "pending":
            actions_logger.info(message or "Action pending", data)
        elif status == "approved":
            actions_logger.info(message or "Action approved", data)
        elif status == "rejected":
            actions_logger.info(message or "Action rejected", data)
        elif status == "executed":
            actions_logger.info(message or "Action executed", data)
        elif status == "failed":
            actions_logger.error(message or "Action failed", error, data)


# テスト用
if __name__ == "__main__":
    logger = get_logger("test")
    
    logger.info("Test log", data={"key": "value"})
    
    with logger.context_scope(user="ichiko", session="test123"):
        logger.info("With context")
        
        with logger.timer("test operation"):
            time.sleep(0.1)
    
    try:
        raise ValueError("Test error")
    except Exception as e:
        logger.error("Error occurred", error=e, data={"context": "test"})
    
    print("✓ Logger test complete")
