import requests
import time
from flask import Flask
from threading import Thread

# --- 1. WEB SZERVER (Hogy a Render ne állítsa le a programot) ---
app = Flask('')

@app.route('/')
def home():
    return "A Radar eloben fut!"

def run_web():
    # A Render a 10000-es portot figyeli
    app.run(host='0.0.0.0', port=10000)

# --- 2. A RADAR PROGRAMOD ---
def radar_logic():
    print("🚀 Radar indítása...")
    # Ide jön az eredeti Waze lekérdező kódod lényege
    while True:
        try:
            print(f"🔍 Pásztázás: {time.strftime('%H:%M:%S')}")
            
            # Itt futna a Waze API hívásod...
            # (A korábbi kódod többi részét ide illeszd be a 'while' alá)
            
            print("⏳ Várakozás 15 percet...")
            time.sleep(900)
        except Exception as e:
            print(f"Hiba történt: {e}")
            time.sleep(60)

# --- 3. INDÍTÁS ---
if __name__ == "__main__":
    # Elindítjuk a weboldalt egy külön szálon
    server_thread = Thread(target=run_web)
    server_thread.start()
    
    # Elindítjuk a radarodat a fő szálon
    radar_logic()
