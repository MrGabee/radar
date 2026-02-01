import requests
import time
import os
from flask import Flask
from threading import Thread

app = Flask(__name__)

# Memória a találatoknak
radar_data = {
    "status": "Indítás folyamatban...",
    "incidents": [],
    "last_check": "Soha"
}

@app.route('/')
def home():
    # Ez a weboldal tartalma
    html = f"""
    <html>
    <head><title>Waze Radar</title><meta http-equiv="refresh" content="60"></head>
    <body style="font-family:sans-serif; padding:20px;">
        <h1>📡 Waze Radar Élő</h1>
        <p><b>Állapot:</b> {radar_data['status']}</p>
        <p><b>Utolsó frissítés:</b> {radar_data['last_check']}</p>
        <hr>
        <h2>Aktuális események:</h2>
        <ul>
    """
    if not radar_data['incidents']:
        html += "<li>Nincs aktív esemény a körzetben.</li>"
    else:
        for inc in radar_data['incidents']:
            html += f"<li>{inc}</li>"
    
    html += "</ul></body></html>"
    return html

def run_flask():
    # A portot a Render környezeti változójából vesszük, vagy alapértelmezetten 10000
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def radar_loop():
    global radar_data
    while True:
        radar_data['status'] = "Pásztázás..."
        try:
            # IDE JÖN A WAZE KÓDOD LÉNYEGE
            # Példaként frissítjük az időt:
            radar_data['last_check'] = time.strftime('%H:%M:%S')
            
            # Itt töltsd fel a 'radar_data['incidents']' listát a Waze találatokkal!
            
            radar_data['status'] = "Várakozás a következő körre"
            time.sleep(900) # 15 perc pihenő
        except Exception as e:
            radar_data['status'] = f"Hiba: {e}"
            time.sleep(60)

if __name__ == "__main__":
    # 1. Először a weboldalt indítjuk el egy külön szálon!
    web_thread = Thread(target=run_flask)
    web_thread.daemon = True
    web_thread.start()
    
    # 2. Utána indítjuk a radart a fő szálon!
    radar_loop()
