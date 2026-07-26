from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache
import re
import time

time.sleep(0.2)
import requests


WIKIPEDIA_API_URL = "https://en.wikipedia.org/w/api.php"
REQUEST_HEADERS = {
    "User-Agent": "TrailSite/1.0 (tourism project; image lookup)"
}
IGNORED_WORDS = {"a", "an", "and", "at", "hotel", "of", "resort", "the"}


def _is_relevant_result(name: str, page_title: str) -> bool:
    """Avoid assigning a city or list-page image to an unrelated place."""
    words = {
        word for word in re.findall(r"[a-z0-9]+", name.lower())
        if len(word) > 2 and word not in IGNORED_WORDS
    }
    title_words = set(re.findall(r"[a-z0-9]+", page_title.lower()))
    if not words:
        return False
    required_matches = max(1, (len(words) + 1) // 2)
    return len(words & title_words) >= required_matches


def find_place_image(name: str, city_name: str, _kind: str) -> str:
    """Return the best Wikipedia thumbnail for a named place or activity."""
    # The actual name and city produce more accurate results than generic
    # qualifiers such as "hotel", which can pull in unrelated list pages.
    query = f"{name} {city_name}"
    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": query,
        "gsrnamespace": 0,
        "gsrlimit": 3,
        "prop": "pageimages",
        "piprop": "thumbnail",
        "pithumbsize": 800,
        "format": "json",
        "formatversion": 2,
        "origin": "*",
    }

    try:
        response = requests.get(
            WIKIPEDIA_API_URL,
            params=params,
            headers=REQUEST_HEADERS,
            timeout=6,
        )
        response.raise_for_status()
        pages = response.json().get("query", {}).get("pages", [])
        for page in pages:
            image_url = page.get("thumbnail", {}).get("source")
            if image_url and _is_relevant_result(name, page.get("title", "")):
                return image_url
    except (requests.RequestException, ValueError) as exc:
        print(f"[Wikipedia Images] {name}: {exc}")

    return ""


@lru_cache(maxsize=16)
def find_fallback_image(topic: str) -> str:
    """Return a reusable generic image for cards without an exact match."""
    params = {
        "action": "query",
        "titles": topic,
        "prop": "pageimages",
        "piprop": "thumbnail",
        "pithumbsize": 800,
        "format": "json",
        "formatversion": 2,
        "origin": "*",
    }
    try:
        response = requests.get(
            WIKIPEDIA_API_URL,
            params=params,
            headers=REQUEST_HEADERS,
            timeout=6,
        )
        response.raise_for_status()
        pages = response.json().get("query", {}).get("pages", [])
        if pages:
            return pages[0].get("thumbnail", {}).get("source", "")
    except (requests.RequestException, ValueError) as exc:
        print(f"[Wikipedia Fallback Image] {topic}: {exc}")
    return ""


def _fallback_topic(item, kind: str) -> str:
    if kind == "hotel accommodation":
        return "Hotel"
    return {
        "outdoor-adventure": "Outdoor recreation",
        "mindfulness": "Meditation",
        "sports": "Sport",
        "entertainment": "Entertainment",
        "nature": "Nature",
    }.get(getattr(item, "category", ""), "Recreation")


def populate_missing_images(items, city_name: str, kind: str, limit: int = 30):
    """
    Look up a small batch of missing images in parallel and persist successes.
    Existing image URLs are never replaced.
    """
    missing = [item for item in items if not item.image_url][:limit]
    if not missing:
        return items

    with ThreadPoolExecutor(max_workers=min(8, len(missing))) as executor:
        image_urls = list(executor.map(
            lambda item: find_place_image(item.name, city_name, kind),
            missing,
        ))

    for item, image_url in zip(missing, image_urls):
        if image_url:
            item.image_url = image_url
            item.save(update_fields=["image_url"])

    # Keep generic fallbacks transient. They make every card complete without
    # storing a generic photo as though it belonged to a specific business.
    for item in items:
        if not item.image_url:
            item.image_url = find_fallback_image(_fallback_topic(item, kind))

    return items
