"""Tests for api/persistence.py."""

from __future__ import annotations

from datetime import date

from api.persistence import build_row, to_date


class TestToDate:
    def test_valid_date(self):
        assert to_date("2026-01-15") == date(2026, 1, 15)

    def test_none(self):
        assert to_date(None) is None

    def test_empty_string(self):
        assert to_date("") is None

    def test_invalid_format(self):
        assert to_date("not-a-date") is None

    def test_partial_date(self):
        assert to_date("2026-01") is None


class TestBuildRow:
    def test_creates_row(self):
        raw = {
            "source_id": "panama",
            "source_name": "Panama Maritime Authority",
            "documento_hash": "abc123",
            "url_origem": "https://example.com",
            "data_publicacao": "2026-01-15",
            "entrada_em_vigor": "2026-06-01",
            "requisito": "Panama Maritime Authority",
            "norma": "MMC-169",
            "assunto": "COM",
            "aplicacao": "D",
            "status": "R",
            "item": "Item 4",
            "itens_modificados": "Mudanca",
            "acao_sugerida": "Notificar",
        }
        row = build_row(raw)
        assert row.source_id == "panama"
        assert row.source_name == "Panama Maritime Authority"
        assert row.norma == "MMC-169"
        assert row.data_publicacao == date(2026, 1, 15)
        assert row.entrada_em_vigor == date(2026, 6, 1)
        assert row.id is not None

    def test_none_dates(self):
        raw = {"norma": "Teste"}
        row = build_row(raw)
        assert row.data_publicacao is None
        assert row.entrada_em_vigor is None
