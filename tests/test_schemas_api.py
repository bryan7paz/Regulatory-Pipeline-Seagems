"""Tests for api/schemas.py — Pydantic API models."""

from __future__ import annotations

from datetime import date, datetime

from api.schemas import AnalysisDetail, AnalysisOut, ValidationAction


class TestAnalysisOut:
    def test_full_model(self):
        r = AnalysisOut(
            id="abc-123",
            source_id="iacs",
            source_name="IACS",
            url_origem="https://example.com/doc.pdf",
            data_publicacao=date(2024, 6, 15),
            entrada_em_vigor=date(2025, 1, 1),
            requisito="Certificacao",
            norma="MSC.1/Circ.1234",
            assunto="SEG",
            aplicacao="D",
            status="R",
            item="1.2.3",
            itens_modificados="Anexo I",
            acao_sugerida="Atualizar",
            status_validacao="aprovado",
            validated_at=datetime(2024, 7, 1),
            validated_by="analista",
            created_at=datetime(2024, 6, 20),
        )
        assert r.id == "abc-123"
        assert r.source_id == "iacs"
        assert r.data_publicacao == date(2024, 6, 15)
        assert r.status_validacao == "aprovado"

    def test_minimal_model(self):
        r = AnalysisOut(id="minimal")
        assert r.id == "minimal"
        assert r.source_id is None
        assert r.norma is None
        assert r.data_publicacao is None

    def test_from_attributes(self):
        """Test that model can be created from ORM attributes."""

        class FakeORM:
            id = "orm-1"
            source_id = "test"
            source_name = None
            url_origem = None
            data_publicacao = None
            entrada_em_vigor = None
            requisito = None
            norma = None
            assunto = None
            aplicacao = None
            status = None
            item = None
            itens_modificados = None
            acao_sugerida = None
            status_validacao = None
            validated_at = None
            validated_by = None
            created_at = None

        r = AnalysisOut.model_validate(FakeORM())
        assert r.id == "orm-1"


class TestAnalysisDetail:
    def test_inherits_analysis_out(self):
        d = AnalysisDetail(id="d-1", raw_json='{"key": "value"}')
        assert d.id == "d-1"
        assert d.raw_json == '{"key": "value"}'

    def test_raw_json_optional(self):
        d = AnalysisDetail(id="d-2")
        assert d.raw_json is None


class TestValidationAction:
    def test_aprovado(self):
        v = ValidationAction(action="aprovado", validated_by="analista")
        assert v.action == "aprovado"
        assert v.validated_by == "analista"

    def test_reprovado(self):
        v = ValidationAction(action="reprovado")
        assert v.action == "reprovado"
        assert v.validated_by == "especialista"  # default

    def test_invalid_action(self):
        from pydantic import ValidationError

        try:
            ValidationAction(action="invalido")
            raise AssertionError("Should have raised ValidationError")
        except ValidationError:
            pass
