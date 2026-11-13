# Streamlit dashboard design skill for GitHub Copilot

A design system Copilot can follow so Streamlit dashboards — especially project
controls dashboards (cost, schedule, earned value, change, risk) — come out
consistent and polished instead of default-looking.

![Sample dashboard built with the kit](.github/skills/streamlit-dashboard-design/assets/example/preview-light.png)

## What is here

```
.github/
  skills/streamlit-dashboard-design/
    SKILL.md                     the instructions Copilot loads
    references/                  design tokens; project controls patterns
    scripts/install.py           copies the kit into a project
    assets/
      ui_kit/                    components + Plotly chart recipes (Python)
      streamlit/config.toml      theme (fonts, colours, light + dark)
      static/InterVariable.woff2 bundled font (SIL Open Font License)
      example/                   reference page with made-up data + previews
  instructions/
    streamlit-design.instructions.md   fallback pointer for Copilot
```

All sample data is synthetic.

## Set up

Use it in this repository, or copy the whole `.github/` folder to the root of the
repository that holds your Streamlit app. Then, from that repository's root:

1. Install the kit:
   `python .github/skills/streamlit-dashboard-design/scripts/install.py`
   This adds `ui_kit/`, `.streamlit/config.toml` and `static/` to the project and
   never overwrites existing files.
2. See the reference dashboard: copy `app.py` and `sample_data.py` from
   `.github/skills/streamlit-dashboard-design/assets/example/` to the repository
   root, then run `streamlit run app.py`.
3. Requirements: `streamlit` 1.46 or newer (built on 1.67), `plotly`, `pandas`.

## Use it in Copilot

Use Copilot Chat in **Agent** mode. The skill loads on its own when you ask for
Streamlit UI work; naming it removes any doubt:

> Use the streamlit-dashboard-design skill. Build a Cost page for the project
> controls dashboard from `data/cost.py`. Plan the page first, then build it.

To restyle an existing page:

> Use the streamlit-dashboard-design skill to rebuild `pages/overview.py` with
> `ui_kit`. Keep the data logic unchanged and run the checklist at the end.

If agent skills are switched off in your organisation, the file in
`.github/instructions/` still points Copilot to the same guidance whenever it edits
Python files.

## Make it yours

- Brand colour, fonts, series colours: see
  `.github/skills/streamlit-dashboard-design/references/design-system.md` ("Rebranding").
- Status thresholds and KPI definitions:
  `.github/skills/streamlit-dashboard-design/references/project-controls-patterns.md`
  lists common defaults; edit them to match your project's rules.
