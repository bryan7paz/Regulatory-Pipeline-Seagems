"""SQLAlchemy ORM models."""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import Column, Date, DateTime, String, Text

from .database import Base, _is_sqlite


class ValidationStatus:
    PENDENTE = "pendente"
    APROVADO = "aprovado"
    REPROVADO = "reprovado"


def _enum_col(*values: str, name: str):
    """Return an Enum column for PostgreSQL, or String for SQLite."""
    if _is_sqlite:
        return Column(String, nullable=True)
    from sqlalchemy import Enum

    return Column(Enum(*values, name=name), nullable=True)


class RegulatoryAnalysis(Base):
    __tablename__ = "regulatory_analysis"

    id = Column(String, primary_key=True)
    source_id = Column(String)
    source_name = Column(String)
    documento_hash = Column(String, index=True)
    url_origem = Column(Text)

    data_publicacao = Column(Date, nullable=True)
    entrada_em_vigor = Column(Date, nullable=True)
    requisito = Column(String, nullable=True)
    norma = Column(String, nullable=True)
    assunto = _enum_col(
        "SEG", "INC", "COM", "NAV", "CON", "TRI", "AMB", "NAU", "IMO", name="assunto_enum"
    )
    aplicacao = _enum_col("D", "I", "NP", name="aplicacao_enum")
    status = _enum_col("R", "N", name="status_enum")
    item = Column(String, nullable=True)
    itens_modificados = Column(Text, nullable=True)
    acao_sugerida = Column(Text, nullable=True)

    status_validacao = Column(String, default=ValidationStatus.PENDENTE)
    raw_json = Column(Text, nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    validated_at = Column(DateTime, nullable=True)
    validated_by = Column(String, nullable=True)
