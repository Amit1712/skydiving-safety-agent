"""Unit conversion helpers for weather data."""

KMH_TO_KNOTS = 1 / 1.852


def kmh_to_knots(speed_kmh: float | None) -> float | None:
    """Convert wind speed from km/h to knots."""
    if speed_kmh is None:
        return None
    return round(speed_kmh * KMH_TO_KNOTS, 1)


def add_wind_knots(wind_data: dict) -> dict:
    """Add knot equivalents to a wind data dict that has km/h fields."""
    if "wind_speed_kmh" in wind_data:
        wind_data["wind_speed_knots"] = kmh_to_knots(wind_data["wind_speed_kmh"])
    if "wind_gusts_kmh" in wind_data:
        wind_data["wind_gusts_knots"] = kmh_to_knots(wind_data["wind_gusts_kmh"])
    return wind_data
