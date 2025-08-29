from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import cloudscraper
import asyncio
from concurrent.futures import ThreadPoolExecutor

BASE_URL = "https://brainly.in/"  # The URL you want to scrape/forward requests to

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create a cloudscraper session
scraper = cloudscraper.create_scraper()

# Thread pool for running blocking calls
executor = ThreadPoolExecutor(max_workers=10)

async def fetch_json(url: str):
    """
    Runs cloudscraper.get in a thread pool to avoid blocking FastAPI
    """
    loop = asyncio.get_event_loop()
    try:
        response = await loop.run_in_executor(executor, lambda: scraper.get(url))
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}

@app.get("/{full_path:path}")
async def proxy(full_path: str, request: Request):
    """
    Forward the request to BASE_URL using cloudscraper
    """
    # Preserve query parameters
    query_string = request.url.query
    target_url = f"{BASE_URL}/{full_path}"
    if query_string:
        target_url += f"?{query_string}"

    return await fetch_json(target_url)
