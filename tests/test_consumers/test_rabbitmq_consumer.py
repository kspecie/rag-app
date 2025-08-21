"""
Unit tests for app.consumers.rabbitmq_consumer with heavy mocking.
Focus on pure functions: extract_text_from_pdf, fetch_and_extract_text_from_url, process_rag_request.
"""
from unittest.mock import patch, MagicMock
from types import SimpleNamespace
import io

import pytest

import app.consumers.rabbitmq_consumer as consumer


def test_extract_text_from_pdf_success():
    fake_reader = SimpleNamespace(pages=[SimpleNamespace(extract_text=lambda: "A"), SimpleNamespace(extract_text=lambda: None)])
    with patch("PyPDF2.PdfReader", return_value=fake_reader):
        out = consumer.extract_text_from_pdf(b"%PDF..")
        assert out == "A"


def test_extract_text_from_pdf_error_returns_empty():
    with patch("PyPDF2.PdfReader", side_effect=Exception("bad pdf")):
        out = consumer.extract_text_from_pdf(b"broken")
        assert out == ""


def test_fetch_and_extract_text_from_url_txt():
    class Resp:
        status_code = 200
        text = "hello"
        def raise_for_status(self):
            return None
    with patch("requests.get", return_value=Resp()):
        text = consumer.fetch_and_extract_text_from_url("http://x/a.txt", "cid")
        assert text == "hello"


def test_fetch_and_extract_text_from_url_pdf_calls_pdf_extract():
    class Resp:
        status_code = 200
        content = b"PDF"
        text = "ignored"
        def raise_for_status(self):
            return None
    with (
        patch("requests.get", return_value=Resp()),
        patch.object(consumer, "extract_text_from_pdf", return_value="pdftext") as m,
    ):
        text = consumer.fetch_and_extract_text_from_url("http://x/file.pdf", "cid")
        assert text == "pdftext"
        m.assert_called_once()


def test_fetch_and_extract_text_from_url_network_error_returns_none():
    with patch("requests.get", side_effect=Exception("down")):
        text = consumer.fetch_and_extract_text_from_url("http://x/file.txt", "cid")
        assert text is None


def test_process_rag_request_with_file_url_and_user_prompts_success():
    msg = {
        "conversation_id": "c1",
        "file_url": "http://x/a.txt",
        "input": [
            {"role": "user", "content": "note1"},
            {"role": "assistant", "content": "ignore"},
            {"role": "user", "content": "note2"},
        ],
    }

    class Resp:
        status_code = 200
        text = "transcript"
        def raise_for_status(self):
            return None

    with (
        patch("requests.get", return_value=Resp()),
        patch.object(consumer, "run_retrieval_and_generation_pipeline", return_value="summary") as mock_pipe,
    ):
        out = consumer.process_rag_request(msg)
        assert out["conversation_id"] == "c1"
        assert out["result"] == "summary"
        # Ensure additional_content passed
        mock_pipe.assert_called_once()
        _, kwargs = (), mock_pipe.call_args.kwargs
        assert "additional_content" in mock_pipe.call_args.kwargs
        assert mock_pipe.call_args.kwargs["additional_content"] == "note1 note2"


def test_process_rag_request_pipeline_returns_none_sets_error():
    msg = {"conversation_id": "c2", "file_url": "http://x/a.txt"}

    class Resp:
        status_code = 200
        text = "transcript"
        def raise_for_status(self):
            return None

    with (
        patch("requests.get", return_value=Resp()),
        patch.object(consumer, "run_retrieval_and_generation_pipeline", return_value=None),
    ):
        out = consumer.process_rag_request(msg)
        assert "Failed to generate summary" in out["result"]


def test_process_rag_request_no_content_error():
    msg = {"conversation_id": "c3"}  # neither file_url nor input
    out = consumer.process_rag_request(msg)
    assert "No transcription content" in out["result"]


