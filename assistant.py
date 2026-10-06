import requests
import subprocess

print("🤖 Yardımcın hazır. Komut yazabilirsin.")
print("Çıkmak için: konuşmayı bitir")

while True:
    komut = input("Sen: ").lower().strip()

    if komut in ["çık", "konuşmayı bitir", "kapat", "görüşürüz"]:
        print("Görüşürüz!")
        break

    if "google" in komut and ("aç" in komut or "başlat" in komut):
        subprocess.Popen(["xdg-open", "https://www.google.com"])
        print("Google açılıyor.")
        continue

    response = requests.post(
        "http://127.0.0.1:11434/api/generate",
        json={
            "model": "llama3.2:1b",
            "prompt": komut,
            "stream": False
        }
    )

    print("AI:", response.json()["response"])import requests
import subprocess

print("🤖 Yardımcın hazır. Komut yazabilirsin.")
print("Çıkmak için: çık")

while True:
    komut = input("Sen: ").lower().strip()

    if komut == "çık":
        break

    if "google" in komut and ("aç" in komut or "başlat" in komut):
        subprocess.Popen(["xdg-open", "https://www.google.com"])
        print("Google açılıyor.")
        continue

    response = requests.post(
        "http://127.0.0.1:11434/api/generate",
        json={
            "model": "llama3.2:1b",
            "prompt": komut,
            "stream": False
        }
    )

    print("AI:", response.json()["response"])
