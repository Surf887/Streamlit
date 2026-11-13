"""Page type: WORKSPACE. Edit many rows of one thing, with totals always in view.
Anatomy: header -> filters -> stat strip (totals) -> editable grid in a card -> save action."""
import streamlit as st

import sample_data as data
import ui_kit as ui

ui.page_header("Cost workspace", eyebrow="Monthly updates",
               subtitle="Set this period's forecast for each cost activity",
               meta={"Period": f"{data.DATA_DATE:%b %Y}"}, status=("12 of 14 updated", "info"))

f1, f2, f3, _ = st.columns([2, 3, 2, 3], vertical_alignment="center")
area = f1.selectbox("Area", ["All areas"] + data.AREAS, label_visibility="collapsed")
query = f2.text_input("Search", placeholder="Search activities", label_visibility="collapsed")
only_var = f3.toggle("Only variances")

df = data.cost_activities()
if area != "All areas":
    df = df[df["Area"] == area]
if query:
    df = df[df["Activity"].str.contains(query, case=False)]
if only_var:
    df = df[df["Variance"].abs() >= 0.5]

t = df[["Budget", "Actual", "Committed", "Forecast", "Variance"]].sum()
ui.stat_strip([
    dict(label="Current budget", value=f"${t['Budget']:,.1f}M"),
    dict(label="Actual to date", value=f"${t['Actual']:,.1f}M",
         note=f"{t['Actual'] / max(t['Budget'], 1e-9):.0%} of budget"),
    dict(label="Committed", value=f"${t['Committed']:,.1f}M"),
    dict(label="Forecast at completion", value=f"${t['Forecast']:,.1f}M"),
    dict(label="Variance", value=ui.signed(t["Variance"], "${:,.1f}M"),
         note="over budget" if t["Variance"] > 0 else "under budget",
         tone="bad" if t["Variance"] > 0 else "good"),
])

with ui.card("Cost activities", "$M. Forecast and comment are editable; everything else is calculated.",
             height=None):
    if df.empty:
        ui.empty_state("No activities match these filters", "Clear the search or choose another area.")
    else:
        edited = ui.editor(
            df, key="cost_grid", editable=["Forecast", "Comment"], height=420,
            columns={
                "Area": ui.col_text("Area", width="medium"),
                "Activity": ui.col_text("Activity", width="medium"),
                "Budget": ui.col_number("Budget", decimals=1),
                "Actual": ui.col_number("Actual", decimals=1),
                "Committed": ui.col_number("Committed", decimals=1),
                "Forecast": ui.col_number("Forecast", decimals=1),
                "Variance": ui.col_number("Variance", decimals=1, signed=True),
                "Progress": ui.col_progress("Progress"),
                "Comment": ui.col_text("Period comment", width="large"),
            })

with ui.card("Monthly phasing", "Actual and forecast cost by month against plan, $M", height=None):
    ui.show(ui.monthly_bars(data.phasing(), x="month", actual="actual", forecast="forecast",
                            planned="planned", prefix="$", suffix="M", height=260))

note, save = st.columns([6, 1.4], vertical_alignment="center")
note.caption("Changes are kept in this session until you save.")
if save.button("Save forecast", type="primary", width="stretch"):
    st.toast("Forecast saved for Oct 2026")
