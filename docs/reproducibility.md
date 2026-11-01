# Reproducibility and Determinism Report

**Random Seed**: `20261022`  
**Verification Result**: `100% BITWISE IDENTICAL`  
**Run 1 Global Digest (SHA-256)**: `f239207fea89ce3e10bdf0775e75c68b75d80975f046b02aa695888149781526`  
**Run 2 Global Digest (SHA-256)**: `f239207fea89ce3e10bdf0775e75c68b75d80975f046b02aa695888149781526`  

---

## 1. Executive Summary

To satisfy strict enterprise compliance and forward-deployed engineering standards, SmartLead AI implements deterministic data generation and rule evaluation. Two independent generation runs were executed using seed `20261022`. All row counts, deterministic zero-padded IDs, calculated lead scores, and injected ground-truth anomalies were compared.

The results confirm that the platform is **100% deterministic and reproducible** across separate execution cycles.

---

## 2. Table-by-Table Reproducibility Audit

| Entity / Dataset | Run 1 Count | Run 2 Count | Run 1 SHA-256 Digest | Run 2 SHA-256 Digest | Match Status |
|---|---|---|---|---|---|
| **activities** | 1,860 | 1,860 | `d40951d591a81079...` | `d40951d591a81079...` | **PASS** |
| **anomalies** | 15 | 15 | `dc0510a92afe7369...` | `dc0510a92afe7369...` | **PASS** |
| **campaigns** | 10 | 10 | `223130d454bf7861...` | `223130d454bf7861...` | **PASS** |
| **companies** | 150 | 150 | `836fb03b54a59d55...` | `836fb03b54a59d55...` | **PASS** |
| **consent_histories** | 69 | 69 | `ec2a0e7aa1f22ec9...` | `ec2a0e7aa1f22ec9...` | **PASS** |
| **consents** | 600 | 600 | `8c9288fef9f4e0fa...` | `8c9288fef9f4e0fa...` | **PASS** |
| **contacts** | 300 | 300 | `db4b5d1412270243...` | `db4b5d1412270243...` | **PASS** |
| **duplicate_relationships** | 19 | 19 | `aca8d71d94932b8c...` | `aca8d71d94932b8c...` | **PASS** |
| **leads** | 600 | 600 | `15bf5e78e7eb1990...` | `15bf5e78e7eb1990...` | **PASS** |
| **opportunities** | 93 | 93 | `2eed55518a9ff821...` | `2eed55518a9ff821...` | **PASS** |
| **sales_reps** | 12 | 12 | `a6d91fc1ebe28ed7...` | `a6d91fc1ebe28ed7...` | **PASS** |
| **score_rules** | 2 | 2 | `9004e8593a7aadf0...` | `9004e8593a7aadf0...` | **PASS** |
| **stage_histories** | 327 | 327 | `d84cb51e76307a48...` | `d84cb51e76307a48...` | **PASS** |
| **tasks** | 435 | 435 | `bad05f5b312adc5f...` | `bad05f5b312adc5f...` | **PASS** |

---

## 3. Deterministic ID Conformance

All entity identifiers strictly follow zero-padded conventions:
- Company IDs: `CO-000001`
- Contact IDs: `CON-000001`
- Lead IDs: `LEAD-2026-000001`
- Activity IDs: `ACT-LEAD-2026-000001-001`
- Opportunity IDs: `OPP-2026-000001`
- Task IDs: `TASK-LEAD-2026-000001-001`

No random UUIDs or non-deterministic timestamps were utilized in identifier creation.
