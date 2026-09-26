import logging
from typing import Any

import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("HttpClient")


class APIError(Exception):
    """Exception raised for API errors."""

    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


class HttpClient:
    """HTTP client for making API requests."""

    def __init__(self, base_url: str):
        self.base_url = base_url

    def get(self, url: str, params: dict[str, Any] | None = None) -> Any:
        """Make a GET request to the API."""
        try:
            logger.info(f"Fetching URL: {url} with params: {params}")
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            logger.error(f"Timeout occurred while calling {url}")
            raise APIError(
                "The external service took too long to respond (Timeout).",
                status_code=504,
            )
        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code if e.response else None
            logger.error(f"HTTP Error {status_code} for {url}")
            raise APIError(
                f"External API returned HTTP error: {e}", status_code=status_code
            )
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error for {url}: {e!s}")
            raise APIError(f"Network error occurred: {e!s}")
        except ValueError:
            logger.error(f"Failed to parse JSON response from {url}")
            raise APIError("Invalid JSON response received from API.")
