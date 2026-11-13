"""Page type: DASHBOARD. One question: are we on budget and on schedule?
Anatomy: header -> filters -> KPI row -> main trend + breakdown -> supporting charts -> detail."""
import streamlit as st

import sample_data as data
import ui_kit as ui

s = data.summary()

# --- 1. Header: what am I looking at, as of when, and is it OK? -----------------
ui.page_header(
    "Kestrel Gas Plant Expansion",
    eyebrow="Project controls",
    subtitle="Execute phase · EPC lump sum with reimbursable construction",
    meta={"Data date": f"{data.DATA_DATE:%d %b %Y}", "Reporting period": "Oct 2026"},
    status=("At risk", "warning"),
)

# --- 2. Filters: one row, directly under the header ------------------------------
f1, f2, _ = st.columns([2, 2, 6], vertical_alignment="center")
view = f1.segmented_control("View", ["Cost", "Hours"], default="Cost", label_visibility="collapsed")
area = f2.selectbox("Area", ["All areas", "Process units", "Utilities & offsites", "Pipelines"],
                    label_visibility="collapsed")

# --- 3. KPI row: the 4-6 numbers that answer "how are we doing?" -----------------
hist, trend = data.index_history(), data.kpi_history()
ui.kpi_row([
    dict(label="Forecast at completion", value=ui.money(s["eac"] * 1e6),
         delta=ui.signed((s["eac"] / s["budget"] - 1) * 100, suffix="%"), tone="bad",
         note=f"vs {ui.money(s['budget'] * 1e6)} budget", spark=trend["eac"]),
    dict(label="Progress", value=ui.pct(s["pct_complete"]),
         delta=ui.signed((s["pct_complete"] - s["pct_planned"]) * 100, suffix=" pts"), tone="bad",
         note=f"vs {ui.pct(s['pct_planned'])} planned", spark=trend["progress"]),
    dict(label="Cost index (CPI)", value=f"{s['cpi']:.2f}", status=("Watch", "warning"),
         note="target 1.00", spark=hist["cpi"].tolist()),
    dict(label="Schedule index (SPI)", value=f"{s['spi']:.2f}", status=("Behind", "critical"),
         note="target 1.00", spark=hist["spi"].tolist()),
    dict(label="Contingency remaining", value=ui.money(s["contingency_left"] * 1e6),
         note=f"{ui.pct(s['contingency_left'] / s['contingency_total'], decimals=0)} of "
              f"{ui.money(s['contingency_total'] * 1e6, decimals=0)}", spark=trend["contingency"]),
])

# --- 4. Main row: the trend (wide) + the breakdown (narrow) ----------------------
left, right = st.columns([5, 3])
with left:
    with ui.card("Cost S-curve", "Cumulative, $M"):
        ui.show(ui.s_curve(data.s_curve(), x="month", planned="planned", earned="earned",
                           actual="actual", forecast="forecast", data_date=data.DATA_DATE,
                           prefix="$", suffix="M", height=350))
with right:
    with ui.card("Progress by discipline", "Percent complete against plan"):
        ui.progress_list(data.discipline_progress())

# --- 5. Supporting row: why is the number what it is? ----------------------------
c1, c2 = st.columns(2)
with c1:
    with ui.card("Budget to forecast", "What moved the forecast at completion, $M"):
        ui.show(ui.bridge(data.eac_bridge(), prefix="$", suffix="M", height=300))
with c2:
    with ui.card("Forecast variance by area", "Forecast minus budget, $M"):
        ui.show(ui.variance_bars(data.area_variance(), category="area", value="variance",
                                 prefix="$", suffix="M", height=300))

c3, c4 = st.columns(2)
with c3:
    with ui.card("Performance indices", "Cumulative cost (CPI) and schedule (SPI) performance index"):
        ui.show(ui.index_trend(hist, x="month", series={"CPI": "cpi", "SPI": "spi"}, height=290))
with c4:
    with ui.card("Key milestones", "Baseline against current forecast"):
        ui.show(ui.milestone_slip(data.milestones(), name="milestone", baseline="baseline",
                                  forecast="forecast", height=290))

# --- 6. Detail: the rows behind the numbers --------------------------------------
with ui.card("Recent change requests", "Largest open and recently decided"):
    rows = [dict(r, value=f"${r['value']:.1f}M") for r in data.change_log()]
    ui.status_table(rows, {"id": "ID", "title": "Change", "area": "Area",
                           "status": "Status", "value": "Value"},
                    status_col="status", right=["value"])
