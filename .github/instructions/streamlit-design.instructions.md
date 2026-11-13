---
applyTo: "**/*.py"
description: Streamlit UI in this repository follows the dashboard design system
---

Before creating or changing any Streamlit page, layout, KPI card, chart or table in
this repository, read `.github/skills/streamlit-dashboard-design/SKILL.md` and follow
it. In short:

- Build pages only from the `ui_kit` package (`import ui_kit as ui`). If `ui_kit/`
  is missing, run `python .github/skills/streamlit-dashboard-design/scripts/install.py`.
- Page files contain no HTML, CSS, hex colours or font sizes, and do not use
  `st.title`, `st.header`, `st.metric`, `st.plotly_chart` or `st.divider`.
- Use `.github/skills/streamlit-dashboard-design/assets/example/app.py` as the pattern.
- If a component is missing, add it to `ui_kit` following
  `.github/skills/streamlit-dashboard-design/references/design-system.md`.
