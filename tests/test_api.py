import pytest
from backend.main import health_check, root
from backend.core.database import SessionLocal
from backend.routers.dashboard import get_dashboard_metrics
from backend.routers.leads import list_leads, get_lead
from backend.routers.scoring import score_lead, list_rules, get_active_rule
from backend.routers.consent import check_lead_consent
from backend.routers.exceptions import list_exceptions
from backend.routers.validation import execute_validation_checks
from backend.routers.sales_reps import list_sales_reps
from backend.routers.opportunities import list_opportunities


@pytest.fixture(scope="module")
def db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def test_health_check_endpoint():
    res = health_check()
    assert res["status"] == "healthy"
    assert "SmartLead" in res["service"] or "SMARTLEAD" in res["service"]


def test_root_endpoint():
    res = root()
    assert res["status"] == "online"
    assert res["documentation"] == "/docs"


def test_dashboard_metrics_endpoint(db):
    metrics = get_dashboard_metrics(db=db)
    assert metrics["total_leads"] > 0
    assert metrics["total_opportunities"] > 0
    assert metrics["conversion_rate"] >= 0.0
    assert "funnel_stages" in metrics


def test_leads_list_and_get_endpoint(db):
    res = list_leads(page=1, page_size=10, db=db)
    items = res["items"]
    assert len(items) > 0
    assert len(items) <= 10

    first_id = items[0].id
    lead = get_lead(lead_id=first_id, db=db)
    assert lead.id == first_id
    assert lead.company_id is not None


def test_scoring_endpoints(db):
    rules = list_rules(db=db)
    assert len(rules) > 0

    active_rule = get_active_rule(db=db)
    assert active_rule.is_active is True

    # Test score lead
    leads_res = list_leads(page=1, page_size=1, db=db)
    lead_id = leads_res["items"][0].id

    score_res = score_lead(lead_id=lead_id, db=db)
    assert "lead_score" in score_res
    assert "priority" in score_res
    assert 0.0 <= score_res["lead_score"] <= 100.0


def test_consent_check_endpoint(db):
    leads_res = list_leads(page=1, page_size=1, db=db)
    lead_id = leads_res["items"][0].id

    res = check_lead_consent(lead_id=lead_id, db=db)
    assert "is_permitted" in res
    assert "consent_status" in res


def test_exceptions_endpoint(db):
    res = list_exceptions(db=db)
    assert "total_anomalies" in res
    assert "case_breakdown" in res
    assert res["total_anomalies"] > 0


def test_validation_endpoint(db):
    res = execute_validation_checks(db=db)
    assert res["total_records_checked"] > 0
    assert res["validation_status"] in {"ALL_PASSED", "VALIDATED_WITH_LABELLED_ANOMALIES"}
