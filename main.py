import os
import time
import requests
from flask import Flask
from threading import Thread

app = Flask(__name__)

# Fájlnév a mentéshez
ADAT_FAJL = "waze_debug.txt"

# Állapot tároló
radar_status = {
    "ido": "Indítás...",
    "info": "A radar éppen ébredezik...",
    "nyers_hossz": 0
}

def radar_motor():
    global radar_status
    # Ez a stabilabb URL Budapest központtal
    waze_url = "https://www.waze.com/row-rtserver/web/TGeoRSS?bottom=47.35&left=18.95&right=19.35&top=47.65"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Accept': 'text/xml,application/xml,application/xhtml+xml',
        'Referer': 'https://www.waze.com/hu/live-map/',
        'Accept-Language': 'hu-HU,hu;q=0.9'
    }

    while True:
        try:
            most = time.strftime('%H:%M:%S')
            # Lekérés a Waze-től
            response = requests.get(waze_url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                tartalom = response.text
                
                # Mentés fájlba
                with open(ADAT_FAJL, "w", encoding="utf-8") as f:
                    f.write(f"FRISSÍTVE: {most}\n")
                    f.write("-" * 30 + "\n")
                    f.write(tartalom)
                
                radar_status['ido'] = most
                radar_status['info'] = "✅ Működik - Adat érkezett"
                radar_status['nyers_hossz'] = len(tartalom)
                print(f"[{most}] Siker: {len(tartalom)} karakter.")
            else:
                radar_status['info'] = f"❌ Waze hiba: {response.status_code}"
                print(f"Hiba: {response.status_code}")
                
        except Exception as e:
            radar_status['info'] = f"⚠️ Hiba: {str(e)}"
            print(f"Hiba: {e}")
        
        # 3 percenként frissít
        time.sleep(180)

@app.route('/')
def home():
    color = "#2ecc71" if "OK" in radar_status['info'] or "Működik" in radar_status['info'] else "#e74c3c"
    return f"""
    <body style="font-family:sans-serif; background:#f0f2f5; display:flex; justify-content:center; align-items:center; height:100vh; margin:0;">
        <div style="background:white; padding:40px; border-radius:20px; shadow:0 4px 15px rgba(0,0,0,0.1); text-align:center; min-width:350px;">
            <h1 style="color:#1a73e8;">🛰️ Waze Radar</h1>
            <div style="font-size:1.2em; margin:20px 0; padding:15px; border-radius:10px; background:#f8f9fa; border-left: 5px solid {color};">
                <p><b>Állapot:</b> {radar_status['info']}</p>
                <p><b>Utolsó mérés:</b> {radar_status['ido']}</p>
                <p><b>Adatméret:</b> {radar_status['nyers_hossz']} karakter</p>
            </div>
            <a href="/debug" style="text-decoration:none; background:#1a73e8; color:white; padding:12px 20px; border-radius:8px; font-weight:bold; display:block;">NYERS ADATOK MEGNYITÁSA</a>
        </div>
    </body>
    """

@app.route('/debug')
def debug():
    if os.path.exists(ADAT_FAJL):
        with open(ADAT_FAJL, "r", encoding="utf-8") as f:
            return f"<html><body style='background:#1e1e1e; color:#00ff00; padding:20px;'><pre>{f.read()}</pre></body></html>"
    return "Még nincs adat. Várj egy kicsit..."

if __name__ == "__main__":
    Thread(target=radar_motor, daemon=True).start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
