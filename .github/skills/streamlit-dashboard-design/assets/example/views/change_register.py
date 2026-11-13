"""Page type: REGISTER. A list of records with status, and the detail of the one selected.
Anatomy: header -> stat strip -> filters -> table (wide) + selected record (narrow) -> related chart."""
import streamlit as st

import sample_data as data
import ui_kit as ui

ui.page_header("Change register", eyebrow="Forecast and change",
               subtitle="Every request that could move the budget or the forecast",
               meta={"Period": f"{data.DATA_DATE:%b %Y}"})

df = data.changes()
by = df.groupby("Status")["Value"].agg(["count", "sum"])
get = lambda s: (int(by["count"].get(s, 0)), float(by["sum"].get(s, 0.0)))
ui.stat_strip([
    dict(label=s, value=f"${get(s)[1]:,.1f}M", note=f"{get(s)[0]} request{'' if get(s)[0] == 1 else 's'}")
    for s in ["Approved", "Pending", "In dispute", "Rejected"]
])

f1, f2, _ = st.columns([4, 2, 4], vertical_alignment="center")
status = f1.pills("Status", ["Approved", "Pending", "In dispute", "Rejected"],
                  selection_mode="multi", label_visibility="collapsed")
area = f2.selectbox("Area", ["All areas"] + data.AREAS, label_visibility="collapsed")
view = df[df["Status"].isin(status)] if status else df
view = view[view["Area"] == area] if area != "All areas" else view

table_col, detail_col = st.columns([5, 3])
with table_col:
    with ui.card("Requests", "Select a row to see its detail"):
        if view.empty:
            ui.empty_state("No requests match these filters")
            picked = None
        else:
            sel = ui.grid(view, key="changes", on_select="rerun", selection_mode="single-row",
                          column_order=["ID", "Change", "Status", "Value", "Raised"],
                          columns={"Value": ui.col_number("Value, $M", decimals=1),
                                   "Raised": st.column_config.DateColumn("Raised", format="DD MMM YYYY")})
            rows = sel.selection.rows
            picked = view.iloc[rows[0]] if rows else view.iloc[0]
with detail_col:
    with ui.card("Selected request", status=None):
        if picked is None:
            ui.empty_state("Nothing selected")
        else:
            ui.key_value({
                "ID": picked["ID"], "Status": (picked["Status"], data.CHANGE_STATUS[picked["Status"]]),
                "Change": picked["Change"], "Area": picked["Area"],
                "Value": f"${picked['Value']:,.1f}M", "Raised": f"{picked['Raised']:%d %b %Y}",
            })
            ui.banner("Status is recorded here for tracking.", "It is not a formal approval.", "neutral")

with ui.card("Contingency drawdown", "Remaining contingency against the planned curve, $M", height=None):
    ui.show(ui.rundown(data.contingency(), x="month", planned="planned", actual="actual",
                       data_date=data.DATA_DATE, prefix="$", suffix="M", height=260))
