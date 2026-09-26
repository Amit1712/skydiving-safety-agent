from typing import Any

import config
from services.aviation_weather_service import get_metar_near_location
from services.http_client import APIError


def check_vmc_conditions(latitude: float, longitude: float) -> dict[str, Any]:
    """
    Evaluate Visual Meteorological Conditions (VMC) using nearest METAR.

    Checks cloud ceiling and visibility against AFF student minimums.
    """
    metar = get_metar_near_location(latitude, longitude)

    ceiling_ft = metar.get("cloud_ceiling_ft_agl")
    visibility_sm = metar.get("visibility_sm")

    ceiling_ok = ceiling_ft is None or ceiling_ft >= config.MIN_CLOUD_CEILING_FT_AGL
    visibility_ok = (
        visibility_sm is None or visibility_sm >= config.MIN_VISIBILITY_STATUTE_MILES
    )

    issues = []
    if ceiling_ft is not None and not ceiling_ok:
        issues.append(
            f"Cloud ceiling {ceiling_ft} ft AGL is below minimum "
            f"{config.MIN_CLOUD_CEILING_FT_AGL} ft AGL"
        )
    if visibility_sm is not None and not visibility_ok:
        issues.append(
            f"Visibility {visibility_sm} SM is below minimum "
            f"{config.MIN_VISIBILITY_STATUTE_MILES} SM"
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
        "minimums": {
            "min_cloud_ceiling_ft_agl": config.MIN_CLOUD_CEILING_FT_AGL,
            "min_visibility_statute_miles": config.MIN_VISIBILITY_STATUTE_MILES,
        },
        "issues": issues,
        "metar_summary": {
            "icao": metar.get("icao"),
            "station_name": metar.get("station_name"),
            "raw_metar": metar.get("raw_metar"),
        },
    }
