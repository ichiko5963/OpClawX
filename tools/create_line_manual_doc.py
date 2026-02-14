#!/usr/bin/env python3
"""
Googleドキュメント作成 + 共有設定
"""
import json
import requests
from pathlib import Path

TOKEN_FILE = Path("/tmp/google_oauth_tokens.json")

def load_token():
    data = json.loads(TOKEN_FILE.read_text())
    url = "https://oauth2.googleapis.com/token"
    response = requests.post(url, data={
        'client_id': data['client_id'],
        'client_secret': data['client_secret'],
        'refresh_token': data['refresh_token'],
        'grant_type': 'refresh_token'
    })
    return response.json()['access_token']

def create_doc(title, content):
    """Googleドキュメント作成"""
    access_token = load_token()
    
    # ドキュメント作成
    url = "https://docs.googleapis.com/v1/documents"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    body = {'title': title}
    
    response = requests.post(url, headers=headers, json=body)
    if response.status_code != 200:
        raise Exception(f"Doc create failed: {response.text}")
    
    doc_data = response.json()
    doc_id = doc_data['documentId']
    
    print(f"✓ ドキュメント作成: {doc_id}")
    
    # コンテンツ追加
    url = f"https://docs.googleapis.com/v1/documents/{doc_id}:batchUpdate"
    requests_list = [{
        'insertText': {
            'location': {'index': 1},
            'text': content
        }
    }]
    
    response = requests.post(url, headers=headers, json={'requests': requests_list})
    if response.status_code != 200:
        raise Exception(f"Content insert failed: {response.text}")
    
    print("✓ コンテンツ追加完了")
    
    # 共有設定（誰でも閲覧可能）
    url = f"https://www.googleapis.com/drive/v3/files/{doc_id}/permissions"
    body = {
        'type': 'anyone',
        'role': 'reader'
    }
    
    response = requests.post(url, headers=headers, json=body)
    if response.status_code != 200:
        raise Exception(f"Permission failed: {response.text}")
    
    print("✓ 共有設定完了（誰でも閲覧可能）")
    
    doc_url = f"https://docs.google.com/document/d/{doc_id}/edit"
    print(f"\n📄 ドキュメントURL:")
    print(doc_url)
    
    return doc_url

if __name__ == "__main__":
    content = Path("/tmp/line_manual.md").read_text()
    create_doc("PLai領収書管理 - 使い方マニュアル", content)
