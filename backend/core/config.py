import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
EXPORTS_DIR = DATA_DIR / "exports"
CSV_EXPORTS_DIR = EXPORTS_DIR / "csv"
JSON_EXPORTS_DIR = EXPORTS_DIR / "json"
SQL_EXPORTS_DIR = EXPORTS_DIR / "sql"
GROUND_TRUTH_DIR = DATA_DIR / "ground_truth"
ML_DIR = BASE_DIR / "ml" / "artifacts"
DOCS_DIR = BASE_DIR / "docs"

# Database Configuration
DATABASE_PATH = DATA_DIR / "smartlead.db"
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DATABASE_PATH.as_posix()}")

# Global Project Settings
PROJECT_NAME = "SMARTLEAD AI"
PROJECT_DESCRIPTION = "Intelligent Lead Scoring and Sales Operations Platform"
VERSION = "1.0.0"
RANDOM_SEED = 20261022

# Lead Scoring Default Weights
DEFAULT_FIT_WEIGHT = 0.40
DEFAULT_INTENT_WEIGHT = 0.35
DEFAULT_ENGAGEMENT_WEIGHT = 0.25

# Score Priority Thresholds
HIGH_PRIORITY_MIN = 80.0
MEDIUM_PRIORITY_MIN = 50.0

# Territory Definitions
VALID_TERRITORIES = ["North America", "EMEA", "APAC", "LATAM"]

# Product Catalog
VALID_PRODUCTS = ["Enterprise Suite", "Cloud Platform", "Security Shield", "AI Analytics"]

# Opportunity Stages
OPPORTUNITY_STAGES = ["New", "Qualified", "Proposal", "Negotiation", "Won", "Lost"]
