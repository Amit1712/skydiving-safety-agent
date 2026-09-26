import os
from typing import Any

from dotenv import load_dotenv

from services.conversions import kmh_to_knots
from services.http_client import APIError, HttpClient

load_dotenv()

CHECKWX_BASE_URL = os.getenv("CHECKWX_BASE_URL", "https://api.checkwx.com")
client = HttpClient(CHECKWX_BASE_URL)


def _get_api_key() -> str:
    api_key = os.getenv("CHECKWX_API_KEY")
    if not api_key:
        raise APIError(
            "CHECKWX_API_KEY is not configured. Sign up at https://www.checkwxapi.com/",
            status_code=503,
        )
    return api_key


def _checkwx_get(path: str) -> dict[str, Any]:
    headers = {"X-API-Key": _get_api_key(), "Accept": "application/json"}
    return client.get(f"{CHECKWX_BASE_URL}{path}", headers=headers)


def _extract_cloud_ceiling_ft(clouds: list[dict[str, Any]] | None) -> int | None:
    """Return the lowest broken/overcast cloud base in feet AGL."""
    if not clouds:
        return None

    ceiling_candidates = []
    for layer in clouds:
        code = (layer.get("code") or "").upper()
        base_ft = layer.get("base_feet_agl") or layer.get("base", {}).get("feet")
        if base_ft is None:
            continue
        if code in {"BKN", "OVC", "VV"} or layer.get("text", "").lower() in {
            "broken",
            "overcast",
            "vertical visibility",
        }:
            ceiling_candidates.append(int(base_ft))

    return min(ceiling_candidates) if ceiling_candidates else None


def _parse_metar_report(report: dict[str, Any]) -> dict[str, Any]:
    visibility = report.get("visibility") or {}
    clouds = report.get("clouds") or []
    wind = report.get("wind") or {}

    wind_speed_kmh = wind.get("speed_kmh")
    gust_kmh = (wind.get("gust") or {}).get("speed_kmh")

    return {
        "icao": report.get("icao") or (report.get("station") or {}).get("icao"),
        "station_name": (report.get("station") or {}).get("name"),
        "station_location": (report.get("station") or {}).get("location"),
        "observed_utc": report.get("observed"),
        "raw_metar": report.get("raw_text") or report.get("raw"),
        "flight_category": report.get("flight_category"),
        "visibility_sm": visibility.get("miles"),
        "visibility_m": visibility.get("meters"),
        "cloud_ceiling_ft_agl": _extract_cloud_ceiling_ft(clouds),
        "cloud_layers": [
            {
                "code": layer.get("code"),
                "text": layer.get("text"),
                "base_ft_agl": layer.get("base_feet_agl")
                or (layer.get("base") or {}).get("feet"),
            }
            for layer in clouds
        ],
        "wind_direction_deg": wind.get("degrees"),
        "wind_speed_kmh": wind_speed_kmh,
        "wind_gusts_kmh": gust_kmh,
        "wind_speed_knots": wind.get("speed_kts") or kmh_to_knots(wind_speed_kmh),
        "wind_gusts_knots": (wind.get("gust") or {}).get("speed_kts")
        or kmh_to_knots(gust_kmh),
        "temperature_c": (report.get("temperature") or {}).get("celsius"),
        "conditions": [
            condition.get("text") for condition in (report.get("conditions") or [])
        ],
    }


def get_metar_near_location(latitude: float, longitude: float) -> dict[str, Any]:
    """Fetch decoded METAR from the nearest aviation weather station."""
    path = f"/metar/lat/{latitude}/lon/{longitude}/decoded"
    data = _checkwx_get(path)

    reports = data.get("data") or []
    if not reports:
        raise APIError(
            f"No METAR data found near ({latitude}, {longitude})", status_code=404
        )

    parsed = _parse_metar_report(reports[0])
    station = reports[0].get("station") or {}
    position = station.get("position") or reports[0].get("position") or {}

    parsed["station_distance_nm"] = position.get("distance_nautical_miles") or position.get(
        "distance_nm"
    )
    parsed["station_bearing_deg"] = position.get("bearing_degrees") or position.get(
        "bearing_deg"
    )
    return parsed


def get_taf_near_location(latitude: float, longitude: float) -> dict[str, Any]:
    """Fetch decoded TAF from the nearest aviation weather station."""
    path = f"/taf/lat/{latitude}/lon/{longitude}/decoded"
    data = _checkwx_get(path)

    reports = data.get("data") or []
    if not reports:
        raise APIError(
            f"No TAF data found near ({latitude}, {longitude})", status_code=404
        )

    report = reports[0]
    station = report.get("station") or {}

    return {
        "icao": report.get("icao") or station.get("icao"),
        "station_name": station.get("name"),
        "station_location": station.get("location"),
        "issued_utc": report.get("issued") or report.get("timestamp"),
        "valid_from_utc": report.get("start_time") or report.get("valid_from"),
        "valid_to_utc": report.get("end_time") or report.get("valid_to"),
        "raw_taf": report.get("raw_text") or report.get("raw"),
        "forecast": report.get("forecast") or report.get("forecasts"),
    }


def get_aviation_weather(latitude: float, longitude: float) -> dict[str, Any]:
    """Fetch both METAR and TAF for the nearest station to a dropzone."""
    metar = get_metar_near_location(latitude, longitude)
    try:
        taf = get_taf_near_location(latitude, longitude)
    except APIError:
        taf = {"status": "unavailable", "message": "TAF not available for this station"}

    return {"metar": metar, "taf": taf}
