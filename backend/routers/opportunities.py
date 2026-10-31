from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from backend.core.database import get_db
from backend.models.entities import Opportunity, StageHistory, Lead, AnomalyRecord
from backend.schemas.pydantic_models import (
    OpportunityOut,
    StageHistoryOut,
    StageTransitionRequest,
    PaginatedResponse,
    PaginationMeta,
)
from backend.services.opportunity_service import OpportunityManagementService
from generator.id_generator import generate_stage_history_id, generate_anomaly_id

router = APIRouter(prefix="/api/opportunities", tags=["Opportunities"])


@router.get("", response_model=PaginatedResponse)
def list_opportunities(
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    stage: Optional[str] = None,
    rep_id: Optional[str] = None,
    is_duplicate: Optional[bool] = None,
    db: Session = Depends(get_db),
):
    query = db.query(Opportunity)
    if stage:
        query = query.filter(Opportunity.current_stage == stage)
    if rep_id:
        query = query.filter(Opportunity.assigned_rep_id == rep_id)
    if is_duplicate is not None:
        query = query.filter(Opportunity.is_duplicate == is_duplicate)

    total = query.count()
    items = query.order_by(Opportunity.creation_date.desc()).offset((page - 1) * page_size).limit(page_size).all()
    total_pages = (total + page_size - 1) // page_size

    return {
        "items": [OpportunityOut.model_validate(o) for o in items],
        "meta": PaginationMeta(total_records=total, page=page, page_size=page_size, total_pages=total_pages),
    }


@router.get("/{opp_id}", response_model=OpportunityOut)
def get_opportunity(opp_id: str, db: Session = Depends(get_db)):
    opp = db.query(Opportunity).filter(Opportunity.id == opp_id).first()
    if not opp:
        raise HTTPException(status_code=404, detail=f"Opportunity {opp_id} not found")
    return opp


@router.get("/{opp_id}/history", response_model=List[StageHistoryOut])
def get_opportunity_history(opp_id: str, db: Session = Depends(get_db)):
    history = (
        db.query(StageHistory)
        .filter(StageHistory.opportunity_id == opp_id)
        .order_by(StageHistory.transition_date.asc())
        .all()
    )
    return [StageHistoryOut.model_validate(h) for h in history]


@router.post("/{opp_id}/transition", response_model=OpportunityOut)
def transition_opportunity_stage(
    opp_id: str,
    request: StageTransitionRequest,
    db: Session = Depends(get_db),
):
    opp = db.query(Opportunity).filter(Opportunity.id == opp_id).first()
    if not opp:
        raise HTTPException(status_code=404, detail=f"Opportunity {opp_id} not found")

    from_stage = opp.current_stage
    to_stage = request.new_stage

    is_valid, validation_msg = OpportunityManagementService.validate_transition(from_stage, to_stage)

    now = datetime.utcnow()
    hist_count = db.query(StageHistory).filter(StageHistory.opportunity_id == opp_id).count()
    hist_id = generate_stage_history_id(opp_id, hist_count + 1)

    # Check for Case 5 Anomaly (e.g. direct jump New -> Won)
    if not is_valid and to_stage == "Won":
        anm_count = db.query(AnomalyRecord).count()
        anom = AnomalyRecord(
            id=generate_anomaly_id(anm_count + 1),
            entity_type="StageHistory",
            entity_id=opp_id,
            issue_type="CASE_5_MISSING_STAGE_TRANSITION",
            severity="High",
            ground_truth_label="MISSING_STAGE_TRANSITIONS",
            expected_decision="REJECT_INVALID_TRANSITION",
            actual_decision="SKIPPED_INTERMEDIATE_STAGES",
            explanation=f"Opportunity {opp_id} leaped directly from '{from_stage}' to '{to_stage}'.",
        )
        db.add(anom)

    # Record stage history
    history_entry = StageHistory(
        id=hist_id,
        opportunity_id=opp_id,
        from_stage=from_stage,
        to_stage=to_stage,
        stage_duration_days=max(1, (now - opp.updated_at).days) if opp.updated_at else 1,
        transition_date=now,
        changed_by=request.changed_by or "Sales Agent",
        is_valid_transition=is_valid,
        notes=request.notes or (validation_msg if not is_valid else f"Moved to {to_stage}"),
        created_at=now,
    )
    db.add(history_entry)

    # Update opportunity
    opp.current_stage = to_stage
    opp.updated_at = now
    if to_stage in {"Won", "Lost"}:
        opp.actual_close_date = now
        opp.won_lost_reason = request.won_lost_reason

    db.commit()
    db.refresh(opp)
    return opp
