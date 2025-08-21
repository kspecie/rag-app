"""
Error-path tests for documents API endpoints
"""
from unittest.mock import patch
from fastapi.testclient import TestClient
import pytest


def test_list_user_documents_handles_exception(test_client: TestClient, api_headers):
    with patch("app.backend.api.documents.get_client", side_effect=Exception("down")):
        resp = test_client.get("/documents/", headers=api_headers)
        assert resp.status_code == 500


def test_list_collections_handles_exception(test_client: TestClient, api_headers):
    with patch("app.backend.api.documents.get_client", side_effect=Exception("down")):
        resp = test_client.get("/documents/collections", headers=api_headers)
        assert resp.status_code == 500


def test_list_documents_in_collection_handles_exception(test_client: TestClient, api_headers):
    with patch("app.backend.api.documents.get_client", side_effect=Exception("down")):
        resp = test_client.get("/documents/collections/documents", headers=api_headers)
        assert resp.status_code == 500


def test_delete_user_collection_handles_exception(test_client: TestClient, api_headers):
    with patch("app.backend.api.documents.get_client", side_effect=Exception("down")):
        resp = test_client.delete("/documents/collections/user", headers=api_headers)
        assert resp.status_code == 500


def test_delete_nice_collection_handles_exception(test_client: TestClient, api_headers):
    with patch("app.backend.api.documents.get_client", side_effect=Exception("down")):
        resp = test_client.delete("/documents/collections/nice", headers=api_headers)
        assert resp.status_code == 500


