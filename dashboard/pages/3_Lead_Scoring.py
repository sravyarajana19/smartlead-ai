import sys
from pathlib import Path
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from dashboard.components.data_loader import load_all_dashboard_data
from backend.services.scoring_service import LeadScoringEngine

st.set_page_config(page_title="Lead Scoring Engine - SMARTLEAD AI", page_icon="🎯", layout="wide")
st.title("🎯 Lead Scoring Engine & Explanations")

data = load_all_dashboard_data()
leads_df = data["leads"]

st.markdown("""
SmartLead AI scores leads using a transparent, multi-factor framework:
- **Company Fit (40%)**: Firmographics, employee scale, revenue tier, industry alignment.
- **Buying Intent (35%)**: High-intent behaviors (Demo requests, pricing views, whitepapers).
- **Engagement Depth (25%)**: Recency, frequency, multi-channel touchpoint activity.
""")

# Component Averages Row
c1, c2, c3, c4 = st.columns(4)
c1.metric("Average Company Fit", f"{leads_df['fit_score'].mean():.1f} / 100")
c2.metric("Average Buying Intent", f"{leads_df['intent_score'].mean():.1f} / 100")
c3.metric("Average Engagement", f"{leads_df['engagement_score'].mean():.1f} / 100")
c4.metric("Average Total Lead Score", f"{leads_df['lead_score'].mean():.1f} / 100")

st.markdown("---")

col_left, col_right = st.columns([6, 4])

with col_left:
    st.subheader("Component Score Distributions")
    comp_melted = leads_df.melt(
        id_vars=["id", "priority"],
        value_vars=["fit_score", "intent_score", "engagement_score", "lead_score"],
        var_name="Component",
        value_name="Score"
    )
    fig_box = px.box(
        comp_melted,
        x="Component",
        y="Score",
        color="Component",
        title="Score Spread Across Dimensions",
    )
    fig_box.update_layout(height=350, showlegend=False)
    st.plotly_chart(fig_box, use_container_width=True)

with col_right:
    st.subheader("Interactive Weight Simulator")
    w_fit = st.slider("Fit Weight", 0.0, 1.0, 0.40, 0.05)
    w_intent = st.slider("Intent Weight", 0.0, 1.0, 0.35, 0.05)
    w_eng = st.slider("Engagement Weight", 0.0, 1.0, 0.25, 0.05)

    total_w = w_fit + w_intent + w_eng
    if abs(total_w - 1.0) > 0.01:
        st.error(f"Weights must sum to 1.0. Current sum: {total_w:.2f}")
    else:
        # Simulate re-scoring
        sim_scores = (leads_df["fit_score"] * w_fit) + (leads_df["intent_score"] * w_intent) + (leads_df["engagement_score"] * w_eng)
        sim_high = (sim_scores >= 80).sum()
        sim_med = ((sim_scores >= 50) & (sim_scores < 80)).sum()
        sim_low = (sim_scores < 50).sum()

        st.success("Simulation Calculated:")
        st.write(f"- **High Priority Leads (>=80)**: {sim_high:,}")
        st.write(f"- **Medium Priority Leads (50-79.9)**: {sim_med:,}")
        st.write(f"- **Low Priority Leads (<50)**: {sim_low:,}")

# Lead Specific Deep Dive
st.markdown("---")
st.subheader("Individual Lead Score Explainability")
selected_lead = st.selectbox("Select Lead to Explain", leads_df["id"].values[:50])

if selected_lead:
    lead = leads_df[leads_df["id"] == selected_lead].iloc[0]
    fit_s = lead["fit_score"]
    int_s = lead["intent_score"]
    eng_s = lead["engagement_score"]
    tot_s = lead["lead_score"]

    col_e1, col_e2 = st.columns([5, 5])
    with col_e1:
        fig_bar = go.Figure(go.Bar(
            x=[fit_s * 0.4, int_s * 0.35, eng_s * 0.25],
            y=["Company Fit (40%)", "Buying Intent (35%)", "Engagement (25%)"],
            orientation="h",
            marker=dict(color=["#1f77b4", "#ff7f0e", "#2ca02c"]),
            text=[f"{fit_s*0.4:.1f} pts", f"{int_s*0.35:.1f} pts", f"{eng_s*0.25:.1f} pts"],
            textposition="auto",
        ))
        fig_bar.update_layout(title="Weighted Contribution to Total Score", height=250, margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_e2:
        st.markdown(f"### Total Lead Score: **{tot_s:.1f}**")
        st.markdown(f"### Classification: **{lead['priority']} Priority**")
        st.markdown(f"""
        - **Company Fit Raw Score**: `{fit_s:.1f} / 100` (Contributes `+{fit_s*0.4:.1f}` pts)
        - **Buying Intent Raw Score**: `{int_s:.1f} / 100` (Contributes `+{int_s*0.35:.1f}` pts)
        - **Engagement Depth Raw Score**: `{eng_s:.1f} / 100` (Contributes `+{eng_s*0.25:.1f}` pts)
        """)
