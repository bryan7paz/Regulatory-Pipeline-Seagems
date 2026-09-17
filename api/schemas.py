"""API Pydantic schemas."""

from __future__ import annotations

from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict


class AnalysisOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    source_id: str | None = None
    source_name: str | None = None
    url_origem: str | None = None
    data_publicacao: date | None = None
    entrada_em_vigor: date | None = None
    requisito: str | None = None
    norma: str | None = None
    assunto: str | None = None
    aplicacao: str | None = None
    status: str | None = None
    item: str | None = None
    itens_modificados: str | None = None
    acao_sugerida: str | None = None
    status_validacao: str | None = None
    validated_at: datetime | None = None
    validated_by: str | None = None
    created_at: datetime | None = None


class AnalysisDetail(AnalysisOut):
    """Full detail including raw_json (used by GET /regs/{id})."""

    raw_json: str | None = None


class ValidationAction(BaseModel):
    action: Literal["aprovado", "reprovado"]
    validated_by: str = "especialista"
