from flask import Flask, render_template_string, request, jsonify
from groq import Groq
import os
import subprocess
import ast
import operator
import re
from datetime import datetime, timedelta
import tasks

app = Flask(__name__)

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

<link rel="stylesheet"
href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.11.1/styles/github-dark.min.css">

<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.11.1/highlight.min.js"></script>

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

.app{
height:100vh;
display:flex;
flex-direction:column;
max-width:1100px;
margin:auto;
}

header{
height:64px;
display:flex;
align-items:center;
padding:0 22px;
border-bottom:1px solid #24272d;
font-size:20px;
font-weight:bold;
background:#0d0f13;
}

.logo{
margin-right:10px;
}

#chat{
flex:1;
overflow-y:auto;
padding:30px 20px 120px;
scroll-behavior:smooth;
}

.message{
max-width:850px;
margin:0 auto 24px;
display:flex;
gap:14px;
line-height:1.6;
}

.avatar{
width:36px;
height:36px;
min-width:36px;
border-radius:50%;
display:flex;
align-items:center;
justify-content:center;
background:#242832;
}

.user .avatar{
background:#2864ff;
}

.content{
flex:1;
overflow-wrap:anywhere;
}

.user .content{
background:#20242b;
padding:12px 16px;
border-radius:18px;
}

.ai .content{
padding-top:5px;
}

pre{
position:relative;
background:#11151b;
border:1px solid #292e37;
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
background:#292e37;
color:white;
border:0;
padding:7px 11px;
border-radius:7px;
cursor:pointer;
}

.copy:hover{
background:#3a414d;
}

.composer{
position:fixed;
bottom:0;
left:0;
right:0;
display:flex;
justify-content:center;
padding:15px;
background:linear-gradient(transparent,#0b0d10 25%);
}

form{
width:min(850px,95%);
display:flex;
gap:10px;
background:#171a20;
border:1px solid #30343c;
border-radius:16px;
padding:8px;
}

input{
flex:1;
background:transparent;
border:0;
outline:none;
color:white;
font-size:16px;
padding:12px;
}

button.send{
width:45px;
height:45px;
border:0;
border-radius:12px;
background:#2864ff;
color:white;
font-size:18px;
cursor:pointer;
}

button.send:hover{
background:#3973ff;
}

.typing{
opacity:.7;
}

.dot{
display:inline-block;
animation:blink 1.2s infinite;
}

@keyframes blink{
0%,100%{opacity:.2}
50%{opacity:1}
}

@media(max-width:600px){
header{padding:0 15px}
#chat{padding:20px 12px 110px}
.message{gap:9px}
.avatar{width:30px;height:30px;min-width:30px}
}
</style>
</head>

<body>
<canvas id="bg"></canvas>

<div class="app">

<header>
<span class="logo">✨</span>
Aura
</header>

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

<input
id="message"
placeholder="Mesajınızı yazın..."
autocomplete="off"
>

<button class="send">↑</button>

</form>

</div>

</div>

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
}

function animate(){

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

async function sendMessage(event){

event.preventDefault();

const input=document.getElementById("message");
const chat=document.getElementById("chat");

const message=input.value.trim();

if(!message)return;

const user=document.createElement("div");

user.className="message user";

user.innerHTML=
'<div class="avatar">👤</div>'+
'<div class="content">'+escapeHtml(message)+'</div>';

chat.appendChild(user);

input.value="";

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
message:message
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

}catch(error){

loading.querySelector(".content").innerText=
"Bağlantı hatası: "+error;

}

chat.scrollTop=chat.scrollHeight;

}

</script>

</body>
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

def ask_groq(message):

    recent_history = history[-10:]

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
        max_completion_tokens=4000
    )

    return response.choices[0].message.content


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
        message = data.get("message", "").strip()

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

        answer = ask_groq(message)

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
