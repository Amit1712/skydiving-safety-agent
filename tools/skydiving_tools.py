import json

from services.geocoding_service import get_coordinates_by_name
from services.http_client import APIError
from services.weather_service import get_weather


def get_dz_coordinates_tool(location_name: str) -> str:
    """Find latitude and longitude coordinates for a dropzone or location name."""
    try:
        result = get_coordinates_by_name(location_name)
        return json.dumps({"status": "success", "data": result})

    except APIError as e:
        return json.dumps(
            {
                "status": "error",
                "error_type": "LOCATION_NOT_FOUND",
                "message": f"Could not find coordinates for '{location_name}': {e!s}",
                "suggestion": "Ask the user to clarify the dropzone or city name.",
            }
        )


def get_weather_and_wind_tool(latitude: float, longitude: float) -> str:
    """Fetch current weather, wind speed, and gusts for a given latitude and longitude."""
    try:
        result = get_weather(latitude, longitude)
        return json.dumps({"status": "success", "data": result})
    except APIError as e:
        return json.dumps(
            {"status": "error", "message": f"Could not retrieve weather data: {e!s}"}
        )


def get_aff_student_safety_limits_tool() -> str:
    """Get safety and wind limits specifically for AFF skydiving students."""
    return json.dumps(
        {
            "status": "success",
            "data": {
                "max_allowed_wind_speed_kmh": 25,
                "max_allowed_gusts_kmh": 30,
                "note": "Students are strictly forbidden from jumping if limits are exceeded.",
            },
        }
    )


TOOLS_MAP = {
    "get_dz_coordinates_tool": get_dz_coordinates_tool,
    "get_weather_and_wind_tool": get_weather_and_wind_tool,
    "get_aff_student_safety_limits_tool": get_aff_student_safety_limits_tool,
}

TOOLS_LIST = [
    get_dz_coordinates_tool,
    get_weather_and_wind_tool,
    get_aff_student_safety_limits_tool,
]
