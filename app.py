from flask import Flask, request, jsonify
import cloudscraper

BASE_URL = "https://brainly.in"  # The URL you want to scrape/forward requests to

app = Flask(__name__)

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


@app.route('/<path:full_path>', methods=["GET"])
def proxy(full_path):
    """
    Forward the request to BASE_URL using cloudscraper
    """
    query_string = request.query_string.decode("utf-8")
    target_url = f"{BASE_URL.rstrip('/')}/{full_path}"
    if query_string:
        target_url += f"?{query_string}"

    try:
        response = scraper.get(target_url, headers=headers)
        response.raise_for_status()
        return jsonify(response.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
