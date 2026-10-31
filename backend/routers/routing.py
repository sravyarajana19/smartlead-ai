from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.core.database import get_db
from backend.models.entities import Lead, SalesRep
from backend.services.routing_service import SalesRoutingEngine
from backend.schemas.pydantic_models import RoutingRequest, RoutingResponse

router = APIRouter(prefix="/api/routing", tags=["Routing"])


@router.post("/route", response_model=RoutingResponse)
def route_lead_endpoint(request: RoutingRequest, db: Session = Depends(get_db)):
    lead = db.query(Lead).filter(Lead.id == request.lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail=f"Lead {request.lead_id} not found")

    reps = db.query(SalesRep).all()
    rep_dicts = [r.__dict__ for r in reps]

    assigned_rep, status, explanation = SalesRoutingEngine.route_lead(
        lead_territory=lead.territory,
        product_interest=lead.product_interest,
        available_reps=rep_dicts,
    )

    if assigned_rep:
        # Update lead in DB
        lead.assigned_rep_id = assigned_rep["id"]
        # Increment rep load
        db_rep = db.query(SalesRep).filter(SalesRep.id == assigned_rep["id"]).first()
        if db_rep:
            db_rep.current_load += 1
        db.commit()

    return {
        "lead_id": lead.id,
        "assigned_rep_id": assigned_rep["id"] if assigned_rep else None,
        "rep_name": assigned_rep["name"] if assigned_rep else None,
        "territory": lead.territory,
        "product_interest": lead.product_interest,
        "routing_status": status,
        "message": explanation,
    }
