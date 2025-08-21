"""
Integration test against a live ChromaDB service.
Skips automatically if Chroma is unreachable.
"""
import os
import uuid
import pytest
import chromadb


def _get_client_or_skip() -> chromadb.HttpClient:
    host = os.getenv("CHROMA_HOST", "chromadb_service")
    port = int(os.getenv("CHROMA_PORT", "8000"))
    try:
        client = chromadb.HttpClient(host=host, port=port)
        # quick call to verify connectivity
        _ = client.list_collections()
        return client
    except Exception:
        pytest.skip("ChromaDB service is not reachable; skipping integration test")


@pytest.mark.integration
def test_create_add_list_delete_collection_in_chroma():
    client = _get_client_or_skip()

    collection_name = f"it_{uuid.uuid4().hex[:8]}"
    collection = client.get_or_create_collection(name=collection_name)

    # Add a tiny document with a trivial embedding to avoid heavy models
    collection.add(
        documents=["hello world"],
        metadatas=[{"source": "it_test"}],
        embeddings=[[0.1, 0.2, 0.3]],
        ids=[f"{collection_name}_chunk_0"],
    )

    names = {c.name for c in client.list_collections()}
    assert collection_name in names

    # cleanup
    client.delete_collection(name=collection_name)

