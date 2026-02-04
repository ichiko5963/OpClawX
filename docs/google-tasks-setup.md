# Google Tasks 連携セットアップ

## 1. n8n で Google Tasks 認証を追加

1. http://localhost:5678 を開く
2. 左メニュー → **Credentials** → **Add Credential**
3. **Google Tasks OAuth2 API** を選択
4. 既存のGoogle認証情報から以下をコピー：
   - Client ID
   - Client Secret
5. **Scopes** に `https://www.googleapis.com/auth/tasks` を追加
6. **Connect** をクリックしてOAuth認証
7. 保存

## 2. ワークフローに Google Tasks ノードを追加

1. **Hourly Sync - Complete** ワークフローを開く
2. **Google Tasks** ノードを追加
3. 以下の設定：
   - Resource: Task
   - Operation: Get Many
   - Task List: @default（または特定のリスト）
   - Return All: true
4. **Tag Tasks** ノードを追加（Codeノード）:

```javascript
return items.map(item => ({
  json: {
    source: 'gtasks',
    tasks: item.json
  }
}));
```

5. **Merge All** ノードに接続
6. 保存 & Activate

## 3. 確認

```bash
python3 scripts/google_tasks_manager.py
```

## スコープ追加が必要な場合

Google Cloud Console で Tasks API を有効化:
1. https://console.cloud.google.com/apis/library/tasks.googleapis.com
2. **有効にする** をクリック
