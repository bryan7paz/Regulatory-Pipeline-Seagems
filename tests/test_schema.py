"""Tests for processor/schema.py — Pydantic models."""

from __future__ import annotations

from processor.schema import (
    Aplicacao,
    Assunto,
    RegulatoryAnalysis,
    Status,
)


class TestEnums:
    def test_aplicacao_values(self):
        assert {a.value for a in Aplicacao} == {"D", "I", "NP"}

    def test_status_values(self):
        assert {s.value for s in Status} == {"R", "N"}

    def test_assunto_values(self):
        expected = {"SEG", "INC", "COM", "NAV", "CON", "TRI", "AMB", "NAU", "IMO"}
        assert {a.value for a in Assunto} == expected


class TestRegulatoryAnalysis:
    def test_full_valid(self):
        r = RegulatoryAnalysis(
            data_publicacao="2026-01-15",
            entrada_em_vigor="2026-06-01",
            requisito="Panama Maritime Authority",
            norma="MMC-169 - Radio Accounting",
            assunto="COM",
            aplicacao="D",
            status="R",
            item="Item 4",
            itens_modificados="Mudanca X",
            acao_sugerida="Notificar equipe",
        )
        d = r.model_dump()
        assert d["assunto"] == "COM"
        assert d["aplicacao"] == "D"

    def test_np_clears_action(self):
        r = RegulatoryAnalysis(aplicacao="NP", acao_sugerida=None)
        assert r.aplicacao == "NP"
        assert r.acao_sugerida is None

    def test_invalid_enum_raises(self):
        import pytest
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            RegulatoryAnalysis(assunto="INVALIDO")

    def test_partial_data(self):
        r = RegulatoryAnalysis(norma="Teste")
        assert r.norma == "Teste"
        assert r.aplicacao is None
        assert r.assunto is None
