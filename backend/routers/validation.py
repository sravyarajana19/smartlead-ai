from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.core.database import get_db
from backend.services.validation_service import ValidationEngine
from backend.schemas.pydantic_models import ValidationSummaryResponse

router = APIRouter(prefix="/api/validation", tags=["Validation"])


@router.get("/run", response_model=ValidationSummaryResponse)
def execute_validation_checks(db: Session = Depends(get_db)):
    engine = ValidationEngine(db)
    results = engine.run_all_checks()

    return {
        "total_records_checked": results["total_records_checked"],
        "passed_checks": results["passed_checks"],
        "failed_checks": results["failed_checks"],
        "warnings": results["warnings"],
        "detected_anomalies": results["detected_anomalies"],
        "validation_status": results["validation_status"],
        "case_breakdown": results["case_breakdown"],
        "details": results["check_details"],
    }
