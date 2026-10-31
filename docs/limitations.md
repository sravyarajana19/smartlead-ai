# SMARTLEAD AI Limitations & Architectural Trade-offs

This document outlines known limitations, trade-offs, and scaling boundaries of the current SmartLead AI implementation, along with recommended production enhancements.

---

## 1. Storage & Database Concurrency

- **Current Implementation**: SQLite with `PRAGMA foreign_keys = ON` and `check_same_thread = False`.
- **Limitation**: SQLite utilizes file-level locking for write operations. Under ultra-high concurrent write workloads (e.g. $> 1,000$ concurrent API requests updating leads simultaneously), write lock contention may occur.
- **Production Recommendation**: Seamless migration to **PostgreSQL** or **CockroachDB** with read replicas. The SQLAlchemy ORM models and schema are already written to be 100% database-agnostic.

---

## 2. Machine Learning Model Architecture

- **Current Implementation**: Scikit-learn Logistic Regression baseline classifier with feature standardization.
- **Strengths**: High explainability, fast training ($< 1$ second on 20,000 rows), direct linear interpretability via odds-ratio coefficients.
- **Limitation**: Logistic regression assumes a linear boundary in the log-odds space and cannot natively capture complex high-order feature interactions (e.g., specific interactions between product type and executive seniority) without manual polynomial expansion.
- **Production Recommendation**: Integrate ensemble tree models (XGBoost / LightGBM) with SHAP (SHapley Additive exPlanations) for non-linear interactions while preserving explainability.

---

## 3. Lead Scoring Rules & Weights

- **Current Implementation**: Static heuristic scoring engine with configurable weights (Fit 40%, Intent 35%, Engagement 25%) and SemVer rule versioning.
- **Limitation**: Scoring weights require manual business calibration or periodic manual review rather than self-tuning.
- **Production Recommendation**: Implement an automated Bayesian parameter optimization loop that periodically calibrates scoring weights against verified closed-won conversion rates over time.

---

## 4. Deduplication Complexity

- **Current Implementation**: Deterministic matching on normalized phone, exact email, and domain + last name combinations.
- **Limitation**: Phonetic spelling variations (e.g. "Jon" vs "John") or corporate entity variations (e.g. "Google Inc." vs "Google LLC") require specialized fuzzy token matching (e.g. Jaro-Winkler or Levenshtein distance).
- **Production Recommendation**: Incorporate an entity resolution graph or vector embedding similarity index (e.g. using Sentence-Transformers / pgvector) for deep semantic deduplication.

---

## 5. Security & Multi-Tenancy

- **Current Implementation**: Open internal enterprise deployment suitable for local forward-deployed technical evaluation without authentication barriers.
- **Production Recommendation**: Implement OAuth2 / JWT authentication, role-based access control (RBAC), and multi-tenant organization row-level security (RLS).
