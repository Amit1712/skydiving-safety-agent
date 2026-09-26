"""License-based safety rules and per-dropzone override engine."""

from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from services.conversions import kmh_to_knots

DEFAULT_LICENSE = "aff_student"

LICENSE_ALIASES: dict[str, str] = {
    "aff": DEFAULT_LICENSE,
    "aff student": DEFAULT_LICENSE,
    "aff_student": DEFAULT_LICENSE,
    "student": DEFAULT_LICENSE,
    "aff-student": DEFAULT_LICENSE,
    "license a": "license_a_b",
    "license b": "license_a_b",
    "license a/b": "license_a_b",
    "license a b": "license_a_b",
    "license_a": "license_a_b",
    "license_b": "license_a_b",
    "license_a_b": "license_a_b",
    "license-a": "license_a_b",
    "license-b": "license_a_b",
    "a": "license_a_b",
    "b": "license_a_b",
    "a license": "license_a_b",
    "b license": "license_a_b",
    "license c": "license_c_d",
    "license d": "license_c_d",
    "license c/d": "license_c_d",
    "license c d": "license_c_d",
    "license_c": "license_c_d",
    "license_d": "license_c_d",
    "license_c_d": "license_c_d",
    "license-c": "license_c_d",
    "license-d": "license_c_d",
    "c": "license_c_d",
    "d": "license_c_d",
    "c license": "license_c_d",
    "d license": "license_c_d",
    "tandem": "tandem_instructor",
    "tandem instructor": "tandem_instructor",
    "tandem_instructor": "tandem_instructor",
    "tandem-instructor": "tandem_instructor",
    "instructor": "tandem_instructor",
    "ti": "tandem_instructor",
}

RULES_PATH = Path(__file__).resolve().parent.parent / "data" / "safety_rules.yaml"
KNOWN_DROPZONES_PATH = (
    Path(__file__).resolve().parent.parent / "data" / "known_dropzones.json"
)


def _normalize_token(value: str) -> str:
    normalized = value.lower().strip()
    normalized = re.sub(r"[^\w\s/-]", " ", normalized)
    return re.sub(r"\s+", " ", normalized).strip()


@lru_cache(maxsize=1)
def _load_rules_config() -> dict[str, Any]:
    if not RULES_PATH.exists():
        return {"licenses": {}, "dropzones": {}}

    with RULES_PATH.open(encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {"licenses": {}, "dropzones": {}}


def resolve_license(license_type: str | None = None) -> str:
    """
    Resolve a user-supplied license string to a canonical license key.
    Falls back to AFF student when empty or unrecognized.
    """
    if not license_type or not license_type.strip():
        return DEFAULT_LICENSE

    token = _normalize_token(license_type)
    if token in LICENSE_ALIASES:
        return LICENSE_ALIASES[token]

    compact = token.replace(" ", "_").replace("-", "_")
    config = _load_rules_config()
    if compact in config.get("licenses", {}):
        return compact

    for alias, canonical in LICENSE_ALIASES.items():
        if alias in token or token in alias:
            return canonical

    return DEFAULT_LICENSE


def _resolve_dropzone_id(
    dropzone_id: str | None = None, dropzone_name: str | None = None
) -> str | None:
    config = _load_rules_config()
    dropzones = config.get("dropzones", {})

    if dropzone_id:
        token = _normalize_token(dropzone_id).replace(" ", "-")
        if token in dropzones:
            return token

    if not dropzone_name:
        return None

    normalized_name = _normalize_token(dropzone_name)

    if KNOWN_DROPZONES_PATH.exists():
        with KNOWN_DROPZONES_PATH.open(encoding="utf-8") as handle:
            known_dropzones = json.load(handle)
        for dropzone in known_dropzones:
            candidates = [dropzone.get("id", ""), dropzone.get("name", "")]
            candidates.extend(dropzone.get("aliases", []))
            for candidate in candidates:
                if _normalize_token(candidate) == normalized_name:
                    dz_id = dropzone.get("id")
                    if dz_id in dropzones:
                        return dz_id

    for dz_id, dz_config in dropzones.items():
        dz_label = _normalize_token(dz_config.get("name", dz_id))
        if normalized_name == dz_label or normalized_name in dz_label:
            return dz_id

    return None


def _add_knot_fields(limits: dict[str, Any]) -> dict[str, Any]:
    enriched = dict(limits)
    if "max_allowed_wind_speed_kmh" in enriched:
        enriched["max_allowed_wind_speed_knots"] = kmh_to_knots(
            enriched["max_allowed_wind_speed_kmh"]
        )
    if "max_allowed_gusts_kmh" in enriched:
        enriched["max_allowed_gusts_knots"] = kmh_to_knots(
            enriched["max_allowed_gusts_kmh"]
        )
    return enriched


def get_safety_limits(
    license_type: str | None = None,
    dropzone_id: str | None = None,
    dropzone_name: str | None = None,
) -> dict[str, Any]:
    """
    Return effective safety limits for a license, optionally merged with
    dropzone-specific overrides from safety_rules.yaml.
    """
    config = _load_rules_config()
    licenses = config.get("licenses", {})
    canonical_license = resolve_license(license_type)

    if canonical_license not in licenses:
        canonical_license = DEFAULT_LICENSE

    base_limits = dict(licenses.get(canonical_license, {}))
    license_label = base_limits.pop("label", canonical_license)

    resolved_dropzone_id = _resolve_dropzone_id(dropzone_id, dropzone_name)
    dropzone_overrides: dict[str, Any] = {}
    dropzone_label: str | None = None

    if resolved_dropzone_id:
        dropzone_config = config.get("dropzones", {}).get(resolved_dropzone_id, {})
        dropzone_label = dropzone_config.get("name", resolved_dropzone_id)
        dropzone_overrides = dict(dropzone_config.get("overrides", {}))

    effective_limits = {**base_limits, **dropzone_overrides}
    effective_limits = _add_knot_fields(effective_limits)

    license_was_defaulted = not license_type or not license_type.strip()
    unrecognized_license = (
        bool(license_type and license_type.strip())
        and resolve_license(license_type) == DEFAULT_LICENSE
        and _normalize_token(license_type) not in LICENSE_ALIASES
        and _normalize_token(license_type).replace(" ", "_").replace("-", "_")
        not in licenses
    )

    return {
        "license": canonical_license,
        "license_label": license_label,
        "license_source": (
            "default_aff_student"
            if license_was_defaulted
            else "user_specified"
        ),
        "license_note": (
            "No license specified in prompt — defaulting to AFF student regulations."
            if license_was_defaulted
            else (
                f"Unrecognized license '{license_type}' — defaulting to AFF student regulations."
                if unrecognized_license
                else f"Applying {license_label} safety regulations."
            )
        ),
        "dropzone_id": resolved_dropzone_id,
        "dropzone_name": dropzone_label,
        "dropzone_overrides_applied": bool(dropzone_overrides),
        "limits": effective_limits,
        "available_licenses": list(licenses.keys()),
    }


def get_vmc_minimums(
    license_type: str | None = None,
    dropzone_id: str | None = None,
    dropzone_name: str | None = None,
) -> dict[str, float]:
    """Return VMC minimums (ceiling + visibility) for the effective ruleset."""
    safety = get_safety_limits(license_type, dropzone_id, dropzone_name)
    limits = safety["limits"]
    return {
        "min_cloud_ceiling_ft_agl": limits["min_cloud_ceiling_ft_agl"],
        "min_visibility_statute_miles": limits["min_visibility_statute_miles"],
    }
