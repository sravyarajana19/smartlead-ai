import sys
from pathlib import Path
import streamlit as st
import plotly.express as px
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from dashboard.components.data_loader import load_all_dashboard_data

st.set_page_config(page_title="Opportunity Pipeline - SMARTLEAD AI", page_icon="💼", layout="wide")
st.title("💼 Opportunity Pipeline & Lifecycle")

data = load_all_dashboard_data()
opps_df = data["opportunities"]
stage_hist_df = data["stage_histories"]

total_opps = len(opps_df)
won_opps = len(opps_df[opps_df["current_stage"] == "Won"])
lost_opps = len(opps_df[opps_df["current_stage"] == "Lost"])
open_opps = total_opps - won_opps - lost_opps
total_val = opps_df["opportunity_value"].sum()
won_val = opps_df[opps_df["current_stage"] == "Won"]["opportunity_value"].sum()

o1, o2, o3, o4 = st.columns(4)
o1.metric("Total Opportunities", f"{total_opps:,}")
o2.metric("Active Pipeline", f"{open_opps:,}", f"${opps_df[~opps_df['current_stage'].isin(['Won', 'Lost'])]['opportunity_value'].sum():,.0f}")
o3.metric("Won Deals", f"{won_opps:,}", f"${won_val:,.0f}")
o4.metric("Win Rate", f"{won_opps / (won_opps + lost_opps) * 100:.1f}%" if (won_opps + lost_opps) > 0 else "N/A")

st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Pipeline Stage Funnel")
    stage_order = ["New", "Qualified", "Proposal", "Negotiation", "Won", "Lost"]
    stage_counts = opps_df["current_stage"].value_counts().reindex(stage_order).fillna(0).reset_index()
    stage_counts.columns = ["Stage", "Count"]

    fig_stg = px.bar(stage_counts, x="Stage", y="Count", color="Stage", text_auto=True, title="Opportunities by Stage")
    fig_stg.update_layout(height=350, showlegend=False)
    st.plotly_chart(fig_stg, use_container_width=True)

with col2:
    st.subheader("Won / Lost Reason Analysis")
    reasons_df = opps_df[opps_df["won_lost_reason"].notna()]
    if not reasons_df.empty:
        fig_reas = px.bar(
            reasons_df.groupby(["current_stage", "won_lost_reason"]).size().reset_index(name="Deals"),
            x="Deals",
            y="won_lost_reason",
            color="current_stage",
            orientation="h",
            color_discrete_map={"Won": "#2ca02c", "Lost": "#d62728"},
            title="Reasons for Deal Win/Loss"
        )
        fig_reas.update_layout(height=350)
        st.plotly_chart(fig_reas, use_container_width=True)

st.markdown("---")
st.subheader("Opportunity Stage History Audit Trail")
selected_opp = st.selectbox("Select Opportunity to View Progression History", opps_df["id"].values[:50])

if selected_opp:
    opp_hist = stage_hist_df[stage_hist_df["opportunity_id"] == selected_opp].sort_values(by="transition_date")
    st.markdown(f"**Audit Trail for `{selected_opp}`** ({len(opp_hist)} Recorded Transitions):")
    st.dataframe(
        opp_hist[["id", "from_stage", "to_stage", "stage_duration_days", "transition_date", "is_valid_transition", "changed_by", "notes"]],
        use_container_width=True,
    )
