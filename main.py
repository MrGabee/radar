import requests
import time
from flask import Flask
from threading import Thread

# --- ADATOK TÁROLÁSA ---
last_update = "Még nem futott"
latest_incidents = []

app = Flask('')

@app.route('/')
def home():
    # Ez az, amit a böngészőben látni fogsz
    html = f"<h1>Waze Radar ÉLŐ</h1>"
    html += f"<p><b>Utolsó frissítés:</b> {last_update}</p>"
    html += "<h2>Legutóbbi találatok:</h2><ul>"
    
    if not latest_incidents:
        html += "<li>Nincs aktív esemény vagy még pörög a kereső...</li>"
    else:
        for inc in latest_incidents:
            html += f"<li>{inc}</li>"
    
    html += "</ul><p><i>Az oldal 15 percenként frissül automatikusan a háttérben.</i></p>"
    return html

def run_web():
    app.run(host='0.0.0.0', port=10000)

def radar_logic():
    global last_update, latest_incidents
    while True:
        try:
            current_time = time.strftime('%H:%M:%S')
            print(f"🔍 Pásztázás: {current_time}")
            
            # --- Ide jön a Waze lekérdező részed ---
            # Példa: tegyük fel, hogy 'talalatok' a lista, amit a Waze-ből kapsz
            # Ezt a részt a saját kódoddal kell összehangolni!
            
            # TESZT ADATOK (hogy lásd, működik):
            last_update = current_time
            latest_incidents = ["Baleset az M0-son", "Útmunkálatok a Váci úton"] 
            
            time.sleep(900)
        except Exception as e:
            print(f"Hiba: {e}")
            time.sleep(60)

if __name__ == "__main__":
    server_thread = Thread(target=run_web)
    server_thread.start()
    radar_logic()
