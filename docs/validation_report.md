# Data Quality and Integrity Validation Report

**Execution Timestamp**: "1793388301.8261774"  
**Overall Validation Status**: `VALIDATED_WITH_LABELLED_ANOMALIES`  
**Total Records Checked**: 49,275  
**Passed Automated Checks**: 9  
**Failed Data Integrity Checks**: 0  
**Detected Exception Scenarios (Labelled Anomalies)**: 50  

---

## 1. Executive Summary

The SmartLead AI Validation Engine automatically verifies relational integrity, primary/foreign key uniqueness, allowed enumeration constraints, date ordering, scoring arithmetic reconciliation, and the 5 mandatory business exception scenarios.

> [!NOTE]
> Labelled business anomalies injected for stress-testing and audit compliance are distinguished from unexpected data corruption. The platform correctly identified 100% of injected anomaly scenarios without corrupting baseline records.

---

## 2. Injected Exception Scenarios Breakdown (Cases 1 - 5)

| Exception Scenario Case | Detected Anomaly Count | Expected Decision | Status |
|---|---|---|---|
| **CASE 1: Consent Violation (Opt-Out Contact)** | 10 | Block Outreach Task & Log Violation | Verified |
| **CASE 2: Temporal Leakage (Post-Conversion Activity)** | 10 | Exclude Activity from Lead Scoring | Verified |
| **CASE 3: Sales Routing Violation (Territory Mismatch)** | 10 | Report Territory Discrepancy | Verified |
| **CASE 4: Duplicate Opportunity Creation** | 10 | Preserve Both & Flag for Review | Verified |
| **CASE 5: Missing Stage History Transitions** | 10 | Reject Direct Skip to Won Stage | Verified |

---

## 3. Comprehensive Checklist of Automated Verifications

| Check Category | Verification Description | Status | Details / Actions |
|---|---|---|---|
| Company PK Uniqueness | Automated engine rule | **PASSED** | Verified |
| Company Mandatory Fields | Automated engine rule | **PASSED** | Verified |
| Contact -> Company FK Integrity | Automated engine rule | **PASSED** | Verified |
| Lead -> Company & Contact FK Integrity | Automated engine rule | **PASSED** | Verified |
| Allowed Enum Values Validation | Automated engine rule | **PASSED** | Verified |
| Score Formula Arithmetic Reconciliation | Automated engine rule | **PASSED** | Verified |
| Component and Lead Score 0-100 Range Check | Automated engine rule | **PASSED** | Verified |
| Lifecycle Date Ordering (Created <= Converted) | Automated engine rule | **PASSED** | Verified |
| CASE 1: Consent Enforcement (Opt-Out Contact Detection) | Automated engine rule | **ANOMALY_DETECTED** | Flagged as privacy consent violations in ground truth and exception logs. |
| CASE 2: Temporal Leakage Detection (Post-Conversion Activities) | Automated engine rule | **ANOMALY_DETECTED** | Flagged as temporal leakage; excluded from valid scoring pipeline. |
| CASE 3: Territory Sales Routing Validation | Automated engine rule | **ANOMALY_DETECTED** | Reported expected vs actual territory in routing anomaly log. |
| CASE 4: Duplicate Opportunity Creation Detection | Automated engine rule | **ANOMALY_DETECTED** | Preserved both canonical and duplicate opportunities for investigation. |
| CASE 5: Opportunity Stage History Lifecycle Transition Integrity | Automated engine rule | **ANOMALY_DETECTED** | Detected invalid or missing stage transitions in lifecycle history. |
| Conversion Funnel Mathematical Reconciliation | Automated engine rule | **PASSED** | Verified |

---

## 4. Arithmetic Reconciliation Validation

- Formula verified: `Lead Score = (Fit Score × 0.40) + (Intent Score × 0.35) + (Engagement Score × 0.25)`
- Discrepancy tolerance: `<= 0.05`
- Out of bounds scores `[0.0, 100.0]`: **0**
- Missing mandatory foreign key pointers: **0**
