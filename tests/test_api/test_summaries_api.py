"""
Tests for summaries API router and behaviors with pipeline mocking.
"""
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import patch
import pytest


def build_app_with_summaries_router():
    from app.backend.api.summaries import router as summaries_router
    app = FastAPI()
    app.include_router(summaries_router)
    return app


def test_summaries_router_returns_400_on_empty_text():
    app = build_app_with_summaries_router()
    client = TestClient(app)
    response = client.post("/summaries/generate/", params={"transcribed_conversation": ""})
    assert response.status_code == 400


def test_summaries_router_returns_200_on_success():
    app = build_app_with_summaries_router()
    client = TestClient(app)
    with patch("app.backend.api.summaries.run_retrieval_and_generation_pipeline", return_value="ok"):
        response = client.post("/summaries/generate/", params={"transcribed_conversation": "hello"})
        assert response.status_code == 200
        assert response.json().get("summary") == "ok"


def test_summaries_router_returns_500_on_failure():
    app = build_app_with_summaries_router()
    client = TestClient(app)
    with patch("app.backend.api.summaries.run_retrieval_and_generation_pipeline", return_value=None):
        response = client.post("/summaries/generate/", params={"transcribed_conversation": "hello"})
        assert response.status_code == 500


