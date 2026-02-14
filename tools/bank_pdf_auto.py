#!/usr/bin/env python3
"""
銀行明細PDF自動処理（完全版）
Telegram PDF → Claude読み取り → 入金抽出 → 収入シート追加
"""
import sys
import json
import requests
from pathlib import Path

TOKEN_FILE = Path("/tmp/google_oauth_tokens.json")
SHEET_ID = "1FH_CZkEkn621MNvFioUHgT3_4UU_TL1POu-Bhpz7KCc"
INCOME_SHEET_NAME = "2026年収入"

# 入金判定キーワード
INCOME_KEYWORDS = [
    'ｶﾞｲｺｸﾋｼﾑｹｿｳｷﾝ', 'ﾋﾟ-ﾃｨﾂｸｽｼﾞﾔﾊﾟﾝ', 'ｽﾄﾗｲﾌﾟｼﾞﾔﾊﾟﾝ',
    'ﾉ-ﾄ', 'ﾎﾟ-ﾄ', 'ﾒﾙﾍﾟｲ', 'ｷﾕｳｼﾕｳﾀﾞｲｶﾞｸ',
    'ﾏｼﾕﾏﾛｴﾝﾀﾒ', 'ｷﾔﾘｱﾃﾞｻﾞｲﾝｾﾝﾀ-', 'ﾐﾝｼﾕｳ',
    'ﾘﾘ', 'ﾌｸｵｶｼﾎｹﾝﾈﾝｷﾝｶ', 'ｵﾘｿｸ',
    '外国非課税送金', 'Stripe', 'Note', 'Port',
    'メルカリ', 'メルペイ', '九州大学', '利息'
]

EXPENSE_KEYWORDS = [
    'ﾌﾘｺﾐｼｷﾝ', 'ﾌﾘｺﾐﾃｽｳﾘﾖｳ', 'RS ﾍﾟｲﾍﾟｲ',
    'ATMｼﾊﾗｲ', 'ATMﾃｽｳﾘﾖｳ', 'ﾐﾂｲｽﾐﾄﾓｶ-ﾄﾞ',
    'ﾗｸﾃﾝｶ-ﾄﾞｻ-ﾋﾞｽ', 'ﾗｲﾌｶ-ﾄﾞ',
    '振込', 'ATM', 'クレカ', 'カード'
]

def load_token():
    """OAuth token読み込み"""
    data = json.loads(TOKEN_FILE.read_text())
    
    url = "https://oauth2.googleapis.com/token"
    response = requests.post(url, data={
        'client_id': data['client_id'],
        'client_secret': data['client_secret'],
        'refresh_token': data['refresh_token'],
        'grant_type': 'refresh_token'
    })
    
    return response.json()['access_token']

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

def find_first_empty_row(access_token):
    """収入シートの一番上の空白行を見つける"""
    print(f"\n=== 空白行検索 ===")
    
    url = f"https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}/values/{INCOME_SHEET_NAME}!A:A"
    headers = {'Authorization': f'Bearer {access_token}'}
    
    response = requests.get(url, headers=headers)
    values = response.json().get('values', [])
    
    # A1はヘッダーなのでスキップ
    for i in range(1, len(values) + 1):
        if i >= len(values) or not values[i] or values[i][0] == '':
            row_num = i + 1
            print(f"✓ 空白行発見: A{row_num}")
            return row_num
    
    row_num = len(values) + 1
    print(f"✓ 最後尾に追加: A{row_num}")
    return row_num

def append_incomes_to_sheet(access_token, incomes):
    """収入を一番上の空白行から順番に追加"""
    print(f"\n=== 収入シートに追加 ===")
    
    if not incomes:
        print("追加する入金がありません")
        return
    
    # 一番上の空白行を見つける
    start_row = find_first_empty_row(access_token)
    
    # データ準備
    values = []
    for income in incomes:
        values.append([
            income.get('date', ''),
            income.get('source', ''),
            '',  # 住所
            '銀行明細',  # メモ
            str(income.get('amount', '')),
            '円',
            ''  # URL
        ])
    
    # 書き込み
    end_row = start_row + len(values) - 1
    range_name = f"{INCOME_SHEET_NAME}!A{start_row}:G{end_row}"
    url = f"https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}/values/{range_name}"
    headers = {'Authorization': f'Bearer {access_token}', 'Content-Type': 'application/json'}
    
    response = requests.put(url, params={'valueInputOption': 'RAW'}, headers=headers, json={'values': values})
    if response.status_code != 200:
        raise Exception(f"Write failed: {response.text}")
    
    print(f"✓ {len(values)}件追加完了（A{start_row}〜A{end_row}）")

def main(pdf_path, incomes_json):
    """
    メイン処理
    incomes_json: Claudeが分析した入金データ（JSON配列）
    [{"date":"2026/01/06","source":"外国非課税送金","amount":"28522"}, ...]
    """
    print("=== 銀行明細PDF自動処理 ===")
    print(f"PDF: {pdf_path}")
    
    # JSON解析
    incomes = json.loads(incomes_json)
    
    # 入金判定（念のため再フィルタ）
    filtered_incomes = []
    for income in incomes:
        source = income.get('source', '')
        if is_income(source):
            filtered_incomes.append(income)
        else:
            print(f"除外（支出）: {source}")
    
    print(f"\n入金件数: {len(filtered_incomes)}件")
    
    if not filtered_incomes:
        print("入金が見つかりませんでした")
        return
    
    # サマリー表示
    total = 0
    for income in filtered_incomes:
        amount = int(income.get('amount', 0))
        total += amount
        print(f"{income.get('date')} | {amount:>10,}円 | {income.get('source')}")
    
    print(f"\n総入金額: {total:,}円")
    
    # 1. Access token取得
    access_token = load_token()
    
    # 2. 収入シートに追加
    append_incomes_to_sheet(access_token, filtered_incomes)
    
    print("\n✅ 完了！")
    print(f"スプレッドシート: https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit#gid=126020037")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: bank_pdf_auto.py <pdf_path> <incomes_json>")
        print("\n例:")
        print('  python3 bank_pdf_auto.py bank.pdf \'[{"date":"2026/01/06","source":"外国非課税送金","amount":"28522"}]\'')
        sys.exit(1)
    
    try:
        main(sys.argv[1], sys.argv[2])
    except Exception as e:
        print(f"❌ エラー: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
