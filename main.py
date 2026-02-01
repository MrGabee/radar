import os
import time
import requests
from flask import Flask
from threading import Thread

# 1. A Flask weboldal létrehozása
app = Flask(__name__)

# Memória, ahol az adatokat tároljuk (hogy a weboldal meg tudja mutatni)
radar_adatok = {
    "ido": "Még nem frissült",
    "esemenyek": ["A radar indul... Kérlek frissíts 1 perc múlva!"]
}

# 2. A weboldal kinézete (amit a böngészőben látsz)
@app.route('/')
def home():
    lista_html = "".join([f"<li style='margin-bottom:10px;'>{sor}</li>" for sor in radar_adatok['esemenyek']])
    return f"""
    <html>
    <head><title>Waze Radar</title><meta charset="utf-8"></head>
    <body style="font-family: sans-serif; padding: 30px; line-height: 1.6; background-color: #f4f4f9;">
        <div style="max-width: 600px; margin: auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
            <h1 style="color: #2c3e50;">📡 Waze Radar Élő</h1>
            <p><b>Utolsó frissítés:</b> {radar_adatok['ido']}</p>
            <hr>
            <ul style="list-style-type: none; padding: 0;">{lista_html}</ul>
        </div>
    </body>
    </html>
    """

# 3. A Radar motorja (ez fut a háttérben 10 percenként)
def radar_motor():
    global radar_adatok
    # Budapest koordináták (Waze formátum)
    waze_url = "https://www.waze.com/row-rtserver/web/TGeoRSS?bottom=47.34&left=18.85&right=19.33&top=47.63"
    headers = {'User-Agent': 'Mozilla/5.0'}

    while True:
        try:
            most = time.strftime('%H:%M:%S')
            print(f"--- Lekérdezés indítása: {most} ---")
            
            response = requests.get(waze_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                # Most egyelőre csak a siker tényét mentjük, a feldolgozás a következő lépés
                radar_adatok['esemenyek'] = [
                    "✅ Kapcsolat a Waze-zel: OK",
                    f"📦 Adat fogadva: {len(response.text)} karakter",
                    "🚀 A rendszer készen áll a finomhangolásra!"
                ]
            else:
                radar_adatok['esemenyek'] = ["❌ Waze szerver hiba: " + str(response.status_code)]
            
            radar_adatok['ido'] = most
            
        except Exception as e:
            radar_adatok['esemenyek'] = [f"⚠️ Hiba történt: {e}"]
        
        time.sleep(600) # 10 perc várakozás a következő körig

# 4. Indítás
if __name__ == "__main__":
    # Elindítjuk a radart egy külön szálon (hogy ne akadjon össze a weboldallal)
    Thread(target=radar_motor, daemon=True).start()
    
    # Elindítjuk a weboldalt azon a porton, amit a Render ad nekünk
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
