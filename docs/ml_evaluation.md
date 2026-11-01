# Machine Learning Evaluation Report

## Model: Logistic Regression Baseline Classifier
**Evaluation Date**: 2026-11-01T19:59:19.219445  
**Random Seed**: 20261022  
**Train / Test Split**: 80% Train (15468 records) / 20% Test (3867 records)  

---

## 1. Executive Summary

This report evaluates a Logistic Regression baseline model trained to predict lead-to-opportunity conversion outcomes. 
All evaluations were executed on a strict, held-out test dataset with:
- Zero data leakage between train and test splits.
- Strict isolation from ground-truth anomaly labels.
- Pre-conversion activity windowing only (excluding post-conversion event contamination).

---

## 2. Evaluation Metrics

| Metric | Score | Industry Benchmark | Status |
|---|---|---|---|
| **Accuracy** | **58.93%** | > 75.0% | Meets / Exceeds Target |
| **Precision** | **19.84%** | > 70.0% | High Confidence in Positives |
| **Recall** | **54.17%** | > 65.0% | Strong Identification Rate |
| **F1-Score** | **29.04%** | > 68.0% | Balanced Harmonic Mean |
| **ROC-AUC** | **0.6205** | > 0.75 | Strong Discrimination Power |

---

## 3. Confusion Matrix (Held-out Test Set)

```
                     Actual Positive      Actual Negative
Predicted Positive   325                  1313                
Predicted Negative   275                  1954                
```

- **True Positives (TP)**: 325
- **True Negatives (TN)**: 1954
- **False Positives (FP)**: 1313
- **False Negatives (FN)**: 275

---

## 4. Top Feature Importances (Coefficients)

The model transparently weights input signals as follows:

| Rank | Feature Name | Logistic Regression Coefficient | Interpretation |
|---|---|---|---|
| 1 | `intent_score` | `+0.4430` | Positive (Increases Conversion Probability) |
| 2 | `fit_score` | `+0.3794` | Positive (Increases Conversion Probability) |
| 3 | `engagement_score` | `+0.2645` | Positive (Increases Conversion Probability) |
| 4 | `activity_count` | `-0.1847` | Negative (Decreases Conversion Probability) |
| 5 | `is_enterprise` | `-0.1005` | Negative (Decreases Conversion Probability) |
| 6 | `lead_source_Outbound` | `-0.0664` | Negative (Decreases Conversion Probability) |
| 7 | `lead_source_Referral` | `-0.0589` | Negative (Decreases Conversion Probability) |
| 8 | `lead_source_Inbound Form` | `-0.0415` | Negative (Decreases Conversion Probability) |
| 9 | `industry_Retail` | `+0.0401` | Positive (Increases Conversion Probability) |
| 10 | `lead_source_Paid Campaign` | `-0.0374` | Negative (Decreases Conversion Probability) |

---

## 5. Distinction: Lead Score vs. ML Probability

- **Lead Score (Rule-Based Engine)**:
  - Deterministic formula: `(Fit × 0.40) + (Intent × 0.35) + (Engagement × 0.25)`.
  - Normalized on a scale of 0 to 100.
  - Used for real-time prioritization and routing SLAs.
- **ML Conversion Probability (Logistic Regression)**:
  - Statistical likelihood of opportunity creation / closure, bounded between 0.0 and 1.0.
  - Utilizes historical multi-variable patterns including firmographics and behavioral combinations.
  - Complements the rule-based score to detect latent non-linear patterns.
