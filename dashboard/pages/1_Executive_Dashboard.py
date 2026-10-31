import sys
from pathlib import Path
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from dashboard.components.data_loader import load_all_dashboard_data

st.set_page_config(page_title="Executive Dashboard - SMARTLEAD AI", page_icon="📊", layout="wide")
st.title("📊 Executive Dashboard")

data = load_all_dashboard_data()
leads_df = data["leads"]
opps_df = data["opportunities"]

total_leads = len(leads_df)
high_priority = len(leads_df[leads_df["priority"] == "High"])
qualified_leads = len(leads_df[leads_df["status"].isin(["Qualified", "Converted"])])
total_opps = len(opps_df)
won_opps = len(opps_df[opps_df["current_stage"] == "Won"])
conversion_rate = (won_opps / total_opps * 100) if total_opps > 0 else 0.0
won_rev = opps_df[opps_df["current_stage"] == "Won"]["opportunity_value"].sum()
pipeline_rev = opps_df["opportunity_value"].sum()

# Top KPI Metrics Row
c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("Total Leads", f"{total_leads:,}")
c2.metric("High Priority", f"{high_priority:,}", f"{high_priority/total_leads*100:.1f}%")
c3.metric("Qualified Leads", f"{qualified_leads:,}")
c4.metric("Opportunities", f"{total_opps:,}")
c5.metric("Won Opportunities", f"{won_opps:,}", f"{conversion_rate:.1f}% Win Rate")
c6.metric("Won Revenue", f"${won_rev:,.0f}", f"of ${pipeline_rev:,.0f}")

st.markdown("---")

# Charts Row 1: Funnel & Priority Distribution
col_left, col_right = st.columns([6, 4])

with col_left:
    st.subheader("Sales Conversion Funnel")
    funnel_stages = ["Total Leads", "Qualified Leads", "Opportunities", "Won Deals"]
    funnel_values = [total_leads, qualified_leads, total_opps, won_opps]
    
    fig_funnel = go.Figure(go.Funnel(
        y=funnel_stages,
        x=funnel_values,
        textinfo="value+percent initial",
        marker={"color": ["#1f77b4", "#33a02c", "#ff7f0e", "#2ca02c"]}
    ))
    fig_funnel.update_layout(margin=dict(l=20, r=20, t=20, b=20), height=350)
    st.plotly_chart(fig_funnel, use_container_width=True)

with col_right:
    st.subheader("Lead Priority Breakdown")
    fig_pie = px.pie(
        leads_df,
        names="priority",
        title="Priority Distribution (Score-Based)",
        color="priority",
        color_discrete_map={"High": "#2ca02c", "Medium": "#ff7f0e", "Low": "#d62728"},
        hole=0.45,
    )
    fig_pie.update_layout(margin=dict(l=20, r=20, t=40, b=20), height=350)
    st.plotly_chart(fig_pie, use_container_width=True)

# Charts Row 2: Territory Breakdown & Monthly Trends
col_t1, col_t2 = st.columns(2)

with col_t1:
    st.subheader("Leads & Opportunities by Territory")
    terr_summary = leads_df.groupby("territory").size().reset_index(name="Lead Count")
    fig_terr = px.bar(
        terr_summary,
        x="territory",
        y="Lead Count",
        color="territory",
        text_auto=True,
    )
    fig_terr.update_layout(showlegend=False, height=350)
    st.plotly_chart(fig_terr, use_container_width=True)

with col_t2:
    st.subheader("Pipeline Stage Distribution")
    stage_summary = opps_df.groupby("current_stage")["opportunity_value"].agg(["count", "sum"]).reset_index()
    stage_summary.columns = ["Stage", "Count", "Value"]
    fig_stage = px.bar(
        stage_summary,
        x="Stage",
        y="Value",
        color="Stage",
        text_auto="$,.0f",
        title="Pipeline Value by Current Stage"
    )
    fig_stage.update_layout(showlegend=False, height=350)
    st.plotly_chart(fig_stage, use_container_width=True)
