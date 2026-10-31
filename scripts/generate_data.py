import sys
import argparse
import time
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.core.database import SessionLocal, engine, Base
from backend.models.entities import (
    Company,
    Contact,
    Campaign,
    SalesRep,
    Lead,
    Activity,
    Consent,
    ScoreRule,
    Task,
    Opportunity,
    StageHistory,
    DuplicateRelationship,
    AnomalyRecord,
    ConsentHistory,
)
from generator.synthetic_data import SyntheticDataGenerator
from generator.anomaly_injector import AnomalyInjector
from generator.exporter import DataExporter


def populate_database(data: dict, anomalies: list):
    """Batch inserts generated records into the SQLite database."""
    print("Populating database with generated records...")
    db = SessionLocal()
    try:
        # Re-initialize clean tables
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)

        # Insert Master / Parent tables first
        db.bulk_insert_mappings(ScoreRule, data["score_rules"])
        db.bulk_insert_mappings(Campaign, data["campaigns"])
        db.bulk_insert_mappings(SalesRep, data["sales_reps"])
        db.bulk_insert_mappings(Company, data["companies"])
        db.commit()

        # Insert Contacts
        db.bulk_insert_mappings(Contact, data["contacts"])
        db.commit()

        # Insert Leads
        db.bulk_insert_mappings(Lead, data["leads"])
        db.commit()

        # Insert Activities in batches
        act_batch_size = 5000
        activities = data["activities"]
        for i in range(0, len(activities), act_batch_size):
            db.bulk_insert_mappings(Activity, activities[i:i + act_batch_size])
            db.commit()

        # Insert Consents and Consent Histories
        db.bulk_insert_mappings(Consent, data["consents"])
        if data.get("consent_histories"):
            db.bulk_insert_mappings(ConsentHistory, data["consent_histories"])
        db.commit()

        # Insert Duplicate Relationships
        if data.get("duplicate_relationships"):
            db.bulk_insert_mappings(DuplicateRelationship, data["duplicate_relationships"])
            db.commit()

        # Insert Opportunities
        db.bulk_insert_mappings(Opportunity, data["opportunities"])
        db.commit()

        # Insert Stage Histories
        db.bulk_insert_mappings(StageHistory, data["stage_histories"])
        db.commit()

        # Insert Tasks
        db.bulk_insert_mappings(Task, data["tasks"])
        db.commit()

        # Insert Anomaly Records
        if anomalies:
            db.bulk_insert_mappings(AnomalyRecord, anomalies)
            db.commit()

        print("Database population complete.")
    except Exception as e:
        db.rollback()
        print(f"Error populating database: {e}")
        raise e
    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(description="SmartLead AI Synthetic Data Generation")
    parser.add_argument("--scale", type=str, choices=["small", "full"], default="small",
                        help="Dataset volume scale: 'small' for starter/testing, 'full' for production benchmark")
    args = parser.parse_args()

    print(f"Starting SmartLead AI Synthetic Data Generation (Scale: {args.scale})...")
    start_time = time.time()

    # 1. Generate Clean Baseline Records
    generator = SyntheticDataGenerator(scale=args.scale)
    data = generator.generate_all()

    # 2. Inject Deliberate Labelled Anomalies (Cases 1 - 5)
    injector = AnomalyInjector(data)
    data, anomalies = injector.inject_all_cases(count_per_case=10 if args.scale == "full" else 3)

    # 3. Populate SQLite Database
    populate_database(data, anomalies)

    # 4. Export CSV, JSON and SQL Seed
    print("Exporting datasets to CSV, JSON, and SQL...")
    exporter = DataExporter(data, anomalies)
    exporter.export_all()

    elapsed = round(time.time() - start_time, 2)
    print("\nGeneration & Export Summary:")
    print(f"- Scale: {args.scale}")
    print(f"- Companies: {len(data['companies'])}")
    print(f"- Contacts: {len(data['contacts'])}")
    print(f"- Leads: {len(data['leads'])}")
    print(f"- Activities: {len(data['activities'])}")
    print(f"- Opportunities: {len(data['opportunities'])}")
    print(f"- Stage Histories: {len(data['stage_histories'])}")
    print(f"- Tasks: {len(data['tasks'])}")
    print(f"- Consents: {len(data['consents'])}")
    print(f"- Anomaly Records (Cases 1-5): {len(anomalies)}")
    print(f"- Elapsed Time: {elapsed} seconds")
    print("Data generation finished successfully.\n")


if __name__ == "__main__":
    main()
