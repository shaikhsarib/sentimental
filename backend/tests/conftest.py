import pytest
import os
import shutil
import json
from unittest.mock import AsyncMock, MagicMock

# Base path for temporary testing storage
TEST_STORAGE = "tests/test_storage"

@pytest.fixture(scope="session", autouse=True)
def setup_test_env():
    """Setup and teardown the testing storage directory."""
    if os.path.exists(TEST_STORAGE):
        shutil.rmtree(TEST_STORAGE)
    os.makedirs(TEST_STORAGE)
    yield
    if os.path.exists(TEST_STORAGE):
        shutil.rmtree(TEST_STORAGE)

@pytest.fixture
def mock_llm_response():
    """Provide a mock LLM response for testing."""
    return {
        "triggered": True,
        "reaction": "Test reaction",
        "emotion": "neutral",
        "virality_risk": 5,
        "trigger_phrase": "test phrase"
    }

@pytest.fixture
def mock_call_llm(mocker, mock_llm_response):
    """Mock the call_llm_with_settings function."""
    mock = mocker.patch("engines.multi_model.call_llm_with_settings", new_callable=AsyncMock)
    mock.return_value = mock_llm_response
    return mock
