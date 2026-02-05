#!/usr/bin/env python3
"""
Pi Voice Assistant - Mac mini用音声対話システム
- マイクで音声を拾う
- Whisper APIで文字起こし
- OpenClawに送信
- TTSで返答を読み上げ
"""

import subprocess
import tempfile
import json
import urllib.request
import urllib.parse
import os
import sys
import time
from pathlib import Path

# 設定
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')
ELEVENLABS_API_KEY = os.environ.get('ELEVENLABS_API_KEY', '')
OPENCLAW_URL = "http://localhost:4444"  # OpenClaw Gateway

# ElevenLabs Voice ID (お好みで変更)
VOICE_ID = "21m00Tcm4TlvDq8ikWAM"  # Rachel (落ち着いた女性)


def record_audio(duration=5, output_path=None):
    """マイクから音声を録音"""
    if output_path is None:
        output_path = tempfile.mktemp(suffix='.wav')
    
    print("🎤 聞いてるよ...")
    
    # macOSのsoxで録音
    try:
        subprocess.run([
            'rec', '-q', output_path,
            'rate', '16000',
            'channels', '1',
            'trim', '0', str(duration),
            'silence', '1', '0.5', '1%', '1', '1.0', '1%'  # 無音検出で自動停止
        ], timeout=duration + 5, check=True)
    except subprocess.TimeoutExpired:
        pass
    except FileNotFoundError:
        # soxがない場合はffmpegを試す
        subprocess.run([
            'ffmpeg', '-y', '-f', 'avfoundation', '-i', ':0',
            '-t', str(duration), '-ar', '16000', '-ac', '1',
            output_path
        ], capture_output=True, timeout=duration + 5)
    
    return output_path


def transcribe_audio(audio_path):
    """Whisper APIで文字起こし"""
    if not OPENAI_API_KEY:
        print("❌ OPENAI_API_KEY not set")
        return None
    
    print("📝 文字起こし中...")
    
    # multipart form data
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
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read())
            return result.get('text', '')
    except Exception as e:
        print(f"❌ Transcription error: {e}")
        return None


def send_to_openclaw(message):
    """OpenClawにメッセージを送信"""
    print("🤖 考え中...")
    
    # OpenClaw sessions API経由でメッセージ送信
    # ここではシンプルにHTTP POSTでメッセージを送る
    
    try:
        # OpenClawのHTTP APIを使う（要設定）
        url = f"{OPENCLAW_URL}/api/chat"
        body = json.dumps({"message": message}).encode()
        
        req = urllib.request.Request(url, data=body, method='POST')
        req.add_header('Content-Type', 'application/json')
        
        with urllib.request.urlopen(req, timeout=60) as response:
            result = json.loads(response.read())
            return result.get('response', '')
    except Exception as e:
        print(f"❌ OpenClaw error: {e}")
        # フォールバック: 直接Anthropic APIを叩く
        return None


def speak_text(text):
    """TTSで読み上げ"""
    print(f"🔊 {text[:50]}...")
    
    if ELEVENLABS_API_KEY:
        # ElevenLabs TTS
        try:
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
            body = json.dumps({
                "text": text,
                "model_id": "eleven_multilingual_v2",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.75
                }
            }).encode()
            
            req = urllib.request.Request(url, data=body, method='POST')
            req.add_header('xi-api-key', ELEVENLABS_API_KEY)
            req.add_header('Content-Type', 'application/json')
            
            with urllib.request.urlopen(req) as response:
                audio_data = response.read()
                
                # 一時ファイルに保存して再生
                with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
                    f.write(audio_data)
                    audio_path = f.name
                
                subprocess.run(['afplay', audio_path], check=True)
                os.unlink(audio_path)
                return
        except Exception as e:
            print(f"ElevenLabs error: {e}, falling back to macOS TTS")
    
    # macOS標準TTS
    subprocess.run(['say', '-v', 'Kyoko', text], check=True)


def main():
    print("=" * 50)
    print("🎙️ Pi Voice Assistant")
    print("=" * 50)
    print("話しかけてね！終了するには Ctrl+C")
    print()
    
    # 起動メッセージ
    greeting = "おはよう！今日はどんなことを自動化する？"
    speak_text(greeting)
    
    while True:
        try:
            # 音声を録音
            audio_path = record_audio(duration=10)
            
            # ファイルが空でないか確認
            if not os.path.exists(audio_path) or os.path.getsize(audio_path) < 1000:
                continue
            
            # 文字起こし
            user_text = transcribe_audio(audio_path)
            os.unlink(audio_path)
            
            if not user_text or len(user_text.strip()) < 2:
                continue
            
            print(f"👤 あなた: {user_text}")
            
            # 終了コマンド
            if any(word in user_text for word in ['終了', 'おわり', 'バイバイ', 'さようなら']):
                speak_text("またね！")
                break
            
            # OpenClawに送信
            response = send_to_openclaw(user_text)
            
            if response:
                print(f"🤖 Pi: {response}")
                speak_text(response)
            else:
                speak_text("ごめん、うまく処理できなかった")
            
            print()
            
        except KeyboardInterrupt:
            print("\n👋 終了します")
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(1)


if __name__ == "__main__":
    main()
