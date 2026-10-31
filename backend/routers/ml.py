import json
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import joblib
import pandas as pd
from backend.core.database import get_db
from backend.core.config import ML_DIR
from backend.models.entities import Lead, Company, Contact, Activity
from backend.schemas.pydantic_models import MLEvaluationMetrics, MLPredictionRequest, MLPredictionResponse

router = APIRouter(prefix="/api/ml", tags=["Machine Learning"])


@router.get("/evaluation", response_model=MLEvaluationMetrics)
def get_ml_evaluation_metrics():
    metrics_path = ML_DIR / "metrics.json"
    if not metrics_path.exists():
        raise HTTPException(status_code=404, detail="ML model evaluation has not been executed yet. Run training pipeline first.")

    with open(metrics_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return {
        "model_type": data["model_type"],
        "train_size": data["train_size"],
        "test_size": data["test_size"],
        "accuracy": data["accuracy"],
        "precision": data["precision"],
        "recall": data["recall"],
        "f1_score": data["f1_score"],
        "roc_auc": data.get("roc_auc"),
        "confusion_matrix": data["confusion_matrix"],
        "feature_importance": data["feature_coefficients"],
        "evaluated_at": data["evaluated_at"],
    }


@router.post("/predict", response_model=MLPredictionResponse)
def predict_lead_conversion(request: MLPredictionRequest, db: Session = Depends(get_db)):
    model_path = ML_DIR / "logistic_regression_model.joblib"
    scaler_path = ML_DIR / "scaler.joblib"
    features_path = ML_DIR / "feature_names.joblib"

    if not model_path.exists() or not scaler_path.exists():
        raise HTTPException(status_code=500, detail="ML Model or Scaler artifact not found on disk.")

    model = joblib.load(model_path)
    scaler = joblib.load(scaler_path)
    feature_names = joblib.load(features_path)

    lead = db.query(Lead).filter(Lead.id == request.lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail=f"Lead {request.lead_id} not found")

    company = db.query(Company).filter(Company.id == lead.company_id).first()
    contact = db.query(Contact).filter(Contact.id == lead.contact_id).first()
    activities = db.query(Activity).filter(Activity.lead_id == lead.id).all()

    # Pre-conversion activity count
    valid_acts = [a for a in activities if not a.is_post_conversion]
    activity_count = len(valid_acts)

    # Build input feature vector
    raw_dict = {
        "fit_score": lead.fit_score,
        "intent_score": lead.intent_score,
        "engagement_score": lead.engagement_score,
        "employee_count": company.employee_count if company else 50,
        "annual_revenue": company.annual_revenue if company else 1000000.0,
        "is_enterprise": 1 if company and company.tier == "Enterprise" else 0,
        "is_executive": 1 if contact and contact.seniority_level in {"C-Level", "VP"} else 0,
        "activity_count": activity_count,
        "territory": lead.territory,
        "product_interest": lead.product_interest,
        "lead_source": lead.lead_source,
        "industry": company.industry if company else "Technology",
    }

    # Format vector matching feature_names
    input_df = pd.DataFrame([raw_dict])
    encoded_df = pd.get_dummies(input_df, columns=["territory", "product_interest", "lead_source", "industry"])

    # Align columns
    final_vector = pd.DataFrame(0, index=[0], columns=feature_names)
    for col in encoded_df.columns:
        if col in final_vector.columns:
            final_vector[col] = encoded_df[col].iloc[0]

    scaled_vector = scaler.transform(final_vector)
    prob = float(model.predict_proba(scaled_vector)[0][1])
    pred = bool(prob >= 0.50)

    return {
        "lead_id": lead.id,
        "rule_score": lead.lead_score,
        "priority": lead.priority,
        "conversion_probability": round(prob, 4),
        "predicted_conversion": pred,
        "explanation": {
            "firmographic_fit": lead.fit_score,
            "intent_signals": lead.intent_score,
            "engagement_depth": lead.engagement_score,
            "model_type": "Logistic Regression Classifier",
            "feature_contributions": "Available in model coefficients dashboard view",
        },
    }
