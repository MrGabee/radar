import os
import time
import requests
from flask import Flask
from threading import Thread

app = Flask(__name__)

ADAT_FAJL = "waze_debug.txt"
radar_status = {"ido": "Indítás...", "info": "Radar ébredezik...", "adat": 0}

def radar_motor():
    global radar_status
    # EZ EGY STABILABB LINK (Publikus Feed)
    waze_url = "https://www.waze.com/row-rtserver/web/TGeoRSS?bottom=47.1&left=18.7&right=19.5&top=47.9"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Accept': '*/*',
        'Referer': 'https://www.waze.com/hu/live-map/'
    }

    while True:
        try:
            # Megpróbáljuk leszedni az adatot
            r = requests.get(waze_url, headers=headers, timeout=20)
            most = time.strftime('%H:%M:%S')
            
            if r.status_code == 200 and len(r.text) > 100:
                with open(ADAT_FAJL, "w", encoding="utf-8") as f:
                    f.write(f"SIKER! {most}\n{'-'*20}\n{r.text[:5000]}") # Csak az első 5000 karaktert mentjük
                
                radar_status = {
                    "ido": most,
                    "info": "✅ MŰKÖDIK - Adat beérkezett!",
                    "adat": len(r.text)
                }
            else:
                # Ha 404 vagy üres, megpróbálunk egy alternatív Budapest linket
                radar_status["info"] = f"❌ Waze hiba: {r.status_code} - Újrapróbálkozás..."
                
        except Exception as e:
            radar_status["info"] = f"⚠️ Hiba: {str(e)[:30]}"
        
        time.sleep(60) # Percenként próbálkozik, amíg be nem jön

@app.route('/')
def home():
    color = "#27ae60" if "✅" in radar_status['info'] else "#e74c3c"
    return f"""
    <body style="font-family:sans-serif; background:#f4f7f6; display:flex; justify-content:center; align-items:center; height:100vh; margin:0;">
        <div style="background:white; padding:40px; border-radius:25px; box-shadow:0 10px 30px rgba(0,0,0,0.1); text-align:center; border-top:8px solid {color};">
            <h1 style="color:#2c3e50;">📡 Waze Radar Budapest</h1>
            <div style="background:#f9f9f9; padding:20px; border-radius:15px; margin:20px 0; text-align:left;">
                <p><b>Állapot:</b> <span style="color:{color};">{radar_status['info']}</span></p>
                <p><b>Utolsó mérés:</b> {radar_status['ido']}</p>
                <p><b>Adatmennyiség:</b> {radar_status['adat']} karakter</p>
            </div>
            <a href="/debug" style="display:block; background:#3498db; color:white; padding:15px; border-radius:10px; text-decoration:none; font-weight:bold;">NYERS ADATOK MEGTEKINTÉSE</a>
        </div>
    </body>
    """

@app.route('/debug')
def debug():
    if os.path.exists(ADAT_FAJL):
        with open(ADAT_FAJL, "r", encoding="utf-8") as f:
            return f"<html><body style='background:#1e1e1e; color:#00ff00; padding:20px;'><pre>{f.read()}</pre></body></html>"
    return "Várj a legelső sikeres mérésre..."

if __name__ == "__main__":
    Thread(target=radar_motor, daemon=True).start()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
