from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from backend.core.database import get_db
from backend.models.entities import Company
from backend.schemas.pydantic_models import CompanyOut, PaginatedResponse, PaginationMeta

router = APIRouter(prefix="/api/companies", tags=["Companies"])


@router.get("", response_model=PaginatedResponse)
def list_companies(
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    industry: Optional[str] = None,
    territory: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(Company)
    if industry:
        query = query.filter(Company.industry == industry)
    if territory:
        query = query.filter(Company.territory == territory)
    if search:
        query = query.filter(Company.name.ilike(f"%{search}%"))

    total = query.count()
    items = query.order_by(Company.id).offset((page - 1) * page_size).limit(page_size).all()
    total_pages = (total + page_size - 1) // page_size

    return {
        "items": [CompanyOut.model_validate(c) for c in items],
        "meta": PaginationMeta(total_records=total, page=page, page_size=page_size, total_pages=total_pages),
    }


@router.get("/{company_id}", response_model=CompanyOut)
def get_company(company_id: str, db: Session = Depends(get_db)):
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail=f"Company {company_id} not found")
    return company
