from pathlib import Path

import streamlit as st

st.write("# Incident Reports")

SUMMARY_DIR = Path("incident-summaries")
REPORTS_DIR = Path("incident-reports")

for incident_summary in sorted(SUMMARY_DIR.glob("*.md"), reverse=True):
    incident_report = REPORTS_DIR / incident_summary.name
    with st.container():
        st.write(f"## {incident_summary.stem}")
        st.write(incident_summary.read_text())
        with st.expander("Full Report"):
            st.write(incident_report.read_text())
