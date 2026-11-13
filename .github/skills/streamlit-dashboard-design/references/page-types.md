# Page types

How to choose a page type and what each one contains. The working examples are in
`assets/example/views/`; read the one for the type you are building.

## Contents
- Choosing a type
- Typical project controls screens and their type
- Dashboard
- Workspace
- Form
- Stepped task
- Register
- Checklist and close
- Reference
- Patterns shared by all types

## Choosing a type

Ask what the user does on the page:

| The user… | Type |
|---|---|
| reads the state of things and spots problems | Dashboard |
| enters or adjusts values across many rows | Workspace |
| fills in a handful of fields that rarely change | Form |
| brings something in or runs a job with distinct stages | Stepped task |
| logs, classifies and follows up individual records | Register |
| checks everything is ready, then commits | Checklist and close |
| looks up a definition, rule or template | Reference |

A page that seems to need two types is two pages. A dashboard may carry a small
detail table, and a workspace may carry one chart of what is being edited; beyond
that, link to the other page.

## Typical project controls screens and their type

| Screen | Type | Notes |
|---|---|---|
| Project setup (identity, currency, funding, contingency, team, FX rates) | Form | One card per group of fields |
| Work breakdown structure, cost activities and original budgets | Workspace | `num_rows="dynamic"` to add rows |
| Gate and milestone dates | Workspace | Date columns; baseline locked once set |
| Import of actuals and commitments | Stepped task | Upload · Map · Review · Apply |
| Contractor submissions | Register | Table + selected submission; Accept / Return as actions |
| Cost workspace (forecast per activity, period comments) | Workspace | Forecast and comment editable |
| Profiles and work in progress | Workspace | Add `ui.monthly_bars` under the grid |
| Key quantities | Workspace | |
| Progress and earned value | Dashboard | `ui.s_curve`, `ui.index_trend`, `ui.progress_list` |
| Reconciliation of budget, forecast and source totals | Workspace (read-only) | `ui.stat_strip` of differences, `ui.grid`, `ui.banner` when out of balance |
| Cost and hours tables | Workspace (read-only) | `ui.grid` with `st.tabs` for cost / hours |
| Highlights | Dashboard | The overview page |
| Forecast bridge, month to month | Dashboard | `ui.bridge`, `ui.variance_bars` |
| Change register | Register | |
| Risks and opportunities | Register | |
| Contingency drawdown, funding, currency effects | Dashboard | `ui.rundown`, `ui.bridge` |
| Report readiness and period close | Checklist and close | |
| Excel export | Part of the close page | A `st.download_button` in its own card |
| Definitions, calculations, rules, templates | Reference | |

## Dashboard

Example: `views/highlights.py`. One question per page.

1. `ui.page_header` with the period in `meta` and an overall status pill.
2. Filter row.
3. `ui.kpi_row` — 4 to 6 cards; sparklines on all cards or none.
4. Main row, `st.columns([5, 3])`: the trend chart wide, a breakdown narrow.
5. Supporting rows, `st.columns(2)`: charts that explain why.
6. Detail: `ui.status_table` or `ui.grid` in a full-width card.

## Workspace

Example: `views/cost_workspace.py`. The grid is the page; everything else supports it.

1. `ui.page_header`; use the `status` pill for completeness ("12 of 14 updated").
2. Filter row: a select for the main grouping, a search box, a toggle for
   "only exceptions".
3. `ui.stat_strip` — the totals of the visible rows, with the variance carrying a
   `tone` and a plain-words note ("over budget").
4. `ui.editor` in a card. The caption states the unit and which columns are
   editable. Fix the height (about 420 px) when there are more than 12 rows.
5. Optional: one chart of what is being edited, in its own card with `height=None`.
6. Save row: a caption about unsaved changes on the left, the primary button on the
   right. Confirm with `st.toast`.

Read-only variants (reconciliation, cost tables) use `ui.grid` and have no save row.

## Form

Example: `views/project_setup.py`.

1. `ui.page_header`.
2. `st.columns([5, 3])`. Left: one `st.form(border=False)` containing a `ui.card`
   per group of fields, with fields in two or three columns. Right: a read-only
   `ui.key_value` summary of what is currently in force, and one `ui.banner`
   explaining when changes take effect.
3. A single primary `st.form_submit_button`, right-aligned under the last card.

Field labels are nouns ("Approved budget"), units go in the card caption, and
related fields share a row. Do not use placeholder text as the only label.

## Stepped task

Example: `views/import_actuals.py`.

1. `ui.page_header` with the period and the last time the task was run.
2. `ui.stepper(steps, current)` — three to five steps, each named with one or two words.
3. One card for the current step only. A review step shows a `ui.stat_strip`
   (rows read, matched, unmatched, value) and the exceptions that need a decision in
   a `ui.editor`.
4. One `ui.banner` stating that nothing is saved until the last step.
5. Back (left) and the primary Next / Apply button (right). Keep the step index in
   `st.session_state`.

## Register

Example: `views/change_register.py`.

1. `ui.page_header`.
2. `ui.stat_strip` — value and count per status.
3. Filter row: `st.pills` for status (multi-select), a select for area.
4. `st.columns([5, 3])`. Left: `ui.grid(..., on_select="rerun",
   selection_mode="single-row")` in a card. Right: the selected record in a card,
   using `ui.key_value` with the status as a pill, then its actions.
5. Optional: one related chart in a full-width card.

If statuses recorded in the app are not formal approvals, say so once with a
`ui.banner` in the detail card.

## Checklist and close

Example: `views/period_close.py`.

1. `ui.page_header`; the status pill says "Ready to close" or "N blocking".
2. `ui.banner` (critical) naming what blocks the action, shown only when blocked.
3. `st.columns([5, 3])`. Left: `ui.checklist` in a card titled "Readiness" with
   "3 of 6 complete" as the caption. Right: a card for the action with a
   `ui.key_value` summary and the primary button, disabled while blocked; below it,
   a card for exports.
4. The action opens an `st.dialog` that repeats what will be saved, states that it
   cannot be undone, and offers Cancel and the action side by side.

Checklist statuses: `good` done, `warning` needs attention but does not block,
`critical` blocks, `neutral` not started. Put the date or count in `meta`.

## Reference

No example file; it is the simplest type.

1. `ui.page_header`.
2. A search `st.text_input` (label collapsed) filtering the topics.
3. One `ui.card` per topic, in a single column no wider than `st.columns([5, 3])`'s
   left side so lines stay readable. Body text via `st.markdown` (plain markdown
   only); formulas via `st.latex` or a `ui.key_value` of term and definition.

## Patterns shared by all types

- The `eyebrow` of the page header is the sidebar group the page belongs to.
- Always show the working period in the header `meta`.
- A banner is for the page's single most important notice. Two banners means one of
  them belongs in a checklist, a pill or a caption.
- Empty results use `ui.empty_state` with a hint about how to get data back.
- Long-running work shows `st.spinner` with a plain description of what is happening.
