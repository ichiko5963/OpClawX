#!/usr/bin/env python3
"""
Daily Memory Digest - 日次メモリダイジェストツール
直近のmemory/*.mdファイルを解析し、重要な情報をサマリー化する。
MEMORY.mdに追加すべき項目を提案する。
"""

import os
import re
import sys
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
import json


WORKSPACE = Path(os.environ.get("WORKSPACE", "/Users/ai-driven-work/Documents/OpenClaw-Workspace"))
MEMORY_DIR = WORKSPACE / "memory"
MEMORY_FILE = WORKSPACE / "MEMORY.md"


def get_recent_files(days: int = 7) -> list[Path]:
    """直近N日分のメモリファイルを取得"""
    files = []
    today = datetime.now()
    for i in range(days):
        date = today - timedelta(days=i)
        filename = f"{date.strftime('%Y-%m-%d')}.md"
        filepath = MEMORY_DIR / filename
        if filepath.exists():
            files.append(filepath)
    return files


def parse_memory_file(filepath: Path) -> dict:
    """メモリファイルを解析"""
    content = filepath.read_text(encoding="utf-8")
    
    result = {
        "date": filepath.stem,
        "sections": {},
        "todos": [],
        "decisions": [],
        "issues": [],
        "projects": [],
    }
    
    current_section = "general"
    lines = content.split("\n")
    
    for line in lines:
        # セクションヘッダー
        section_match = re.match(r"^##\s+(.+)$", line)
        if section_match:
            current_section = section_match.group(1).strip()
            if current_section not in result["sections"]:
                result["sections"][current_section] = []
            continue
        
        # 内容行
        if line.strip() and not line.startswith("#"):
            if current_section not in result["sections"]:
                result["sections"][current_section] = []
            result["sections"][current_section].append(line.strip())
        
        # TODO抽出
        if re.search(r"TODO|タスク|やること", line, re.IGNORECASE):
            result["todos"].append(line.strip())
        
        # 決定事項抽出
        if re.search(r"決定|決まった|合意|確定", line):
            result["decisions"].append(line.strip())
        
        # 問題・エラー抽出
        if re.search(r"エラー|問題|障害|バグ|失敗|Error|Issue", line, re.IGNORECASE):
            result["issues"].append(line.strip())
        
        # プロジェクト関連
        if re.search(r"AirCle|ClimbBeyond|SlideBox|Genspark|PLai", line):
            result["projects"].append(line.strip())
    
    return result


def analyze_memory_md() -> dict:
    """MEMORY.mdの現在の構造を分析"""
    if not MEMORY_FILE.exists():
        return {"sections": {}, "last_updated": None}
    
    content = MEMORY_FILE.read_text(encoding="utf-8")
    sections = {}
    current_section = "header"
    
    for line in content.split("\n"):
        section_match = re.match(r"^##\s+(.+)$", line)
        if section_match:
            current_section = section_match.group(1).strip()
            sections[current_section] = []
            continue
        if current_section in sections and line.strip():
            sections[current_section].append(line.strip())
    
    return {"sections": sections}


def generate_digest(days: int = 7) -> str:
    """ダイジェストを生成"""
    files = get_recent_files(days)
    if not files:
        return "直近のメモリファイルが見つかりませんでした。"
    
    all_data = []
    all_todos = []
    all_decisions = []
    all_issues = []
    all_projects = defaultdict(list)
    
    for f in files:
        data = parse_memory_file(f)
        all_data.append(data)
        all_todos.extend([(data["date"], t) for t in data["todos"]])
        all_decisions.extend([(data["date"], d) for d in data["decisions"]])
        all_issues.extend([(data["date"], i) for i in data["issues"]])
        for p in data["projects"]:
            for proj in ["AirCle", "ClimbBeyond", "SlideBox", "Genspark", "PLai"]:
                if proj in p:
                    all_projects[proj].append((data["date"], p))
    
    # 現在のMEMORY.md分析
    memory_analysis = analyze_memory_md()
    
    output = []
    output.append(f"# メモリダイジェスト（直近{days}日分）")
    output.append(f"生成日時: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    output.append(f"対象ファイル: {len(files)}件")
    output.append("")
    
    # 日次サマリー
    output.append("## 日次サマリー")
    for data in all_data:
        output.append(f"\n### {data['date']}")
        for section, lines in data["sections"].items():
            if lines:
                output.append(f"- **{section}**: {'; '.join(lines[:3])}")
    output.append("")
    
    # TODO一覧
    if all_todos:
        output.append("## 未完了TODO（要確認）")
        for date, todo in all_todos:
            output.append(f"- [{date}] {todo}")
        output.append("")
    
    # 決定事項
    if all_decisions:
        output.append("## 決定事項")
        for date, dec in all_decisions:
            output.append(f"- [{date}] {dec}")
        output.append("")
    
    # 問題・エラー
    if all_issues:
        output.append("## 継続中の問題")
        for date, issue in all_issues:
            output.append(f"- [{date}] {issue}")
        output.append("")
    
    # プロジェクト動向
    if all_projects:
        output.append("## プロジェクト動向")
        for proj, entries in all_projects.items():
            output.append(f"\n### {proj}")
            for date, entry in entries:
                output.append(f"- [{date}] {entry}")
        output.append("")
    
    # MEMORY.md更新提案
    output.append("## MEMORY.md更新提案")
    output.append("以下の情報をMEMORY.mdに追加/更新することを推奨:")
    
    if all_decisions:
        output.append("- [ ] 新しい決定事項を「Important Decisions」セクションに追加")
    if all_issues:
        output.append("- [ ] 「Known Issues」セクションのステータス更新")
    if all_projects:
        output.append("- [ ] 「Active Projects」セクションの進捗更新")
    
    output.append("")
    
    return "\n".join(output)


def main():
    days = int(sys.argv[1]) if len(sys.argv) > 1 else 7
    digest = generate_digest(days)
    print(digest)
    
    # ファイルにも保存
    output_file = MEMORY_DIR / f"digest-{datetime.now().strftime('%Y-%m-%d')}.md"
    output_file.write_text(digest, encoding="utf-8")
    print(f"\n✅ ダイジェスト保存: {output_file}")


if __name__ == "__main__":
    main()
