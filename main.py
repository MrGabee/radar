import os
import time
import requests
import random
from flask import Flask
from threading import Thread

app = Flask(__name__)

ADAT_FAJL = "waze_debug.txt"
radar_status = {"ido": "Indítás...", "info": "Privát híd építése...", "adat": 0}

# A TE ADATAID A KÉPRŐL (image_0821db.png)
P_USER = "qlidbwxz"
P_PASS = "ls2turb9u8b3"

# A listád első néhány proxyja a képernyőképed alapján
PROXY_LIST = [
    "31.59.20.176:6754",
    "23.95.150.145:6114",
    "198.23.239.134:6540",
    "107.172.163.27:6543",
    "198.105.121.200:6462"
]

def radar_motor():
    global radar_status
    waze_url = "https://www.waze.com/row-rtserver/web/TGeoRSS?bottom=47.3&left=18.8&right=19.5&top=47.7"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Referer': 'https://www.waze.com/hu/live-map/'
    }

    while True:
        # Kiválasztunk egy véletlen proxyt és összerakjuk a hitelesítést
        proxy_addr = random.choice(PROXY_LIST)
        proxy_url = f"http://{P_USER}:{P_PASS}@{proxy_addr}"
        proxies = {"http": proxy_url, "https": proxy_url}
        
        try:
            most = time.strftime('%H:%M:%S')
            # Kérés a privát hídon keresztül
            r = requests.get(waze_url, headers=headers, proxies=proxies, timeout=25)
            
            if r.status_code == 200 and len(r.text) > 100:
                with open(ADAT_FAJL, "w", encoding="utf-8") as f:
                    f.write(f"SIKER! Privát hídon át: {most}\n")
                    f.write(f"Aktív híd: {proxy_addr}\n")
                    f.write("-" * 30 + "\n")
                    f.write(r.text)
                
                radar_status = {
                    "ido": most,
                    "info": f"✅ ONLINE (Híd: {proxy_addr.split('.')[0]}...)",
                    "adat": len(r.text)
                }
            else:
                radar_status["info"] = f"❌ Híd válasz hiba: {r.status_code}"
                
        except Exception as e:
            radar_status["info"] = f"⚠️ Kapcsolódás sikertelen..."
        
        # 2 percenként frissítünk a háttérben
        time.sleep(120)

@app.route('/')
def home():
    color = "#27ae60" if "✅" in radar_status['info'] else "#e74c3c"
    return f"""
    <html>
    <head>
        <meta http-equiv="refresh" content="30">
        <title>Waze Radar Online</title>
        <style>
            body {{ font-family: sans-serif; background: #f0f2f5; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }}
            .card {{ background: white; padding: 40px; border-radius: 30px; box-shadow: 0 15px 35px rgba(0,0,0,0.1); text-align: center; min-width: 400px; border-top: 10px solid {color}; }}
            .stats {{ background: #f8f9fa; padding: 25px; border-radius: 20px; text-align: left; margin: 20px 0; border-left: 5px solid {color}; }}
        </style>
    </head>
    <body>
        <div class="card">
            <h1 style="color:#2c3e50;">🛰️ PRIVÁT WAZE RADAR</h1>
            <p style="color:#7f8c8d;">Biztonságos, privát hídon keresztül</p>
            <div class="stats">
                <p><b>Állapot:</b> <span style="color:{color}; font-weight:bold;">{radar_status['info']}</span></p>
                <p><b>Utolsó mérés:</b> {radar_status['ido']}</p>
                <p><b>Adatméret:</b> {radar_status['adat']} karakter</p>
            </div>
            <p style="font-size:0.8em; color:#bdc3c7;">Az oldal 30 másodpercenként magától frissül.</p>
            <a href="/debug" style="display:block; background:#3498db; color:white; padding:15px; border-radius:12px; text-decoration:none; font-weight:bold;">📄 NYERS ADATOK</a>
        </div>
    </body>
    </html>
    """

@app.route('/debug')
def debug():
    if os.path.exists(ADAT_FAJL):
        with open(ADAT_FAJL, "r", encoding="utf-8") as f:
            return f"<html><body style='background:#1a1a1a; color:#00ff00; padding:20px; font-family:monospace;'><pre>{f.read()}</pre></body></html>"
    return "Adatok betöltése..."

if __name__ == "__main__":
    Thread(target=radar_motor, daemon=True).start()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
