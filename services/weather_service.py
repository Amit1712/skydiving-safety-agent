import os
from typing import Any

from dotenv import load_dotenv

from services.http_client import HttpClient

load_dotenv()

OPEN_METEO_BASE_URL = os.getenv("OPEN_METEO_BASE_URL")
client = HttpClient(OPEN_METEO_BASE_URL)


def get_weather(latitude: float, longitude: float) -> dict[str, Any]:
    """Get the weather for a given latitude and longitude."""
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m,wind_speed_10m,wind_gusts_10m",
        "wind_speed_unit": "kmh",
    }
    data = client.get(OPEN_METEO_BASE_URL, params=params)
    current = data.get("current", {})
    return {
        "temperature_c": current.get("temperature_2m"),
        "wind_speed_kmh": current.get("wind_speed_10m"),
        "wind_gusts_kmh": current.get("wind_gusts_10m"),
        "units": "km/h",
    }
