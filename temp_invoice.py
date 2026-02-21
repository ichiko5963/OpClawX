#!/usr/bin/env python3
"""Quick invoice creator for ポート株式会社 Xプレミアム"""

import sys
sys.path.insert(0, '/Users/ai-driven-work/Documents/OpenClaw-Workspace')

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import json

SPREADSHEET_ID = '1R6dEPRTHfjnCXu1VWMh0lwfea0OqMTYjhzIVL_NA990'
DRIVE_FOLDER_ID = '1oLO6kGT31AV780TzymtC6puZ9vM8xqMH'
CREDS_PATH = '/Users/ai-driven-work/.credentials/gmail-token.json'

creds = Credentials.from_authorized_user_info(json.load(open(CREDS_PATH)))
docs = build('docs', 'v1', credentials=creds)
drive = build('drive', 'v3', credentials=creds)
sheets = build('sheets', 'v4', credentials=creds)

# Get next invoice number
result = sheets.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID, range='A:A').execute()
values = result.get('values', [])
if len(values) > 1:
    last = values[-1][0]
    year, num = last.split('-')
    invoice_no = f'{year}-{int(num)+1:04d}'
else:
    invoice_no = '2026-0027'

print(f'請求書番号: {invoice_no}')

# Create new document
doc = docs.documents().create(body={'title': invoice_no}).execute()
doc_id = doc['documentId']

# Content
content = f"""請求書

請求番号: {invoice_no}
請求日: 2026年2月21日

宛先: ポート株式会社
件名: Xプレミアム2月分

--------------------------------------------------------------------------------
品名                    数量    単価        金額
--------------------------------------------------------------------------------
Xプレミアム(999円)       1       ¥999        ¥999
Xプレミアム(499円)       1       ¥499        ¥499

                                          小計:    ¥1,498
                                          消費税:  ¥150
                                          合計:    ¥1,648
                                          
================================================================================
支払期限: 2026年3月21日
================================================================================
"""

# Insert content
docs.documents().batchUpdate(
    documentId=doc_id,
    body={'requests': [{
        'insertText': {
            'location': {'index': 1},
            'text': content
        }
    }]}
).execute()

# Move to Drive folder
drive.files().update(fileId=doc_id, addParents=DRIVE_FOLDER_ID).execute()

# Share with anyone
drive.permissions().create(fileId=doc_id, body={'type': 'anyone', 'role': 'reader'}).execute()

# Get link
link = drive.files().get(fileId=doc_id, fields='webViewLink').execute()['webViewLink']

# Record in spreadsheet
sheets.spreadsheets().values().append(
    spreadsheetId=SPREADSHEET_ID,
    range='A:F',
    valueInputOption='USER_ENTERED',
    body={'values': [[invoice_no, 'ポート株式会社', '¥1,648', '2026年2月21日', '作成済み', link]]}
).execute()

print('✅ 作成完了!')
print(f'リンク: {link}')
