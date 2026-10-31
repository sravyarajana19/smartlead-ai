from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.core.database import get_db
from backend.models.entities import Lead, Company, Contact, Activity, ScoreRule
from backend.services.scoring_service import LeadScoringEngine
from backend.schemas.pydantic_models import ScoreExplanation

router = APIRouter(prefix="/api/scoring", tags=["Scoring"])


@router.get("/rules")
def list_rules(db: Session = Depends(get_db)):
    return db.query(ScoreRule).all()


@router.get("/rules/active")
def get_active_rule(db: Session = Depends(get_db)):
    rule = db.query(ScoreRule).filter(ScoreRule.is_active == True).first()
    if not rule:
        raise HTTPException(status_code=404, detail="No active score rule configured")
    return rule


@router.get("/lead/{lead_id}", response_model=ScoreExplanation)
def score_lead(lead_id: str, db: Session = Depends(get_db)):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail=f"Lead {lead_id} not found")

    company = db.query(Company).filter(Company.id == lead.company_id).first()
    contact = db.query(Contact).filter(Contact.id == lead.contact_id).first()
    activities = db.query(Activity).filter(Activity.lead_id == lead_id).all()

    rule = db.query(ScoreRule).filter(ScoreRule.is_active == True).first()
    engine = LeadScoringEngine(
        fit_weight=rule.fit_weight if rule else 0.40,
        intent_weight=rule.intent_weight if rule else 0.35,
        engagement_weight=rule.engagement_weight if rule else 0.25,
        rule_version=rule.rule_version if rule else "v1.0.0",
    )

    act_dicts = [a.__dict__ for a in activities]
    comp_dict = company.__dict__ if company else {}
    con_dict = contact.__dict__ if contact else {}
    lead_dict = lead.__dict__

    result = engine.evaluate_lead_full(
        lead_id=lead_id,
        company_data=comp_dict,
        contact_data=con_dict,
        lead_data=lead_dict,
        activities=act_dicts,
        converted_date=lead.converted_date,
        filter_post_conversion=True,
    )

    return result
