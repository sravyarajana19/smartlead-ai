from datetime import datetime
from backend.services.task_service import TaskManagementService


def test_task_creation_with_valid_consent():
    lead = {
        "id": "LEAD-001",
        "priority": "High",
        "lead_score": 85.0,
        "assigned_rep_id": "REP-001",
    }
    consent = {
        "consent_status": "Opt-In",
        "expiry_date": datetime(2027, 1, 1),
    }

    task, err, anom = TaskManagementService.create_follow_up_task(
        lead=lead,
        consent_record=consent,
        existing_tasks=[],
    )
    assert err is None
    assert task is not None
    assert task["task_type"] == "Discovery Call"
    assert task["priority"] == "Urgent"
    assert task["is_consent_verified"] is True


def test_task_creation_blocked_by_opt_out():
    lead = {
        "id": "LEAD-002",
        "priority": "High",
        "lead_score": 95.0,
        "assigned_rep_id": "REP-001",
    }
    consent = {
        "consent_status": "Opt-Out",
        "opt_out_timestamp": datetime(2026, 1, 1),
    }

    task, err, anom = TaskManagementService.create_follow_up_task(
        lead=lead,
        consent_record=consent,
        existing_tasks=[],
    )
    assert task is None
    assert "LEGAL CONSENT VIOLATION" in err
    assert anom is not None
    assert anom["issue_type"] == "CASE_1_CONSENT_VIOLATION"


def test_task_deduplication():
    lead = {
        "id": "LEAD-003",
        "priority": "Medium",
        "lead_score": 60.0,
        "assigned_rep_id": "REP-001",
    }
    consent = {"consent_status": "Opt-In"}
    existing = [
        {"lead_id": "LEAD-003", "task_type": "Email Outreach", "status": "Pending"}
    ]

    task, err, anom = TaskManagementService.create_follow_up_task(
        lead=lead,
        consent_record=consent,
        existing_tasks=existing,
        task_type="Email Outreach",
    )
    assert task is None
    assert "Duplicate task rejected" in err
