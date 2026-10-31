"""
Deterministic, immutable and zero-padded ID Generator for SmartLead AI.
Adheres strictly to the specification ID formats:
- Company: CO-000001
- Contact: CON-000001
- Lead: LEAD-2026-000001
- Activity: ACT-LEAD-2026-000001-001
- Opportunity: OPP-2026-000001
- Task: TASK-LEAD-2026-000001-001
- Campaign: CMP-000001
- SalesRep: REP-000001
- Consent: CNS-000001
- ScoreRule: SCR-000001
- StageHistory: STG-OPP-2026-000001-001
- Duplicate: DUP-000001
- Anomaly: ANM-000001
- ConsentHistory: CNH-000001
"""

def generate_company_id(index: int) -> str:
    """CO-000001"""
    return f"CO-{index:06d}"

def generate_contact_id(index: int) -> str:
    """CON-000001"""
    return f"CON-{index:06d}"

def generate_lead_id(index: int, year: int = 2026) -> str:
    """LEAD-2026-000001"""
    return f"LEAD-{year}-{index:06d}"

def generate_activity_id(lead_id: str, sequence: int) -> str:
    """ACT-LEAD-2026-000001-001"""
    return f"ACT-{lead_id}-{sequence:03d}"

def generate_opportunity_id(index: int, year: int = 2026) -> str:
    """OPP-2026-000001"""
    return f"OPP-{year}-{index:06d}"

def generate_task_id(lead_id: str, sequence: int) -> str:
    """TASK-LEAD-2026-000001-001"""
    return f"TASK-{lead_id}-{sequence:03d}"

def generate_campaign_id(index: int) -> str:
    """CMP-000001"""
    return f"CMP-{index:06d}"

def generate_sales_rep_id(index: int) -> str:
    """REP-000001"""
    return f"REP-{index:06d}"

def generate_consent_id(index: int) -> str:
    """CNS-000001"""
    return f"CNS-{index:06d}"

def generate_score_rule_id(index: int) -> str:
    """SCR-{index:06d}"""
    return f"SCR-{index:06d}"

def generate_stage_history_id(opp_id: str, sequence: int) -> str:
    """STG-OPP-2026-000001-001"""
    return f"STG-{opp_id}-{sequence:03d}"

def generate_duplicate_id(index: int) -> str:
    """DUP-000001"""
    return f"DUP-{index:06d}"

def generate_anomaly_id(index: int) -> str:
    """ANM-000001"""
    return f"ANM-{index:06d}"

def generate_consent_history_id(index: int) -> str:
    """CNH-000001"""
    return f"CNH-{index:06d}"
