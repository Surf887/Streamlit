# Project controls patterns

What to put on a project controls dashboard, and which component shows it. For the
other page types (workspaces, forms, imports, registers, period close) see
`page-types.md`. Thresholds and definitions here are common defaults: confirm them
with the user, because every project sets its own.

## Contents
- Pages and the question each answers
- KPI catalogue
- Status thresholds
- Which chart for which question
- Tables
- Vocabulary and formats

## Pages and the question each answers

| Page | Question | KPI row | Main row | Supporting |
|---|---|---|---|---|
| Overview | Are we on budget and on schedule? | Forecast at completion, progress, CPI, SPI, contingency | S-curve + progress by discipline | Budget-to-forecast bridge, variance by area, index trend, milestones |
| Cost | Where is the money going and what will it finish at? | Budget, committed, actual to date, forecast at completion, variance at completion | Cost S-curve + variance by area | Bridge, commitments vs budget by package, contingency rundown |
| Schedule | Will we finish on time, and what is driving it? | SPI, progress vs plan, critical milestones late, float on critical path | Progress S-curve + milestone slip | Progress by discipline, lookahead table |
| Change | What is changing the baseline? | Approved, pending, rejected (count and value), average days to decide | Cumulative change value over time + value by area | Change log table with status pills |
| Risk | What could move the forecast? | Open risks, high risks, exposure, contingency vs exposure | Exposure by category + top risks table | Contingency rundown |

One page, one question. A KPI that does not help answer the page's question belongs
on another page.

## KPI catalogue

Abbreviations: BAC budget at completion, PV planned value, EV earned value,
AC actual cost, EAC estimate (forecast) at completion.

| KPI | Definition | Format | Delta / note | Tone |
|---|---|---|---|---|
| Forecast at completion | EAC | `ui.money` | `% vs budget`, note "vs $X budget" | Over budget is bad |
| Variance at completion | BAC − EAC | `ui.money` with sign | note "budget minus forecast" | Negative is bad |
| Actual to date | AC | `ui.money` | note "X% of budget spent" | Neutral |
| Committed | Value of awarded contracts and orders | `ui.money` | note "X% of budget" | Neutral |
| Progress | EV / BAC | `ui.pct` | `pts vs planned`, note "vs X% planned" | Behind plan is bad |
| CPI | EV / AC | two decimals | status pill, note "target 1.00" | Below 1 is bad |
| SPI | EV / PV | two decimals | status pill, note "target 1.00" | Below 1 is bad |
| Cost variance | EV − AC | `ui.money` with sign | | Negative is bad |
| Schedule variance | EV − PV | `ui.money` with sign | | Negative is bad |
| TCPI | (BAC − EV) / (BAC − AC) | two decimals | note "efficiency needed to finish on budget" | Above about 1.05 is bad |
| Contingency remaining | Contingency − drawdown | `ui.money` | note "X% of $Y" | Bad when below remaining risk exposure |
| Pending changes | Sum of unapproved change value | `ui.money` | note "N requests" | Neutral or warn |
| Milestones late | Count with forecast after baseline | integer | note "of N in next 90 days" | More is bad |

Show a sparkline when history for the last 6–12 periods exists; use sparklines on
all cards in a row or on none, so the row stays even.

## Status thresholds (defaults)

| Measure | Good | Warning | Critical |
|---|---|---|---|
| CPI, SPI | 1.00 and above | 0.95 to 0.99 | below 0.95 |
| Forecast vs budget | at or under budget | up to 5% over | more than 5% over |
| Progress vs plan | within 2.5 pts | 2.5 to 7.5 pts behind | more than 7.5 pts behind |
| Milestone slip | on time or early | 1 to 30 days late | more than 30 days late |

Keep thresholds in one place in the data layer (a small `status_for(metric, value)`
function returning `(label, status)`), not scattered through pages. Labels: "On
track", "Watch", "At risk", "Behind", "Over budget" — a word that says what is
wrong, not just "Red".

## Which chart for which question

| Question | Component |
|---|---|
| How do plan, earned and actual compare over time? | `ui.s_curve` |
| Why did the forecast move from A to B? | `ui.bridge` |
| Which areas, packages or disciplines are over or under? | `ui.variance_bars` |
| Is performance improving or deteriorating? | `ui.index_trend` |
| Which milestones have slipped, and by how much? | `ui.milestone_slip` |
| How is cost phased by month, and what is still to come? | `ui.monthly_bars` |
| Is contingency being used faster than planned? | `ui.rundown` |
| How far along is each discipline against plan? | `ui.progress_list` |
| What are the specific items (changes, risks, packages)? | `ui.status_table` or `st.dataframe` |
| A single headline value | A KPI card — not a chart |

Avoid: gauges for CPI/SPI (a KPI card with a pill is clearer), pie charts for cost
breakdown (use ranked bars), cost and progress on one chart with two axes (use two
charts), full Gantt charts with hundreds of bars (show key milestones and link to
the scheduling tool).

## Tables

- Up to about 12 rows with a status: `ui.status_table` (pills, right-aligned numbers).
- Larger or sortable data: `ui.grid(df, columns={...})` inside a `ui.card`; editable
  data: `ui.editor`. Use `ui.col_number` for money (unit in the header) and
  `ui.col_progress` for percent complete.
- Order rows by what matters (largest variance, latest date), not alphabetically.
- Right-align numbers and dates; keep one unit per column and name it in the header
  ("Value, $M").

## Vocabulary and formats

- Use the project's own terms for WBS levels (area, unit, package, discipline) and
  ask if unsure.
- Money: one unit per page where possible ($M), stated in captions. KPI cards may
  use the compact form (`$1.29B`).
- Percent complete to one decimal in KPI cards, whole numbers in bars and tables.
- Indices (CPI, SPI, TCPI) always to two decimals.
- Favourable and unfavourable must be unambiguous: say "over budget" / "behind
  plan" in notes rather than relying on a sign.
- Always show the data date. Numbers without an as-of date are not trusted.
