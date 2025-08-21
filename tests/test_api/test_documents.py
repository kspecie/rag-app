"""
Tests for Documents API endpoints with ChromaDB mocked.
"""
from typing import Any, Dict, List
from unittest.mock import patch
import io

import pytest
from fastapi.testclient import TestClient


class MockCollection:
    def __init__(self, name: str, metadatas: List[Dict[str, Any]] | None = None):
        self.name = name
        self._metadatas = metadatas or []

    def get(self, include: List[str] | None = None):
        return {"metadatas": self._metadatas}

    def add(self, documents=None, embeddings=None, ids=None):
        return None

    def update(self, metadata=None):
        return None


class MockClient:
    def __init__(self, collections: Dict[str, MockCollection]):
        self._collections = collections

    def get_or_create_collection(self, name: str) -> MockCollection:
        if name not in self._collections:
            self._collections[name] = MockCollection(name)
        return self._collections[name]

    def list_collections(self):
        return list(self._collections.values())

    def get_collection(self, name: str):
        if name not in self._collections:
            raise Exception("NotFound")
        return self._collections[name]

    def delete_collection(self, name: str):
        self._collections.pop(name, None)


@pytest.fixture()
def mock_chroma_client():
    # Preload a documents collection with duplicate sources
    docs_meta = [
        {"source": "file1.pdf", "upload_date": "2024-01-01"},
        {"source": "file1.pdf", "upload_date": "2024-01-02"},
        {"source": "file2.pdf", "upload_date": "2024-02-01"},
        None,
    ]
    collections = {
        "documents": MockCollection("documents", docs_meta),
        "other": MockCollection("other", [{"source": "x", "upload_date": "2024-03-01"}]),
    }
    return MockClient(collections)


def test_list_user_documents_dedup(test_client: TestClient, api_headers, mock_chroma_client):
    with patch("app.backend.api.documents.get_client", return_value=mock_chroma_client):
        response = test_client.get("/documents/", headers=api_headers)
        assert response.status_code == 200
        data = response.json()
        # Expect 2 unique sources
        assert len(data) == 2
        ids = {item["id"] for item in data}
        assert {"file1.pdf", "file2.pdf"} == ids
        # file1 uploadDate should be latest non-unknown if present
        file1 = next(item for item in data if item["id"] == "file1.pdf")
        assert file1["uploadDate"] in ["2024-01-01", "2024-01-02", "unknown"]


def test_list_collections(test_client: TestClient, api_headers, mock_chroma_client):
    with patch("app.backend.api.documents.get_client", return_value=mock_chroma_client):
        response = test_client.get("/documents/collections", headers=api_headers)
        assert response.status_code == 200
        names = {c["name"] for c in response.json()}
        assert {"documents", "other"}.issubset(names)


def test_list_documents_in_collection(test_client: TestClient, api_headers, mock_chroma_client):
    with patch("app.backend.api.documents.get_client", return_value=mock_chroma_client):
        response = test_client.get("/documents/collections/documents", headers=api_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert {"filename", "upload_date"}.issubset(data[0].keys())


def test_delete_user_collection(test_client: TestClient, api_headers, mock_chroma_client):
    with patch("app.backend.api.documents.get_client", return_value=mock_chroma_client):
        response = test_client.delete("/documents/collections/user", headers=api_headers)
        assert response.status_code == 200
        assert "deleted" in response.json()["message"]


def test_document_metadata_stores_clean_filenames():
    """Test that document metadata stores clean filenames, not full paths."""
    from app.data_ingestion.split_and_chunk import split_documents_into_chunks
    from unittest.mock import MagicMock
    
    # Mock a document with file_name set (as the document loader would do)
    mock_doc = MagicMock()
    mock_doc.metadata = {
        "file_name": "document.txt",  # This is what document_loader sets
        "source": "temp_uploaded_docs/document.txt"  # This might be set elsewhere
    }
    mock_doc.page_content = "Test content"
    
    # Test that the chunking process cleans up the source field
    chunks = split_documents_into_chunks([mock_doc])
    
    # Verify that source is now just the filename, not the full path
    assert len(chunks) > 0
    for chunk in chunks:
        # Our logic should prioritize file_name over source
        assert chunk.metadata["source"] == "document.txt"
        assert "temp_uploaded_docs" not in chunk.metadata["source"]


def test_document_metadata_cleans_paths_when_no_file_name():
    """Test that document metadata cleans paths when file_name is not available."""
    from app.data_ingestion.split_and_chunk import split_documents_into_chunks
    from unittest.mock import MagicMock
    
    # Mock a document with only source containing a path (no file_name)
    mock_doc = MagicMock()
    mock_doc.metadata = {
        "source": "temp_uploaded_docs/document.txt"  # Only source with path
    }
    mock_doc.page_content = "Test content"
    
    # Test that the chunking process extracts filename from path
    chunks = split_documents_into_chunks([mock_doc])
    
    # Verify that source is cleaned to just the filename
    assert len(chunks) > 0
    for chunk in chunks:
        assert chunk.metadata["source"] == "document.txt"
        assert "temp_uploaded_docs" not in chunk.metadata["source"]


def test_upload_no_files_returns_400(test_client: TestClient, api_headers):
    response = test_client.post("/documents/upload/", headers=api_headers, files={})
    # FastAPI may raise 422 for missing required form field before handler runs
    assert response.status_code in [400, 422]


def test_upload_documents_happy_path(test_client: TestClient, api_headers, mock_chroma_client):
    # Patch chroma client and ingestion/storage pipelines
    from unittest.mock import MagicMock
    
    # Create proper mock Document objects that our code expects
    mock_doc = MagicMock()
    mock_doc.metadata = {"source": "test.txt"}
    mock_doc.page_content = "test content"
    
    with (
        patch("app.backend.api.documents.get_client", return_value=mock_chroma_client),
        patch("app.backend.api.documents.run_ingestion_pipeline", return_value=[mock_doc]),
        patch("app.backend.api.documents.run_embedding_and_storage_pipeline", return_value=None),
    ):
        files = [
            ("files", ("a.txt", io.BytesIO(b"hello"), "text/plain")),
            ("files", ("b.txt", io.BytesIO(b"world"), "text/plain")),
        ]
        response = test_client.post("/documents/upload/", headers=api_headers, files=files)
        assert response.status_code == 200
        assert "Successfully processed" in response.json()["message"]


