import requests

def get_city_from_coordinates(lat, lon):
    url = (
        f"https://nominatim.openstreetmap.org/reverse"
        f"?lat={lat}&lon={lon}&format=json"
    )

    headers = {
        "User-Agent": "TourismPlatform/1.0"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()

        address = data.get("address", {})

        return (
              address.get("city")
              or address.get("state_district")
              or address.get("county")
              or address.get("town")
              or address.get("village")
        )

    return None