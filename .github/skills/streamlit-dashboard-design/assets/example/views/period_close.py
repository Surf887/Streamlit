"""Page type: CHECKLIST AND CLOSE. Confirm readiness, then take one irreversible action.
Anatomy: header -> banner if blocked -> readiness checklist (wide) + the action (narrow)."""
import streamlit as st

import sample_data as data
import ui_kit as ui

items = data.close_checklist()
blocking = [i for i in items if i["status"] == "critical"]
period = f"{data.DATA_DATE:%B %Y}"

ui.page_header("Period close", eyebrow="Reporting",
               subtitle="Check the month is complete, then save the month-end snapshot",
               meta={"Period": f"{data.DATA_DATE:%b %Y}"},
               status=(f"{len(blocking)} blocking", "critical") if blocking else ("Ready to close", "good"))

if blocking:
    ui.banner(f"{period} cannot be closed yet.",
              f"{len(blocking)} item must be resolved first: {blocking[0]['label'].lower()}.", "critical")


@st.dialog("Close this period?")
def confirm_close():
    ui.key_value({"Period": period, "Forecast at completion": "$1,286.0M"})
    ui.banner("This cannot be undone.",
              "The snapshot becomes the comparison point for next month.", "warning")
    cancel, ok = st.columns(2)
    if cancel.button("Cancel", width="stretch"):
        st.rerun()
    if ok.button("Close period", type="primary", width="stretch"):
        st.session_state.closed = True
        st.rerun()


check_col, action_col = st.columns([5, 3])
with check_col:
    with ui.card("Readiness", f"{sum(i['status'] == 'good' for i in items)} of {len(items)} complete"):
        ui.checklist(items)
with action_col:
    with ui.card(f"Close {period}", "Saves the month-end snapshot", height=None):
        ui.key_value({"Forecast at completion": "$1,286.0M", "Change vs last close": "+$9.4M",
                      "Last closed period": "Sep 2026", "Closed by": "R. Mehta"})
        if st.button("Close period", type="primary", disabled=bool(blocking), width="stretch"):
            confirm_close()
    with ui.card("Export", "Excel copy of the current period", height=None):
        st.download_button("Download monthly report", data=b"", file_name="monthly_report.xlsx",
                           icon=":material/download:", width="stretch")
