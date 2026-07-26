import requests
from django.conf import settings

GEOAPIFY_URL = "https://api.geoapify.com/v2/places"


def get_attractions_from_api(latitude, longitude, radius=5000, limit=20):
    """
    Fetch nearby tourist attractions from Geoapify Places API.
    Returns raw list of GeoJSON features, or [] on any error.
    """
    params = {
        "categories": (
            "tourism,tourism.attraction,entertainment,"
            "national_park,leisure.park,religion,"
            "tourism.sights,heritage,natural"
        ),
        "filter": f"circle:{longitude},{latitude},{radius}",
        "bias":   f"proximity:{longitude},{latitude}",
        "limit":  limit,
        "apiKey": settings.GEOAPIFY_API_KEY,
    }
    try:
        r = requests.get(GEOAPIFY_URL, params=params, timeout=10)
        r.raise_for_status()
        return r.json().get("features", [])
    except requests.RequestException as e:
        print(f"[Geoapify Attractions] {e}")
        return []