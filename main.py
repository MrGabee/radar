import os
import time
from flask import Flask
from threading import Thread

app = Flask(__name__)

# Ebben tároljuk az adatokat, hogy a weboldal el érje
status_adatok = {
    "ido": "Még nem frissült",
    "lista": []
}

@app.route('/')
def home():
    # Nagyon egyszerű HTML, hogy biztosan ne legyen hiba
    return f"""
    <h1>Waze Radar Status</h1>
    <p>Utolso ellenorzes: {status_adatok['ido']}</p>
    <hr>
    <p>A szerver fut, a hatterfolyamat aktiv.</p>
    """

def radar_loop():
    global status_adatok
    while True:
        try:
            status_adatok['ido'] = time.strftime('%H:%M:%S')
            print(f"--- Radar kor: {status_adatok['ido']} ---")
            # Ide majd visszatesszük a Waze kódodat, ha ez már stabil
            time.sleep(600)
        except Exception as e:
            print(f"Hiba: {e}")
            time.sleep(30)

if __name__ == "__main__":
    # 1. Háttérfolyamat indítása
    Thread(target=radar_loop, daemon=True).start()
    
    # 2. Weboldal indítása a Render által kért porton
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
