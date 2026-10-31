import sys
from pathlib import Path
import streamlit as st
import plotly.express as px
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from dashboard.components.data_loader import load_all_dashboard_data

st.set_page_config(page_title="Campaign & Activity Analytics - SMARTLEAD AI", page_icon="📈", layout="wide")
st.title("📈 Campaign & Activity Analytics")

data = load_all_dashboard_data()
campaigns_df = data["campaigns"]
activities_df = data["activities"]

tab1, tab2 = st.tabs(["📢 Marketing Campaigns", "⚡ Touchpoint Activities"])

with tab1:
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Campaigns", f"{len(campaigns_df):,}")
    m2.metric("Active Campaigns", f"{len(campaigns_df[campaigns_df['status'] == 'Active']):,}")
    m3.metric("Total Marketing Budget", f"${campaigns_df['budget'].sum():,.0f}")

    col1, col2 = st.columns(2)
    with col1:
        fig_type = px.pie(campaigns_df, names="campaign_type", title="Campaigns by Type", hole=0.4)
        fig_type.update_layout(height=320)
        st.plotly_chart(fig_type, use_container_width=True)

    with col2:
        fig_chan = px.bar(campaigns_df.groupby("channel")["budget"].sum().reset_index(), x="channel", y="budget", color="channel", text_auto="$,.0f", title="Marketing Budget by Channel")
        fig_chan.update_layout(height=320, showlegend=False)
        st.plotly_chart(fig_chan, use_container_width=True)

    st.subheader("Campaign Details")
    st.dataframe(
        campaigns_df[["id", "name", "campaign_type", "channel", "budget", "target_territory", "target_product", "status", "start_date", "end_date"]],
        use_container_width=True,
        height=300,
    )

with tab2:
    a1, a2, a3 = st.columns(3)
    a1.metric("Total Tracked Activities", f"{len(activities_df):,}")
    demo_requests = len(activities_df[activities_df["activity_type"] == "Demo Request"])
    pricing_views = len(activities_df[activities_df["activity_type"] == "Pricing View"])
    a2.metric("High-Intent Demo Requests", f"{demo_requests:,}")
    a3.metric("Pricing Page Views", f"{pricing_views:,}")

    col_a1, col_a2 = st.columns(2)
    with col_a1:
        act_summary = activities_df.groupby("activity_type").size().reset_index(name="Count").sort_values(by="Count", ascending=True)
        fig_acts = px.bar(act_summary, y="activity_type", x="Count", orientation="h", color="activity_type", text_auto=True, title="Activity Volume by Interaction Type")
        fig_acts.update_layout(height=350, showlegend=False)
        st.plotly_chart(fig_acts, use_container_width=True)

    with col_a2:
        fig_ch = px.pie(activities_df, names="channel", title="Activity Volume by Channel", hole=0.4)
        fig_ch.update_layout(height=350)
        st.plotly_chart(fig_ch, use_container_width=True)

    st.subheader("Activity Event Log")
    st.dataframe(
        activities_df[["id", "lead_id", "activity_type", "channel", "intent_weight", "engagement_weight", "activity_date", "is_post_conversion"]].head(200),
        use_container_width=True,
        height=300,
    )
