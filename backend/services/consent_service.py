from datetime import datetime, timezone
from typing import Dict, Any, Optional, Tuple


def _normalize_to_utc_naive(dt_val: Any) -> Optional[datetime]:
    """Converts string, date, or datetime (naive or aware) to UTC naive datetime."""
    if dt_val is None:
        return None
    if isinstance(dt_val, str):
        # Handle ISO strings with Z or offsets
        clean_str = dt_val.replace("Z", "+00:00")
        try:
            parsed = datetime.fromisoformat(clean_str)
        except Exception:
            return None
        if parsed.tzinfo is not None:
            return parsed.astimezone(timezone.utc).replace(tzinfo=None)
        return parsed
    if isinstance(dt_val, datetime):
        if dt_val.tzinfo is not None:
            return dt_val.astimezone(timezone.utc).replace(tzinfo=None)
        return dt_val
    return None


class ConsentEnforcementService:
    """
    Marketing Consent Enforcement Service.
    Enforces GDPR/CCPA compliance and sales outreach rules.
    Rules:
    - Opted-out lead MUST NEVER receive contact follow-up tasks or outbound communication.
    - Consent checked before any task creation or simulated outreach.
    - High lead score NEVER overrides opt-out.
    - Effective dates (effective_start <= action_time < expiry_date) strictly enforced.
    - Detects CASE 1: Consent violation if outreach attempted on opted-out contact.
    """

    @staticmethod
    def verify_consent_for_outreach(
        lead_id: str,
        consent_record: Optional[Dict[str, Any]],
        lead_score: float = 0.0,
        channel: Optional[str] = None,
        as_of: Optional[datetime] = None,
    ) -> Tuple[bool, Optional[str]]:
        """
        Check if contact outreach is legally permitted.
        Returns: (is_permitted, refusal_reason)
        """
        if not consent_record:
            return False, f"Consent record not found for lead {lead_id}. Outbound contact blocked (Requires Opt-In)."

        status = consent_record.get("consent_status", "Pending")
        opt_out_time = consent_record.get("opt_out_timestamp")

        if status == "Opt-Out" or opt_out_time is not None:
            reason = (
                f"LEGAL CONSENT VIOLATION: Lead {lead_id} opted out at {opt_out_time or 'Unknown'}. "
                f"Contact strictly forbidden. (Lead Score {lead_score} cannot override Opt-Out)."
            )
            return False, reason

        if status == "Pending":
            return False, f"Consent status for lead {lead_id} is Pending. Awaiting verification before outbound outreach."

        now = _normalize_to_utc_naive(as_of) or datetime.utcnow()

        # Check effective start date
        raw_effective = consent_record.get("effective_date") or consent_record.get("consent_date") or consent_record.get("created_at")
        if raw_effective:
            eff_dt = _normalize_to_utc_naive(raw_effective)
            if eff_dt is None and isinstance(raw_effective, str):
                return False, f"Consent record for lead {lead_id} has malformed effective date: {raw_effective}."
            if eff_dt and eff_dt > now:
                return False, f"Consent for lead {lead_id} is effective in the future ({eff_dt.isoformat()}) and is not yet active."

        # Check expiry date
        raw_expiry = consent_record.get("expiry_date")
        if raw_expiry:
            exp_dt = _normalize_to_utc_naive(raw_expiry)
            if exp_dt is None:
                return False, f"Consent record for lead {lead_id} has malformed expiry date: {raw_expiry}."
            if exp_dt < now:
                return False, f"Consent for lead {lead_id} expired on {exp_dt.isoformat()}."

        # Check channel scope if requested
        if channel:
            consent_type = consent_record.get("consent_type")
            if consent_type and consent_type not in {"All", channel}:
                return False, f"Consent type '{consent_type}' for lead {lead_id} does not authorize '{channel}' outreach."

        if status == "Opt-In":
            return True, None

        return False, f"Unknown consent status: {status}"

    @staticmethod
    def detect_case_1_consent_violation(
        task_data: Dict[str, Any],
        consent_record: Optional[Dict[str, Any]],
    ) -> Optional[Dict[str, Any]]:
        """
        CASE 1 Detection:
        If a task is created or contact attempted for an Opt-Out lead, flag Case 1 violation.
        """
        if not consent_record:
            return None

        status = consent_record.get("consent_status")
        if status == "Opt-Out":
            return {
                "issue_type": "CASE_1_CONSENT_VIOLATION",
                "entity_type": "Task",
                "entity_id": task_data.get("id") or task_data.get("lead_id"),
                "severity": "Critical",
                "ground_truth_label": "OPT_OUT_CONTACTED",
                "expected_decision": "BLOCK_OUTREACH",
                "actual_decision": "CONTACT_ATTEMPTED",
                "explanation": (
                    f"Lead {task_data.get('lead_id')} has explicit Opt-Out status. "
                    f"Attempted action '{task_data.get('task_type')}' violates privacy consent rules."
                ),
            }
        return None
