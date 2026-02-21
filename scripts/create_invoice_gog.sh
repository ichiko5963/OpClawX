#!/bin/bash
# Invoice Creator using gog CLI

# スプレッドシートID
SHEET_ID="1R6dEPRTHfjnCXu1VWMh0lwfea0OqMTYjhzIVL_NA990"
FOLDER_ID="1oLO6kGT31AV780TzymtC6puZ9vM8xqMH"

echo "=== 請求書作成 start ==="

# 1. 請求書番号取得
echo "1. Getting next invoice number..."
LAST_NUM=$(gog sheets values get "$SHEET_ID" "A:A" 2>/dev/null | tail -1 | cut -d',' -f1)
if [ -z "$LAST_NUM" ]; then
    INVOICE_NO="2026-0027"
else
    YEAR=$(echo $LAST_NUM | cut -d'-' -f1)
    NUM=$(echo $LAST_NUM | cut -d'-' -f2)
    NEW_NUM=$((10#$NUM + 1))
    INVOICE_NO="${YEAR}-$(printf "%04d" $NEW_NUM)"
fi
echo "Invoice No: $INVOICE_NO"

# 2. Google Docsで請求書作成
echo "2. Creating Google Doc..."
DOC_URL=$(gog docs create --title "$INVOICE_NO" 2>/dev/null | grep -o 'https://docs.google.com/document/d/[^ ]*' | head -1)
DOC_ID=$(echo $DOC_URL | sed 's|https://docs.google.com/document/d/||' | sed 's|/edit.*||')
echo "Doc ID: $DOC_ID"

# 3. 内容を插入（gog docs使わずにcurlで）
echo "3. Inserting content..."

# 請求書の本文
CONTENT="請求書

請求番号: $INVOICE_NO
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
"

# 4. Driveフォルダに移動
echo "4. Moving to Drive folder..."
gog drive mv "$DOC_ID" "$FOLDER_ID" 2>/dev/null

# 5. 共有設定
echo "5. Setting sharing..."
gog drive share "$DOC_ID" --role reader --type anyone 2>/dev/null

# 6. リンク取得
echo "6. Getting link..."
LINK="https://docs.google.com/document/d/$DOC_ID/edit"

echo ""
echo "=== 完了! ==="
echo "請求書番号: $INVOICE_NO"
echo "リンク: $LINK"
