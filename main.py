import os
import time
import requests
from flask import Flask
from threading import Thread

app = Flask(__name__)

# A fájl neve, amibe a radar menteni fog
ADAT_FAJL = "waze_debug.txt"

# Memória az adatoknak a weboldalhoz
radar_status = {
    "ido": "Indítás...",
    "info": "A radar éppen ébredezik, kérlek várj 1 percet!"
}

def radar_motor():
    global radar_status
    # Budapest koordináták (Waze formátum)
    waze_url = "https://www.waze.com/row-rtserver/web/TGeoRSS?bottom=47.34&left=18.85&right=19.33&top=47.63"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

    while True:
        try:
            most = time.strftime('%Y-%m-%d %H:%M:%S')
            response = requests.get(waze_url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                nyers_adat = response.text
                
                # 1. ELMENTJÜK TXT FÁJLBA (hogy online is meg tudd nézni)
                with open(ADAT_FAJL, "w", encoding="utf-8") as f:
                    f.write(f"UTOLSÓ FRISSÍTÉS: {most}\n")
                    f.write("-" * 30 + "\n")
                    f.write(nyers_adat[:10000]) # Az első 10 ezer karaktert mentjük
                
                radar_status['ido'] = most
                radar_status['info'] = f"Sikeres lekérdezés! (Méret: {len(nyers_adat)} byte)"
                print(f"[{most}] Radar frissítve.")
            else:
                radar_status['info'] = f"Hiba a Waze szervertől: {response.status_code}"
        except Exception as e:
            radar_status['info'] = f"Rendszerhiba: {str(e)}"
        
        time.sleep(600) # 10 percenként frissít

# FŐOLDAL: Itt látod a státuszt
@app.route('/')
def home():
    return f"""
    <body style="font-family:sans-serif; padding:50px; background:#f4f7f6;">
        <div style="max-width:600px; margin:auto; background:white; padding:30px; border-radius:15px; box-shadow: 0 4px 10px rgba(0,0,0,0.1);">
            <h1 style="color:#1a73e8;">📡 Waze Radar Budapest</h1>
            <p><b>Állapot:</b> {radar_status['info']}</p>
            <p><b>Időpont:</b> {radar_status['ido']}</p>
            <hr>
            <p>📂 <b>Online TXT nézegető:</b> <a href="/debug" style="color:#1a73e8; font-weight:bold;">Kattints ide a nyers adatokért</a></p>
        </div>
    </body>
    """

# DEBUG OLDAL: Itt tudod megnézni a TXT tartalmát online
@app.route('/debug')
def debug_view():
    try:
        if os.path.exists(ADAT_FAJL):
            with open(ADAT_FAJL, "r", encoding="utf-8") as f:
                tartalom = f.read()
            return f"<html><body style='background:#1e1e1e; color:#00ff00; padding:20px;'><pre>{tartalom}</pre></body></html>"
        else:
            return "A fájl még nem jött létre. Várj a következő radar-körig!"
    except Exception as e:
        return f"Hiba a fájl olvasásakor: {e}"

if __name__ == "__main__":
    # Radar indítása külön szálon
    Thread(target=radar_motor, daemon=True).start()
    
    # Weboldal indítása a Render által kért porton
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
