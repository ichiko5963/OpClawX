#!/usr/bin/env python3
"""
Expense Scanner Script
Scans Gmail for invoices/receipts and appends data to Google Sheets.
"""

import argparse
import json
import subprocess
import os
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional

# Configuration
SHEET_ID = os.environ.get("EXPENSE_SHEET_ID")
GOG_ACCOUNT = os.environ.get("GOG_ACCOUNT")

# Keywords for invoice/receipt detection
INVOICE_KEYWORDS = [
    "invoice", "receipt", "請求書", "領収書", "receipt", "payment",
    "注文確認", "order confirmation", "ご注文", "お支払い"
]


def run_gog_command(args: List[str]) -> Optional[Dict]:
    """Run a gog command and return JSON output."""
    cmd = ["gog"] + args
    if GOG_ACCOUNT:
        cmd.extend(["--account", GOG_ACCOUNT])
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60
        )
        if result.returncode != 0:
            print(f"gog error: {result.stderr}")
            return None
        return json.loads(result.stdout) if result.stdout else {}
    except Exception as e:
        print(f"Command failed: {e}")
        return None


def search_invoice_emails(days: int) -> List[Dict]:
    """Search Gmail for invoice/receipt emails from the last N days."""
    queries = [
        f"newer_than:{days}d has:attachment ({' OR '.join(INVOICE_KEYWORDS)})",
        f"newer_than:{days}d (請求 OR 領収 OR invoice OR receipt)"
    ]
    
    all_emails = []
    for query in queries:
        print(f"Searching: {query}")
        result = run_gog_command([
            "gmail", "messages", "search",
            query,
            "--max", "50",
            "--json"
        ])
        if result and isinstance(result.get("items"), list):
            all_emails.extend(result["items"])
    
    # Deduplicate by message ID
    seen_ids = set()
    unique_emails = []
    for email in all_emails:
        msg_id = email.get("id")
        if msg_id and msg_id not in seen_ids:
            seen_ids.add(msg_id)
            unique_emails.append(email)
    
    return unique_emails


def extract_invoice_data(email: Dict) -> Optional[Dict]:
    """Extract invoice data from an email."""
    subject = email.get("subject", "")
    from_addr = email.get("from", "")
    date_str = email.get("internalDate", "")
    
    if date_str:
        try:
            date = datetime.fromtimestamp(int(date_str) / 1000)
            date_formatted = date.strftime("%Y-%m-%d")
        except:
            date_formatted = date_str
    else:
        date_formatted = ""
    
    # Try to extract amount
    amount = extract_amount(subject + email.get("snippet", ""))
    
    return {
        "date": date_formatted,
        "vendor": from_addr,
        "description": subject,
        "amount": amount,
        "email_id": email.get("id", "")
    }


def extract_amount(text: str) -> str:
    """Extract monetary amount from text."""
    # Look for currency patterns
    patterns = [
        r'[¥￥](\d[\d,]+)',
        r'JPY\s*(\d[\d,]+)',
        r'\$(\d[\d,]+\.?\d*)',
        r'(\d[\d,]+)\s*円',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1).replace(",", "")
    
    return ""


def append_to_sheet(data: List[Dict]) -> bool:
    """Append invoice data to Google Sheets."""
    if not SHEET_ID:
        print("Error: EXPENSE_SHEET_ID environment variable not set")
        return False
    
    # Get current row count
    meta = run_gog_command([
        "sheets", "metadata", SHEET_ID,
        "--json"
    ])
    
    if not meta:
        print("Failed to get sheet metadata")
        return False
    
    # Prepare values
    rows = []
    for item in data:
        rows.append([
            item.get("date", ""),
            item.get("vendor", ""),
            item.get("description", ""),
            item.get("amount", ""),
            item.get("email_id", "")
        ])
    
    if not rows:
        print("No data to append")
        return True
    
    # Append to sheet
    values_json = json.dumps(rows, ensure_ascii=False)
    result = run_gog_command([
        "sheets", "append", SHEET_ID,
        "経費!A:E",  # Assumes sheet tab is named '経費'
        "--values-json", values_json,
        "--insert", "INSERT_ROWS"
    ])
    
    return result is not None


def main():
    parser = argparse.ArgumentParser(description="Scan for expense emails and append to sheet")
    parser.add_argument("--days", type=int, default=1, help="Number of days to scan")
    args = parser.parse_args()
    
    print(f"Expense Scanner - Scanning last {args.days} days...")
    print(f"Current time: {datetime.now().isoformat()}")
    
    # Search emails
    emails = search_invoice_emails(args.days)
    print(f"Found {len(emails)} potential invoice/receipt emails")
    
    if not emails:
        print("No emails to process")
        return
    
    # Extract data
    invoice_data = []
    for email in emails:
        data = extract_invoice_data(email)
        if data:
            invoice_data.append(data)
    
    print(f"Extracted data from {len(invoice_data)} emails")
    for item in invoice_data:
        print(f"  - {item['date']}: {item['description'][:50]}... ({item['amount']})")
    
    # Append to sheet
    if invoice_data:
        success = append_to_sheet(invoice_data)
        if success:
            print(f"Successfully appended {len(invoice_data)} entries to sheet")
        else:
            print("Failed to append to sheet")
    
    # Report summary
    summary = {
        "scanned_days": args.days,
        "emails_found": len(emails),
        "invoices_processed": len(invoice_data),
        "timestamp": datetime.now().isoformat()
    }
    print(json.dumps(summary))


if __name__ == "__main__":
    main()
