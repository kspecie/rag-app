"""
Pytest configuration and common fixtures for testing the RAG application.
"""
import pytest
import asyncio
from fastapi.testclient import TestClient
from app.main import app
import os
from unittest.mock import patch
from pathlib import Path
from langchain.schema import Document

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


# ---- Shared realistic data fixtures ----

@pytest.fixture
def sample_docs_dir(tmp_path: Path) -> str:
    d = tmp_path / "docs"
    d.mkdir()
    (d / "a.txt").write_text("hello world")
    (d / "b.txt").write_text("second file")
    return str(d)


@pytest.fixture
def make_documents():
    def _make(texts, with_source: bool = True):
        docs = []
        for i, t in enumerate(texts):
            metadata = {"file_name": f"doc{i}.txt"}
            if with_source:
                metadata["source"] = metadata["file_name"]
            docs.append(Document(page_content=t, metadata=metadata))
        return docs
    return _make


@pytest.fixture
def make_rabbit_message():
    def _make(conv_id: str = "c1", url: str | None = None, user_notes: list[str] | None = None):
        msg = {"conversation_id": conv_id}
        if url:
            msg["file_url"] = url
        if user_notes:
            msg["input"] = [{"role": "user", "content": n} for n in user_notes]
        return msg
    return _make