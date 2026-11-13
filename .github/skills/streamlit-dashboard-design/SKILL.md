---
name: streamlit-dashboard-design
description: Design system for building polished, professional Streamlit dashboards, especially project controls dashboards (cost, schedule, earned value, progress, change, risk). Use whenever creating, extending or restyling a Streamlit app or page, adding KPI cards, charts, tables, status indicators or layouts, or when asked to make a Streamlit app look better, modern, professional or "less like default Streamlit". Provides a theme with bundled fonts, a ui_kit Python package (page header, KPI cards, cards, status pills, progress bars, Plotly chart recipes) and layout rules.
---

# Streamlit dashboard design

Default Streamlit apps look generic because each page is improvised from raw
`st.title`, `st.metric` and `st.bar_chart` calls with default fonts, spacing and
colours. Good dashboard design is mostly consistency: one type scale, one spacing
rhythm, one colour system, the same card everywhere.

This skill removes the improvisation. It ships a small design system — a theme, a
bundled font and a `ui_kit` package — and your job is to **compose pages from the
kit**, not to style anything by hand. Page code should contain no HTML, no CSS, no
hex colours and no font sizes.

Preview of the result: `assets/example/preview-light.png` and `preview-dark.png`.

## Workflow

### 1. Install the kit (once per project)

If the project has no `ui_kit/` folder, run from the project root:

```
python .github/skills/streamlit-dashboard-design/scripts/install.py
```

It copies `ui_kit/`, `.streamlit/config.toml` and `static/InterVariable.woff2` into
the project and never overwrites existing files. If a `config.toml` already exists,
merge the `[server]`, `[client]`, `[[theme.fontFaces]]` and `[theme*]` sections in
by hand. Dependencies: `streamlit` (1.46 or newer, written for 1.67), `plotly`,
`pandas`.

### 2. Read the reference page

Read `assets/example/app.py` before writing any page. It is the pattern to imitate:
about 80 lines, every visual element comes from `ui_kit`. `sample_data.py` beside it
is synthetic and shows the expected shape of the data layer.

### 3. Plan the page before coding

Write the plan as a comment block at the top of the page file:

- The one question this page answers ("Are we on budget and on schedule?").
- Four to six KPIs that answer it at a glance.
- One main chart (the trend) and one breakdown beside it.
- Up to four supporting charts that explain *why*.
- The detail table behind the numbers.

For which KPIs and charts suit which project controls question, read
`references/project-controls-patterns.md`.

### 4. Build

- Keep data separate from UI: plain functions returning DataFrames or dicts,
  already scaled to display units (pass `1240.0` meaning $M, not `1240000000`).
  Cache loaders with `@st.cache_data`.
- First line of every page: `ui.setup_page("Title")`.
- Follow the page anatomy below, top to bottom.

### 5. Run and check

Run `streamlit run <page>.py`, fix every error and console warning, then go through
the checklist at the end of this file. If you can take a screenshot, compare it with
the preview images.

## Page anatomy

Every page uses the same six bands, in this order. Skip a band rather than reorder.

| Band | Built with | Notes |
|---|---|---|
| 1. Header | `ui.page_header` | Title, one-line subtitle, data date in `meta`, overall status pill |
| 2. Filters | `st.columns` + native widgets | One row, labels collapsed, directly under the header |
| 3. KPI row | `ui.kpi_row` | 4–6 cards. One row only |
| 4. Main row | `st.columns([5, 3])` + `ui.card` | Trend chart wide, breakdown narrow |
| 5. Supporting rows | `st.columns(2)` + `ui.card` | Two cards per row, three at most |
| 6. Detail | `ui.card` + `ui.status_table` or `st.dataframe` | Full width |

More than about two screens of content means the page is doing too much: split it
with `st.navigation` pages or `st.tabs` (Overview, Cost, Schedule, Change, Risk).

## ui_kit reference

`import ui_kit as ui`

| Call | Use for |
|---|---|
| `ui.setup_page(title)` | First line of each page: wide layout and design-system CSS |
| `ui.page_header(title, eyebrow=, subtitle=, meta={}, status=(label, status))` | Band 1 |
| `ui.section(title, caption)` | Optional heading above a group of rows |
| `ui.kpi_row([dict(label, value, delta=, tone=, note=, status=, spark=)])` | Band 3 |
| `with ui.card(title, caption):` | The surface for every chart and table |
| `ui.show(fig)` | The only way to render a Plotly figure |
| `ui.s_curve(df, x=, planned=, earned=, actual=, forecast=, data_date=)` | Cumulative plan vs earned vs actual |
| `ui.bridge(steps)` | How one total becomes another (budget to forecast) |
| `ui.variance_bars(df, category=, value=)` | Signed variance by category |
| `ui.index_trend(df, x=, series={"CPI": "cpi"})` | Ratios against a reference line |
| `ui.milestone_slip(df, name=, baseline=, forecast=)` | Baseline vs forecast dates |
| `ui.progress_list(rows)` | Percent complete with a planned marker |
| `ui.status_table(rows, columns, status_col=, right=[])` | Small table with status pills |
| `ui.pill(label, status)` | Status: `good`, `warning`, `critical`, `info`, `neutral` |
| `ui.empty_state(title, hint)` | Instead of an empty chart when a filter returns nothing |
| `ui.style(fig)` | Apply the design system to a custom Plotly figure |
| `ui.money`, `ui.pct`, `ui.signed` | Number formatting |
| `ui.tokens()` | Colours for the active light or dark mode |

Docstrings in `ui_kit/components.py` and `ui_kit/charts.py` give every parameter.

## Rules

**Use the kit, not raw Streamlit, for display.** These each have a kit replacement
because the raw version breaks the type scale, spacing or colour system:

| Do not use in pages | Use instead |
|---|---|
| `st.title`, `st.header`, `st.subheader` | `ui.page_header`, `ui.section`, card titles |
| `st.metric` | `ui.kpi_row` |
| `st.markdown(..., unsafe_allow_html=True)`, `st.html` | A `ui_kit` component (add one if missing) |
| `st.line_chart`, `st.bar_chart`, `st.plotly_chart` | A chart recipe, or `ui.style(fig)` then `ui.show(fig)` |
| `st.success` / `st.warning` / `st.error` for status | `ui.pill` or a `status=` argument |
| `st.divider` between sections | Nothing: cards and spacing already separate content |

Native widgets are fine and already themed: `st.columns`, `st.tabs`,
`st.navigation`, `st.sidebar`, `st.selectbox`, `st.segmented_control`,
`st.date_input`, `st.dataframe`. Put `st.dataframe` inside a `ui.card`, with
`hide_index=True` and `column_config` number formats.

**Colour carries meaning, so spend it carefully.**
- Neutral by default. Most of the page is ink on white; colour appears in data and status only.
- Series colours come from `ui.tokens()["series"]` in order. A series keeps its
  colour on every page and under every filter. More than six series: group the tail
  as "Other" or use a table.
- Status colours (green, amber, red) mean status and nothing else, and always come
  with an icon and a word. Never colour a KPI value itself.
- `tone` on a delta is a judgement, not a sign: cost up is `"bad"`, progress up is
  `"good"`. Decide it from the metric's meaning.
- Plan and baseline are grey context lines. Only forecasts are dashed.

**Charts**
- One y-axis per chart. Two measures with different units go in two charts.
- No pie or donut charts, no 3D, no gauges. Ranked bars or a KPI card say it better.
- Titles and units live in the card title and caption, not inside the figure.
- Pre-scale values and pass `prefix`/`suffix` (`"$"`, `"M"`), so axes read `$800M`.
- Chart height 290–350 px; cards in one row share a height.
- An empty result shows `ui.empty_state`, never a blank chart or a traceback.

**Numbers**
- Every number goes through `ui.money`, `ui.pct`, `ui.signed` or an explicit format.
- KPI values show three significant figures (`$1.29B`, `54.0%`, `0.95`).
- Deltas always carry a sign and a unit, and say what they compare with:
  `+3.7%` "vs $1.24B budget". Percentage-point gaps are `pts`, not `%`.
- Dates read `31 Oct 2026`. State the data date in the header.

**Words**
- Sentence case everywhere. No emoji in titles, labels or tabs.
- Card title names the thing ("Cost S-curve"); caption gives unit or definition
  ("Cumulative, $M"). Spell out an abbreviation once, in the label or caption.
- KPI labels are two to four words. Notes under the value are a short phrase.

## When the kit lacks something

Add it to `ui_kit` as a reusable component or chart recipe, then call it from the
page. Do not write one-off HTML or CSS in a page: that is how a dashboard drifts back
to looking improvised. `references/design-system.md` has the tokens, the type scale,
the component pattern and the constraints of `st.html` (inline `<svg>` and scripts
are stripped). Read it before adding or changing anything in `ui_kit`, and before
changing brand colours or fonts.

## Checklist before finishing

- [ ] `ui.setup_page(...)` is the first Streamlit call on the page.
- [ ] Page file has no HTML, CSS, hex colour, `unsafe_allow_html` or font size.
- [ ] No `st.title`/`st.header`/`st.metric`/`st.plotly_chart`/`st.divider` in pages.
- [ ] Bands appear in anatomy order; KPI row has 4–6 cards; at most 3 cards per row.
- [ ] Every chart and table sits in a `ui.card` with a title and a caption giving the unit.
- [ ] Every figure is rendered with `ui.show`.
- [ ] Every delta has a sign, a unit, a comparison note and a deliberate `tone`.
- [ ] Status is shown with a pill (icon and word), never colour alone.
- [ ] Filters that can return no rows are handled with `ui.empty_state`.
- [ ] App runs with no exceptions and no Streamlit warnings in the terminal.
