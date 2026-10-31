# SMARTLEAD AI Data Dictionary

Comprehensive technical data dictionary covering all 11 mandatory entities and supporting bridge/audit tables.

---

## 1. Entity: `Company` (`companies`)

| Field Name | Data Type | Req/Opt | Allowed Values | Units | Uniqueness | Validation Rules | Keys & Relationships |
|---|---|---|---|---|---|---|---|
| `id` | `VARCHAR(32)` | Required | Format: `CO-000001` | String | Unique (PK) | Regex: `^CO-\d{6}$` | Primary Key |
| `name` | `VARCHAR(255)` | Required | Any non-empty string | Text | Non-unique | Length: 1–255 chars | None |
| `domain` | `VARCHAR(255)` | Required | Valid FQDN (e.g. `acme.com`) | Domain | Non-unique | Valid domain format | Indexed |
| `industry` | `VARCHAR(100)` | Required | `Technology`, `Financial Services`, `Healthcare`, `Manufacturing`, `Retail`, `Professional Services` | Categorical | Non-unique | Must match allowed industry catalog | Indexed |
| `employee_count` | `INTEGER` | Required | Integer `>= 1` | Count | Non-unique | Positive integer | None |
| `annual_revenue` | `FLOAT` | Required | Float `>= 0.0` | USD ($) | Non-unique | Non-negative numeric | None |
| `country` | `VARCHAR(100)` | Required | ISO or standard country name | String | Non-unique | Non-empty string | None |
| `territory` | `VARCHAR(50)` | Required | `North America`, `EMEA`, `APAC`, `LATAM` | Categorical | Non-unique | Must match territory catalog | Indexed |
| `tier` | `VARCHAR(50)` | Required | `Enterprise`, `Mid-Market`, `SMB` | Categorical | Non-unique | Must match tier definitions | None |
| `created_at` | `DATETIME` | Required | ISO 8601 Datetime | Timestamp | Non-unique | Must be `<=` current timestamp | None |
| `updated_at` | `DATETIME` | Required | ISO 8601 Datetime | Timestamp | Non-unique | Must be `>= created_at` | None |

---

## 2. Entity: `Contact` (`contacts`)

| Field Name | Data Type | Req/Opt | Allowed Values | Units | Uniqueness | Validation Rules | Keys & Relationships |
|---|---|---|---|---|---|---|---|
| `id` | `VARCHAR(32)` | Required | Format: `CON-000001` | String | Unique (PK) | Regex: `^CON-\d{6}$` | Primary Key |
| `company_id` | `VARCHAR(32)` | Required | Existing `companies.id` | String | Non-unique | Referential integrity | Foreign Key -> `companies.id` |
| `first_name` | `VARCHAR(100)` | Required | String | Text | Non-unique | Length: 1–100 chars | None |
| `last_name` | `VARCHAR(100)` | Required | String | Text | Non-unique | Length: 1–100 chars | None |
| `email` | `VARCHAR(255)` | Required | Valid email string | RFC 5322 | Non-unique | Standard email regex validation | Indexed |
| `phone` | `VARCHAR(50)` | Optional | Raw phone format | Phone | Non-unique | None | None |
| `normalized_phone`| `VARCHAR(50)` | Optional | E.164 format (e.g. `+15551234567`) | Phone | Non-unique | Digits prefixed with `+` | Indexed |
| `job_title` | `VARCHAR(100)` | Required | String | Text | Non-unique | Non-empty string | None |
| `seniority_level` | `VARCHAR(50)` | Required | `C-Level`, `VP`, `Director`, `Manager`, `Individual` | Categorical | Non-unique | Must match seniority catalog | None |
| `department` | `VARCHAR(100)` | Required | String | Text | Non-unique | Non-empty string | None |
| `is_primary` | `BOOLEAN` | Required | `True`, `False` (or 1, 0) | Flag | Non-unique | Boolean | None |
| `created_at` | `DATETIME` | Required | ISO 8601 Datetime | Timestamp | Non-unique | Must be `<=` current timestamp | None |
| `updated_at` | `DATETIME` | Required | ISO 8601 Datetime | Timestamp | Non-unique | Must be `>= created_at` | None |

---

## 3. Entity: `Lead` (`leads`)

| Field Name | Data Type | Req/Opt | Allowed Values | Units | Uniqueness | Validation Rules | Keys & Relationships |
|---|---|---|---|---|---|---|---|
| `id` | `VARCHAR(32)` | Required | Format: `LEAD-2026-000001` | String | Unique (PK) | Regex: `^LEAD-\d{4}-\d{6}$` | Primary Key |
| `company_id` | `VARCHAR(32)` | Required | Existing `companies.id` | String | Non-unique | Referential integrity | Foreign Key -> `companies.id` |
| `contact_id` | `VARCHAR(32)` | Required | Existing `contacts.id` | String | Non-unique | Referential integrity | Foreign Key -> `contacts.id` |
| `campaign_id` | `VARCHAR(32)` | Optional | Existing `campaigns.id` | String | Non-unique | Referential integrity | Foreign Key -> `campaigns.id` |
| `assigned_rep_id`| `VARCHAR(32)` | Optional | Existing `sales_reps.id` | String | Non-unique | Referential integrity | Foreign Key -> `sales_reps.id` |
| `canonical_lead_id`|`VARCHAR(32)`| Optional | Existing `leads.id` | String | Non-unique | Points to canonical record if dup | Foreign Key -> `leads.id` |
| `lead_source` | `VARCHAR(100)`| Required | `Website`, `Inbound Form`, `Referral`, `Event`, `Organic Search`, `Paid Campaign`, `Outbound` | Categorical | Non-unique | Allowed source catalog | Indexed |
| `product_interest`| `VARCHAR(100)`| Required | `Enterprise Suite`, `Cloud Platform`, `Security Shield`, `AI Analytics` | Categorical | Non-unique | Allowed products | Indexed |
| `territory` | `VARCHAR(50)` | Required | `North America`, `EMEA`, `APAC`, `LATAM` | Categorical | Non-unique | Allowed territories | Indexed |
| `status` | `VARCHAR(50)` | Required | `New`, `Contacted`, `Working`, `Qualified`, `Unqualified`, `Converted` | Categorical | Non-unique | Allowed statuses | Indexed |
| `fit_score` | `FLOAT` | Required | `0.0` to `100.0` | Pts | Non-unique | Bound between 0 and 100 | None |
| `intent_score` | `FLOAT` | Required | `0.0` to `100.0` | Pts | Non-unique | Bound between 0 and 100 | None |
| `engagement_score`|`FLOAT` | Required | `0.0` to `100.0` | Pts | Non-unique | Bound between 0 and 100 | None |
| `lead_score` | `FLOAT` | Required | `0.0` to `100.0` | Pts | Non-unique | `Fit*0.4 + Intent*0.35 + Eng*0.25` | Indexed |
| `priority` | `VARCHAR(20)` | Required | `High`, `Medium`, `Low` | Categorical | Non-unique | High (>=80), Med (50-79.99), Low (<50) | Indexed |
| `is_duplicate` | `BOOLEAN` | Required | `True`, `False` | Flag | Non-unique | Boolean | Indexed |
| `is_converted` | `BOOLEAN` | Required | `True`, `False` | Flag | Non-unique | Boolean | Indexed |
| `converted_date` | `DATETIME` | Optional | ISO 8601 Datetime | Timestamp | Non-unique | Must be `>= created_at` | None |
| `created_at` | `DATETIME` | Required | ISO 8601 Datetime | Timestamp | Non-unique | Standard audit | Indexed |
| `updated_at` | `DATETIME` | Required | ISO 8601 Datetime | Timestamp | Non-unique | Must be `>= created_at` | None |

---

## 4. Entity: `Campaign` (`campaigns`)

| Field Name | Data Type | Req/Opt | Allowed Values | Units | Uniqueness | Validation Rules | Keys & Relationships |
|---|---|---|---|---|---|---|---|
| `id` | `VARCHAR(32)` | Required | Format: `CMP-000001` | String | Unique (PK) | Regex: `^CMP-\d{6}$` | Primary Key |
| `name` | `VARCHAR(255)` | Required | String | Text | Non-unique | Length: 1–255 chars | None |
| `campaign_type` | `VARCHAR(100)` | Required | `Webinar`, `Whitepaper`, `Product Launch`, `Email Blast`, `Search Ads`, `Partner Co-Marketing` | Categorical | Non-unique | Allowed campaign types | None |
| `channel` | `VARCHAR(50)` | Required | `Email`, `Web`, `Social`, `Search`, `Event` | Categorical | Non-unique | Allowed channels | None |
| `budget` | `FLOAT` | Required | Numeric `>= 0.0` | USD ($) | Non-unique | Non-negative | None |
| `start_date` | `DATE` | Required | ISO Date (`YYYY-MM-DD`) | Date | Non-unique | Standard date | None |
| `end_date` | `DATE` | Required | ISO Date (`YYYY-MM-DD`) | Date | Non-unique | Must be `>= start_date` | None |
| `target_territory`|`VARCHAR(50)` | Required | Valid territory | Categorical | Non-unique | Territory catalog | None |
| `target_product` | `VARCHAR(100)`| Required | Valid product | Categorical | Non-unique | Product catalog | None |
| `status` | `VARCHAR(50)` | Required | `Active`, `Completed`, `Planned`, `Paused` | Categorical | Non-unique | Allowed campaign status | None |
| `created_at` | `DATETIME` | Required | ISO 8601 Datetime | Timestamp | Non-unique | Standard audit | None |

---

## 5. Entity: `Activity` (`activities`)

| Field Name | Data Type | Req/Opt | Allowed Values | Units | Uniqueness | Validation Rules | Keys & Relationships |
|---|---|---|---|---|---|---|---|
| `id` | `VARCHAR(64)` | Required | Format: `ACT-LEAD-2026-000001-001` | String | Unique (PK) | Standard sequence | Primary Key |
| `lead_id` | `VARCHAR(32)` | Required | Existing `leads.id` | String | Non-unique | Referential integrity | Foreign Key -> `leads.id` |
| `activity_type` | `VARCHAR(100)` | Required | `Page View`, `Pricing View`, `Whitepaper Download`, `Webinar Attend`, `Demo Request`, `Email Open`, `Email Click`, `Inbound Call` | Categorical | Non-unique | Activity taxonomy | Indexed |
| `channel` | `VARCHAR(50)` | Required | `Web`, `Email`, `Phone`, `Event` | Categorical | Non-unique | Channel taxonomy | None |
| `intent_weight` | `FLOAT` | Required | Numeric `>= 0.0` | Pts | Non-unique | Non-negative weight | None |
| `engagement_weight`|`FLOAT` | Required | Numeric `>= 0.0` | Pts | Non-unique | Non-negative weight | None |
| `activity_date` | `DATETIME` | Required | ISO 8601 Datetime | Timestamp | Non-unique | Event occurrence time | Indexed |
| `metadata_json` | `TEXT` | Optional | JSON string | JSON | Non-unique | Valid JSON payload | None |
| `is_post_conversion`|`BOOLEAN` | Required | `True`, `False` | Flag | Non-unique | Temporal leakage marker | Indexed |
| `created_at` | `DATETIME` | Required | ISO 8601 Datetime | Timestamp | Non-unique | Standard audit | None |

---

## 6. Entity: `Consent` (`consents`)

| Field Name | Data Type | Req/Opt | Allowed Values | Units | Uniqueness | Validation Rules | Keys & Relationships |
|---|---|---|---|---|---|---|---|
| `id` | `VARCHAR(32)` | Required | Format: `CNS-000001` | String | Unique (PK) | Regex: `^CNS-\d{6}$` | Primary Key |
| `lead_id` | `VARCHAR(32)` | Required | Existing `leads.id` | String | Non-unique | Referential integrity | Foreign Key -> `leads.id` |
| `contact_id` | `VARCHAR(32)` | Required | Existing `contacts.id` | String | Non-unique | Referential integrity | Foreign Key -> `contacts.id` |
| `consent_status` | `VARCHAR(50)` | Required | `Opt-In`, `Opt-Out`, `Pending` | Categorical | Non-unique | Allowed consent statuses | Indexed |
| `consent_type` | `VARCHAR(50)` | Required | `Email`, `Phone`, `SMS`, `All` | Categorical | Non-unique | Consent communication types | None |
| `channel` | `VARCHAR(50)` | Required | `Email`, `Phone`, `SMS`, `Web` | Categorical | Non-unique | Origin channel | None |
| `effective_date` | `DATETIME` | Required | ISO 8601 Datetime | Timestamp | Non-unique | Granted date | None |
| `expiry_date` | `DATETIME` | Optional | ISO 8601 Datetime | Timestamp | Non-unique | If provided, `>= effective_date` | None |
| `opt_out_timestamp`|`DATETIME` | Optional | ISO 8601 Datetime | Timestamp | Non-unique | Required if `Opt-Out` | None |
| `notes` | `TEXT` | Optional | String | Text | Non-unique | Compliance audit reason | None |
| `created_at` | `DATETIME` | Required | ISO 8601 Datetime | Timestamp | Non-unique | Standard audit | None |
| `updated_at` | `DATETIME` | Required | ISO 8601 Datetime | Timestamp | Non-unique | Standard audit | None |

---

## 7. Entity: `ScoreRule` (`score_rules`)

| Field Name | Data Type | Req/Opt | Allowed Values | Units | Uniqueness | Validation Rules | Keys & Relationships |
|---|---|---|---|---|---|---|---|
| `id` | `VARCHAR(32)` | Required | Format: `SCR-000001` | String | Unique (PK) | Regex: `^SCR-\d{6}$` | Primary Key |
| `rule_version` | `VARCHAR(50)` | Required | e.g. `v1.0.0` | String | Unique | SemVer format | Unique Key |
| `fit_weight` | `FLOAT` | Required | `0.0` to `1.0` | Weight | Non-unique | Weights must sum to 1.0 | None |
| `intent_weight` | `FLOAT` | Required | `0.0` to `1.0` | Weight | Non-unique | Weights must sum to 1.0 | None |
| `engagement_weight`|`FLOAT` | Required | `0.0` to `1.0` | Weight | Non-unique | Weights must sum to 1.0 | None |
| `is_active` | `BOOLEAN` | Required | `True`, `False` | Flag | Non-unique | Only one active version | None |
| `description` | `TEXT` | Optional | String | Text | Non-unique | Explanatory note | None |
| `effective_start_date`|`DATETIME`| Required | ISO 8601 Datetime | Timestamp | Non-unique | Activation date | None |
| `effective_end_date`|`DATETIME` | Optional | ISO 8601 Datetime | Timestamp | Non-unique | Retirement date | None |
| `created_at` | `DATETIME` | Required | ISO 8601 Datetime | Timestamp | Non-unique | Standard audit | None |

---

## 8. Entity: `SalesRep` (`sales_reps`)

| Field Name | Data Type | Req/Opt | Allowed Values | Units | Uniqueness | Validation Rules | Keys & Relationships |
|---|---|---|---|---|---|---|---|
| `id` | `VARCHAR(32)` | Required | Format: `REP-000001` | String | Unique (PK) | Regex: `^REP-\d{6}$` | Primary Key |
| `name` | `VARCHAR(150)` | Required | String | Text | Non-unique | Non-empty string | None |
| `email` | `VARCHAR(255)` | Required | Valid email string | RFC 5322 | Unique | Unique representative email | Unique Key |
| `territory` | `VARCHAR(50)` | Required | Valid territory | Categorical | Non-unique | Territory catalog | Indexed |
| `product_specialization`|`VARCHAR(100)`| Required | Valid product | Categorical | Non-unique | Product catalog | Indexed |
| `is_active` | `BOOLEAN` | Required | `True`, `False` | Flag | Non-unique | Boolean | None |
| `capacity` | `INTEGER` | Required | Integer `>= 1` | Count | Non-unique | Max concurrent leads/opps | None |
| `current_load` | `INTEGER` | Required | Integer `>= 0` | Count | Non-unique | Active assigned volume | None |
| `created_at` | `DATETIME` | Required | ISO 8601 Datetime | Timestamp | Non-unique | Standard audit | None |
| `updated_at` | `DATETIME` | Required | ISO 8601 Datetime | Timestamp | Non-unique | Standard audit | None |

---

## 9. Entity: `Task` (`tasks`)

| Field Name | Data Type | Req/Opt | Allowed Values | Units | Uniqueness | Validation Rules | Keys & Relationships |
|---|---|---|---|---|---|---|---|
| `id` | `VARCHAR(64)` | Required | Format: `TASK-LEAD-2026-000001-001` | String | Unique (PK) | Standard sequence | Primary Key |
| `lead_id` | `VARCHAR(32)` | Required | Existing `leads.id` | String | Non-unique | Referential integrity | Foreign Key -> `leads.id` |
| `assigned_rep_id`| `VARCHAR(32)` | Required | Existing `sales_reps.id` | String | Non-unique | Referential integrity | Foreign Key -> `sales_reps.id` |
| `task_type` | `VARCHAR(100)` | Required | `Discovery Call`, `Email Outreach`, `Product Demo`, `Contract Follow-up`, `Meeting` | Categorical | Non-unique | Task type taxonomy | None |
| `priority` | `VARCHAR(20)` | Required | `Urgent`, `High`, `Normal`, `Low` | Categorical | Non-unique | Task SLA priorities | None |
| `due_date` | `DATETIME` | Required | ISO 8601 Datetime | Timestamp | Non-unique | SLA schedule date | Indexed |
| `status` | `VARCHAR(50)` | Required | `Pending`, `In Progress`, `Completed`, `Cancelled`, `Blocked` | Categorical | Non-unique | Task lifecycle state | Indexed |
| `blocked_reason` | `TEXT` | Optional | String | Text | Non-unique | Set if blocked by opt-out | None |
| `is_consent_verified`|`BOOLEAN`| Required | `True`, `False` | Flag | Non-unique | Must be True for active tasks | None |
| `created_at` | `DATETIME` | Required | ISO 8601 Datetime | Timestamp | Non-unique | Standard audit | None |
| `completed_at` | `DATETIME` | Optional | ISO 8601 Datetime | Timestamp | Non-unique | Completion timestamp | None |

---

## 10. Entity: `Opportunity` (`opportunities`)

| Field Name | Data Type | Req/Opt | Allowed Values | Units | Uniqueness | Validation Rules | Keys & Relationships |
|---|---|---|---|---|---|---|---|
| `id` | `VARCHAR(32)` | Required | Format: `OPP-2026-000001` | String | Unique (PK) | Regex: `^OPP-\d{4}-\d{6}$` | Primary Key |
| `lead_id` | `VARCHAR(32)` | Required | Existing `leads.id` | String | Non-unique | Referential integrity | Foreign Key -> `leads.id` |
| `company_id` | `VARCHAR(32)` | Required | Existing `companies.id` | String | Non-unique | Referential integrity | Foreign Key -> `companies.id` |
| `assigned_rep_id`| `VARCHAR(32)` | Required | Existing `sales_reps.id` | String | Non-unique | Referential integrity | Foreign Key -> `sales_reps.id` |
| `canonical_opp_id`|`VARCHAR(32)`| Optional | Existing `opportunities.id` | String | Non-unique | Referential integrity | Foreign Key -> `opportunities.id` |
| `opportunity_value`|`FLOAT` | Required | Numeric `>= 0.0` | Currency | Non-unique | Deal size amount | None |
| `currency` | `VARCHAR(10)` | Required | `USD`, `EUR`, `GBP` | Currency | Non-unique | Standard currency code | None |
| `current_stage` | `VARCHAR(50)` | Required | `New`, `Qualified`, `Proposal`, `Negotiation`, `Won`, `Lost` | Categorical | Non-unique | Pipeline state machine | Indexed |
| `creation_date` | `DATETIME` | Required | ISO 8601 Datetime | Timestamp | Non-unique | Must be `>= lead.created_at` | Indexed |
| `expected_close_date`|`DATETIME`| Required | ISO 8601 Datetime | Timestamp | Non-unique | Must be `>= creation_date` | None |
| `actual_close_date`|`DATETIME` | Optional | ISO 8601 Datetime | Timestamp | Non-unique | Set upon Won/Lost | None |
| `won_lost_reason`| `VARCHAR(255)`| Optional | Closed reason | Text | Non-unique | Reason for deal outcome | None |
| `is_duplicate` | `BOOLEAN` | Required | `True`, `False` | Flag | Non-unique | Case 4 duplicate marker | Indexed |
| `created_at` | `DATETIME` | Required | ISO 8601 Datetime | Timestamp | Non-unique | Standard audit | None |
| `updated_at` | `DATETIME` | Required | ISO 8601 Datetime | Timestamp | Non-unique | Standard audit | None |

---

## 11. Entity: `StageHistory` (`stage_histories`)

| Field Name | Data Type | Req/Opt | Allowed Values | Units | Uniqueness | Validation Rules | Keys & Relationships |
|---|---|---|---|---|---|---|---|
| `id` | `VARCHAR(64)` | Required | Format: `STG-OPP-2026-000001-001` | String | Unique (PK) | Standard sequence | Primary Key |
| `opportunity_id` | `VARCHAR(32)` | Required | Existing `opportunities.id` | String | Non-unique | Referential integrity | Foreign Key -> `opportunities.id` |
| `from_stage` | `VARCHAR(50)` | Optional | Valid pipeline stage or `NULL` | Categorical | Non-unique | Preceding stage | None |
| `to_stage` | `VARCHAR(50)` | Required | Valid pipeline stage | Categorical | Non-unique | Destination stage | None |
| `stage_duration_days`|`INTEGER` | Required | Integer `>= 0` | Days | Non-unique | Dwell duration in from_stage | None |
| `transition_date`| `DATETIME` | Required | ISO 8601 Datetime | Timestamp | Non-unique | Transition timestamp | Indexed |
| `changed_by` | `VARCHAR(100)` | Required | Actor string (e.g. `Sales Agent`) | String | Non-unique | Actor initiating transition | None |
| `is_valid_transition`|`BOOLEAN` | Required | `True`, `False` | Flag | Non-unique | State machine compliance | None |
| `notes` | `TEXT` | Optional | String | Text | Non-unique | Audit log comments | None |
| `created_at` | `DATETIME` | Required | ISO 8601 Datetime | Timestamp | Non-unique | Standard audit | None |
