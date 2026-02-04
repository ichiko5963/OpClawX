#!/usr/bin/env python3
"""
Pi Voice Assistant Server
- Receives user speech text from browser
- Sends to OpenClaw for processing
- Generates TTS via ElevenLabs
- Returns response with audio
"""

import os
import sys
import json
import subprocess
import tempfile
import hashlib
import urllib.request
import urllib.error
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading

# Configuration
HOST = 'localhost'
PORT = 5555
ELEVENLABS_API_KEY = os.environ.get('ELEVENLABS_API_KEY', '')
ELEVENLABS_VOICE_ID = 'EXAVITQu4vr4xnSDxMaL'  # Bella - warm female voice
AUDIO_CACHE_DIR = Path('/tmp/pi-voice-cache')
WORKSPACE = Path('/Users/ai-driven-work/Library/Mobile Documents/com~apple~CloudDocs/OpenClaw-Shared')

# Load ElevenLabs API key from file if not in env
if not ELEVENLABS_API_KEY:
    key_file = Path.home() / '.config/openclaw/secrets/elevenlabs.env'
    if key_file.exists():
        with open(key_file) as f:
            for line in f:
                if line.startswith('ELEVENLABS_API_KEY='):
                    ELEVENLABS_API_KEY = line.strip().split('=', 1)[1]
                    break

# Create cache dir
AUDIO_CACHE_DIR.mkdir(parents=True, exist_ok=True)


class VoiceAssistantHandler(BaseHTTPRequestHandler):
    """HTTP Request Handler for voice assistant"""
    
    def log_message(self, format, *args):
        """Custom logging"""
        print(f"[{self.log_date_time_string()}] {format % args}")
    
    def send_cors_headers(self):
        """Send CORS headers for browser access"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
    
    def do_OPTIONS(self):
        """Handle preflight CORS requests"""
        self.send_response(200)
        self.send_cors_headers()
        self.end_headers()
    
    def do_GET(self):
        """Handle GET requests"""
        parsed = urlparse(self.path)
        
        if parsed.path == '/health':
            self.send_json({'status': 'ok'})
        
        elif parsed.path.startswith('/audio/'):
            # Serve cached audio file
            filename = parsed.path.split('/')[-1]
            audio_path = AUDIO_CACHE_DIR / filename
            
            if audio_path.exists():
                self.send_response(200)
                self.send_header('Content-Type', 'audio/mpeg')
                self.send_cors_headers()
                self.end_headers()
                
                with open(audio_path, 'rb') as f:
                    self.wfile.write(f.read())
            else:
                self.send_error(404, 'Audio not found')
        
        else:
            self.send_error(404, 'Not found')
    
    def do_POST(self):
        """Handle POST requests"""
        parsed = urlparse(self.path)
        
        if parsed.path == '/api/chat':
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            
            try:
                data = json.loads(body)
                user_text = data.get('text', '')
                
                if not user_text:
                    self.send_json({'error': 'No text provided'}, 400)
                    return
                
                print(f"User: {user_text}")
                
                # Get AI response
                response_text = get_ai_response(user_text)
                print(f"Pi: {response_text}")
                
                # Generate TTS
                audio_url = None
                if ELEVENLABS_API_KEY:
                    audio_filename = generate_tts(response_text)
                    if audio_filename:
                        audio_url = f'http://{HOST}:{PORT}/audio/{audio_filename}'
                
                self.send_json({
                    'response': response_text,
                    'audio_url': audio_url
                })
                
            except json.JSONDecodeError:
                self.send_json({'error': 'Invalid JSON'}, 400)
            except Exception as e:
                print(f"Error: {e}")
                self.send_json({'error': str(e)}, 500)
        
        else:
            self.send_error(404, 'Not found')
    
    def send_json(self, data, status=200):
        """Send JSON response"""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))


def get_ai_response(user_text: str) -> str:
    """Get response from OpenClaw"""
    
    try:
        # Method 1: Use openclaw CLI directly
        result = subprocess.run(
            ['openclaw', 'chat', '--message', user_text, '--quiet'],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=str(WORKSPACE)
        )
        
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
        
    except subprocess.TimeoutExpired:
        print("OpenClaw timeout")
    except FileNotFoundError:
        print("OpenClaw CLI not found")
    except Exception as e:
        print(f"OpenClaw error: {e}")
    
    # Method 2: Simple fallback responses
    return get_fallback_response(user_text)


def get_fallback_response(user_text: str) -> str:
    """Fallback responses when OpenClaw is not available"""
    
    text_lower = user_text.lower()
    
    if 'こんにちは' in text_lower or 'やあ' in text_lower:
        return 'やあ、いちさん！元気？今日もよろしくね！'
    
    elif 'ありがとう' in text_lower:
        return 'どういたしまして！いつでも話しかけてね！'
    
    elif '元気' in text_lower:
        return '俺は元気だよ！いちさんは？何か手伝えることある？'
    
    elif 'かわいい' in text_lower or '可愛い' in text_lower:
        return 'えへへ、ありがとう！いちさんに褒められると嬉しいな！'
    
    elif 'おやすみ' in text_lower:
        return 'おやすみ、いちさん！ゆっくり休んでね。また明日！'
    
    elif '何できる' in text_lower or '機能' in text_lower:
        return '俺はいちさんの秘書ロボットだよ！メールやSlackのチェック、タスク管理、あと雑談もできるよ！'
    
    elif 'タスク' in text_lower or 'やること' in text_lower:
        return '今のGoogle Tasksには修士論文関連のタスクが5個あるよ。確認する？'
    
    elif 'today' in text_lower or '今日' in text_lower:
        return '今日はContext Curatorを完成させたね！Gmail、Slack、Calendar、Google Tasksが全部連携してるよ。'
    
    else:
        return f'「{user_text}」って言ったね！OpenClawとの接続がうまくいってないみたい。サーバーを確認してね。'


def generate_tts(text: str) -> str:
    """Generate TTS audio using ElevenLabs"""
    
    if not ELEVENLABS_API_KEY:
        print("No ElevenLabs API key")
        return None
    
    # Check cache
    text_hash = hashlib.md5(text.encode('utf-8')).hexdigest()[:12]
    cache_filename = f'voice_{text_hash}.mp3'
    cache_path = AUDIO_CACHE_DIR / cache_filename
    
    if cache_path.exists():
        print(f"Using cached audio: {cache_filename}")
        return cache_filename
    
    try:
        url = f'https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}'
        
        payload = json.dumps({
            'text': text,
            'model_id': 'eleven_multilingual_v2',
            'voice_settings': {
                'stability': 0.5,
                'similarity_boost': 0.75,
                'style': 0.5,
                'use_speaker_boost': True
            }
        }).encode('utf-8')
        
        req = urllib.request.Request(
            url,
            data=payload,
            headers={
                'Content-Type': 'application/json',
                'xi-api-key': ELEVENLABS_API_KEY
            }
        )
        
        with urllib.request.urlopen(req, timeout=30) as response:
            audio_data = response.read()
            
            with open(cache_path, 'wb') as f:
                f.write(audio_data)
            
            print(f"Generated audio: {cache_filename}")
            return cache_filename
    
    except urllib.error.HTTPError as e:
        print(f"ElevenLabs API error: {e.code} - {e.read().decode()}")
    except Exception as e:
        print(f"TTS error: {e}")
    
    return None


def run_server():
    """Start the HTTP server"""
    
    print(f"""
╔════════════════════════════════════════════════════════════╗
║                    Pi Voice Assistant                       ║
║────────────────────────────────────────────────────────────║
║  Server: http://{HOST}:{PORT}                                 ║
║  ElevenLabs: {'Configured' if ELEVENLABS_API_KEY else 'Not configured'}                                    ║
║────────────────────────────────────────────────────────────║
║  Endpoints:                                                 ║
║    GET  /health        - Health check                      ║
║    POST /api/chat      - Send chat message                 ║
║    GET  /audio/<file>  - Get cached audio                  ║
╚════════════════════════════════════════════════════════════╝
    """)
    
    server = HTTPServer((HOST, PORT), VoiceAssistantHandler)
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.shutdown()


if __name__ == '__main__':
    run_server()
