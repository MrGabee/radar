import os
import time
import requests
import random
from flask import Flask
from threading import Thread

app = Flask(__name__)

ADAT_FAJL = "waze_debug.txt"
radar_status = {"ido": "Indítás...", "info": "Híd keresése...", "adat": 0}

# INGYENES PROXY LISTA - Ezeken keresztül "osonunk" át
# Ha ezek lelassulnának, a Webshare-es saját proxyra kell majd cserélni
PROXY_LIST = [
    "http://149.28.44.50:8080",
    "http://167.71.230.134:8080",
    "http://138.68.60.8:8080",
    "http://159.203.85.195:3128"
]

def radar_motor():
    global radar_status
    waze_url = "https://www.waze.com/row-rtserver/web/TGeoRSS?bottom=47.3&left=18.8&right=19.5&top=47.7"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Referer': 'https://www.waze.com/hu/live-map/',
        'Accept-Language': 'hu-HU,hu;q=0.9'
    }

    while True:
        # Minden körben választunk egy véletlen hidat (proxyt)
        current_proxy = random.choice(PROXY_LIST)
        proxies = {"http": current_proxy, "https": current_proxy}
        
        try:
            most = time.strftime('%H:%M:%S')
            # Itt küldjük a kérést a hídon keresztül
            r = requests.get(waze_url, headers=headers, proxies=proxies, timeout=15)
            
            if r.status_code == 200 and len(r.text) > 100:
                with open(ADAT_FAJL, "w", encoding="utf-8") as f:
                    f.write(f"SIKER A HÍDON ÁT! Frissítve: {most}\n")
                    f.write(f"Használt híd: {current_proxy}\n")
                    f.write("-" * 30 + "\n")
                    f.write(r.text)
                
                radar_status = {
                    "ido": most,
                    "info": f"✅ ONLINE (Híd: {current_proxy.split(':')[1]})",
                    "adat": len(r.text)
                }
            else:
                radar_status["info"] = f"❌ A híd túlterhelt (Kód: {r.status_code})"
                
        except Exception as e:
            radar_status["info"] = f"⚠️ Híd hiba, újratervezés..."
        
        # Rövidebb várakozás, hogy gyorsabban találjon működő hidat
        time.sleep(60)

@app.route('/')
def home():
    color = "#27ae60" if "✅" in radar_status['info'] else "#e74c3c"
    return f"""
    <body style="font-family:sans-serif; background:#f4f7f6; display:flex; justify-content:center; align-items:center; height:100vh; margin:0;">
        <div style="background:white; padding:40px; border-radius:30px; box-shadow:0 15px 35px rgba(0,0,0,0.1); text-align:center; min-width:400px; border-top:10px solid {color};">
            <h1 style="color:#2c3e50;">📡 WAZE ONLINE RADAR</h1>
            <p style="color:#7f8c8d;">Hídon keresztül továbbított adatok</p>
            <div style="background:#f8f9fa; padding:25px; border-radius:20px; text-align:left; border-left:5px solid {color};">
                <p><b>Állapot:</b> <span style="color:{color};">{radar_status['info']}</span></p>
                <p><b>Utolsó mérés:</b> {radar_status['ido']}</p>
                <p><b>Adatméret:</b> {radar_status['adat']} karakter</p>
            </div>
            <br>
            <a href="/debug" style="display:block; background:#3498db; color:white; padding:18px; border-radius:12px; text-decoration:none; font-weight:bold;">NYERS ADATOK</a>
        </div>
    </body>
    """

@app.route('/debug')
def debug():
    if os.path.exists(ADAT_FAJL):
        with open(ADAT_FAJL, "r", encoding="utf-8") as f:
            return f"<html><body style='background:#1a1a1a; color:#00ff00; padding:20px; font-family:monospace;'><pre>{f.read()}</pre></body></html>"
    return "Híd kiépítése folyamatban... Frissíts 1 perc múlva!"

if __name__ == "__main__":
    Thread(target=radar_motor, daemon=True).start()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
