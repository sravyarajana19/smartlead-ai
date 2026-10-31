from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from backend.core.database import get_db
from backend.models.entities import Contact
from backend.schemas.pydantic_models import ContactOut, PaginatedResponse, PaginationMeta

router = APIRouter(prefix="/api/contacts", tags=["Contacts"])


@router.get("", response_model=PaginatedResponse)
def list_contacts(
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    company_id: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(Contact)
    if company_id:
        query = query.filter(Contact.company_id == company_id)
    if search:
        query = query.filter(
            (Contact.first_name.ilike(f"%{search}%")) |
            (Contact.last_name.ilike(f"%{search}%")) |
            (Contact.email.ilike(f"%{search}%"))
        )

    total = query.count()
    items = query.order_by(Contact.id).offset((page - 1) * page_size).limit(page_size).all()
    total_pages = (total + page_size - 1) // page_size

    return {
        "items": [ContactOut.model_validate(c) for c in items],
        "meta": PaginationMeta(total_records=total, page=page, page_size=page_size, total_pages=total_pages),
    }


@router.get("/{contact_id}", response_model=ContactOut)
def get_contact(contact_id: str, db: Session = Depends(get_db)):
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail=f"Contact {contact_id} not found")
    return contact
