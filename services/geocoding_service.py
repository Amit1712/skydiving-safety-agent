import os
from typing import Any

from dotenv import load_dotenv

from services.http_client import APIError, HttpClient

load_dotenv()
GEOCODING_BASE_URL = os.getenv("GEOCODING_BASE_URL")
client = HttpClient(GEOCODING_BASE_URL)


def get_coordinates_by_name(location_name: str) -> dict[str, Any]:
    """Get the coordinates for a given location name."""
    params = {"name": location_name, "count": 1, "language": "en", "format": "json"}

    data = client.get(GEOCODING_BASE_URL, params=params)
    results = data.get("results")

    if not results or len(results) == 0:
        raise APIError(
            f"No coordinates found for location: '{location_name}'", status_code=404
        )

    top_result = results[0]
    return {
        "location_name": top_result.get("name"),
        "country": top_result.get("country"),
        "latitude": top_result.get("latitude"),
        "longitude": top_result.get("longitude"),
    }
