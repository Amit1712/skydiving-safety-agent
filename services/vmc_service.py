from typing import Any

from services.aviation_weather_service import get_metar_near_location
from services.http_client import APIError
from services.safety_rules_service import get_safety_limits, get_vmc_minimums


def check_vmc_conditions(
    latitude: float,
    longitude: float,
    license_type: str | None = None,
    dropzone_id: str | None = None,
    dropzone_name: str | None = None,
) -> dict[str, Any]:
    """
    Evaluate Visual Meteorological Conditions (VMC) using nearest METAR.

    Checks cloud ceiling and visibility against license- and dropzone-specific minimums.
    Defaults to AFF student regulations when no license is specified.
    """
    metar = get_metar_near_location(latitude, longitude)
    safety_context = get_safety_limits(license_type, dropzone_id, dropzone_name)
    minimums = get_vmc_minimums(license_type, dropzone_id, dropzone_name)

    min_ceiling = minimums["min_cloud_ceiling_ft_agl"]
    min_visibility = minimums["min_visibility_statute_miles"]

    ceiling_ft = metar.get("cloud_ceiling_ft_agl")
    visibility_sm = metar.get("visibility_sm")

    ceiling_ok = ceiling_ft is None or ceiling_ft >= min_ceiling
    visibility_ok = visibility_sm is None or visibility_sm >= min_visibility

    issues = []
    if ceiling_ft is not None and not ceiling_ok:
        issues.append(
            f"Cloud ceiling {ceiling_ft} ft AGL is below minimum {min_ceiling} ft AGL"
        )
    if visibility_sm is not None and not visibility_ok:
        issues.append(
            f"Visibility {visibility_sm} SM is below minimum {min_visibility} SM"
        )

    flight_category = metar.get("flight_category")
    if flight_category in {"IFR", "LIFR"}:
        issues.append(f"Flight category is {flight_category} (below VFR minimums)")

    vmc_ok = ceiling_ok and visibility_ok and flight_category not in {"IFR", "LIFR"}

    return {
        "vmc_ok": vmc_ok,
        "flight_category": flight_category,
        "cloud_ceiling_ft_agl": ceiling_ft,
        "visibility_sm": visibility_sm,
        "license": safety_context["license"],
        "license_label": safety_context["license_label"],
        "license_note": safety_context["license_note"],
        "dropzone_id": safety_context["dropzone_id"],
        "dropzone_name": safety_context["dropzone_name"],
        "dropzone_overrides_applied": safety_context["dropzone_overrides_applied"],
        "minimums": minimums,
        "issues": issues,
        "metar_summary": {
            "icao": metar.get("icao"),
            "station_name": metar.get("station_name"),
            "raw_metar": metar.get("raw_metar"),
        },
    }
