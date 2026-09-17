"""Shared persistence helpers for saving processed analyses to the database."""
from __future__ import annotations

import json
import uuid
from datetime import date, datetime
from typing import Any

from .database import SessionLocal
from . import models


def to_date(value: Any) -> date | None:
    """Convert an ``AAAA-MM-DD`` string to ``date``, or return ``None``."""
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


def build_row(raw: dict[str, Any]) -> models.RegulatoryAnalysis:
    """Build an ORM instance from a normalized analysis dict."""
    return models.RegulatoryAnalysis(
        id=str(uuid.uuid4()),
        source_id=raw.get("source_id"),
        source_name=raw.get("source_name"),
        documento_hash=raw.get("documento_hash"),
        url_origem=raw.get("url_origem"),
        data_publicacao=to_date(raw.get("data_publicacao")),
        entrada_em_vigor=to_date(raw.get("entrada_em_vigor")),
        requisito=raw.get("requisito"),
        assunto=raw.get("assunto"),
        norma=raw.get("norma"),
        aplicacao=raw.get("aplicacao"),
        status=raw.get("status"),
        item=raw.get("item"),
        itens_modificados=raw.get("itens_modificados"),
        acao_sugerida=raw.get("acao_sugerida"),
        raw_json=json.dumps(raw, ensure_ascii=False),
    )


def persist(results: list[dict[str, Any]]) -> int:
    """Insert a list of analyses and return how many were saved."""
    db = SessionLocal()
    try:
        rows = [build_row(r) for r in results]
        db.add_all(rows)
        db.commit()
        return len(rows)
    finally:
        db.close()