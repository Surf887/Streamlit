"""Page type: FORM. Set up something once, in clearly grouped sections.
Anatomy: header -> two columns: form cards (wide) + read-only summary (narrow) -> one primary action."""
import streamlit as st

import sample_data as data
import ui_kit as ui

ui.page_header("Project setup", eyebrow="Baselines",
               subtitle="Identity, funding and key dates used by every other page")

form_col, side_col = st.columns([5, 3])

with form_col, st.form("project_setup", border=False):
    with ui.card("Identity", "How the project is named in reports"):
        a, b = st.columns(2)
        a.text_input("Project name", data.PROJECT)
        b.text_input("Project code", "KGP-2025")
        a.selectbox("Phase", ["Define", "Execute", "Close-out"], index=1)
        b.selectbox("Reporting currency", ["USD", "EUR", "GBP"])
    with ui.card("Funding and contingency", "Approved amounts, $M"):
        a, b, c = st.columns(3)
        a.number_input("Approved budget", value=1240.0, step=1.0, format="%.1f")
        b.number_input("Contingency", value=110.0, step=1.0, format="%.1f")
        c.number_input("Escalation allowance", value=36.0, step=1.0, format="%.1f")
    with ui.card("Key dates", "Baseline dates for the main gates"):
        a, b, c = st.columns(3)
        a.date_input("Funding approval", data.DATA_DATE - 22 * data.MONTH)
        b.date_input("Mechanical completion", data.DATA_DATE + 9 * data.MONTH)
        c.date_input("Ready for start-up", data.DATA_DATE + 12 * data.MONTH)
    _, save = st.columns([6, 2])
    saved = save.form_submit_button("Save changes", type="primary", width="stretch")

with side_col:
    with ui.card("Current baseline", "What the rest of the app is using", height=None):
        ui.key_value({
            "Approved budget": "$1,240.0M", "Contingency": "$110.0M",
            "Baseline set": "12 Jan 2025", "Last changed": "03 Oct 2026",
            "Changed by": "R. Mehta", "Status": ("Not yet approved", "warning"),
        })
    ui.banner("Changes apply from the open period.",
              "Closed periods keep the values they were closed with.", "info")

if saved:
    st.toast("Project setup saved")
