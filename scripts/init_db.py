import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.core.database import engine, Base
from backend.models import *


def init_database():
    print("Initializing SmartLead AI database schema...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully with foreign key constraints enabled.")


if __name__ == "__main__":
    init_database()
