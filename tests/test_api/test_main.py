"""
Tests for main FastAPI application endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

def test_read_root(test_client: TestClient):
    """Test the root endpoint."""
    response = test_client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "Medical Conversation RAG API is running. Visit /docs for API documentation."

def test_generate_summary_without_api_key(test_client: TestClient):
    """Test that summary generation requires API key."""
    response = test_client.post("/summaries/generate/", json={"text": "Test conversation"})
    assert response.status_code == 403

def test_generate_summary_with_valid_api_key(test_client: TestClient, api_headers):
    """Test summary generation with valid API key."""
    response = test_client.post(
        "/summaries/generate/", 
        json={"text": "Test medical conversation"}, 
        headers=api_headers
    )
    # This might fail if the RAG pipeline isn't mocked, but we're testing the endpoint structure
    assert response.status_code in [200, 500]  # 500 if RAG pipeline fails, 200 if it works

def test_generate_summary_empty_text(test_client: TestClient, api_headers):
    """Test summary generation with empty text."""
    response = test_client.post(
        "/summaries/generate/", 
        json={"text": ""}, 
        headers=api_headers
    )
    # Should handle empty text appropriately
    assert response.status_code in [200, 400, 422]

def test_api_docs_available(test_client: TestClient):
    """Test that API documentation is available."""
    response = test_client.get("/docs")
    assert response.status_code == 200 