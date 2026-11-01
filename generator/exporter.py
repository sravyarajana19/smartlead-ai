import json
import csv
from datetime import datetime, date
from pathlib import Path
from typing import Dict, Any, List
from backend.core.config import CSV_EXPORTS_DIR, JSON_EXPORTS_DIR, SQL_EXPORTS_DIR


def json_serializer(obj):
    """Custom serializer for date/datetime objects."""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")


class DataExporter:
    """
    Exports synthetic datasets to standard formats:
    - CSV files in data/exports/csv/
    - JSON files in data/exports/json/
    - SQL Seed script in data/exports/sql/smartlead_seed.sql
    Preserves exact deterministic IDs and relational integrity.
    """

    def __init__(self, data: Dict[str, List[Dict[str, Any]]], anomalies: List[Dict[str, Any]] = None):
        self.data = data
        self.anomalies = anomalies or []

    def export_all(self):
        """Executes CSV, JSON and SQL seed exports."""
        CSV_EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
        JSON_EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
        SQL_EXPORTS_DIR.mkdir(parents=True, exist_ok=True)

        self.export_csv()
        self.export_json()
        self.export_sql()

    def export_csv(self):
        """Export each entity list to a dedicated CSV file."""
        for entity_name, records in self.data.items():
            csv_path = CSV_EXPORTS_DIR / f"{entity_name}.csv"
            if not records:
                if csv_path.exists():
                    csv_path.unlink()
                continue

            fieldnames = list(records[0].keys())
            with open(csv_path, mode="w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for r in records:
                    row = {}
                    for k, v in r.items():
                        if isinstance(v, (datetime, date)):
                            row[k] = v.isoformat()
                        else:
                            row[k] = v
                    writer.writerow(row)

        anom_path = CSV_EXPORTS_DIR / "anomaly_records.csv"
        if self.anomalies:
            with open(anom_path, mode="w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=list(self.anomalies[0].keys()))
                writer.writeheader()
                writer.writerows(self.anomalies)
        elif anom_path.exists():
            anom_path.unlink()

    def export_json(self):
        """Export each entity list to a JSON file."""
        for entity_name, records in self.data.items():
            json_path = JSON_EXPORTS_DIR / f"{entity_name}.json"
            if not records and json_path.exists():
                json_path.unlink()
                continue
            with open(json_path, mode="w", encoding="utf-8") as f:
                json.dump(records, f, indent=2, default=json_serializer)

        anom_path = JSON_EXPORTS_DIR / "anomaly_records.json"
        if self.anomalies:
            with open(anom_path, mode="w", encoding="utf-8") as f:
                json.dump(self.anomalies, f, indent=2, default=json_serializer)
        elif anom_path.exists():
            anom_path.unlink()
                json.dump(self.anomalies, f, indent=2, default=json_serializer)

    def export_sql(self):
        """Generates SQL INSERT seed script."""
        sql_path = SQL_EXPORTS_DIR / "smartlead_seed.sql"
        table_map = {
            "score_rules": "score_rules",
            "campaigns": "campaigns",
            "sales_reps": "sales_reps",
            "companies": "companies",
            "contacts": "contacts",
            "leads": "leads",
            "activities": "activities",
            "consents": "consents",
            "consent_histories": "consent_histories",
            "duplicate_relationships": "duplicate_relationships",
            "opportunities": "opportunities",
            "stage_histories": "stage_histories",
            "tasks": "tasks",
        }

        with open(sql_path, mode="w", encoding="utf-8") as f:
            f.write("-- SMARTLEAD AI Seed Data\n")
            f.write("-- Generated deterministically with seed 20261022\n\n")
            f.write("PRAGMA foreign_keys = OFF;\n\n")

            for key, table_name in table_map.items():
                records = self.data.get(key, [])
                if not records:
                    continue
                f.write(f"-- Table: {table_name} ({len(records)} records)\n")
                cols = list(records[0].keys())
                col_names = ", ".join(cols)

                for r in records:
                    val_strs = []
                    for c in cols:
                        val = r.get(c)
                        if val is None:
                            val_strs.append("NULL")
                        elif isinstance(val, bool):
                            val_strs.append("1" if val else "0")
                        elif isinstance(val, (int, float)):
                            val_strs.append(str(val))
                        elif isinstance(val, (datetime, date)):
                            val_strs.append(f"'{val.isoformat()}'")
                        else:
                            clean_str = str(val).replace("'", "''")
                            val_strs.append(f"'{clean_str}'")
                    f.write(f"INSERT INTO {table_name} ({col_names}) VALUES ({', '.join(val_strs)});\n")
                f.write("\n")

            f.write("PRAGMA foreign_keys = ON;\n")
