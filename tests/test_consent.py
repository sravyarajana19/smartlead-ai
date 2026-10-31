from datetime import datetime
from backend.services.consent_service import ConsentEnforcementService


def test_opt_in_allows_contact():
    consent = {
        "consent_status": "Opt-In",
        "opt_out_timestamp": None,
        "expiry_date": datetime(2027, 1, 1),
    }
    permitted, reason = ConsentEnforcementService.verify_consent_for_outreach("LEAD-001", consent, lead_score=85.0)
    assert permitted is True
    assert reason is None


def test_opt_out_strictly_blocks_contact():
    consent = {
        "consent_status": "Opt-Out",
        "opt_out_timestamp": datetime(2026, 1, 10, 10, 0, 0),
    }
    # Even with a maximum lead score of 100, contact MUST be blocked!
    permitted, reason = ConsentEnforcementService.verify_consent_for_outreach("LEAD-001", consent, lead_score=100.0)
    assert permitted is False
    assert "LEGAL CONSENT VIOLATION" in reason
    assert "cannot override Opt-Out" in reason


def test_missing_or_pending_consent_blocks_contact():
    permitted, reason = ConsentEnforcementService.verify_consent_for_outreach("LEAD-002", None, lead_score=90.0)
    assert permitted is False

    pending_consent = {"consent_status": "Pending"}
    p_perm, p_reason = ConsentEnforcementService.verify_consent_for_outreach("LEAD-003", pending_consent, lead_score=90.0)
    assert p_perm is False


def test_case_1_consent_violation_detection():
    task_data = {"id": "TASK-001", "lead_id": "LEAD-001", "task_type": "Discovery Call"}
    consent = {"consent_status": "Opt-Out", "opt_out_timestamp": datetime(2026, 1, 10)}

    anomaly = ConsentEnforcementService.detect_case_1_consent_violation(task_data, consent)
    assert anomaly is not None
    assert anomaly["issue_type"] == "CASE_1_CONSENT_VIOLATION"
    assert anomaly["ground_truth_label"] == "OPT_OUT_CONTACTED"
    assert anomaly["expected_decision"] == "BLOCK_OUTREACH"
