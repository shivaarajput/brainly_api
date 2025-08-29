from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import cloudscraper
import asyncio
from concurrent.futures import ThreadPoolExecutor
import time

BASE_URL = "https://brainly.in"  # target site

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create a cloudscraper session
scraper = cloudscraper.create_scraper(
    browser={
        "browser": "chrome",
        "platform": "windows",
        "mobile": False
    }
)

# Thread pool for running blocking calls
executor = ThreadPoolExecutor(max_workers=10)


def get_with_retries(url: str, retries: int = 3, delay: int = 2):
    """Blocking request with retries and browser-like headers"""
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/116.0 Safari/537.36"
        ),
        "Accept": "application/json,text/html;q=0.9",
        "Accept-Language": "en-US,en;q=0.9",
    }

    for attempt in range(1, retries + 1):
        try:
            resp = scraper.get(url, headers=headers, timeout=15)
            if resp.status_code == 200:
                return resp
            else:
                print(f"Attempt {attempt}: got status {resp.status_code}")
        except Exception as e:
            print(f"Attempt {attempt} failed: {e}")
        time.sleep(delay)

    raise Exception(f"Failed to fetch {url} after {retries} attempts")


async def fetch_json_or_html(url: str):
    """Run blocking scraper inside thread pool and return JSON if possible, else HTML"""
    loop = asyncio.get_event_loop()
    try:
        response = await loop.run_in_executor(executor, lambda: get_with_retries(url))
        try:
            return response.json()  # if JSON available
        except Exception:
            return {"html": response.text}  # fallback: raw HTML
    except Exception as e:
        return {"error": str(e)}


@app.get("/{full_path:path}")
async def proxy(full_path: str, request: Request):
    """Forward any path to BASE_URL"""
    query_string = request.url.query
    target_url = f"{BASE_URL}/{full_path}"
    if query_string:
        target_url += f"?{query_string}"

    return await fetch_json_or_html(target_url)
