import json

from services.aviation_weather_service import get_aviation_weather
from services.daylight_service import get_daylight_times, is_within_daylight
from services.geocoding_service import get_coordinates_by_name
from services.http_client import APIError
from services.vmc_service import check_vmc_conditions
from services.weather_service import get_hourly_forecast, get_weather


def _error_response(message: str, error_type: str = "API_ERROR") -> str:
    return json.dumps({"status": "error", "error_type": error_type, "message": message})


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
    """Fetch current weather, wind speed (km/h and knots), and gusts for given coordinates."""
    try:
        result = get_weather(latitude, longitude)
        return json.dumps({"status": "success", "data": result})
    except APIError as e:
        return _error_response(f"Could not retrieve weather data: {e!s}")


def get_hourly_forecast_tool(
    latitude: float, longitude: float, jump_datetime: str
) -> str:
    """
    Fetch hourly weather forecast for a specific jump time.
    jump_datetime: ISO format like '2026-09-26T15:00' (local time at dropzone).
    """
    try:
        result = get_hourly_forecast(latitude, longitude, jump_datetime)
        return json.dumps({"status": "success", "data": result})
    except APIError as e:
        return _error_response(f"Could not retrieve hourly forecast: {e!s}")


def get_aviation_weather_tool(latitude: float, longitude: float) -> str:
    """Fetch METAR and TAF from the nearest aviation weather station to the dropzone."""
    try:
        result = get_aviation_weather(latitude, longitude)
        return json.dumps({"status": "success", "data": result})
    except APIError as e:
        return _error_response(
            f"Could not retrieve aviation weather: {e!s}",
            error_type="AVIATION_WEATHER_UNAVAILABLE",
        )


def get_daylight_times_tool(
    latitude: float,
    longitude: float,
    target_date: str = "",
    timezone_name: str = "UTC",
) -> str:
    """
    Get sunrise, sunset, and civil twilight times for a dropzone on a given date.
    target_date: ISO date like '2026-09-26'. Defaults to today.
    timezone_name: IANA timezone like 'Asia/Jerusalem' or 'America/Chicago'.
    """
    try:
        date_arg = target_date if target_date else None
        result = get_daylight_times(latitude, longitude, date_arg, timezone_name)
        return json.dumps({"status": "success", "data": result})
    except APIError as e:
        return _error_response(f"Could not calculate daylight times: {e!s}")


def check_jump_daylight_tool(
    latitude: float,
    longitude: float,
    jump_datetime: str,
    timezone_name: str = "UTC",
) -> str:
    """
    Verify whether a planned jump time falls within civil daylight hours.
    jump_datetime: ISO format like '2026-09-26T15:00'.
    """
    try:
        result = is_within_daylight(
            latitude, longitude, jump_datetime, timezone_name
        )
        return json.dumps({"status": "success", "data": result})
    except APIError as e:
        return _error_response(f"Could not verify daylight: {e!s}")


def check_vmc_conditions_tool(latitude: float, longitude: float) -> str:
    """
    Check Visual Meteorological Conditions (VMC): cloud ceiling and visibility
    from nearest METAR against AFF student minimums.
    """
    try:
        result = check_vmc_conditions(latitude, longitude)
        return json.dumps({"status": "success", "data": result})
    except APIError as e:
        return _error_response(
            f"Could not check VMC conditions: {e!s}",
            error_type="VMC_CHECK_UNAVAILABLE",
        )


def get_aff_student_safety_limits_tool() -> str:
    """Get safety and wind limits specifically for AFF skydiving students."""
    return json.dumps(
        {
            "status": "success",
            "data": {
                "max_allowed_wind_speed_kmh": 25,
                "max_allowed_wind_speed_knots": 13.5,
                "max_allowed_gusts_kmh": 30,
                "max_allowed_gusts_knots": 16.2,
                "min_cloud_ceiling_ft_agl": 3000,
                "min_visibility_statute_miles": 3.0,
                "note": "Students are strictly forbidden from jumping if limits are exceeded.",
            },
        }
    )


TOOLS_MAP = {
    "get_dz_coordinates_tool": get_dz_coordinates_tool,
    "get_weather_and_wind_tool": get_weather_and_wind_tool,
    "get_hourly_forecast_tool": get_hourly_forecast_tool,
    "get_aviation_weather_tool": get_aviation_weather_tool,
    "get_daylight_times_tool": get_daylight_times_tool,
    "check_jump_daylight_tool": check_jump_daylight_tool,
    "check_vmc_conditions_tool": check_vmc_conditions_tool,
    "get_aff_student_safety_limits_tool": get_aff_student_safety_limits_tool,
}

TOOLS_LIST = list(TOOLS_MAP.values())
