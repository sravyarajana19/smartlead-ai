from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from backend.core.database import get_db
from backend.models.entities import SalesRep
from backend.schemas.pydantic_models import SalesRepOut, PaginatedResponse, PaginationMeta

router = APIRouter(prefix="/api/sales-reps", tags=["Sales Representatives"])


@router.get("", response_model=PaginatedResponse)
def list_sales_reps(
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    territory: Optional[str] = None,
    product: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
):
    query = db.query(SalesRep)
    if territory:
        query = query.filter(SalesRep.territory == territory)
    if product:
        query = query.filter(SalesRep.product_specialization == product)
    if is_active is not None:
        query = query.filter(SalesRep.is_active == is_active)

    total = query.count()
    items = query.order_by(SalesRep.id).offset((page - 1) * page_size).limit(page_size).all()
    total_pages = (total + page_size - 1) // page_size

    return {
        "items": [SalesRepOut.model_validate(r) for r in items],
        "meta": PaginationMeta(total_records=total, page=page, page_size=page_size, total_pages=total_pages),
    }


@router.get("/{rep_id}", response_model=SalesRepOut)
def get_sales_rep(rep_id: str, db: Session = Depends(get_db)):
    rep = db.query(SalesRep).filter(SalesRep.id == rep_id).first()
    if not rep:
        raise HTTPException(status_code=404, detail=f"Sales rep {rep_id} not found")
    return rep
