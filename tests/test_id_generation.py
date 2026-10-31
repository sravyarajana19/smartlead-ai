import pytest
from generator.id_generator import (
    generate_company_id,
    generate_contact_id,
    generate_lead_id,
    generate_activity_id,
    generate_opportunity_id,
    generate_task_id,
    generate_campaign_id,
    generate_sales_rep_id,
    generate_consent_id,
    generate_score_rule_id,
    generate_stage_history_id,
    generate_anomaly_id,
)


def test_company_id_format():
    assert generate_company_id(1) == "CO-000001"
    assert generate_company_id(5000) == "CO-005000"


def test_contact_id_format():
    assert generate_contact_id(1) == "CON-000001"
    assert generate_contact_id(10000) == "CON-010000"


def test_lead_id_format():
    assert generate_lead_id(1, year=2026) == "LEAD-2026-000001"
    assert generate_lead_id(20000, year=2026) == "LEAD-2026-020000"


def test_activity_id_format():
    lead_id = "LEAD-2026-000001"
    assert generate_activity_id(lead_id, 1) == "ACT-LEAD-2026-000001-001"
    assert generate_activity_id(lead_id, 99) == "ACT-LEAD-2026-000001-099"


def test_opportunity_id_format():
    assert generate_opportunity_id(1, year=2026) == "OPP-2026-000001"
    assert generate_opportunity_id(3000, year=2026) == "OPP-2026-003000"


def test_task_id_format():
    lead_id = "LEAD-2026-000001"
    assert generate_task_id(lead_id, 1) == "TASK-LEAD-2026-000001-001"


def test_all_auxiliary_id_formats():
    assert generate_campaign_id(1) == "CMP-000001"
    assert generate_sales_rep_id(1) == "REP-000001"
    assert generate_consent_id(1) == "CNS-000001"
    assert generate_score_rule_id(1) == "SCR-000001"
    assert generate_stage_history_id("OPP-2026-000001", 1) == "STG-OPP-2026-000001-001"
    assert generate_anomaly_id(1) == "ANM-000001"
