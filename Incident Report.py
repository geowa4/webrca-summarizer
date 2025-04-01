"""Streamlit application to manage reports."""

from os import getenv

import streamlit as st

from settings import REPORTS_DIR, SUMMARY_DIR
from reports import gen_reports
from summaries import summarize_reports

st.write("# Incident Reports")

with st.spinner("Generating reports and summaries"):
    gen_reports(REPORTS_DIR, getenv("OCM_TOKEN"))
    summarize_reports(REPORTS_DIR, SUMMARY_DIR)

if st.button("Regenerate"):
    import shutil
    shutil.rmtree(REPORTS_DIR)
    shutil.rmtree(SUMMARY_DIR)
    st.rerun()

for incident_summary in sorted(SUMMARY_DIR.glob("*.md"), reverse=True):
    incident_report = REPORTS_DIR / incident_summary.name
    with st.container():
        st.write(f"## {incident_summary.stem}")
        st.write(incident_summary.read_text())
        with st.expander("Full Report"):
            st.write(incident_report.read_text())
