#!/usr/bin/env python3
"""
Pi Voice v7 - 超シンプル版
固定3秒録音、無音検知なし
確実に音を拾う
"""

import subprocess
import tempfile
import json
import urllib.request
import os
import time
import threading
import http.server
import socketserver

OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')
PORT = 8771
WORKSPACE = "/Users/ai-driven-work/Library/Mobile Documents/com~apple~CloudDocs/OpenClaw-Shared"
LOG_FILE = f"{WORKSPACE}/logs/pi_voice.log"

os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

def log(msg):
    ts = time.strftime("%H:%M:%S")
    try:
        with open(LOG_FILE, 'a') as f:
            f.write(f"[{ts}] {msg}\n")
    except:
        pass
    print(f"[{ts}] {msg}", flush=True)

conversation = []
state = {
    "status": "idle",
    "transcript": "",
    "history": [],
    "muted": False,
    "turn": 0
}

def get_memory():
    """MEMORY.md + Obsidianの関連情報を読み込む"""
    content = []
    
    # MEMORY.md
    try:
        with open(f"{WORKSPACE}/MEMORY.md", 'r') as f:
            content.append("# MEMORY.md\n" + f.read()[:4000])
    except:
        pass
    
    # Obsidian: アクティブプロジェクト
    projects_dir = f"{WORKSPACE}/obsidian/Ichioka Obsidian/03_Projects/_Active"
    try:
        for proj in os.listdir(projects_dir):
            proj_path = os.path.join(projects_dir, proj)
            if os.path.isdir(proj_path):
                # MEMORY.md or README.md
                for fname in ['MEMORY.md', 'README.md', 'PROFILE.md']:
                    fpath = os.path.join(proj_path, fname)
                    if os.path.exists(fpath):
                        try:
                            with open(fpath, 'r') as f:
                                content.append(f"# {proj}\n" + f.read()[:1000])
                        except:
                            pass
                        break
    except:
        pass
    
    # Obsidian: 人物情報 (主要人物のみ)
    people_dir = f"{WORKSPACE}/obsidian/Ichioka Obsidian/10_People"
    try:
        for person in os.listdir(people_dir)[:10]:  # 最大10人
            person_path = os.path.join(people_dir, person)
            if os.path.isdir(person_path):
                profile = os.path.join(person_path, 'PROFILE.md')
                if os.path.exists(profile):
                    try:
                        with open(profile, 'r') as f:
                            content.append(f"# {person}\n" + f.read()[:500])
                    except:
                        pass
    except:
        pass
    
    # Obsidian: 企業情報
    companies_dir = f"{WORKSPACE}/obsidian/Ichioka Obsidian/11_Companies"
    try:
        for company in os.listdir(companies_dir)[:10]:
            company_path = os.path.join(companies_dir, company)
            if os.path.isdir(company_path):
                profile = os.path.join(company_path, 'PROFILE.md')
                if os.path.exists(profile):
                    try:
                        with open(profile, 'r') as f:
                            content.append(f"# {company}\n" + f.read()[:500])
                    except:
                        pass
    except:
        pass
    
    # 今日のメモリ
    today = time.strftime("%Y-%m-%d")
    today_file = f"{WORKSPACE}/memory/{today}.md"
    try:
        if os.path.exists(today_file):
            with open(today_file, 'r') as f:
                content.append(f"# 今日のメモ ({today})\n" + f.read()[:1000])
    except:
        pass
    
    result = "\n\n".join(content)
    # トークン制限を考慮して切り詰め
    return result[:12000]

def chat(user_msg):
    global conversation
    state["status"] = "thinking"
    
    if not OPENAI_API_KEY:
        return "APIキーがない"
    
    conversation.append({"role": "user", "content": user_msg})
    if len(conversation) > 30:
        conversation = conversation[-30:]
    
    memory = get_memory()
    
    system_prompt = f"""あなたはPi、いちさん専用のAIアシスタント。

{memory}

# ルール
- 会話の文脈を理解して返答
- カジュアル、敬語なし
- 具体的に答える"""

    messages = [{"role": "system", "content": system_prompt}] + conversation
    log(f"GPT: {len(conversation)} msgs")
    
    body = json.dumps({
        "model": "gpt-4o",
        "messages": messages,
        "max_tokens": 400
    }).encode()
    
    req = urllib.request.Request(
        'https://api.openai.com/v1/chat/completions',
        data=body, method='POST'
    )
    req.add_header('Authorization', f'Bearer {OPENAI_API_KEY}')
    req.add_header('Content-Type', 'application/json')
    
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            reply = json.loads(r.read())['choices'][0]['message']['content']
            conversation.append({"role": "assistant", "content": reply})
            return reply
    except Exception as e:
        log(f"API Error: {e}")
        return "ごめん、もう一回言って"

HTML = '''<!DOCTYPE html><html lang="ja"><head><meta charset="UTF-8"><title>Pi</title>
<style>*{margin:0;padding:0;box-sizing:border-box}html,body{height:100%;overflow:hidden;font-family:-apple-system,sans-serif}.app{display:grid;grid-template-columns:1fr 360px;height:100vh}.main{background:linear-gradient(160deg,#e8a090,#d4877a);display:flex;flex-direction:column;align-items:center;justify-content:center;position:relative}.face{display:flex;flex-direction:column;align-items:center}.eyes{display:flex;gap:40px;margin-bottom:18px}.eye{width:60px;height:75px;background:#1a1a1a;border-radius:10px}.mouth{width:45px;height:22px;background:#1a1a1a;border-radius:6px;opacity:0}.face.idle .eye{animation:blink 4s infinite}@keyframes blink{0%,45%,55%,100%{transform:scaleY(1)}50%{transform:scaleY(.1)}}.face.listening .eye{height:22px;width:65px;background:#333;animation:pulse .3s infinite}@keyframes pulse{0%,100%{opacity:1}50%{opacity:.5}}.face.speaking .eye{animation:sb .08s infinite alternate}.face.speaking .mouth{opacity:1;animation:talk .06s infinite alternate}@keyframes sb{0%{transform:scaleY(1)}100%{transform:scaleY(.6)}}@keyframes talk{0%{height:15px}100%{height:35px}}.face.thinking .eye{animation:think .5s infinite}@keyframes think{0%,100%{transform:translateX(0)}50%{transform:translateX(8px)}}.face.muted .eye{opacity:.2}.transcript{position:absolute;bottom:80px;font-size:20px;color:#1a1a1a;max-width:85%;text-align:center}.status{position:absolute;bottom:35px;padding:8px 20px;background:rgba(0,0,0,.1);border-radius:20px;font-size:13px}.info{position:absolute;top:20px;left:20px;font-size:12px;color:rgba(0,0,0,.3)}.mute{position:absolute;top:20px;right:20px;padding:10px 18px;background:rgba(0,0,0,.1);border:none;border-radius:20px;font-size:14px;cursor:pointer}.mute.on{background:rgba(0,0,0,.3);color:#fff}.sidebar{background:#0a0a0a;display:flex;flex-direction:column;height:100vh}.sidebar-head{padding:18px;border-bottom:1px solid #1a1a1a;display:flex;justify-content:space-between}.sidebar-title{font-size:11px;color:#555;text-transform:uppercase}.clear-btn{padding:6px 12px;background:#1a1a1a;border:none;border-radius:6px;color:#666;font-size:11px;cursor:pointer}.history{flex:1;overflow-y:auto;padding:15px}.msg{margin-bottom:12px;padding:12px;background:#111;border-radius:10px}.msg.pi{border-left:3px solid #e8a090}.msg.user{border-left:3px solid #7ec8e3}.msg-who{font-size:10px;font-weight:600;margin-bottom:6px}.msg.pi .msg-who{color:#e8a090}.msg.user .msg-who{color:#7ec8e3}.msg-text{font-size:13px;line-height:1.6;color:#999}</style></head>
<body><div class="app"><div class="main"><div class="info" id="info">Turn 0</div><button class="mute" id="mute" onclick="mute()">🔊</button><div class="face" id="face"><div class="eyes"><div class="eye"></div><div class="eye"></div></div><div class="mouth"></div></div><div class="transcript" id="transcript"></div><div class="status" id="status">Ready</div></div><div class="sidebar"><div class="sidebar-head"><span class="sidebar-title">会話</span><button class="clear-btn" onclick="clear_()">クリア</button></div><div class="history" id="history"></div></div></div>
<script>let last=0;function mute(){fetch('/mute',{method:'POST'})}function clear_(){document.getElementById('history').innerHTML='';last=0;fetch('/clear',{method:'POST'})}function add(r,t){const h=document.getElementById('history'),d=document.createElement('div');d.className='msg '+r;d.innerHTML='<div class="msg-who">'+(r==='pi'?'Pi':'You')+'</div><div class="msg-text">'+t+'</div>';h.appendChild(d);h.scrollTop=h.scrollHeight}async function poll(){try{const r=await fetch('/state'),d=await r.json();let f='face '+d.status;if(d.muted)f='face muted';document.getElementById('face').className=f;document.getElementById('status').textContent=d.muted?'ミュート':{idle:'待機中',listening:'録音中...',thinking:'考え中',speaking:'話し中'}[d.status]||'';document.getElementById('transcript').textContent=d.transcript||'';document.getElementById('mute').textContent=d.muted?'🔇':'🔊';document.getElementById('mute').className=d.muted?'mute on':'mute';document.getElementById('info').textContent='Turn '+d.turn;if(d.history.length>last){for(let i=last;i<d.history.length;i++)add(d.history[i].role,d.history[i].text);last=d.history.length}}catch{}}setInterval(poll,100);</script></body></html>'''

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path=='/':
            self.send_response(200)
            self.send_header('Content-type','text/html;charset=utf-8')
            self.end_headers()
            self.wfile.write(HTML.encode())
        elif self.path=='/state':
            self.send_response(200)
            self.send_header('Content-type','application/json')
            self.end_headers()
            self.wfile.write(json.dumps(state).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        global conversation
        if self.path=='/mute':
            state['muted']=not state['muted']
            log(f"Muted: {state['muted']}")
        elif self.path=='/clear':
            conversation=[]
            state['history']=[]
            state['turn']=0
        self.send_response(200)
        self.end_headers()
    
    def log_message(self,*a):pass

def speak(text):
    state["status"]="speaking"
    subprocess.run(['say','-v','Kyoko','-r','280',text],capture_output=True)
    state["status"]="idle"

def record():
    """シンプル固定3秒録音"""
    if state.get('muted'):
        time.sleep(0.1)
        return None
    
    state["status"]="listening"
    state["transcript"]=""
    
    raw = tempfile.mktemp(suffix='.wav')
    trimmed = tempfile.mktemp(suffix='.wav')
    
    try:
        # 固定3秒録音（確実に音を拾う）
        subprocess.run([
            'rec', '-q', raw,
            'rate', '16000', 'channels', '1',
            'trim', '0', '3'
        ], timeout=5, capture_output=True)
        
        # 無音部分をトリム
        subprocess.run([
            'sox', raw, trimmed,
            'silence', '1', '0.05', '0.1%',
            'reverse',
            'silence', '1', '0.05', '0.1%',
            'reverse'
        ], timeout=3, capture_output=True)
        
        try: os.unlink(raw)
        except: pass
        
        if os.path.exists(trimmed):
            size = os.path.getsize(trimmed)
            if size > 1000:  # 1KB以上なら音声あり
                return trimmed
            try: os.unlink(trimmed)
            except: pass
        
        return None
        
    except Exception as e:
        log(f"Rec err: {e}")
        try: os.unlink(raw)
        except: pass
        try: os.unlink(trimmed)
        except: pass
        return None

def transcribe(path):
    if not OPENAI_API_KEY:
        return None
    
    state["transcript"]="..."
    
    try:
        with open(path,'rb') as f:
            data=f.read()
    except:
        return None
    
    b='----B'
    body=(f'--{b}\r\nContent-Disposition:form-data;name="file";filename="a.wav"\r\nContent-Type:audio/wav\r\n\r\n').encode()+data+(f'\r\n--{b}\r\nContent-Disposition:form-data;name="model"\r\n\r\nwhisper-1\r\n--{b}\r\nContent-Disposition:form-data;name="language"\r\n\r\nja\r\n--{b}--\r\n').encode()
    
    req=urllib.request.Request('https://api.openai.com/v1/audio/transcriptions',data=body,method='POST')
    req.add_header('Authorization',f'Bearer {OPENAI_API_KEY}')
    req.add_header('Content-Type',f'multipart/form-data;boundary={b}')
    
    try:
        with urllib.request.urlopen(req,timeout=15) as r:
            text=json.loads(r.read()).get('text','').strip()
            if len(text)<2:
                return None
            noise=['ご視聴','次回を','チャンネル','おしまい','ありがとうございます','良い一日','ご覧いただき','最後まで']
            if any(n in text for n in noise):
                return None
            state["transcript"]=text
            return text
    except:
        return None

def add_history(role, text):
    state['history'].append({'role': role, 'text': text})

def greeting():
    g="何でも話して！"
    add_history('pi', g)
    speak(g)

def main_loop():
    log("=== v7 Loop ===")
    greeting()
    
    while True:
        try:
            if state.get('muted'):
                state["status"]="idle"
                time.sleep(0.1)
                continue
            
            path = record()
            if not path:
                # 無音だった、すぐ次へ
                continue
            
            text = transcribe(path)
            try: os.unlink(path)
            except: pass
            
            if not text:
                continue
            
            state['turn'] += 1
            log(f"[T{state['turn']}] {text}")
            add_history('user', text)
            
            reply = chat(text)
            log(f"[T{state['turn']}] Pi: {reply[:50]}...")
            add_history('pi', reply)
            speak(reply)
            
        except Exception as e:
            log(f"Err: {e}")
            state["status"]="idle"
            time.sleep(0.3)

def main():
    log(f"=== Pi v7 === Port {PORT}")
    threading.Thread(target=main_loop, daemon=True).start()
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), Handler) as server:
        log("HTTP OK")
        server.serve_forever()

if __name__=="__main__":
    main()
