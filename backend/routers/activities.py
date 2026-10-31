from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from backend.core.database import get_db
from backend.models.entities import Activity
from backend.schemas.pydantic_models import ActivityOut, PaginatedResponse, PaginationMeta

router = APIRouter(prefix="/api/activities", tags=["Activities"])


@router.get("", response_model=PaginatedResponse)
def list_activities(
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    lead_id: Optional[str] = None,
    activity_type: Optional[str] = None,
    is_post_conversion: Optional[bool] = None,
    db: Session = Depends(get_db),
):
    query = db.query(Activity)
    if lead_id:
        query = query.filter(Activity.lead_id == lead_id)
    if activity_type:
        query = query.filter(Activity.activity_type == activity_type)
    if is_post_conversion is not None:
        query = query.filter(Activity.is_post_conversion == is_post_conversion)

    total = query.count()
    items = query.order_by(Activity.activity_date.desc()).offset((page - 1) * page_size).limit(page_size).all()
    total_pages = (total + page_size - 1) // page_size

    return {
        "items": [ActivityOut.model_validate(a) for a in items],
        "meta": PaginationMeta(total_records=total, page=page, page_size=page_size, total_pages=total_pages),
    }
