import requests
from django.conf import settings
from django.utils.text import slugify

GEOAPIFY_URL = "https://api.geoapify.com/v2/places"

# ── Geoapify category → our Activity.CATEGORY_CHOICES ────────
ACTIVITY_CATEGORY_MAP = {
    # outdoor-adventure
    "sport.water_sports":        "outdoor-adventure",
    "sport.climbing":            "outdoor-adventure",
    "sport.diving":              "outdoor-adventure",
    "sport.surfing":             "outdoor-adventure",
    "sport.cycling":             "outdoor-adventure",
    "leisure.playground":        "outdoor-adventure",
    "tourism.adventure":         "outdoor-adventure",
    "natural.beach":             "outdoor-adventure",
    "natural.cave":              "outdoor-adventure",

    # nature
    "natural":                   "nature",
    "national_park":             "nature",
    "leisure.park":              "nature",
    "leisure.nature_reserve":    "nature",
    "natural.forest":            "nature",
    "natural.waterfall":         "nature",
    "natural.mountain":          "nature",
    "natural.hot_spring":        "nature",

    # sports
    "sport":                     "sports",
    "sport.stadium":             "sports",
    "sport.swimming":            "sports",
    "sport.tennis":              "sports",
    "sport.golf":                "sports",
    "sport.fitness":             "sports",

    # mindfulness
    "religion":                  "mindfulness",
    "religion.temple":           "mindfulness",
    "religion.mosque":           "mindfulness",
    "religion.church":           "mindfulness",
    "leisure.spa":               "mindfulness",
    "leisure.yoga":              "mindfulness",
    "healthcare.meditation":     "mindfulness",

    # entertainment
    "entertainment":             "entertainment",
    "entertainment.cinema":      "entertainment",
    "entertainment.theme_park":  "entertainment",
    "entertainment.zoo":         "entertainment",
    "entertainment.aquarium":    "entertainment",
    "entertainment.museum":      "entertainment",
    "tourism.attraction":        "entertainment",
    "tourism.sights":            "entertainment",
    "commercial.shopping_mall":  "entertainment",
}

# Geoapify categories to request from the API
FETCH_CATEGORIES = (
    "sport,leisure.park,leisure.playground,leisure.spa,"
    "national_park,natural,religion,"
    "entertainment.cinema,entertainment.theme_park,"
    "entertainment.zoo,entertainment.aquarium,"
    "commercial.shopping_mall"
)


def _map_activity_category(categories: list) -> str:
    """
    Match the first Geoapify category string that exists in our map.
    Falls back to 'outdoor-adventure' if nothing matches.
    """
    for cat in categories:
        # Try exact match first
        if cat in ACTIVITY_CATEGORY_MAP:
            return ACTIVITY_CATEGORY_MAP[cat]
        # Try prefix match (e.g. "sport.cricket" → "sport")
        for key, value in ACTIVITY_CATEGORY_MAP.items():
            if cat.startswith(key):
                return value
    return "outdoor-adventure"


def get_activities_from_api(latitude: float, longitude: float,
                             radius: int = 5000, limit: int = 20) -> list:
    """
    Fetch nearby activity places from Geoapify Places API.
    Returns raw list of GeoJSON features, or [] on any error.
    """
    params = {
        "categories": FETCH_CATEGORIES,
        "filter":     f"circle:{longitude},{latitude},{radius}",
        "bias":       f"proximity:{longitude},{latitude}",
        "limit":      limit,
        "apiKey":     settings.GEOAPIFY_API_KEY,
    }
    try:
        r = requests.get(GEOAPIFY_URL, params=params, timeout=10)
        r.raise_for_status()
        return r.json().get("features", [])
    except requests.RequestException as e:
        print(f"[Geoapify Activities] {e}")
        return []


def save_activities(city, features: list) -> list:
    """
    Parse Geoapify GeoJSON features and save them as Activity records.
    Skips duplicates (get_or_create by city + name).
    Returns list of Activity instances.

    Import this in views.py:
        from .services.activity_service import get_activities_from_api, save_activities
    """
    # Import here to avoid circular imports
    from newapp.models import Activity

    saved = []
    seen_slugs = set()

    for f in features:
        props = f.get("properties", {})
        name  = props.get("name", "").strip()
        if not name:
            continue

        categories = props.get("categories", [])
        category   = _map_activity_category(categories)

        # Build a unique slug — append counter if collision
        base_slug = slugify(name)
        slug      = base_slug
        counter   = 1
        while (
            slug in seen_slugs
            or Activity.objects.filter(slug=slug).exclude(city=city).exists()
        ):
            slug = f"{base_slug}-{counter}"
            counter += 1
        seen_slugs.add(slug)

        obj, _ = Activity.objects.get_or_create(
            city=city,
            name=name,
            defaults={
                "slug":        slug,
                "category":    category,
                "description": props.get("formatted", ""),
                "image_url":   None,   # Geoapify doesn't return images; set via admin
            },
        )
        saved.append(obj)

    return saved
