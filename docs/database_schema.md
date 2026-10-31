# Database Schema & Entity Relationship Diagram (ERD)

## SMARTLEAD AI Platform
**Architecture**: Relational Star/Snowflake Hybrid OLTP Schema  
**Database Engine**: SQLite with enforced Foreign Keys (`PRAGMA foreign_keys = ON`)  
**ORM Layer**: SQLAlchemy 2.0  

---

## 1. Entity-Relationship Diagram (ERD)

```mermaid
erDiagram
    COMPANIES ||--o{ CONTACTS : "employs (1:N)"
    COMPANIES ||--o{ LEADS : "generates (1:N)"
    COMPANIES ||--o{ OPPORTUNITIES : "holds (1:N)"
    
    CONTACTS ||--o{ LEADS : "submits (1:N)"
    CONTACTS ||--o{ CONSENTS : "grants (1:N)"
    
    CAMPAIGNS ||--o{ LEADS : "attracts (1:N)"
    
    SALES_REPS ||--o{ LEADS : "assigned_to (1:N)"
    SALES_REPS ||--o{ TASKS : "owns (1:N)"
    SALES_REPS ||--o{ OPPORTUNITIES : "manages (1:N)"
    
    LEADS ||--o{ ACTIVITIES : "records (1:N)"
    LEADS ||--o{ CONSENTS : "maintains (1:N)"
    LEADS ||--o{ TASKS : "triggers (1:N)"
    LEADS ||--o{ OPPORTUNITIES : "converts_to (1:N)"
    LEADS ||--o{ DUPLICATE_RELATIONSHIPS : "participates_in (1:N)"
    
    OPPORTUNITIES ||--o{ STAGE_HISTORIES : "tracks (1:N)"

    COMPANIES {
        string id PK "CO-000001"
        string name "Company Name"
        string domain "Domain URL"
        string industry "Industry Sector"
        int employee_count "Staff Count"
        float annual_revenue "Revenue in USD"
        string country "Country"
        string territory "Territory"
        string tier "Enterprise / Mid-Market / SMB"
        datetime created_at
        datetime updated_at
    }

    CONTACTS {
        string id PK "CON-000001"
        string company_id FK "CO-000001"
        string first_name "First Name"
        string last_name "Last Name"
        string email "Email Address (Indexed)"
        string phone "Raw Phone"
        string normalized_phone "E.164 Normalized"
        string job_title "Job Title"
        string seniority_level "C-Level / VP / Director / Manager"
        string department "Department"
        boolean is_primary "Primary Account Contact"
        datetime created_at
        datetime updated_at
    }

    LEADS {
        string id PK "LEAD-2026-000001"
        string company_id FK "CO-000001"
        string contact_id FK "CON-000001"
        string campaign_id FK "CMP-000001 (Nullable)"
        string assigned_rep_id FK "REP-000001 (Nullable)"
        string canonical_lead_id FK "LEAD-2026-000001 (Nullable)"
        string lead_source "Inbound / Referral / Event / Web"
        string product_interest "Product Line"
        string territory "Territory"
        string status "New / Working / Qualified / Converted"
        float fit_score "0.0 - 100.0"
        float intent_score "0.0 - 100.0"
        float engagement_score "0.0 - 100.0"
        float lead_score "0.0 - 100.0 (Weighted)"
        string priority "High / Medium / Low"
        boolean is_duplicate "Duplicate Flag"
        boolean is_converted "Converted Flag"
        datetime converted_date "Conversion Timestamp"
        datetime created_at
        datetime updated_at
    }

    CAMPAIGNS {
        string id PK "CMP-000001"
        string name "Campaign Name"
        string campaign_type "Webinar / Launch / Whitepaper"
        string channel "Email / Web / Social / Event"
        float budget "Budget USD"
        date start_date
        date end_date
        string target_territory "Territory Target"
        string target_product "Product Target"
        string status "Active / Completed / Planned"
        datetime created_at
    }

    ACTIVITIES {
        string id PK "ACT-LEAD-2026-000001-001"
        string lead_id FK "LEAD-2026-000001"
        string activity_type "Demo Request / Pricing View / etc"
        string channel "Web / Email / Phone / Event"
        float intent_weight "Weight contribution"
        float engagement_weight "Weight contribution"
        datetime activity_date "Timestamp of activity"
        string metadata_json "Payload details"
        boolean is_post_conversion "Temporal Leakage Flag"
        datetime created_at
    }

    CONSENTS {
        string id PK "CNS-000001"
        string lead_id FK "LEAD-2026-000001"
        string contact_id FK "CON-000001"
        string consent_status "Opt-In / Opt-Out / Pending"
        string consent_type "Email / Phone / SMS / All"
        string channel "Email / Web / Phone"
        datetime effective_date "Consent Granted At"
        datetime expiry_date "Expiry Timestamp"
        datetime opt_out_timestamp "Revocation Timestamp"
        string notes "Audit Reason"
        datetime created_at
        datetime updated_at
    }

    SCORE_RULES {
        string id PK "SCR-000001"
        string rule_version "v1.0.0"
        float fit_weight "0.40"
        float intent_weight "0.35"
        float engagement_weight "0.25"
        boolean is_active "Active Version Flag"
        string description "Rule description"
        datetime effective_start_date
        datetime effective_end_date
        datetime created_at
    }

    SALES_REPS {
        string id PK "REP-000001"
        string name "Representative Name"
        string email "Corporate Email"
        string territory "Territory Alignment"
        string product_specialization "Product Focus"
        boolean is_active "Active Status"
        int capacity "Maximum Concurrent Leads"
        int current_load "Assigned Count"
        datetime created_at
        datetime updated_at
    }

    TASKS {
        string id PK "TASK-LEAD-2026-000001-001"
        string lead_id FK "LEAD-2026-000001"
        string assigned_rep_id FK "REP-000001"
        string task_type "Discovery Call / Demo / Outreach"
        string priority "Urgent / High / Normal"
        datetime due_date "SLA Due Date"
        string status "Pending / Completed / Blocked"
        string blocked_reason "Reason if Blocked by Opt-Out"
        boolean is_consent_verified "Verified Legal Clearance"
        datetime created_at
        datetime completed_at
    }

    OPPORTUNITIES {
        string id PK "OPP-2026-000001"
        string lead_id FK "LEAD-2026-000001"
        string company_id FK "CO-000001"
        string assigned_rep_id FK "REP-000001"
        string canonical_opp_id FK "OPP-2026-000001 (Nullable)"
        float opportunity_value "Deal Amount USD"
        string currency "USD"
        string current_stage "New / Qualified / Proposal / Negotiation / Won / Lost"
        datetime creation_date "Opened Date"
        datetime expected_close_date "Forecasted Close"
        datetime actual_close_date "Close Date"
        string won_lost_reason "Reason won or lost"
        boolean is_duplicate "Duplicate Opportunity Flag"
        datetime created_at
        datetime updated_at
    }

    STAGE_HISTORIES {
        string id PK "STG-OPP-2026-000001-001"
        string opportunity_id FK "OPP-2026-000001"
        string from_stage "Previous Stage"
        string to_stage "New Stage"
        int stage_duration_days "Dwell Time (Days)"
        datetime transition_date "Transition Timestamp"
        string changed_by "Actor or Engine"
        boolean is_valid_transition "State Machine Compliance"
        string notes "Audit Note"
        datetime created_at
    }

    DUPLICATE_RELATIONSHIPS {
        string id PK "DUP-000001"
        string primary_lead_id FK "LEAD-2026-000001"
        string duplicate_lead_id FK "LEAD-2026-000001"
        string match_type "Exact / Potential / Legitimate Repeat"
        string match_reason "Email / Phone / Domain Match"
        float similarity_score "1.0 to 0.7"
        string status "Detected / Merged / Dismissed"
        datetime detected_at
    }

    ANOMALY_RECORDS {
        string id PK "ANM-000001"
        string entity_type "Lead / Task / Activity / Opp / Stage"
        string entity_id "Entity ID Ref"
        string issue_type "CASE_1_CONSENT ... CASE_5_STAGE"
        string severity "Critical / High / Medium"
        string ground_truth_label "Label"
        string expected_decision "Expected Action"
        string actual_decision "Observed Action"
        string explanation "Detailed explanation"
        datetime detected_at
        string resolution_status "Open / In Review"
    }
```

---

## 2. Relational Cardinality & Integrity Rules

1. **Company to Contacts (`1:N`)**: A single company can have multiple contacts. If a company record is removed, orphan cascade cleanup occurs.
2. **Contact to Leads (`1:N`)**: Multiple leads over time can originate from the same contact persona (e.g. repeated interest).
3. **Lead to Activities (`1:N`)**: Touchpoints belong strictly to a single lead. Cascade delete applies on lead deletion.
4. **Lead to Consent (`1:1` or `1:N`)**: Consent is tracked per lead and contact, preserving full revocation history in `consent_histories`.
5. **Opportunity to StageHistory (`1:N`)**: Every lifecycle stage change is appended as an immutable event record. Historical states are never overwritten.
