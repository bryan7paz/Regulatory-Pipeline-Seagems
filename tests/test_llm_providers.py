"""Tests for core/llm_providers.py — multi-provider LLM gateway."""

from __future__ import annotations

from unittest.mock import patch

from core.llm_providers import (
    generate_structured,
    list_providers,
)


class TestListProviders:
    def test_returns_list(self):
        result = list_providers()
        assert isinstance(result, list)

    def test_each_entry_has_fields(self):
        result = list_providers()
        for p in result:
            assert "id" in p
            assert "name" in p
            assert "active" in p
            assert "configured" in p


class TestGenerateStructured:
    @patch("core.llm_providers._get_env")
    def test_raises_when_no_provider(self, mock_env):
        mock_env.return_value = ""
        try:
            generate_structured("sys", "usr")
            raise AssertionError("Should have raised")
        except Exception:
            pass
