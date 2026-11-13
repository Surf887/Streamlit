# Design system reference

Read this before changing anything inside `ui_kit/`, adding a component or chart, or
rebranding. Page code never needs it.

## Contents
- Where things live
- Tokens
- Type scale
- Spacing, radius, elevation
- Adding a component
- Adding a chart
- Rebranding (colours, font)
- Light and dark mode
- Streamlit version notes

## Where things live

| File | Holds |
|---|---|
| `.streamlit/config.toml` | Streamlit's own theme: font, base size, radius, widget colours |
| `static/InterVariable.woff2` | The font, served by the app itself (no internet needed) |
| `ui_kit/theme.py` | Tokens (`LIGHT`, `DARK`), icons, all CSS, `setup_page` |
| `ui_kit/components.py` | HTML components and number formatters |
| `ui_kit/charts.py` | Plotly base style and chart recipes |

`config.toml` and `theme.py` repeat the same colour values. Change both together.

## Tokens

Get them with `ui.tokens()` inside a script run (not at import: the mode can change).

| Token | Light | Dark | Role |
|---|---|---|---|
| `bg` | `#F5F6F8` | `#0D1117` | Page plane |
| `surface` | `#FFFFFF` | `#161B22` | Cards |
| `surface_2` | `#F0F2F5` | `#1F252E` | Tracks, subtle fills |
| `border` | `#E3E6EB` | `#2A313C` | Card and table hairlines |
| `ink` | `#111827` | `#E6E9EE` | Values, titles |
| `ink_2` | `#4B5563` | `#B3BAC5` | Body text |
| `ink_3` | `#6B7280` | `#8B94A3` | Labels, captions, axis ticks |
| `accent` | `#256ABF` | `#3987E5` | Primary action, default bar |
| `context` | `#9AA3B2` | `#6B7482` | Plan, baseline, totals, "everything else" |
| `grid` / `axis` | `#E9ECF0` / `#C9CED6` | `#232A34` / `#39414D` | Chart chrome |
| `neg` / `pos` | blue / red | blue / red | Two sides of a signed value |
| `series[0..7]` | blue, orange, aqua, yellow, magenta, green, violet, red | same hues, re-stepped | Categorical series, fixed order |
| `status[name]` | `fg`, `bg`, `solid` | | `good`, `warning`, `critical`, `info`, `neutral` |

The series order is deliberate: neighbouring colours were checked to stay
distinguishable under colour-vision deficiency. Use slots in order and do not
reorder or insert hues. Three of the light series colours (aqua, yellow, magenta)
have low contrast against white, so a chart using them needs a legend or labels,
which the recipes already provide.

In CSS the same values are available as `var(--uk-surface)`, `var(--uk-ink-3)`,
`var(--uk-good-fg)` and so on (see the `:root` block in `theme.py`).

## Type scale

One family (Inter), six sizes. Do not introduce a size outside this table.

| Use | Size / weight | Colour |
|---|---|---|
| Page title | 24 / 650, tracking -0.02em | `ink` |
| KPI value | 28 / 650, tracking -0.025em, tabular figures | `ink` |
| Section title | 15 / 650 | `ink` |
| Card title | 14 / 650 | `ink` |
| Body, table cells | 13–14 / 400–500 | `ink_2` |
| Labels, captions, axis ticks, pills | 12–12.5 / 500–600 | `ink_3` |

Numbers that line up in columns use the `.uk-num` class (tabular figures).

## Spacing, radius, elevation

- Card padding 18–20 px; gap between cards 14–16 px (Streamlit's default column gap).
- Radius 10 px on cards, 8 px on widgets, 999 px on pills, 4 px on bar ends.
- One elevation: hairline border plus a 1 px shadow in light mode, border only in dark.
  No heavier shadows, no gradients, no coloured card backgrounds.

## Adding a component

Pattern (see `page_header` or `progress_list` for a full example):

1. In `components.py`, write a function that builds an HTML string and ends with
   `_render(html)`. Escape every piece of data with `_e(...)`.
2. Add its CSS to `_CSS` in `theme.py`, with class names prefixed `uk-`, using only
   `var(--uk-*)` colours and sizes from the type scale. `_CSS` is a `%`-format
   string: write a literal percent sign as `%%`.
3. Export it from `ui_kit/__init__.py`.
4. Check it in light and dark mode.

Constraints of `st.html` (it sanitises its input):

- Inline `<svg>` and `<script>` are removed. For icons, add a path to `ICONS` in
  `theme.py` and use `<i class="uk-i uk-i-NAME"></i>`; it takes the surrounding text
  colour. For data-driven graphics, build an SVG string and embed it as an
  `<img src="data:image/svg+xml;base64,...">` (see `sparkline_img`).
- Inline `style="..."` attributes survive; use them only for data-driven values
  such as a bar width.
- Do not target Streamlit's generated class names (`st-emotion-cache-*`); they
  change between versions. Stable hooks are `data-testid` attributes and the
  `st-key-<key>` class that `st.container(key=...)` adds, which is how `ui.card`
  is styled.

## Adding a chart

1. Build a `go.Figure` in `charts.py` using colours from `tokens()` only.
2. Call `style(fig, height=...)` — it sets font, grid, legend, hover label and
   transparent backgrounds so the card surface shows through.
3. Return the figure; pages render it with `ui.show(fig)`.

Conventions the existing recipes follow:

- Lines 2–2.5 px; bars with 4 px rounded ends; markers at least 9 px with a 2 px
  surface-coloured ring.
- Horizontal gridlines only, solid hairlines. No axis lines, no tick marks.
- Legend above the plot, left-aligned, whenever there are two or more series.
  With four series or fewer, also label line ends directly where they will not collide.
- Label values selectively (bar ends, last point), never every point.
- `hovermode="x unified"` for time series; a one-line `hovertemplate` elsewhere.
- Category labels wrap (`_wrap`) rather than rotate.
- A truncated value axis is allowed only when every bar is labelled and the axis is
  hidden, as in `bridge`.

## Rebranding

Brand colour: change `accent` in `LIGHT` and `DARK` and `primaryColor` in both
`[theme.light]` and `[theme.dark]`. Keep text contrast of at least 4.5:1 for white
text on the accent.

Series colours: replace the `series` lists and `chartCategoricalColors` together.
Any new palette needs checking for colour-blind separation between neighbouring
slots before use; if that cannot be checked, keep the shipped palette and change only
the accent.

Font: put the `.woff2` files in `static/`, declare them under `[[theme.fontFaces]]`,
set `font` and `headingFont` in `config.toml`, and update `FONT` in `theme.py`.
Choose a face with tabular figures. Keep one family for the whole app.

## Light and dark mode

Both are defined and the viewer's choice is followed automatically:
`ui.tokens()` reads `st.context.theme.type`. To force one mode, delete the other
`[theme.*]` section from `config.toml` and make `mode()` in `theme.py` return a
constant. Never hard-code a colour that only works in one mode.

## Streamlit version notes

- Written for and tested on Streamlit 1.67 with Plotly 7.
- `ui_kit` needs 1.46 or newer (`st.context.theme`, keyed containers, `st.html`).
- If Streamlit reports that it does not recognise `[theme.light]` / `[theme.dark]`,
  the installed version predates them: move the `[theme.light]` values into `[theme]`
  and delete both mode sections. The app is then light-only.
- `ui.card` falls back to content height where `height="stretch"` is unsupported.
