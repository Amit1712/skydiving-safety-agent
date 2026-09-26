import json
import logging
import os
import re
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from services.http_client import APIError, HttpClient

load_dotenv()

logger = logging.getLogger(__name__)

GEOCODING_BASE_URL = os.getenv("GEOCODING_BASE_URL")
NOMINATIM_BASE_URL = "https://nominatim.openstreetmap.org/search"

SKYDIVING_KEYWORDS = (
    "skydiv",
    "dropzone",
    "drop zone",
    "parachute",
    "dz",
    "airfield",
    "airstrip",
    "airport",
)

open_meteo_client = HttpClient(GEOCODING_BASE_URL)
nominatim_client = HttpClient(NOMINATIM_BASE_URL)

KNOWN_DROPZONES_PATH = Path(__file__).resolve().parent.parent / "data" / "known_dropzones.json"


def _normalize_query(text: str) -> str:
    """Normalize a location query for fuzzy matching."""
    normalized = text.lower().strip()
    normalized = re.sub(r"[^\w\s]", " ", normalized)
    return re.sub(r"\s+", " ", normalized).strip()


def _similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, _normalize_query(a), _normalize_query(b)).ratio()


def _load_known_dropzones() -> list[dict[str, Any]]:
    if not KNOWN_DROPZONES_PATH.exists():
        return []
    with KNOWN_DROPZONES_PATH.open(encoding="utf-8") as handle:
        return json.load(handle)


def _match_known_dropzone(location_name: str) -> dict[str, Any] | None:
    """Try to match against the curated dropzone registry."""
    query = _normalize_query(location_name)
    best_match: dict[str, Any] | None = None
    best_score = 0.0

    for dropzone in _load_known_dropzones():
        candidates = [dropzone["name"], *dropzone.get("aliases", [])]
        for candidate in candidates:
            normalized_candidate = _normalize_query(candidate)

            if query == normalized_candidate:
                score = 1.0
            elif query in normalized_candidate or normalized_candidate in query:
                score = 0.92
            else:
                score = _similarity(query, normalized_candidate)

            if score > best_score:
                best_score = score
                best_match = dropzone

    if best_match and best_score >= 0.72:
        return {
            "dropzone_id": best_match.get("id"),
            "location_name": best_match["name"],
            "country": best_match.get("country"),
            "region": best_match.get("region"),
            "latitude": best_match["latitude"],
            "longitude": best_match["longitude"],
            "nearest_icao": best_match.get("nearest_icao"),
            "match_source": "known_dropzone_registry",
            "match_confidence": round(best_score, 2),
            "is_dropzone": True,
        }

    return None


def _score_geocoding_result(result: dict[str, Any], original_query: str) -> float:
    """Score a geocoding candidate for dropzone relevance."""
    name = result.get("name", "") or result.get("display_name", "")
    feature_type = (result.get("feature_type") or result.get("type") or "").lower()
    category = (result.get("category") or result.get("class") or "").lower()
    combined = f"{name} {feature_type} {category}".lower()
    query = _normalize_query(original_query)

    score = _similarity(query, name)

    if any(keyword in combined for keyword in SKYDIVING_KEYWORDS):
        score += 0.35
    if feature_type in {"aerodrome", "airport", "airfield"} or category == "aeroway":
        score += 0.2
    if result.get("importance"):
        score += min(float(result["importance"]), 1.0) * 0.1

    return score


def _search_open_meteo(query: str, count: int = 5) -> list[dict[str, Any]]:
    params = {"name": query, "count": count, "language": "en", "format": "json"}
    data = open_meteo_client.get(GEOCODING_BASE_URL, params=params)
    return data.get("results") or []


def _search_nominatim(query: str, count: int = 5) -> list[dict[str, Any]]:
    params = {
        "q": query,
        "format": "json",
        "limit": count,
        "addressdetails": 1,
    }
    headers = {"User-Agent": "SkydivingSafetyAgent/1.0 (educational project)"}

    try:
        response = nominatim_client.get(
            NOMINATIM_BASE_URL, params=params, headers=headers
        )
    except APIError:
        logger.warning("Nominatim geocoding failed for query: %s", query)
        return []

    if not isinstance(response, list):
        return []

    normalized = []
    for item in response:
        address = item.get("address", {})
        normalized.append(
            {
                "name": item.get("display_name", item.get("name", "")),
                "latitude": float(item["lat"]),
                "longitude": float(item["lon"]),
                "country": address.get("country"),
                "feature_type": item.get("type", ""),
                "category": item.get("class", ""),
                "importance": float(item.get("importance", 0)),
                "match_source": "nominatim",
            }
        )
    return normalized


def _normalize_open_meteo_result(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": result.get("name"),
        "latitude": result.get("latitude"),
        "longitude": result.get("longitude"),
        "country": result.get("country"),
        "feature_type": result.get("feature_code", ""),
        "category": result.get("country_code", ""),
        "importance": 0.0,
        "match_source": "open_meteo",
    }


def _build_search_queries(location_name: str) -> list[str]:
    """Generate search query variations biased toward dropzones."""
    base = location_name.strip()
    queries = [
        f"{base} skydiving dropzone",
        f"{base} parachute center",
        base,
    ]

    seen = set()
    unique_queries = []
    for query in queries:
        normalized = _normalize_query(query)
        if normalized not in seen:
            seen.add(normalized)
            unique_queries.append(query)
    return unique_queries


def get_coordinates_by_name(location_name: str) -> dict[str, Any]:
    """
    Resolve a dropzone or location name to coordinates.

    Resolution order:
    1. Curated known dropzone registry (highest confidence)
    2. Nominatim/OSM search with skydiving-biased queries
    3. Open-Meteo geocoding fallback
    """
    known_match = _match_known_dropzone(location_name)
    if known_match:
        return known_match

    candidates: list[dict[str, Any]] = []

    for query in _build_search_queries(location_name):
        for result in _search_nominatim(query):
            result["search_query"] = query
            candidates.append(result)

        for raw in _search_open_meteo(query):
            result = _normalize_open_meteo_result(raw)
            result["search_query"] = query
            candidates.append(result)

    if not candidates:
        raise APIError(
            f"No coordinates found for location: '{location_name}'", status_code=404
        )

    scored = []
    for candidate in candidates:
        score = _score_geocoding_result(candidate, location_name)
        scored.append((score, candidate))

    scored.sort(key=lambda item: item[0], reverse=True)
    best_score, best = scored[0]

    is_dropzone = any(
        keyword in (best.get("name") or "").lower() for keyword in SKYDIVING_KEYWORDS
    ) or best.get("feature_type") in {"aerodrome", "airport", "airfield"}

    alternates = []
    for score, candidate in scored[1:4]:
        alternates.append(
            {
                "location_name": candidate.get("name"),
                "latitude": candidate.get("latitude"),
                "longitude": candidate.get("longitude"),
                "match_confidence": round(score, 2),
                "match_source": candidate.get("match_source"),
            }
        )

    return {
        "location_name": best.get("name"),
        "country": best.get("country"),
        "latitude": best.get("latitude"),
        "longitude": best.get("longitude"),
        "match_source": best.get("match_source"),
        "match_confidence": round(best_score, 2),
        "is_dropzone": is_dropzone,
        "search_query_used": best.get("search_query"),
        "alternates": alternates,
    }
