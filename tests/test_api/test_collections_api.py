"""
Tests for collections API with heavy mocking of external services.
"""
from unittest.mock import patch
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient


def build_app_with_collections_router():
    from app.backend.api.collections import router as collections_router
    app = FastAPI()
    app.include_router(collections_router)
    return app


def test_update_nice_success():
    app = build_app_with_collections_router()
    client = TestClient(app)
    with patch("app.backend.api.collections.index_nice_knowledge", return_value=[1, 2, 3]):
        response = client.post("/collections/update_nice")
        assert response.status_code == 200
        assert response.json()["status"] == "success"


def test_update_nice_failure():
    app = build_app_with_collections_router()
    client = TestClient(app)
    with patch("app.backend.api.collections.index_nice_knowledge", side_effect=Exception("fail")):
        response = client.post("/collections/update_nice")
        assert response.status_code == 500


def test_update_miriad_skips_if_exists():
    app = build_app_with_collections_router()
    client = TestClient(app)

    class MockClient:
        def get_collection(self, name: str):
            return object()

    with patch("chromadb.HttpClient", return_value=MockClient()):
        response = client.post("/collections/update_miriad")
        assert response.status_code == 200
        assert "already exists" in response.json()["message"]


def test_update_miriad_creates_and_indexes():
    app = build_app_with_collections_router()
    client = TestClient(app)

    class MockCollection:
        def add(self, documents=None, embeddings=None, ids=None):
            return None
        def update(self, metadata=None):
            return None

    # Use the module's NotFoundError type to satisfy the except clause
    import app.backend.api.collections as col_mod

    class MockClient:
        def get_collection(self, name: str):
            raise col_mod.chromadb.errors.NotFoundError("not found")
        def create_collection(self, name: str, embedding_function=None):
            return MockCollection()

    # Fake dataset of 2 rows
    class MockDataset:
        def __iter__(self):
            return iter([
                {"question": "q1", "answer": "a1"},
                {"question": "q2", "answer": "a2"},
            ])

    with (
        patch("app.backend.api.collections.chroma_client", new=MockClient()),
        patch("app.backend.api.collections.load_dataset", return_value=MockDataset()),
        patch("app.backend.api.collections.embedding_functions.SentenceTransformerEmbeddingFunction"),
        patch("app.backend.api.collections.tei_embedding_function", return_value=[[0.1], [0.2]]),
    ):
        response = client.post("/collections/update_miriad")
        assert response.status_code == 200
        assert "Indexing complete" in response.json()["message"]


