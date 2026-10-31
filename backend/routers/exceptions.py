from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.core.database import get_db
from backend.models.entities import AnomalyRecord

router = APIRouter(prefix="/api/exceptions", tags=["Exceptions & Anomalies"])


@router.get("")
def list_exceptions(
    issue_type: Optional[str] = None,
    severity: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(AnomalyRecord)
    if issue_type:
        query = query.filter(AnomalyRecord.issue_type == issue_type)
    if severity:
        query = query.filter(AnomalyRecord.severity == severity)

    records = query.order_by(AnomalyRecord.detected_at.desc()).all()

    # Case breakdown
    counts = (
        db.query(AnomalyRecord.issue_type, func.count(AnomalyRecord.id))
        .group_by(AnomalyRecord.issue_type)
        .all()
    )
    breakdown = {t: c for t, c in counts}

    return {
        "total_anomalies": len(records),
        "case_breakdown": breakdown,
        "anomalies": records,
    }
