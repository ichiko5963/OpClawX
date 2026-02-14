#!/usr/bin/env python3
"""
銀行口座明細から収入抽出
- 入金のみを検出
- 収入スプレッドシートに追記
"""

import sys
import json
import subprocess
from datetime import datetime

INCOME_SHEET_ID = "1R6dEPRTHfjnCXu1VWMh0lwfea0OqMTYjhzIVL_NA990"
GOG_ACCOUNT = "jiuhuot10@gmail.com"

# 銀行明細テキスト（PDFから）
BANK_STATEMENT = """
2026-01-05 598,000 ﾌﾘｺﾐｼｷﾝ
2026-01-05 1,650,000 ﾌﾘｺﾐｼｷﾝ
2026-01-06 28,522 ｶﾞｲｺｸﾋｼﾑｹｿｳｷﾝ
2026-01-14 123,600 ﾒﾙﾍﾟｲ(ﾒﾙｶﾘ
2026-01-19 112,547 ﾋﾟ-ﾃｲﾂｸｽｼﾞﾔﾊﾟﾝ(Stripe)
2026-01-19 6,423 ﾋﾟ-ﾃｲﾂｸｽｼﾞﾔﾊﾟﾝ(Stripe)
2026-01-20 26,400 ﾘﾘ(ｶ
2026-01-21 12,600 ｷﾕｳｼﾕｳﾀﾞｲｶﾞｸ(九州大学)
2026-01-21 163,552 ｶﾞｲｺｸﾋｼﾑｹｿｳｷﾝ
2026-01-23 62,853 ﾏｼﾕﾏﾛｴﾝﾀﾒ(マシュマロエンタメ)
2026-01-26 61,342 ｽﾄﾗｲﾌﾟｼﾞﾔﾊﾟﾝ(Stripe)
2026-01-30 2,750,000 ﾎﾟ-ﾄ(Port)
2026-01-30 51,734 ﾉ-ﾄ(Note)
2026-01-30 87,276 ﾉ-ﾄ(Note)
2026-01-30 218,294 ﾉ-ﾄ(Note)
2026-01-30 11,416 ﾉ-ﾄ(Note)
2026-01-30 90,918 ﾉ-ﾄ(Note)
2026-01-30 19,473 ﾉ-ﾄ(Note)
2026-01-30 2,865 ﾉ-ﾄ(Note)
2026-01-30 4,734 ﾉ-ﾄ(Note)
2026-01-30 158,400 ｷﾔﾘｱﾃﾞｻﾞｲﾝｾﾝﾀ-(キャリアデザインセンター)
2026-01-30 138,600 ﾐﾝｼﾕｳ(みん就)
2026-02-03 51,876 ｶﾞｲｺｸﾋｼﾑｹｿｳｷﾝ
2026-02-05 1,600 ﾌｸｵｶｼﾎｹﾝﾈﾝｷﾝｶ(福岡市保険年金課・還付)
2026-02-06 150,000 ｷﾕｳｼﾕｳﾀﾞｲｶﾞｸ(九州大学)
2026-02-09 97,955 ﾋﾟ-ﾃｲﾂｸｽｼﾞﾔﾊﾟﾝ(Stripe)
2026-02-14 6,241 ｵﾘｿｸ(利息)
"""

def parse_incomes():
    """入金データをパース"""
    incomes = []
    for line in BANK_STATEMENT.strip().split('\n'):
        if not line.strip():
            continue
        parts = line.split()
        if len(parts) >= 3:
            date = parts[0]
            amount_str = parts[1].replace(',', '')
            source = ' '.join(parts[2:])
            
            incomes.append({
                'date': date,
                'amount': int(amount_str),
                'source': source
            })
    return incomes

def append_income_to_sheet(date, source, amount, memo=""):
    """
    収入スプレッドシートに追記
    TODO: 列構造確認後に実装
    """
    # Placeholder: 構造が不明なので一旦保留
    print(f"TODO: 収入追記 - {date} | {source} | {amount:,}円 | {memo}")

def main():
    incomes = parse_incomes()
    
    print("=== 銀行口座入金一覧 ===")
    print(f"期間: 2026/01/01 - 2026/02/14")
    print(f"件数: {len(incomes)}件")
    print()
    
    total = 0
    for inc in incomes:
        print(f"{inc['date']} | {inc['amount']:>10,}円 | {inc['source']}")
        total += inc['amount']
        
        # スプレッドシート追記（TODO）
        # append_income_to_sheet(inc['date'], inc['source'], inc['amount'])
    
    print()
    print(f"総入金額: {total:,}円")
    print()
    print("収入スプレッドシートの列構造を確認後、自動追記を実装します")

if __name__ == "__main__":
    main()
