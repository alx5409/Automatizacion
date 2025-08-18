import asyncio
import httpx
import logging

# Configuramos el logging a nivel INFO
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

async def post_endpoint(url: str):
    logging.info(f"Iniciando POST en el endpoint: {url}")
    async with httpx.AsyncClient() as client:
        try:
            if "run-main-nima-vlc" in url:
                response = await client.post(url, json={"nif": "B45578069"})
            else:
                response = await client.post(url)
            logging.info(f"Respuesta del endpoint {url}: {response.status_code} - {response.json()}")
        except Exception as e:
            logging.error(f"Error al hacer POST a {url}: {e}")

async def main():
    base_url = "http://localhost:8000"
    endpoints = [f"{base_url}/run-main-nima-vlc", f"{base_url}/run-main-certificados"]
    tasks = [post_endpoint(url) for url in endpoints]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())