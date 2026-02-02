import os
import time
import requests
from flask import Flask
from threading import Thread

app = Flask(__name__)

# Itt tároljuk az aktuális infókat
statusz = {"allapot": "Indítás...", "frissitve": "Soha", "meret": 0}

def adat_motor():
    global statusz
    # Stabilabb Waze URL (Budapest környéke)
    url = "https://www.waze.com/row-rtserver/web/TGeoRSS?bottom=47.1&left=18.5&right=19.8&top=47.9"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://www.waze.com/'
    }

    while True:
        try:
            # Megpróbáljuk lekérni az adatokat
            r = requests.get(url, headers=headers, timeout=15)
            if r.status_code == 200:
                statusz["allapot"] = "✅ ONLINE"
                statusz["frissitve"] = time.strftime('%H:%M:%S')
                statusz["meret"] = len(r.text)
            else:
                # Ha 404-et vagy mást kapunk, azt jelezzük
                statusz["allapot"] = f"❌ Waze hiba: {r.status_code}"
                statusz["meret"] = 0
        except Exception as e:
            statusz["allapot"] = "⚠️ Hálózati hiba"
        
        # Várjunk 2 percet a következő lekérésig, hogy ne tiltson le a Waze
        time.sleep(120)

@app.route('/')
def home():
    szin = "#27ae60" if "✅" in statusz["allapot"] else "#e74c3c"
    return f"""
    <html>
    <head>
        <meta http-equiv="refresh" content="30">
        <style>
            body {{ background: #121212; color: white; font-family: 'Segoe UI', sans-serif; text-align: center; padding-top: 50px; }}
            .card {{ display: inline-block; background: #1e1e1e; padding: 40px; border-radius: 20px; border-top: 10px solid {szin}; box-shadow: 0 10px 40px rgba(0,0,0,0.6); }}
            h1 {{ color: #f1c40f; margin-bottom: 20px; letter-spacing: 1px; }}
            .stat {{ font-size: 1.8em; font-weight: bold; color: {szin}; margin: 20px 0; }}
            .info {{ color: #aaa; font-size: 0.9em; }}
        </style>
    </head>
    <body>
        <div class="card">
            <h1>🛰️ Waze Stealth Radar</h1>
            <p class="stat">{statusz["allapot"]}</p>
            <p>Utolsó frissítés: <b style="color:white;">{statusz["frissitve"]}</b></p>
            <p class="info">Lekért adatmennyiség: {statusz["meret"]} bájt</p>
            <hr style="border:0; border-top:1px solid #333; margin:20px 0;">
            <p style="font-size:0.7em; color:#444;">GitHub: MrGabee/radar ✓</p>
        </div>
    </body>
    </html>
    """

if __name__ == "__main__":
    Thread(target=adat_motor, daemon=True).start()
    # A Repliten a 8080-as port kell
    app.run(host='0.0.0.0', port=8080)
