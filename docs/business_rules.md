# SMARTLEAD AI Business Rules & Operating Governance

This document codifies the operational business rules, compliance policies, and automated enforcement mechanisms implemented across the SmartLead AI platform.

---

## 1. Lead Scoring Engine Rules

1. **Scoring Bounds**:
   - Every component score (`Fit`, `Intent`, `Engagement`) and the composite `Lead Score` must strictly fall within `[0.0, 100.0]`.
2. **Formula & Weighting**:
   $$\text{Lead Score} = (\text{Fit Score} \times 0.40) + (\text{Intent Score} \times 0.35) + (\text{Engagement Score} \times 0.25)$$
   - Weights must sum to exactly `1.0`. Any rule modification violating this constraint is rejected.
3. **Priority Thresholds**:
   - **High Priority**: Score $\ge 80.00$
   - **Medium Priority**: $50.00 \le \text{Score} < 80.00$
   - **Low Priority**: Score $< 50.00$
4. **Temporal Anti-Leakage Rule (CASE 2)**:
   - No activity timestamped after a lead's conversion date (`activity_date > converted_date`) may be incorporated into a lead's score calculation.
   - Any score utilizing post-conversion touchpoints is invalidated and flagged as a temporal leakage anomaly.

---

## 2. Consent Enforcement & Privacy Rules (CASE 1)

1. **Pre-Contact Verification**:
   - Consent status must be queried before creating any contact follow-up task or initiating outbound outreach.
2. **Opt-Out Primacy**:
   - An opted-out lead must **NEVER** receive follow-up contact tasks.
   - **Lead score cannot override opt-out**: A lead with a score of 100.0 is treated with identical blocking severity as a score of 0.0.
3. **CASE 1 Detection**:
   - If an outreach task is generated for a contact with `Opt-Out` status, the platform halts task dispatch, flags a `Critical` severity anomaly (`CASE_1_CONSENT_VIOLATION`), and logs the event in the audit ledger.

---

## 3. Deduplication Governance (CASE 4)

1. **Exact Duplicate Rule**:
   - Identified by identical lowercase email address or identical normalized phone number (`+1...`).
   - The original (earliest) record is designated as canonical. Subsequent records are marked `is_duplicate = True` and link to `canonical_lead_id`.
2. **Potential Duplicate Rule**:
   - Identified by identical company domain + identical contact last name.
   - Flagged for manual review and relationship mapping.
3. **Legitimate Repeat Lead Rule**:
   - If an existing contact submits a new inquiry for a **different product** after $\ge 180$ days, it is classified as a legitimate repeat lead and is not blocked.
4. **Duplicate Opportunity Rule (CASE 4)**:
   - When a duplicate lead generates a secondary opportunity for an account with an existing open opportunity, the second opportunity is marked `is_duplicate = True`, pointing to `canonical_opp_id`, and flagged for pipeline merge investigation.

---

## 4. Sales Routing & Territory Governance (CASE 3)

1. **Four-Tier Routing Algorithm**:
   - Tier 1: Local active representative matching both territory and product specialization with current load $<$ capacity.
   - Tier 2: Local active representative matching territory with capacity (general territory coverage).
   - Tier 3: Local reps exist but are at maximum capacity -> Lead flagged as `No_Capacity`.
   - Tier 4: No active rep in territory -> Lead placed in `General Triage Queue`.
2. **Deterministic Tie-Breaking**:
   - If multiple candidates qualify, the representative with the lowest `current_load` is selected. In case of equal load, alphabetical order of `REP-XXXXXX` breaks ties.
3. **CASE 3 Detection**:
   - If a lead in Territory A is assigned to a representative registered in Territory B, the routing engine reports a `CASE_3_ROUTING_VIOLATION` displaying expected territory vs actual territory.

---

## 5. Follow-Up Task Management & SLA Rules

1. **SLA Scheduling**:
   - High-priority leads receive `Urgent` tasks with a 1-day turnaround SLA.
   - Medium-priority leads receive `High` tasks with a 2-day SLA.
   - Low-priority leads receive `Normal` tasks with a 5-day SLA.
2. **Task Deduplication**:
   - If an identical task type (`Discovery Call`, `Email Outreach`) is currently `Pending` or `In Progress` for a lead, creation of a duplicate task is blocked.
3. **Consent Clearance**:
   - `is_consent_verified` must be explicitly asserted prior to task creation.

---

## 6. Opportunity Pipeline & Stage History Rules (CASE 5)

1. **Permitted Stage Transitions**:
   - `New` $\rightarrow$ `Qualified` or `Lost`
   - `Qualified` $\rightarrow$ `Proposal` or `Lost`
   - `Proposal` $\rightarrow$ `Negotiation` or `Lost`
   - `Negotiation` $\rightarrow$ `Won` or `Lost`
   - `Won` and `Lost` are terminal lifecycle states.
2. **Event-Sourced Stage History**:
   - Every stage transition appends an immutable `StageHistory` record documenting `from_stage`, `to_stage`, `stage_duration_days`, `transition_date`, and `changed_by`.
3. **CASE 5 Detection**:
   - Transitions directly jumping over intermediate stages (e.g. `New` directly to `Won`) violate the pipeline state machine. Such transitions are flagged as `CASE_5_MISSING_STAGE_TRANSITION` anomalies.
