from datetime import datetime, timedelta
from backend.services.dedup_service import DeduplicationService, normalize_phone


def test_phone_normalization():
    assert normalize_phone("(555) 123-4567") == "+15551234567"
    assert normalize_phone("+1-555-123-4567") == "+15551234567"
    assert normalize_phone(None) is None
    assert normalize_phone("") is None


def test_exact_email_duplicate():
    con1 = {"email": "alex.smith@acme.com", "phone": "+15551112222", "last_name": "Smith"}
    con2 = {"email": "alex.smith@acme.com", "phone": "+15553334444", "last_name": "Smith"}
    comp1 = {"domain": "acme.com"}
    comp2 = {"domain": "acme.com"}
    lead1 = {"product_interest": "Cloud Platform", "created_at": datetime(2025, 1, 1)}
    lead2 = {"product_interest": "Cloud Platform", "created_at": datetime(2025, 1, 5)}

    match = DeduplicationService.compare_leads(lead1, lead2, con1, con2, comp1, comp2)
    assert match is not None
    assert match["match_type"] == "Exact"
    assert match["is_duplicate"] is True


def test_legitimate_repeat_lead():
    # Same email, but different product and 200 days later
    con1 = {"email": "alex.smith@acme.com", "phone": "+15551112222", "last_name": "Smith"}
    con2 = {"email": "alex.smith@acme.com", "phone": "+15551112222", "last_name": "Smith"}
    comp1 = {"domain": "acme.com"}
    comp2 = {"domain": "acme.com"}
    lead1 = {"product_interest": "Cloud Platform", "created_at": datetime(2025, 1, 1)}
    lead2 = {"product_interest": "AI Analytics", "created_at": datetime(2025, 8, 15)}

    match = DeduplicationService.compare_leads(lead1, lead2, con1, con2, comp1, comp2)
    assert match is not None
    assert match["match_type"] == "Legitimate Repeat"
    assert match["is_duplicate"] is False


def test_case_4_duplicate_opportunity_detection():
    existing_opps = [
        {"id": "OPP-001", "current_stage": "Proposal"}
    ]
    anomaly = DeduplicationService.detect_duplicate_opportunity(
        lead_id="LEAD-002",
        is_lead_duplicate=True,
        existing_opportunities=existing_opps,
    )
    assert anomaly is not None
    assert anomaly["issue_type"] == "CASE_4_DUPLICATE_OPPORTUNITY"
    assert anomaly["canonical_opp_id"] == "OPP-001"
