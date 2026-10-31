import sys
from pathlib import Path
import streamlit as st
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from dashboard.components.data_loader import load_all_dashboard_data

st.set_page_config(page_title="Lead Explorer - SMARTLEAD AI", page_icon="🔍", layout="wide")
st.title("🔍 Lead Explorer")

data = load_all_dashboard_data()
leads_df = data["leads"]
companies_df = data["companies"]
contacts_df = data["contacts"]
consents_df = data["consents"]
reps_df = data["sales_reps"]

# Merge relevant metadata for unified explorer view
merged = leads_df.merge(companies_df[["id", "name", "domain", "industry"]], left_on="company_id", right_on="id", suffixes=("", "_comp"))
merged = merged.merge(contacts_df[["id", "first_name", "last_name", "email", "job_title", "seniority_level"]], left_on="contact_id", right_on="id", suffixes=("", "_con"))
merged = merged.merge(consents_df[["lead_id", "consent_status"]], left_on="id", right_on="lead_id", suffixes=("", "_cns"), how="left")
merged = merged.merge(reps_df[["id", "name"]], left_on="assigned_rep_id", right_on="id", suffixes=("", "_rep"), how="left")

# Filters Sidebar
st.sidebar.header("Filter Criteria")
search = st.sidebar.text_input("Search (Company, Contact, Email, ID)", "")

priority_filter = st.sidebar.multiselect("Priority", ["High", "Medium", "Low"], default=["High", "Medium", "Low"])
territory_filter = st.sidebar.multiselect("Territory", merged["territory"].unique(), default=list(merged["territory"].unique()))
source_filter = st.sidebar.multiselect("Lead Source", merged["lead_source"].unique(), default=list(merged["lead_source"].unique()))
consent_filter = st.sidebar.multiselect("Consent Status", ["Opt-In", "Opt-Out", "Pending"], default=["Opt-In", "Opt-Out", "Pending"])
score_range = st.sidebar.slider("Lead Score Range", 0.0, 100.0, (0.0, 100.0))

# Apply filters
filtered = merged[
    (merged["priority"].isin(priority_filter)) &
    (merged["territory"].isin(territory_filter)) &
    (merged["lead_source"].isin(source_filter)) &
    (merged["consent_status"].fillna("Pending").isin(consent_filter)) &
    (merged["lead_score"] >= score_range[0]) &
    (merged["lead_score"] <= score_range[1])
]

if search:
    s = search.lower()
    filtered = filtered[
        (filtered["id"].str.lower().str.contains(s)) |
        (filtered["name"].str.lower().str.contains(s)) |
        (filtered["email"].str.lower().str.contains(s)) |
        (filtered["first_name"].str.lower().str.contains(s)) |
        (filtered["last_name"].str.lower().str.contains(s))
    ]

st.markdown(f"**Showing {len(filtered):,} matching leads** (out of {len(merged):,} total)")

# Display Table
display_cols = [
    "id", "name", "first_name", "last_name", "email",
    "territory", "product_interest", "lead_source",
    "lead_score", "priority", "status", "consent_status", "name_rep"
]
col_rename = {
    "id": "Lead ID",
    "name": "Company",
    "first_name": "First Name",
    "last_name": "Last Name",
    "email": "Email",
    "territory": "Territory",
    "product_interest": "Product",
    "lead_source": "Source",
    "lead_score": "Score",
    "priority": "Priority",
    "status": "Status",
    "consent_status": "Consent",
    "name_rep": "Assigned Rep",
}

st.dataframe(
    filtered[display_cols].rename(columns=col_rename),
    use_container_width=True,
    height=450,
)

# Inspection Section
st.markdown("---")
st.subheader("Lead Record Deep Dive")
selected_lead_id = st.selectbox("Select Lead ID to Inspect", filtered["id"].values[:50] if len(filtered) > 0 else [])

if selected_lead_id:
    row = filtered[filtered["id"] == selected_lead_id].iloc[0]
    ci1, ci2, ci3 = st.columns(3)
    with ci1:
        st.markdown(f"**Company**: {row['name']} ({row['domain']})")
        st.markdown(f"**Industry**: {row['industry']}")
        st.markdown(f"**Territory**: {row['territory']}")
    with ci2:
        st.markdown(f"**Contact**: {row['first_name']} {row['last_name']}")
        st.markdown(f"**Title**: {row['job_title']} ({row['seniority_level']})")
        st.markdown(f"**Email**: {row['email']}")
    with ci3:
        st.markdown(f"**Lead Score**: `{row['lead_score']}` ({row['priority']})")
        st.markdown(f"**Status**: `{row['status']}`")
        st.markdown(f"**Consent**: `{row['consent_status']}`")
        st.markdown(f"**Assigned Rep**: `{row['name_rep']}`")
