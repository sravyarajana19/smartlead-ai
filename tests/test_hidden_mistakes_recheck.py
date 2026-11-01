import pytest
import math
from datetime import datetime, timedelta, timezone
from backend.services.scoring_service import LeadScoringEngine
from backend.services.consent_service import ConsentEnforcementService
from backend.services.dedup_service import DeduplicationService
from backend.services.opportunity_service import OpportunityManagementService
from generator.anomaly_injector import AnomalyInjector
from backend.schemas.pydantic_models import StageTransitionRequest
from backend.routers.opportunities import transition_opportunity_stage
from backend.routers.routing import route_lead_endpoint
from backend.routers.tasks import create_follow_up_task
from backend.schemas.pydantic_models import RoutingRequest, TaskCreate
from backend.models.entities import Lead, SalesRep, Opportunity, Consent, Task, Company
from backend.core.database import SessionLocal, ensure_database_initialized
from fastapi import HTTPException
from pydantic import ValidationError


@pytest.fixture(scope="module")
def db_session():
    ensure_database_initialized()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_h12_scoring_weights_validation():
    """H12: Test that invalid scoring weights (-1, 1, 1), NaN, >1 are strictly rejected."""
    # Negative weight summing to 1.0
    with pytest.raises(ValueError, match="between 0.0 and 1.0"):
        LeadScoringEngine(fit_weight=-1.0, intent_weight=1.0, engagement_weight=1.0)

    # Weight greater than 1.0
    with pytest.raises(ValueError, match="between 0.0 and 1.0"):
        LeadScoringEngine(fit_weight=1.2, intent_weight=-0.1, engagement_weight=-0.1)

    # NaN weight
    with pytest.raises(ValueError, match="must be a finite number"):
        LeadScoringEngine(fit_weight=float("nan"), intent_weight=0.5, engagement_weight=0.5)

    # Valid weights must pass
    engine = LeadScoringEngine(fit_weight=0.40, intent_weight=0.35, engagement_weight=0.25)
    assert engine.fit_weight == 0.40


def test_h03_consent_future_malformed_and_timezone_aware():
    """H03: Test that future effective consent, malformed dates, and aware datetimes are handled safely."""
    # 1. Future consent (2099) must be blocked
    future_record = {
        "consent_status": "Opt-In",
        "effective_date": datetime(2099, 1, 1),
    }
    allowed, reason = ConsentEnforcementService.verify_consent_for_outreach("LEAD-001", future_record)
    assert not allowed
    assert "future" in reason.lower()

    # 2. Malformed expiry string must be blocked, NOT allowed
    malformed_record = {
        "consent_status": "Opt-In",
        "expiry_date": "nonsense-date-format",
    }
    allowed, reason = ConsentEnforcementService.verify_consent_for_outreach("LEAD-002", malformed_record)
    assert not allowed
    assert "malformed" in reason.lower()

    # 3. Timezone-aware expiry string or datetime must compare cleanly without TypeError
    aware_record = {
        "consent_status": "Opt-In",
        "expiry_date": "2030-12-31T23:59:59+00:00",
    }
    allowed, reason = ConsentEnforcementService.verify_consent_for_outreach("LEAD-003", aware_record)
    assert allowed
    assert reason is None

    # 4. Channel scoping: Email-only consent must block Phone outreach
    channel_record = {
        "consent_status": "Opt-In",
        "consent_type": "Email",
    }
    phone_allowed, phone_reason = ConsentEnforcementService.verify_consent_for_outreach("LEAD-004", channel_record, channel="Phone")
    assert not phone_allowed
    assert "does not authorize 'Phone'" in phone_reason


def test_h01_routing_endpoint_response_and_idempotency(db_session):
    """H01: Test that routing endpoint commits changes and returns 200 without KeyError: 'id'."""
    lead = db_session.query(Lead).first()
    assert lead is not None

    req = RoutingRequest(lead_id=lead.id)
    resp = route_lead_endpoint(req, db=db_session)

    assert resp["lead_id"] == lead.id
    assert resp["routing_status"] in {"Assigned", "Fallback_Territory_Only", "No_Capacity", "Fallback_Unassigned"}
    if resp["assigned_rep_id"]:
        assert resp["rep_name"] is not None

    # Test idempotency: re-running routing for same lead does not double-count global load
    total_load_before = sum(r.current_load for r in db_session.query(SalesRep).all())
    route_lead_endpoint(req, db=db_session)
    total_load_after = sum(r.current_load for r in db_session.query(SalesRep).all())
    assert total_load_after == total_load_before


def test_h02_stage_transition_validation(db_session):
    """H02: Test that invalid stages ('Banana'), missing reasons, and invalid leaps are rejected."""
    opp = db_session.query(Opportunity).filter(Opportunity.current_stage == "New").first()
    if not opp:
        opp = db_session.query(Opportunity).first()
        opp.current_stage = "New"
        db_session.commit()

    # 1. Pydantic validation rejects 'Banana'
    with pytest.raises(ValidationError):
        StageTransitionRequest(new_stage="Banana")

    # 2. Direct leap New -> Won is rejected by state machine
    leap_req = StageTransitionRequest(new_stage="Won", won_lost_reason="Skipped everything")
    with pytest.raises(HTTPException) as exc_info:
        transition_opportunity_stage(opp.id, leap_req, db=db_session)
    assert exc_info.value.status_code == 400

    # 3. Transition to Won without won_lost_reason is rejected
    opp.current_stage = "Negotiation"
    db_session.commit()
    no_reason_req = StageTransitionRequest(new_stage="Won", won_lost_reason=None)
    with pytest.raises(HTTPException) as exc_info:
        transition_opportunity_stage(opp.id, no_reason_req, db=db_session)
    assert exc_info.value.status_code == 400


def test_h09_duplicate_opportunity_matching():
    """H09: Test that duplicate opportunity detector strictly checks company/product matching."""
    unrelated_opps = [
        {
            "id": "OPP-999",
            "company_id": "CO-OTHER",
            "lead_id": "LEAD-OTHER",
            "current_stage": "Proposal",
        }
    ]

    # Given a duplicate lead but an unrelated active deal, should NOT match
    match = DeduplicationService.detect_duplicate_opportunity(
        lead_id="LEAD-001",
        is_lead_duplicate=True,
        existing_opportunities=unrelated_opps,
        company_id="CO-001",
        canonical_lead_id="LEAD-ORIGINAL",
    )
    assert match is None

    # Given a matching company opportunity, should match
    matching_opps = [
        {
            "id": "OPP-100",
            "company_id": "CO-001",
            "lead_id": "LEAD-ORIGINAL",
            "current_stage": "Proposal",
        }
    ]
    match2 = DeduplicationService.detect_duplicate_opportunity(
        lead_id="LEAD-001",
        is_lead_duplicate=True,
        existing_opportunities=matching_opps,
        company_id="CO-001",
        canonical_lead_id="LEAD-ORIGINAL",
    )
    assert match2 is not None
    assert match2["canonical_opp_id"] == "OPP-100"


def test_h11_anomaly_injector_alias():
    """H11: Test that inject_all and inject_all_cases are both available and callable."""
    sample_data = {
        "leads": [{"id": "LEAD-001", "created_at": datetime.utcnow(), "territory": "North America", "assigned_rep_id": "REP-001"}],
        "consents": [{"lead_id": "LEAD-001", "consent_status": "Opt-In"}],
        "tasks": [],
        "activities": [],
        "sales_reps": [{"id": "REP-001", "territory": "North America"}],
        "opportunities": [],
        "stage_histories": [],
    }
    injector = AnomalyInjector(sample_data)
    assert hasattr(injector, "inject_all")
    assert hasattr(injector, "inject_all_cases")


def test_h03_opt_out_task_creation_returns_403_not_500(db_session):
    """H03: Test that attempting to create a task for an opted-out lead returns 403 without KeyError: 'entity_type'."""
    # Find an opted out lead
    opt_out_consent = db_session.query(Consent).filter(Consent.consent_status == "Opt-Out").first()
    if not opt_out_consent:
        # Create one if not found
        lead = db_session.query(Lead).first()
        opt_out_consent = db_session.query(Consent).filter(Consent.lead_id == lead.id).first()
        opt_out_consent.consent_status = "Opt-Out"
        opt_out_consent.opt_out_timestamp = datetime.utcnow()
        db_session.commit()

    task_in = TaskCreate(
        lead_id=opt_out_consent.lead_id,
        task_type="Discovery Call",
        priority="Urgent",
    )

    with pytest.raises(HTTPException) as exc_info:
        create_follow_up_task(task_in, db=db_session)

    assert exc_info.value.status_code == 403
    assert "LEGAL CONSENT VIOLATION" in exc_info.value.detail

