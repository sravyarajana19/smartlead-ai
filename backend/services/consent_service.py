from datetime import datetime
from typing import Dict, Any, Optional, Tuple


class ConsentEnforcementService:
    """
    Marketing Consent Enforcement Service.
    Enforces GDPR/CCPA compliance and sales outreach rules.
    Rules:
    - Opted-out lead MUST NEVER receive contact follow-up tasks or outbound communication.
    - Consent checked before any task creation or simulated outreach.
    - High lead score NEVER overrides opt-out.
    - Detects CASE 1: Consent violation if outreach attempted on opted-out contact.
    """

    @staticmethod
    def verify_consent_for_outreach(
        lead_id: str,
        consent_record: Optional[Dict[str, Any]],
        lead_score: float = 0.0,
    ) -> Tuple[bool, Optional[str]]:
        """
        Check if contact outreach is legally permitted.
        Returns: (is_permitted, refusal_reason)
        """
        if not consent_record:
            # Pending or missing consent - cautious approach: requires explicit opt-in
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

        # Check expiry date
        expiry_date = consent_record.get("expiry_date")
        if expiry_date:
            if isinstance(expiry_date, str):
                try:
                    expiry_date = datetime.fromisoformat(expiry_date)
                except Exception:
                    pass
            if isinstance(expiry_date, datetime) and expiry_date < datetime.utcnow():
                return False, f"Consent for lead {lead_id} expired on {expiry_date.isoformat()}."

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
