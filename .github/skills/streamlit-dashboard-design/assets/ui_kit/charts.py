"""Plotly chart recipes for project controls, pre-styled from the design tokens.

Every function returns a go.Figure. Render with `ui.show(fig)` - never call
st.plotly_chart directly, or the styling is lost.

Values are plotted as given: pre-scale to display units in the data layer
(e.g. pass $M, not raw dollars) and describe them with `prefix` / `suffix`.
"""
from __future__ import annotations

import inspect
from typing import Mapping, Sequence

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from .theme import FONT, tokens

MINUS = "−"
_HAS_WIDTH = "width" in inspect.signature(st.plotly_chart).parameters


# ----------------------------------------------------------------------------
# Base styling
# ----------------------------------------------------------------------------
def style(fig: go.Figure, *, height: int = 320, legend: bool = True) -> go.Figure:
    """Apply the design system to any Plotly figure. Use this for custom charts too."""
    t = tokens()
    axis = dict(
        showgrid=True, gridcolor=t["grid"], gridwidth=1, zeroline=False,
        showline=False, ticks="", automargin=True,
        tickfont=dict(size=12, color=t["ink_3"]),
        title=dict(font=dict(size=12, color=t["ink_3"]), standoff=8),
    )
    fig.update_layout(
        height=height,
        margin=dict(l=4, r=8, t=34 if legend else 8, b=4),
        font=dict(family=FONT, size=12.5, color=t["ink_2"]),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        colorway=t["series"],
        showlegend=legend,
        legend=dict(orientation="h", x=0, xanchor="left", y=1.0, yanchor="bottom",
                    font=dict(size=12.5, color=t["ink_2"]), bgcolor="rgba(0,0,0,0)",
                    itemsizing="constant", tracegroupgap=0),
        hoverlabel=dict(bgcolor=t["surface"], bordercolor=t["border_strong"],
                        font=dict(family=FONT, size=12.5, color=t["ink"])),
        hovermode="closest",
        bargap=0.38,
        uniformtext=dict(minsize=11, mode="hide"),
    )
    fig.update_xaxes(**axis)
    fig.update_yaxes(**axis)
    fig.update_xaxes(showgrid=False)       # horizontal gridlines only, by default
    return fig


def show(fig: go.Figure, *, key: str | None = None) -> None:
    """Render a figure with the toolbar hidden and the design-system styling intact."""
    kwargs = dict(theme=None, key=key, config={"displayModeBar": False})
    if _HAS_WIDTH:
        kwargs["width"] = "stretch"
    else:  # older Streamlit
        kwargs["use_container_width"] = True
    st.plotly_chart(fig, **kwargs)


def _wrap(label: str, width: int = 12) -> str:
    """Wrap a category label onto lines of ~`width` chars so axis labels never rotate."""
    lines, cur = [], ""
    for word in str(label).split():
        if cur and len(cur) + 1 + len(word) > width:
            lines.append(cur); cur = word
        else:
            cur = f"{cur} {word}".strip()
    return "<br>".join(lines + [cur])


def _mix(color: str, base: str, amount: float) -> str:
    """Blend `color` toward `base` (both #RRGGBB). amount=0 gives color, 1 gives base."""
    c, b = (int(color[i:i + 2], 16) for i in (1, 3, 5)), (int(base[i:i + 2], 16) for i in (1, 3, 5))
    return "#" + "".join(f"{round(x + (y - x) * amount):02X}" for x, y in zip(c, b))


def _num(prefix: str, suffix: str, decimals: int) -> str:
    """d3 hover/tick format pieces -> a hovertemplate value token."""
    return f"{prefix}%{{VAL:,.{decimals}f}}{suffix}"


# ----------------------------------------------------------------------------
# 1. S-curve - cumulative plan vs earned vs actual, with forecast
# ----------------------------------------------------------------------------
def s_curve(df: pd.DataFrame, *, x: str, planned: str, earned: str | None = None,
            actual: str | None = None, forecast: str | None = None, data_date=None,
            names: Mapping[str, str] | None = None, prefix: str = "", suffix: str = "",
            decimals: int = 0, height: int = 340) -> go.Figure:
    """Cumulative S-curve. One y-axis, one unit for every series.
    Plan is the neutral context line; forecast is the only dashed line (dashed = projection)."""
    t = tokens()
    n = {"planned": "Planned", "earned": "Earned", "actual": "Actual", "forecast": "Forecast"}
    n.update(names or {})
    tmpl = "%{fullData.name}: <b>" + _num(prefix, suffix, decimals).replace("VAL", "y") + "</b><extra></extra>"
    fig = go.Figure()
    fig.add_scatter(x=df[x], y=df[planned], name=n["planned"], mode="lines",
                    line=dict(color=t["context"], width=2), hovertemplate=tmpl)
    if earned:
        fig.add_scatter(x=df[x], y=df[earned], name=n["earned"], mode="lines",
                        line=dict(color=t["series"][0], width=2.5), hovertemplate=tmpl)
    if actual:
        fig.add_scatter(x=df[x], y=df[actual], name=n["actual"], mode="lines",
                        line=dict(color=t["series"][1], width=2.5), hovertemplate=tmpl)
    if forecast:
        fig.add_scatter(x=df[x], y=df[forecast], name=n["forecast"], mode="lines",
                        line=dict(color=t["series"][0], width=2, dash="dot"), hovertemplate=tmpl)
    style(fig, height=height)
    fig.update_layout(hovermode="x unified")
    fig.update_yaxes(tickprefix=prefix, ticksuffix=suffix, tickformat=",.0f", rangemode="tozero")
    fig.update_xaxes(hoverformat="%b %Y", tickformat="%b\n%Y")
    if data_date is not None:
        d = pd.Timestamp(data_date)
        fig.add_shape(type="line", x0=d, x1=d, y0=0, y1=1, yref="paper",
                      line=dict(color=t["ink_3"], width=1))
        fig.add_annotation(x=d, y=1, yref="paper", text="Data date", showarrow=False,
                           xanchor="right", yanchor="top", xshift=-6,
                           font=dict(size=11.5, color=t["ink_3"]))
    return fig


# ----------------------------------------------------------------------------
# 2. Variance bars - signed value per category (over / under)
# ----------------------------------------------------------------------------
def variance_bars(df: pd.DataFrame, *, category: str, value: str, prefix: str = "",
                  suffix: str = "", decimals: int = 1, positive_is_bad: bool = True,
                  sort: bool = True, height: int | None = None) -> go.Figure:
    """Horizontal diverging bars around zero, sorted worst-first.
    Colour = sign (one hue per side); the label carries the exact number."""
    t = tokens()
    d = df.sort_values(value, ascending=True) if sort else df.iloc[::-1]
    bad, ok = t["pos"], t["neg"]
    colors = [(bad if v > 0 else ok) if positive_is_bad else (ok if v > 0 else bad) for v in d[value]]
    labels = [f"{'+' if v > 0 else MINUS if v < 0 else ''}{prefix}{abs(v):,.{decimals}f}{suffix}"
              for v in d[value]]
    fig = go.Figure(go.Bar(
        x=d[value], y=d[category], orientation="h", marker=dict(color=colors, cornerradius=4),
        # positive bars are labelled at the bar end; negative ones are annotated below
        text=[lab if v >= 0 else "" for lab, v in zip(labels, d[value])],
        textposition="outside", cliponaxis=False, textfont=dict(size=12, color=t["ink_2"]),
        customdata=labels, hovertemplate="%{y}: <b>%{customdata}</b><extra></extra>"))
    style(fig, height=height or max(180, 44 * len(d) + 30), legend=False)
    # Negative bars carry their label on the empty side of the zero line, so it can never
    # collide with the category names on the left.
    for cat, v, lab in zip(d[category], d[value], labels):
        if v < 0:
            fig.add_annotation(x=0, y=cat, text=lab, showarrow=False, xanchor="left", xshift=6,
                               font=dict(size=12, color=t["ink_2"]))
    lo, hi = min(0.0, float(d[value].min())), max(0.0, float(d[value].max()))
    span = (hi - lo) or 1.0
    fig.update_xaxes(range=[lo - span * 0.03, hi + span * 0.34],   # right side: room for labels
                     showgrid=False, showticklabels=False,
                     zeroline=True, zerolinecolor=t["axis"], zerolinewidth=1)
    fig.update_yaxes(showgrid=False, tickfont=dict(size=12.5, color=t["ink"]))
    return fig


# ----------------------------------------------------------------------------
# 3. Bridge - how one number becomes another (budget -> EAC)
# ----------------------------------------------------------------------------
def bridge(steps: Sequence[tuple[str, float, str]], *, prefix: str = "", suffix: str = "",
           decimals: int = 0, increase_is_bad: bool = True, height: int = 320) -> go.Figure:
    """Waterfall. steps = [(label, value, kind)], kind in 'total' | 'delta'.
    The first step is the opening total; a later 'total' shows the running sum (value ignored)."""
    t = tokens()
    up, down = (t["pos"], t["neg"]) if increase_is_bad else (t["neg"], t["pos"])
    measures, ys, text, levels, running = [], [], [], [], 0.0
    for i, (_, v, kind) in enumerate(steps):
        if kind == "total" and i > 0:
            measures.append("total"); ys.append(0); levels.append(running)
            text.append(f"{prefix}{running:,.{decimals}f}{suffix}")
        elif kind == "total":
            running = v; measures.append("absolute"); ys.append(v); levels.append(v)
            text.append(f"{prefix}{v:,.{decimals}f}{suffix}")
        else:
            running += v; measures.append("relative"); ys.append(v); levels.append(running)
            text.append(f"{'+' if v > 0 else MINUS if v < 0 else ''}{prefix}{abs(v):,.{decimals}f}{suffix}")
    fig = go.Figure(go.Waterfall(
        x=[_wrap(s[0]) for s in steps], y=ys, measure=measures, text=text, textposition="outside",
        textfont=dict(size=12, color=t["ink_2"]), cliponaxis=False,
        increasing=dict(marker=dict(color=up)), decreasing=dict(marker=dict(color=down)),
        totals=dict(marker=dict(color=t["context"])),
        connector=dict(line=dict(color=t["axis"], width=1)),
        hovertemplate="%{x}: <b>%{text}</b><extra></extra>"))
    style(fig, height=height, legend=False)
    fig.update_layout(waterfallgap=0.42)
    lo, hi = min(levels), max(levels)
    span = max(hi - lo, hi * 0.04)
    # Zoomed axis so small deltas are readable. The total bars are therefore truncated:
    # every bar carries its value as a label and the axis is hidden, so nothing is read off it.
    fig.update_yaxes(range=[max(0, lo - span * 0.9), hi + span * 0.45], showticklabels=False,
                     showgrid=False)
    fig.update_xaxes(tickfont=dict(size=12, color=t["ink_2"]), tickangle=0)
    return fig


# ----------------------------------------------------------------------------
# 4. Index trend - CPI / SPI style ratios against a reference line
# ----------------------------------------------------------------------------
def index_trend(df: pd.DataFrame, *, x: str, series: Mapping[str, str], reference: float = 1.0,
                reference_label: str = "On plan", decimals: int = 2, height: int = 300) -> go.Figure:
    """Up to 4 ratio lines on one axis. series = {display name: column}.
    Each line is labelled at its last point; the legend stays for identity."""
    t = tokens()
    fig = go.Figure()
    ends = []
    for i, (name, col) in enumerate(series.items()):
        c = t["series"][i]
        fig.add_scatter(x=df[x], y=df[col], name=name, mode="lines", line=dict(color=c, width=2.5),
                        hovertemplate=f"{name}: <b>%{{y:.{decimals}f}}</b><extra></extra>")
        last = df[[x, col]].dropna().iloc[-1]
        fig.add_scatter(x=[last[x]], y=[last[col]], mode="markers", showlegend=False, hoverinfo="skip",
                        marker=dict(size=9, color=c, line=dict(color=t["surface"], width=2)))
        ends.append((name, last[x], float(last[col])))
    style(fig, height=height)
    fig.update_layout(hovermode="x unified", margin=dict(r=74))
    vals = pd.concat([df[c] for c in series.values()]).dropna()
    lo, hi = min(vals.min(), reference), max(vals.max(), reference)
    pad = (hi - lo) * 0.25 or 0.05
    fig.update_yaxes(range=[lo - pad, hi + pad], tickformat=f".{decimals}f")
    fig.update_xaxes(hoverformat="%b %Y", tickformat="%b\n%Y")
    fig.add_hline(y=reference, line=dict(color=t["axis"], width=1.5))
    fig.add_annotation(x=0, xref="paper", y=reference, text=reference_label, showarrow=False,
                       xanchor="left", yanchor="bottom", font=dict(size=11.5, color=t["ink_3"]))
    # end labels, nudged apart when two lines finish close together
    ends.sort(key=lambda e: e[2])
    min_gap, shift = (hi - lo + 2 * pad) * 0.085, [0.0] * len(ends)
    for i in range(1, len(ends)):
        if ends[i][2] - ends[i - 1][2] < min_gap:
            shift[i - 1] -= 7; shift[i] += 7
    for (name, xv, yv), dy in zip(ends, shift):
        fig.add_annotation(x=xv, y=yv, text=f"{name} <b>{yv:.{decimals}f}</b>", showarrow=False,
                           xanchor="left", xshift=10, yshift=dy, font=dict(size=12, color=t["ink"]))
    return fig


# ----------------------------------------------------------------------------
# 5. Milestones - baseline vs forecast date per milestone
# ----------------------------------------------------------------------------
def milestone_slip(df: pd.DataFrame, *, name: str, baseline: str, forecast: str,
                   watch_days: int = 0, late_days: int = 30, height: int | None = None) -> go.Figure:
    """Dumbbell: open circle = baseline date, filled = forecast. Slip in days is written beside
    each row, so status never depends on colour alone."""
    t = tokens()
    d = df.iloc[::-1].copy()
    d["_slip"] = (pd.to_datetime(d[forecast]) - pd.to_datetime(d[baseline])).dt.days
    s = t["status"]
    col = [s["critical"]["solid"] if v > late_days else s["warning"]["solid"] if v > watch_days
           else s["good"]["solid"] for v in d["_slip"]]
    fig = go.Figure()
    for _, r in d.iterrows():
        fig.add_scatter(x=[r[baseline], r[forecast]], y=[r[name], r[name]], mode="lines",
                        line=dict(color=t["axis"], width=2), showlegend=False, hoverinfo="skip")
    fig.add_scatter(x=d[baseline], y=d[name], name="Baseline", mode="markers",
                    marker=dict(size=10, color=t["surface"], line=dict(color=t["context"], width=2)),
                    hovertemplate="Baseline: <b>%{x|%d %b %Y}</b><extra></extra>")
    fig.add_scatter(x=[None], y=[None], name="Forecast", mode="markers",   # legend key only
                    marker=dict(size=10, color=t["ink_2"]))
    fig.add_scatter(x=d[forecast], y=d[name], name="Forecast", mode="markers+text", showlegend=False,
                    marker=dict(size=11, color=col, line=dict(color=t["surface"], width=2)),
                    text=[("On time" if v == 0 else f"{'+' if v > 0 else MINUS}{abs(v)}d") for v in d["_slip"]],
                    textposition="middle right", textfont=dict(size=12, color=t["ink_2"]),
                    cliponaxis=False,
                    hovertemplate="Forecast: <b>%{x|%d %b %Y}</b><extra></extra>")
    style(fig, height=height or max(200, 40 * len(d) + 70))
    fig.update_layout(margin=dict(r=64))
    fig.update_xaxes(showgrid=True, tickformat="%b\n%Y")
    fig.update_yaxes(showgrid=False, tickfont=dict(size=12.5, color=t["ink"]))
    return fig


# ----------------------------------------------------------------------------
# 6. Rundown - a balance being drawn down against its planned curve (contingency)
# ----------------------------------------------------------------------------
def rundown(df: pd.DataFrame, *, x: str, planned: str, actual: str, data_date=None,
            names: Mapping[str, str] | None = None, prefix: str = "", suffix: str = "",
            decimals: int = 0, height: int = 300) -> go.Figure:
    """Remaining balance over time: planned curve (grey) vs actual (blue), from zero.
    Actual below the plan line means the balance is being used faster than planned."""
    t = tokens()
    n = {"planned": "Planned", "actual": "Actual"}
    n.update(names or {})
    tmpl = "%{fullData.name}: <b>" + _num(prefix, suffix, decimals).replace("VAL", "y") + "</b><extra></extra>"
    fig = go.Figure()
    fig.add_scatter(x=df[x], y=df[planned], name=n["planned"], mode="lines",
                    line=dict(color=t["context"], width=2), hovertemplate=tmpl)
    fig.add_scatter(x=df[x], y=df[actual], name=n["actual"], mode="lines",
                    line=dict(color=t["series"][0], width=2.5), hovertemplate=tmpl)
    last = df[[x, actual]].dropna().iloc[-1]
    fig.add_scatter(x=[last[x]], y=[last[actual]], mode="markers", showlegend=False, hoverinfo="skip",
                    marker=dict(size=9, color=t["series"][0], line=dict(color=t["surface"], width=2)))
    style(fig, height=height)
    fig.update_layout(hovermode="x unified")
    fig.update_yaxes(tickprefix=prefix, ticksuffix=suffix, tickformat=",.0f", rangemode="tozero")
    fig.update_xaxes(hoverformat="%b %Y", tickformat="%b\n%Y")
    fig.add_annotation(x=last[x], y=last[actual], showarrow=False, xanchor="left", yanchor="bottom",
                       xshift=8, yshift=2, font=dict(size=12, color=t["ink"]),
                       text=f"<b>{prefix}{last[actual]:,.{decimals}f}{suffix}</b>")
    if data_date is not None:
        d = pd.Timestamp(data_date)
        fig.add_shape(type="line", x0=d, x1=d, y0=0, y1=1, yref="paper", line=dict(color=t["ink_3"], width=1))
    return fig


# ----------------------------------------------------------------------------
# 7. Monthly phasing - period values: actual to date, forecast to go, plan as a line
# ----------------------------------------------------------------------------
def monthly_bars(df: pd.DataFrame, *, x: str, actual: str, forecast: str | None = None,
                 planned: str | None = None, names: Mapping[str, str] | None = None,
                 prefix: str = "", suffix: str = "", decimals: int = 0, height: int = 300) -> go.Figure:
    """Per-period bars. Actual and forecast are the same measure, so they share one hue:
    actual solid, forecast lighter. The plan is a thin grey line on the same axis."""
    t = tokens()
    n = {"actual": "Actual", "forecast": "Forecast", "planned": "Planned"}
    n.update(names or {})
    tmpl = "%{fullData.name}: <b>" + _num(prefix, suffix, decimals).replace("VAL", "y") + "</b><extra></extra>"
    c = t["series"][0]
    fig = go.Figure()
    fig.add_bar(x=df[x], y=df[actual], name=n["actual"], marker=dict(color=c, cornerradius=3),
                hovertemplate=tmpl)
    if forecast:
        fig.add_bar(x=df[x], y=df[forecast], name=n["forecast"], hovertemplate=tmpl,
                    marker=dict(color=_mix(c, t["surface"], 0.6), cornerradius=3))
    if planned:
        fig.add_scatter(x=df[x], y=df[planned], name=n["planned"], mode="lines",
                        line=dict(color=t["context"], width=2, shape="spline", smoothing=0.6),
                        hovertemplate=tmpl)
    style(fig, height=height)
    fig.update_layout(barmode="overlay", bargap=0.3, hovermode="x unified")
    fig.update_yaxes(tickprefix=prefix, ticksuffix=suffix, tickformat=",.0f", rangemode="tozero")
    fig.update_xaxes(hoverformat="%b %Y", tickformat="%b\n%Y")
    return fig
