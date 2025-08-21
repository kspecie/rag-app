"""
Tests for data_ingestion.split_and_chunk utilities
"""
from typing import List
import pytest
from langchain.schema import Document
from app.data_ingestion.split_and_chunk import clean_document_content, split_documents_into_chunks


def make_docs(texts: List[str]) -> List[Document]:
    return [Document(page_content=t, metadata={"file_name": f"doc{i}.txt"}) for i, t in enumerate(texts)]


def test_clean_document_content_trims_and_normalizes():
    docs = make_docs(["  line1  \n\n\n line2   ", "\n\nhello   world\n\n"])
    cleaned = clean_document_content(docs)
    # Function normalizes multiple newlines and spaces down to single spaces
    assert cleaned[0].page_content == "line1 line2"
    assert cleaned[1].page_content == "hello world"


def test_split_documents_into_chunks_preserves_metadata_and_source():
    long_text = "a" * 1000
    docs = make_docs([long_text])
    chunks = split_documents_into_chunks(docs, chunk_size=200, chunk_overlap=50)
    assert len(chunks) > 1
    for chunk in chunks:
        # should carry over parent metadata and set source from file_name if missing
        assert chunk.metadata.get("file_name") is not None
        assert chunk.metadata.get("source") is not None


