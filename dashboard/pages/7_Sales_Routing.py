import sys
from pathlib import Path
import streamlit as st
import plotly.express as px
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from dashboard.components.data_loader import load_all_dashboard_data
from backend.services.routing_service import SalesRoutingEngine
from backend.core.config import VALID_TERRITORIES, VALID_PRODUCTS

st.set_page_config(page_title="Sales Routing - SMARTLEAD AI", page_icon="🧭", layout="wide")
st.title("🧭 Deterministic Sales Routing Engine")

data = load_all_dashboard_data()
reps_df = data["sales_reps"]

st.markdown("""
SmartLead AI deterministically routes leads to sales representatives matching:
1. **Territory match**
2. **Product specialization**
3. **Active representative status**
4. **Available capacity** (`current_load < capacity`)
""")

r1, r2, r3, r4 = st.columns(4)
r1.metric("Total Sales Representatives", f"{len(reps_df):,}")
r2.metric("Active Reps", f"{len(reps_df[reps_df['is_active'] == 1]):,}")
r3.metric("Total Capacity (Leads)", f"{reps_df['capacity'].sum():,}")
r4.metric("Current Assigned Load", f"{reps_df['current_load'].sum():,}")

st.markdown("---")

col1, col2 = st.columns([6, 4])

with col1:
    st.subheader("Sales Representative Capacity Utilization")
    reps_df["utilization_pct"] = (reps_df["current_load"] / reps_df["capacity"] * 100).round(1)
    fig_load = px.bar(
        reps_df.sort_values(by="utilization_pct", ascending=True),
        y="name",
        x="utilization_pct",
        orientation="h",
        color="territory",
        text="utilization_pct",
        title="Rep Workload (% of Max Capacity)",
    )
    fig_load.update_layout(height=400)
    st.plotly_chart(fig_load, use_container_width=True)

with col2:
    st.subheader("Interactive Routing Simulator")
    sim_terr = st.selectbox("Lead Territory", VALID_TERRITORIES)
    sim_prod = st.selectbox("Product Interest", VALID_PRODUCTS)

    if st.button("Simulate Deterministic Lead Routing"):
        rep_dicts = reps_df.to_dict(orient="records")
        chosen_rep, status, expl = SalesRoutingEngine.route_lead(sim_terr, sim_prod, rep_dicts)

        if chosen_rep:
            st.success(f"**Status**: `{status}`")
            st.markdown(f"**Assigned Representative**: **{chosen_rep['name']}** (`{chosen_rep['id']}`)")
            st.markdown(f"**Rep Territory**: {chosen_rep['territory']} | **Specialization**: {chosen_rep['product_specialization']}")
            st.markdown(f"**Current Load**: {chosen_rep['current_load']} / {chosen_rep['capacity']} ({chosen_rep['current_load']/chosen_rep['capacity']*100:.1f}%)")
            st.info(f"**Routing Logic**: {expl}")
        else:
            st.error(f"**Status**: `{status}` - {expl}")

st.markdown("---")
st.subheader("Sales Representative Roster")
st.dataframe(
    reps_df[["id", "name", "email", "territory", "product_specialization", "is_active", "capacity", "current_load", "utilization_pct"]],
    use_container_width=True,
    height=300,
)
