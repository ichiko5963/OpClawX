#!/usr/bin/env python3
"""
請求書Generator - 完全版
Usage: 
  python3 create_invoice.py --company "ポート株式会社" --title "Xプレミアム2月分" --items "Xプレミアム(999円):1:999,Xプレミアム(499円):1:499"
  python3 create_invoice.py --company "Genspark" --title "SNSコンサルティング" --amount 225000
"""

import os
import sys
import argparse
import subprocess
import re
from datetime import datetime, timedelta

# デフォルト値（市岡さん用）
DEFAULT_ISSUER = {
    'name': '市岡直人',
    'kana': 'イチオカナオト',
    'tel': '080-3896-7229',
    'email': 'jiuhuot10@gmail.com',
    'bank': '西日本シティ銀行 周船寺支行',
    'account': 'イチオカナオト（普通）3124131'
}

HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>請求書 - {invoice_no}</title>
    <style>
        @page {{ size: A4; margin: 0; }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: "Yu Gothic", "Meiryo", "Hiragino Sans", sans-serif; font-size: 10pt; line-height: 1.6; color: #333; width: 100%; max-width: 800px; margin: 0 auto; padding: 40px; }}
        .header {{ display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 25px; border-bottom: 3px solid #333; padding-bottom: 15px; }}
        .header-left h1 {{ font-size: 28pt; letter-spacing: 12px; font-weight: bold; }}
        .invoice-info {{ display: flex; justify-content: space-between; margin-bottom: 25px; }}
        .info-box {{ width: 48%; }}
        .info-row {{ display: flex; border-bottom: 1px solid #ddd; padding: 5px 0; }}
        .info-label {{ width: 80px; color: #666; }}
        .info-value {{ font-weight: bold; }}
        .to {{ margin-bottom: 20px; padding: 15px; border: 1px solid #333; }}
        .to-label {{ font-size: 9pt; color: #666; }}
        .to-name {{ font-size: 14pt; font-weight: bold; }}
        .subject {{ margin-bottom: 20px; padding: 12px 15px; background: #f8f8f8; border-left: 4px solid #333; }}
        .amount-box {{ text-align: right; margin-bottom: 25px; padding: 15px; background: #fff; border: 2px solid #333; }}
        .amount-label {{ font-size: 12pt; margin-bottom: 5px; }}
        .amount-value {{ font-size: 24pt; font-weight: bold; }}
        table {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; }}
        th, td {{ border: 1px solid #333; padding: 12px 10px; text-align: left; }}
        th {{ background: #333; color: #fff; font-size: 9pt; font-weight: normal; }}
        .text-right {{ text-align: right; }}
        .text-center {{ text-align: center; }}
        .summary {{ display: flex; justify-content: flex-end; margin-bottom: 30px; }}
        .summary-table {{ width: 200px; }}
        .summary-table td {{ border: none; padding: 5px 10px; }}
        .summary-label {{ text-align: right; color: #666; }}
        .summary-value {{ text-align: right; font-weight: bold; }}
        .total-row {{ border-top: 2px solid #333 !important; font-size: 14pt; }}
        .issuer {{ margin-bottom: 25px; padding: 15px; border: 1px solid #333; }}
        .issuer-title {{ font-size: 9pt; color: #666; margin-bottom: 8px; }}
        .issuer-name {{ font-size: 14pt; font-weight: bold; margin-bottom: 5px; }}
        .bank {{ margin-bottom: 25px; padding: 15px; background: #fafafa; border: 1px solid #ccc; }}
        .bank-title {{ font-size: 9pt; color: #666; margin-bottom: 8px; }}
        .bank-name {{ font-size: 12pt; font-weight: bold; }}
        .footer {{ text-align: center; color: #888; font-size: 8pt; padding-top: 15px; border-top: 1px solid #ddd; }}
        .back-link {{ display: inline-block; margin-bottom: 20px; }}
    </style>
</head>
<body>
    <a href="/" class="back-link">← 一覧に戻る</a>
    <div class="header">
        <div class="header-left"><h1>請 求 書</h1></div>
    </div>
    <div class="invoice-info">
        <div class="info-box">
            <div class="info-row"><span class="info-label">日付：</span><span class="info-value">{date}</span></div>
        </div>
        <div class="info-box" style="text-align: right;">
            <div class="info-row" style="justify-content: flex-end;"><span class="info-label">請求番号：</span><span class="info-value">{invoice_no}</span></div>
        </div>
    </div>
    <div class="to">
        <div class="to-label">請求先</div>
        <div class="to-name">{company_name}</div>
    </div>
    <div class="subject">
        件名：{title}<br>
        、下記のとおりご請求申し上げます。
    </div>
    <div class="amount-box">
        <div class="amount-label">ご請求金額</div>
        <div class="amount-value">¥ {total_formatted}-</div>
    </div>
    <table>
        <thead>
            <tr><th style="width: 50%;">品番・品名</th><th style="width: 15%; text-align: center;">数量</th><th style="width: 17%; text-align: right;">単価</th><th style="width: 18%; text-align: right;">金額</th></tr>
        </thead>
        <tbody>
            {items_html}
        </tbody>
    </table>
    <div class="summary">
        <table class="summary-table">
            <tr><td class="summary-label">小計：</td><td class="summary-value">{subtotal_formatted}</td></tr>
            {tax_row}
            <tr class="total-row"><td class="summary-label">合計：</td><td class="summary-value">{total_formatted}</td></tr>
        </table>
    </div>
    <div class="issuer">
        <div class="issuer-title">請求者情報</div>
        <div class="issuer-name">{issuer_name}</div>
        <div>TEL：{issuer_tel}</div>
        <div>{issuer_email}</div>
    </div>
    <div class="bank">
        <div class="bank-title">お振込先</div>
        <div class="bank-name">{bank_name}</div>
        <div>{bank_account}</div>
    </div>
    <div class="footer">
        ※お振込手数料はお客様負担にてお願い申し上げます。<br>
        ※ご不明な点がございましたら、お気軽にお問い合わせください。
    </div>
</body>
</html>
'''

INDEX_TEMPLATE = '''<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>請求書一覧</title>
    <style>
        @page {{ size: A4; margin: 0; }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: "Yu Gothic", "Meiryo", "Hiragino Sans", sans-serif; font-size: 12pt; line-height: 1.8; color: #333; width: 100%; max-width: 900px; margin: 0 auto; padding: 40px; }}
        h1 {{ font-size: 24pt; text-align: center; margin-bottom: 30px; letter-spacing: 8px; }}
        .invoice-list {{ list-style: none; }}
        .invoice-item {{ border: 2px solid #333; margin-bottom: 15px; }}
        .invoice-item a {{ display: block; padding: 20px; text-decoration: none; color: #333; transition: background 0.2s; }}
        .invoice-item a:hover {{ background: #f5f5f5; }}
        .invoice-header {{ display: flex; justify-content: space-between; align-items: center; }}
        .invoice-no {{ font-size: 16pt; font-weight: bold; }}
        .invoice-date {{ color: #666; }}
        .invoice-company {{ font-size: 14pt; margin-top: 5px; }}
        .invoice-amount {{ font-size: 18pt; font-weight: bold; color: #c00; }}
        .invoice-title {{ color: #666; font-size: 10pt; margin-top: 5px; }}
    </style>
</head>
<body>
    <h1>請求書一覧</h1>
    <ul class="invoice-list">
        {invoice_items}
    </ul>
</body>
</html>
'''

INDEX_ITEM = '''        <li class="invoice-item">
            <a href="/{no}.html">
                <div class="invoice-header">
                    <span class="invoice-no">No.{no}</span>
                    <span class="invoice-date">{date}</span>
                </div>
                <div class="invoice-company">{company}</div>
                <div class="invoice-title">{title}</div>
                <div class="invoice-amount">¥{amount}-</div>
            </a>
        </li>'''

def get_next_invoice_no():
    """次の請求書番号を取得（01, 02, 03...）"""
    invoices_dir = '/Users/ai-driven-work/Documents/OpenClaw-Workspace/invoices'
    
    # 既存の請求書を確認
    existing = []
    for f in os.listdir(invoices_dir):
        if re.match(r'\d+\.html$', f):
            no = f.replace('.html', '')
            existing.append(int(no))
    
    if existing:
        next_no = max(existing) + 1
    else:
        next_no = 1
    
    return f"{next_no:02d}"

def format_yen(amount):
    """日本円フォーマット"""
    return f"{amount:,}"

def parse_items(items_str):
    """アイテム文字列をパース
    形式: "name:quantity:unit_price:amount,name:quantity:unit_price:amount"
    または "name:amount" (quantity=1, unit_price=amount)
    """
    items = []
    for item_str in items_str.split(','):
        parts = item_str.strip().split(':')
        if len(parts) == 4:
            items.append({
                'name': parts[0],
                'quantity': parts[1],
                'unit_price': parts[2],
                'amount': int(parts[3])
            })
        elif len(parts) == 2:
            items.append({
                'name': parts[0],
                'quantity': '1',
                'unit_price': parts[1],
                'amount': int(parts[1])
            })
    return items

def create_invoice(
    company_name,
    title,
    items,
    date=None,
    invoice_no=None,
    issuer=None
):
    """請求書HTML生成"""
    
    # デフォルト値設定
    if date is None:
        date = datetime.now().strftime('%Y年%m月%d日')
    if invoice_no is None:
        invoice_no = get_next_invoice_no()
    if issuer is None:
        issuer = DEFAULT_ISSUER
    
    # Items HTML生成
    items_html = ''
    for item in items:
        items_html += f'''<tr>
            <td>{item['name']}</td>
            <td class="text-center">{item['quantity']}</td>
            <td class="text-right">{format_yen(int(item['unit_price']))}</td>
            <td class="text-right">{format_yen(item['amount'])}</td>
        </tr>'''
    
    # 計算
    subtotal = sum(item['amount'] for item in items)
    tax = int(subtotal * 0.1)  # 10%
    total = subtotal + tax
    
    # 税金の行（常に表示）
    tax_row = f'<tr><td class="summary-label">消費税(10%)：</td><td class="summary-value">{format_yen(tax)}</td></tr>'
    
    # HTML生成
    html = HTML_TEMPLATE.format(
        invoice_no=invoice_no,
        date=date,
        company_name=company_name,
        title=title,
        total_formatted=format_yen(total),
        subtotal_formatted=format_yen(subtotal),
        tax_row=tax_row,
        items_html=items_html,
        issuer_name=issuer['name'],
        issuer_tel=issuer['tel'],
        issuer_email=issuer['email'],
        bank_name=issuer['bank'],
        bank_account=issuer['account']
    )
    
    # 保存
    output_path = f'/Users/ai-driven-work/Documents/OpenClaw-Workspace/invoices/{invoice_no}.html'
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✅ 請求書HTML生成完了: {output_path}")
    return invoice_no, total

def update_index(new_no, new_company, new_title, new_amount, new_date):
    """一覧ページ更新"""
    invoices_dir = '/Users/ai-driven-work/Documents/OpenClaw-Workspace/invoices'
    
    # 既存の請求書リスト取得
    invoices = []
    for f in sorted(os.listdir(invoices_dir)):
        if re.match(r'\d+\.html$', f) and f != 'index.html':
            no = f.replace('.html', '')
            # 対応するHTMLから情報を取得（簡易的に新しいものを先頭に）
            invoices.append({
                'no': no,
                'company': '',
                'title': '',
                'amount': '',
                'date': ''
            })
    
    # 新しい請求書を先頭に追加
    invoices.insert(0, {
        'no': new_no,
        'company': new_company,
        'title': new_title,
        'amount': format_yen(new_amount),
        'date': new_date or datetime.now().strftime('%Y年%m月%d日')
    })
    
    # HTML生成
    items_html = ''
    for inv in invoices[:20]:  # 最大20件
        items_html += INDEX_ITEM.format(
            no=inv['no'],
            date=inv['date'],
            company=inv['company'],
            title=inv['title'],
            amount=inv['amount']
        )
    
    html = INDEX_TEMPLATE.format(invoice_items=items_html)
    
    output_path = f'{invoices_dir}/index.html'
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✅ 一覧ページ更新完了: {output_path}")

def deploy_to_vercel():
    """Vercelにデプロイ"""
    result = subprocess.run(
        ['npx', 'vercel', '--prod', '--yes'],
        cwd='/Users/ai-driven-work/Documents/OpenClaw-Workspace/invoices',
        capture_output=True,
        text=True
    )
    
    # URL抽出 - 恒久URL優先
    if 'invoices-henna.vercel.app' in result.stdout:
        return 'https://invoices-henna.vercel.app'
    
    for line in result.stdout.split('\n'):
        if 'vercel.app' in line and 'Aliased:' in line:
            url = line.split('Aliased:')[-1].strip()
            return url
    
    for line in result.stdout.split('\n'):
        if 'https://' in line and 'vercel.app' in line:
            return line.strip()
    
    return None

def main():
    parser = argparse.ArgumentParser(description='請求書Generator')
    
    # 必須
    parser.add_argument('--company', '-c', required=True, help='請求先企業名（必須）')
    parser.add_argument('--title', '-t', required=True, help='件名（必須）')
    
    # 商品（複数OK）
    parser.add_argument('--items', '-i', help='商品リスト（カンマ区切り）例: "品名1:数量:単価:金額,品名2:数量:単価:金額"')
    parser.add_argument('--amount', '-a', type=int, help='金額（単一商品の場合）')
    
    # 日付
    parser.add_argument('--date', '-d', help='請求日（デフォルト: 今日）例: 2026年2月21日')
    parser.add_argument('--no', '-n', help='請求番号（デフォルト: 自動採番）')
    
    args = parser.parse_args()
    
    # Itemsパース
    items = []
    if args.items:
        items = parse_items(args.items)
    elif args.amount:
        items = [{
            'name': args.title,
            'quantity': '1',
            'unit_price': str(args.amount),
            'amount': args.amount
        }]
    else:
        print("❌ --items または --amount は必須です")
        sys.exit(1)
    
    # 請求書番号
    invoice_no = args.no or get_next_invoice_no()
    
    # 請求書作成
    no, total = create_invoice(
        company_name=args.company,
        title=args.title,
        items=items,
        date=args.date,
        invoice_no=invoice_no
    )
    
    # 一覧更新
    update_index(no, args.company, args.title, total, args.date)
    
    # デプロイ
    print("\n🚀 Vercelにデプロイ中...")
    url = deploy_to_vercel()
    
    if url:
        print(f"\n✅ 請求書完成！")
        print(f"🌐 一覧: {url}")
        print(f"🌐 個別: {url}/{no}.html")
        print(f"\n開いて Cmd+P → PDF保存でええで！")
    else:
        print("❌ デプロイ失敗")

if __name__ == '__main__':
    main()
