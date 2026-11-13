"""Entry file: app shell. Sets up the page once, defines the sidebar navigation in
workflow order, shows the working context, then runs the selected page.

Run with:  streamlit run app.py
Pages contain no HTML, CSS, colours or font sizes - everything visual comes from ui_kit.
"""
import streamlit as st

import sample_data as data
import ui_kit as ui

ui.setup_page("Project controls")

# Sidebar groups follow the monthly cycle, top to bottom. Icons are Material Symbols
# (":material/name:"), never emoji. One icon style across the whole app.
# Page files live in views/, not pages/: a folder named pages/ switches on Streamlit's
# older automatic multi-page mode, which can load a page without this shell.
page = st.navigation({
    "Baselines": [
        st.Page("views/project_setup.py", title="Project setup", icon=":material/tune:"),
    ],
    "Monthly updates": [
        st.Page("views/import_actuals.py", title="Import actuals", icon=":material/upload_file:"),
        st.Page("views/cost_workspace.py", title="Cost workspace", icon=":material/table_rows:"),
    ],
    "Performance": [
        st.Page("views/highlights.py", title="Highlights", icon=":material/monitoring:", default=True),
    ],
    "Forecast and change": [
        st.Page("views/change_register.py", title="Change register", icon=":material/swap_horiz:"),
    ],
    "Reporting": [
        st.Page("views/period_close.py", title="Period close", icon=":material/task_alt:"),
    ],
})

ui.sidebar_context("Project controls", {
    "Project": data.PROJECT,
    "Period": f"{data.DATA_DATE:%B %Y}",
    "Status": ("Open for updates", "info"),
})

page.run()
