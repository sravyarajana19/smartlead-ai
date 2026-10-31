from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from backend.core.database import get_db
from backend.models.entities import Consent, ConsentHistory, Lead
from backend.schemas.pydantic_models import ConsentOut, PaginatedResponse, PaginationMeta
from backend.services.consent_service import ConsentEnforcementService
from generator.id_generator import generate_consent_history_id

router = APIRouter(prefix="/api/consent", tags=["Consent"])


@router.get("", response_model=PaginatedResponse)
def list_consents(
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    status: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(Consent)
    if status:
        query = query.filter(Consent.consent_status == status)

    total = query.count()
    items = query.order_by(Consent.id).offset((page - 1) * page_size).limit(page_size).all()
    total_pages = (total + page_size - 1) // page_size

    return {
        "items": [ConsentOut.model_validate(c) for c in items],
        "meta": PaginationMeta(total_records=total, page=page, page_size=page_size, total_pages=total_pages),
    }


@router.get("/check/{lead_id}")
def check_lead_consent(lead_id: str, db: Session = Depends(get_db)):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail=f"Lead {lead_id} not found")

    consent = db.query(Consent).filter(Consent.lead_id == lead_id).first()
    consent_dict = consent.__dict__ if consent else None

    is_permitted, reason = ConsentEnforcementService.verify_consent_for_outreach(
        lead_id=lead_id,
        consent_record=consent_dict,
        lead_score=lead.lead_score,
    )

    return {
        "lead_id": lead_id,
        "is_permitted": is_permitted,
        "consent_status": consent.consent_status if consent else "Missing",
        "reason": reason,
        "opt_out_timestamp": consent.opt_out_timestamp if consent else None,
    }


@router.post("/opt-out/{lead_id}")
def record_lead_opt_out(lead_id: str, reason: Optional[str] = "User requested opt-out", db: Session = Depends(get_db)):
    consent = db.query(Consent).filter(Consent.lead_id == lead_id).first()
    if not consent:
        raise HTTPException(status_code=404, detail=f"Consent record for lead {lead_id} not found")

    now = datetime.utcnow()
    old_status = consent.consent_status
    consent.consent_status = "Opt-Out"
    consent.opt_out_timestamp = now
    consent.notes = f"Opt-Out recorded via API: {reason}"
    consent.updated_at = now

    hist_count = db.query(ConsentHistory).count()
    history = ConsentHistory(
        id=generate_consent_history_id(hist_count + 1),
        lead_id=lead_id,
        old_status=old_status,
        new_status="Opt-Out",
        reason=reason,
        changed_at=now,
    )
    db.add(history)
    db.commit()

    return {
        "status": "Success",
        "message": f"Lead {lead_id} successfully marked as Opt-Out. All future outbound contact blocked.",
        "opt_out_timestamp": now.isoformat(),
    }
