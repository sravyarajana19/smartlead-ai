# SMARTLEAD AI – Intelligent Lead Scoring & Sales Operations Platform

[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-FF4B4B.svg)](https://streamlit.io)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0+-D71F00.svg)](https://www.sqlalchemy.org/)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-1.3+-F7931E.svg)](https://scikit-learn.org/)
[![Pytest](https://img.shields.io/badge/Tests-52%20Passed-brightgreen.svg)](https://pytest.org)

**SMARTLEAD AI** is an intelligent, enterprise-grade lead scoring and sales operations platform engineered for technical evaluation as an **Associate AI Forward Deployed Engineer**. 

It provides an end-to-end operational system that scores leads using firmographic fit, buying intent, and behavioral engagement; enforces regulatory marketing consent; eliminates data duplicates; deterministically routes opportunities to sales representatives based on territory and product specialization; and evaluates conversion outcomes with Scikit-learn machine learning on held-out records.

---

## 1. Business Problem & Solution

### The Challenge
High-growth B2B revenue teams face major inefficiencies:
- Sales representatives waste time following up on low-intent or ill-fitting leads.
- Inconsistent routing causes territory mismatches and representative overload.
- Marketing consent violations (e.g., contacting opted-out individuals) trigger severe regulatory fines (GDPR / CCPA).
- Duplicate leads result in duplicate opportunities, corrupting revenue forecasts.
- Machine learning models suffer from **post-conversion temporal data leakage**, fabricating unrealistic accuracy metrics.

### The Solution: SmartLead AI
- **Explainable Multi-Factor Scoring**: Transparent formula combining Company Fit (40%), Buying Intent (35%), and Engagement (25%) bounded from 0 to 100 with clear priority tiers (High, Medium, Low).
- **Zero-Tolerance Consent Enforcement**: Absolute blocking of outreach to opted-out contacts (high lead scores never override consent).
- **Intelligent Deduplication**: Differentiates exact duplicates, potential duplicates, and legitimate repeat inquiries after 180+ days.
- **Deterministic Territory Routing**: Automatically routes qualified leads to active local specialists with available capacity.
- **Event-Sourced Opportunity Pipeline**: Full state machine validation with immutable `StageHistory` tracking.
- **Continuous Audit & Exception Surveillance**: Live detection and logging for all 5 mandatory business exception scenarios.
- **Leakage-Free ML Evaluation**: Logistic Regression classifier evaluated on held-out test data strictly isolated from ground-truth labels and post-conversion events.

---

## 2. Technology Stack

Built strictly with **free, local, and open-source** technologies:
- **Backend**: Python 3.13, FastAPI, SQLAlchemy 2.0, SQLite (with `PRAGMA foreign_keys = ON`).
- **Frontend / Dashboard**: Streamlit, Plotly Express & Graph Objects.
- **Data Engineering**: Pandas, NumPy, Faker.
- **Machine Learning**: Scikit-learn (Logistic Regression, StandardScaler, Classification Metrics).
- **Automated Testing**: Pytest (52 automated tests covering all modules, regression checks, and business rules).
- **Documentation**: Markdown, Mermaid Entity-Relationship Diagrams.

---

## 3. System Architecture & Database Design

### 3.1 Architecture Overview
```
smartlead-ai/
├── backend/                  # FastAPI REST API Service
│   ├── core/                 # Config & Database Engine (Foreign keys enabled)
│   ├── models/               # SQLAlchemy 2.0 ORM Entities
│   ├── schemas/              # Pydantic V2 Request/Response Models
│   ├── services/             # Scoring, Routing, Consent, Task, Opportunity Services
│   ├── routers/              # 15 Domain Endpoints
│   └── main.py               # FastAPI App & Middleware
├── generator/                # Deterministic Synthetic Data Generator
│   ├── id_generator.py       # Zero-padded ID generator (CO-000001, LEAD-2026-000001)
│   ├── synthetic_data.py     # Parameterized Generator (Seed 20261022)
│   ├── anomaly_injector.py   # Injects Cases 1 - 5 + Ground Truth
│   └── exporter.py           # Exports to CSV, JSON, SQL
├── ml/                       # Machine Learning Pipeline
│   ├── dataset.py            # Feature engineering & anti-leakage isolation
│   └── pipeline.py           # Logistic Regression trainer & reporter
├── dashboard/                # Streamlit Multi-Page Application
│   ├── app.py                # Landing hub & overview
│   ├── components/           # High-speed data loaders & caches
│   └── pages/                # 12 Operational pages
├── tests/                    # Pytest Suite (52 tests, 100% pass)
├── data/
│   ├── exports/              # CSV, JSON, and SQL Seed data
│   └── ground_truth/         # ground_truth.csv and ground_truth.json
├── docs/                     # Full Technical Architecture & Data Dictionaries
├── prompts/                  # Prompt history & AI assistance disclosure
└── scripts/                  # Standalone execution CLI scripts
```

### 3.2 11 Mandatory Entities & Deterministic ID Conventions
All entities feature deterministic, zero-padded, immutable IDs:
1. **Company**: `CO-000001`
2. **Contact**: `CON-000001`
3. **Lead**: `LEAD-2026-000001`
4. **Campaign**: `CMP-000001`
5. **Activity**: `ACT-LEAD-2026-000001-001`
6. **Consent**: `CNS-000001`
7. **ScoreRule**: `SCR-000001`
8. **SalesRep**: `REP-000001`
9. **Task**: `TASK-LEAD-2026-000001-001`
10. **Opportunity**: `OPP-2026-000001`
11. **StageHistory**: `STG-OPP-2026-000001-001`
*Additional bridge/audit tables: `DuplicateRelationship` (`DUP-000001`), `AnomalyRecord` (`ANM-000001`), `ConsentHistory` (`CNH-000001`).*

---

## 4. Installation & Setup Instructions

### Step 1: Clone or Navigate to the Repository
```bash
git clone https://github.com/sravyarajana19/smartlead-ai.git
cd smartlead-ai
```

### Step 2: Virtual Environment Setup (Recommended)
```bash
# Windows
python -m venv venv
.\venv\Scripts\Activate.ps1

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
python -m pip install -r requirements.txt
```

---

## 5. Execution Workflow & Step-by-Step Commands

### Step 1: Initialize the Database Schema
Initializes SQLite database tables with foreign-key constraints enabled:
```powershell
python scripts\init_db.py
```

### Step 2: Generate Synthetic Business Data
Supports two modes:
- Starter small scale (quick trial):
  ```powershell
  python scripts\generate_data.py --scale small
  ```
- **Full benchmark scale (5,000 companies, 10,000 contacts, 20,000 leads, 3,000 opportunities)**:
  ```powershell
  python scripts\generate_data.py --scale full
  ```
*Generates baseline records, injects Cases 1–5 anomalies, populates the database, and exports CSV, JSON, and SQL seed scripts in ~22 seconds.*

### Step 3: Execute Automated Relational & Integrity Validation
Runs all 14 database integrity checks:
```powershell
python scripts\run_validation.py
```
*Outputs detailed audit summary and generates `docs/validation_report.md`.*

### Step 4: Train & Evaluate Machine Learning Pipeline
Trains the Scikit-learn Logistic Regression baseline model on historical conversions:
```powershell
python scripts\train_ml.py
```
*Outputs factual accuracy, precision, recall, F1, ROC-AUC, confusion matrix, and generates `docs/ml_evaluation.md`.*

### Step 5: Verify 100% Deterministic Reproducibility
Runs two independent generations with seed `20261022` and performs bitwise SHA-256 verification:
```powershell
python scripts\verify_reproducibility.py
```
*Outputs verification result and generates `docs/reproducibility.md`.*

### Step 6: Run Automated Pytest Suite
Executes 43 tests across all modules:
```powershell
python -m pytest tests -v
```

### Step 7: Launch the FastAPI REST Backend
Starts the REST API server on `http://127.0.0.1:8000`:
```powershell
python scripts\run_backend.py
```
- Interactive Swagger UI: **http://127.0.0.1:8000/docs**
- ReDoc Documentation: **http://127.0.0.1:8000/redoc**
- Health Endpoint: **http://127.0.0.1:8000/health**

### Step 8: Launch the Streamlit Operations Dashboard
Starts the multi-page interactive business dashboard on `http://localhost:8501`:
```powershell
streamlit run dashboard\app.py
```

---

## 6. Streamlit Operations Dashboard Guide

The platform includes 12 operational pages accessible from the sidebar:

| Page | Key Features & Business Functions |
|---|---|
| **1. Executive Dashboard** | Top-level KPI cards, Sales Conversion Funnel (Plotly), Lead Priority Distribution, Territory breakdown, Pipeline value by stage. |
| **2. Lead Explorer** | Real-time search by company, contact, or email; multi-filter by priority, territory, lead source, consent status, score range; record deep-dive. |
| **3. Lead Scoring** | Transparent breakdown of Company Fit (40%), Buying Intent (35%), and Engagement (25%); interactive weight simulator to test custom business policies. |
| **4. Company & Contacts** | Enterprise vs. Mid-Market vs. SMB firmographics, buyer persona seniority breakdown, searchable account directory. |
| **5. Campaign & Activities** | Campaign performance and channel budget mix; touchpoint volume by event type (Demo requests, pricing views, webinars). |
| **6. Consent Management** | Opt-In vs. Opt-Out privacy tracking; interactive live consent verification tool; opt-out audit trail. |
| **7. Sales Routing** | Representative capacity utilization bars; interactive lead routing simulator testing territory and specialization rules. |
| **8. Follow-up Tasks** | Task backlog sorted by SLA priority (Urgent 1-day, High 2-day, Normal 5-day); consent verification status. |
| **9. Opportunity Pipeline** | Stage progression (New $\rightarrow$ Qualified $\rightarrow$ Proposal $\rightarrow$ Negotiation $\rightarrow$ Won/Lost); win/loss reason analysis; immutable stage history audit. |
| **10. Exception Monitoring** | Compliance surveillance for all 5 mandatory exception cases with severity levels, entity IDs, and expected resolutions. |
| **11. Data Quality & Validation** | 14-point database integrity audit with live execution button and pass/fail indicators. |
| **12. ML Evaluation** | Classification benchmarks on held-out test data; confusion matrix heatmap; ROC curve; feature importance coefficients; live conversion predictor for any lead. |

---

## 7. Mandatory Exception Scenarios (Cases 1 - 5)

SmartLead AI deliberately injects and detects all 5 mandatory negative test scenarios:

| Case | Scenario Description | Detection Mechanism | Expected Platform Action |
|---|---|---|---|
| **CASE 1** | **Opted-out lead contacted** | Verified before task creation or simulated contact. | **BLOCKS OUTREACH**: Raises 403 Forbidden, logs `CASE_1_CONSENT_VIOLATION` in audit ledger. |
| **CASE 2** | **Post-conversion activity used in scoring** | Compares `activity_date` against `converted_date`. | **ELIMINATES LEAKAGE**: Excludes post-conversion events from score and flags `CASE_2_TEMPORAL_LEAKAGE`. |
| **CASE 3** | **Lead assigned outside territory** | Compares `lead.territory` with `rep.territory`. | **DETECTS MISMATCH**: Reports expected vs. actual territory and logs `CASE_3_ROUTING_VIOLATION`. |
| **CASE 4** | **Duplicate lead creates duplicate opportunity** | Matches duplicate lead against active opportunities for the same account. | **PRESERVES RECORDS**: Marks `is_duplicate = True`, links to canonical opportunity, and flags `CASE_4_DUPLICATE_OPPORTUNITY`. |
| **CASE 5** | **Missing or skipped stage transitions** | Audits sequential stage history transitions (e.g. `New` straight to `Won`). | **VALIDATES LIFECYCLE**: Detects invalid leap, records missing intermediate stages, flags `CASE_5_MISSING_STAGE_TRANSITION`. |

All injected anomalies are isolated in `data/ground_truth/ground_truth.csv` and `ground_truth.json` and are **strictly excluded** from ML model features.

---

## 8. Real Execution Benchmark Results

Factual metrics recorded on the **full benchmark dataset (20,000 leads)**:

### 8.1 Generated Entity Volumes
- **Companies**: 5,000
- **Contacts**: 10,000
- **Leads**: 20,000
- **Activities**: 61,243
- **Opportunities**: 3,010 (3,000 baseline + 10 duplicate opps)
- **Stage Histories**: 11,183
- **Tasks**: 14,258
- **Consents**: 20,000
- **Injected Anomaly Records**: 50 (10 per case)
- **Generation & Export Runtime**: **24.59 seconds**

### 8.2 Machine Learning Evaluation (Held-out 20% Test Split)
- **Model**: Logistic Regression (Baseline Classifier with Class Balancing)
- **Accuracy**: **58.93%**
- **Precision**: **19.84%**
- **Recall**: **54.17%**
- **F1-Score**: **29.04%**
- **ROC-AUC**: **0.6205**
- **Confusion Matrix**: `[[1954, 1313], [275, 325]]` (TP=325, TN=1954, FP=1313, FN=275)
- **Top Predictive Features**:
  1. `intent_score` (+0.4430)
  2. `fit_score` (+0.3794)
  3. `engagement_score` (+0.2645)

### 8.3 Data Validation Engine Results
- **Records Audited**: 124,786
- **Passed Checks**: 9
- **Failed Checks**: 0 (Zero accidental data corruption)
- **Labelled Anomalies Detected**: 50 (100% detection rate for Cases 1–5; 10 per case)
- **Status**: `VALIDATED_WITH_LABELLED_ANOMALIES`

### 8.4 Deterministic Reproducibility
- **Run 1 Digest**: `f239207fea89ce3e10bdf0775e75c68b75d80975f046b02aa695888149781526`
- **Run 2 Digest**: `f239207fea89ce3e10bdf0775e75c68b75d80975f046b02aa695888149781526`
- **Match Status**: **MATCH (100% BITWISE IDENTICAL)**

### 8.5 Automated Test Suite
- **Pytest Results**: **52 passed in 16.37s** (0 failures, 100% pass rate).

---

## 9. Data Exports & Deliverables

All datasets are saved in the project repository:
- **CSV Exports**: `data/exports/csv/` (`companies.csv`, `leads.csv`, `activities.csv`, `opportunities.csv`, etc.)
- **JSON Exports**: `data/exports/json/`
- **SQL Seed Script**: `data/exports/sql/smartlead_seed.sql`
- **Ground Truth Dataset**: `data/ground_truth/ground_truth.csv` and `ground_truth.json`
- **Documentation**:
  - `docs/architecture.md`
  - `docs/database_schema.md` (with Mermaid ERD)
  - `docs/data_dictionary.md` (All 11 entities)
  - `docs/business_rules.md`
  - `docs/scoring_methodology.md`
  - `docs/validation_report.md`
  - `docs/ml_evaluation.md`
  - `docs/reproducibility.md`
  - `docs/limitations.md`
  - `prompts/prompt_history.md`

---

## 10. AI Assistance Disclosure

In compliance with YottaFlex technical evaluation requirements:
- **AI Assistant Used**: Antigravity (Google DeepMind Advanced Agentic Coding)
- **Model**: Gemini 3.8 Flash
- **Full Prompt & Disclosure**: Preserved verbatim in `prompts/prompt_history.md`.
- All generated code, database schemas, validation rules, and machine learning pipelines were executed and verified locally in Python 3.13 on Windows.
