from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from backend.core.database import get_db
from backend.models.entities import Campaign, Activity
from backend.schemas.pydantic_models import CampaignOut, ActivityOut, PaginatedResponse, PaginationMeta

router = APIRouter(prefix="/api/campaigns", tags=["Campaigns"])


@router.get("", response_model=PaginatedResponse)
def list_campaigns(
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    status: Optional[str] = None,
    channel: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(Campaign)
    if status:
        query = query.filter(Campaign.status == status)
    if channel:
        query = query.filter(Campaign.channel == channel)

    total = query.count()
    items = query.order_by(Campaign.id).offset((page - 1) * page_size).limit(page_size).all()
    total_pages = (total + page_size - 1) // page_size

    return {
        "items": [CampaignOut.model_validate(c) for c in items],
        "meta": PaginationMeta(total_records=total, page=page, page_size=page_size, total_pages=total_pages),
    }


@router.get("/{campaign_id}", response_model=CampaignOut)
def get_campaign(campaign_id: str, db: Session = Depends(get_db)):
    camp = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not camp:
        raise HTTPException(status_code=404, detail=f"Campaign {campaign_id} not found")
    return camp
