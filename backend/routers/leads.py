from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from backend.core.database import get_db
from backend.models.entities import Lead
from backend.schemas.pydantic_models import LeadOut, PaginatedResponse, PaginationMeta

router = APIRouter(prefix="/api/leads", tags=["Leads"])


@router.get("", response_model=PaginatedResponse)
def list_leads(
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    priority: Optional[str] = None,
    status: Optional[str] = None,
    territory: Optional[str] = None,
    product: Optional[str] = None,
    is_duplicate: Optional[bool] = None,
    db: Session = Depends(get_db),
):
    query = db.query(Lead)
    if priority:
        query = query.filter(Lead.priority == priority)
    if status:
        query = query.filter(Lead.status == status)
    if territory:
        query = query.filter(Lead.territory == territory)
    if product:
        query = query.filter(Lead.product_interest == product)
    if is_duplicate is not None:
        query = query.filter(Lead.is_duplicate == is_duplicate)

    total = query.count()
    items = query.order_by(Lead.id).offset((page - 1) * page_size).limit(page_size).all()
    total_pages = (total + page_size - 1) // page_size

    return {
        "items": [LeadOut.model_validate(l) for l in items],
        "meta": PaginationMeta(total_records=total, page=page, page_size=page_size, total_pages=total_pages),
    }


@router.get("/{lead_id}", response_model=LeadOut)
def get_lead(lead_id: str, db: Session = Depends(get_db)):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail=f"Lead {lead_id} not found")
    return lead
