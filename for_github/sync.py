#!/usr/bin/env python3
"""OpenClaw データ同期スクリプト（修正版）- GitHub Actions用"""
import os, sys, json, subprocess
from datetime import datetime, timedelta

def run_gog(cmd, timeout=60):
    """gog CLIコマンド実行"""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        if result.returncode == 0:
            return json.loads(result.stdout) if result.stdout else []
        else:
            print(f"  ⚠️  {result.stderr[:100]}")
    except Exception as e:
        print(f"  ⚠️  {e}")
    return []

def sync_gmail():
    print("📧 Gmail同期...")
    return run_gog(['gog','gmail','search','newer_than:1d','--max','50','--json'])

def sync_calendar():
    print("📅 Calendar同期...")
    today = datetime.now().strftime('%Y-%m-%d')
    tomorrow = (datetime.now()+timedelta(days=1)).strftime('%Y-%m-%d')
    return run_gog(['gog','calendar','events','primary','--from',today,'--to',tomorrow,'--json'])

def sync_tasks():
    print("✅ Tasks同期...")
    return run_gog(['gog','tasks','list','--max','100','--json'])

def sync_drive():
    print("🎤 Drive同期...")
    return run_gog(['gog','drive','search','mimeType:audio/*','--max','10','--json'])

def sync_sheets():
    print("📊 Sheets同期...")
    sheet_id = os.getenv('EXPENSE_SHEET_ID','')
    if not sheet_id: print("  ⚠️ シートID未設定"); return []
    return run_gog(['gog','sheets','get',sheet_id,'経費!A1:Z100','--json'])

def sync_docs():
    print("📄 Docs同期...")
    return run_gog(['gog','drive','search','mimeType:application/vnd.google-apps.document','--max','10','--json'])

def sync_slides():
    print("🎨 Slides同期...")
    return run_gog(['gog','drive','search','mimeType:application/vnd.google-apps.presentation','--max','10','--json'])

def sync_docs_content():
    """ドキュメント内容同期（修正: この関数が未定義でエラーになってた）"""
    print("📄 Docs内容同期...")
    docs = sync_docs()
    contents = []
    for doc in docs[:5]:
        doc_id = doc.get('id')
        if doc_id:
            try:
                r = subprocess.run(['gog','docs','export',doc_id,'--format','txt'], 
                                 capture_output=True, text=True, timeout=30)
                if r.returncode == 0:
                    contents.append({'id':doc_id,'title':doc.get('name','Unknown'),'content':r.stdout[:1000]})
            except: pass
    print(f"  ✅ {len(contents)}件の内容取得")
    return contents

def main():
    print("="*60)
    print("🚀 データ同期開始")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    results = {}
    try: results['gmail'] = sync_gmail()
    except Exception as e: print(f"  ⚠️ Gmail: {e}")
    
    try: results['calendar'] = sync_calendar()
    except Exception as e: print(f"  ⚠️ Calendar: {e}")
    
    try: results['tasks'] = sync_tasks()
    except Exception as e: print(f"  ⚠️ Tasks: {e}")
    
    try: results['drive'] = sync_drive()
    except Exception as e: print(f"  ⚠️ Drive: {e}")
    
    try: results['sheets'] = sync_sheets()
    except Exception as e: print(f"  ⚠️ Sheets: {e}")
    
    try: results['docs'] = sync_docs()
    except Exception as e: print(f"  ⚠️ Docs: {e}")
    
    try: results['slides'] = sync_slides()
    except Exception as e: print(f"  ⚠️ Slides: {e}")
    
    try: results['docs_content'] = sync_docs_content()
    except Exception as e: print(f"  ⚠️ Docs内容: {e}")
    
    # 結果保存
    output_dir = os.getenv('SYNC_OUTPUT_DIR','./sync_output')
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f"sync_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    with open(output_file,'w',encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 完了: {output_file}")
    return 0

if __name__=='__main__':
    sys.exit(main())
