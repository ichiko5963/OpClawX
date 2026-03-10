#!/usr/bin/env python3
"""メールマネージャー (gog CLI対応版)"""
import subprocess
import json
import argparse
from datetime import datetime, timedelta

def get_emails(max_results=50, unread_only=False):
    """Gmailからメール取得"""
    try:
        query = "in:inbox newer_than:1d" if unread_only else "in:inbox"
        result = subprocess.run(
            ['gog', 'gmail', 'search', query, '--max', str(max_results), '--json'],
            capture_output=True, text=True, timeout=60
        )
        
        if result.returncode != 0:
            print(f"メール取得エラー: {result.stderr}")
            return []
            
        emails = json.loads(result.stdout) if result.stdout else []
        return emails
    except Exception as e:
        print(f"メール取得エラー: {e}")
        return []

def process_emails(all_emails=False):
    """メール処理"""
    emails = get_emails(max_results=50, unread_only=not all_emails)
    
    if not emails:
        print("新着メールはありません")
        return {"processed": 0, "needs_reply": 0}
    
    print(f"{len(emails)}件のメールを取得")
    
    # 簡易的分析
    needs_reply = []
    for email in emails:
        subject = email.get('subject', '')
        from_addr = email.get('from', '')
        
        # 返信が必要そうなキーワード
        keywords = ['Re:', 'FW:', '確認', '質問', '依頼', 'お願い']
        if any(kw in subject for kw in keywords):
            needs_reply.append(email)
    
    print(f"返信が必要な候補: {len(needs_reply)}件")
    return {"processed": len(emails), "needs_reply": len(needs_reply)}

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--all', action='store_true')
    args = parser.parse_args()
    
    if args.check:
        process_emails(all_emails=args.all)
