import requests
import time
import os
from flask import Flask
from threading import Thread

app = Flask(__name__)

# Memória a találatoknak
radar_status = {
    "utolso_frissites": "Indítás...",
    "esemenyek": []
}

@app.route('/')
def home():
    return f"""
    <html>
    <body style="font-family: sans-serif; padding: 30px;">
        <h1>📡 Waze Radar Élő</h1>
        <p><b>Állapot:</b> Aktív</p>
        <p><b>Utolsó frissítés:</b> {radar_status['utolso_frissites']}</p>
        <hr>
        <ul>{"".join([f"<li>{inc}</li>" for inc in radar_status['esemenyek']]) if radar_status['esemenyek'] else "<li>Nincs aktív esemény...</li>"}</ul>
    </body>
    </html>
    """

def radar_logic():
    global radar_status
    while True:
        try:
            # ITT FUT A RADAROD
            current_time = time.strftime('%H:%M:%S')
            print(f"🔍 Pásztázás: {current_time}")
            
            radar_status['utolso_frissites'] = current_time
            # Ide jön majd a valódi Waze lekérdezésed
            
            time.sleep(900)
        except Exception as e:
            print(f"Hiba: {e}")
            time.sleep(60)

# --- A TRÜKK: A háttérben indítjuk a radart, a fő szálon a webet ---
print("🚀 Rendszer indítása...")
radar_thread = Thread(target=radar_logic, daemon=True)
radar_thread.start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    # Ez a sor fogja életben tartani a kapcsolatot a Renderrel
    app.run(host='0.0.0.0', port=port)
