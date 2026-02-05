#!/usr/bin/env python3
"""
Pi Voice Assistant v2 - Mac mini用音声対話システム
- マイクで音声を拾う（sox/rec使用）
- Whisper APIで文字起こし
- OpenClaw Telegram経由で対話
- macOS TTSで返答を読み上げ
"""

import subprocess
import tempfile
import json
import urllib.request
import urllib.parse
import os
import sys
import time
import threading
from pathlib import Path

# 設定
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')
WORKSPACE = Path("/Users/ai-driven-work/Library/Mobile Documents/com~apple~CloudDocs/OpenClaw-Shared")

# 会話履歴
conversation_history = []


def record_audio(max_duration=15):
    """マイクから音声を録音（無音で自動停止）"""
    output_path = tempfile.mktemp(suffix='.wav')
    
    print("🎤 聞いてるよ... (話し終わったら自動で止まる)")
    
    try:
        # soxのrecコマンドで録音
        # silence 1 0.3 1% = 開始時に0.3秒以上の無音があればスキップ
        # silence 1 2.0 1% = 2秒の無音で停止
        result = subprocess.run([
            'rec', '-q', output_path,
            'rate', '16000',
            'channels', '1',
            'silence', '1', '0.1', '1%',  # 最初の無音をスキップ
            '1', '2.0', '1%',  # 2秒無音で停止
            'trim', '0', str(max_duration)  # 最大15秒
        ], timeout=max_duration + 5, capture_output=True)
    except subprocess.TimeoutExpired:
        print("（タイムアウト）")
    except Exception as e:
        print(f"録音エラー: {e}")
        return None
    
    if os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
        return output_path
    return None


def transcribe_audio(audio_path):
    """Whisper APIで文字起こし"""
    if not OPENAI_API_KEY:
        print("❌ OPENAI_API_KEY not set")
        return None
    
    boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
    
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
        print(f"❌ Transcription error: {e}")
        return None


def chat_with_claude(user_message):
    """Claude APIで対話"""
    if not OPENAI_API_KEY:
        # AnthropicのAPIキーを使う（環境変数から）
        pass
    
    # OpenAI互換APIを使う
    conversation_history.append({"role": "user", "content": user_message})
    
    system_prompt = """あなたはPi、いちさんの個人アシスタントです。
音声で会話しています。短く、自然に返答してください。
いちさんはAirCle代表で、AIツールや自動化に詳しい人です。
「今日はどんなことを自動化する？」のような提案をしてください。
返答は1-2文で簡潔に。"""
    
    messages = [{"role": "system", "content": system_prompt}] + conversation_history[-10:]
    
    body = json.dumps({
        "model": "gpt-4o",
        "messages": messages,
        "max_tokens": 200,
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
            assistant_message = result['choices'][0]['message']['content']
            conversation_history.append({"role": "assistant", "content": assistant_message})
            return assistant_message
    except Exception as e:
        print(f"❌ API error: {e}")
        return "ごめん、うまく処理できなかった。"


def speak_text(text, voice='Kyoko'):
    """macOS TTSで読み上げ"""
    # 長すぎるテキストは省略
    if len(text) > 500:
        text = text[:500] + "..."
    
    try:
        subprocess.run(['say', '-v', voice, text], check=True, timeout=60)
    except Exception as e:
        print(f"TTS error: {e}")


def main():
    print("=" * 50)
    print("🎙️ Pi Voice Assistant v2")
    print("=" * 50)
    print("Mac miniで動作中。話しかけてね！")
    print("終了: Ctrl+C または「終了」「バイバイ」と言う")
    print()
    
    # 起動メッセージ
    greeting = "おはよう！今日はどんなことを自動化する？"
    print(f"🤖 Pi: {greeting}")
    speak_text(greeting)
    
    while True:
        try:
            # 音声を録音
            audio_path = record_audio(max_duration=15)
            
            if not audio_path:
                continue
            
            # 文字起こし
            print("📝 文字起こし中...")
            user_text = transcribe_audio(audio_path)
            
            # 一時ファイル削除
            try:
                os.unlink(audio_path)
            except:
                pass
            
            if not user_text or len(user_text.strip()) < 2:
                continue
            
            print(f"👤 あなた: {user_text}")
            
            # 終了コマンド
            if any(word in user_text for word in ['終了', 'おわり', 'バイバイ', 'さようなら', 'ストップ']):
                farewell = "またね！いつでも呼んでね。"
                print(f"🤖 Pi: {farewell}")
                speak_text(farewell)
                break
            
            # Claude/GPTで返答生成
            print("🤖 考え中...")
            response = chat_with_claude(user_text)
            
            print(f"🤖 Pi: {response}")
            speak_text(response)
            
            print()
            
        except KeyboardInterrupt:
            print("\n👋 終了します")
            speak_text("バイバイ！")
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(1)


if __name__ == "__main__":
    main()
