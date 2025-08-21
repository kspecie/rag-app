"""
Additional error-path tests for embed and store modules
"""
from typing import List
from unittest.mock import patch
from langchain.schema import Document

from app.embed_and_store.embed import create_embeddings
from app.embed_and_store.store import store_chunks_in_chroma


def test_create_embeddings_handles_request_exceptions():
    docs = [Document(page_content="x", metadata={})]
    with patch("requests.post") as mock_post:
        class MockResp:
            def raise_for_status(self):
                raise Exception("boom")
        mock_post.return_value = MockResp()
        # Should handle and return an empty list, not raise
        result = create_embeddings(docs, tei_service_url="http://tei")
        assert isinstance(result, list)


def test_store_chunks_in_chroma_handles_exception():
    chunks = [{"text": "x", "metadata": {}, "embedding": [0.1]}]
    with patch("chromadb.HttpClient", side_effect=Exception("down")):
        # Should swallow and not raise
        store_chunks_in_chroma(chunks, chroma_service_url="http://chromadb:8000")


