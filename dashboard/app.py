import sys
from pathlib import Path
import streamlit as st

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dashboard.components.data_loader import load_all_dashboard_data

st.set_page_config(
    page_title="SMARTLEAD AI - Operations Platform",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("⚡ SMARTLEAD AI")
st.subheader("Intelligent Lead Scoring and Sales Operations Platform")

st.markdown("""
Welcome to **SMARTLEAD AI**, an end-to-end forward deployed operational platform designed to automate lead scoring, 
enforce regulatory marketing consent, route opportunities to sales representatives deterministically, 
and provide comprehensive machine learning evaluation with continuous exception monitoring.
""")

try:
    data = load_all_dashboard_data()
    leads_df = data["leads"]
    opps_df = data["opportunities"]
    anom_df = data["anomalies"]

    total_leads = len(leads_df)
    high_leads = len(leads_df[leads_df["priority"] == "High"])
    total_opps = len(opps_df)
    won_opps = len(opps_df[opps_df["current_stage"] == "Won"])
    won_revenue = opps_df[opps_df["current_stage"] == "Won"]["opportunity_value"].sum()
    anomalies_count = len(anom_df)

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total Leads", f"{total_leads:,}")
    col2.metric("High Priority Leads", f"{high_leads:,}", f"{high_leads/total_leads*100:.1f}%")
    col3.metric("Opportunities Created", f"{total_opps:,}")
    col4.metric("Won Deals", f"{won_opps:,}", f"${won_revenue:,.0f}")
    col5.metric("Detected Anomalies", f"{anomalies_count:,}", "Cases 1-5")

except Exception as e:
    st.warning(f"Database currently initializing or loading: {e}")

st.markdown("---")
st.markdown("### 📋 Platform Navigation Guide")

col_a, col_b, col_c = st.columns(3)
with col_a:
    st.markdown("""
    **Core Sales Intelligence**
    - **1. Executive Dashboard**: KPI cards, conversion funnel, revenue trends.
    - **2. Lead Explorer**: Multi-dimensional search & filtering.
    - **3. Lead Scoring**: 40/35/25 component explanation & weight simulation.
    - **4. Company & Contacts**: Firmographics & buyer personas.
    """)
with col_b:
    st.markdown("""
    **Operations & Execution**
    - **5. Campaign & Activity**: Marketing touchpoints & channel analytics.
    - **6. Consent Management**: Opt-out enforcement & privacy compliance.
    - **7. Sales Routing**: Territory & specialization matching.
    - **8. Follow-up Tasks**: Prioritized SLAs & consent verification.
    """)
with col_c:
    st.markdown("""
    **Governance & AI Evaluation**
    - **9. Opportunity Pipeline**: Stage progression & won/lost reasons.
    - **10. Exception Monitoring**: Audit log for Cases 1 through 5.
    - **11. Data Quality & Validation**: Automated 14-point database integrity audit.
    - **12. ML Evaluation**: Scikit-learn Logistic Regression benchmarks & live inference.
    """)

st.info("👈 Select any page from the sidebar to explore live operational capabilities.")
