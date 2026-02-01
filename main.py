import os
import time
import requests
import random
from flask import Flask
from threading import Thread

app = Flask(__name__)

# Fájl az adatoknak
ADAT_FAJL = "waze_debug.txt"
radar_status = {"ido": "Indítás...", "info": "Kapcsolódás...", "adat": 0}

def radar_motor():
    global radar_status
    
    # Ez a GeoRSS feed Budapest közepére van lőve, ez a legkevésbé védett pontjuk
    waze_url = "https://www.waze.com/row-rtserver/web/TGeoRSS?bottom=47.3&left=18.8&right=19.5&top=47.7"
    
    # Nagyon erős fejlécek, hogy hús-vér embernek tűnjünk
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Accept': 'text/xml,application/xml,application/xhtml+xml,text/html;q=0.9,*/*;q=0.8',
        'Accept-Language': 'hu-HU,hu;q=0.9,en-US;q=0.8,en;q=0.7',
        'Referer': 'https://www.waze.com/hu/live-map/',
        'Cookie': f'f_id={random.randint(1000,9999)}; _ga=GA1.1.{random.randint(100000,999999)}.{time.time()}',
        'Connection': 'keep-alive'
    }

    while True:
        try:
            most = time.strftime('%H:%M:%S')
            # Egy session-t használunk, ami stabilabb kapcsolatot ad
            with requests.Session() as s:
                r = s.get(waze_url, headers=headers, timeout=20)
                
                if r.status_code == 200 and len(r.text) > 100:
                    with open(ADAT_FAJL, "w", encoding="utf-8") as f:
                        f.write(f"SIKER! Frissítve: {most}\n")
                        f.write("-" * 30 + "\n")
                        f.write(r.text)
                    
                    radar_status = {
                        "ido": most,
                        "info": "✅ MŰKÖDIK - Adatfolyam aktív",
                        "adat": len(r.text)
                    }
                else:
                    radar_status["info"] = f"❌ Waze hiba: {r.status_code} (Tiltás)"
            
        except Exception as e:
            radar_status["info"] = f"⚠️ Hiba: {str(e)[:25]}"
        
        # 120 és 300 másodperc közötti véletlen várás (hogy ne legyen gyanús a ritmus)
        time.sleep(random.randint(120, 300))

@app.route('/')
def home():
    color = "#27ae60" if "✅" in radar_status['info'] else "#e74c3c"
    return f"""
    <body style="font-family:sans-serif; background:#f4f7f6; display:flex; justify-content:center; align-items:center; height:100vh; margin:0;">
        <div style="background:white; padding:40px; border-radius:30px; box-shadow:0 15px 35px rgba(0,0,0,0.1); text-align:center; min-width:400px; border-top:10px solid {color};">
            <h1 style="color:#2c3e50; margin-bottom:5px;">📡 WAZE RADAR v3.0</h1>
            <p style="color:#7f8c8d; font-size:0.9em; margin-bottom:20px;">Budapest Monitoring</p>
            <div style="background:#f8f9fa; padding:25px; border-radius:20px; text-align:left; border-left:5px solid {color};">
                <p><b>Állapot:</b> <span style="color:{color}; font-weight:bold;">{radar_status['info']}</span></p>
                <p><b>Utolsó mérés:</b> {radar_status['ido']}</p>
                <p><b>Adatméret:</b> {radar_status['adat']} karakter</p>
            </div>
            <br>
            <a href="/debug" style="display:block; background:#3498db; color:white; padding:18px; border-radius:12px; text-decoration:none; font-weight:bold;">📄 NYERS ADATOK MEGTEKINTÉSE</a>
        </div>
    </body>
    """

@app.route('/debug')
def debug():
    if os.path.exists(ADAT_FAJL):
        with open(ADAT_FAJL, "r", encoding="utf-8") as f:
            return f"<html><body style='background:#1a1a1a; color:#00ff00; padding:20px; font-family:monospace;'><pre>{f.read()}</pre></body></html>"
    return "Nincs adat. Várj legalább 2 percet!"

if __name__ == "__main__":
    Thread(target=radar_motor, daemon=True).start()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
