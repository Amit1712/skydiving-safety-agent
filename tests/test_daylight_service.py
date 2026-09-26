"""Tests for sunrise/sunset and daylight window checks."""

import pytest

from services.daylight_service import get_daylight_times, is_within_daylight
from services.http_client import APIError

# Go Jump Dead Sea coordinates
LAT = 31.2058
LON = 35.3652
TZ = "Asia/Jerusalem"


class TestGetDaylightTimes:
    def test_returns_civil_twilight_window(self):
        result = get_daylight_times(LAT, LON, "2026-09-26", TZ)

        assert result["date"] == "2026-09-26"
        assert result["timezone"] == TZ
        assert "sunrise_local" in result
        assert "civil_dawn_local" in result
        assert "civil_dusk_local" in result
        assert result["daylight_window"]["start"] == result["civil_dawn_local"]

    def test_rejects_invalid_date(self):
        with pytest.raises(APIError, match="Invalid date format"):
            get_daylight_times(LAT, LON, "26-09-2026", TZ)


class TestIsWithinDaylight:
    def test_midday_jump_is_within_daylight(self):
        result = is_within_daylight(LAT, LON, "2026-09-26T12:00", TZ)

        assert result["is_within_daylight"] is True
        assert result["verdict"] == "daylight"

    def test_late_night_jump_is_after_dark(self):
        result = is_within_daylight(LAT, LON, "2026-09-26T23:30", TZ)

        assert result["is_within_daylight"] is False
        assert result["verdict"] == "after_dark_or_before_dawn"

    def test_rejects_invalid_datetime(self):
        with pytest.raises(APIError, match="Invalid datetime format"):
            is_within_daylight(LAT, LON, "not-a-datetime", TZ)
