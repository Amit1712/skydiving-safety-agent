from datetime import date, datetime
from typing import Any
from zoneinfo import ZoneInfo

from astral import LocationInfo
from astral.sun import dawn, dusk, sun

from services.http_client import APIError


def _parse_date(date_str: str | None) -> date:
    if not date_str:
        return datetime.now().date()
    try:
        return date.fromisoformat(date_str)
    except ValueError as exc:
        raise APIError(
            f"Invalid date format '{date_str}'. Use ISO format like '2026-09-26'.",
            status_code=400,
        ) from exc


def get_daylight_times(
    latitude: float,
    longitude: float,
    target_date: str | None = None,
    timezone_name: str = "UTC",
) -> dict[str, Any]:
    """
    Calculate sunrise, sunset, and civil twilight for a dropzone location.

    Civil twilight is used to verify jumps occur during daylight hours.
    """
    jump_date = _parse_date(target_date)

    try:
        tz = ZoneInfo(timezone_name)
    except Exception:
        tz = ZoneInfo("UTC")

    location = LocationInfo(
        name="dropzone",
        region="",
        timezone=timezone_name,
        latitude=latitude,
        longitude=longitude,
    )

    sun_times = sun(location.observer, date=jump_date, tzinfo=tz)
    civil_dawn = dawn(location.observer, date=jump_date, tzinfo=tz)
    civil_dusk = dusk(location.observer, date=jump_date, tzinfo=tz)

    return {
        "date": jump_date.isoformat(),
        "timezone": timezone_name,
        "sunrise_local": sun_times["sunrise"].isoformat(),
        "sunset_local": sun_times["sunset"].isoformat(),
        "civil_dawn_local": civil_dawn.isoformat(),
        "civil_dusk_local": civil_dusk.isoformat(),
        "daylight_window": {
            "start": civil_dawn.isoformat(),
            "end": civil_dusk.isoformat(),
            "note": "Jumps should occur between civil dawn and civil dusk for daylight ops.",
        },
    }


def is_within_daylight(
    latitude: float,
    longitude: float,
    jump_datetime: str,
    timezone_name: str = "UTC",
) -> dict[str, Any]:
    """Check whether a specific jump time falls within civil daylight hours."""
    try:
        normalized = jump_datetime.replace(" ", "T")
        jump_time = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise APIError(
            f"Invalid datetime format '{jump_datetime}'. Use ISO format like '2026-09-26T15:00'.",
            status_code=400,
        ) from exc

    tz = ZoneInfo(timezone_name)
    if jump_time.tzinfo is None:
        jump_time = jump_time.replace(tzinfo=tz)

    daylight = get_daylight_times(
        latitude, longitude, jump_time.date().isoformat(), timezone_name
    )

    civil_dawn = datetime.fromisoformat(daylight["civil_dawn_local"])
    civil_dusk = datetime.fromisoformat(daylight["civil_dusk_local"])

    is_daylight = civil_dawn <= jump_time <= civil_dusk

    return {
        **daylight,
        "jump_time_local": jump_time.isoformat(),
        "is_within_daylight": is_daylight,
        "verdict": "daylight" if is_daylight else "after_dark_or_before_dawn",
    }
