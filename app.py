from fastapi import FastAPI, Request
import cloudscraper

BASE_URL = "https://brainly.in"  # The URL you want to scrape/forward requests to

app = FastAPI()

# Create a cloudscraper session
scraper = cloudscraper.create_scraper(browser={
    'browser': 'chrome',
    'platform': 'windows',
    'mobile': False
})
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://brainly.in/",
}


@app.get("/{full_path:path}")
async def proxy(full_path: str, request: Request):
    """
    Forward the request to BASE_URL using cloudscraper
    """
    query_string = request.url.query
    target_url = f"{BASE_URL.rstrip('/')}/{full_path}"
    if query_string:
        target_url += f"?{query_string}"

    try:
        response = scraper.get(target_url, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}
