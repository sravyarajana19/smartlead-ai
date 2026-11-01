from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import declarative_base, sessionmaker
from backend.core.config import DATABASE_URL, DATA_DIR, DATABASE_PATH, CSV_EXPORTS_DIR

DATA_DIR.mkdir(parents=True, exist_ok=True)

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False
)

# Enable foreign key constraint enforcement in SQLite
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

_DB_INITIALIZED = False


def ensure_database_initialized():
    """Ensures database schema and starter data exist (crucial for cloud deployments like Streamlit Cloud)."""
    global _DB_INITIALIZED
    if _DB_INITIALIZED and DATABASE_PATH.exists():
        return

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    needs_init = False

    if not DATABASE_PATH.exists() or DATABASE_PATH.stat().st_size == 0:
        needs_init = True
    else:
        try:
            import sqlite3
            with sqlite3.connect(DATABASE_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='leads'")
                res = cursor.fetchone()
                if not res or res[0] == 0:
                    needs_init = True
                else:
                    cursor.execute("SELECT count(*) FROM leads")
                    count_res = cursor.fetchone()
                    if not count_res or count_res[0] == 0:
                        needs_init = True
        except Exception:
            needs_init = True

    if needs_init:
        print("[Auto-Init] Initializing database schema and populating records...")
        import backend.models.entities  # Ensure all SQLAlchemy models are registered
        Base.metadata.create_all(bind=engine)

        if CSV_EXPORTS_DIR.exists() and (CSV_EXPORTS_DIR / "leads.csv").exists():
            import sqlite3
            import pandas as pd
            insert_order = [
                "score_rules", "campaigns", "sales_reps", "companies",
                "contacts", "leads", "activities", "consents",
                "consent_histories", "duplicate_relationships", "tasks",
                "opportunities", "stage_histories", "anomaly_records"
            ]
            with sqlite3.connect(DATABASE_PATH) as conn:
                cursor = conn.cursor()
                for table in insert_order:
                    csv_path = CSV_EXPORTS_DIR / f"{table}.csv"
                    if csv_path.exists():
                        df = pd.read_csv(csv_path)
                        cursor.execute(f"PRAGMA table_info({table})")
                        valid_cols = [row[1] for row in cursor.fetchall()]
                        matching_cols = [c for c in df.columns if c in valid_cols]
                        if matching_cols:
                            df[matching_cols].to_sql(table, conn, if_exists="append", index=False)
            print("[Auto-Init] Successfully seeded database from CSV exports.")
        else:
            from generator.synthetic_data import SyntheticDataGenerator
            from generator.anomaly_injector import AnomalyInjector
            from scripts.generate_data import populate_database
            gen = SyntheticDataGenerator(scale="small")
            data = gen.generate_all()
            injector = AnomalyInjector(data)
            data, anomalies = injector.inject_all_cases()
            populate_database(data, anomalies)
            print("[Auto-Init] Database populated via synthetic generator fallback.")

    _DB_INITIALIZED = True


def get_db():
    ensure_database_initialized()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

