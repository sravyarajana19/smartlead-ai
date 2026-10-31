from backend.core.database import SessionLocal
from backend.services.validation_service import ValidationEngine


def test_validation_engine_execution():
    db = SessionLocal()
    try:
        engine = ValidationEngine(db)
        results = engine.run_all_checks()

        assert results["total_records_checked"] > 0
        assert results["passed_checks"] > 0
        assert results["failed_checks"] == 0
        assert results["validation_status"] in {"ALL_PASSED", "VALIDATED_WITH_LABELLED_ANOMALIES"}
        assert "CASE_1_CONSENT_VIOLATION" in results["case_breakdown"]
    finally:
        db.close()
