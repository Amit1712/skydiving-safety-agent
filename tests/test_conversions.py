"""Tests for wind unit conversion helpers."""

from services.conversions import add_wind_knots, kmh_to_knots


class TestKmhToKnots:
    def test_converts_speed(self):
        assert kmh_to_knots(37.0) == 20.0

    def test_returns_none_for_none_input(self):
        assert kmh_to_knots(None) is None

    def test_rounds_to_one_decimal(self):
        assert kmh_to_knots(25) == 13.5


class TestAddWindKnots:
    def test_adds_knot_fields(self):
        data = {"wind_speed_kmh": 37.0, "wind_gusts_kmh": 44.0}
        result = add_wind_knots(data)

        assert result["wind_speed_knots"] == 20.0
        assert result["wind_gusts_knots"] == 23.8

    def test_leaves_dict_unchanged_when_no_wind_fields(self):
        data = {"temperature_c": 22}
        assert add_wind_knots(data) == {"temperature_c": 22}
