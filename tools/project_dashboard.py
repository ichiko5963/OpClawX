#!/usr/bin/env python3
"""
プロジェクトダッシュボード生成ツール

機能:
1. Obsidianのプロジェクト情報を集約
2. Google Tasks/Calendarから進捗を取得
3. HTMLダッシュボードを生成
4. Telegram/Discord報告用サマリーを生成

Usage:
    python project_dashboard.py --html
    python project_dashboard.py --summary
    python project_dashboard.py --project AirCle
"""

import argparse
import json
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional

def get_workspace_root() -> Path:
    """ワークスペースルートを取得"""
    return Path('/Users/ai-driven-work/Library/Mobile Documents/com~apple~CloudDocs/OpenClaw-Shared')


def get_obsidian_root() -> Path:
    """Obsidian Vaultのルートを取得"""
    return get_workspace_root() / 'obsidian' / 'Ichioka Obsidian'


def scan_active_projects() -> List[Dict]:
    """アクティブプロジェクトをスキャン"""
    projects_dir = get_obsidian_root() / '03_Projects' / '_Active'
    projects = []
    
    if not projects_dir.exists():
        return projects
    
    for project_path in projects_dir.iterdir():
        if project_path.is_dir() and not project_path.name.startswith('.'):
            project = {
                'name': project_path.name,
                'path': project_path,
                'files': list(project_path.rglob('*.md')),
                'last_modified': None,
                'todos': [],
                'notes': []
            }
            
            # 最終更新日を取得
            file_times = []
            for f in project_path.rglob('*'):
                if f.is_file():
                    file_times.append(f.stat().st_mtime)
            if file_times:
                project['last_modified'] = datetime.fromtimestamp(max(file_times))
            
            # TODOを抽出
            for md_file in project['files']:
                try:
                    content = md_file.read_text(encoding='utf-8')
                    for line in content.split('\n'):
                        if '- [ ]' in line:
                            project['todos'].append(line.strip())
                        elif '- [x]' in line:
                            pass  # 完了済みはスキップ
                except:
                    pass
            
            projects.append(project)
    
    # 最終更新日でソート
    projects.sort(key=lambda x: x['last_modified'] or datetime.min, reverse=True)
    return projects


def scan_people() -> List[Dict]:
    """人物情報をスキャン"""
    people_dir = get_obsidian_root() / '10_People'
    people = []
    
    if not people_dir.exists():
        return people
    
    for person_path in people_dir.iterdir():
        if person_path.is_dir() and not person_path.name.startswith('.'):
            person = {
                'name': person_path.name,
                'path': person_path,
                'profile': None
            }
            
            # PROFILE.mdを読み込み
            profile_path = person_path / 'PROFILE.md'
            if profile_path.exists():
                try:
                    person['profile'] = profile_path.read_text(encoding='utf-8')[:500]
                except:
                    pass
            
            people.append(person)
    
    return people


def scan_companies() -> List[Dict]:
    """企業情報をスキャン"""
    companies_dir = get_obsidian_root() / '11_Companies'
    companies = []
    
    if not companies_dir.exists():
        return companies
    
    for company_path in companies_dir.iterdir():
        if company_path.is_dir() and not company_path.name.startswith('.'):
            company = {
                'name': company_path.name,
                'path': company_path,
                'profile': None
            }
            
            # PROFILE.mdを読み込み
            profile_path = company_path / 'PROFILE.md'
            if profile_path.exists():
                try:
                    company['profile'] = profile_path.read_text(encoding='utf-8')[:500]
                except:
                    pass
            
            companies.append(company)
    
    return companies


def generate_html_dashboard(projects: List[Dict], people: List[Dict], companies: List[Dict]) -> str:
    """HTMLダッシュボードを生成"""
    
    projects_html = ""
    for p in projects[:10]:
        last_mod = p['last_modified'].strftime('%Y-%m-%d') if p['last_modified'] else 'N/A'
        todo_count = len(p['todos'])
        file_count = len(p['files'])
        
        projects_html += f'''
        <div class="project-card">
            <h3>{p['name']}</h3>
            <div class="meta">
                <span>📁 {file_count}ファイル</span>
                <span>📝 {todo_count} TODO</span>
                <span>🕒 {last_mod}</span>
            </div>
            <div class="todos">
                {''.join(f'<div class="todo">{t[:50]}...</div>' for t in p['todos'][:3])}
            </div>
        </div>
        '''
    
    html = f'''<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>プロジェクトダッシュボード</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, sans-serif;
            background: #0a0a0f;
            color: #e0e0e0;
            padding: 2rem;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        h1 {{
            font-size: 2rem;
            margin-bottom: 2rem;
            background: linear-gradient(90deg, #00d4ff, #7b2cbf);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        h2 {{
            font-size: 1.3rem;
            margin: 2rem 0 1rem;
            color: #00d4ff;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }}
        .stat-card {{
            background: rgba(255,255,255,0.05);
            border-radius: 12px;
            padding: 1.5rem;
            text-align: center;
        }}
        .stat-value {{
            font-size: 2.5rem;
            font-weight: 700;
            color: #00d4ff;
        }}
        .stat-label {{
            color: #888;
            font-size: 0.9rem;
        }}
        .projects-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1.5rem;
        }}
        .project-card {{
            background: rgba(255,255,255,0.03);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 12px;
            padding: 1.5rem;
        }}
        .project-card h3 {{
            font-size: 1.1rem;
            margin-bottom: 0.5rem;
        }}
        .meta {{
            display: flex;
            gap: 1rem;
            color: #888;
            font-size: 0.8rem;
            margin-bottom: 1rem;
        }}
        .todos {{
            font-size: 0.85rem;
        }}
        .todo {{
            padding: 0.5rem 0;
            border-bottom: 1px solid rgba(255,255,255,0.05);
            color: #aaa;
        }}
        .footer {{
            margin-top: 3rem;
            text-align: center;
            color: #666;
            font-size: 0.85rem;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 プロジェクトダッシュボード</h1>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-value">{len(projects)}</div>
                <div class="stat-label">アクティブプロジェクト</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{sum(len(p['todos']) for p in projects)}</div>
                <div class="stat-label">未完了TODO</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{len(people)}</div>
                <div class="stat-label">人物プロファイル</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{len(companies)}</div>
                <div class="stat-label">企業プロファイル</div>
            </div>
        </div>
        
        <h2>🚀 アクティブプロジェクト</h2>
        <div class="projects-grid">
            {projects_html}
        </div>
        
        <div class="footer">
            <p>Generated by OpenClaw 🦞 | {datetime.now().strftime('%Y-%m-%d %H:%M')} JST</p>
        </div>
    </div>
</body>
</html>'''
    
    return html


def generate_summary(projects: List[Dict]) -> str:
    """テキストサマリーを生成"""
    
    summary = f"""📊 **プロジェクトダッシュボード** ({datetime.now().strftime('%Y-%m-%d %H:%M')})

**アクティブプロジェクト**: {len(projects)}件
**未完了TODO**: {sum(len(p['todos']) for p in projects)}件

---

**プロジェクト別:**
"""
    
    for p in projects[:5]:
        last_mod = p['last_modified'].strftime('%m/%d') if p['last_modified'] else 'N/A'
        summary += f"\n• **{p['name']}** - {len(p['todos'])} TODO (最終更新: {last_mod})"
    
    if len(projects) > 5:
        summary += f"\n...他 {len(projects) - 5}件"
    
    return summary


def main():
    parser = argparse.ArgumentParser(description='プロジェクトダッシュボード生成')
    parser.add_argument('--html', action='store_true', help='HTMLダッシュボードを生成')
    parser.add_argument('--summary', action='store_true', help='テキストサマリーを出力')
    parser.add_argument('--project', type=str, help='特定プロジェクトの詳細を表示')
    parser.add_argument('--output', type=str, help='出力先ファイル')
    
    args = parser.parse_args()
    
    # データ収集
    print("📊 データ収集中...")
    projects = scan_active_projects()
    people = scan_people()
    companies = scan_companies()
    
    print(f"   プロジェクト: {len(projects)}件")
    print(f"   人物: {len(people)}件")
    print(f"   企業: {len(companies)}件")
    
    if args.project:
        # 特定プロジェクトの詳細
        project = next((p for p in projects if p['name'].lower() == args.project.lower()), None)
        if project:
            print(f"\n📁 **{project['name']}**")
            print(f"   ファイル数: {len(project['files'])}")
            print(f"   TODO: {len(project['todos'])}件")
            if project['todos']:
                print("\n   未完了TODO:")
                for todo in project['todos'][:10]:
                    print(f"   {todo}")
        else:
            print(f"プロジェクト '{args.project}' が見つかりません")
        return 0
    
    if args.html:
        # HTMLダッシュボード生成
        html = generate_html_dashboard(projects, people, companies)
        
        if args.output:
            Path(args.output).write_text(html, encoding='utf-8')
            print(f"\n✅ ダッシュボード保存: {args.output}")
        else:
            output_path = get_workspace_root() / 'public' / 'dashboard.html'
            output_path.write_text(html, encoding='utf-8')
            print(f"\n✅ ダッシュボード保存: {output_path}")
    
    elif args.summary:
        # テキストサマリー
        summary = generate_summary(projects)
        print("\n" + summary)
    
    else:
        # デフォルト: 簡易サマリー
        print(f"\n📊 ダッシュボードサマリー")
        print(f"   アクティブプロジェクト: {len(projects)}")
        print(f"   未完了TODO: {sum(len(p['todos']) for p in projects)}")
        print(f"\n   上位プロジェクト:")
        for p in projects[:5]:
            print(f"   • {p['name']} ({len(p['todos'])} TODO)")
    
    return 0


if __name__ == '__main__':
    exit(main())
