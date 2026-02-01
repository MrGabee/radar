import os
import time
import requests
from flask import Flask
from threading import Thread

app = Flask(__name__)

# Fájlnév az adatok tárolásához
ADAT_FAJL = "waze_debug.txt"

# Állapot infó a weboldalhoz
radar_status = {
    "ido": "Indítás...",
    "info": "Radar inicializálása...",
    "nyers_hossz": 0
}

def radar_motor():
    global radar_status
    # Stabil GeoRSS URL Budapest koordinátáival
    waze_url = "https://www.waze.com/row-rtserver/web/TGeoRSS?bottom=47.30&left=18.90&right=19.40&top=47.70"
    
    # Professzionális böngésző-imitáció (Headers)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Accept': 'text/xml,application/xml,application/xhtml+xml,text/html;q=0.9,*/*;q=0.8',
        'Referer': 'https://www.waze.com/hu/live-map/',
        'Accept-Language': 'hu-HU,hu;q=0.9,en-US;q=0.8,en;q=0.7'
    }

    while True:
        try:
            most = time.strftime('%H:%M:%S')
            # Próbáljuk meg elérni a Waze-t
            response = requests.get(waze_url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                adat = response.text
                
                # Mentés a fájlba a későbbi feldolgozáshoz
                with open(ADAT_FAJL, "w", encoding="utf-8") as f:
                    f.write(f"UTOLSÓ FRISSÍTÉS: {most}\n")
                    f.write("-" * 40 + "\n")
                    f.write(adat)
                
                radar_status['ido'] = most
                radar_status['info'] = "✅ MŰKÖDIK - Adatok betöltve"
                radar_status['nyers_hossz'] = len(adat)
                print(f"[{most}] Sikeres frissítés: {len(adat)} karakter.")
            else:
                radar_status['info'] = f"❌ Waze hiba: {response.status_code}"
                print(f"[{most}] Waze hiba: {response.status_code}")
                
        except Exception as e:
            radar_status['info'] = f"⚠️ Rendszerhiba: {str(e)}"
            print(f"Hiba: {e}")
        
        # 3 percenként nézünk rá az utakra
        time.sleep(180)

@app.route('/')
def home():
    # Vizuális visszajelzés: zöld ha jó, piros ha hiba
    status_color = "#27ae60" if "✅" in radar_status['info'] else "#e74c3c"
    
    return f"""
    <html>
    <head><title>Waze Radar</title></head>
    <body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f4f7f6; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0;">
        <div style="background: white; padding: 40px; border-radius: 25px; shadow: 0 10px 30px rgba(0,0,0,0.1); text-align: center; border-top: 8px solid {status_color};">
            <h1 style="color: #2c3e50; margin-bottom: 5px;">📡 Waze Radar Budapest</h1>
            <p style="color: #7f8c8d; margin-bottom: 30px;">Élő közlekedési adatgyűjtő</p>
            
            <div style="background: #f9f9f9; padding: 20px; border-radius: 15px; margin-bottom: 25px; text-align: left;">
                <p style="margin: 10px 0;"><b>Állapot:</b> <span style="color: {status_color};">{radar_status['info']}</span></p>
                <p style="margin: 10px 0;"><b>Utolsó mérés:</b> {radar_status['ido']}</p>
                <p style="margin: 10px 0;"><b>Adatmennyiség:</b> {radar_status['nyers_hossz']} karakter</p>
            </div>
            
            <a href="/debug" style="display: block; text-decoration: none; background: #3498db; color: white; padding: 15px; border-radius: 10px; font-weight: bold; transition: 0.3s;">NYERS ADATOK MEGTEKINTÉSE</a>
            <p style="font-size: 0.8em; color: #bdc3c7; margin-top: 20px;">A radar 3 percenként automatikusan frissít.</p>
        </div>
    </body>
    </html>
    """

@app.route('/debug')
def debug():
    if os.path.exists(ADAT_FAJL):
        with open(ADAT_FAJL, "r", encoding="utf-8") as f:
            tartalom = f.read()
        return f"<html><body style='background: #1e1e1e; color: #00ff00; padding: 20px; font-family: monospace;'><pre>{tartalom}</pre></body></html>"
    return "Még nincs adat. Várj pár másodpercet az első lekérésig..."

if __name__ == "__main__":
    # Motor indítása
    Thread(target=radar_motor, daemon=True).start()
    
    # Port beállítása a Render környezethez
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
