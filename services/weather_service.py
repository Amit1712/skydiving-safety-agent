import os
from datetime import datetime
from typing import Any

from dotenv import load_dotenv

from services.conversions import add_wind_knots
from services.http_client import APIError, HttpClient

load_dotenv()

OPEN_METEO_BASE_URL = os.getenv("OPEN_METEO_BASE_URL")
client = HttpClient(OPEN_METEO_BASE_URL)


def _format_wind_reading(current: dict[str, Any]) -> dict[str, Any]:
    data = {
        "temperature_c": current.get("temperature_2m"),
        "wind_speed_kmh": current.get("wind_speed_10m"),
        "wind_gusts_kmh": current.get("wind_gusts_10m"),
        "wind_direction_deg": current.get("wind_direction_10m"),
        "cloud_cover_percent": current.get("cloud_cover"),
        "visibility_m": current.get("visibility"),
        "units": {
            "wind_speed": "km/h",
            "wind_speed_alternate": "knots",
            "wind_gusts": "km/h",
            "wind_gusts_alternate": "knots",
            "temperature": "celsius",
        },
    }
    return add_wind_knots(data)


def get_weather(latitude: float, longitude: float) -> dict[str, Any]:
    """Get current weather for a given latitude and longitude."""
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": (
            "temperature_2m,wind_speed_10m,wind_gusts_10m,"
            "wind_direction_10m,cloud_cover,visibility"
        ),
        "wind_speed_unit": "kmh",
    }
    data = client.get(OPEN_METEO_BASE_URL, params=params)
    current = data.get("current", {})
    result = _format_wind_reading(current)
    result["observation_time"] = current.get("time")
    result["timezone"] = data.get("timezone")
    return result


def get_hourly_forecast(
    latitude: float,
    longitude: float,
    target_datetime: str,
) -> dict[str, Any]:
    """
    Get hourly forecast for a specific jump time.

    target_datetime: ISO 8601 string, e.g. '2026-09-26T15:00' or '2026-09-26 15:00'
    """
    try:
        normalized = target_datetime.replace(" ", "T")
        if "T" in normalized and len(normalized) == 16:
            parsed = datetime.fromisoformat(normalized)
        else:
            parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise APIError(
            f"Invalid datetime format '{target_datetime}'. Use ISO format like '2026-09-26T15:00'.",
            status_code=400,
        ) from exc

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": (
            "temperature_2m,wind_speed_10m,wind_gusts_10m,"
            "wind_direction_10m,cloud_cover,visibility,precipitation_probability"
        ),
        "wind_speed_unit": "kmh",
        "start_date": parsed.date().isoformat(),
        "end_date": parsed.date().isoformat(),
        "timezone": "auto",
    }
    data = client.get(OPEN_METEO_BASE_URL, params=params)
    hourly = data.get("hourly", {})
    times = hourly.get("time", [])

    target_hour = parsed.strftime("%Y-%m-%dT%H:00")
    if target_hour not in times:
        raise APIError(
            f"No hourly forecast available for {target_datetime}. "
            f"Available hours on {parsed.date().isoformat()}: {times}",
            status_code=404,
        )

    index = times.index(target_hour)
    reading = {
        "temperature_c": hourly["temperature_2m"][index],
        "wind_speed_kmh": hourly["wind_speed_10m"][index],
        "wind_gusts_kmh": hourly["wind_gusts_10m"][index],
        "wind_direction_deg": hourly["wind_direction_10m"][index],
        "cloud_cover_percent": hourly["cloud_cover"][index],
        "visibility_m": hourly["visibility"][index],
        "precipitation_probability_percent": hourly["precipitation_probability"][
            index
        ],
        "units": {
            "wind_speed": "km/h",
            "wind_speed_alternate": "knots",
            "wind_gusts": "km/h",
            "wind_gusts_alternate": "knots",
            "temperature": "celsius",
        },
    }
    result = add_wind_knots(reading)
    result["forecast_time"] = target_hour
    result["timezone"] = data.get("timezone")
    return result
