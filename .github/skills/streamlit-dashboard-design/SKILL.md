---
name: streamlit-dashboard-design
description: Design system for building polished, professional Streamlit apps and dashboards, especially project controls tools (cost, schedule, earned value, forecast, change, risk, monthly reporting). Use whenever creating, extending or restyling a Streamlit app or page - dashboards, data-entry forms, editable grids, import steps, registers, checklists, sidebar navigation - or adding KPI cards, charts, tables or status indicators, or when asked to make a Streamlit app look better, modern, professional or "less like default Streamlit". Provides a theme with bundled fonts, a ui_kit Python package (app shell, page header, KPI cards, cards, banners, steppers, stat strips, checklists, tables, Plotly chart recipes) and page patterns.
---

# Streamlit app and dashboard design

Default Streamlit apps look generic because each page is improvised from raw
`st.title`, `st.metric`, `st.warning` and `st.bar_chart` calls with default fonts,
spacing and colours. Good application design is mostly consistency: one type scale,
one spacing rhythm, one colour system, the same card and the same page shapes
everywhere.

This skill removes the improvisation. It ships a small design system — a theme, a
bundled font and a `ui_kit` package — plus a fixed set of page types. Your job is to
**pick the page type and compose it from the kit**, not to style anything by hand.
Page code contains no HTML, no CSS, no hex colours and no font sizes.

Previews of the result are in `assets/example/` (`preview-*.png`).

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

If `ui_kit/` exists but is missing something listed in the reference below (for
example `ui.stat_strip`), it is an older copy: run the script again with `--update`
to refresh the `ui_kit/*.py` files.

### 2. Read the reference app

`assets/example/` is a small working app: `app.py` (the shell) and one file per page
type in `views/`. Before writing a page, read `app.py` and the example of the page
type you are about to build. `sample_data.py` is synthetic and shows the expected
shape of a data layer.

### 3. Choose the page type and plan

Every page is exactly one of the types below. Write the plan as a docstring at the
top of the page file: the page type, the one thing the user does or learns here, and
the bands top to bottom. For which type suits which project controls screen, and
which KPIs and charts to use, read `references/page-types.md` and
`references/project-controls-patterns.md`.

### 4. Build

- Keep data separate from UI: plain functions returning DataFrames or dicts, already
  scaled to display units (pass `1240.0` meaning $M, not `1240000000`). Cache
  read-only loaders with `@st.cache_data`.
- Compose the page from `ui_kit` in the band order of its type.

### 5. Run and check

Run `streamlit run app.py`, open every page you touched, fix every error and
terminal warning, then go through the checklist at the end of this file. If you can
take a screenshot, compare it with the preview images.

## App shell

One entry file (`app.py`) owns the frame; see `assets/example/app.py`.

1. `ui.setup_page("App name")` — the first Streamlit call, once, in the entry file
   only.
2. `page = st.navigation({...})` — sidebar groups in the order people work
   (set-up, then the recurring cycle, then review, then reporting). Group names are
   plain nouns. Each `st.Page` gets a short title and a Material Symbols icon
   (`":material/table_rows:"`); never emoji.
3. `ui.sidebar_context("App name", {...})` — app name and the working context
   (project, period, status) above the navigation.
4. `page.run()`.

Keep page files in `views/`, **not** `pages/`: a folder named `pages/` switches on
Streamlit's older automatic multi-page mode, which can load a page without the
shell and its styling. A single-file app just calls `ui.setup_page` at the top.

## Page types

| Type | The user… | Bands, top to bottom | Example |
|---|---|---|---|
| Dashboard | reads how things stand | header · filters · `kpi_row` · main chart + breakdown · supporting charts · detail table | `views/highlights.py` |
| Workspace | edits many rows of one thing | header · filters · `stat_strip` · `editor` in a card · optional chart · save | `views/cost_workspace.py` |
| Form | sets something up once | header · form cards (wide) + read-only summary (narrow) · save | `views/project_setup.py` |
| Stepped task | completes a multi-step job | header · `stepper` · one card for the current step · Back / Next | `views/import_actuals.py` |
| Register | tracks records and their status | header · `stat_strip` · filters · table (wide) + selected record (narrow) | `views/change_register.py` |
| Checklist and close | confirms readiness, then commits | header · `banner` if blocked · `checklist` (wide) + the action (narrow) | `views/period_close.py` |
| Reference | looks something up | header · search · text in cards, one topic each | — |

Skip a band rather than reorder. If a page needs two types, it is two pages.

## ui_kit reference

`import ui_kit as ui`. Docstrings in `ui_kit/components.py` and `ui_kit/charts.py`
give every parameter.

**Structure**

| Call | Use for |
|---|---|
| `ui.setup_page(title)` | Once, first, in the entry file |
| `ui.sidebar_context(app, {...})` | App name and context at the top of the sidebar |
| `ui.page_header(title, eyebrow=, subtitle=, meta={}, status=)` | Top of every page; `eyebrow` is the sidebar group |
| `with ui.card(title, caption):` | The surface for every chart, table, form section |
| `ui.section(title, caption)` | Optional heading above a group of rows |
| `ui.banner(title, detail, status)` | One page-level notice (caveat, blocked, not approved) |
| `ui.stepper(steps, current)` | Progress through a stepped task |
| `ui.empty_state(title, hint)` | Instead of an empty chart or table |

**Numbers and status**

| Call | Use for |
|---|---|
| `ui.kpi_row([dict(label, value, delta=, tone=, note=, status=, spark=)])` | Dashboard headline numbers, 4–6 |
| `ui.stat_strip([dict(label, value, note=, tone=)])` | Compact totals above a table or editor |
| `ui.pill(label, status)` | Status: `good`, `warning`, `critical`, `info`, `neutral` |
| `ui.checklist([dict(label, status, detail=, meta=)])` | Readiness list |
| `ui.key_value({...}, columns=2)` | Read-only facts; a `(label, status)` value shows a pill |
| `ui.progress_list(rows)` | Percent complete with a planned marker |
| `ui.money`, `ui.pct`, `ui.signed` | Number formatting in text |

**Tables**

| Call | Use for |
|---|---|
| `ui.editor(df, editable=[...], columns={...}, key=)` | Editable grid; unlisted columns are locked |
| `ui.grid(df, columns={...})` | Read-only table; add `on_select="rerun"` for row selection |
| `ui.status_table(rows, columns, status_col=, right=[])` | Small table (≤ 12 rows) with status pills |
| `ui.col_number`, `ui.col_money`, `ui.col_pct`, `ui.col_progress`, `ui.col_text` | Column formats for `editor` and `grid` |

**Charts** — render every figure with `ui.show(fig)`

| Call | Use for |
|---|---|
| `ui.s_curve(df, x=, planned=, earned=, actual=, forecast=, data_date=)` | Cumulative plan vs earned vs actual |
| `ui.monthly_bars(df, x=, actual=, forecast=, planned=)` | Per-period phasing |
| `ui.bridge(steps)` | How one total becomes another (budget to forecast, month to month) |
| `ui.variance_bars(df, category=, value=)` | Signed variance by category |
| `ui.index_trend(df, x=, series={"CPI": "cpi"})` | Ratios against a reference line |
| `ui.rundown(df, x=, planned=, actual=)` | A balance drawn down against its planned curve |
| `ui.milestone_slip(df, name=, baseline=, forecast=)` | Baseline vs forecast dates |
| `ui.style(fig)` | Apply the design system to a custom Plotly figure |

## Rules

**Use the kit, not raw Streamlit, for display.** These each have a kit replacement
because the raw version breaks the type scale, spacing or colour system:

| Do not use in pages | Use instead |
|---|---|
| `st.title`, `st.header`, `st.subheader` | `ui.page_header`, `ui.section`, card titles |
| `st.metric` | `ui.kpi_row`, `ui.stat_strip` |
| `st.markdown(..., unsafe_allow_html=True)`, `st.html` | A `ui_kit` component (add one if missing) |
| `st.line_chart`, `st.bar_chart`, `st.plotly_chart` | A chart recipe, or `ui.style(fig)` then `ui.show(fig)` |
| `st.success` / `st.info` / `st.warning` / `st.error` | `ui.banner` (page notice), `ui.pill` (status), `st.toast` (confirmation) |
| `st.dataframe`, `st.data_editor` | `ui.grid`, `ui.editor` |
| `st.divider`, `st.expander` as layout | Cards and spacing already separate content |

Native inputs and layout are fine and already themed: `st.columns`, `st.tabs`,
`st.form`, `st.dialog`, `st.navigation`, `st.button`, `st.selectbox`, `st.pills`,
`st.segmented_control`, `st.toggle`, `st.text_input`, `st.number_input`,
`st.date_input`, `st.file_uploader`, `st.download_button`, `st.toast`.

**Layout**
- Column splits: `[5, 3]` for main + side, `2` or `3` equal columns for peers.
  At most three cards in a row.
- Filters sit in one row under the header with labels collapsed, and filter the
  whole page.
- Cards in one row share a height (the default). A card whose content should not
  stretch takes `height=None`.

**Actions**
- One primary button per page (`type="primary"`), right-aligned, at the end of the
  task. Everything else is a default button.
- Button labels say what happens: "Save forecast", "Apply import", "Close period" —
  not "Submit" or "OK".
- An action that cannot be undone opens an `st.dialog` that states the consequence
  and offers Cancel beside the action.
- A disabled action is explained by a `ui.banner` or checklist saying what is missing.
- Confirm a successful save with `st.toast`, not a persistent message.
- Group related inputs in `st.form` so the page does not rerun on every keystroke;
  keep multi-step state in `st.session_state`.

**Tables and editors**
- Make it obvious what can be edited: pass only input columns to `editable`, and say
  so in the card caption ("Forecast and comment are editable").
- One unit per column, named in the header or caption ("$M"), not repeated in cells.
- Variances use `ui.col_number(..., signed=True)`. Percent complete uses
  `ui.col_progress`.
- Keep totals in a `ui.stat_strip` above the grid, recalculated from the filtered rows.
- Order rows by what matters (structure, largest variance, latest date), and never
  show the DataFrame index.

**Colour carries meaning, so spend it carefully.**
- Neutral by default. Most of the page is ink on white; colour appears in data and
  status only.
- Series colours come from `ui.tokens()["series"]` in order. A series keeps its
  colour on every page and under every filter. More than six series: group the tail
  as "Other" or use a table.
- Status colours (green, amber, red) mean status and nothing else, and always come
  with an icon and a word. Never colour a KPI value itself.
- `tone` on a delta or stat is a judgement, not a sign: cost up is `"bad"`, progress
  up is `"good"`. Decide it from the metric's meaning.
- Plan and baseline are grey context lines. Only forecasts are dashed or lighter.

**Charts**
- One y-axis per chart. Two measures with different units go in two charts.
- No pie or donut charts, no 3D, no gauges. Ranked bars or a KPI card say it better.
- Titles and units live in the card title and caption, not inside the figure.
- Pre-scale values and pass `prefix`/`suffix` (`"$"`, `"M"`), so axes read `$800M`.
- Chart height 260–350 px.

**Numbers**
- Every number goes through `ui.money`, `ui.pct`, `ui.signed`, a `ui.col_*` format
  or an explicit format string.
- KPI values show three significant figures (`$1.29B`, `54.0%`, `0.95`).
- Deltas always carry a sign and a unit, and say what they compare with:
  `+3.7%` "vs $1.24B budget". Percentage-point gaps are `pts`, not `%`.
- Dates read `31 Oct 2026`. Show the working period in the header `meta`.

**Words**
- Sentence case everywhere. No emoji in titles, labels, tabs or buttons.
- Card title names the thing ("Cost S-curve"); caption gives unit or definition
  ("Cumulative, $M"). Spell out an abbreviation once, in the label or caption.
- KPI and stat labels are two to four words. Notes are a short phrase.
- Messages say what happened and what to do next, in plain words:
  "October 2026 cannot be closed yet. 1 item must be resolved first."

## When the kit lacks something

Add it to `ui_kit` as a reusable component or chart recipe, then call it from the
page. Do not write one-off HTML or CSS in a page: that is how an app drifts back to
looking improvised. `references/design-system.md` has the tokens, the type scale,
the component pattern and the constraints of `st.html` (inline `<svg>` and scripts
are stripped). Read it before adding or changing anything in `ui_kit`, and before
changing brand colours or fonts.

## Checklist before finishing

- [ ] `ui.setup_page(...)` is called once, first, in the entry file; page files live in `views/`.
- [ ] Every page starts with a type-and-plan docstring and `ui.page_header`.
- [ ] Page files have no HTML, CSS, hex colour, `unsafe_allow_html` or font size.
- [ ] No `st.title`/`st.header`/`st.metric`/`st.plotly_chart`/`st.dataframe`/`st.data_editor`/`st.warning`/`st.divider` in pages.
- [ ] Bands follow the page type's order; at most 3 cards per row; KPI row has 4–6 cards.
- [ ] Every chart, table and form section sits in a `ui.card` with a title and a caption giving the unit or purpose.
- [ ] Every figure is rendered with `ui.show`.
- [ ] One primary button per page; irreversible actions confirm in a dialog.
- [ ] Editable columns are the only unlocked ones and are named in the caption.
- [ ] Every delta has a sign, a unit, a comparison note and a deliberate `tone`.
- [ ] Status is shown with a pill or icon and a word, never colour alone.
- [ ] Filters that can return no rows are handled with `ui.empty_state`.
- [ ] No emoji; sidebar icons are Material Symbols.
- [ ] App runs with no exceptions and no Streamlit warnings in the terminal.
