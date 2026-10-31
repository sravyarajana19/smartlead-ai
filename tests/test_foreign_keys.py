import pytest
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from backend.core.database import SessionLocal
from backend.models.entities import Contact


def test_sqlite_foreign_key_enforcement():
    db = SessionLocal()
    try:
        # Non-existent company ID should fail foreign key pragma constraint
        invalid_contact = Contact(
            id="CON-TEST-FAIL-001",
            company_id="CO-NON-EXISTENT-999999",
            first_name="Ghost",
            last_name="User",
            email="ghost@nonexistent.com",
            job_title="Tester",
            seniority_level="Manager",
            department="IT",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.add(invalid_contact)
        with pytest.raises(IntegrityError):
            db.commit()
    finally:
        db.rollback()
        db.close()
