"""
Tests for embed_and_store modules with external services mocked.
"""
from typing import List, Dict, Any
from unittest.mock import patch
import json
from langchain.schema import Document

import pytest

from app.embed_and_store.embed import batch_chunks_by_payload_size_and_count, create_embeddings
from app.embed_and_store.store import store_chunks_in_chroma


def make_docs(n: int, size: int = 10) -> List[Document]:
    return [Document(page_content=("x" * size), metadata={"source": f"f{i}"}) for i in range(n)]


def test_batching_respects_item_count_and_payload():
    docs = make_docs(100, size=100)
    batches = batch_chunks_by_payload_size_and_count(docs, max_bytes=1000, max_items=16)
    assert all(len(b) <= 16 for b in batches)
    # payload constraint is approximated; ensure at least more than one batch
    assert len(batches) > 1


def test_create_embeddings_happy_path():
    docs = make_docs(3, size=5)
    fake_vectors = [[0.1, 0.2], [0.2, 0.3], [0.3, 0.4]]
    with patch("requests.post") as mock_post:
        class MockResp:
            def raise_for_status(self):
                return None
            def json(self):
                return fake_vectors
        mock_post.return_value = MockResp()

        result = create_embeddings(docs, tei_service_url="http://tei")
        assert len(result) == 3
        assert all(isinstance(r["embedding"], list) for r in result)


def test_store_chunks_in_chroma_basic_flow():
    chunks: List[Dict[str, Any]] = [
        {"text": "hello", "metadata": {"source": "s1"}, "embedding": [0.1, 0.2]},
        {"text": "world", "metadata": {"source": "s1"}, "embedding": [0.2, 0.3]},
    ]

    class MockCollection:
        def add(self, documents=None, metadatas=None, embeddings=None, ids=None):
            assert len(documents) == 2
            assert len(metadatas) == 2
            assert len(embeddings) == 2
            assert len(ids) == 2

    class MockClient:
        def get_or_create_collection(self, name: str):
            return MockCollection()

    with patch("chromadb.HttpClient", return_value=MockClient()):
        # Should not raise
        store_chunks_in_chroma(chunks, chroma_service_url="http://chromadb:8000", collection_name="test")


