#!/usr/bin/env python3
"""
Pi Voice - Mac mini 音声アシスタント
OpenClawに接続して本当の会話をする
"""

import subprocess
import tempfile
import json
import urllib.request
import os
import sys
import time

# 設定
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')
OPENCLAW_URL = "http://localhost:4444"

# 会話履歴
conversation_history = []

def speak(text):
    """macOS TTSで話す"""
    print(f"🦞 Pi: {text}")
    # Kyoko (日本語) で話す
    subprocess.run(['say', '-v', 'Kyoko', '-r', '180', text], check=True)

def record_audio(max_duration=10):
    """マイクから録音"""
    output_path = tempfile.mktemp(suffix='.wav')
    
    print("👂 聞いてます...")
    
    try:
        # sox で録音（2秒無音で停止）
        subprocess.run([
            'rec', '-q', output_path,
            'rate', '16000',
            'channels', '1',
            'silence', '1', '0.1', '1%',
            '1', '2.0', '1%',
            'trim', '0', str(max_duration)
        ], timeout=max_duration + 5, capture_output=True)
    except subprocess.TimeoutExpired:
        pass
    except Exception as e:
        print(f"録音エラー: {e}")
        return None
    
    if os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
        return output_path
    return None

def transcribe(audio_path):
    """Whisper APIで文字起こし"""
    if not OPENAI_API_KEY:
        print("❌ OPENAI_API_KEY が設定されていません")
        return None
    
    boundary = '----FormBoundary7MA4YWxk'
    
    with open(audio_path, 'rb') as f:
        audio_data = f.read()
    
    body = (
        f'--{boundary}\r\n'
        f'Content-Disposition: form-data; name="file"; filename="audio.wav"\r\n'
        f'Content-Type: audio/wav\r\n\r\n'
    ).encode() + audio_data + (
        f'\r\n--{boundary}\r\n'
        f'Content-Disposition: form-data; name="model"\r\n\r\n'
        f'whisper-1\r\n'
        f'--{boundary}\r\n'
        f'Content-Disposition: form-data; name="language"\r\n\r\n'
        f'ja\r\n'
        f'--{boundary}--\r\n'
    ).encode()
    
    req = urllib.request.Request(
        'https://api.openai.com/v1/audio/transcriptions',
        data=body,
        method='POST'
    )
    req.add_header('Authorization', f'Bearer {OPENAI_API_KEY}')
    req.add_header('Content-Type', f'multipart/form-data; boundary={boundary}')
    
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read())
            return result.get('text', '')
    except Exception as e:
        print(f"文字起こしエラー: {e}")
        return None

def chat_with_openclaw(user_message):
    """OpenClawに直接接続して会話"""
    
    # 会話履歴に追加
    conversation_history.append(f"ユーザー: {user_message}")
    
    # OpenClawのAPIを試す
    try:
        body = json.dumps({
            "message": user_message,
            "sessionId": "voice-assistant"
        }).encode()
        
        req = urllib.request.Request(
            f"{OPENCLAW_URL}/api/chat",
            data=body,
            method='POST'
        )
        req.add_header('Content-Type', 'application/json')
        
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read())
            reply = result.get('response') or result.get('message') or result.get('text')
            if reply:
                conversation_history.append(f"Pi: {reply}")
                return reply
    except Exception as e:
        print(f"OpenClaw接続エラー: {e}, GPT-4oにフォールバック")
    
    # フォールバック: OpenAI API直接
    return chat_with_gpt(user_message)

def chat_with_gpt(user_message):
    """GPT-4oで会話"""
    if not OPENAI_API_KEY:
        return "APIキーがないから返事できないよ..."
    
    context = "\n".join(conversation_history[-10:])
    
    system_prompt = f"""あなたはPi、いちさん専用のAIアシスタントです。
性格: フレンドリーで頼りになる。
話し方: カジュアル、敬語なし、短く簡潔に（1-2文）。

いちさんについて:
- AirCle（大学生AI団体）の代表
- AIツールや自動化が得意
- 忙しいので効率重視

直近の会話:
{context}

重要: 文脈を踏まえて返答。同じことを繰り返さない。"""

    body = json.dumps({
        "model": "gpt-4o",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        "max_tokens": 150,
        "temperature": 0.8
    }).encode()
    
    req = urllib.request.Request(
        'https://api.openai.com/v1/chat/completions',
        data=body,
        method='POST'
    )
    req.add_header('Authorization', f'Bearer {OPENAI_API_KEY}')
    req.add_header('Content-Type', 'application/json')
    
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read())
            reply = result['choices'][0]['message']['content']
            conversation_history.append(f"Pi: {reply}")
            return reply
    except Exception as e:
        print(f"GPTエラー: {e}")
        return "ごめん、ちょっとエラーが起きちゃった。"

def main():
    print("=" * 50)
    print("🦞 Pi Voice - Mac mini")
    print("=" * 50)
    print("終了: Ctrl+C または「終了」と言う")
    print()
    
    # 挨拶
    hour = time.localtime().tm_hour
    if hour < 12:
        greeting = "おはよう、いちさん！今日はどんなことを自動化する？"
    elif hour < 18:
        greeting = "やあ、いちさん！何か手伝えることある？"
    else:
        greeting = "こんばんは！今日も一日お疲れ様。何か話そうか？"
    
    speak(greeting)
    
    while True:
        try:
            # 録音
            audio_path = record_audio()
            
            if not audio_path:
                continue
            
            # 文字起こし
            user_text = transcribe(audio_path)
            
            # 一時ファイル削除
            try:
                os.unlink(audio_path)
            except:
                pass
            
            if not user_text or len(user_text.strip()) < 2:
                continue
            
            print(f"👤 あなた: {user_text}")
            
            # 終了コマンド
            if any(word in user_text for word in ['終了', 'おわり', 'バイバイ', 'さようなら']):
                speak("またね！いつでも呼んでね。")
                break
            
            # 返答を取得
            print("💭 考え中...")
            response = chat_with_openclaw(user_text)
            
            # 話す
            speak(response)
            print()
            
        except KeyboardInterrupt:
            print("\n👋 終了します")
            speak("バイバイ！")
            break
        except Exception as e:
            print(f"エラー: {e}")
            time.sleep(1)

if __name__ == "__main__":
    main()
