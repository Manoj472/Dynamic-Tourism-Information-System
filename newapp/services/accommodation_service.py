import requests
from django.conf import settings

GEOAPIFY_URL = "https://api.geoapify.com/v2/places"


def get_accommodations_from_api(latitude, longitude, radius=5000, limit=20):
    """
    Fetch only real hotels/guest houses from Geoapify.
    Strict category list avoids restaurants, shops, etc.
    """
    params = {
        # Only genuine accommodation categories
        "categories": (
            "accommodation.hotel,"
            "accommodation.guest_house,"
            "accommodation.hostel,"
            "accommodation.motel,"
            "accommodation.resort"
        ),
        "filter": f"circle:{longitude},{latitude},{radius}",
        "bias":   f"proximity:{longitude},{latitude}",
        "limit":  limit,
        "apiKey": settings.GEOAPIFY_API_KEY,
    }
    try:
        r = requests.get(GEOAPIFY_URL, params=params, timeout=10)
        r.raise_for_status()
        features = r.json().get("features", [])

        # Extra guard: drop any feature whose name contains restaurant keywords
        EXCLUDE_KEYWORDS = [
            "restaurant", "cafe", "hotel restaurant", "food", "dhaba",
            "bar", "canteen", "mess", "kitchen", "bakery", "sweets"
        ]
        filtered = []
        for f in features:
            name = f.get("properties", {}).get("name", "").lower()
            if not any(kw in name for kw in EXCLUDE_KEYWORDS):
                filtered.append(f)

        return filtered

    except requests.RequestException as e:
        print(f"[Geoapify Accommodations] {e}")
        return []