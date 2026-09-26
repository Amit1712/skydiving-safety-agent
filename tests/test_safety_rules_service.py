"""Tests for license resolution and safety limit rules."""

from services.safety_rules_service import (
    DEFAULT_LICENSE,
    get_safety_limits,
    get_vmc_minimums,
    resolve_license,
)


class TestResolveLicense:
    def test_defaults_to_aff_student_when_empty(self):
        assert resolve_license() == DEFAULT_LICENSE
        assert resolve_license("") == DEFAULT_LICENSE
        assert resolve_license("   ") == DEFAULT_LICENSE

    def test_resolves_common_aliases(self):
        assert resolve_license("AFF") == "aff_student"
        assert resolve_license("license b") == "license_a_b"
        assert resolve_license("License C") == "license_c_d"
        assert resolve_license("tandem instructor") == "tandem_instructor"

    def test_defaults_unrecognized_license(self):
        assert resolve_license("super expert") == DEFAULT_LICENSE


class TestGetSafetyLimits:
    def test_aff_student_base_limits(self):
        result = get_safety_limits()

        assert result["license"] == "aff_student"
        assert result["license_source"] == "default_aff_student"
        assert result["limits"]["max_allowed_wind_speed_kmh"] == 25
        assert result["limits"]["max_allowed_wind_speed_knots"] == 13.5

    def test_license_c_d_has_higher_wind_tolerance(self):
        aff = get_safety_limits("aff_student")["limits"]
        experienced = get_safety_limits("license_c_d")["limits"]

        assert experienced["max_allowed_wind_speed_kmh"] > aff["max_allowed_wind_speed_kmh"]

    def test_dropzone_override_merges_limits(self):
        result = get_safety_limits(
            license_type="aff_student",
            dropzone_name="Go Jump Dead Sea",
        )

        assert result["dropzone_id"] == "go-jump-dead-sea"
        assert result["dropzone_overrides_applied"] is True
        assert result["limits"]["max_allowed_wind_speed_kmh"] == 22

    def test_paradive_gust_override(self):
        result = get_safety_limits(dropzone_name="Paradive")

        assert result["dropzone_id"] == "paradive"
        assert result["limits"]["max_allowed_gusts_kmh"] == 28


class TestGetVmcMinimums:
    def test_returns_ceiling_and_visibility(self):
        minimums = get_vmc_minimums("license_a_b")

        assert minimums["min_cloud_ceiling_ft_agl"] == 2500
        assert minimums["min_visibility_statute_miles"] == 3.0
