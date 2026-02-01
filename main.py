import os
import time
import requests
import random
from flask import Flask
from threading import Thread

app = Flask(__name__)

ADAT_FAJL = "waze_debug.txt"
radar_status = {"ido": "Indítás...", "info": "Kapcsolódás a műholdakhoz...", "adat": 0}

def radar_motor():
    global radar_status
    # Ez a Waze legstabilabb belső feedje Budapest környékére
    waze_url = "https://www.waze.com/row-rtserver/web/TGeoRSS?bottom=47.35&left=18.95&right=19.35&top=47.65"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'hu-HU,hu;q=0.8,en-US;q=0.5,en;q=0.3',
        'Referer': 'https://www.waze.com/hu/live-map/',
        'Connection': 'keep-alive'
    }

    while True:
        try:
            # Egy kis véletlen szünet, hogy ne legyen gyanús a robot
            session = requests.Session()
            r = session.get(waze_url, headers=headers, timeout=25)
            most = time.strftime('%H:%M:%S')
            
            if r.status_code == 200 and len(r.text) > 150:
                with open(ADAT_FAJL, "w", encoding="utf-8") as f:
                    f.write(f"SIKER! Frissítve: {most}\n")
                    f.write("-" * 30 + "\n")
                    f.write(r.text)
                
                radar_status = {
                    "ido": most,
                    "info": "✅ ONLINE - Adatfolyam aktív",
                    "adat": len(r.text)
                }
                print(f"[{most}] Siker: {len(r.text)} bájt.")
            else:
                radar_status["info"] = f"❌ Waze korlátozás (Kód: {r.status_code})"
                print(f"[{most}] Hiba kód: {r.status_code}")
                
        except Exception as e:
            radar_status["info"] = f"⚠️ Kapcsolati hiba: {str(e)[:20]}..."
        
        # 2 és 4 perc közötti véletlenszerű várakozás
        time.sleep(random.randint(120, 240))

@app.route('/')
def home():
    color = "#27ae60" if "✅" in radar_status['info'] else "#e74c3c"
    return f"""
    <body style="font-family:sans-serif; background:#f0f2f5; display:flex; justify-content:center; align-items:center; height:100vh; margin:0;">
        <div style="background:white; padding:40px; border-radius:30px; box-shadow:0 15px 35px rgba(0,0,0,0.2); text-align:center; min-width:380px; border-top:10px solid {color};">
            <h1 style="color:#2c3e50; margin-bottom:5px;">🛰️ WAZE RADAR v2.0</h1>
            <p style="color:#7f8c8d; font-size:0.9em;">Budapest és környéke</p>
            <div style="background:#f8f9fa; padding:25px; border-radius:20px; margin:25px 0; text-align:left; border-left:5px solid {color};">
                <p style="margin:8px 0;"><b>Állapot:</b> <span style="color:{color}; font-weight:bold;">{radar_status['info']}</span></p>
                <p style="margin:8px 0;"><b>Utolsó mérés:</b> <span style="color:#34495e;">{radar_status['ido']}</span></p>
                <p style="margin:8px 0;"><b>Adatméret:</b> <span style="color:#34495e;">{radar_status['adat']} karakter</span></p>
            </div>
            <a href="/debug" style="display:block; background:#3498db; color:white; padding:18px; border-radius:12px; text-decoration:none; font-weight:bold; transition:0.3s;">📄 NYERS ADATOK MEGTEKINTÉSE</a>
            <p style="margin-top:15px; font-size:0.7em; color:#bdc3c7;">Az oldal 3 percenként automatikusan frissül a háttérben.</p>
        </div>
    </body>
    """

@app.route('/debug')
def debug():
    if os.path.exists(ADAT_FAJL):
        with open(ADAT_FAJL, "r", encoding="utf-8") as f:
            return f"<html><body style='background:#1a1a1a; color:#00ff00; padding:20px; font-family:monospace;'><pre>{f.read()}</pre></body></html>"
    return "Még nem érkezett adat. Frissíts rá 1 perc múlva!"

if __name__ == "__main__":
    Thread(target=radar_motor, daemon=True).start()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
