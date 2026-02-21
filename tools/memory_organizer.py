#!/usr/bin/env python3
"""
メモリ整理ツール
memory/ ディレクトリの日次ファイルを分析し、整理状況をレポート
- 欠落日の検出
- 重複情報の特定
- MEMORY.mdとの整合性チェック
"""

import os
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path
from collections import Counter

WORKSPACE = "/Users/ai-driven-work/Documents/OpenClaw-Workspace"
MEMORY_DIR = os.path.join(WORKSPACE, "memory")
MEMORY_MD = os.path.join(WORKSPACE, "MEMORY.md")


def get_daily_files() -> dict:
    """日付付きメモリファイルを取得"""
    files = {}
    if not os.path.exists(MEMORY_DIR):
        return files
    
    for f in os.listdir(MEMORY_DIR):
        match = re.match(r"(\d{4}-\d{2}-\d{2})\.md", f)
        if match:
            date_str = match.group(1)
            filepath = os.path.join(MEMORY_DIR, f)
            size = os.path.getsize(filepath)
            files[date_str] = {
                "path": filepath,
                "size": size,
                "date": datetime.strptime(date_str, "%Y-%m-%d"),
            }
    
    return files


def find_missing_dates(files: dict) -> list:
    """欠落している日付を検出"""
    if not files:
        return []
    
    dates = sorted([info["date"] for info in files.values()])
    start = dates[0]
    end = dates[-1]
    
    missing = []
    current = start
    while current <= end:
        date_str = current.strftime("%Y-%m-%d")
        if date_str not in files:
            missing.append(date_str)
        current += timedelta(days=1)
    
    return missing


def analyze_content(files: dict) -> dict:
    """ファイル内容を分析"""
    keywords = Counter()
    headings = Counter()
    total_chars = 0
    
    for date_str, info in files.items():
        content = Path(info["path"]).read_text(encoding="utf-8")
        total_chars += len(content)
        
        # ## 見出しを抽出
        for match in re.finditer(r"^## (.+)$", content, re.MULTILINE):
            headings[match.group(1).strip()] += 1
        
        # キーワード抽出（日本語は簡易的に）
        for word in ["AirCle", "ClimbBeyond", "Genspark", "SlideBox", 
                      "議事録", "投稿", "ツール", "エラー", "修正",
                      "Claude", "Cursor", "Obsidian", "Discord", "Telegram",
                      "請求書", "カレンダー", "メール"]:
            count = content.count(word)
            if count > 0:
                keywords[word] += count
    
    return {
        "total_chars": total_chars,
        "keywords": keywords.most_common(20),
        "headings": headings.most_common(20),
    }


def check_memory_md() -> dict:
    """MEMORY.mdの状態チェック"""
    if not os.path.exists(MEMORY_MD):
        return {"exists": False}
    
    content = Path(MEMORY_MD).read_text(encoding="utf-8")
    
    sections = re.findall(r"^## (.+)$", content, re.MULTILINE)
    line_count = len(content.split("\n"))
    char_count = len(content)
    
    # 最終更新日の検出
    dates = re.findall(r"(\d{4}-\d{2}-\d{2})", content)
    latest_date = max(dates) if dates else "不明"
    
    return {
        "exists": True,
        "sections": sections,
        "line_count": line_count,
        "char_count": char_count,
        "latest_date": latest_date,
    }


def generate_report() -> str:
    """レポート生成"""
    report = []
    report.append("# 🧠 メモリ整理レポート")
    report.append(f"**分析日時**: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    report.append("")
    
    # 日次ファイル分析
    files = get_daily_files()
    report.append(f"## 📁 日次ファイル")
    report.append(f"- ファイル数: {len(files)}件")
    
    if files:
        sorted_dates = sorted(files.keys())
        report.append(f"- 期間: {sorted_dates[0]} ～ {sorted_dates[-1]}")
        
        # サイズ統計
        sizes = [info["size"] for info in files.values()]
        report.append(f"- 合計サイズ: {sum(sizes):,} bytes")
        report.append(f"- 平均サイズ: {sum(sizes)//len(sizes):,} bytes")
        report.append(f"- 最大: {max(sizes):,} bytes")
        report.append(f"- 最小: {min(sizes):,} bytes")
        
        # 欠落日
        missing = find_missing_dates(files)
        if missing:
            report.append(f"\n### ⚠️ 欠落日 ({len(missing)}日)")
            for date in missing[-10:]:  # 直近10件のみ
                report.append(f"  - {date}")
            if len(missing) > 10:
                report.append(f"  - ...他 {len(missing)-10}日")
        else:
            report.append("\n✅ 欠落日なし")
    
    report.append("")
    
    # MEMORY.md チェック
    memory_info = check_memory_md()
    report.append("## 📝 MEMORY.md")
    if memory_info["exists"]:
        report.append(f"- 行数: {memory_info['line_count']}")
        report.append(f"- 文字数: {memory_info['char_count']:,}")
        report.append(f"- セクション数: {len(memory_info['sections'])}")
        report.append(f"- 最新日付参照: {memory_info['latest_date']}")
        report.append(f"- セクション一覧:")
        for section in memory_info["sections"]:
            report.append(f"  - {section}")
    else:
        report.append("❌ MEMORY.md が見つかりません")
    
    report.append("")
    
    # コンテンツ分析
    if files:
        analysis = analyze_content(files)
        report.append("## 📊 コンテンツ分析")
        report.append(f"- 総文字数: {analysis['total_chars']:,}")
        
        if analysis["keywords"]:
            report.append("\n### 頻出キーワード")
            for word, count in analysis["keywords"][:10]:
                report.append(f"  - {word}: {count}回")
        
        if analysis["headings"]:
            report.append("\n### 頻出見出し")
            for heading, count in analysis["headings"][:10]:
                report.append(f"  - {heading}: {count}回")
    
    report.append("")
    
    # 推奨アクション
    report.append("## 🎯 推奨アクション")
    actions = []
    
    if files:
        missing = find_missing_dates(files)
        if missing:
            actions.append(f"- [ ] 欠落日 {len(missing)}日分の記録を確認")
        
        # 古い日付のファイルチェック
        today = datetime.now()
        old_files = [d for d, info in files.items() 
                     if (today - info["date"]).days > 30]
        if old_files:
            actions.append(f"- [ ] 30日以上前のファイル {len(old_files)}件をMEMORY.mdに統合検討")
    
    if memory_info["exists"]:
        if memory_info["char_count"] > 10000:
            actions.append("- [ ] MEMORY.mdが大きい（要整理）")
        if memory_info["latest_date"] < (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"):
            actions.append("- [ ] MEMORY.mdの更新が1週間以上前")
    
    if not actions:
        actions.append("✅ 特になし。メモリは良好な状態です。")
    
    report.extend(actions)
    
    return "\n".join(report)


if __name__ == "__main__":
    print(generate_report())
