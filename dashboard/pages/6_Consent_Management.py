import sys
from pathlib import Path
import streamlit as st
import plotly.express as px
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from dashboard.components.data_loader import load_all_dashboard_data
from backend.services.consent_service import ConsentEnforcementService

st.set_page_config(page_title="Consent Management - SMARTLEAD AI", page_icon="🛡️", layout="wide")
st.title("🛡️ Marketing Consent & Privacy Enforcement")

data = load_all_dashboard_data()
consents_df = data["consents"]
leads_df = data["leads"]

st.markdown("""
> [!IMPORTANT]
> **Core Privacy Compliance Rule**: An opted-out contact **MUST NEVER** receive follow-up contact tasks. 
> High lead scoring can **never** override explicit opt-outs.
""")

opt_in_count = len(consents_df[consents_df["consent_status"] == "Opt-In"])
opt_out_count = len(consents_df[consents_df["consent_status"] == "Opt-Out"])
pending_count = len(consents_df[consents_df["consent_status"] == "Pending"])

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Consent Records", f"{len(consents_df):,}")
c2.metric("Active Opt-In", f"{opt_in_count:,}", f"{opt_in_count/len(consents_df)*100:.1f}%")
c3.metric("Opt-Out (Outreach Blocked)", f"{opt_out_count:,}", f"{opt_out_count/len(consents_df)*100:.1f}%", delta_color="inverse")
c4.metric("Pending Verification", f"{pending_count:,}")

st.markdown("---")

col1, col2 = st.columns([5, 5])
with col1:
    fig_c = px.pie(
        consents_df,
        names="consent_status",
        title="Marketing Consent Breakdown",
        color="consent_status",
        color_discrete_map={"Opt-In": "#2ca02c", "Opt-Out": "#d62728", "Pending": "#ff7f0e"},
        hole=0.45,
    )
    fig_c.update_layout(height=320)
    st.plotly_chart(fig_c, use_container_width=True)

with col2:
    st.subheader("Live Consent Verification Simulator")
    test_lead = st.selectbox("Select Lead ID to Verify Outreach Clearance", leads_df["id"].values[:50])
    
    if test_lead:
        c_record = consents_df[consents_df["lead_id"] == test_lead]
        if not c_record.empty:
            c_dict = c_record.iloc[0].to_dict()
            lead_row = leads_df[leads_df["id"] == test_lead].iloc[0]
            permitted, reason = ConsentEnforcementService.verify_consent_for_outreach(test_lead, c_dict, lead_score=lead_row["lead_score"])

            if permitted:
                st.success(f"✅ OUTREACH PERMITTED: Status is {c_dict['consent_status']}. Follow-up tasks allowed.")
            else:
                st.error(f"🚫 OUTREACH FORBIDDEN: {reason}")
        else:
            st.warning("No consent record found for this lead.")

st.markdown("---")
st.subheader("Opt-Out Audit Trail & Blocked Records")
opt_outs = consents_df[consents_df["consent_status"] == "Opt-Out"]
st.dataframe(
    opt_outs[["id", "lead_id", "contact_id", "consent_status", "opt_out_timestamp", "channel", "notes"]],
    use_container_width=True,
    height=300,
)
