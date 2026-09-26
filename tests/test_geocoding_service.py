"""Tests for dropzone geocoding (registry matching without external APIs)."""

from unittest.mock import patch

import pytest

from services.geocoding_service import get_coordinates_by_name
from services.http_client import APIError


class TestKnownDropzoneRegistry:
    def test_exact_name_match(self):
        result = get_coordinates_by_name("Go Jump Dead Sea")

        assert result["match_source"] == "known_dropzone_registry"
        assert result["is_dropzone"] is True
        assert result["latitude"] == 31.2058
        assert result["longitude"] == 35.3652
        assert result["dropzone_id"] == "go-jump-dead-sea"

    def test_alias_match(self):
        result = get_coordinates_by_name("gjds")

        assert result["match_source"] == "known_dropzone_registry"
        assert result["location_name"] == "Go Jump Dead Sea"

    def test_paradive_alias(self):
        result = get_coordinates_by_name("habonim dropzone")

        assert result["dropzone_id"] == "paradive"
        assert result["nearest_icao"] == "LLBO"


class TestExternalGeocodingFallback:
    @patch("services.geocoding_service._search_nominatim", return_value=[])
    @patch("services.geocoding_service._search_open_meteo", return_value=[])
    def test_raises_when_no_candidates(self, _open_meteo, _nominatim):
        with pytest.raises(APIError, match="No coordinates found"):
            get_coordinates_by_name("Unknown Place XYZ")

    @patch("services.geocoding_service._search_nominatim", return_value=[])
    @patch("services.geocoding_service._search_open_meteo")
    def test_uses_open_meteo_when_registry_misses(self, mock_open_meteo, _nominatim):
        mock_open_meteo.return_value = [
            {
                "name": "Test Airport",
                "latitude": 40.0,
                "longitude": -75.0,
                "country": "US",
                "feature_code": "AIRP",
                "country_code": "US",
            }
        ]

        result = get_coordinates_by_name("Totally Unknown DZ Name 99999")

        assert result["latitude"] == 40.0
        assert result["match_source"] == "open_meteo"
