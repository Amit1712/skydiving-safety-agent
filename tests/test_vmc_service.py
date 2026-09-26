"""Tests for VMC condition evaluation."""

from unittest.mock import patch

from services.vmc_service import check_vmc_conditions


class TestCheckVmcConditions:
    @patch("services.vmc_service.get_metar_near_location")
    def test_vmc_ok_when_above_minimums(self, mock_metar):
        mock_metar.return_value = {
            "cloud_ceiling_ft_agl": 5000,
            "visibility_sm": 10.0,
            "flight_category": "VFR",
            "icao": "OJAM",
            "station_name": "Masada",
            "raw_metar": "OJAM 261200Z 00000KT CAVOK",
        }

        result = check_vmc_conditions(31.2, 35.3, license_type="aff_student")

        assert result["vmc_ok"] is True
        assert result["issues"] == []
        assert result["license"] == "aff_student"

    @patch("services.vmc_service.get_metar_near_location")
    def test_vmc_fails_low_ceiling(self, mock_metar):
        mock_metar.return_value = {
            "cloud_ceiling_ft_agl": 1500,
            "visibility_sm": 10.0,
            "flight_category": "MVFR",
            "icao": "OJAM",
            "station_name": "Masada",
            "raw_metar": "OJAM 261200Z BKN015",
        }

        result = check_vmc_conditions(31.2, 35.3, license_type="aff_student")

        assert result["vmc_ok"] is False
        assert any("Cloud ceiling" in issue for issue in result["issues"])

    @patch("services.vmc_service.get_metar_near_location")
    def test_ifr_category_fails_vmc(self, mock_metar):
        mock_metar.return_value = {
            "cloud_ceiling_ft_agl": 4000,
            "visibility_sm": 5.0,
            "flight_category": "IFR",
            "icao": "OJAM",
            "station_name": "Masada",
            "raw_metar": "OJAM 261200Z IFR",
        }

        result = check_vmc_conditions(31.2, 35.3)

        assert result["vmc_ok"] is False
        assert any("IFR" in issue for issue in result["issues"])
