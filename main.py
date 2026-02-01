import requests
import time
import os
 
def log_esemeny(szoveg):
    with open("balesetek_naplo.txt", "a", encoding="utf-8") as f:
        f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {szoveg}\n")

def lekerdezes(coords):
    url = "https://www.waze.com/live-map/api/georss"
    params = {
        "left": coords[0], "right": coords[1], "top": coords[2], "bottom": coords[3],
        "env": "row", "types": "alerts"
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Referer": "https://www.waze.com/hu/live-map/",
        "X-Requested-With": "XMLHttpRequest"
    }
    try:
        response = requests.get(url, params=params, headers=headers, timeout=15)
        return response.json().get('alerts', []) if response.status_code == 200 else []
    except:
        return []

def inditas():
    regiok = {
        "Budapest és környéke": [18.80, 19.50, 47.70, 47.20],
        "Dunántúl": [16.5, 18.5, 48.0, 46.5],
        "Alföld": [19.5, 22.0, 47.5, 46.0]
    }

    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"=== PROFESSZIONÁLIS RADAR: {time.strftime('%H:%M:%S')} ===")
        
        statisztika = {"ACCIDENT": 0, "POLICE": 0, "ROAD_CLOSED": 0, "POT_HOLE": 0}
        osszes_talalat = []

        for nev, coords in regiok.items():
            print(f" 🔍 Pásztázás: {nev}...", end="\r")
            alerts = lekerdezes(coords)
            
            for a in alerts:
                t = a.get('type')
                st = a.get('subtype', '')
                if t in ['ACCIDENT', 'POLICE', 'ROAD_CLOSED'] or 'POT_HOLE' in st:
                    ikon = "🚨" if t == 'ACCIDENT' else "👮" if t == 'POLICE' else "🚫" if t == 'ROAD_CLOSED' else "🕳️"
                    hely = f"{a.get('city', 'Vidéken')}, {a.get('street', 'út')}"
                    teljes_sor = f"{ikon} {t} | {hely} ({nev})"
                    
                    osszes_talalat.append(teljes_sor)
                    log_esemeny(teljes_sor)
                    
                    # Statisztika számolása
                    if t in statisztika: statisztika[t] += 1
                    if 'POT_HOLE' in st: statisztika["POT_HOLE"] += 1
            
            time.sleep(2)

        # EREDMÉNYEK KIÍRÁSA
        print("\n" + "="*55)
        print(f" 📊 ÖSSZESÍTETT STATISZTIKA (Ebben a körben):")
        print(f" 🚨 Balesetek: {statisztika['ACCIDENT']}")
        print(f" 👮 Rendőrök:  {statisztika['POLICE']}")
        print(f" 🚫 Lezárások: {statisztika['ROAD_CLOSED']}")
        print(f" 🕳️ Kátyúk:    {statisztika['POT_HOLE']}")
        print("-" * 55)
        print(f" ÖSSZESEN: {len(osszes_talalat)} fontos esemény.")
        print("="*55)

        print(f"\nKövetkező frissítés 15 perc múlva. A naplófájl bővült.")
        time.sleep(900)

if __name__ == "__main__":
    inditas()
