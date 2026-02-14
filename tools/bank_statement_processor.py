#!/usr/bin/env python3
"""
銀行明細PDF処理（完全版）
- PDFからテキスト抽出
- 入金/支出判定
- 収入スプレッドシートへ自動追記
"""

import re
import sys
import subprocess
from datetime import datetime
from pathlib import Path

# 入金判定キーワード
INCOME_KEYWORDS = [
    'ｶﾞｲｺｸﾋｼﾑｹｿｳｷﾝ',  # 外国非課税送金
    'ﾋﾟ-ﾃｲﾂｸｽｼﾞﾔﾊﾟﾝ', 'ｽﾄﾗｲﾌﾟｼﾞﾔﾊﾟﾝ',  # Stripe
    'ﾉ-ﾄ',  # Note
    'ﾎﾟ-ﾄ',  # Port
    'ﾒﾙﾍﾟｲ',  # メルカリ
    'ｷﾕｳｼﾕｳﾀﾞｲｶﾞｸ',  # 九州大学
    'ﾏｼﾕﾏﾛｴﾝﾀﾒ',  # マシュマロエンタメ
    'ｷﾔﾘｱﾃﾞｻﾞｲﾝｾﾝﾀ-',  # キャリアデザインセンター
    'ﾐﾝｼﾕｳ',  # みん就
    'ﾘﾘ',  # Lily
    'ﾌｸｵｶｼﾎｹﾝﾈﾝｷﾝｶ',  # 福岡市保険年金課
    'ｵﾘｿｸ',  # 利息
]

# 支出キーワード
EXPENSE_KEYWORDS = [
    'ﾌﾘｺﾐｼｷﾝ', 'ﾌﾘｺﾐﾃｽｳﾘﾖｳ',  # 振込
    'RS ﾍﾟｲﾍﾟｲ', 'ATMｼﾊﾗｲ', 'ATMﾃｽｳﾘﾖｳ',
    'ﾐﾂｲｽﾐﾄﾓｶ-ﾄﾞ', 'ﾗｸﾃﾝｶ-ﾄﾞｻ-ﾋﾞｽ', 'ﾗｲﾌｶ-ﾄﾞ',
]

def extract_text_from_pdf(pdf_path):
    """
    PDFからテキスト抽出
    方法1: pdftotext（poppler-utils）
    方法2: Gemini Vision API
    """
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")
    
    # TODO: pdftotext実装
    # subprocess.run(['pdftotext', str(pdf_path), '-'], capture_output=True)
    
    # Placeholder: 手動で抽出したテキスト返す
    return ""

def parse_bank_statement_text(text):
    """銀行明細テキストから取引を抽出"""
    transactions = []
    
    # パターン: 日付 摘要 金額
    # 例: "2026-01-05 598,000 ﾌﾘｺﾐｼｷﾝ"
    lines = text.strip().split('\n')
    
    for line in lines:
        # 日付パターン
        date_match = re.search(r'(\d{4}-\d{2}-\d{2})', line)
        if not date_match:
            continue
        
        date = date_match.group(1)
        
        # 金額パターン（カンマ区切り）
        amounts = re.findall(r'([\d,]+)', line)
        if len(amounts) < 2:
            continue
        
        # 摘要（金額以外の部分）
        description = line
        for amt in amounts:
            description = description.replace(amt, '')
        description = description.replace(date, '').strip()
        
        # 金額（最後から2番目が実際の金額、最後が残高）
        if len(amounts) >= 2:
            amount_str = amounts[-2].replace(',', '')
            if amount_str.isdigit():
                amount = int(amount_str)
                
                transactions.append({
                    'date': date,
                    'description': description,
                    'amount': amount
                })
    
    return transactions

def is_income(description):
    """入金かどうか判定"""
    # 支出キーワードチェック
    for keyword in EXPENSE_KEYWORDS:
        if keyword in description:
            return False
    
    # 入金キーワードチェック
    for keyword in INCOME_KEYWORDS:
        if keyword in description:
            return True
    
    return False

def extract_incomes_from_pdf(pdf_path):
    """PDFから入金のみを抽出"""
    text = extract_text_from_pdf(pdf_path)
    transactions = parse_bank_statement_text(text)
    
    incomes = []
    for txn in transactions:
        if is_income(txn['description']):
            incomes.append({
                'date': txn['date'],
                'source': txn['description'].strip(),
                'amount': txn['amount'],
                'memo': '銀行明細（自動抽出）',
                'url': ''
            })
    
    return incomes

def process_bank_statement_pdf(pdf_path):
    """銀行明細PDF処理メイン"""
    print(f"Processing: {pdf_path}")
    
    incomes = extract_incomes_from_pdf(pdf_path)
    
    print(f"\n=== 入金一覧 ({len(incomes)}件) ===")
    total = 0
    for inc in incomes:
        print(f"{inc['date']} | {inc['amount']:>10,}円 | {inc['source']}")
        total += inc['amount']
    
    print(f"\n総入金額: {total:,}円")
    
    # TODO: Sheets APIで追記
    print("\nTODO: スプレッドシート追記（OAuth認証完了後）")
    
    return incomes

if __name__ == "__main__":
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
        process_bank_statement_pdf(pdf_path)
    else:
        print("Usage: bank_statement_processor.py <pdf_path>")
        print("\nTODO: PDF抽出実装")
