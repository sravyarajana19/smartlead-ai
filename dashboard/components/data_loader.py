import sqlite3
import pandas as pd
from pathlib import Path
from backend.core.config import DATABASE_PATH


def get_db_connection():
    """Returns raw SQLite connection for high performance read queries."""
    return sqlite3.connect(DATABASE_PATH)


def load_table(table_name: str) -> pd.DataFrame:
    """Reads table into Pandas DataFrame."""
    conn = get_db_connection()
    try:
        df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
        return df
    finally:
        conn.close()


def load_all_dashboard_data():
    """Loads all core entities for dashboard consumption."""
    conn = get_db_connection()
    try:
        leads = pd.read_sql("SELECT * FROM leads", conn)
        companies = pd.read_sql("SELECT * FROM companies", conn)
        contacts = pd.read_sql("SELECT * FROM contacts", conn)
        opportunities = pd.read_sql("SELECT * FROM opportunities", conn)
        sales_reps = pd.read_sql("SELECT * FROM sales_reps", conn)
        campaigns = pd.read_sql("SELECT * FROM campaigns", conn)
        activities = pd.read_sql("SELECT * FROM activities", conn)
        consents = pd.read_sql("SELECT * FROM consents", conn)
        tasks = pd.read_sql("SELECT * FROM tasks", conn)
        anomalies = pd.read_sql("SELECT * FROM anomaly_records", conn)
        stage_histories = pd.read_sql("SELECT * FROM stage_histories", conn)

        return {
            "leads": leads,
            "companies": companies,
            "contacts": contacts,
            "opportunities": opportunities,
            "sales_reps": sales_reps,
            "campaigns": campaigns,
            "activities": activities,
            "consents": consents,
            "tasks": tasks,
            "anomalies": anomalies,
            "stage_histories": stage_histories,
        }
    finally:
        conn.close()
