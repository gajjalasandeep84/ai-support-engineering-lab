# Fetches these 3 URLs concurrently using asyncio.gather:

##asyncio.to_thread approach (yours):
 # → runs sync HTTP call in separate thread
#  → threads run truly in parallel
#→ works with any sync library
#  → slightly more overhead per call

#httpx async approach (what I showed):
#  → truly async I/O — no threads
#  → single thread, event loop switches between waiting calls
#→ lower overhead, more scalable
#  → "proper" async HTTP


import asyncio
import httpx
import time

URLS = [
    "https://jsonplaceholder.typicode.com/todos/1",
    "https://jsonplaceholder.typicode.com/todos/2",
    "https://jsonplaceholder.typicode.com/todos/3",
]

async def fetch_todo(client: httpx.AsyncClient, url: str) -> dict:
    response = await client.get(url, timeout=10)
    response.raise_for_status()
    return response.json()

async def main():
    start = time.time()

    async with httpx.AsyncClient() as client:
        results = await asyncio.gather(
            *[fetch_todo(client, url) for url in URLS]
        )

    elapsed = time.time() - start

    for result in results:
        print(result["title"])

    print(f"Concurrent fetch: {elapsed:.2f}s")

asyncio.run(main())