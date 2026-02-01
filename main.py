import os
import time
import requests
from flask import Flask
from threading import Thread

# 1. A Flask webalkalmazás létrehozása
app = Flask(__name__)

# Memória az adatok tárolásához
radar_status = {
    "ido": "Indítás...",
    "uzenetek": ["A radar éppen ébredezik. Kérlek, frissíts 1 perc múlva!"]
}

# 2. A Weboldal kinézete (amit a böngészőben látsz majd)
@app.route('/')
def home():
    lista = "".join([f"<li style='margin-bottom:10px;'>{msg}</li>" for msg in radar_status['uzenetek']])
    return f"""
    <html>
    <head><title>Waze Radar Budapest</title><meta charset="utf-8"></head>
    <body style="font-family: sans-serif; padding: 40px; background-color: #f0f2f5;">
        <div style="max-width: 600px; margin: auto; background: white; padding: 30px; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            <h1 style="color: #1a73e8;">📡 Waze Radar Élő</h1>
            <p><b>Utolsó pásztázás:</b> {radar_status['ido']}</p>
            <hr style="border: 0; border-top: 1px solid #eee;">
            <ul style="list-style-type: none; padding: 0;">{lista}</ul>
        </div>
    </body>
    </html>
    """

# 3. A Radar motorja (10 percenként lekéri a Waze adatait)
def radar_loop():
    global radar_status
    # Budapest és környéke koordinátái
    waze_url = "https://www.waze.com/row-rtserver/web/TGeoRSS?bottom=47.34&left=18.85&right=19.33&top=47.63"
    headers = {'User-Agent': 'Mozilla/5.0'}

    while True:
        try:
            most = time.strftime('%H:%M:%S')
            print(f"--- Waze frissítés: {most} ---")
            
            response = requests.get(waze_url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                hossz = len(response.text)
                radar_status['uzenetek'] = [
                    "✅ Kapcsolat a Waze szerverrel: OK",
                    f"📦 Érkezett adat: {hossz} karakter",
                    "🚀 A radar aktívan figyeli Budapestet!"
                ]
            else:
                radar_status['uzenetek'] = [f"❌ Waze hiba: {response.status_code}"]
            
            radar_status['ido'] = most
            
        except Exception as e:
            radar_status['uzenetek'] = [f"⚠️ Hiba a lekérdezésben: {e}"]
        
        time.sleep(600) # 10 perc pihenő

# 4. A program elindítása
if __name__ == "__main__":
    # A radart egy külön háttérszálon indítjuk el
    Thread(target=radar_loop, daemon=True).start()
    
    # A weboldalt a Render által kijelölt porton indítjuk
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
