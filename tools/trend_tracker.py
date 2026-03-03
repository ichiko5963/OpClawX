#!/usr/bin/env python3
"""
Trend Tracker v1.0
AI・テック業界のトレンドを追跡し、投稿ネタの鮮度を管理するツール。
過去に取り上げたネタ、未使用のネタ、トレンドの継続性を可視化。

Usage:
  python3 tools/trend_tracker.py status            # 現在のトレンド状況
  python3 tools/trend_tracker.py add <topic> <src>  # 新トレンド追加
  python3 tools/trend_tracker.py used <topic>       # 使用済みマーク
  python3 tools/trend_tracker.py suggest            # 未使用ネタ提案
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timedelta

WORKSPACE = Path("/Users/ai-driven-work/Documents/OpenClaw-Workspace")
TRACKER_FILE = WORKSPACE / "memory" / "trend-tracker.json"


def load_tracker() -> dict:
    """トラッカーデータ読み込み"""
    if TRACKER_FILE.exists():
        return json.loads(TRACKER_FILE.read_text(encoding="utf-8"))
    return {
        "version": "1.0",
        "last_updated": datetime.now().isoformat(),
        "trends": [],
        "categories": {
            "ai_coding": "AIコーディングツール",
            "ai_marketing": "AIマーケティング",
            "ai_startup": "AIスタートアップ",
            "x_algorithm": "Xアルゴリズム",
            "product_growth": "プロダクトグロース",
            "ai_agents": "AIエージェント",
            "ai_infra": "AIインフラ",
        }
    }


def save_tracker(data: dict):
    """トラッカーデータ保存"""
    data["last_updated"] = datetime.now().isoformat()
    TRACKER_FILE.parent.mkdir(parents=True, exist_ok=True)
    TRACKER_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def add_trend(data: dict, topic: str, source: str, category: str = "ai_coding"):
    """新トレンド追加"""
    trend = {
        "topic": topic,
        "source": source,
        "category": category,
        "added": datetime.now().isoformat(),
        "used": False,
        "used_date": None,
        "used_in": None,
        "freshness": "hot",  # hot, warm, cold
    }
    data["trends"].append(trend)
    save_tracker(data)
    print(f"✅ トレンド追加: {topic}")


def mark_used(data: dict, topic: str, used_in: str = None):
    """使用済みマーク"""
    for t in data["trends"]:
        if topic.lower() in t["topic"].lower():
            t["used"] = True
            t["used_date"] = datetime.now().isoformat()
            t["used_in"] = used_in
            save_tracker(data)
            print(f"✅ 使用済み: {t['topic']}")
            return
    print(f"❌ 見つかりません: {topic}")


def show_status(data: dict):
    """現在の状況表示"""
    now = datetime.now()
    print(f"\n{'='*60}")
    print(f"📊 トレンドトラッカー状況")
    print(f"{'='*60}")
    print(f"最終更新: {data.get('last_updated', 'N/A')}")
    
    total = len(data["trends"])
    used = sum(1 for t in data["trends"] if t["used"])
    unused = total - used
    
    print(f"📝 総トレンド: {total}")
    print(f"✅ 使用済み: {used}")
    print(f"🆕 未使用: {unused}")
    
    # カテゴリ別
    cats = {}
    for t in data["trends"]:
        cat = t.get("category", "other")
        if cat not in cats:
            cats[cat] = {"total": 0, "used": 0}
        cats[cat]["total"] += 1
        if t["used"]:
            cats[cat]["used"] += 1
    
    if cats:
        print(f"\n📋 カテゴリ別:")
        cat_labels = data.get("categories", {})
        for cat, counts in sorted(cats.items()):
            label = cat_labels.get(cat, cat)
            print(f"  {label}: {counts['used']}/{counts['total']} 使用")
    
    # 未使用トレンド一覧
    unused_trends = [t for t in data["trends"] if not t["used"]]
    if unused_trends:
        print(f"\n🆕 未使用トレンド:")
        for t in unused_trends[-10:]:
            age = ""
            try:
                added = datetime.fromisoformat(t["added"])
                days = (now - added).days
                if days == 0:
                    age = "(今日)"
                elif days == 1:
                    age = "(昨日)"
                else:
                    age = f"({days}日前)"
            except:
                pass
            print(f"  • {t['topic']} {age}")


def suggest(data: dict, count: int = 5):
    """未使用ネタ提案"""
    unused = [t for t in data["trends"] if not t["used"]]
    if not unused:
        print("📭 未使用のトレンドがありません")
        return
    
    # 新しい順
    unused.sort(key=lambda t: t.get("added", ""), reverse=True)
    
    print(f"\n💡 投稿ネタ提案 (上位{min(count, len(unused))}件):")
    for t in unused[:count]:
        cat_labels = data.get("categories", {})
        cat = cat_labels.get(t.get("category", ""), t.get("category", ""))
        print(f"  📌 {t['topic']}")
        print(f"     カテゴリ: {cat} | ソース: {t['source']}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 trend_tracker.py {status|add|used|suggest}")
        sys.exit(1)
    
    action = sys.argv[1]
    data = load_tracker()
    
    if action == "status":
        show_status(data)
    elif action == "add":
        if len(sys.argv) < 4:
            print("Usage: python3 trend_tracker.py add <topic> <source> [category]")
            sys.exit(1)
        topic = sys.argv[2]
        source = sys.argv[3]
        category = sys.argv[4] if len(sys.argv) > 4 else "ai_coding"
        add_trend(data, topic, source, category)
    elif action == "used":
        if len(sys.argv) < 3:
            print("Usage: python3 trend_tracker.py used <topic>")
            sys.exit(1)
        mark_used(data, sys.argv[2])
    elif action == "suggest":
        count = int(sys.argv[2]) if len(sys.argv) > 2 else 5
        suggest(data, count)
    else:
        print(f"Unknown action: {action}")
        sys.exit(1)


if __name__ == "__main__":
    main()
