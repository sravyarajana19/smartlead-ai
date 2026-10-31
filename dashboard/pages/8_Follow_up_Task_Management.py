import sys
from pathlib import Path
import streamlit as st
import plotly.express as px
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from dashboard.components.data_loader import load_all_dashboard_data
from backend.services.task_service import TaskManagementService

st.set_page_config(page_title="Task Management - SMARTLEAD AI", page_icon="📝", layout="wide")
st.title("📝 Follow-up Task Management")

data = load_all_dashboard_data()
tasks_df = data["tasks"]
leads_df = data["leads"]
consents_df = data["consents"]

t1, t2, t3, t4 = st.columns(4)
t1.metric("Total Follow-up Tasks", f"{len(tasks_df):,}")
urgent_tasks = len(tasks_df[tasks_df["priority"] == "Urgent"])
pending_tasks = len(tasks_df[tasks_df["status"] == "Pending"])
completed_tasks = len(tasks_df[tasks_df["status"] == "Completed"])

t2.metric("Urgent SLA Tasks", f"{urgent_tasks:,}")
t3.metric("Pending Tasks", f"{pending_tasks:,}")
t4.metric("Completed Tasks", f"{completed_tasks:,}")

st.markdown("---")

col1, col2 = st.columns([5, 5])
with col1:
    fig_pri = px.pie(tasks_df, names="priority", title="Tasks by SLA Priority", hole=0.4, color="priority",
                     color_discrete_map={"Urgent": "#d62728", "High": "#ff7f0e", "Normal": "#1f77b4"})
    fig_pri.update_layout(height=320)
    st.plotly_chart(fig_pri, use_container_width=True)

with col2:
    fig_type = px.bar(tasks_df.groupby("task_type").size().reset_index(name="Count"), x="task_type", y="Count", color="task_type", text_auto=True, title="Tasks by Action Type")
    fig_type.update_layout(height=320, showlegend=False)
    st.plotly_chart(fig_type, use_container_width=True)

st.markdown("---")
st.subheader("Follow-up Task Queue")

status_filter = st.multiselect("Filter by Status", tasks_df["status"].unique(), default=list(tasks_df["status"].unique()))
pri_filter = st.multiselect("Filter by Priority", tasks_df["priority"].unique(), default=list(tasks_df["priority"].unique()))

filtered_tasks = tasks_df[(tasks_df["status"].isin(status_filter)) & (tasks_df["priority"].isin(pri_filter))]

st.dataframe(
    filtered_tasks[["id", "lead_id", "assigned_rep_id", "task_type", "priority", "due_date", "status", "is_consent_verified", "blocked_reason"]],
    use_container_width=True,
    height=350,
)
