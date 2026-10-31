# SMARTLEAD AI Architecture Documentation

## 1. System Overview

**SMARTLEAD AI** is an intelligent lead scoring and sales operations platform engineered for high-velocity revenue operations, enterprise data integrity, regulatory marketing compliance, and machine-learning evaluation.

The system is architected as an end-to-end, decoupled multi-layer architecture:
- **Presentation Layer**: Streamlit multi-page interactive web application with Plotly data visualizations.
- **API & Orchestration Layer**: FastAPI RESTful backend service with asynchronous support, OpenAPI/Swagger documentation, and Pydantic schema validation.
- **Business Logic & Service Layer**: Modular domain engines (Lead Scoring, Deduplication, Sales Routing, Consent Enforcement, Task Orchestration, and Opportunity Lifecycle Management).
- **Data & Persistence Layer**: SQLAlchemy 2.0 ORM with SQLite, featuring enforced foreign-key integrity constraints, deterministic zero-padded IDs, and event-sourced historical tracking.
- **Machine Learning & Evaluation Pipeline**: Scikit-learn predictive classification pipeline with strictly isolated train/test sets, zero data leakage, and live inference.
- **Validation & Governance Engine**: Automated 14-dimension relational and lifecycle rule verification engine with continuous audit reporting.

---

## 2. Architecture Diagram

```mermaid
flowchart TD
    subgraph Client_Layer [Client & Presentation Layer]
        UI[Streamlit Multi-Page Dashboard\n12 Operational Pages / Plotly Charts]
        API_Client[REST API Consumer / Swagger UI\nhttp://127.0.0.1:8000/docs]
    end

    subgraph Service_Layer [FastAPI REST Service Layer]
        Router[FastAPI Router Gateway\nCORS, Pagination, Pydantic V2 Schemas]
        ScoringSvc[Lead Scoring Engine\n40% Fit | 35% Intent | 25% Engagement]
        ConsentSvc[Consent Enforcement Service\nOpt-Out Gatekeeper & Anomaly Detection]
        RoutingSvc[Sales Routing Engine\nTerritory, Specialization & Capacity Match]
        TaskSvc[Task Orchestration Service\nPrioritization & SLA Scheduling]
        OppSvc[Opportunity Lifecycle Service\nState Machine & Stage History Audit]
        DedupSvc[Deduplication Engine\nExact, Potential & Repeat Lead Match]
        ValEngine[Data Quality Validation Engine\n14 Automated Integrity Audits]
    end

    subgraph ML_Layer [Machine Learning Pipeline]
        DatasetBuilder[ML Dataset Builder\nLeakage Prevention & Isolation]
        ModelTrainer[Scikit-learn Logistic Regression\nBalanced Train/Test Split]
        MetricsEvaluator[Evaluation Reporter\nAccuracy, Precision, Recall, F1, ROC-AUC]
        Artifacts[Serialized Model & Scaler Artifacts\nml/artifacts/model.joblib]
    end

    subgraph Data_Layer [Data & Persistence Layer]
        ORM[SQLAlchemy 2.0 ORM]
        DB[(SQLite Database\nsmartlead.db\nPRAGMA foreign_keys = ON)]
        Exports[Data Exporters\nCSV / JSON / SQL Seed]
        GroundTruth[Ground Truth Dataset\nground_truth.csv / json]
    end

    UI --> Router
    API_Client --> Router
    Router --> ScoringSvc
    Router --> ConsentSvc
    Router --> RoutingSvc
    Router --> TaskSvc
    Router --> OppSvc
    Router --> DedupSvc
    Router --> ValEngine
    Router --> ML_Layer

    ScoringSvc --> ORM
    ConsentSvc --> ORM
    RoutingSvc --> ORM
    TaskSvc --> ORM
    OppSvc --> ORM
    DedupSvc --> ORM
    ValEngine --> ORM

    ORM --> DB
    DB --> Exports
    DB --> GroundTruth
    DB --> DatasetBuilder
    DatasetBuilder --> ModelTrainer --> MetricsEvaluator --> Artifacts
```

---

## 3. Component Deep Dive

### 3.1 Presentation Layer (Streamlit)
- Multi-page structure under `dashboard/pages/` featuring 12 responsive operational views.
- Reactive Plotly graphs for conversion funnels, stage distributions, capacity bars, and ROC curves.
- Local high-speed caching with SQLite connection pooling for smooth performance on laptops.

### 3.2 REST API Backend (FastAPI)
- Structured modular routers partitioned by business domain (`backend/routers/`).
- Standardized response formatting, pagination headers, and HTTP status codes (`200 OK`, `201 Created`, `400 Bad Request`, `403 Forbidden`, `404 Not Found`).
- Auto-generated interactive Swagger UI documentation at `/docs` and ReDoc at `/redoc`.

### 3.3 Scoring Service (`LeadScoringEngine`)
- Pure functional scoring calculations enforcing `0.0` to `100.0` bounds.
- Configurable rule versions and weights (Default: Fit 40%, Intent 35%, Engagement 25%).
- Temporal protection: Automatically filters activities timestamped after the lead's conversion date, eliminating post-conversion leakage.

### 3.4 Consent Enforcement Service (`ConsentEnforcementService`)
- Gatekeeper pattern: Evaluates consent before any contact task creation or simulated outreach.
- Strict precedence: Legal opt-out status supersedes all lead scores (even score = 100).
- Automatic logging of CASE 1 consent violations into the anomaly audit ledger.

### 3.5 Sales Routing Engine (`SalesRoutingEngine`)
- Four-tier deterministic routing:
  1. Primary: Active Rep + Territory Match + Product Specialization + Capacity Available.
  2. Secondary: Active Rep + Territory Match + Capacity Available (General territory rep).
  3. Tertiary: Territory match but full capacity -> Flags `No_Capacity`.
  4. Quaternary: No territory match -> Moves lead to General Triage Queue.
- Deterministic tie-breaking by lowest current workload, then alphabetical representative ID.

### 3.6 ML Evaluation Pipeline (`MLEvaluationPipeline`)
- Logistic Regression baseline classification model predicting lead conversion.
- Features: Firmographic fit score, intent score, engagement score, employee scale, annual revenue, enterprise tier, executive seniority, pre-conversion activity touchpoints, and one-hot encoded territory/product/source/industry.
- Strict anti-leakage isolation: Ground-truth anomaly labels and post-conversion activities are completely absent from the feature matrix.
