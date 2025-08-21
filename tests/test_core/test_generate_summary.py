"""
Tests for generation.generate_summary
"""
from unittest.mock import patch

from app.generation.generate_summary import generate_summary


def test_generate_summary_empty_conversation_returns_message():
    result = generate_summary("   ", relevant_knowledge_chunks=[], tgi_service_url="http://tgi")
    assert result.startswith("No transcribed conversation")


def test_generate_summary_success_saves_and_returns_text():
    class MockResp:
        status_code = 200
        def raise_for_status(self):
            return None
        def json(self):
            return {"generated_text": "SUMMARY"}

    with (
        patch("requests.post", return_value=MockResp()),
        patch("app.generation.generate_summary.save_summary_to_db") as mock_save,
    ):
        result = generate_summary("hello", [{"page_content": "ctx"}], tgi_service_url="http://tgi")
        assert result == "SUMMARY"
        mock_save.assert_called_once()


def test_generate_summary_unexpected_json_returns_empty():
    class MockResp:
        status_code = 200
        def raise_for_status(self):
            return None
        def json(self):
            return {"not_generated_text": True}

    with patch("requests.post", return_value=MockResp()):
        result = generate_summary("hello", [], tgi_service_url="http://tgi")
        assert result == ""


def test_generate_summary_http_error_returns_empty():
    class MockResp:
        status_code = 500
        def raise_for_status(self):
            raise Exception("bad")
    with patch("requests.post", return_value=MockResp()):
        result = generate_summary("hello", [], tgi_service_url="http://tgi")
        assert result == ""


