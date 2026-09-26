"""Tests for agent tool wrappers."""

import json
from unittest.mock import patch

from services.http_client import APIError
from tools.skydiving_tools import (
    get_dz_coordinates_tool,
    get_safety_limits_tool,
    get_weather_and_wind_tool,
)


class TestGetDzCoordinatesTool:
    def test_success_response_shape(self):
        with patch("tools.skydiving_tools.get_coordinates_by_name") as mock_geo:
            mock_geo.return_value = {
                "location_name": "Go Jump Dead Sea",
                "latitude": 31.2,
                "longitude": 35.3,
            }

            result = json.loads(get_dz_coordinates_tool("Go Jump Dead Sea"))

        assert result["status"] == "success"
        assert result["data"]["latitude"] == 31.2

    def test_location_not_found_error(self):
        with patch(
            "tools.skydiving_tools.get_coordinates_by_name",
            side_effect=APIError("not found", status_code=404),
        ):
            result = json.loads(get_dz_coordinates_tool("Nowhere"))

        assert result["status"] == "error"
        assert result["error_type"] == "LOCATION_NOT_FOUND"


class TestGetWeatherAndWindTool:
    def test_success_response(self):
        with patch("tools.skydiving_tools.get_weather") as mock_weather:
            mock_weather.return_value = {"wind_speed_kmh": 10}

            result = json.loads(get_weather_and_wind_tool(31.2, 35.3))

        assert result["status"] == "success"
        assert result["data"]["wind_speed_kmh"] == 10


class TestGetSafetyLimitsTool:
    def test_returns_aff_defaults(self):
        result = json.loads(get_safety_limits_tool())

        assert result["status"] == "success"
        assert result["data"]["license"] == "aff_student"
        assert result["data"]["limits"]["max_allowed_wind_speed_kmh"] == 25
