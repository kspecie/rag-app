"""
Edge-case tests for core pipeline functions
"""
from unittest.mock import patch
import pytest

from app.core.pipeline import run_ingestion_pipeline, run_embedding_and_storage_pipeline, run_retrieval_and_generation_pipeline


def test_run_ingestion_pipeline_no_documents(tmp_path):
    # Mock loader to return empty list
    with patch("app.core.pipeline.load_documents", return_value=[]):
        chunks = run_ingestion_pipeline(str(tmp_path))
        assert chunks == []


def test_run_embedding_and_storage_pipeline_no_chunks():
    # Should early return without errors
    with patch("app.core.pipeline.create_embeddings", return_value=[]):
        assert run_embedding_and_storage_pipeline([]) is None


def test_run_retrieval_and_generation_pipeline_no_relevant_chunks():
    with patch("app.core.pipeline.retrieve_relevant_chunks", return_value=[]):
        assert run_retrieval_and_generation_pipeline("hello") is None


def test_run_retrieval_and_generation_pipeline_success():
    with (
        patch("app.core.pipeline.retrieve_relevant_chunks", return_value=["c1", "c2"]),
        patch("app.core.pipeline.generate_summary", return_value="summary"),
    ):
        result = run_retrieval_and_generation_pipeline("hello")
        assert result == "summary"


