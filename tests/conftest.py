"""
Pytest configuration and common fixtures for testing the RAG application.
"""
import pytest
import asyncio
from fastapi.testclient import TestClient
from app.main import app
import os
from unittest.mock import patch

# Configure test environment
os.environ["TESTING"] = "true"
# Use the actual API key from environment or fallback to test key
os.environ["API_KEY"] = os.getenv("API_KEY", "test-api-key")

@pytest.fixture
def test_client():
    """Create a test client for FastAPI app."""
    return TestClient(app)

@pytest.fixture
def api_headers():
    """Return headers with test API key."""
    api_key = os.getenv("API_KEY", "test-api-key")
    return {"X-API-Key": api_key}

@pytest.fixture
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def mock_env_vars():
    """Mock environment variables for testing."""
    with patch.dict(os.environ, {
        "API_KEY": "test-api-key",
        "TESTING": "true"
    }):
        yield 