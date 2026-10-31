import sys
import json
from pathlib import Path
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import joblib

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from backend.core.config import ML_DIR
from dashboard.components.data_loader import load_all_dashboard_data
from backend.core.database import SessionLocal
from backend.models.entities import Lead, Company, Contact, Activity

st.set_page_config(page_title="ML Evaluation - SMARTLEAD AI", page_icon="🤖", layout="wide")
st.title("🤖 Machine Learning Model Evaluation & Inference")

metrics_file = ML_DIR / "metrics.json"

if not metrics_file.exists():
    st.warning("ML Evaluation metrics not found. Please run the training pipeline first.")
    st.stop()

with open(metrics_file, "r", encoding="utf-8") as f:
    metrics = json.load(f)

st.markdown("""
Evaluation benchmark for the **Logistic Regression Baseline Classifier** trained on historical lead conversions:
- Evaluated on a **strict, held-out test split (20%)** with fixed random seed `20261022`.
- Zero post-conversion data leakage; ground-truth anomaly labels strictly excluded.
""")

# Top metrics row
m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Accuracy", f"{metrics['accuracy'] * 100:.2f}%")
m2.metric("Precision", f"{metrics['precision'] * 100:.2f}%")
m3.metric("Recall", f"{metrics['recall'] * 100:.2f}%")
m4.metric("F1-Score", f"{metrics['f1_score'] * 100:.2f}%")
m5.metric("ROC-AUC", f"{metrics['roc_auc']:.4f}")

st.markdown("---")

col_cm, col_roc = st.columns(2)

with col_cm:
    st.subheader("Confusion Matrix (Held-out Test Set)")
    cm = metrics["confusion_matrix"]
    cm_df = pd.DataFrame(
        cm,
        index=["Actual Non-Converter (0)", "Actual Converted (1)"],
        columns=["Predicted Non-Converter (0)", "Predicted Converted (1)"],
    )
    fig_cm = px.imshow(
        cm_df,
        text_auto=True,
        color_continuous_scale="Blues",
        title=f"Test Set Confusion Matrix (N = {metrics['test_size']})",
    )
    fig_cm.update_layout(height=350)
    st.plotly_chart(fig_cm, use_container_width=True)

with col_roc:
    st.subheader("Receiver Operating Characteristic (ROC Curve)")
    roc_data = metrics.get("roc_curve", {})
    if roc_data:
        fpr = roc_data["fpr"]
        tpr = roc_data["tpr"]
        fig_roc = go.Figure()
        fig_roc.add_trace(go.Scatter(x=fpr, y=tpr, mode="lines+markers", name=f"Logistic Regression (AUC = {metrics['roc_auc']:.3f})", line=dict(color="#1f77b4", width=3)))
        fig_roc.add_trace(go.Scatter(x=[0, 1], y=[0, 1], mode="lines", name="Random Guess (AUC = 0.50)", line=dict(dash="dash", color="gray")))
        fig_roc.update_layout(
            xaxis_title="False Positive Rate",
            yaxis_title="True Positive Rate",
            height=350,
            margin=dict(l=20, r=20, t=30, b=20),
        )
        st.plotly_chart(fig_roc, use_container_width=True)

st.markdown("---")
st.subheader("Top Predictive Signals (Logistic Regression Coefficients)")

coefs = metrics.get("feature_coefficients", {})
if coefs:
    coef_df = pd.DataFrame(list(coefs.items())[:12], columns=["Feature", "Coefficient"])
    fig_coef = px.bar(
        coef_df.sort_values(by="Coefficient", ascending=True),
        y="Feature",
        x="Coefficient",
        orientation="h",
        color="Coefficient",
        color_continuous_scale="RdBu_r",
        text_auto=".3f",
        title="Impact of Features on Log-Odds of Lead Conversion"
    )
    fig_coef.update_layout(height=400)
    st.plotly_chart(fig_coef, use_container_width=True)

st.markdown("---")
st.subheader("Live Lead Conversion Probability Predictor")

data = load_all_dashboard_data()
leads_df = data["leads"]
selected_lead = st.selectbox("Select Lead to Predict Conversion Probability", leads_df["id"].values[:50])

if selected_lead:
    model_path = ML_DIR / "logistic_regression_model.joblib"
    scaler_path = ML_DIR / "scaler.joblib"
    features_path = ML_DIR / "feature_names.joblib"

    if model_path.exists() and scaler_path.exists():
        model = joblib.load(model_path)
        scaler = joblib.load(scaler_path)
        feature_names = joblib.load(features_path)

        db = SessionLocal()
        try:
            lead = db.query(Lead).filter(Lead.id == selected_lead).first()
            company = db.query(Company).filter(Company.id == lead.company_id).first()
            contact = db.query(Contact).filter(Contact.id == lead.contact_id).first()
            activities = db.query(Activity).filter(Activity.lead_id == lead.id).all()

            valid_acts = [a for a in activities if not a.is_post_conversion]

            raw_dict = {
                "fit_score": lead.fit_score,
                "intent_score": lead.intent_score,
                "engagement_score": lead.engagement_score,
                "employee_count": company.employee_count if company else 50,
                "annual_revenue": company.annual_revenue if company else 1000000.0,
                "is_enterprise": 1 if company and company.tier == "Enterprise" else 0,
                "is_executive": 1 if contact and contact.seniority_level in {"C-Level", "VP"} else 0,
                "activity_count": len(valid_acts),
                "territory": lead.territory,
                "product_interest": lead.product_interest,
                "lead_source": lead.lead_source,
                "industry": company.industry if company else "Technology",
            }

            input_df = pd.DataFrame([raw_dict])
            encoded_df = pd.get_dummies(input_df, columns=["territory", "product_interest", "lead_source", "industry"])

            final_vector = pd.DataFrame(0, index=[0], columns=feature_names)
            for col in encoded_df.columns:
                if col in final_vector.columns:
                    final_vector[col] = encoded_df[col].iloc[0]

            scaled_vec = scaler.transform(final_vector)
            prob = float(model.predict_proba(scaled_vec)[0][1])

            cp1, cp2, cp3 = st.columns(3)
            cp1.metric("Rule-Based Lead Score", f"{lead.lead_score:.1f} / 100", f"Priority: {lead.priority}")
            cp2.metric("ML Conversion Probability", f"{prob * 100:.1f}%")
            cp3.metric("Predicted Outcome", "Will Convert ✅" if prob >= 0.5 else "Unlikely to Convert ❌")
        finally:
            db.close()
