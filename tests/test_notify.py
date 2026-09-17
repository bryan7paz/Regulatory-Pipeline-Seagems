"""Tests for core/notify.py — notification system."""

from __future__ import annotations

import json
from unittest.mock import patch

from core.notify import (
    clear_notifications,
    get_notifications,
    notify_new_documents,
    notify_pipeline_complete,
    notify_pipeline_error,
    notify_validation,
)


class TestNotifyPipelineComplete:
    def test_creates_notification(self, tmp_path):
        with patch("core.notify.LOG_DIR", tmp_path):
            notify_pipeline_complete(processed=10, new_documents=3, duration_seconds=12.5)
            log_file = tmp_path / "notifications.jsonl"
            assert log_file.exists()
            lines = log_file.read_text().strip().split("\n")
            assert len(lines) == 1
            event = json.loads(lines[0])
            assert event["event"] == "pipeline_complete"
            assert event["processed"] == 10
            assert event["new_documents"] == 3
            assert event["duration_seconds"] == 12.5

    def test_with_errors(self, tmp_path):
        with patch("core.notify.LOG_DIR", tmp_path):
            notify_pipeline_complete(processed=5, new_documents=0, errors=["err1", "err2"])
            event = json.loads((tmp_path / "notifications.jsonl").read_text().strip())
            assert event["errors"] == ["err1", "err2"]


class TestNotifyPipelineError:
    def test_creates_error_notification(self, tmp_path):
        with patch("core.notify.LOG_DIR", tmp_path):
            notify_pipeline_error("connection timeout", source="iacs")
            event = json.loads((tmp_path / "notifications.jsonl").read_text().strip())
            assert event["event"] == "pipeline_error"
            assert event["error"] == "connection timeout"
            assert event["source"] == "iacs"


class TestNotifyNewDocuments:
    def test_creates_notification(self, tmp_path):
        with patch("core.notify.LOG_DIR", tmp_path):
            notify_new_documents(count=5, source="IACS")
            event = json.loads((tmp_path / "notifications.jsonl").read_text().strip())
            assert event["event"] == "new_documents"
            assert event["count"] == 5
            assert event["source"] == "IACS"

    def test_with_documents_list(self, tmp_path):
        docs = [{"title": "doc1"}, {"title": "doc2"}]
        with patch("core.notify.LOG_DIR", tmp_path):
            notify_new_documents(count=2, source="IMCA", documents=docs)
            event = json.loads((tmp_path / "notifications.jsonl").read_text().strip())
            assert len(event["documents"]) == 2


class TestNotifyValidation:
    def test_creates_notification(self, tmp_path):
        with patch("core.notify.LOG_DIR", tmp_path):
            notify_validation("doc-123", "aprovado", "analista")
            event = json.loads((tmp_path / "notifications.jsonl").read_text().strip())
            assert event["event"] == "validation"
            assert event["doc_id"] == "doc-123"
            assert event["action"] == "aprovado"
            assert event["validated_by"] == "analista"


class TestGetNotifications:
    def test_returns_empty_when_no_file(self, tmp_path):
        with patch("core.notify.LOG_DIR", tmp_path):
            assert get_notifications() == []

    def test_reads_notifications(self, tmp_path):
        with patch("core.notify.LOG_DIR", tmp_path):
            notify_pipeline_complete(1, 0)
            notify_validation("d1", "aprovado", "a1")
            events = get_notifications()
            assert len(events) == 2
            assert events[0]["event"] == "pipeline_complete"
            assert events[1]["event"] == "validation"

    def test_limit_works(self, tmp_path):
        with patch("core.notify.LOG_DIR", tmp_path):
            for i in range(5):
                notify_validation(f"d{i}", "aprovado", "a1")
            events = get_notifications(limit=2)
            assert len(events) == 2

    def test_skips_invalid_json(self, tmp_path):
        with patch("core.notify.LOG_DIR", tmp_path):
            log_file = tmp_path / "notifications.jsonl"
            log_file.write_text('invalid json\n{"event":"test"}\n')
            events = get_notifications()
            assert len(events) == 1
            assert events[0]["event"] == "test"


class TestClearNotifications:
    def test_clears_file(self, tmp_path):
        with patch("core.notify.LOG_DIR", tmp_path):
            notify_pipeline_complete(1, 0)
            notify_validation("d1", "aprovado", "a1")
            count = clear_notifications()
            assert count == 2
            assert not (tmp_path / "notifications.jsonl").exists()

    def test_returns_zero_when_no_file(self, tmp_path):
        with patch("core.notify.LOG_DIR", tmp_path):
            count = clear_notifications()
            assert count == 0
