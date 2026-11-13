"""Page type: STEPPED TASK. A multi-step job with a clear end: upload, map, review, apply.
Anatomy: header -> stepper -> one card for the current step -> Back / Next actions."""
import streamlit as st

import sample_data as data
import ui_kit as ui

STEPS = ["Upload", "Map columns", "Review", "Apply"]
step = st.session_state.setdefault("import_step", 2)      # the example opens on Review

ui.page_header("Import actuals", eyebrow="Monthly updates",
               subtitle="Bring in actual costs and commitments for the open period",
               meta={"Period": f"{data.DATA_DATE:%b %Y}", "Last import": "02 Nov 2026"})
ui.stepper(STEPS, step)

if step == 0:
    with ui.card("Upload the extract", "Excel or CSV, one row per posting"):
        st.segmented_control("Source", ["Actuals", "Commitments"], default="Actuals")
        st.file_uploader("File", type=["xlsx", "csv"], label_visibility="collapsed")
elif step == 1:
    with ui.card("Map columns", "Match the file's columns to the fields the app needs"):
        ui.editor(data.column_mapping(), editable=["File column"], key="mapping",
                  columns={"Required": st.column_config.CheckboxColumn("Required")})
elif step == 2:
    r = data.import_review()
    ui.stat_strip([
        dict(label="Rows read", value=f"{r['rows']:,}"),
        dict(label="Matched to activities", value=f"{r['matched']:,}", note="98.6% of rows", tone="good"),
        dict(label="Unmatched", value=f"{r['unmatched']:,}", note="needs a decision", tone="warn"),
        dict(label="Value to apply", value="$41.8M", note="vs $39.2M last period"),
    ])
    with ui.card("Unmatched rows", "These postings have no activity yet. Assign one or leave them out."):
        ui.editor(data.unmatched_rows(), editable=["Assign to activity"], key="unmatched",
                  columns={"Amount": ui.col_money("Amount, $M", decimals=2)})
    ui.banner("Nothing is saved yet.", "Applying the import adds these costs to the open period.", "info")
else:
    with ui.card("Ready to apply", "Summary of what will change"):
        ui.key_value({"Rows to apply": "1,264", "Value": "$41.8M", "Period": "Oct 2026",
                      "Left out": "18 rows, $0.6M"}, columns=4)

back, _, nxt = st.columns([1, 6, 1.4])
if back.button("Back", disabled=step == 0, width="stretch"):
    st.session_state.import_step = step - 1
    st.rerun()
label = "Apply import" if step == len(STEPS) - 1 else "Next"
if nxt.button(label, type="primary", width="stretch"):
    st.session_state.import_step = min(step + 1, len(STEPS) - 1)
    st.rerun()
