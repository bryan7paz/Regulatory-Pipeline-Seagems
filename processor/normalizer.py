"""Normalization: validate LLM output against the Pydantic schema."""
from __future__ import annotations

from typing import Any

from .schema import RegulatoryAnalysis

ENUM_FIELDS = ("aplicacao", "status", "assunto")


def normalize(raw: dict[str, Any]) -> RegulatoryAnalysis:
    """Validate and coerce the raw LLM dict into a RegulatoryAnalysis.

    On validation failure, drops enum fields that may contain invalid values
    and retries — these become ``None`` rather than crashing the pipeline.
    """
    data: dict[str, Any] = {}
    for field in RegulatoryAnalysis.model_fields:
        if field in raw:
            data[field] = raw[field]

    try:
        return RegulatoryAnalysis(**data)
    except Exception:  # noqa: BLE001
        safe = {k: v for k, v in data.items() if k not in ENUM_FIELDS}
        return RegulatoryAnalysis(**safe)