# Lead Scoring Methodology & Mathematical Formulation

## SMARTLEAD AI Transparent Scoring System

This document provides a technical walkthrough of the deterministic, explainable lead scoring engine powering SmartLead AI.

---

## 1. Mathematical Formulation

The composite **Lead Score** $S \in [0.0, 100.0]$ is computed as a linear convex combination of three sub-dimensional indices:

$$S = (w_{\text{fit}} \cdot S_{\text{fit}}) + (w_{\text{intent}} \cdot S_{\text{intent}}) + (w_{\text{eng}} \cdot S_{\text{eng}})$$

Where the baseline weights are:
- $w_{\text{fit}} = 0.40$ (Company Fit: 40%)
- $w_{\text{intent}} = 0.35$ (Buying Intent: 35%)
- $w_{\text{eng}} = 0.25$ (Engagement Depth: 25%)
- Subject to the constraint: $\sum w_i = 1.0$

---

## 2. Component Scoring Breakdown

### 2.1 Company Fit Score ($S_{\text{fit}} \in [0, 100]$)
Evaluates whether the prospective company matches our ideal customer profile (ICP):

| Sub-factor | Evaluation Criteria | Max Points |
|---|---|---|
| **Employee Scale** | $\ge 1,000$ (Enterprise) = 40 pts<br>$250 - 999$ (Upper Mid-Market) = 30 pts<br>$50 - 249$ (Lower Mid-Market) = 20 pts<br>$< 50$ (SMB) = 10 pts | 40.0 pts |
| **Annual Revenue** | $\ge \$50\text{M}$ = 30 pts<br>$\$10\text{M} - \$50\text{M}$ = 20 pts<br>$\$1\text{M} - \$10\text{M}$ = 15 pts<br>$< \$1\text{M}$ = 5 pts | 30.0 pts |
| **Industry Alignment** | High-Fit (Technology, Financial Services, Healthcare, Manufacturing) = 20 pts<br>Secondary Industries (Retail, Services) = 10 pts | 20.0 pts |
| **Buyer Persona Seniority** | C-Level / VP = 10 pts<br>Director / Head = 8 pts<br>Manager / Lead = 5 pts<br>Individual Contributor = 2 pts | 10.0 pts |
| **Total Max Fit** | Sum of sub-factors bounded at 100.0 | **100.0 pts** |

---

### 2.2 Buying Intent Score ($S_{\text{intent}} \in [0, 100]$)
Evaluates active purchasing signals exhibited through digital interactions prior to opportunity conversion:

| Interaction Signal | Intent Score Contribution |
|---|---|
| **High Intent Source** | Inbound Website Form / Referral Source = +25.0 pts<br>Event / Organic Search = +15.0 pts<br>Outbound / Cold Source = +5.0 pts |
| **Demo Request** | +40.0 pts per occurrence |
| **Pricing Page Visit** | +25.0 pts per occurrence |
| **Webinar Attendance** | +20.0 pts per occurrence |
| **Inbound Call** | +20.0 pts per occurrence |
| **Whitepaper Download** | +15.0 pts per occurrence |
| **Total Max Intent** | Bounded at $[0.0, 100.0]$ |

---

### 2.3 Engagement Depth Score ($S_{\text{eng}} \in [0, 100]$)
Measures the velocity, recency, and multi-channel consistency of account engagement:

| Dimension | Evaluation Logic | Max Points |
|---|---|---|
| **Frequency of Touchpoints** | $\ge 8$ valid events = 35 pts<br>$5 - 7$ events = 28 pts<br>$3 - 4$ events = 20 pts<br>$1 - 2$ events = 10 pts | 35.0 pts |
| **Recency of Last Event** | Within 7 days = 35 pts<br>Within 30 days = 25 pts<br>Within 90 days = 15 pts<br>$> 90$ days = 5 pts | 35.0 pts |
| **Channel Diversity** | Email Click (+15 pts) + Email Open (+8 pts) + Web Session (+7 pts) | 30.0 pts |
| **Total Max Engagement** | Bounded at $[0.0, 100.0]$ | **100.0 pts** |

---

## 3. Priority Classification Tiers

| Composite Score ($S$) | Priority Classification | SLA Response Window | Routing Target |
|---|---|---|---|
| **$80.00 \le S \le 100.00$** | **High** | $\le 24$ hours (Urgent SLA) | Dedicated Enterprise Product Specialist |
| **$50.00 \le S < 80.00$** | **Medium** | $\le 48$ hours (High SLA) | Territory Account Representative |
| **$0.00 \le S < 50.00$** | **Low** | $\le 5$ business days (Normal SLA) | Automated Marketing Nurture Track |

---

## 4. Protection Against Temporal Data Leakage (CASE 2)

A common flaw in sales scoring models is utilizing post-conversion data (e.g. contract signatures or post-sale onboarding views) to score the initial lead.

SmartLead AI implements a strict temporal window filter:
```python
if converted_date and activity_date > converted_date:
    leakage_detected = True
    if filter_post_conversion:
        continue # Exclude from score computation
```
Any calculation that includes post-conversion activities without filtering is flagged with an anomaly alert: `CASE_2_TEMPORAL_LEAKAGE`.

---

## 5. Explainability Payload Format

For every evaluated lead, the engine generates an explainable contribution breakdown returned via the API and displayed in Streamlit:
```json
{
  "lead_id": "LEAD-2026-000001",
  "fit_score": 85.0,
  "intent_score": 70.0,
  "engagement_score": 60.0,
  "lead_score": 73.5,
  "priority": "Medium",
  "rule_version": "v1.0.0",
  "explanation_details": {
    "weighted_contributions": {
      "fit_contribution": 34.0,
      "intent_contribution": 24.5,
      "engagement_contribution": 15.0
    }
  }
}
```
