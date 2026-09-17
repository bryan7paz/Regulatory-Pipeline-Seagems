"""Routes for executive metrics (foundation for future dashboards)."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from .. import models
from ..database import get_db

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/metrics")
def metrics(db: Session = Depends(get_db)):
    total = db.query(func.count(models.RegulatoryAnalysis.id)).scalar() or 0
    by_aplicacao = (
        db.query(models.RegulatoryAnalysis.aplicacao, func.count(models.RegulatoryAnalysis.id))
        .group_by(models.RegulatoryAnalysis.aplicacao)
        .all()
    )
    by_status = (
        db.query(models.RegulatoryAnalysis.status, func.count(models.RegulatoryAnalysis.id))
        .group_by(models.RegulatoryAnalysis.status)
        .all()
    )
    by_validacao = (
        db.query(
            models.RegulatoryAnalysis.status_validacao, func.count(models.RegulatoryAnalysis.id)
        )
        .group_by(models.RegulatoryAnalysis.status_validacao)
        .all()
    )
    by_assunto = (
        db.query(models.RegulatoryAnalysis.assunto, func.count(models.RegulatoryAnalysis.id))
        .group_by(models.RegulatoryAnalysis.assunto)
        .all()
    )
    return {
        "total": total,
        "por_aplicacao": {k or "null": v for k, v in by_aplicacao},
        "por_status": {k or "null": v for k, v in by_status},
        "por_validacao": {k or "null": v for k, v in by_validacao},
        "por_assunto": {k or "null": v for k, v in by_assunto},
    }
