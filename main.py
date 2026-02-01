import os
import time
from flask import Flask
from threading import Thread

app = Flask(__name__)

# Adatok tárolása
radar_status = {"ido": "Indítás...", "msg": "Szerver fut"}

@app.route('/')
def home():
    return f"<h1>Waze Radar</h1><p>Utolso frissites: {radar_status['ido']}</p>"

def radar_loop():
    global radar_status
    while True:
        radar_status['ido'] = time.strftime('%H:%M:%S')
        print(f"Radar frissitve: {radar_status['ido']}")
        time.sleep(900)

if __name__ == "__main__":
    # Figyelj, hogy a Thread és az app.run előtt pontosan 4 szóköz legyen!
    t = Thread(target=radar_loop, daemon=True)
    t.start()
    
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
