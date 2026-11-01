import sys
from pathlib import Path
import streamlit as st
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from backend.core.database import SessionLocal, ensure_database_initialized
from backend.services.validation_service import ValidationEngine

ensure_database_initialized()

st.set_page_config(page_title="Data Quality & Validation - SMARTLEAD AI", page_icon="✅", layout="wide")
st.title("✅ Automated Data Quality & Validation Engine")

st.markdown("""
The Validation Engine runs continuous automated health audits across 14 enterprise data integrity dimensions.
It strictly distinguishes **deliberately labelled anomalies** from unexpected database corruption.
""")

if st.button("🚀 Execute Comprehensive System Audit"):
    db = SessionLocal()
    try:
        engine = ValidationEngine(db)
        results = engine.run_all_checks()
        st.session_state["validation_results"] = results
    finally:
        db.close()

# Load cached or newly run results
if "validation_results" not in st.session_state:
    db = SessionLocal()
    try:
        engine = ValidationEngine(db)
        st.session_state["validation_results"] = engine.run_all_checks()
    finally:
        db.close()

results = st.session_state["validation_results"]

# High Level Metrics Row
v1, v2, v3, v4, v5 = st.columns(5)
v1.metric("Total Records Audited", f"{results['total_records_checked']:,}")
v2.metric("Passed Checks", f"{results['passed_checks']}")
v3.metric("Failed Checks", f"{results['failed_checks']}")
v4.metric("Labelled Anomalies", f"{results['detected_anomalies']}")
status_text = results["validation_status"]
if status_text == "ALL_PASSED":
    v5.success(status_text)
elif "ANOMALIES" in status_text:
    v5.info(status_text)
else:
    v5.error(status_text)

st.markdown("---")
st.subheader("14-Point Validation Checklist Results")

details_df = pd.DataFrame(results["check_details"])
if not details_df.empty:
    st.dataframe(details_df, use_container_width=True, height=450)
else:
    st.write("No check details recorded.")
