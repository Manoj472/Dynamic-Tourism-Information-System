import requests
from urllib.parse import quote


def get_city_description(city_name: str) -> dict:
    """
    Fetch city summary from Wikipedia API — no API key needed.
    Returns dict with 'summary', 'image_url', 'wiki_url'.
    Falls back to empty strings on any error.
    """
    try:
        # Wikipedia REST API — returns plain-text summary + thumbnail
        encoded_city = quote(city_name.replace(" ", "_"), safe="")
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded_city}"
        r   = requests.get(url, timeout=8, headers={"User-Agent": "TourismPlatform/1.0"})
        r.raise_for_status()
        data = r.json()

        return {
            "summary":   data.get("extract", ""),
            "image_url": data.get("thumbnail", {}).get("source", ""),
            "wiki_url":  data.get("content_urls", {}).get("desktop", {}).get("page", ""),
        }

    except requests.RequestException as e:
        print(f"[Wikipedia City Description] {e}")
        return {"summary": "", "image_url": "", "wiki_url": ""}
