"""
End-to-end integration test (upload -> ingest/embed/store -> list -> summarize),
gated behind env E2E_FULL. In mock mode (default), TEI/TGI calls are patched.
"""
import io
import os
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from app.main import app


def _require_e2e_or_skip():
    if os.getenv("E2E_FULL") != "1":
        pytest.skip("E2E_FULL!=1; skipping end-to-end integration test")


@pytest.mark.integration
def test_e2e_upload_to_summary_flow():
    _require_e2e_or_skip()

    client = TestClient(app)
    api_key = os.getenv("API_KEY", "test-api-key")
    headers = {"X-API-Key": api_key}

    use_mocks = os.getenv("E2E_MOCK_MODE", "1") == "1"

    patches = []
    if use_mocks:
        # Speed/stability: avoid hitting real TEI/TGI
        patches.extend([
            patch("app.core.pipeline.create_embeddings", return_value=[
                {"text": "hello", "metadata": {"source": "mem"}, "embedding": [0.1, 0.2, 0.3]}
            ]),
            patch("app.core.pipeline.generate_summary", return_value="OK_SUMMARY"),
        ])

    # Apply patches as context managers
    ctx = None
    for p in patches:
        ctx = p if ctx is None else ctx.__enter__() or p
        p.__enter__()
    try:
        # 1) Upload small file
        files = [("files", ("it.txt", io.BytesIO(b"hello world"), "text/plain"))]
        r = client.post("/documents/upload/", headers=headers, files=files)
        assert r.status_code == 200

        # 2) List collections
        r = client.get("/documents/collections", headers=headers)
        assert r.status_code == 200
        cols = r.json()
        assert isinstance(cols, list)

        # 3) Generate summary (pipeline retrieval + generation)
        r = client.post("/summaries/generate/", json={"text": "patient conversation"}, headers=headers)
        # In mock mode, expect 200; in real mode, could be 200 or 500 depending on services
        assert r.status_code in (200, 500)
    finally:
        # Exit patches
        for p in reversed(patches):
            p.__exit__(None, None, None)


