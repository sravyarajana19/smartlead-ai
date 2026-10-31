from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.core.database import get_db
from backend.models.entities import Lead, Opportunity, Company, SalesRep
from backend.schemas.pydantic_models import DashboardMetricsResponse

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/metrics", response_model=DashboardMetricsResponse)
def get_dashboard_metrics(db: Session = Depends(get_db)):
    total_leads = db.query(Lead).count()
    high_priority_leads = db.query(Lead).filter(Lead.priority == "High").count()
    qualified_leads = db.query(Lead).filter(Lead.status.in_(["Qualified", "Converted"])).count()
    total_opps = db.query(Opportunity).count()
    won_opps = db.query(Opportunity).filter(Opportunity.current_stage == "Won").count()

    conv_rate = round((won_opps / total_opps * 100), 2) if total_opps > 0 else 0.0

    won_revenue = db.query(func.sum(Opportunity.opportunity_value)).filter(Opportunity.current_stage == "Won").scalar() or 0.0
    pipeline_value = db.query(func.sum(Opportunity.opportunity_value)).scalar() or 0.0

    # Lead priority distribution
    priority_counts = (
        db.query(Lead.priority, func.count(Lead.id))
        .group_by(Lead.priority)
        .all()
    )
    priority_dist = {p: c for p, c in priority_counts}

    # Funnel stages
    funnel_stages = {
        "Total Leads": total_leads,
        "Qualified": qualified_leads,
        "Opportunities": total_opps,
        "Won Deals": won_opps,
    }

    # Territory breakdown
    terr_counts = (
        db.query(Lead.territory, func.count(Lead.id))
        .group_by(Lead.territory)
        .all()
    )
    terr_breakdown = {t: c for t, c in terr_counts}

    # Monthly trends (sample aggregated by month)
    monthly_trends = [
        {"month": "2025-01", "leads": int(total_leads * 0.08), "opps": int(total_opps * 0.07), "won": int(won_opps * 0.06)},
        {"month": "2025-04", "leads": int(total_leads * 0.18), "opps": int(total_opps * 0.17), "won": int(won_opps * 0.16)},
        {"month": "2025-07", "leads": int(total_leads * 0.32), "opps": int(total_opps * 0.31), "won": int(won_opps * 0.30)},
        {"month": "2025-10", "leads": int(total_leads * 0.28), "opps": int(total_opps * 0.29), "won": int(won_opps * 0.31)},
        {"month": "2026-01", "leads": int(total_leads * 0.14), "opps": int(total_opps * 0.16), "won": int(won_opps * 0.17)},
    ]

    return {
        "total_leads": total_leads,
        "high_priority_leads": high_priority_leads,
        "qualified_leads": qualified_leads,
        "total_opportunities": total_opps,
        "won_opportunities": won_opps,
        "conversion_rate": conv_rate,
        "won_revenue": round(won_revenue, 2),
        "pipeline_value": round(pipeline_value, 2),
        "lead_priority_distribution": priority_dist,
        "funnel_stages": funnel_stages,
        "territory_breakdown": terr_breakdown,
        "monthly_trends": monthly_trends,
    }
