import sys
from pathlib import Path
import streamlit as st
import plotly.express as px
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from dashboard.components.data_loader import load_all_dashboard_data

st.set_page_config(page_title="Exception Monitoring - SMARTLEAD AI", page_icon="⚠️", layout="wide")
st.title("⚠️ Exception Monitoring & Audit Governance")

data = load_all_dashboard_data()
anom_df = data["anomalies"]

st.markdown("""
Continuous compliance surveillance engine monitoring all 5 mandatory business exception scenarios:
1. **CASE 1**: Opted-out lead contacted (Privacy & Consent Violation)
2. **CASE 2**: Lead score calculated with post-conversion touchpoint (Temporal Data Leakage)
3. **CASE 3**: Lead assigned to rep outside territory (Sales Routing Violation)
4. **CASE 4**: Duplicate lead generated duplicate opportunity (Pipeline Integrity Violation)
5. **CASE 5**: Stage history contains missing or skipped transitions (Lifecycle State Machine Violation)
""")

# Metrics row
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Detected Anomalies", f"{len(anom_df):,}")
critical_count = len(anom_df[anom_df["severity"] == "Critical"])
high_count = len(anom_df[anom_df["severity"] == "High"])
c2.metric("Critical Severity", f"{critical_count:,}", delta_color="inverse")
c3.metric("High Severity", f"{high_count:,}", delta_color="inverse")
c4.metric("Resolution Status", "Open / In Review")

st.markdown("---")

col1, col2 = st.columns([5, 5])
with col1:
    fig_case = px.bar(
        anom_df.groupby("issue_type").size().reset_index(name="Count"),
        x="Count",
        y="issue_type",
        orientation="h",
        color="issue_type",
        text_auto=True,
        title="Detected Incidents by Mandatory Case Type"
    )
    fig_case.update_layout(height=340, showlegend=False)
    st.plotly_chart(fig_case, use_container_width=True)

with col2:
    fig_sev = px.pie(
        anom_df,
        names="severity",
        title="Incident Severity Distribution",
        color="severity",
        color_discrete_map={"Critical": "#d62728", "High": "#ff7f0e", "Medium": "#1f77b4"},
        hole=0.45,
    )
    fig_sev.update_layout(height=340)
    st.plotly_chart(fig_sev, use_container_width=True)

st.markdown("---")
st.subheader("Exception Records & Audit Log")

case_filter = st.multiselect("Filter by Case Type", anom_df["issue_type"].unique(), default=list(anom_df["issue_type"].unique()))
filtered_anom = anom_df[anom_df["issue_type"].isin(case_filter)]

st.dataframe(
    filtered_anom[["id", "entity_type", "entity_id", "issue_type", "severity", "ground_truth_label", "expected_decision", "actual_decision", "explanation"]],
    use_container_width=True,
    height=400,
)
