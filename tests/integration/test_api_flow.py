"""
High-level API flow tests using the real FastAPI app and live services if available.
Skips when dependencies are not reachable.
"""
import os
import pytest
from fastapi.testclient import TestClient

from app.main import app


def _has_live_services():
    # We only check for Chroma host env; actual connectivity is tested implicitly
    return os.getenv("CHROMA_HOST") is not None


@pytest.mark.integration
def test_root_and_docs_available(api_headers):
    client = TestClient(app)
    r = client.get("/")
    assert r.status_code == 200
    r = client.get("/docs")
    assert r.status_code == 200


@pytest.mark.integration
def test_collections_list_and_documents_listing(api_headers):
    if not _has_live_services():
        pytest.skip("Missing live service env; skipping")

    client = TestClient(app)
    # list collections
    r = client.get("/documents/collections", headers=api_headers)
    if r.status_code != 200:
        pytest.skip("Chroma not reachable; skipping")
    cols = r.json()
    assert isinstance(cols, list)
    # if any collection exists, try listing documents
    if cols:
        name = cols[0]["name"]
        r2 = client.get(f"/documents/collections/{name}", headers=api_headers)
        # status may be 200 with possibly empty list
        assert r2.status_code == 200

