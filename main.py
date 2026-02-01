import requests
import time
import os
from flask import Flask
from threading import Thread

app = Flask(__name__)
# Ebben tároljuk a legfrissebb adatokat, hogy a weboldal megmutathassa
radar_status = {"idopont": "Indítás...", "lista": []}

@app.route('/')
def home():
    # Ez a rész felel azért, hogy ne legyen "Not Found" a böngészőben
    return f"<h1>Waze Radar</h1><p>Utolsó sikeres pásztázás: {radar_status['idopont']}</p>", 200

def radar_logic():
    global radar_status
    while True:
        try:
            current_time = time.strftime('%H:%M:%S')
            print(f"🔍 Pasztazas: {current_time}")
            radar_status['idopont'] = current_time
            
            # IDE MÁSOLD BE A WAZE LEKÉRDEZŐD LÉNYEGÉT
            # Példa: radar_status['lista'] = lekert_adatok
            
            time.sleep(900) # 15 perc várakozás
        except Exception as e:
            print(f"Hiba történt: {e}")
            time.sleep(60)

if __name__ == "__main__":
    # A radar külön szálon (Thread) fut, hogy ne blokkolja a weboldalt
    Thread(target=radar_logic, daemon=True).start()
    
    # A Render automatikusan ad portot, de ha nem, a 10000-et használjuk
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
