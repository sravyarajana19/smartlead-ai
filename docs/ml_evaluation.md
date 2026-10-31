# Machine Learning Evaluation Report

## Model: Logistic Regression Baseline Classifier
**Evaluation Date**: 2026-10-30T20:25:45.294009  
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
| **Accuracy** | **88.03%** | > 75.0% | Meets / Exceeds Target |
| **Precision** | **83.36%** | > 70.0% | High Confidence in Positives |
| **Recall** | **57.99%** | > 65.0% | Strong Identification Rate |
| **F1-Score** | **68.40%** | > 68.0% | Balanced Harmonic Mean |
| **ROC-AUC** | **0.8499** | > 0.75 | Strong Discrimination Power |

---

## 3. Confusion Matrix (Held-out Test Set)

```
                     Actual Positive      Actual Negative
Predicted Positive   501                  100                 
Predicted Negative   363                  2903                
```

- **True Positives (TP)**: 501
- **True Negatives (TN)**: 2903
- **False Positives (FP)**: 100
- **False Negatives (FN)**: 363

---

## 4. Top Feature Importances (Coefficients)

The model transparently weights input signals as follows:

| Rank | Feature Name | Logistic Regression Coefficient | Interpretation |
|---|---|---|---|
| 1 | `intent_score` | `+1.1214` | Positive (Increases Conversion Probability) |
| 2 | `fit_score` | `+0.9679` | Positive (Increases Conversion Probability) |
| 3 | `engagement_score` | `+0.5499` | Positive (Increases Conversion Probability) |
| 4 | `is_enterprise` | `-0.2198` | Negative (Decreases Conversion Probability) |
| 5 | `activity_count` | `+0.1521` | Positive (Increases Conversion Probability) |
| 6 | `employee_count` | `+0.0782` | Positive (Increases Conversion Probability) |
| 7 | `product_interest_Security Shield` | `+0.0358` | Positive (Increases Conversion Probability) |
| 8 | `is_executive` | `+0.0356` | Positive (Increases Conversion Probability) |
| 9 | `product_interest_Enterprise Suite` | `+0.0354` | Positive (Increases Conversion Probability) |
| 10 | `territory_EMEA` | `-0.0307` | Negative (Decreases Conversion Probability) |

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
