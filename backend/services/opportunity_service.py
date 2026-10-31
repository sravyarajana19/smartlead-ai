from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple


VALID_STAGE_ORDER = ["New", "Qualified", "Proposal", "Negotiation", "Won", "Lost"]

# Allowed direct stage transitions
ALLOWED_TRANSITIONS = {
    None: ["New"],
    "New": ["Qualified", "Lost"],
    "Qualified": ["Proposal", "Lost"],
    "Proposal": ["Negotiation", "Lost"],
    "Negotiation": ["Won", "Lost"],
    "Won": [],  # Terminal state
    "Lost": [],  # Terminal state
}


class OpportunityManagementService:
    """
    Opportunity Lifecycle and Stage History Management Service.
    Enforces valid state machine transitions and audit history.
    Detects CASE 5: Missing or invalid stage transitions.
    """

    @staticmethod
    def validate_transition(from_stage: Optional[str], to_stage: str) -> Tuple[bool, Optional[str]]:
        """Check if transition from one stage to another is standard."""
        allowed = ALLOWED_TRANSITIONS.get(from_stage, [])
        if to_stage in allowed:
            return True, None
        return False, f"Invalid stage transition: '{from_stage}' -> '{to_stage}'. Standard flow requires sequential progression."

    @staticmethod
    def detect_case_5_stage_history_anomaly(
        opportunity_id: str,
        stage_history_records: List[Dict[str, Any]],
    ) -> Optional[Dict[str, Any]]:
        """
        CASE 5 Detection:
        Examines the sequence of stage transitions for an opportunity.
        If an opportunity reached 'Won' or 'Negotiation' without visiting required preceding stages
        (e.g., jumping from 'New' straight to 'Won'), flag Case 5.
        """
        if not stage_history_records:
            return None

        # Sort transitions by transition_date
        sorted_records = sorted(
            stage_history_records,
            key=lambda x: x.get("transition_date") or datetime.min
        )

        visited_stages = [r.get("to_stage") for r in sorted_records]

        # If it reached Won
        if "Won" in visited_stages:
            required = ["Qualified", "Proposal", "Negotiation"]
            missing = [s for s in required if s not in visited_stages]
            if missing:
                return {
                    "issue_type": "CASE_5_MISSING_STAGE_TRANSITION",
                    "entity_id": opportunity_id,
                    "severity": "High",
                    "ground_truth_label": "MISSING_STAGE_TRANSITIONS",
                    "expected_decision": "LOG_INVALID_PROGRESSION",
                    "actual_decision": "STAGE_SKIPPED",
                    "explanation": (
                        f"Opportunity {opportunity_id} reached 'Won' but skipped mandatory sales pipeline stages: "
                        f"{', '.join(missing)}. Recorded progression: {visited_stages}."
                    ),
                    "missing_stages": missing,
                    "visited_stages": visited_stages,
                }

        # Check for invalid direct leaps recorded in histories
        for r in sorted_records:
            f_stage = r.get("from_stage")
            t_stage = r.get("to_stage")
            if not r.get("is_valid_transition", True) or (f_stage == "New" and t_stage == "Won"):
                return {
                    "issue_type": "CASE_5_MISSING_STAGE_TRANSITION",
                    "entity_id": opportunity_id,
                    "severity": "High",
                    "ground_truth_label": "MISSING_STAGE_TRANSITIONS",
                    "expected_decision": "LOG_INVALID_PROGRESSION",
                    "actual_decision": "STAGE_SKIPPED",
                    "explanation": (
                        f"Opportunity {opportunity_id} transitioned directly from '{f_stage}' to '{t_stage}' "
                        f"without intermediate qualification or proposal steps."
                    ),
                    "from_stage": f_stage,
                    "to_stage": t_stage,
                }

        return None
