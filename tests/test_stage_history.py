from datetime import datetime, timedelta
from backend.services.opportunity_service import OpportunityManagementService


def test_case_5_missing_stage_transition_detection():
    # An opportunity that skipped Qualified, Proposal, Negotiation
    now = datetime.utcnow()
    records = [
        {"to_stage": "New", "transition_date": now - timedelta(days=5)},
        {"to_stage": "Won", "transition_date": now},
    ]

    anomaly = OpportunityManagementService.detect_case_5_stage_history_anomaly("OPP-001", records)
    assert anomaly is not None
    assert anomaly["issue_type"] == "CASE_5_MISSING_STAGE_TRANSITION"
    assert anomaly["ground_truth_label"] == "MISSING_STAGE_TRANSITIONS"
    assert "Qualified" in anomaly["missing_stages"]
    assert "Proposal" in anomaly["missing_stages"]


def test_valid_stage_history_passes():
    now = datetime.utcnow()
    records = [
        {"to_stage": "New", "transition_date": now - timedelta(days=20)},
        {"to_stage": "Qualified", "transition_date": now - timedelta(days=15)},
        {"to_stage": "Proposal", "transition_date": now - timedelta(days=10)},
        {"to_stage": "Negotiation", "transition_date": now - timedelta(days=5)},
        {"to_stage": "Won", "transition_date": now},
    ]

    anomaly = OpportunityManagementService.detect_case_5_stage_history_anomaly("OPP-002", records)
    assert anomaly is None
