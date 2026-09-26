"""Tests for shared HTTP client error handling."""

from unittest.mock import MagicMock, patch

import pytest
import requests

from services.http_client import APIError, HttpClient


@pytest.fixture
def client():
    return HttpClient("https://api.example.com")


class TestHttpClient:
    def test_get_returns_json(self, client):
        mock_response = MagicMock()
        mock_response.json.return_value = {"ok": True}

        with patch("services.http_client.requests.get", return_value=mock_response) as mock_get:
            mock_response.raise_for_status.return_value = None
            result = client.get("https://api.example.com/data", params={"q": "test"})

        assert result == {"ok": True}
        mock_get.assert_called_once_with(
            "https://api.example.com/data",
            params={"q": "test"},
            headers=None,
            timeout=10,
        )

    def test_timeout_raises_api_error(self, client):
        with patch(
            "services.http_client.requests.get",
            side_effect=requests.exceptions.Timeout(),
        ):
            with pytest.raises(APIError, match="too long to respond") as exc_info:
                client.get("https://api.example.com/slow")

        assert exc_info.value.status_code == 504

    def test_http_error_raises_api_error(self, client):
        http_error = requests.exceptions.HTTPError("404")
        http_error.response = MagicMock(status_code=404)

        with patch(
            "services.http_client.requests.get",
            side_effect=http_error,
        ):
            with pytest.raises(APIError, match="HTTP error") as exc_info:
                client.get("https://api.example.com/missing")

        assert exc_info.value.status_code == 404

    def test_invalid_json_raises_api_error(self, client):
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.side_effect = ValueError("bad json")

        with patch("services.http_client.requests.get", return_value=mock_response):
            with pytest.raises(APIError, match="Invalid JSON"):
                client.get("https://api.example.com/bad")
