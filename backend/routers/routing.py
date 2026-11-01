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
    # Materialize independent plain dicts so ORM expiration on commit does not clear attributes
    rep_dicts = [
        {
            "id": r.id,
            "name": r.name,
            "territory": r.territory,
            "product_specialization": r.product_specialization,
            "current_load": r.current_load,
            "capacity": r.capacity,
            "is_active": r.is_active,
        }
        for r in reps
    ]

    assigned_rep, status, explanation = SalesRoutingEngine.route_lead(
        lead_territory=lead.territory,
        product_interest=lead.product_interest,
        available_reps=rep_dicts,
    )

    assigned_rep_id = None
    rep_name = None

    if assigned_rep:
        assigned_rep_id = assigned_rep["id"]
        rep_name = assigned_rep["name"]

        # Check if already assigned to this rep (idempotent replay)
        if lead.assigned_rep_id != assigned_rep_id:
            # If lead was previously assigned to a different rep, decrement old rep load
            if lead.assigned_rep_id:
                old_rep = db.query(SalesRep).filter(SalesRep.id == lead.assigned_rep_id).first()
                if old_rep and old_rep.current_load > 0:
                    old_rep.current_load -= 1

            # Update lead
            lead.assigned_rep_id = assigned_rep_id

            # Increment new rep load
            db_rep = db.query(SalesRep).filter(SalesRep.id == assigned_rep_id).first()
            if db_rep:
                db_rep.current_load += 1

            db.commit()

    return {
        "lead_id": lead.id,
        "assigned_rep_id": assigned_rep_id,
        "rep_name": rep_name,
        "territory": lead.territory,
        "product_interest": lead.product_interest,
        "routing_status": status,
        "message": explanation,
    }

