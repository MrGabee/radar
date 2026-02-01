import requests
import time
import os
from flask import Flask
from threading import Thread

app = Flask(__name__)
radar_status = {"idopont": "Indítás...", "lista": []}

@app.route('/')
def home():
    # Ez a rész felel azért, hogy ne legyen "Not Found"
    return f"<h1>Waze Radar</h1><p>Utolsó keresés: {radar_status['idopont']}</p>", 200

def radar_logic():
    global radar_status
    while True:
        try:
            current_time = time.strftime('%H:%M:%S')
            print(f"🔍 Pasztazas: {current_time}")
            radar_status['idopont'] = current_time
            # Ide jön a Waze lekérdezésed...
            time.sleep(900)
        except Exception as e:
            print(f"Hiba: {e}")
            time.sleep(60)

if __name__ == "__main__":
    # A radar külön szálon fut, hogy ne blokkolja a webet
    Thread(target=radar_logic, daemon=True).start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
