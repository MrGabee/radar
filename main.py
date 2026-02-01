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
    "info": "A radar éppen ébredezik, kérlek várj 1 percet!",
    "nyers_hossz": 0
}

def radar_motor():
    global radar_status
    # Frissített Budapest és környéke koordináták (szélesebb kör)
    waze_url = "https://www.waze.com/row-rtserver/web/TGeoRSS?bottom=47.16&left=18.65&right=19.48&top=47.72"
    
    # Emberi böngészőt utánzó fejlécek, hogy ne blokkoljon a Waze
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': '*/*',
        'Referer': 'https://www.waze.com/hu/live-map/'
    }

    while True:
        try:
            most = time.strftime('%Y-%m-%d %H:%M:%S')
            response = requests.get(waze_url, headers=headers, timeout=20)
            
            if response.status_code == 200:
                nyers_adat = response.text
                
                # Mentés TXT fájlba az online megtekintéshez
                with open(ADAT_FAJL, "w", encoding="utf-8") as f:
                    f.write(f"UTOLSÓ SIKERES FRISSÍTÉS: {most}\n")
                    f.write("=" * 40 + "\n")
                    f.write(nyers_adat)
                
                radar_status['ido'] = most
                radar_status['info'] = "✅ Kapcsolat OK - Adatok beérkeztek"
                radar_status['nyers_hossz'] = len(nyers_adat)
                print(f"[{most}] Radar sikeresen frissítve.")
            else:
                radar_status['info'] = f"❌ Waze hiba: {response.status_code}"
                print(f"[{most}] Hiba: {response.status_code}")
                
        except Exception as e:
            radar_status['info'] = f"⚠️ Rendszerhiba: {str(e)}"
            print(f"Hiba történt: {e}")
        
        # 5 percenként frissít (300 másodperc)
        time.sleep(300)

@app.route('/')
def home():
    return f"""
    <body style="font-family:sans-serif; padding:50px; background:#f4f7f6; color: #333;">
        <div style="max-width:700px; margin:auto; background:white; padding:40px; border-radius:20px; box-shadow: 0 10px 25px rgba(0,0,0,0.1);">
            <h1 style="color:#1a73e8; margin-bottom:10px;">📡 Waze Radar Budapest</h1>
            <div style="background:#e8f0fe; padding:15px; border-radius:10px; margin-bottom:20px;">
                <p style="margin:5px 0;"><b>Állapot:</b> {radar_status['info']}</p>
                <p style="margin:5px 0;"><b>Utolsó mérés:</b> {radar_status['ido']}</p>
                <p style="margin:5px 0;"><b>Adatméret:</b> {radar_status['nyers_hossz']} karakter</p>
            </div>
            <hr style="border:0; border-top:1px solid #eee; margin:20px 0;">
            <p>📂 <b>Nyers adatok ellenőrzése:</b></p>
            <a href="/debug" style="display:inline-block; background:#1a73e8; color:white; padding:12px 25px; border-radius:8px; text-decoration:none; font-weight:bold;">TXT fájl megnyitása</a>
            <p style="font-size:0.8em; color:#888; margin-top:20px;">A radar 5 percenként automatikusan frissül.</p>
        </div>
    </body>
    """

@app.route('/debug')
def debug_view():
    try:
        if os.path.exists(ADAT_FAJL):
            with open(ADAT_FAJL, "r", encoding="utf-8") as f:
                tartalom = f.read()
            return f"<html><body style='background:#1e1e1e; color:#00ff00; padding:20px;'><pre>{tartalom}</pre></body></html>"
        else:
            return "A fájl még nem jött létre. Várj kb. 30 másodpercet az első mérésig!"
    except Exception as e:
        return f"Hiba a fájl olvasásakor: {e}"

if __name__ == "__main__":
    # Radar indítása külön szálon
    t = Thread(target=radar_motor, daemon=True)
    t.start()
    
    # Port beállítása a Renderhez
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
