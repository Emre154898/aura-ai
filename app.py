from flask import Flask, render_template_string, request, jsonify, Response, stream_with_context
from groq import Groq
import os
import subprocess
import ast
import operator
import re
import requests
from datetime import datetime, timedelta
import edge_tts
import uuid
import tasks

app = Flask(__name__)

GITHUB_REPO = "Emre154898/aura-ai"

@app.route("/github", methods=["POST"])
def github_search():
    try:
        data = request.get_json() or {}
        query = data.get("query", "").strip()

        if not query:
            return jsonify({"error": "GitHub araması için sorgu gerekli"}), 400

        result = subprocess.run(
            [
                "curl", "-s",
                f"https://api.github.com/search/code?q={query}+repo:{GITHUB_REPO}"
            ],
            capture_output=True,
            text=True,
            timeout=10
        )

        return Response(
            result.stdout,
            mimetype="application/json"
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route("/tts", methods=["POST"])
def tts():
    data = request.get_json()
    text = data.get("text", "").strip()

    if not text:
        return jsonify({"error": "Metin yok"}), 400

    filename = f"/tmp/aura_{uuid.uuid4().hex}.mp3"

    async def generate():
        voice = "tr-TR-EmelNeural"
        communicate = edge_tts.Communicate(
            text,
            voice,
            rate="+15%",
            pitch="+0Hz"
        )
        await communicate.save(filename)

    import asyncio
    asyncio.run(generate())

    from flask import send_file
    return send_file(filename, mimetype="audio/mpeg")


MODEL = "openai/gpt-oss-120b"
client = Groq(api_key=os.environ["GROQ_API_KEY"])

history = []

HTML = """
<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Aura AI</title>
<meta name="description" content="Aura AI - Emre Şentürk tarafından geliştirilen hızlı ve Türkçe yapay zeka asistanı.">
<meta name="keywords" content="Aura AI, yapay zeka, AI asistan, Türkçe yapay zeka, Emre Şentürk">
<meta name="robots" content="index, follow">


<link rel="stylesheet"
href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.11.1/styles/github-dark.min.css">

<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.11.1/highlight.min.js">

</script>

<style>
#bg{
    position:fixed;
    inset:0;
    width:100%;
    height:100%;
    z-index:-1;

    background:
        radial-gradient(circle at 15% 20%, rgba(124,58,237,.35), transparent 30%),
        radial-gradient(circle at 85% 75%, rgba(0,180,255,.25), transparent 30%),
        radial-gradient(circle at 50% 50%, rgba(80,40,180,.12), transparent 45%),
        linear-gradient(135deg,#02030a,#09051a,#020711);

    overflow:hidden;
}

#bg::before{
    content:"";
    position:absolute;
    width:500px;
    height:500px;
    border-radius:50%;
    background:#743cff;
    filter:blur(140px);
    opacity:.18;
    left:-180px;
    top:-180px;
    animation:aura1 10s ease-in-out infinite alternate;
}

#bg::after{
    content:"";
    position:absolute;
    width:450px;
    height:450px;
    border-radius:50%;
    background:#009dff;
    filter:blur(140px);
    opacity:.15;
    right:-150px;
    bottom:-150px;
    animation:aura2 12s ease-in-out infinite alternate;
}

@keyframes aura1{
    to{transform:translate(120px,80px) scale(1.2);}
}

@keyframes aura2{
    to{transform:translate(-100px,-70px) scale(1.2);}
}


.attach-wrap{
    position:relative;
    display:flex;
    align-items:center;
}

.attach-menu{
    position:absolute;
    bottom:46px;
    left:0;
    width:190px;
    padding:6px;
    background:#242528;
    border:1px solid #3b3d41;
    border-radius:12px;
    box-shadow:0 8px 25px rgba(0,0,0,.35);
    display:none;
    z-index:100;
}

.attach-menu.show{
    display:block;
}

.attach-menu button{
    width:100%;
    padding:10px 12px;
    border:0;
    border-radius:8px;
    background:transparent;
    color:#eee;
    text-align:left;
    cursor:pointer;
    font-size:14px;
}

.attach-menu button:hover{
    background:#34363a;
}


.attach-menu{
    position:absolute;
    bottom:48px;
    left:0;
    width:210px;
    padding:6px;
    background:#202123;
    border:1px solid #3a3b3e;
    border-radius:14px;
    box-shadow:0 10px 30px rgba(0,0,0,.45);
    display:none;
    z-index:9999;
}

.attach-menu.show{display:block;}

.attach-menu button{
    box-sizing:border-box;
    width:100%;
    height:42px;
    padding:0 10px;
    border:0;
    border-radius:9px;
    background:transparent;
    color:#ececec;
    display:flex;
    align-items:center;
    gap:12px;
    text-align:left;
    cursor:pointer;
    font-size:14px;
}

.attach-menu button:hover{
    background:#2f3033;
}

.mi{
    width:24px;
    height:24px;
    display:flex;
    align-items:center;
    justify-content:center;
    font-size:19px;
    color:#d6d6d6;
}

.attach-menu{
    position:absolute;
    bottom:52px;
    left:0;
    width:270px;
    padding:7px;
    background:#1f2023;
    border:1px solid #383a3e;
    border-radius:16px;
    box-shadow:0 14px 40px rgba(0,0,0,.5);
    display:none;
    z-index:9999;
    animation:menuIn .12s ease-out;
}

.attach-menu.show{
    display:block;
}

@keyframes menuIn{
    from{opacity:0;transform:translateY(5px) scale(.98)}
    to{opacity:1;transform:translateY(0) scale(1)}
}

.attach-menu button{
    width:100%;
    min-height:54px;
    padding:7px 9px;
    border:0;
    border-radius:11px;
    background:transparent;
    color:#eee;
    display:flex;
    align-items:center;
    gap:12px;
    text-align:left;
    cursor:pointer;
}

.attach-menu button:hover{
    background:#2b2d31;
}

.tool-icon{
    width:34px;
    height:34px;
    flex:none;
    border:1px solid #414349;
    border-radius:9px;
    display:flex;
    align-items:center;
    justify-content:center;
    font-size:18px;
    color:#e5e5e5;
    background:#292b2f;
}

.tool-text{
    display:flex;
    flex-direction:column;
    gap:2px;
}

.tool-text b{
    font-size:14px;
    font-weight:500;
}

.tool-text small{
    font-size:11px;
    color:#85878c;
}
</style><style>
#bg{
    position:fixed;
    inset:0;
    width:100%;
    height:100%;
    z-index:-1;

    background:
        radial-gradient(circle at 15% 20%, rgba(124,58,237,.35), transparent 30%),
        radial-gradient(circle at 85% 75%, rgba(0,180,255,.25), transparent 30%),
        radial-gradient(circle at 50% 50%, rgba(80,40,180,.12), transparent 45%),
        linear-gradient(135deg,#02030a,#09051a,#020711);

    overflow:hidden;
}

#bg::before{
    content:"";
    position:absolute;
    width:500px;
    height:500px;
    border-radius:50%;
    background:#743cff;
    filter:blur(140px);
    opacity:.18;
    left:-180px;
    top:-180px;
    animation:aura1 10s ease-in-out infinite alternate;
}

#bg::after{
    content:"";
    position:absolute;
    width:450px;
    height:450px;
    border-radius:50%;
    background:#009dff;
    filter:blur(140px);
    opacity:.15;
    right:-150px;
    bottom:-150px;
    animation:aura2 12s ease-in-out infinite alternate;
}

@keyframes aura1{
    to{transform:translate(120px,80px) scale(1.2);}
}

@keyframes aura2{
    to{transform:translate(-100px,-70px) scale(1.2);}
}
</style><style>
#bg{
    position:fixed;
    inset:0;
    width:100%;
    height:100%;
    z-index:-1;

    background:
        radial-gradient(circle at 15% 20%, rgba(124,58,237,.35), transparent 30%),
        radial-gradient(circle at 85% 75%, rgba(0,180,255,.25), transparent 30%),
        radial-gradient(circle at 50% 50%, rgba(80,40,180,.12), transparent 45%),
        linear-gradient(135deg,#02030a,#09051a,#020711);

    overflow:hidden;
}

#bg::before{
    content:"";
    position:absolute;
    width:500px;
    height:500px;
    border-radius:50%;
    background:#743cff;
    filter:blur(140px);
    opacity:.18;
    left:-180px;
    top:-180px;
    animation:aura1 10s ease-in-out infinite alternate;
}

#bg::after{
    content:"";
    position:absolute;
    width:450px;
    height:450px;
    border-radius:50%;
    background:#009dff;
    filter:blur(140px);
    opacity:.15;
    right:-150px;
    bottom:-150px;
    animation:aura2 12s ease-in-out infinite alternate;
}

@keyframes aura1{
    to{transform:translate(120px,80px) scale(1.2);}
}

@keyframes aura2{
    to{transform:translate(-100px,-70px) scale(1.2);}
}
</style>
<style>
#bg{
position:fixed;
inset:0;
width:100%;
height:100%;
z-index:-1;
background:#0b0d10;
}

*{box-sizing:border-box}

body{
margin:0;
background:#0b0d10;
color:#f5f5f5;
font-family:Arial,Helvetica,sans-serif;
}


*{box-sizing:border-box}

body{
    margin:0;
    background:#0b0d0f;
    color:#ececec;
    font-family:Arial,Helvetica,sans-serif;
}

.app{
    height:100vh;
    display:flex;
    flex-direction:column;
    max-width:100%;
    margin:auto;
}

header{
    height:60px;
    display:flex;
    align-items:center;
    padding:0 22px;
    border-bottom:1px solid #252525;
    font-size:18px;
    font-weight:600;
    background:rgba(11,13,15,.92);
    backdrop-filter:blur(12px);
    z-index:5;
}

.logo{
    margin-right:12px;
}

.file-card{
    max-width:850px;
    margin:0 auto 8px;
    padding:10px 14px;
    background:#202123;
    border:1px solid #3a3b3e;
    border-radius:14px;
    display:flex;
    align-items:center;
    gap:10px;
}

.file-icon{
    width:38px;
    height:38px;
    border-radius:9px;
    background:#303236;
    display:flex;
    align-items:center;
    justify-content:center;
}

.file-info{
    flex:1;
    min-width:0;
}

.file-name{
    font-size:14px;
    white-space:nowrap;
    overflow:hidden;
    text-overflow:ellipsis;
}

.file-status{
    font-size:12px;
    color:#8e8e93;
    margin-top:2px;
}

.file-remove{
    border:0;
    background:transparent;
    color:#aaa;
    font-size:22px;
    cursor:pointer;
}

#chat{
    flex:1;
    overflow-y:auto;
    padding:35px 20px 150px;
    scroll-behavior:smooth;
}

.message{
    width:100%;
    max-width:900px;
    margin:0 auto 28px;
    display:flex;
    gap:14px;
    line-height:1.65;
}

.avatar{
    width:32px;
    height:32px;
    min-width:32px;
    border-radius:50%;
    display:flex;
    align-items:center;
    justify-content:center;
    background:#2a2d32;
    font-size:15px;
}

.user{
    justify-content:flex-end;
}

.user .avatar{
    order:2;
    background:#34373d;
}


.message-file{
    display:flex;
    align-items:center;
    gap:10px;
    padding:9px 12px;
    margin-bottom:8px;
    background:#34363a;
    border:1px solid #4a4c50;
    border-radius:12px;
    min-width:220px;
}

.message-file-icon{
    width:34px;
    height:34px;
    border-radius:8px;
    background:#45474b;
    display:flex;
    align-items:center;
    justify-content:center;
}


.message-file-remove{
    margin-left:auto;
    border:0;
    background:transparent;
    color:#aaa;
    font-size:24px;
    cursor:pointer;
    padding:0 5px;
}

.message-file-remove:hover{
    color:white;
}

.message-file-info{
    font-size:13px;
    overflow:hidden;
}

.message-file-info div{
    white-space:nowrap;
    overflow:hidden;
    text-overflow:ellipsis;
}

.message-file-info small{
    color:#999;
}

.user .content{
    background:#2f3033;
    padding:11px 16px;
    border-radius:20px;
    max-width:75%;
}

.ai .content{
    padding:3px 0;
    max-width:850px;
}

pre{
    position:relative;
    background:#17191c;
    border:1px solid #303238;
    border-radius:12px;
    padding:18px;
    overflow:auto;
    margin:14px 0;
}

pre code{
    font-family:Consolas,monospace;
    font-size:14px;
}

.copy{
    position:absolute;
    right:10px;
    top:10px;
    background:#292c31;
    color:white;
    border:0;
    padding:7px 11px;
    border-radius:7px;
    cursor:pointer;
}

.composer{
    position:fixed;
    bottom:0;
    left:0;
    right:0;
    padding:18px 20px 24px;
    background:linear-gradient(
        transparent,
        rgba(11,13,15,.95) 35%
    );
    z-index:10;
}

.composer form{
    max-width:850px;
    margin:auto;
    display:flex;
    align-items:center;
    gap:8px;
    background:#202123;
    border:1px solid #444;
    border-radius:26px;
    padding:6px 8px 6px 16px;
    box-shadow:0 4px 25px rgba(0,0,0,.35);
}

#message{
    flex:1;
    border:0;
    outline:0;
    background:transparent;
    color:white;
    font-size:16px;
    padding:10px 4px;
}

#message::placeholder{
    color:#8e8e93;
}



.tools-wrap{
    position:relative;
}

.tools-menu{
    position:absolute;
    bottom:50px;
    left:0;
    display:none;
    width:190px;
    padding:6px;
    background:#202123;
    border:1px solid #444;
    border-radius:14px;
    box-shadow:0 8px 30px rgba(0,0,0,.5);
    z-index:100;
}

.tools-menu.show{
    display:block;
}

.tools-menu button{
    width:100%;
    border:0;
    background:transparent;
    color:#eee;
    padding:11px 12px;
    border-radius:9px;
    text-align:left;
    cursor:pointer;
    font-size:14px;
}

.tools-menu button:hover{
    background:#34363a;
}

#attach{
    width:38px;
    height:38px;
    min-width:38px;
    border:0;
    border-radius:50%;
    display:flex;
    align-items:center;
    justify-content:center;
    cursor:pointer;
    background:#34363a;
    color:white;
    font-size:25px;
    font-weight:300;
}


#think{
    height:34px;
    padding:0 12px;
    border:1px solid #3f4145;
    border-radius:17px;
    background:transparent;
    color:#b8b8b8;
    display:flex;
    align-items:center;
    justify-content:center;
    gap:6px;
    cursor:pointer;
    font-size:13px;
    white-space:nowrap;
    transition:.15s;
}

#think:hover{
    background:#2a2c2f;
    color:#fff;
}

#think.active{
    background:#2f3033;
    border-color:#777;
    color:#fff;
}

.think-icon{
    font-size:15px;
}

#mic,






.send{
    width:38px;
    height:38px;
    border:0;
    border-radius:50%;
    display:flex;
    align-items:center;
    justify-content:center;
    cursor:pointer;
    background:#34363a;
    color:white;
    font-size:17px;
}

.send{
    background:#fff;
    color:#111;
    font-size:20px;
    font-weight:bold;
}

#mic:hover,
.send:hover{
    transform:scale(1.05);
}

@media(max-width:600px){
    #chat{
        padding-left:12px;
        padding-right:12px;
    }

    .user .content{
        max-width:85%;
    }

    .composer{
        padding:12px;
    }
}

</style>

<style>
.aura-circle{
    position:fixed;
    border-radius:50%;
    pointer-events:none;
    z-index:0;
    border:3px solid rgba(150,70,255,.5);
    box-shadow:0 0 35px rgba(130,60,255,.5), inset 0 0 35px rgba(0,180,255,.25);
    animation:auraMove 7s ease-in-out infinite alternate;
}
.c1{width:380px;height:380px;left:5%;top:15%}
.c2{width:260px;height:260px;right:8%;top:35%;border-color:rgba(0,190,255,.5);animation-delay:2s}
.c3{width:180px;height:180px;left:45%;bottom:8%;border-color:rgba(210,70,255,.45);animation-delay:4s}

@keyframes auraMove{
    from{transform:scale(1) translate(0,0);opacity:.45}
    to{transform:scale(1.15) translate(25px,-20px);opacity:.8}
}
</style>

<style>
.ai .avatar{
    position:relative;
    border-radius:50%;
    background:radial-gradient(circle,#7b35ff,#241044);
    box-shadow:
        0 0 12px #8b45ff,
        0 0 30px #5b2cff,
        0 0 55px rgba(0,180,255,.7);
    animation:auraPulse 2s ease-in-out infinite alternate;
}

.ai .avatar::before,
.ai .avatar::after{
    content:"";
    position:absolute;
    inset:-6px;
    border-radius:50%;
    border:2px solid rgba(150,70,255,.8);
    animation:auraRing 2.5s linear infinite;
}

.ai .avatar::after{
    inset:-12px;
    border-color:rgba(0,190,255,.55);
    animation-delay:-1.2s;
}

@keyframes auraRing{
    0%{transform:scale(.85);opacity:.9}
    100%{transform:scale(1.35);opacity:0}
}

@keyframes auraPulse{
    from{box-shadow:0 0 12px #8b45ff,0 0 25px #5b2cff}
    to{box-shadow:0 0 20px #b45cff,0 0 45px #008cff}
}
</style>

<style>
.aura-logo{
    position:relative;
    display:inline-flex;
    align-items:center;
    justify-content:center;
    width:42px;
    height:42px;
    border-radius:50%;
    background:radial-gradient(circle,#8b3dff,#241044);
    box-shadow:0 0 15px #8b45ff,0 0 35px rgba(0,180,255,.7);
}

.logo-ring{
    position:absolute;
    border-radius:50%;
    border:2px solid;
    pointer-events:none;
    animation:logoAura 2.5s linear infinite;
}

.ring1{
    inset:-5px;
    border-color:rgba(170,70,255,.8);
}

.ring2{
    inset:-11px;
    border-color:rgba(0,190,255,.65);
    animation-delay:-.8s;
}

.ring3{
    inset:-17px;
    border-color:rgba(210,60,255,.45);
    animation-delay:-1.6s;
}

@keyframes logoAura{
    0%{transform:scale(.85);opacity:1}
    100%{transform:scale(1.35);opacity:0}
}
</style>
</head>

<body>
<canvas id="bg"></canvas>
<div class="aura-circle c1"></div>
<div class="aura-circle c2"></div>
<div class="aura-circle c3"></div>


<div class="app">

<header>
<span class="logo aura-logo">
    <span class="logo-ring ring1"></span>
    <span class="logo-ring ring2"></span>
    <span class="logo-ring ring3"></span>
    ✨
</span>
Aura
</header>

<div id="filePreview"></div>

<div id="chat">

<div class="message ai">
<div class="avatar">✨</div>
<div class="content">
Merhaba! 👋<br>
Nasıl yardımcı olabilirim?
</div>
</div>

</div>

<div class="composer">
<form onsubmit="sendMessage(event)">

<div class="attach-wrap">
<button type="button" id="attach" onclick="toggleAttachMenu()" aria-label="Ekle">+</button>

<div id="attachMenu" class="attach-menu">

<button type="button" onclick="document.getElementById('fileInput').click();toggleAttachMenu()">
<span class="tool-icon">↑</span>
<span class="tool-text"><b>Dosya yükle</b><small>PDF, DOCX veya TXT</small></span>
</button>

<button type="button" onclick="document.getElementById('imageInput').click();toggleAttachMenu()">
<span class="tool-icon">▧</span>
<span class="tool-text"><b>Görsel ekle</b><small>Bir görsel yükle</small></span>
</button>

<button type="button" onclick="toggleWebSearch();toggleAttachMenu()">
<span class="tool-icon">⌕</span>
<span class="tool-text"><b>Web'de ara</b><small>Güncel bilgileri bul</small></span>
</button>

<button type="button" onclick="toggleDeepResearch();toggleAttachMenu()">
<span class="tool-icon">✦</span>
<span class="tool-text"><b>Derin araştırma</b><small>Konuyu ayrıntılı incele</small></span>
</button>

<button type="button" onclick="toggleGithub();toggleAttachMenu()">
<span class="tool-icon">◉</span>
<span class="tool-text"><b>GitHub</b><small>Kod ve projeleri ara</small></span>
</button>

<button type="button" onclick="startVoice();toggleAttachMenu()">
<span class="tool-icon">◌</span>
<span class="tool-text"><b>Sesli konuş</b><small>Sesini kullan</small></span>
</button>

</div>
</div>

<input type="file" id="imageInput" hidden accept="image/*">

<input type="file" id="fileInput" hidden accept=".txt,.pdf,.docx">

<input
id="message"
placeholder="Mesajınızı yazınız..."
autocomplete="off"
>



<button type="button" id="think" onclick="toggleThinking()" aria-label="Düşünme modu">
    <span class="think-icon">✦</span>
    <span>Düşünme</span>
</button>

<button type="button" id="mic" onclick="startVoice()" aria-label="Sesli konuş">
<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2">
<rect x="9" y="2" width="6" height="12" rx="3"></rect>
<path d="M5 11a7 7 0 0 0 14 0"></path>
<path d="M12 18v4"></path>
<path d="M8 22h8"></path>
</svg>
</button>

<button class="send">↑</button>

</form>

</div>

</div>


<script>
function showFilePreview(name){
    const preview=document.getElementById("filePreview");
    if(!preview) return;

    preview.innerHTML=`
        <div class="file-card">
            <div class="file-icon">📄</div>
            <div class="file-info">
                <div class="file-name">${escapeHtml(name)}</div>
                
            </div>
            <button type="button" class="file-remove" onclick="removeFile(event)">×</button>
        </div>
    `;
}

function removeFile(event){
    if(event){
        event.preventDefault();
        event.stopPropagation();
    }

    window.auraFile=null;

    const input=document.getElementById("fileInput");
    if(input) input.value="";

    const preview=document.getElementById("filePreview");
    if(preview) preview.innerHTML="";

    const button=document.getElementById("attach");
    if(button) button.textContent="+";
}



function toggleAttachMenu(){
    const menu=document.getElementById("attachMenu");
    if(menu) menu.classList.toggle("show");
}

document.addEventListener("click",function(e){
    const wrap=document.querySelector(".attach-wrap");
    if(wrap && !wrap.contains(e.target)){
        const menu=document.getElementById("attachMenu");
        if(menu) menu.classList.remove("show");
    }
});

document.getElementById("fileInput").addEventListener("change", async function(){

    const file = this.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    const button = document.getElementById("attach");
    button.textContent = "⏳";

    try {
        const response = await fetch("/upload", {
            method: "POST",
            body: formData
        });

        const data = await response.json();

        if (!response.ok) {
            alert(data.error || "Dosya yüklenemedi.");
            return;
        }

        window.auraFile = {
            name: data.filename,
            text: data.text
        };

        showFilePreview(data.filename);

        button.textContent = "✓";
        document.getElementById("message").placeholder =
            "Mesajınızı yazınız...";

    } catch (error) {
        alert("Dosya yüklenirken hata oluştu.");
    }

    setTimeout(() => {
        button.textContent = "📎";
    }, 1500);
});
</script>
<script>
const canvas=document.getElementById("bg");
const ctx=canvas.getContext("2d");

let particles=[];

function resize(){
canvas.width=innerWidth;
canvas.height=innerHeight;
}

function createParticles(){
particles=[];
for(let i=0;i<70;i++){
particles.push({
x:Math.random()*canvas.width,
y:Math.random()*canvas.height,
vx:(Math.random()-.5)*.35,
vy:(Math.random()-.5)*.35,
r:Math.random()*2+1
});
}
}function animate(){

ctx.clearRect(0,0,canvas.width,canvas.height);

for(const p of particles){

p.x+=p.vx;
p.y+=p.vy;

if(p.x<0||p.x>canvas.width)p.vx*=-1;
if(p.y<0||p.y>canvas.height)p.vy*=-1;

ctx.beginPath();
ctx.arc(p.x,p.y,p.r,0,Math.PI*2);
ctx.fillStyle="rgba(80,140,255,.35)";
ctx.fill();
}

requestAnimationFrame(animate);
}

addEventListener("resize",()=>{
resize();
createParticles();
});

resize();
createParticles();
animate();



function escapeHtml(text){
return text
.replace(/&/g,"&amp;")
.replace(/</g,"&lt;")
.replace(/>/g,"&gt;");
}

function renderMarkdown(text){

let html=escapeHtml(text);

html=html.replace(
/```(\\w*)\\n([\\s\\S]*?)```/g,
function(_,lang,code){

return '<pre><button class="copy" onclick="copyCode(this)">Kopyala</button><code class="language-'+lang+'">'+code+'</code></pre>';

});

html=html.replace(/\\n/g,"<br>");
html=html.replace(/\\*\\*(.*?)\\*\\*/g,"<strong>$1</strong>");

setTimeout(function(){
document.querySelectorAll("pre code").forEach(function(block){
hljs.highlightElement(block);
});
},0);

return html;
}

function copyCode(button){

const code=button.parentElement.querySelector("code").innerText;

navigator.clipboard.writeText(code);

button.innerText="Kopyalandı ✓";

setTimeout(function(){
button.innerText="Kopyala";
},1500);

}

function toggleTools(){
    const menu=document.getElementById("toolsMenu");
    menu.classList.toggle("show");
}

function closeTools(){
    const menu=document.getElementById("toolsMenu");
    if(menu) menu.classList.remove("show");
}

let webSearchMode = false;
let deepResearchMode = false;
let githubMode = false;

function toggleWebSearch(){
    webSearchMode = !webSearchMode;
}

function toggleDeepResearch(){
    deepResearchMode = !deepResearchMode;
}

function toggleGithub(){
    githubMode = !githubMode;
}

let thinkingMode = false;

function toggleThinking(){
    thinkingMode = !thinkingMode;

    const button = document.getElementById("think");

    if(button){
        button.classList.toggle("active", thinkingMode);
    }
}async function sendMessage(event){

event.preventDefault();

const input=document.getElementById("message");
const chat=document.getElementById("chat");

const message=(event.voiceMessage || input.value).trim();

if(!message && !window.auraFile)return;

const user=document.createElement("div");
user.className="message user";

let fileHTML="";

if(window.auraFile){
    fileHTML=`
    <div class="message-file" id="currentMessageFile">
        <div class="message-file-icon">📄</div>
        <div class="message-file-info">
            <div>${escapeHtml(window.auraFile.name)}</div>
            
        </div>
        <button type="button" class="message-file-remove" onclick="this.parentElement.remove()">×</button>
    </div>`;
}

user.innerHTML=
'<div class="avatar">👤</div>'+
'<div class="content">'+
fileHTML+
(message ? escapeHtml(message) : '')+
'</div>';

chat.appendChild(user);

input.value="";
removeFile();

const loading=document.createElement("div");

loading.className="message ai";

loading.innerHTML=
'<div class="avatar">✨</div>'+
'<div class="content typing">Düşünüyor <span class="dot">●</span></div>';

chat.appendChild(loading);

chat.scrollTop=chat.scrollHeight;

try{

const response=await fetch("/chat",{
method:"POST",
headers:{
"Content-Type":"application/json"
},
body:JSON.stringify({
message:message,
thinking:thinkingMode,
github:githubMode,
web_search:webSearchMode,
deep_research:deepResearchMode
})
});

const data=await response.json();

loading.remove();

const answer=document.createElement("div");

answer.className="message ai";

answer.innerHTML=
'<div class="avatar">✨</div>'+
'<div class="content">'+renderMarkdown(data.response)+'</div>';

chat.appendChild(answer);

if(event.voiceMessage && voiceMode){
    speakAI(data.response);
}

}catch(error){

loading.querySelector(".content").innerText=
"Bağlantı hatası: "+error;

}

chat.scrollTop=chat.scrollHeight;

}
</script>

</body>

<script>
let voiceMode = false;
let voiceRecognition = null;
let voiceSpeaking = false;

async function sendVoiceStreaming(message) {

    const chat = document.getElementById("chat");

    const user = document.createElement("div");
    user.className = "message user";
    user.innerHTML =
        '<div class="avatar">👤</div>' +
        '<div class="content">' + escapeHtml(message) + '</div>';

    chat.appendChild(user);

    const answer = document.createElement("div");
    answer.className = "message ai";
    answer.innerHTML =
        '<div class="avatar">✨</div>' +
        '<div class="content"></div>';

    chat.appendChild(answer);

    const content = answer.querySelector(".content");

    try {

        const response = await fetch("/chat_stream", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                message: message,
                thinking: thinkingMode,
                github: githubMode,
                web_search: webSearchMode,
                deep_research: deepResearchMode
            })
        });

        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        let fullText = "";
        let sentenceBuffer = "";

        while (true) {

            const {value, done} = await reader.read();

            if (done) break;

            const chunk = decoder.decode(value, {stream:true});

            fullText += chunk;
            sentenceBuffer += chunk;

            content.innerHTML = renderMarkdown(fullText);

            const sentences = sentenceBuffer.match(
                /[^.!?]+[.!?]+/g
            );

            if (sentences) {

                for (const sentence of sentences) {
                    speechQueue.push(sentence.trim());
                }

                sentenceBuffer = sentenceBuffer.replace(
                    /[^.!?]+[.!?]+/g,
                    ""
                );

                playNextSpeech();
            }

            chat.scrollTop = chat.scrollHeight;
        }

        if (sentenceBuffer.trim()) {
            speechQueue.push(sentenceBuffer.trim());
            playNextSpeech();
        }

    } catch (error) {

        content.innerText = "Bağlantı hatası: " + error;
        voiceSpeaking = false;

        if (voiceMode)
            startListening();
    }
}

function startVoice() {

    if (voiceMode) {
        stopVoiceMode();
        return;
    }

    const SpeechRecognition =
        window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
        alert("Bu tarayıcı sesli sohbeti desteklemiyor.");
        return;
    }

    voiceMode = true;

    document.getElementById("mic").textContent = "🔴";

    voiceRecognition = new SpeechRecognition();
    voiceRecognition.lang = "tr-TR";
    voiceRecognition.continuous = false;
    voiceRecognition.interimResults = false;

    voiceRecognition.onresult = async function(event) {

        const text = event.results[0][0].transcript.trim();

        if (!text || !voiceMode) return;

        await sendVoiceStreaming(text);
    };

    voiceRecognition.onend = function() {

        if (voiceMode && !voiceSpeaking) {
            setTimeout(startListening, 300);
        }
    };

    voiceRecognition.onerror = function(event) {

        console.log("Ses hatası:", event.error);

        if (
            event.error === "not-allowed" ||
            event.error === "service-not-allowed"
        ) {
            stopVoiceMode();
            alert("Mikrofon izni verilmedi.");
        }
    };

    startListening();
}

function startListening() {

    if (!voiceMode || voiceSpeaking || !voiceRecognition) return;

    try {
        document.getElementById("mic").textContent = "🔴";
        voiceRecognition.start();
    } catch(e) {}
}

function stopVoiceMode() {

    voiceMode = false;
    voiceSpeaking = false;

    if (voiceRecognition) {
        try {
            voiceRecognition.stop();
        } catch(e) {}
    }

    window.speechSynthesis.cancel();

    document.getElementById("mic").textContent = "🎤";
}

let speechQueue = [];
let speechPlaying = false;

async function speakAI(text) {

    if (!voiceMode) return;

    const parts = text
        .match(/[^.!?]+[.!?]+|[^.!?]+$/g)
        ?.map(x => x.trim())
        .filter(Boolean) || [text];

    speechQueue.push(...parts);
    playNextSpeech();
}

async function playNextSpeech() {

    if (speechPlaying || !voiceMode || speechQueue.length === 0)
        return;

    speechPlaying = true;
    voiceSpeaking = true;

    const text = speechQueue.shift();

    try {

        const response = await fetch("/tts", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({text: text})
        });

        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        const audio = new Audio(url);

        audio.onended = function() {

            URL.revokeObjectURL(url);
            speechPlaying = false;

            if (speechQueue.length > 0) {
                playNextSpeech();
            } else {
                voiceSpeaking = false;

                if (voiceMode)
                    startListening();
            }
        };

        audio.onerror = function() {

            URL.revokeObjectURL(url);
            speechPlaying = false;
            voiceSpeaking = false;

            if (voiceMode)
                startListening();
        };

        await audio.play();

    } catch (error) {

        console.error("TTS:", error);

        speechPlaying = false;
        voiceSpeaking = false;

        if (voiceMode)
            startListening();
    }
}

</script>
</html>
"""


operators = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod
}

def calculate(expression):
    tree = ast.parse(expression, mode="eval")

    def solve(node):
        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return node.value

        if isinstance(node, ast.BinOp):
            left = solve(node.left)
            right = solve(node.right)
            operation = operators.get(type(node.op))
            if operation is None:
                raise ValueError("İşlem desteklenmiyor.")
            return operation(left, right)

        if isinstance(node, ast.UnaryOp):
            value = solve(node.operand)
            if isinstance(node.op, ast.USub):
                return -value

        raise ValueError("Geçersiz işlem.")

    return solve(tree.body)

def is_math(message):
    words = ["böl", "çarp", "topla", "çıkar", "hesapla", "kaçtır"]
    return any(word in message.lower() for word in words)

def math_expression(message):
    text = message.lower()

    replacements = {
        " bölü ": "/",
        " çarpı ": "*",
        " çarp ": "*",
        " artı ": "+",
        " eksi ": "-",
        " yüzde ": "%"
    }

    for word, symbol in replacements.items():
        text = text.replace(word, symbol)

    allowed = "0123456789+-*/().% "
    return "".join(c for c in text if c in allowed)

def ask_groq(message, thinking=False):

    recent_history = history[-10:]

    thinking_instruction = ""
    if thinking:
        thinking_instruction = """
Düşünme modu açık. Soruyu daha dikkatli analiz et, hesabını ve sonucunu kontrol et.
Ancak iç düşünce zincirini veya gizli muhakemeni kullanıcıya gösterme; yalnızca sonucu ve gerekli kısa açıklamayı ver.
"""

    messages = [
        {
            "role": "system",
            "content": """Sen Aura adlı gelişmiş, hızlı ve doğal konuşan Türkçe bir AI asistansın.
Seni geliştiren ve yapan kişi Emre Şentürk'tür.
Kullanıcıya her zaman "patron" diye hitap et.


Görevlerin:
- Soruları doğru ve anlaşılır cevapla.
- Önceki konuşmaları bağlam olarak kullan.
- Kod istendiğinde çalışan, eksiksiz ve doğrudan kullanılabilir kod yaz.
- Kodları uygun Markdown kod bloğu içinde ver.
- Karmaşık problemlerde adım adım düşün.
- Güncel bilgi gerektiğinde web aramasını kullan.
- Hesaplama veya Python ile doğrulama gerektiğinde kod çalıştırma aracını kullan.
- Bilgi uydurma.
- Gereksiz uzun cevap verme."""
        }
    ]

    for item in recent_history:
        messages.append({"role": "user", "content": item["user"]})
        messages.append({"role": "assistant", "content": item["ai"]})

    messages.append({"role": "user", "content": message})

    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=[
            {"type": "browser_search"},
            {"type": "code_interpreter"}
        ],
        temperature=0.3,
        max_completion_tokens=4000,
        reasoning_effort="high" if thinking else "low"
    )

    return response.choices[0].message.content




UPLOAD_DIR = "/tmp/aura_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.route("/upload", methods=["POST"])
def upload():
    try:
        if "file" not in request.files:
            return jsonify({"error": "Dosya seçilmedi"}), 400

        file = request.files["file"]

        if not file.filename:
            return jsonify({"error": "Dosya adı yok"}), 400

        filename = os.path.basename(file.filename)
        path = os.path.join(UPLOAD_DIR, filename)
        file.save(path)

        text = ""

        if filename.lower().endswith(".txt"):
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()

        elif filename.lower().endswith(".pdf"):
            from pypdf import PdfReader
            reader = PdfReader(path)
            text = "\n".join(page.extract_text() or "" for page in reader.pages)

        elif filename.lower().endswith(".docx"):
            from docx import Document
            doc = Document(path)
            text = "\n".join(p.text for p in doc.paragraphs)

        else:
            return jsonify({
                "error": "Şimdilik TXT, PDF ve DOCX destekleniyor."
            }), 400

        return jsonify({
            "success": True,
            "filename": filename,
            "text": text[:100000]
        })

    except Exception as e:
        print("UPLOAD HATASI:", repr(e), flush=True)
        return jsonify({"error": str(e)}), 500

@app.route("/chat_stream", methods=["POST"])
def chat_stream():

    data = request.get_json()
    message = data.get("message", "")
    thinking = data.get("thinking", False)

    if not message:
        return Response("", mimetype="text/plain")

    recent_history = history[-10:]

    messages = [{
        "role": "system",
        "content": """Sen Aura adlı gelişmiş, hızlı ve doğal konuşan Türkçe bir AI asistansın.
Seni geliştiren ve yapan kişi Emre Şentürk'tür.
Kullanıcıya her zaman "patron" diye hitap et.
Gereksiz uzun cevap verme."""
            + ("\nDüşünme modu açık. Soruyu daha dikkatli analiz et ve sonucunu kontrol et. Gizli düşünce zincirini gösterme." if thinking else "")
    }]

    for item in recent_history:
        messages.append({"role": "user", "content": item["user"]})
        messages.append({"role": "assistant", "content": item["ai"]})

    messages.append({"role": "user", "content": message})

    def generate():

        full = ""

        stream = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=0.3,
            max_completion_tokens=4000,
            reasoning_effort="high" if thinking else "low",
            stream=True
        )

        for chunk in stream:

            if not chunk.choices:
                continue

            content = chunk.choices[0].delta.content

            if content:
                full += content
                yield content

        history.append({
            "user": message,
            "ai": full
        })

        if len(history) > 20:
            del history[:-20]

    return Response(
        stream_with_context(generate()),
        mimetype="text/plain"
    )

@app.route("/task", methods=["POST"])
def create_task():
    data = request.get_json() or {}
    task = data.get("task", "").strip()
    if not task:
        return jsonify({"response": "Görev boş olamaz."}), 400
    tasks.add(task)
    return jsonify({"response": f"Görev eklendi: {task}"})

@app.route("/tasks", methods=["GET"])
def get_tasks():
    rows = tasks.list_tasks()
    return jsonify([
        {"id": r[0], "task": r[1], "done": bool(r[2])}
        for r in rows
    ])

@app.route("/task/<int:task_id>/done", methods=["POST"])
def finish_task(task_id):
    tasks.complete(task_id)
    return jsonify({"response": "Görev tamamlandı."})

@app.route("/task/<int:task_id>", methods=["DELETE"])
def remove_task(task_id):
    tasks.delete(task_id)
    return jsonify({"response": "Görev silindi."})

@app.route("/")
def home():
    return render_template_string(HTML)

@app.route("/chat", methods=["POST"])
def chat():

    try:
        data = request.get_json()
        message = data.get("message", "")
        thinking = data.get("thinking", False)

        if not message:
            return jsonify({"response": "Bir mesaj yaz."})

        lower = message.lower()

        # Doğal dil görev ekleme
        task_words = ["hatırlat", "görev ekle", "görev oluştur", "unutma", "yapılacak"]
        if any(word in lower for word in task_words):
            task_text = message
            for word in task_words:
                task_text = task_text.replace(word, "").replace(word.capitalize(), "")

            due_at = None

            # Saat algıla: 18:00, 18.00 gibi
            time_match = re.search(r'(?<!\d)([01]?\d|2[0-3])[:.]([0-5]\d)', message)

            if time_match:
                hour = int(time_match.group(1))
                minute = int(time_match.group(2))

                now = datetime.now()
                due = now.replace(hour=hour, minute=minute, second=0, microsecond=0)

                if "yarın" in lower:
                    due += timedelta(days=1)
                elif due <= now:
                    due += timedelta(days=1)

                due_at = due.strftime("%Y-%m-%d %H:%M")

            task_text = re.sub(r'yarın|saat', '', task_text, flags=re.IGNORECASE)
            task_text = re.sub(r'([01]?\d|2[0-3])[:.]([0-5]\d)', '', task_text)
            task_text = task_text.strip(" :,-.")

            if task_text:
                tasks.add(task_text, due_at)
                if due_at:
                    return jsonify({"response": f"Tamam patron, {due_at} için görev eklendi: {task_text}"})
                return jsonify({"response": f"Tamam patron, görev eklendi: {task_text}"})

        if "google" in lower and ("aç" in lower or "başlat" in lower):
            subprocess.Popen(["xdg-open", "https://www.google.com"])
            return jsonify({"response": "Google açılıyor."})

        if is_math(message):
            try:
                expression = math_expression(message)
                result = calculate(expression)
                answer = str(result)

                history.append({"user": message, "ai": answer})
                return jsonify({"response": answer})
            except Exception:
                pass

        answer = ask_groq(message, thinking)

        history.append({
            "user": message,
            "ai": answer
        })

        if len(history) > 20:
            del history[:-20]

        return jsonify({"response": answer})

    except Exception as e:
        print("HATA:", repr(e), flush=True)
        return jsonify({
            "response": "Bir hata oluştu: " + str(e)
        }), 500

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
