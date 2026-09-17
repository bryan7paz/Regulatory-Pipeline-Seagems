"""Tests for process_queue.py — queue processing."""

from __future__ import annotations

import contextlib
import json
from unittest.mock import patch

from process_queue import _compact_queue


class TestCompactQueue:
    def test_removes_processed(self, tmp_path):
        q = tmp_path / "queue.jsonl"
        q.write_text(
            json.dumps({"sha256": "aaa", "title": "doc1"})
            + "\n"
            + json.dumps({"sha256": "bbb", "title": "doc2"})
            + "\n"
            + json.dumps({"sha256": "ccc", "title": "doc3"})
            + "\n"
        )
        with patch("process_queue.QUEUE_PATH", q):
            _compact_queue(["aaa", "ccc"])
            lines = q.read_text().strip().split("\n")
            assert len(lines) == 1
            assert json.loads(lines[0])["sha256"] == "bbb"

    def test_empty_processed(self, tmp_path):
        q = tmp_path / "queue.jsonl"
        q.write_text(json.dumps({"sha256": "aaa"}) + "\n")
        with patch("process_queue.QUEUE_PATH", q):
            _compact_queue([])
            lines = q.read_text().strip().split("\n")
            assert len(lines) == 1

    def test_no_file(self, tmp_path):
        q = tmp_path / "nonexistent.jsonl"
        with patch("process_queue.QUEUE_PATH", q), contextlib.suppress(FileNotFoundError):
            _compact_queue(["aaa"])
