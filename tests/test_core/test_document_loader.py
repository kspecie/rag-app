"""
Tests for document_loader.load_documents
"""
from pathlib import Path
import io
import os
import pytest

from app.data_ingestion.document_loader import load_documents


def test_load_documents_raises_for_missing_dir(tmp_path: Path):
    missing = tmp_path / "does_not_exist"
    with pytest.raises(FileNotFoundError):
        load_documents(str(missing))


def test_load_documents_loads_txt_and_injects_metadata(tmp_path: Path):
    # Create text files
    d = tmp_path / "docs"
    d.mkdir()
    f1 = d / "a.txt"
    f1.write_text("hello world")

    docs = load_documents(str(d))
    assert len(docs) == 1
    doc = docs[0]
    assert doc.metadata.get("file_name") == "a.txt"
    assert "upload_date" in doc.metadata


