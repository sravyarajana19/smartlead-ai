import sys
from pathlib import Path
import streamlit as st
import plotly.express as px
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from dashboard.components.data_loader import load_all_dashboard_data

st.set_page_config(page_title="Company & Contact Management - SMARTLEAD AI", page_icon="🏢", layout="wide")
st.title("🏢 Company & Contact Management")

data = load_all_dashboard_data()
companies_df = data["companies"]
contacts_df = data["contacts"]

tab1, tab2 = st.tabs(["🏢 Companies", "👤 Contacts"])

with tab1:
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Companies", f"{len(companies_df):,}")
    c2.metric("Enterprise Tier (>=1k emp)", f"{len(companies_df[companies_df['tier'] == 'Enterprise']):,}")
    c3.metric("Average Revenue", f"${companies_df['annual_revenue'].mean():,.0f}")

    col_c1, col_c2 = st.columns(2)
    with col_c1:
        fig_ind = px.pie(companies_df, names="industry", title="Industry Breakdown", hole=0.4)
        fig_ind.update_layout(height=320)
        st.plotly_chart(fig_ind, use_container_width=True)

    with col_c2:
        fig_tier = px.bar(companies_df.groupby("tier").size().reset_index(name="Count"), x="tier", y="Count", color="tier", text_auto=True, title="Companies by Tier")
        fig_tier.update_layout(height=320, showlegend=False)
        st.plotly_chart(fig_tier, use_container_width=True)

    st.subheader("Company Directory")
    comp_search = st.text_input("Filter Companies by Name or Domain", "")
    comp_filtered = companies_df
    if comp_search:
        comp_filtered = comp_filtered[comp_filtered["name"].str.contains(comp_search, case=False) | comp_filtered["domain"].str.contains(comp_search, case=False)]

    st.dataframe(
        comp_filtered[["id", "name", "domain", "industry", "tier", "employee_count", "annual_revenue", "territory", "country"]],
        use_container_width=True,
        height=350,
    )

with tab2:
    p1, p2, p3 = st.columns(3)
    p1.metric("Total Contacts", f"{len(contacts_df):,}")
    p2.metric("Executive Decision Makers", f"{len(contacts_df[contacts_df['seniority_level'].isin(['C-Level', 'VP'])]):,}")
    p3.metric("Primary Account Contacts", f"{len(contacts_df[contacts_df['is_primary'] == 1]):,}")

    col_p1, col_p2 = st.columns(2)
    with col_p1:
        fig_sen = px.pie(contacts_df, names="seniority_level", title="Seniority Level Distribution", hole=0.4)
        fig_sen.update_layout(height=320)
        st.plotly_chart(fig_sen, use_container_width=True)

    with col_p2:
        fig_dept = px.bar(contacts_df.groupby("department").size().reset_index(name="Count"), x="department", y="Count", color="department", text_auto=True, title="Contacts by Department")
        fig_dept.update_layout(height=320, showlegend=False)
        st.plotly_chart(fig_dept, use_container_width=True)

    st.subheader("Contact Directory")
    st.dataframe(
        contacts_df[["id", "company_id", "first_name", "last_name", "email", "normalized_phone", "job_title", "seniority_level", "department", "is_primary"]],
        use_container_width=True,
        height=350,
    )
