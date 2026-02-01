import requests
import time
import os
from flask import Flask
from threading import Thread

# --- 1. ADATOK TÁROLÁSA (Memória a weboldalnak) ---
radar_status = {
    "utolso_frissites": "Indítás...",
    "esemenyek": []
}

app = Flask(__name__)

@app.route('/')
def home():
    # Ez a weboldal kinézete a böngészőben
    html = f"""
    <html>
    <head>
        <title>Waze Radar Élő</title>
        <meta http-equiv="refresh" content="60">
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; background-color: #f4f4f9; }}
            .card {{ background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
            h1 {{ color: #2c3e50; }}
            .time {{ color: #7f8c8d; font-size: 0.9em; }}
            ul {{ list-style-type: none; padding: 0; }}
            li {{ background: #fff; margin-bottom: 10px; padding: 10px; border-left: 5px solid #3498db; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }}
        </style>
    </head>
    <body>
        <div class="card">
            <h1>📡 Waze Radar Budapest</h1>
            <p class="time"><b>Utolsó pásztázás:</b> {radar_status['utolso_frissites']}</p>
            <hr>
            <h3>Aktuális balesetek / események:</h3>
            <ul>
    """
    if not radar_status['esemenyek']:
        html += "<li>Jelenleg nincs rögzített esemény, vagy a rendszer még dolgozik...</li>"
    else:
        for inc in radar_status['esemenyek']:
            html += f"<li>{inc}</li>"
    
    html += """
            </ul>
            <p style="font-size: 0.8em; color: gray; margin-top: 20px;">
                Az oldal percenként frissül. A radar 15 percenként pásztáz.
            </p>
        </div>
    </body>
    </html>
    """
    return html

def run_web():
    # A Rendernek kötelező a port kezelése
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- 2. A RADAR LOGIKÁJA ---
def radar_loop():
    global radar_status
    print("🚀 Radar folyamat elindítva...")
    
    while True:
        try:
            current_time = time.strftime('%H:%M:%S')
            print(f"🔍 Pásztázás indítása: {current_time}")
            
            # --- Ide jön a te Waze API lekérdező kódod ---
            # Példa adatok (ezt a részedet ide másold be):
            # talalatok = waze_lekerdezes() 
            
            # Frissítjük a weboldal adatait
            radar_status['utolso_frissites'] = current_time
            # radar_status['esemenyek'] = talalatok (ide kerülnek a valódi adatok)
            
            print("⏳ Várakozás 15 percet a következő frissítésig...")
            time.sleep(900)
            
        except Exception as e:
            print(f"❌ Hiba a radarban: {e}")
            time.sleep(60)

# --- 3. INDÍTÁS ---
if __name__ == "__main__":
    # FONTOS: Előbb a Weboldal szálat indítjuk, hogy a Render azonnal lássa!
    print("🌐 Weboldal indítása...")
    t = Thread(target=run_web)
    t.daemon = True
    t.start()
    
    # Utána jöhet a végtelenített radar loop
    radar_loop()
