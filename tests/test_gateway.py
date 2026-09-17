"""Tests for processor/gateway.py — LLM gateway delegation."""

from __future__ import annotations

from unittest.mock import patch

from processor.gateway import generate_structured


class TestGenerateStructured:
    @patch("processor.gateway._generate")
    def test_delegates_to_llm_providers(self, mock_generate):
        mock_generate.return_value = {"norma": "MSC.1/Circ.1234", "assunto": "SEG"}
        result = generate_structured("system prompt", "user prompt")
        mock_generate.assert_called_once_with("system prompt", "user prompt")
        assert result == {"norma": "MSC.1/Circ.1234", "assunto": "SEG"}

    @patch("processor.gateway._generate")
    def test_returns_dict(self, mock_generate):
        mock_generate.return_value = {"key": "value"}
        result = generate_structured("sys", "usr")
        assert isinstance(result, dict)
