#!/usr/bin/env python3
"""
エラー監視システム
- スクリプト実行エラーを監視
- Slack/Telegramに自動レポート
"""

import json
import sys
import traceback
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import Dict, Optional, List
import urllib.request
import urllib.parse
import urllib.error

# 設定
JST = timezone(timedelta(hours=9))
WORKSPACE = Path("/Users/ai-driven-work/Library/Mobile Documents/com~apple~CloudDocs/OpenClaw-Shared")
STATE_PATH = WORKSPACE / "obsidian/Ichioka Obsidian/00_System/01_State"

# 通知設定（環境変数または設定ファイルから取得）
SLACK_WEBHOOK_URL = None
TELEGRAM_BOT_TOKEN = None
TELEGRAM_CHAT_ID = None


def load_config() -> Dict:
    """設定を読み込み"""
    config_path = STATE_PATH / "error_monitor_config.json"
    if config_path.exists():
        with open(config_path) as f:
            return json.load(f)
    return {}


def init_config():
    """初期設定ファイルを作成"""
    config_path = STATE_PATH / "error_monitor_config.json"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    default_config = {
        "slack_webhook_url": "",
        "telegram_bot_token": "",
        "telegram_chat_id": "",
        "enabled": True,
        "error_log_path": str(STATE_PATH / "error_log.json"),
        "notify_on_retry": True,
        "notify_on_timeout": True,
        "notify_on_critical": True,
    }
    
    if not config_path.exists():
        with open(config_path, 'w') as f:
            json.dump(default_config, f, indent=2)
    
    return default_config


def get_error_level(exit_code: int) -> str:
    """終了コードからエラーレベルを判定"""
    if exit_code == 0:
        return "success"
    elif exit_code == 124:
        return "timeout"
    elif exit_code >= 100:
        return "critical"
    else:
        return "error"


def format_error_message(
    script_name: str,
    error_type: str,
    message: str,
    traceback_str: str = "",
    timestamp: str = None
) -> Dict:
    """エラーメッセージをフォーマット"""
    if timestamp is None:
        timestamp = datetime.now(JST).isoformat()
    
    return {
        "script": script_name,
        "type": error_type,
        "message": message,
        "traceback": traceback_str,
        "timestamp": timestamp,
    }


def send_slack_notification(webhook_url: str, message: Dict, channel: str = "#errors") -> bool:
    """Slackに通知を送信"""
    if not webhook_url:
        return False
    
    level_emoji = {
        "error": "🔴",
        "timeout": "⏰",
        "critical": "🚨",
        "success": "✅",
    }
    
    emoji = level_emoji.get(message.get("type", "error"), "❌")
    
    slack_message = {
        "channel": channel,
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"{emoji} エラー発生: {message['script']}"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*タイプ:*\n{message.get('type', 'unknown')}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": "*タイムスタンプ:*\n{message['timestamp']}"
                    }
                ]
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*メッセージ:*\n```{message.get('message', 'No message')}```"
                }
            }
        ]
    }
    
    if message.get('traceback'):
        slack_message["blocks"].append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*トレースバック:*\n```{message['traceback'][:1000]}```"
            }
        })
    
    try:
        data = json.dumps(slack_message).encode('utf-8')
        req = urllib.request.Request(webhook_url, data=data, method='POST')
        req.add_header('Content-Type', 'application/json')
        with urllib.request.urlopen(req) as response:
            return response.status == 200
    except Exception as e:
        print(f"Slack notification failed: {e}", file=sys.stderr)
        return False


def send_telegram_notification(bot_token: str, chat_id: str, message: Dict) -> bool:
    """Telegramに通知を送信"""
    if not bot_token or not chat_id:
        return False
    
    level_emoji = {
        "error": "🔴",
        "timeout": "⏰",
        "critical": "🚨",
        "success": "✅",
    }
    
    emoji = level_emoji.get(message.get("type", "error"), "❌")
    
    text = f"{emoji} *エラー発生*\n\n"
    text += f"*スクリプト:* {message['script']}\n"
    text += f"*タイプ:* {message.get('type', 'unknown')}\n"
    text += f"*メッセージ:* {message.get('message', 'No message')}\n"
    text += f"*タイムスタンプ:* {message['timestamp']}\n"
    
    if message.get('traceback'):
        text += f"\n*トレースバック:*\n```\n{message['traceback'][:500]}```"
    
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown",
    }
    
    try:
        data_encoded = urllib.parse.urlencode(data).encode('utf-8')
        req = urllib.request.Request(url, data=data_encoded, method='POST')
        with urllib.request.urlopen(req) as response:
            return response.status == 200
    except Exception as e:
        print(f"Telegram notification failed: {e}", file=sys.stderr)
        return False


def log_error(error_log: Dict, log_path: str):
    """エラーログを保存"""
    log_file = Path(log_path)
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    # 既存のログを読み込み
    errors = []
    if log_file.exists():
        try:
            with open(log_file) as f:
                errors = json.load(f)
        except:
            errors = []
    
    # 新しいエラーを追加
    errors.append(error_log)
    
    # 最新100件のみ保持
    errors = errors[-100:]
    
    with open(log_file, 'w') as f:
        json.dump(errors, f, indent=2, ensure_ascii=False)


def report_error(
    script_name: str,
    error_type: str,
    message: str,
    traceback_str: str = "",
    exit_code: int = 1
) -> bool:
    """
    エラーを報告（Slack/Telegramに送信＋ログ保存）
    
    Args:
        script_name: スクリプト名
        error_type: エラータイプ (error/timeout/critical)
        message: エラーメッセージ
        traceback_str: トレースバック文字列
        exit_code: 終了コード
    
    Returns:
        bool: 報告が成功したかどうか
    """
    config = load_config()
    
    # 通知が無効の場合はログのみ
    if not config.get("enabled", True):
        return False
    
    # エラーメッセージを作成
    error_msg = format_error_message(
        script_name=script_name,
        error_type=error_type,
        message=message,
        traceback_str=traceback_str
    )
    
    # ログに保存
    log_path = config.get("error_log_path", str(STATE_PATH / "error_log.json"))
    log_error(error_msg, log_path)
    
    # 通知設定を確認
    if error_type == "timeout" and not config.get("notify_on_timeout", True):
        return True
    if error_type == "error" and not config.get("notify_on_retry", True):
        return True
    if error_type == "critical" and not config.get("notify_on_critical", True):
        return True
    
    # Slackに送信
    success = False
    slack_url = config.get("slack_webhook_url", "") or SLACK_WEBHOOK_URL
    if slack_url:
        send_slack_notification(slack_url, error_msg)
        success = True
    
    # Telegramに送信
    bot_token = config.get("telegram_bot_token", "") or TELEGRAM_BOT_TOKEN
    chat_id = config.get("telegram_chat_id", "") or TELEGRAM_CHAT_ID
    if bot_token and chat_id:
        send_telegram_notification(bot_token, chat_id, error_msg)
        success = True
    
    return success


def catch_errors(script_name: str):
    """
    デコレータ：スクリプトのエラーを自動監視
    
    Usage:
        @catch_errors("my_script_name")
        def main():
            ...
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                tb = traceback.format_exc()
                error_type = get_error_level(sys.exc_info()[1].code if hasattr(e, 'code') else 1)
                report_error(
                    script_name=script_name,
                    error_type=error_type,
                    message=str(e),
                    traceback_str=tb,
                    exit_code=1
                )
                raise
        return wrapper
    return decorator


def run_with_error_handling(script_path: str, args: List[str] = None) -> Dict:
    """
    スクリプトを実行し、エラーを監視
    
    Args:
        script_path: 実行するスクリプトのパス
        args: 引数リスト
    
    Returns:
        Dict: 実行結果
    """
    import subprocess
    
    script_name = Path(script_path).stem
    result = {
        "script": script_name,
        "exit_code": None,
        "stdout": "",
        "stderr": "",
        "timestamp": datetime.now(JST).isoformat(),
    }
    
    try:
        cmd = [sys.executable, script_path]
        if args:
            cmd.extend(args)
        
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120  # 最大2分
        )
        
        result["exit_code"] = proc.returncode
        result["stdout"] = proc.stdout
        result["stderr"] = proc.stderr
        
        # エラーがあれば報告
        if proc.returncode != 0:
            error_level = get_error_level(proc.returncode)
            report_error(
                script_name=script_name,
                error_type=error_level,
                message=proc.stderr if proc.stderr else f"Exit code: {proc.returncode}",
                traceback_str="",
                exit_code=proc.returncode
            )
    
    except subprocess.TimeoutExpired:
        result["exit_code"] = 124
        result["stderr"] = "Timeout"
        report_error(
            script_name=script_name,
            error_type="timeout",
            message="Script execution timed out",
            traceback_str="",
            exit_code=124
        )
    except Exception as e:
        result["exit_code"] = 1
        result["stderr"] = str(e)
        report_error(
            script_name=script_name,
            error_type="error",
            message=str(e),
            traceback_str=traceback.format_exc(),
            exit_code=1
        )
    
    return result


def get_recent_errors(log_path: str = None, limit: int = 10) -> List[Dict]:
    """最近のエラー履歴を取得"""
    if log_path is None:
        config = load_config()
        log_path = config.get("error_log_path", str(STATE_PATH / "error_log.json"))
    
    log_file = Path(log_path)
    if not log_file.exists():
        return []
    
    try:
        with open(log_file) as f:
            errors = json.load(f)
        return errors[-limit:]
    except:
        return []


def clear_error_log(log_path: str = None):
    """エラーログをクリア"""
    if log_path is None:
        config = load_config()
        log_path = config.get("error_log_path", str(STATE_PATH / "error_log.json"))
    
    log_file = Path(log_path)
    if log_file.exists():
        with open(log_file, 'w') as f:
            json.dump([], f)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Error Monitor")
    parser.add_argument("--init", action="store_true", help="Initialize configuration")
    parser.add_argument("--status", action="store_true", help="Show recent errors")
    parser.add_argument("--clear", action="store_true", help="Clear error log")
    parser.add_argument("--test", action="store_true", help="Send test notification")
    parser.add_argument("--run", type=str, help="Run a script with error monitoring")
    parser.add_argument("--args", type=str, help="Arguments for --run (comma-separated)")
    
    args = parser.parse_args()
    
    if args.init:
        config = init_config()
        print("Configuration initialized:")
        print(json.dumps(config, indent=2))
    
    elif args.status:
        errors = get_recent_errors()
        if errors:
            print(f"Recent {len(errors)} errors:")
            for e in errors:
                print(f"  [{e['timestamp']}] {e['script']}: {e['message'][:50]}...")
        else:
            print("No errors logged")
    
    elif args.clear:
        clear_error_log()
        print("Error log cleared")
    
    elif args.test:
        # テスト通知を送信
        test_msg = {
            "script": "test_script",
            "type": "error",
            "message": "This is a test error notification",
            "timestamp": datetime.now(JST).isoformat(),
        }
        
        config = load_config()
        sent = False
        
        if config.get("slack_webhook_url"):
            send_slack_notification(config["slack_webhook_url"], test_msg)
            sent = True
        
        if config.get("telegram_bot_token") and config.get("telegram_chat_id"):
            send_telegram_notification(
                config["telegram_bot_token"],
                config["telegram_chat_id"],
                test_msg
            )
            sent = True
        
        if sent:
            print("Test notification sent!")
        else:
            print("Configure Slack/Telegram in error_monitor_config.json first")
    
    elif args.run:
        script_path = args.run
        script_args = args.args.split(",") if args.args else None
        result = run_with_error_handling(script_path, script_args)
        print(json.dumps(result, indent=2))
    
    else:
        parser.print_help()
