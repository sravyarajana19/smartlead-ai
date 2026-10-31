# Reproducibility and Determinism Report

**Random Seed**: `20261022`  
**Verification Result**: `100% BITWISE IDENTICAL`  
**Run 1 Global Digest (SHA-256)**: `fc0a93f886a8f8c5e8fcc53aba66d5683904299aca7325d1554721265555a08c`  
**Run 2 Global Digest (SHA-256)**: `fc0a93f886a8f8c5e8fcc53aba66d5683904299aca7325d1554721265555a08c`  

---

## 1. Executive Summary

To satisfy strict enterprise compliance and forward-deployed engineering standards, SmartLead AI implements deterministic data generation and rule evaluation. Two independent generation runs were executed using seed `20261022`. All row counts, deterministic zero-padded IDs, calculated lead scores, and injected ground-truth anomalies were compared.

The results confirm that the platform is **100% deterministic and reproducible** across separate execution cycles.

---

## 2. Table-by-Table Reproducibility Audit

| Entity / Dataset | Run 1 Count | Run 2 Count | Run 1 SHA-256 Digest | Run 2 SHA-256 Digest | Match Status |
|---|---|---|---|---|---|
| **activities** | 2,173 | 2,173 | `40434b1bcd7ac829...` | `40434b1bcd7ac829...` | **PASS** |
| **anomalies** | 15 | 15 | `8eee29fb6f8989f5...` | `8eee29fb6f8989f5...` | **PASS** |
| **campaigns** | 10 | 10 | `223130d454bf7861...` | `223130d454bf7861...` | **PASS** |
| **companies** | 150 | 150 | `836fb03b54a59d55...` | `836fb03b54a59d55...` | **PASS** |
| **consent_histories** | 75 | 75 | `1034676c942cdf79...` | `1034676c942cdf79...` | **PASS** |
| **consents** | 600 | 600 | `806d753d3873c8ba...` | `806d753d3873c8ba...` | **PASS** |
| **contacts** | 300 | 300 | `db4b5d1412270243...` | `db4b5d1412270243...` | **PASS** |
| **duplicate_relationships** | 19 | 19 | `f97fa6e6950e251e...` | `f97fa6e6950e251e...` | **PASS** |
| **leads** | 600 | 600 | `0041a2f07dab81da...` | `0041a2f07dab81da...` | **PASS** |
| **opportunities** | 93 | 93 | `2cf38fd30e833edd...` | `2cf38fd30e833edd...` | **PASS** |
| **sales_reps** | 12 | 12 | `985c2c26f06c1575...` | `985c2c26f06c1575...` | **PASS** |
| **score_rules** | 2 | 2 | `9004e8593a7aadf0...` | `9004e8593a7aadf0...` | **PASS** |
| **stage_histories** | 334 | 334 | `aadf2941e8f73881...` | `aadf2941e8f73881...` | **PASS** |
| **tasks** | 427 | 427 | `b09baeb91cdd1ed4...` | `b09baeb91cdd1ed4...` | **PASS** |

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
