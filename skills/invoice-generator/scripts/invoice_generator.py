#!/usr/bin/env python3
"""
Invoice Generator Script
Google Docsテンプレートから請求書を自動作成しPDFでDriveにアップロード
複数行明細対応
"""

import os
import sys
from datetime import datetime

sys.path.insert(0, '/Users/ai-driven-work/Documents/OpenClaw-Workspace')

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import json

# ============ 設定 ============
SPREADSHEET_ID = '1R6dEPRTHfjnCXu1VWMh0lwfea0OqMTYjhzIVL_NA990'
TEMPLATE_DOC_ID = None
DRIVE_FOLDER_ID = '1oLO6kGT31AV780TzymtC6puZ9vM8xqMH'
CREDENTIALS_PATH = '/Users/ai-driven-work/.credentials/gmail-token.json'
DEFAULT_TAX_RATE = 0.10

def get_credentials():
    creds = Credentials.from_authorized_user_info(json.load(open(CREDENTIALS_PATH)))
    return creds

def get_next_invoice_number(sheets_service):
    """Google Sheetsから最終請求書番号を取得"""
    result = sheets_service.values().get(
        spreadsheetId=SPREADSHEET_ID,
        range='A:A'
    ).execute()
    
    values = result.get('values', [])
    if len(values) <= 1:
        return 'INV-2026-0001'
    
    last_invoice = values[-1][0] if values[-1] else 'INV-2026-0000'
    try:
        year, num = last_invoice.split('-')
        new_num = int(num) + 1
        return f"INV-{year}-{new_num:04d}"
    except:
        return f"INV-{datetime.now().year}-0001"

def format_yen(amount):
    """日本円フォーマット"""
    return f"¥{amount:,}"

def create_invoice(
    company_name,
    due_date,
    items=None,
    title=None,
    invoice_date=None,
    details=None,
    tax_rate=None,
    invoice_no=None
):
    """
    請求書作成
    
    items: [{'name': '品名', 'quantity': 数量, 'unit_price': 単価}, ...]
    """
    creds = get_credentials()
    docs_service = build('docs', 'v1', credentials=creds)
    drive_service = build('drive', 'v3', credentials=creds)
    sheets_service = build('sheets', 'v4', credentials=creds)
    
    # デフォルト値
    if invoice_date is None:
        invoice_date = datetime.now().strftime('%Y年%m月%d日')
    if items is None:
        items = [{'name': '-', 'quantity': 1, 'unit_price': 0}]
    if title is None:
        title = company_name
    if details is None:
        details = ''
    if tax_rate is None:
        tax_rate = DEFAULT_TAX_RATE
    if invoice_no is None:
        invoice_no = get_next_invoice_number(sheets_service)
    
    # 計算
    subtotal = sum(item['quantity'] * item['unit_price'] for item in items)
    tax_amount = int(subtotal * tax_rate)
    total_amount = subtotal + tax_amount
    
    print(f"請求書番号: {invoice_no}")
    print(f"請求先: {company_name}")
    print(f"件数: {len(items)}件")
    
    # テンプレートからコピー
    if TEMPLATE_DOC_ID:
        doc = docs_service.documents().copy(
            documentId=TEMPLATE_DOC_ID,
            body={'name': invoice_no}
        ).execute()
        doc_id = doc['documentId']
    else:
        doc = docs_service.documents().create(
            body={'title': invoice_no, 'body': {'content': []}}
        ).execute()
        doc_id = doc['documentId']
    
    # 基本情報
    replacements = {
        '{{invoice_no}}': invoice_no,
        '{{company_name}}': company_name,
        '{{title}}': title,
        '{{date}}': invoice_date,
        '{{details}}': details,
    }
    
    # 複数行明細（最大10行）
    for i, item in enumerate(items[:10], 1):
        replacements[f'{{item_{i}_name}}'] = item['name']
        replacements[f'{{item_{i}_quantity}}'] = str(item['quantity'])
        replacements[f'{{item_{i}_unit_price}}'] = format_yen(item['unit_price'])
        replacements[f'{{item_{i}_amount}}'] = format_yen(item['quantity'] * item['unit_price'])
    
    # 不足分行は空欄
    for i in range(len(items) + 1, 11):
        replacements[f'{{item_{i}_name}}'] = ''
        replacements[f'{{item_{i}_quantity}}'] = ''
        replacements[f'{{item_{i}_unit_price}}'] = ''
        replacements[f'{{item_{i}_amount}}'] = ''
    
    # 計算結果
    replacements['{{subtotal}}'] = format_yen(subtotal)
    replacements['{{tax}}'] = format_yen(tax_amount)
    replacements['{{total}}'] = format_yen(total_amount)
    replacements['{{due_date}}'] = due_date
    
    # 置換実行
    requests = []
    for pattern, text in replacements.items():
        requests.append({
            'replaceAllText': {
                'containsText': {'pattern': pattern},
                'replaceText': text
            }
        })
    
    if requests:
        docs_service.documents().batchUpdate(
            documentId=doc_id,
            body={'requests': requests}
        ).execute()
    
    # Driveに移動＆共有
    drive_service.files().update(fileId=doc_id, addParents=DRIVE_FOLDER_ID).execute()
    drive_service.permissions().create(fileId=doc_id, body={'type': 'anyone', 'role': 'reader'}).execute()
    
    # リンク取得
    file_info = drive_service.files().get(fileId=doc_id, fields='webViewLink').execute()
    
    # スプレッドシートに記録
    sheets_service.spreadsheets().values().append(
        spreadsheetId=SPREADSHEET_ID,
        range='A:F',
        valueInputOption='USER_ENTERED',
        body={'values': [[invoice_no, company_name, format_yen(total_amount), invoice_date, '作成済み', file_info['webViewLink']]]}
    ).execute()
    
    return {
        'invoice_no': invoice_no,
        'company_name': company_name,
        'subtotal': format_yen(subtotal),
        'tax': format_yen(tax_amount),
        'total': format_yen(total_amount),
        'date': invoice_date,
        'due_date': due_date,
        'items': items,
        'link': file_info['webViewLink']
    }

# ============ メイン ============
if __name__ == '__main__':
    if len(sys.argv) < 4:
        print("Usage:")
        print("  単一行: python invoice_generator.py <企業名> <品名> <数量> <単価> <支払期限>")
        print("  複数行: python invoice_generator.py <企業名> <支払期限> '<JSONitems>'")
        print("")
        print("Examples:")
        print('  python invoice_generator.py "Tailent株式会社" "AIライティング制作" 1 80000 "2026年2月28日"')
        print('  python invoice_generator.py "Genspark" "2026年3月15日" \'[{"name":"記事制作費","quantity":1,"unit_price":80000},{"name":"オプション","quantity":1,"unit_price":20000}]\'')
        sys.exit(1)
    
    company = sys.argv[1]
    due_date = sys.argv[2]
    
    # JSONItems或有
    if len(sys.argv) > 3:
        import json
        items = json.loads(sys.argv[3])
    else:
        # 単一行
        product_name = sys.argv[3] if len(sys.argv) > 3 else '-'
        quantity = int(sys.argv[4]) if len(sys.argv) > 4 else 1
        unit_price = int(sys.argv[5]) if len(sys.argv) > 5 else 0
        items = [{'name': product_name, 'quantity': quantity, 'unit_price': unit_price}]
    
    result = create_invoice(
        company_name=company,
        due_date=due_date,
        items=items
    )
    
    print("=" * 40)
    print("✅ 請求書作成完了!")
    print("=" * 40)
    print(f"請求書番号: {result['invoice_no']}")
    print(f"請求先: {result['company_name']}")
    print(f"請求日: {result['date']}")
    print(f"支払期限: {result['due_date']}")
    print("-" * 40)
    print("【明細】")
    for item in result['items']:
        print(f"  {item['name']}: {item['quantity']} x ¥{item['unit_price']:,} = ¥{item['quantity']*item['unit_price']:,}")
    print("-" * 40)
    print(f"小計: {result['subtotal']}")
    print(f"税額: {result['tax']}")
    print(f"合計: {result['total']}")
    print("=" * 40)
    print(f"リンク: {result['link']}")
