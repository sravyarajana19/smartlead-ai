from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from backend.core.database import get_db
from backend.models.entities import Task, Lead, Consent, AnomalyRecord
from backend.schemas.pydantic_models import TaskOut, TaskCreate, PaginatedResponse, PaginationMeta
from backend.services.task_service import TaskManagementService
from generator.id_generator import generate_task_id, generate_anomaly_id

router = APIRouter(prefix="/api/tasks", tags=["Tasks"])


@router.get("", response_model=PaginatedResponse)
def list_tasks(
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    status: Optional[str] = None,
    priority: Optional[str] = None,
    lead_id: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(Task)
    if status:
        query = query.filter(Task.status == status)
    if priority:
        query = query.filter(Task.priority == priority)
    if lead_id:
        query = query.filter(Task.lead_id == lead_id)

    total = query.count()
    items = query.order_by(Task.due_date.asc()).offset((page - 1) * page_size).limit(page_size).all()
    total_pages = (total + page_size - 1) // page_size

    return {
        "items": [TaskOut.model_validate(t) for t in items],
        "meta": PaginationMeta(total_records=total, page=page, page_size=page_size, total_pages=total_pages),
    }


@router.post("", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
def create_follow_up_task(task_in: TaskCreate, db: Session = Depends(get_db)):
    lead = db.query(Lead).filter(Lead.id == task_in.lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail=f"Lead {task_in.lead_id} not found")

    consent = db.query(Consent).filter(Consent.lead_id == task_in.lead_id).first()
    existing_tasks = db.query(Task).filter(Task.lead_id == task_in.lead_id).all()

    task_dict, error_msg, anomaly = TaskManagementService.create_follow_up_task(
        lead=lead.__dict__,
        consent_record=consent.__dict__ if consent else None,
        existing_tasks=[t.__dict__ for t in existing_tasks],
        task_type=task_in.task_type,
        custom_priority=task_in.priority,
        assigned_rep_id=task_in.assigned_rep_id,
    )

    if error_msg:
        if anomaly:
            # Record Case 1 Anomaly
            anm_count = db.query(AnomalyRecord).count()
            db_anom = AnomalyRecord(
                id=generate_anomaly_id(anm_count + 1),
                entity_type=anomaly.get("entity_type", "Task"),
                entity_id=anomaly.get("entity_id", task_in.lead_id),
                issue_type=anomaly.get("issue_type", "CASE_1_CONSENT_VIOLATION"),
                severity=anomaly.get("severity", "Critical"),
                ground_truth_label=anomaly.get("ground_truth_label", "OPT_OUT_CONTACTED"),
                expected_decision=anomaly.get("expected_decision", "BLOCK_OUTREACH"),
                actual_decision=anomaly.get("actual_decision", "CONTACT_ATTEMPTED"),
                explanation=anomaly.get("explanation", error_msg),
            )
            db.add(db_anom)
            db.commit()

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN if "LEGAL CONSENT VIOLATION" in error_msg else status.HTTP_400_BAD_REQUEST,
            detail=error_msg,
        )

    # Generate sequential Task ID
    total_tasks = db.query(Task).filter(Task.lead_id == task_in.lead_id).count()
    task_id = generate_task_id(lead.id, total_tasks + 1)

    new_task = Task(
        id=task_id,
        lead_id=task_dict["lead_id"],
        assigned_rep_id=task_dict["assigned_rep_id"],
        task_type=task_dict["task_type"],
        priority=task_dict["priority"],
        due_date=task_dict["due_date"],
        status=task_dict["status"],
        blocked_reason=task_dict["blocked_reason"],
        is_consent_verified=task_dict["is_consent_verified"],
        created_at=task_dict["created_at"],
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    return new_task
