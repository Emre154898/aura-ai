from flask import Flask, render_template_string, request, jsonify
import requests
import subprocess
import ast
import operator
from duckduckgo_search import DDGS

app = Flask(__name__)

MODEL = "llama3.2:1b"
OLLAMA_URL = "http://127.0.0.1:11434/api/generate"

HTML = """
<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>AI Asistan</title>
<style>
body{margin:0;background:#0f1115;color:white;font-family:Arial}
.app{max-width:900px;margin:auto;height:100vh;display:flex;flex-direction:column}
header{padding:20px;font-size:22px;font-weight:bold;border-bottom:1px solid #292d35}
#chat{flex:1;overflow-y:auto;padding:20px}
.message{max-width:80%;padding:14px;margin:10px 0;border-radius:14px;white-space:pre-wrap}
.user{margin-left:auto;background:#2b6cff}
.ai{background:#1b1f27}
form{display:flex;gap:10px;padding:15px;border-top:1px solid #292d35}
input{flex:1;padding:15px;border-radius:12px;border:1px solid #333;background:#181b21;color:white;font-size:16px}
button{padding:0 20px;border:0;border-radius:12px;font-weight:bold}
</style>
</head>
<body>
<div class="app">
<header>🤖 AI Asistan</header>
<div id="chat">
<div class="message ai">Merhaba! Nasıl yardımcı olabilirim?</div>
</div>
<form onsubmit="sendMessage(event)">
<input id="message" placeholder="Bir şey yaz..." autocomplete="off">
<button>Gönder</button>
</form>
</div>

<script>
async function sendMessage(event){
    event.preventDefault();

    const input=document.getElementById("message");
    const chat=document.getElementById("chat");
    const message=input.value.trim();

    if(!message)return;

    const user=document.createElement("div");
    user.className="message user";
    user.innerText=message;
    chat.appendChild(user);

    input.value="";

    const loading=document.createElement("div");
    loading.className="message ai";
    loading.innerText="🔎 Araştırıyor...";
    chat.appendChild(loading);

    chat.scrollTop=chat.scrollHeight;

    try{
        const response=await fetch("/chat",{
            method:"POST",
            headers:{"Content-Type":"application/json"},
            body:JSON.stringify({message})
        });

        const data=await response.json();

        loading.remove();

        const answer=document.createElement("div");
        answer.className="message ai";
        answer.innerText=data.response;
        chat.appendChild(answer);

    }catch(error){
        loading.innerText="Bağlantı hatası: "+error;
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
    expression = expression.replace(",", ".")
    expression = expression.replace("×", "*")
    expression = expression.replace("÷", "/")

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

def web_search(query):
    results = []

    try:
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=5):
                results.append(
                    f"Başlık: {r.get('title')}\n"
                    f"Kaynak: {r.get('href')}\n"
                    f"Bilgi: {r.get('body')}"
                )
    except Exception as e:
        print("WEB HATASI:", repr(e), flush=True)

    return "\n\n".join(results)

def needs_web(message):
    words = [
        "güncel", "bugün", "şimdi", "son dakika",
        "haber", "fiyat", "hava", "kim kazandı",
        "son durum", "2026", "2025",
        "kaç tl", "ne kadar", "maç", "transfer"
    ]

    text = message.lower()
    return any(word in text for word in words)

def ask_ai(message):

    if needs_web(message):

        web_results = web_search(message)

        prompt = f"""
Sen hızlı ve doğru Türkçe konuşan bir AI asistansın.

Kullanıcı güncel bilgi istedi.
Aşağıdaki web arama sonuçlarını kullanarak cevap ver.

Kullanıcı:
{message}

WEB SONUÇLARI:
{web_results}

Kurallar:
- Web sonuçlarına göre cevap ver.
- Emin olmadığın bilgiyi uydurma.
- Kısa ve anlaşılır cevap ver.
"""

    else:

        prompt = f"""
Sen Türkçe konuşan hızlı bir AI asistanısın.
Kısa, doğru ve anlaşılır cevap ver.

Kullanıcı:
{message}
"""

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "prompt": prompt,
            "stream": False, "keep_alive": "10m",
            "options": {
                "temperature": 0.1
            }
        },
        timeout=120
    )

    response.raise_for_status()
    return response.json()["response"]

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

        if "google" in lower and ("aç" in lower or "başlat" in lower):
            subprocess.Popen([
                "xdg-open",
                "https://www.google.com"
            ])

            return jsonify({"response": "Google açılıyor."})

        if is_math(message):

            try:
                expression = math_expression(message)
                result = calculate(expression)

                return jsonify({
                    "response": str(result)
                })

            except Exception:
                pass

        answer = ask_ai(message)

        return jsonify({
            "response": answer
        })

    except Exception as e:

        print("HATA:", repr(e), flush=True)

        return jsonify({
            "response": "Bir hata oluştu: " + str(e)
        }), 500

if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000
    )
