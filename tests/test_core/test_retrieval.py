"""
Tests for retrieval.retrieve_relevant_chunks
"""
from unittest.mock import patch

from app.retrieval.retrieve import retrieve_relevant_chunks


def test_retrieve_relevant_chunks_happy_path():
    class MockCollection:
        def __init__(self, name):
            self.name = name
            self.metadata = {"hnsw:space": "cosine"}
        def query(self, query_texts, n_results, include):
            return {
                "documents": [["doc1", "doc2"]],
                "metadatas": [[{"source": "s1"}, {"source": "s2"}]],
                "distances": [[0.1, 0.95]],  # second filtered out by threshold
            }

    class MockClient:
        def list_collections(self):
            class C:
                def __init__(self, name):
                    self.name = name
            return [C("c1"), C("c2")]
        def get_collection(self, name):
            return MockCollection(name)

    with patch("chromadb.HttpClient", return_value=MockClient()):
        chunks = retrieve_relevant_chunks("hello", chroma_db_url="http://chromadb:8000", n_results=5)
        # Two collections, each contributes the same first doc
        assert len(chunks) == 2
        assert all(c["page_content"] == "doc1" for c in chunks)


def test_retrieve_relevant_chunks_handles_exception():
    with patch("chromadb.HttpClient", side_effect=Exception("down")):
        chunks = retrieve_relevant_chunks("hello", chroma_db_url="http://chromadb:8000")
        assert chunks == []


