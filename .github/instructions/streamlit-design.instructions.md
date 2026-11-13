---
applyTo: "**/*.py"
description: Streamlit UI in this repository follows the dashboard design system
---

Before creating or changing any Streamlit page, layout, form, table, KPI card or chart in
this repository, read `.github/skills/streamlit-dashboard-design/SKILL.md` and follow
it. In short:

- Build pages only from the `ui_kit` package (`import ui_kit as ui`). If `ui_kit/`
  is missing, run `python .github/skills/streamlit-dashboard-design/scripts/install.py`.
- Every page is one of the skill's page types (dashboard, workspace, form, stepped
  task, register, checklist and close, reference); see
  `.github/skills/streamlit-dashboard-design/references/page-types.md`.
- Page files contain no HTML, CSS, hex colours or font sizes, and do not use
  `st.title`, `st.header`, `st.metric`, `st.plotly_chart`, `st.dataframe`,
  `st.data_editor`, `st.warning` or `st.divider`.
- Page files live in `views/`, never `pages/`; `ui.setup_page` is called once in `app.py`.
- Use `.github/skills/streamlit-dashboard-design/assets/example/` as the pattern.
- If a component is missing, add it to `ui_kit` following
  `.github/skills/streamlit-dashboard-design/references/design-system.md`.
