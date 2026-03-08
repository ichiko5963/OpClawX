# GitHub Actions 同期スクリプト修正手順書

## 📋 やること3つ

### 1. sync.pyファイルを更新（2分）

**手順:**
1. GitHubで `OpenClaw/OpenClaw` リポジトリを開く
2. `scripts/sync.py` をクリック
3. 右上の ✏️ **Edit** ボタンをクリック
4. 現在の内容を **全削除**
5. 下記の修正版コードを **全貼り付け**

```python
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
```

6. **Commit changes** をクリック
   - Commit message: `Fix sync.py: add sync_docs_content() and migrate to gog CLI`

---

### 2. GitHub Actionsの設定を更新（3分）

**ファイル:** `.github/workflows/data-sync.yml` （または該当するワークフローファイル）

**変更内容:**
```yaml
name: Data Sync

on:
  schedule:
    - cron: '0 * * * *'  # 毎時実行
  workflow_dispatch:  # 手動実行も可能

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      # ★ 追加: gog CLIをインストール
      - name: Install gog CLI
        run: |
          brew install steipete/tap/gogcli
          
      # ★ 追加: gog認証設定
      - name: Setup gog auth
        env:
          GOG_TOKEN: ${{ secrets.GOG_TOKEN }}
        run: |
          mkdir -p ~/.config/gog
          echo "$GOG_TOKEN" > ~/.config/gog/credentials.json
          
      - name: Run sync
        env:
          EXPENSE_SHEET_ID: ${{ secrets.EXPENSE_SHEET_ID }}
        run: |
          python scripts/sync.py
```

---

### 3. GitHub Secretsを設定（5分）

**手順:**
1. GitHubリポジトリア → **Settings** → **Secrets and variables** → **Actions**
2. **New repository secret** をクリック
3. 以下のSecretsを追加:

| Secret名 | 値 |
|---------|-----|
| `GOG_TOKEN` | gog認証トークン（後述の取得方法） |
| `EXPENSE_SHEET_ID` | 経費スプレッドシートのID |

---

### 4. gog認証トークンの取得（Macで実行）

**ターミナルで実行:**
```bash
# gogがインストール済みの場合
ls ~/.config/gog/credentials.json

# または認証情報の場所を確認
gog auth list --json
```

**認証済みなら:**
- `~/.config/gog/credentials.json` の内容をコピー
- それをGitHub Secretsの `GOG_TOKEN` に設定

**未認証なら:**
```bash
gog auth add jiuhuot10@gmail.com --services gmail,calendar,tasks,drive
gog auth list --json
# 出力をコピーしてGOG_TOKENに設定
```

---

## ✅ 完了後の確認

1. GitHubで **Actions** タブを開く
2. **Data Sync** ワークフローをクリック
3. **Run workflow** をクリック（手動実行）
4. 緑色の✅が出れば成功！

---

## 🆘 エラーが出たら

**エラー: "gog: command not found"**
→ gog CLIのインストールstepを確認

**エラー: "authorization failed"**
→ GOG_TOKENの値を確認（期限切れの可能性）

**その他のエラー**
→ いちさんにSlack/Discordで連絡 → 私が調査

---

**所要時間の目安:** 10〜15分
**難易度:** ★★☆☆☆（普通）
