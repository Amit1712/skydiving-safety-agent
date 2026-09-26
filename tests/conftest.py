"""Shared pytest fixtures."""

from unittest.mock import MagicMock

import pytest

from services.agent_service import AgentService


@pytest.fixture
def mock_gemini_service():
    return MagicMock()


@pytest.fixture
def agent_service(mock_gemini_service):
    return AgentService(mock_gemini_service)
