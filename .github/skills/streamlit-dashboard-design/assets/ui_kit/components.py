"""Layout and display components. All HTML lives here - app code never writes HTML or CSS."""
from __future__ import annotations

import base64
import html as _html
import re
from contextlib import contextmanager
from typing import Iterable, Mapping, Sequence

import streamlit as st

from .theme import tokens

_e = _html.escape

# ----------------------------------------------------------------------------
# Formatters - every number on screen goes through one of these
# ----------------------------------------------------------------------------
MINUS = "−"  # true minus sign, same width as "+"


def money(x: float, *, currency: str = "$", decimals: int | None = None) -> str:
    """1_240_000_000 -> '$1.24B', 312_500_000 -> '$312.5M', 48_200 -> '$48.2K'."""
    if x is None:
        return "–"
    sign, a = (MINUS if x < 0 else ""), abs(x)
    for div, suf, dec in ((1e9, "B", 2), (1e6, "M", 1), (1e3, "K", 1)):
        if a >= div:
            d = dec if decimals is None else decimals
            return f"{sign}{currency}{a / div:,.{d}f}{suf}"
    return f"{sign}{currency}{a:,.0f}"


def pct(x: float, *, decimals: int = 1) -> str:
    """0.569 -> '56.9%'."""
    if x is None:
        return "–"
    return f"{x * 100:.{decimals}f}%".replace("-", MINUS)


def signed(x: float, fmt: str = "{:,.1f}", *, suffix: str = "") -> str:
    """Explicit sign for deltas: 2.1 -> '+2.1', -4.5 -> '−4.5'."""
    if x is None:
        return "–"
    s = "+" if x > 0 else (MINUS if x < 0 else "")
    return f"{s}{fmt.format(abs(x))}{suffix}"


STATUSES = ("good", "warning", "critical", "info", "neutral")
TONES = ("good", "bad", "warn", "neutral")


def _render(body: str) -> None:
    st.html(f'<div class="uk">{body}</div>')


# ----------------------------------------------------------------------------
# HTML builders (return strings, for composing)
# ----------------------------------------------------------------------------
def pill_html(label: str, status: str = "neutral") -> str:
    """Status pill: icon + label. status: good | warning | critical | info | neutral."""
    status = status if status in STATUSES else "neutral"
    return f'<span class="uk-pill uk-pill-{status}"><i class="uk-i uk-i-{status}"></i>{_e(str(label))}</span>'


def delta_html(text: str, tone: str = "neutral") -> str:
    """Delta chip. `tone` says whether the change is good or bad - it is NOT the sign.
    (Cost going up is 'bad'; progress going up is 'good'.) The arrow follows the sign."""
    tone = tone if tone in TONES else "neutral"
    t = str(text).strip()
    arrow = ('<i class="uk-i uk-i-up"></i>' if t.startswith("+")
             else '<i class="uk-i uk-i-down"></i>' if t[:1] in ("-", MINUS) else "")
    return f'<span class="uk-delta uk-tone-{tone} uk-num">{arrow}{_e(t.lstrip("+-" + MINUS))}</span>'


def sparkline_img(values: Sequence[float], *, color: str | None = None) -> str:
    """Tiny trend line for a KPI card, as an <img> (st.html strips inline <svg>).
    No axes - it shows shape only, so always pair it with the number."""
    vals = [float(v) for v in values if v is not None and v == v]
    if len(vals) < 2:
        return ""
    color = color or tokens()["accent"]
    w, h, pad = 240.0, 30.0, 3.0
    lo, hi = min(vals), max(vals)
    span = (hi - lo) or 1.0
    pts = [(i * w / (len(vals) - 1), pad + (h - 2 * pad) * (1 - (v - lo) / span))
           for i, v in enumerate(vals)]
    line = " ".join(f"{'M' if i == 0 else 'L'}{x:.1f},{y:.1f}" for i, (x, y) in enumerate(pts))
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.0f} {h:.0f}" '
           f'preserveAspectRatio="none">'
           f'<path d="{line} L{w:.1f},{h:.1f} L0,{h:.1f} Z" fill="{color}" fill-opacity=".10"/>'
           f'<path d="{line}" fill="none" stroke="{color}" stroke-width="1.75" '
           f'stroke-linejoin="round" stroke-linecap="round" vector-effect="non-scaling-stroke"/></svg>')
    uri = "data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode()
    return f'<img src="{uri}" alt="">'


def _kpi_html(label: str, value: str, *, unit: str | None = None, delta: str | None = None,
              tone: str = "neutral", note: str | None = None, status: tuple[str, str] | None = None,
              spark: Sequence[float] | None = None, **_: object) -> str:
    unit_html = f'<span class="uk-kpi-unit">{_e(unit)}</span>' if unit else ""
    foot = ((pill_html(status[0], status[1]) if status else "")
            + (delta_html(delta, tone) if delta else "")
            + (f"<span>{_e(note)}</span>" if note else ""))
    spark_html = f'<div class="uk-kpi-spark">{sparkline_img(spark)}</div>' if spark is not None else ""
    return (f'<div class="uk-kpi"><div class="uk-kpi-label">{_e(label)}</div>'
            f'<div class="uk-kpi-value uk-num">{_e(str(value))}{unit_html}</div>'
            f'<div class="uk-kpi-foot">{foot}</div>{spark_html}</div>')


# ----------------------------------------------------------------------------
# Components (render to the page)
# ----------------------------------------------------------------------------
def page_header(title: str, *, eyebrow: str | None = None, subtitle: str | None = None,
                meta: Mapping[str, str] | None = None, status: tuple[str, str] | None = None) -> None:
    """Top of page. `meta` = small label/value facts (e.g. {"Data date": "31 Oct 2026"}).
    `status` = (label, status) pill, e.g. ("At risk", "warning")."""
    left = ""
    if eyebrow:
        left += f'<div class="uk-eyebrow">{_e(eyebrow)}</div>'
    left += f'<h1 class="uk-title">{_e(title)}</h1>'
    if subtitle:
        left += f'<div class="uk-subtitle">{_e(subtitle)}</div>'
    right = "".join(
        f'<div class="uk-meta-item"><span class="uk-meta-label">{_e(k)}</span>'
        f'<span class="uk-meta-value uk-num">{_e(str(v))}</span></div>'
        for k, v in (meta or {}).items())
    if status:
        right += pill_html(status[0], status[1])
    _render(f'<div class="uk-header"><div>{left}</div><div class="uk-meta">{right}</div></div>')


def section(title: str, caption: str | None = None) -> None:
    """Heading for a group of cards. Use sparingly - one per row group."""
    cap = f'<span class="uk-section-caption">{_e(caption)}</span>' if caption else ""
    _render(f'<div class="uk-section"><span class="uk-section-title">{_e(title)}</span>{cap}</div>')


def kpi_row(items: Iterable[Mapping]) -> None:
    """A row of KPI cards (3-6). Each item: dict(label, value, unit=None, delta=None,
    tone='good'|'bad'|'warn'|'neutral', note=None, status=(label, status), spark=[...]).
    Under the value, show EITHER a delta chip OR a status pill, then a short note.
    Cards share one grid, so they are always equal height and wrap on narrow screens."""
    _render('<div class="uk-kpis">' + "".join(_kpi_html(**dict(i)) for i in items) + "</div>")


def kpi_card(label: str, value: str, **kwargs) -> None:
    """A single KPI card (prefer kpi_row for a row of them)."""
    _render(_kpi_html(label, value, **kwargs))


def pill(label: str, status: str = "neutral") -> None:
    _render(pill_html(label, status))


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-") or "card"


@contextmanager
def card(title: str | None = None, caption: str | None = None, *, key: str | None = None,
         status: tuple[str, str] | None = None, height: int | str | None = "stretch"):
    """Card surface for a chart, table or any content.

        with ui.card("Cost S-curve", "Cumulative, $M"):
            ui.show(fig)

    `key` must be unique on the page; it defaults to the title.
    height="stretch" (default) makes cards in the same st.columns row equal height;
    pass a pixel int for a fixed-height scrolling card, or None for content height."""
    k = "ukcard-" + _slug(key or title or "card")
    kwargs = {"border": True, "key": k}
    if height:
        kwargs["height"] = height
    try:
        box = st.container(**kwargs)
    except Exception:  # older Streamlit: no height="stretch"
        kwargs.pop("height", None)
        box = st.container(**kwargs)
    with box:
        if title:
            cap = f'<div class="uk-card-caption">{_e(caption)}</div>' if caption else ""
            right = pill_html(status[0], status[1]) if status else ""
            _render(f'<div class="uk-card-head"><div><div class="uk-card-title">{_e(title)}</div>'
                    f'{cap}</div>{right}</div>')
        yield box


def progress_list(rows: Iterable[Mapping], *, actual_label: str = "Actual",
                  planned_label: str = "Planned", watch: float = 0.025, behind: float = 0.075) -> None:
    """Progress bars with a planned marker. rows: dict(label, actual, planned) as 0-1 fractions.
    Bar turns amber when actual trails planned by more than `watch`, red beyond `behind`."""
    out = []
    for r in rows:
        a, p = float(r["actual"]), r.get("planned")
        gap = round(p - a, 6) if p is not None else 0.0
        cls = " is-behind" if gap > behind else " is-watch" if gap > watch else ""
        tick = f'<div class="uk-prog-tick" style="left:calc({min(max(p, 0), 1) * 100:.1f}% - 1px)"></div>' if p is not None else ""
        plan = f"<small>plan {pct(p, decimals=0)}</small>" if p is not None else ""
        out.append(
            f'<div class="uk-prog-row"><span class="uk-prog-label">{_e(str(r["label"]))}</span>'
            f'<span class="uk-prog-val uk-num">{pct(a, decimals=0)}{plan}</span>'
            f'<div class="uk-prog-track"><div class="uk-prog-fill{cls}" '
            f'style="width:{min(max(a, 0), 1) * 100:.1f}%"></div>{tick}</div></div>')
    legend = (f'<div class="uk-prog-legend"><span><i class="bar"></i>{_e(actual_label)}</span>'
              f'<span><i class="tick"></i>{_e(planned_label)}</span></div>')
    _render(f'<div class="uk-prog">{"".join(out)}{legend}</div>')


def status_table(rows: Sequence[Mapping], columns: Mapping[str, str], *,
                 status_col: str | None = None, right: Sequence[str] = ()) -> None:
    """Small read-only table (<= ~12 rows) that can show status pills.
    columns: {row_key: header}. status_col cells must be (label, status) tuples.
    right: keys to right-align (numbers, dates). For large or sortable data use st.dataframe."""
    head = "".join(f'<th class="{"r" if k in right else ""}">{_e(h)}</th>' for k, h in columns.items())
    body = ""
    for r in rows:
        tds = ""
        for k in columns:
            v = r.get(k, "")
            cell = pill_html(v[0], v[1]) if k == status_col and isinstance(v, (tuple, list)) else _e(str(v))
            cls = "r uk-num" if k in right else ""
            tds += f'<td class="{cls}">{cell}</td>'
        body += f"<tr>{tds}</tr>"
    _render(f'<table class="uk-table"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>')


def empty_state(title: str, hint: str | None = None) -> None:
    """Show instead of an empty chart/table when a filter returns no data."""
    _render(f'<div class="uk-empty"><b>{_e(title)}</b>{_e(hint) if hint else ""}</div>')


# ----------------------------------------------------------------------------
# App pages: notices, steps, totals, checklists, facts, sidebar
# ----------------------------------------------------------------------------
def banner(title: str, detail: str | None = None, status: str = "info") -> None:
    """Slim page-level notice under the header (data caveat, unsaved state, not-approved warning).
    One per page at most. For field-level validation use the widget's own error state."""
    status = status if status in STATUSES else "info"
    body = f"<b>{_e(title)}</b>" + (f"<span>{_e(detail)}</span>" if detail else "")
    _render(f'<div class="uk-banner uk-banner-{status}"><i class="uk-i uk-i-{status}"></i><div>{body}</div></div>')


def stepper(steps: Sequence[str], current: int) -> None:
    """Horizontal progress through a multi-step task (import: Upload > Map > Review > Apply).
    `current` is the 0-based index of the active step; earlier steps show as done."""
    out = []
    for i, name in enumerate(steps):
        cls = "is-done" if i < current else "is-current" if i == current else ""
        dot = '<i class="uk-i uk-i-check"></i>' if i < current else str(i + 1)
        if i:
            out.append(f'<li class="uk-step-line {"is-done" if i <= current else ""}" aria-hidden="true"></li>')
        out.append(f'<li class="uk-step {cls}"><span class="uk-step-dot uk-num">{dot}</span>{_e(name)}</li>')
    _render(f'<ol class="uk-steps">{"".join(out)}</ol>')


def stat_strip(items: Iterable[Mapping]) -> None:
    """Compact row of totals above a table or editor (lighter than KPI cards).
    Each item: dict(label, value, note=None, tone=None|'good'|'bad'|'warn')."""
    cells = ""
    for it in items:
        tone = it.get("tone")
        note = (f'<span class="uk-stat-note {"is-" + tone if tone in ("good", "bad", "warn") else ""}">'
                f'{_e(str(it["note"]))}</span>') if it.get("note") else ""
        cells += (f'<div class="uk-stat"><span class="uk-stat-label">{_e(str(it["label"]))}</span>'
                  f'<span class="uk-stat-value uk-num">{_e(str(it["value"]))}</span>{note}</div>')
    _render(f'<div class="uk-stats">{cells}</div>')


def checklist(items: Iterable[Mapping]) -> None:
    """Readiness list. Each item: dict(label, status, detail=None, meta=None).
    status: good (done) | warning (needs attention) | critical (blocking) | neutral (not started)."""
    icon = {"good": "check", "warning": "warning", "critical": "critical", "neutral": "neutral", "info": "info"}
    rows = ""
    for it in items:
        st_ = it.get("status", "neutral")
        st_ = st_ if st_ in STATUSES else "neutral"
        detail = f'<div class="uk-check-detail">{_e(str(it["detail"]))}</div>' if it.get("detail") else ""
        meta = f'<span class="uk-check-meta uk-num">{_e(str(it["meta"]))}</span>' if it.get("meta") else ""
        rows += (f'<li><span class="uk-check-ico is-{st_}"><i class="uk-i uk-i-{icon[st_]}"></i></span>'
                 f'<div class="uk-check-body"><div class="uk-check-title">{_e(str(it["label"]))}</div>{detail}</div>{meta}</li>')
    _render(f'<ul class="uk-check">{rows}</ul>')


def key_value(facts: Mapping[str, object], *, columns: int = 2) -> None:
    """Read-only facts as label/value pairs (project identity, a selected record's details).
    A value may be a (label, status) tuple to show a status pill."""
    cells = ""
    for k, v in facts.items():
        val = pill_html(v[0], v[1]) if isinstance(v, (tuple, list)) and len(v) == 2 else _e(str(v))
        cells += (f'<div class="uk-kv-item"><span class="uk-kv-label">{_e(str(k))}</span>'
                  f'<span class="uk-kv-value uk-num">{val}</span></div>')
    _render(f'<div class="uk-kv" style="--uk-kv-cols:{int(columns)}">{cells}</div>')


def sidebar_context(app: str, facts: Mapping[str, object] | None = None) -> None:
    """Top of the sidebar: app name plus the working context (project, period, status).
    Call after st.navigation(...). A value may be a (label, status) tuple for a pill."""
    box = ""
    for k, v in (facts or {}).items():
        val = pill_html(v[0], v[1]) if isinstance(v, (tuple, list)) and len(v) == 2 else \
            f'<span class="uk-side-value">{_e(str(v))}</span>'
        box += f'<div><div class="uk-side-label">{_e(str(k))}</div>{val}</div>'
    box = f'<div class="uk-side-box">{box}</div>' if box else ""
    with st.sidebar:
        _render(f'<div class="uk-side"><div class="uk-side-app">{_e(app)}</div>{box}</div>')


# ----------------------------------------------------------------------------
# Tables and editable grids
# ----------------------------------------------------------------------------
def col_money(label: str, *, unit: str = "M", currency: str = "$", decimals: int = 1, **kw):
    """Money column for values already scaled to `unit` (e.g. $M). Right-aligned, grouped."""
    return st.column_config.NumberColumn(label, format=f"{currency}%,.{decimals}f{unit}", **kw)


def col_number(label: str, *, decimals: int = 0, suffix: str = "", signed: bool = False, **kw):
    """Plain number column, right-aligned and grouped. Put the unit in the header or the card
    caption ("Budget, $M") rather than repeating it in every cell. signed=True shows +/-
    (use it for variances)."""
    return st.column_config.NumberColumn(label, format=f"%{'+' if signed else ''},.{decimals}f{suffix}", **kw)


def col_pct(label: str, *, decimals: int = 1, **kw):
    """Percent column for values stored as 0-100."""
    return st.column_config.NumberColumn(label, format=f"%.{decimals}f%%", **kw)


def col_progress(label: str, **kw):
    """Progress bar column for values stored as 0-1 fractions."""
    return st.column_config.ProgressColumn(label, min_value=0.0, max_value=1.0, format="percent", **kw)


def col_text(label: str, *, width: str | None = None, **kw):
    return st.column_config.TextColumn(label, width=width, **kw)


def grid(df, *, columns: Mapping | None = None, height: int | str = "auto", key: str | None = None, **kw):
    """Read-only table for larger or sortable data. Put it inside a ui.card.
    `columns` = {column_name: ui.col_money(...), ...}; unlisted columns keep defaults.
    Extra keyword arguments go to st.dataframe (e.g. on_select="rerun", selection_mode="single-row")."""
    return st.dataframe(df, hide_index=True, column_config=dict(columns or {}), height=height, key=key, **kw)


def editor(df, *, columns: Mapping | None = None, editable: Sequence[str] = (), key: str,
           height: int | str = "auto", num_rows: str = "fixed", **kw):
    """Editable grid. Only the columns named in `editable` can be changed; the rest are locked,
    so users can tell inputs from calculated values. Returns the edited DataFrame."""
    locked = [c for c in df.columns if c not in editable]
    return st.data_editor(df, hide_index=True, column_config=dict(columns or {}), disabled=locked,
                          height=height, num_rows=num_rows, key=key, **kw)
