from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_GET

from .forms import ContactMessageForm
from .models import City, State, Country, TouristAttraction, Accommodation, Activity, ContactInfo
from .services.location_service import get_city_from_coordinates
from .services.attraction_service import get_attractions_from_api
from .services.accommodation_service import get_accommodations_from_api
from .services.activity_service import get_activities_from_api, save_activities
from .services.city_service import get_city_description


# ─────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────

def _get_or_create_city(city_name, lat, lon):
    city = City.objects.filter(name__iexact=city_name).first()
    if city:
        return city
    country, _ = Country.objects.get_or_create(code="XX", defaults={"name": "Unknown"})
    state, _   = State.objects.get_or_create(country=country, name="Unknown")
    return City.objects.create(state=state, name=city_name, latitude=lat, longitude=lon)


CATEGORY_MAP = {
    "beach": "Beach", "park": "Park", "national": "Park",
    "religion": "Temple", "museum": "Museum", "monument": "Monument",
    "hill": "Hill", "lake": "Lake", "adventure": "Adventure",
    "historical": "Historical", "heritage": "Historical",
}

def _map_category(categories):
    for cat in categories:
        for key, val in CATEGORY_MAP.items():
            if key in cat.lower():
                return val
    return "Other"


def _remove_attraction_duplicates(city, activities):
    """Prevent the same place appearing in both Attractions and Activities."""
    attraction_names = {
        n.casefold()
        for n in TouristAttraction.objects.filter(city=city).values_list("name", flat=True)
    }
    return [a for a in activities if a.name.casefold() not in attraction_names]


def _save_attractions(city, features):
    saved = []
    for f in features:
        props  = f.get("properties", {})
        name   = props.get("name", "").strip()
        if not name:
            continue
        coords = f.get("geometry", {}).get("coordinates", [0, 0])
        obj, _ = TouristAttraction.objects.get_or_create(
            city=city, name=name,
            defaults={
                "external_id": props.get("place_id", ""),
                "source":      "Geoapify",
                "category":    _map_category(props.get("categories", [])),
                "description": props.get("formatted", ""),
                "latitude":    coords[1],
                "longitude":   coords[0],
                "address":     props.get("formatted", ""),
            },
        )
        saved.append(obj)
    return saved


def _save_accommodations(city, features):
    saved = []
    for f in features:
        props   = f.get("properties", {})
        name    = props.get("name", "").strip()
        if not name:
            continue
        coords  = f.get("geometry", {}).get("coordinates", [None, None])
        contact = props.get("contact", {}) if isinstance(props.get("contact"), dict) else {}
        obj, created = Accommodation.objects.get_or_create(
            city=city, name=name,
            defaults={
                "external_id": props.get("place_id", ""),
                "address":     props.get("formatted", ""),
                "latitude":    coords[1],
                "longitude":   coords[0],
                "phone":       contact.get("phone", ""),
                "website":     props.get("website", ""),
            },
        )
        if not created and (obj.latitude is None or obj.longitude is None):
            obj.latitude  = coords[1]
            obj.longitude = coords[0]
            obj.save(update_fields=["latitude", "longitude"])
        saved.append(obj)
    return saved


# ─────────────────────────────────────────────────────────────
# Page views
# ─────────────────────────────────────────────────────────────

def home(request):
    city_name = request.session.get("city_name", "")
    contact_info = ContactInfo.objects.first()
    contact_form = ContactMessageForm()

    if request.method == "POST":
        contact_form = ContactMessageForm(request.POST)
        if contact_form.is_valid():
            contact_form.save()
            messages.success(request, "Thank you for your message! We will get back to you soon.")
            return redirect("/#contact-us")

    return render(request, "index.html", {
        "city_name": city_name,
        "contact_info": contact_info,
        "contact_form": contact_form,
    })


def activity_detail(request, slug):
    activity = get_object_or_404(Activity, slug=slug)
    return render(request, "activity_detail.html", {"activity": activity})


def beaches(request):
    return render(request, "beaches.html")


def parks(request):
    return render(request, "parks.html")


def rkbeach(request):
    return render(request, "components/rk-beach.html")


def vudapark(request):
    return render(request, "components/vuda-park.html")


# ─────────────────────────────────────────────────────────────
# AJAX endpoints  (called by JS)
# ─────────────────────────────────────────────────────────────

@require_GET
def detect_location(request):
    """Reverse-geocodes lat/lon via Nominatim and saves city to session."""
    lat = request.GET.get("lat")
    lon = request.GET.get("lon")

    if not lat or not lon:
        return JsonResponse({"error": "Missing lat/lon"}, status=400)
    try:
        lat, lon = float(lat), float(lon)
    except ValueError:
        return JsonResponse({"error": "Invalid coordinates"}, status=400)

    city_name = get_city_from_coordinates(lat, lon)
    if city_name:
        request.session["city_name"] = city_name
        request.session["lat"]       = lat
        request.session["lon"]       = lon

    return JsonResponse({"city": city_name})


@require_GET
def api_attractions(request):
    """DB-first → Geoapify fallback."""
    city_name = request.session.get("city_name")
    lat       = request.session.get("lat")
    lon       = request.session.get("lon")

    if not city_name or lat is None or lon is None:
        return JsonResponse({"attractions": [], "source": "no_location"})

    city = City.objects.filter(name__iexact=city_name).first()
    if city:
        rows = list(TouristAttraction.objects.filter(city=city).values(
            "id", "name", "category", "description", "address",
            "rating", "latitude", "longitude"
        ))
        if rows:
            return JsonResponse({"attractions": rows, "source": "database"})

    features = get_attractions_from_api(lat, lon)
    if not features:
        return JsonResponse({"attractions": [], "source": "api_empty"})

    city   = _get_or_create_city(city_name, lat, lon)
    saved  = _save_attractions(city, features)
    result = [
        {"id": a.id, "name": a.name, "category": a.category,
         "description": a.description, "address": a.address,
         "rating": a.rating, "latitude": a.latitude, "longitude": a.longitude}
        for a in saved
    ]
    return JsonResponse({"attractions": result, "source": "api"})


@require_GET
def api_accommodations(request):
    """DB-first → Geoapify fallback."""
    city_name = request.session.get("city_name")
    lat       = request.session.get("lat")
    lon       = request.session.get("lon")

    if not city_name or lat is None or lon is None:
        return JsonResponse({"accommodations": [], "source": "no_location"})

    city = City.objects.filter(name__iexact=city_name).first()
    if city:
        accommodations = list(Accommodation.objects.filter(city=city))
        # Backfill coordinates if any record is missing them
        if accommodations and any(a.latitude is None for a in accommodations):
            features = get_accommodations_from_api(lat, lon)
            if features:
                _save_accommodations(city, features)
                accommodations = list(Accommodation.objects.filter(city=city))

        rows = []
        for a in accommodations:
            rows.append({
                "id":        a.pk,
                "name":      a.name,
                "address":   a.address,
                "rating":    a.rating,
                "phone":     a.phone,
                "website":   a.website,
                "latitude":  a.latitude,
                "longitude": a.longitude,
            })
        if rows:
            return JsonResponse({
                "accommodations": rows, "source": "database",
                "center": {"latitude": lat, "longitude": lon},
            })

    features = get_accommodations_from_api(lat, lon)
    if not features:
        return JsonResponse({"accommodations": [], "source": "api_empty"})

    city  = _get_or_create_city(city_name, lat, lon)
    saved = _save_accommodations(city, features)
    result = [
        {"id": a.id, "name": a.name, "address": a.address,
         "rating": a.rating, "phone": a.phone, "website": a.website,
         "latitude": a.latitude, "longitude": a.longitude}
        for a in saved
    ]
    return JsonResponse({
        "accommodations": result, "source": "api",
        "center": {"latitude": lat, "longitude": lon},
    })


@require_GET
def api_activities(request):
    """DB-first → Geoapify fallback."""
    city_name = request.session.get("city_name")
    lat       = request.session.get("lat")
    lon       = request.session.get("lon")

    if not city_name or lat is None or lon is None:
        return JsonResponse({"activities": [], "source": "no_location"})

    city = City.objects.filter(name__iexact=city_name).first()
    if city:
        activities = _remove_attraction_duplicates(
            city, list(Activity.objects.filter(city=city))
        )
        rows = [
            {"id": a.pk, "name": a.name, "slug": a.slug,
             "category": a.category, "image_url": a.image_url or "",
             "description": a.description}
            for a in activities
        ]
        if rows:
            return JsonResponse({"activities": rows, "source": "database"})

    features = get_activities_from_api(lat, lon)
    if not features:
        features = get_activities_from_api(lat, lon, radius=15000)
    if not features:
        return JsonResponse({"activities": [], "source": "api_empty"})

    city  = _get_or_create_city(city_name, lat, lon)
    saved = _remove_attraction_duplicates(city, save_activities(city, features))
    result = [
        {"id": a.id, "name": a.name, "slug": a.slug,
         "category": a.category, "image_url": a.image_url or "",
         "description": a.description}
        for a in saved
    ]
    return JsonResponse({"activities": result, "source": "api"})


@require_GET
def api_city_description(request):
    """Returns Wikipedia summary + image for the detected city."""
    city_name = request.session.get("city_name")

    if not city_name:
        return JsonResponse({"summary": "", "image_url": "", "wiki_url": ""})

    cached = request.session.get("city_description")
    if cached and request.session.get("city_description_for") == city_name:
        return JsonResponse(cached)

    data = get_city_description(city_name)
    if data.get("summary"):
        request.session["city_description"]     = data
        request.session["city_description_for"] = city_name

    return JsonResponse(data)
