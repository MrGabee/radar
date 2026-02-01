import requests
import time
import os
from flask import Flask
from threading import Thread

# --- ÁL-WEBOLDAL A RENDERNEK ---
app = Flask('')

@app.route('/')
def home():
    return "A radar eloben fut a hatterben!"

def run_web():
    # A Render a 10000-es portot figyeli alapból
    app.run(host='0.0.0.0', port=10000)

# --- A TE EREDETI RADAR KÓDOD (Kicsit átalakítva a folyamatos futáshoz) ---
def radar_loop():
    print("🚀 Radar indítása a háttérben...")
    while True:
        # Ide jön a lekérdező kódod lényege
        print(f"🔍 Pásztázás: {time.strftime('%H:%M:%S')}")
        
        # ... (Ide másold be a lekérdezésed többi részét) ...
        
        print("⏳ Várakozás 15 percet a következő frissítésig...")
        time.sleep(900)

if __name__ == "__main__":
    # 1. Elindítjuk a weboldalt egy külön szálon
    t = Thread(target=run_web)
    t.start()
    
    # 2. Elindítjuk a radart a fő szálon
    radar_loop()
