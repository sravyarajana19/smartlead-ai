from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from backend.services.consent_service import ConsentEnforcementService


class TaskManagementService:
    """
    Follow-up Task Management Service.
    Enforces consent validation, deduplication, and automated task prioritization.
    """

    @staticmethod
    def create_follow_up_task(
        lead: Dict[str, Any],
        consent_record: Optional[Dict[str, Any]],
        existing_tasks: List[Dict[str, Any]],
        task_type: Optional[str] = None,
        custom_priority: Optional[str] = None,
        assigned_rep_id: Optional[str] = None,
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str], Optional[Dict[str, Any]]]:
        """
        Creates a follow-up task adhering to consent and deduplication rules.
        Returns: (task_dict, error_message, anomaly_if_violation)
        """
        lead_id = lead.get("id")
        lead_priority = lead.get("priority", "Medium")
        lead_score = lead.get("lead_score", 0.0)
        rep_id = assigned_rep_id or lead.get("assigned_rep_id")

        if not rep_id:
            return None, f"Cannot create task for lead {lead_id}: No sales representative assigned.", None

        # 1. CONSENT ENFORCEMENT CHECK
        is_permitted, refusal_reason = ConsentEnforcementService.verify_consent_for_outreach(
            lead_id=lead_id,
            consent_record=consent_record,
            lead_score=lead_score,
        )

        # Check for Case 1 Anomaly
        case1_anomaly = None
        if consent_record and consent_record.get("consent_status") == "Opt-Out":
            case1_anomaly = ConsentEnforcementService.detect_case_1_consent_violation(
                task_data={"lead_id": lead_id, "task_type": task_type or "Outreach Call"},
                consent_record=consent_record,
            )

        if not is_permitted:
            return None, refusal_reason, case1_anomaly

        # 2. TASK DEDUPLICATION CHECK
        determined_type = task_type or ("Discovery Call" if lead_priority == "High" else "Email Outreach")
        for task in existing_tasks:
            if (
                task.get("lead_id") == lead_id
                and task.get("task_type") == determined_type
                and task.get("status") in {"Pending", "In Progress"}
            ):
                return None, f"Duplicate task rejected: Active '{determined_type}' already exists for lead {lead_id}.", None

        # 3. PRIORITY & SLA SCHEDULING
        if custom_priority:
            task_priority = custom_priority
        else:
            task_priority = "Urgent" if lead_priority == "High" else ("High" if lead_priority == "Medium" else "Normal")

        # SLA: Urgent = 1 day, High = 2 days, Normal = 5 days
        now = datetime.utcnow()
        if task_priority == "Urgent":
            due_date = now + timedelta(days=1)
        elif task_priority == "High":
            due_date = now + timedelta(days=2)
        else:
            due_date = now + timedelta(days=5)

        task_dict = {
            "lead_id": lead_id,
            "assigned_rep_id": rep_id,
            "task_type": determined_type,
            "priority": task_priority,
            "due_date": due_date,
            "status": "Pending",
            "blocked_reason": None,
            "is_consent_verified": True,
            "created_at": now,
        }

        return task_dict, None, None
