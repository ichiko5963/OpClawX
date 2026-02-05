#!/usr/bin/env python3
"""
Pi Voice - Obsidian連携版
- MEMORY.md + Obsidianプロジェクト情報を参照
- 右側チャットのみスクロール
- 左側は固定（文字表示なし）
- 即座に返答
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
from datetime import datetime
from pathlib import Path

OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')
PORT = 8765
WORKSPACE = "/Users/ai-driven-work/Library/Mobile Documents/com~apple~CloudDocs/OpenClaw-Shared"
OBSIDIAN = f"{WORKSPACE}/obsidian/Ichioka Obsidian"

state = {
    "status": "idle",
    "transcript": "",
    "history": [],
    "needGreeting": False
}

conversation_history = []
full_context = ""

def load_all_context():
    """MEMORY.md + Obsidianプロジェクト情報を読み込む"""
    global full_context
    parts = []
    
    # MEMORY.md
    mem_path = f"{WORKSPACE}/MEMORY.md"
    if os.path.exists(mem_path):
        with open(mem_path, 'r') as f:
            parts.append("## MEMORY.md\n" + f.read())
    
    # Today's memory
    today = datetime.now().strftime('%Y-%m-%d')
    today_path = f"{WORKSPACE}/memory/{today}.md"
    if os.path.exists(today_path):
        with open(today_path, 'r') as f:
            parts.append(f"## 今日のメモリ ({today})\n" + f.read())
    
    # Obsidian Active Projects
    active_projects = f"{OBSIDIAN}/03_Projects/_Active"
    if os.path.exists(active_projects):
        for proj in os.listdir(active_projects):
            proj_path = f"{active_projects}/{proj}"
            if os.path.isdir(proj_path):
                # Read project files
                for fname in ['README.md', 'OVERVIEW.md', 'PROJECT.md']:
                    fpath = f"{proj_path}/{fname}"
                    if os.path.exists(fpath):
                        with open(fpath, 'r') as f:
                            content = f.read()[:500]
                            parts.append(f"## Project: {proj}\n{content}")
                        break
    
    # ClimbBeyond specific
    cb_path = f"{OBSIDIAN}/03_Projects/_Active/ClimbBeyond"
    if os.path.exists(cb_path):
        for f in Path(cb_path).rglob('*.md'):
            try:
                with open(f, 'r') as file:
                    content = file.read()[:300]
                    parts.append(f"## ClimbBeyond/{f.name}\n{content}")
            except: pass
    
    # Genspark specific
    gs_path = f"{OBSIDIAN}/03_Projects/_Active/Genspark"
    if os.path.exists(gs_path):
        for f in Path(gs_path).rglob('*.md'):
            try:
                with open(f, 'r') as file:
                    content = file.read()[:300]
                    parts.append(f"## Genspark/{f.name}\n{content}")
            except: pass
    
    full_context = "\n\n".join(parts)[:6000]  # 6000文字まで
    print(f"📚 Context loaded: {len(full_context)} chars")

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>Pi</title>
    <style>
        *{margin:0;padding:0;box-sizing:border-box}
        html,body{height:100%;overflow:hidden}
        .app{display:grid;grid-template-columns:1fr 360px;height:100vh}
        .main{background:linear-gradient(160deg,#e8a090,#d4877a,#c97a6d);display:flex;flex-direction:column;align-items:center;justify-content:center;position:relative;overflow:hidden}
        .face{display:flex;flex-direction:column;align-items:center}
        .eyes{display:flex;gap:40px;margin-bottom:18px}
        .eye{width:60px;height:75px;background:#1a1a1a;border-radius:10px;transition:all .15s}
        .mouth{width:45px;height:22px;background:#1a1a1a;border-radius:6px;opacity:0;transition:all .15s}
        .face.idle .eye{animation:blink 4s infinite}
        @keyframes blink{0%,45%,55%,100%{transform:scaleY(1)}50%{transform:scaleY(.1)}}
        .face.listening .eye{height:22px;width:65px;border-radius:5px;animation:pulse .5s infinite}
        @keyframes pulse{0%,100%{opacity:1}50%{opacity:.3}}
        .face.speaking .eye{animation:sb .1s infinite alternate}
        .face.speaking .mouth{opacity:1;animation:talk .05s infinite alternate}
        @keyframes sb{0%{transform:scaleY(1)}100%{transform:scaleY(.65)}}
        @keyframes talk{0%{height:12px;width:34px}100%{height:40px;width:56px}}
        .face.thinking .eye{animation:think .4s infinite}
        .face.thinking .mouth{opacity:.6;width:28px;height:28px;border-radius:50%}
        @keyframes think{0%,100%{transform:translateX(0)}50%{transform:translateX(7px)}}
        .transcript{position:absolute;bottom:70px;font-size:22px;color:#1a1a1a;max-width:80%;text-align:center}
        .status{position:absolute;bottom:30px;padding:8px 18px;background:rgba(0,0,0,.1);border-radius:20px;font-size:12px;color:#1a1a1a;display:flex;align-items:center;gap:6px}
        .dot{width:6px;height:6px;background:#1a1a1a;border-radius:50%}
        .listening .dot{animation:dp .3s infinite}
        @keyframes dp{0%,100%{transform:scale(1)}50%{transform:scale(1.8);opacity:.2}}
        .mute{position:absolute;top:20px;right:20px;padding:8px 14px;background:rgba(0,0,0,.1);border:none;border-radius:16px;color:#1a1a1a;font-size:12px;cursor:pointer}
        .sidebar{background:#111;border-left:1px solid #222;display:flex;flex-direction:column;height:100vh;overflow:hidden}
        .sidebar-head{padding:16px 18px;border-bottom:1px solid #222;display:flex;justify-content:space-between;align-items:center;flex-shrink:0}
        .sidebar-title{font-size:10px;color:#666;text-transform:uppercase;letter-spacing:2px}
        .new-btn{padding:6px 10px;background:#222;border:1px solid #333;border-radius:5px;color:#888;font-size:10px;cursor:pointer}
        .history{flex:1;overflow-y:auto;padding:12px;-webkit-overflow-scrolling:touch}
        .history::-webkit-scrollbar{width:4px}
        .history::-webkit-scrollbar-thumb{background:#333;border-radius:2px}
        .msg{margin-bottom:10px;padding:10px;background:#1a1a1a;border-radius:8px;font-family:-apple-system,sans-serif}
        .msg.pi{border-left:2px solid #e8a090}
        .msg.user{border-left:2px solid #7ec8e3}
        .msg-head{display:flex;align-items:center;gap:5px;margin-bottom:5px}
        .msg-label{font-size:9px;font-weight:600;text-transform:uppercase}
        .msg.pi .msg-label{color:#e8a090}
        .msg.user .msg-label{color:#7ec8e3}
        .msg-text{font-size:12px;line-height:1.5;color:#aaa}
    </style>
</head>
<body>
    <div class="app">
        <div class="main">
            <button class="mute" id="mute" onclick="toggleMute()">🔊</button>
            <div class="face" id="face">
                <div class="eyes"><div class="eye"></div><div class="eye"></div></div>
                <div class="mouth"></div>
            </div>
            <div class="transcript" id="transcript"></div>
            <div class="status" id="status"><div class="dot"></div><span id="st">Ready</span></div>
        </div>
        <div class="sidebar">
            <div class="sidebar-head">
                <span class="sidebar-title">会話</span>
                <button class="new-btn" onclick="newChat()">+ New</button>
            </div>
            <div class="history" id="history"></div>
        </div>
    </div>
    <script>
        let muted=false,lastLen=0;
        function toggleMute(){muted=!muted;document.getElementById('mute').textContent=muted?'🔇':'🔊';fetch('/mute',{method:'POST',body:JSON.stringify({muted})})}
        function newChat(){document.getElementById('history').innerHTML='';lastLen=0;fetch('/new',{method:'POST'})}
        function addMsg(r,t){const h=document.getElementById('history'),d=document.createElement('div');d.className='msg '+r;d.innerHTML=`<div class="msg-head"><span>${r==='pi'?'🦞':'👤'}</span><span class="msg-label">${r==='pi'?'Pi':'You'}</span></div><div class="msg-text">${t}</div>`;h.appendChild(d);h.scrollTop=h.scrollHeight}
        async function poll(){try{const r=await fetch('/state'),d=await r.json();document.getElementById('face').className='face '+d.status;document.getElementById('status').className='status '+d.status;document.getElementById('st').textContent={idle:'Ready',listening:'Listening',thinking:'...',speaking:'Speaking'}[d.status]||'';document.getElementById('transcript').textContent=d.transcript||'';if(d.history.length>lastLen){for(let i=lastLen;i<d.history.length;i++)addMsg(d.history[i].role,d.history[i].text);lastLen=d.history.length}}catch{}}
        setInterval(poll,40);
    </script>
</body>
</html>
'''

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path=='/':
            self.send_response(200)
            self.send_header('Content-type','text/html;charset=utf-8')
            self.end_headers()
            self.wfile.write(HTML_TEMPLATE.encode())
        elif self.path=='/state':
            self.send_response(200)
            self.send_header('Content-type','application/json')
            self.end_headers()
            self.wfile.write(json.dumps(state).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        global conversation_history
        if self.path=='/mute':
            l=int(self.headers.get('Content-Length',0))
            d=json.loads(self.rfile.read(l))
            state['muted']=d.get('muted',False)
        elif self.path=='/new':
            conversation_history=[]
            state['history']=[]
            state['needGreeting']=True
        self.send_response(200)
        self.end_headers()
    
    def log_message(self,*a):pass

def speak(text):
    state["status"]="speaking"
    if not state.get('muted'):
        subprocess.run(['say','-v','Kyoko','-r','300',text])
    state["status"]="idle"

def record():
    state["status"]="listening"
    state["transcript"]=""
    p=tempfile.mktemp(suffix='.wav')
    try:
        subprocess.run(['rec','-q',p,'rate','16000','channels','1','silence','1','0.05','1%','1','0.6','1%','trim','0','5'],timeout=7,capture_output=True)
    except:pass
    if os.path.exists(p) and os.path.getsize(p)>400:
        return p
    return None

def transcribe(p):
    if not OPENAI_API_KEY:return None
    state["transcript"]="..."
    b='----B'
    with open(p,'rb') as f:data=f.read()
    body=(f'--{b}\r\nContent-Disposition:form-data;name="file";filename="a.wav"\r\nContent-Type:audio/wav\r\n\r\n').encode()+data+(f'\r\n--{b}\r\nContent-Disposition:form-data;name="model"\r\n\r\nwhisper-1\r\n--{b}\r\nContent-Disposition:form-data;name="language"\r\n\r\nja\r\n--{b}--\r\n').encode()
    req=urllib.request.Request('https://api.openai.com/v1/audio/transcriptions',data=body,method='POST')
    req.add_header('Authorization',f'Bearer {OPENAI_API_KEY}')
    req.add_header('Content-Type',f'multipart/form-data;boundary={b}')
    try:
        with urllib.request.urlopen(req,timeout=6) as r:
            t=json.loads(r.read()).get('text','')
            state["transcript"]=t
            return t
    except:return None

def chat(msg):
    global conversation_history
    state["status"]="thinking"
    state["transcript"]=""
    
    if not OPENAI_API_KEY:return "APIキーがないよ"
    
    conversation_history.append(f"User:{msg}")
    ctx="\n".join(conversation_history[-6:])
    
    system_prompt = f"""あなたはPi、いちさん専用のAIアシスタント。OpenClawで動いている。

# いちさんの情報（必ず参照）
{full_context[:4000]}

# 話し方
- カジュアル、敬語なし、短く（1-2文）
- いちさんのプロジェクトを把握している
- ClimbBeyond = 就活支援、ポート株式会社と連携
- Genspark = コンテンツ制作、2/12締め切り

# 会話
{ctx}"""

    body=json.dumps({
        "model":"gpt-4o-mini",
        "messages":[
            {"role":"system","content":system_prompt},
            {"role":"user","content":msg}
        ],
        "max_tokens":80,
        "temperature":0.7
    }).encode()
    
    req=urllib.request.Request('https://api.openai.com/v1/chat/completions',data=body,method='POST')
    req.add_header('Authorization',f'Bearer {OPENAI_API_KEY}')
    req.add_header('Content-Type','application/json')
    try:
        with urllib.request.urlopen(req,timeout=5) as r:
            reply=json.loads(r.read())['choices'][0]['message']['content']
            conversation_history.append(f"Pi:{reply}")
            return reply
    except:return "ん？"

def add_h(role,text):
    state['history'].append({'role':role,'text':text})

def greeting():
    h=time.localtime().tm_hour
    g="おはよう！" if h<12 else "やあ！" if h<18 else "こんばんは！"
    g+="何する？"
    add_h('pi',g)
    speak(g)

def loop():
    load_all_context()
    greeting()
    
    while True:
        try:
            if state.get('needGreeting'):
                state['needGreeting']=False
                load_all_context()
                greeting()
                continue
            
            p=record()
            if not p:
                state["status"]="idle"
                continue
            
            t=transcribe(p)
            try:os.unlink(p)
            except:pass
            
            if not t or len(t.strip())<2:
                state["status"]="idle"
                continue
            
            print(f"👤 {t}")
            add_h('user',t)
            
            if any(w in t for w in ['終了','バイバイ','おわり']):
                add_h('pi','またね！')
                speak('またね！')
                greeting()
                continue
            
            r=chat(t)
            print(f"🦞 {r}")
            add_h('pi',r)
            speak(r)
            
        except Exception as e:
            print(f"E:{e}")
            state["status"]="idle"
            time.sleep(0.1)

def main():
    print(f"🦞 http://localhost:{PORT}")
    subprocess.Popen(['open',f'http://localhost:{PORT}'])
    threading.Thread(target=loop,daemon=True).start()
    with socketserver.TCPServer(("",PORT),Handler) as h:
        h.serve_forever()

if __name__=="__main__":
    main()
