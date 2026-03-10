#!/usr/bin/env python3
"""Google API直接アクセス用ヘルパー（新OAuth対応版）"""
import os
import json
import pickle
from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# 認証情報保存先
TOKEN_DIR = Path.home() / '.openclaw' / 'google_auth'
TOKEN_DIR.mkdir(parents=True, exist_ok=True)

def get_credentials(service_name, scopes):
    """Google API認証情報を取得"""
    token_file = TOKEN_DIR / f'{service_name}_token.pickle'
    creds_file = TOKEN_DIR / 'credentials.json'
    
    creds = None
    
    # 既存のトークンがあれば読み込み
    if token_file.exists():
        with open(token_file, 'rb') as token:
            creds = pickle.load(token)
    
    # 有効でない場合は更新または新規作成
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # クライアントシークレットファイルが必要
            if not creds_file.exists():
                print(f"エラー: {creds_file} が見つかりません")
                print("Google Cloud Consoleからcredentials.jsonをダウンロードしてください")
                return None
            
            flow = InstalledAppFlow.from_client_secrets_file(
                str(creds_file), scopes)
            creds = flow.run_local_server(port=0)
        
        # トークンを保存
        with open(token_file, 'wb') as token:
            pickle.dump(creds, token)
    
    return creds

def get_calendar_service():
    """Google Calendar APIサービスを取得"""
    SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
    creds = get_credentials('calendar', SCOPES)
    if creds:
        return build('calendar', 'v3', credentials=creds)
    return None

def get_gmail_service():
    """Gmail APIサービスを取得"""
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
    creds = get_credentials('gmail', SCOPES)
    if creds:
        return build('gmail', 'v1', credentials=creds)
    return None

def get_tasks_service():
    """Google Tasks APIサービスを取得"""
    SCOPES = ['https://www.googleapis.com/auth/tasks.readonly']
    creds = get_credentials('tasks', SCOPES)
    if creds:
        return build('tasks', 'v1', credentials=creds)
    return None

if __name__ == '__main__':
    # テスト
    print("認証ヘルパーテスト")
    service = get_calendar_service()
    if service:
        print("✅ Calendar API接続成功")
    else:
        print("❌ Calendar API接続失敗")
