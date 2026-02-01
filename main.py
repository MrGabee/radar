import os
import time
from flask import Flask
from threading import Thread
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

app = Flask(__name__)
ADAT_FAJL = "waze_data.txt"
status = {"ido": "Indítás...", "info": "Böngésző indítása...", "meret": 0}

def waze_robot():
    global status
    url = "https://www.waze.com/row-rtserver/web/TGeoRSS?bottom=47.3&left=18.8&right=19.5&top=47.7"
    
    # Chrome beállítások a felhőhöz
    chrome_options = Options()
    chrome_options.add_argument("--headless") # Nincs ablak
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    while True:
        driver = None
        try:
            most = time.strftime('%H:%M:%S')
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Megnyitjuk a Waze-t, mintha emberek lennénk
            driver.get(url)
            time.sleep(5) # Várunk, hogy betöltsön az adat
            
            nyers_adat = driver.page_source
            
            if len(nyers_adat) > 200:
                with open(ADAT_FAJL, "w", encoding="utf-8") as f:
                    f.write(nyers_adat)
                status = {"ido": most, "info": "✅ SIKER (Böngészővel)", "meret": len(nyers_adat)}
            else:
                status["info"] = "❌ Üres válasz (Blokkolva?)"
                
        except Exception as e:
            status["info"] = f"⚠️ Hiba: {str(e)[:30]}"
        finally:
            if driver:
                driver.quit()
        
        time.sleep(600) # 10 perc pihenő, hogy ne legyen gyanús

@app.route('/')
def home():
    color = "#27ae60" if "✅" in status['info'] else "#e74c3c"
    return f"""
    <body style="font-family:sans-serif; text-align:center; background:#f4f7f6; padding:50px;">
        <div style="background:white; padding:40px; border-radius:20px; box-shadow:0 10px 30px rgba(0,0,0,0.1); display:inline-block; border-top:10px solid {color};">
            <h1>🛰️ Waze Stealth Radar</h1>
            <p>Állapot: <b style="color:{color}">{status['info']}</b></p>
            <p>Frissítve: {status['ido']}</p>
            <p>Adat: {status['meret']} karakter</p>
            <br><a href="/debug">Adatok megtekintése</a>
        </div>
    </body>
    """

@app.route('/debug')
def debug():
    if os.path.exists(ADAT_FAJL):
        with open(ADAT_FAJL, "r", encoding="utf-8") as f:
            return f"<pre>{f.read()}</pre>"
    return "Nincs adat."

if __name__ == "__main__":
    Thread(target=waze_robot, daemon=True).start()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
