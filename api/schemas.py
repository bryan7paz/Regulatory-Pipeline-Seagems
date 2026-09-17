"""API Pydantic schemas."""
from __future__ import annotations

from datetime import date, datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict


class AnalysisOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    source_id: Optional[str] = None
    source_name: Optional[str] = None
    url_origem: Optional[str] = None
    data_publicacao: Optional[date] = None
    entrada_em_vigor: Optional[date] = None
    requisito: Optional[str] = None
    norma: Optional[str] = None
    assunto: Optional[str] = None
    aplicacao: Optional[str] = None
    status: Optional[str] = None
    item: Optional[str] = None
    itens_modificados: Optional[str] = None
    acao_sugerida: Optional[str] = None
    status_validacao: Optional[str] = None
    validated_at: Optional[datetime] = None
    validated_by: Optional[str] = None
    created_at: Optional[datetime] = None


class AnalysisDetail(AnalysisOut):
    """Full detail including raw_json (used by GET /regs/{id})."""
    raw_json: Optional[str] = None


class ValidationAction(BaseModel):
    action: Literal["aprovado", "reprovado"]
    validated_by: str = "especialista"
