#!/usr/bin/env python3
"""
Pi Voice Bridge Server
- Receives chat requests from Vercel app
- Forwards to OpenClaw
- Returns response with TTS
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.request
import urllib.error
import hashlib

# Config
HOST = '0.0.0.0'  # Allow external connections
PORT = 5555
WORKSPACE = Path('/Users/ai-driven-work/Library/Mobile Documents/com~apple~CloudDocs/OpenClaw-Shared')

# Load ElevenLabs API key
ELEVENLABS_API_KEY = ''
key_file = Path.home() / '.config/openclaw/secrets/elevenlabs.env'
if key_file.exists():
    with open(key_file) as f:
        for line in f:
            if line.startswith('ELEVENLABS_API_KEY='):
                ELEVENLABS_API_KEY = line.strip().split('=', 1)[1]
                break

# Audio cache
AUDIO_CACHE = Path('/tmp/pi-voice-cache')
AUDIO_CACHE.mkdir(exist_ok=True)


class RequestHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        print(f'[{self.log_date_time_string()}] {format % args}')
    
    def send_cors(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_cors()
        self.end_headers()
    
    def do_GET(self):
        if self.path == '/health':
            self.send_json({'status': 'ok', 'elevenlabs': bool(ELEVENLABS_API_KEY)})
        elif self.path.startswith('/audio/'):
            filename = self.path.split('/')[-1]
            filepath = AUDIO_CACHE / filename
            if filepath.exists():
                self.send_response(200)
                self.send_header('Content-Type', 'audio/mpeg')
                self.send_cors()
                self.end_headers()
                with open(filepath, 'rb') as f:
                    self.wfile.write(f.read())
            else:
                self.send_error(404)
        else:
            self.send_error(404)
    
    def do_POST(self):
        if self.path == '/api/chat':
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            
            try:
                data = json.loads(body)
                text = data.get('text', data.get('message', ''))
                
                if not text:
                    self.send_json({'error': 'No text provided'}, 400)
                    return
                
                print(f'User: {text}')
                
                # Get response from OpenClaw
                response = self.get_openclaw_response(text)
                print(f'Pi: {response}')
                
                # Generate TTS
                audio_url = None
                if ELEVENLABS_API_KEY:
                    audio_filename = self.generate_tts(response)
                    if audio_filename:
                        # Return base64 audio data
                        audio_path = AUDIO_CACHE / audio_filename
                        if audio_path.exists():
                            with open(audio_path, 'rb') as f:
                                import base64
                                audio_data = base64.b64encode(f.read()).decode()
                                audio_url = f'data:audio/mpeg;base64,{audio_data}'
                
                self.send_json({
                    'response': response,
                    'audioUrl': audio_url,
                    'connected': True
                })
                
            except json.JSONDecodeError:
                self.send_json({'error': 'Invalid JSON'}, 400)
            except Exception as e:
                print(f'Error: {e}')
                self.send_json({'error': str(e)}, 500)
        else:
            self.send_error(404)
    
    def get_openclaw_response(self, text: str) -> str:
        """Get response from OpenClaw CLI"""
        try:
            # Use sessions_send approach - write to a file that OpenClaw can pick up
            # For now, just use simple responses and let Vercel handle it
            
            # Try openclaw chat command
            result = subprocess.run(
                ['openclaw', 'chat', '-m', text, '-q'],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=str(WORKSPACE)
            )
            
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
            
        except subprocess.TimeoutExpired:
            print('OpenClaw timeout')
        except FileNotFoundError:
            print('OpenClaw CLI not found')
        except Exception as e:
            print(f'OpenClaw error: {e}')
        
        # Fallback
        return self.fallback_response(text)
    
    def fallback_response(self, text: str) -> str:
        """Fallback responses"""
        t = text.lower()
        
        if 'こんにちは' in t or 'やあ' in t:
            return 'やあ、いちさん！元気？'
        elif 'ありがとう' in t:
            return 'どういたしまして！'
        elif '元気' in t:
            return '俺は元気だよ！いちさんは？'
        elif 'かわいい' in t:
            return 'えへへ、ありがとう！'
        elif 'おやすみ' in t:
            return 'おやすみ、いちさん！'
        else:
            return f'「{text}」って言ったね！'
    
    def generate_tts(self, text: str) -> str:
        """Generate TTS using ElevenLabs"""
        if not ELEVENLABS_API_KEY:
            return None
        
        # Check cache
        text_hash = hashlib.md5(text.encode()).hexdigest()[:12]
        filename = f'voice_{text_hash}.mp3'
        filepath = AUDIO_CACHE / filename
        
        if filepath.exists():
            return filename
        
        try:
            voice_id = 'EXAVITQu4vr4xnSDxMaL'
            url = f'https://api.elevenlabs.io/v1/text-to-speech/{voice_id}'
            
            payload = json.dumps({
                'text': text,
                'model_id': 'eleven_multilingual_v2',
                'voice_settings': {
                    'stability': 0.5,
                    'similarity_boost': 0.75
                }
            }).encode()
            
            req = urllib.request.Request(url, data=payload, headers={
                'Content-Type': 'application/json',
                'xi-api-key': ELEVENLABS_API_KEY
            })
            
            with urllib.request.urlopen(req, timeout=30) as resp:
                audio_data = resp.read()
                with open(filepath, 'wb') as f:
                    f.write(audio_data)
                return filename
                
        except urllib.error.HTTPError as e:
            print(f'ElevenLabs error: {e.code}')
        except Exception as e:
            print(f'TTS error: {e}')
        
        return None
    
    def send_json(self, data: dict, status: int = 200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_cors()
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode())


def main():
    print(f'''
╔═══════════════════════════════════════════════════════════╗
║               Pi Voice Bridge Server                       ║
╠═══════════════════════════════════════════════════════════╣
║  Server: http://{HOST}:{PORT}                                 ║
║  ElevenLabs: {'✓ Configured' if ELEVENLABS_API_KEY else '✗ Not configured'}                              ║
╠═══════════════════════════════════════════════════════════╣
║  Endpoints:                                                ║
║    GET  /health      - Health check                       ║
║    POST /api/chat    - Chat with Pi                       ║
╚═══════════════════════════════════════════════════════════╝
    ''')
    
    server = HTTPServer((HOST, PORT), RequestHandler)
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\nShutting down...')
        server.shutdown()


if __name__ == '__main__':
    main()
