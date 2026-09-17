"""Tests for processor/pipeline.py — processing pipeline."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from processor.pipeline import process_all, process_record


class TestProcessRecord:
    @patch("processor.pipeline.extract_from_file")
    @patch("processor.pipeline.build_prompt")
    @patch("processor.pipeline.generate_structured")
    @patch("processor.pipeline.normalize")
    def test_success(self, mock_normalize, mock_generate, mock_build, mock_extract):
        mock_extract.return_value = "document text"
        mock_build.return_value = ("system", "user")
        mock_generate.return_value = {"norma": "MSC.1"}
        mock_normalize.return_value = MagicMock(model_dump=lambda: {"norma": "MSC.1"})

        record = {"url": "http://example.com/doc.pdf", "local_path": "/tmp/doc.pdf"}
        process_record(record)

        mock_extract.assert_called_once()
        mock_build.assert_called_once_with("document text")
        mock_generate.assert_called_once_with("system", "user")
        mock_normalize.assert_called_once()

    @patch("processor.pipeline.extract_from_file", side_effect=Exception("error"))
    def test_extract_error(self, mock_extract):
        record = {"url": "http://example.com/doc.pdf", "local_path": "/tmp/doc.pdf"}
        try:
            process_record(record)
            raise AssertionError()
        except Exception as e:
            assert "error" in str(e)


class TestProcessAll:
    @patch("processor.pipeline.process_record")
    @patch("processor.pipeline.read_queue")
    def test_calls_process_record(self, mock_read, mock_process):
        mock_read.return_value = [
            {"url": "http://a.com/1.pdf", "sha256": "aaa"},
            {"url": "http://a.com/2.pdf", "sha256": "bbb"},
        ]
        mock_process.return_value = {"norma": "MSC.1"}
        results = process_all()
        assert len(results) == 2
        assert mock_process.call_count == 2

    @patch("processor.pipeline.process_record", side_effect=Exception("err"))
    @patch("processor.pipeline.read_queue")
    def test_error_skipped(self, mock_read, mock_process):
        mock_read.return_value = [{"url": "http://a.com/1.pdf", "sha256": "aaa"}]
        results = process_all()
        assert len(results) == 0
