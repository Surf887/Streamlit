"""Design tokens, global CSS and page setup.

Single source of truth for every colour, size and radius in the app.
Nothing outside this file should contain a hex colour or a font size.
Keep LIGHT / DARK in sync with .streamlit/config.toml.
"""
from __future__ import annotations

from urllib.parse import quote

import streamlit as st

FONT = "Inter, 'Segoe UI', system-ui, -apple-system, sans-serif"

# ----------------------------------------------------------------------------
# Tokens
# ----------------------------------------------------------------------------
LIGHT = {
    "mode": "light",
    # surfaces
    "bg": "#F5F6F8",          # page plane
    "surface": "#FFFFFF",     # cards
    "surface_2": "#F0F2F5",   # subtle fills, tracks, table header
    "border": "#E3E6EB",
    "border_strong": "#CBD0D8",
    "shadow": "0 1px 2px rgba(16,24,40,.05)",
    # ink
    "ink": "#111827",         # values, titles
    "ink_2": "#4B5563",       # body, secondary
    "ink_3": "#6B7280",       # labels, captions, axis ticks
    "accent": "#256ABF",
    # chart chrome
    "grid": "#E9ECF0",
    "axis": "#C9CED6",
    "context": "#9AA3B2",     # neutral series: baseline / plan / "everything else"
    # categorical series, FIXED ORDER (colour-blind validated as an ordered set)
    "series": ["#2A78D6", "#EB6834", "#1BAF7A", "#EDA100",
               "#E87BA4", "#008300", "#6250D6", "#E34948"],
    # diverging pair for signed values (variance, slip)
    "neg": "#2A78D6",         # under / favourable side
    "pos": "#E34948",         # over / unfavourable side
    # status: fg = text+icon, bg = pill fill, solid = chart mark
    "status": {
        "good":     {"fg": "#0A5F0A", "bg": "#E6F4E6", "solid": "#0CA30C"},
        "warning":  {"fg": "#7A4B00", "bg": "#FFF1CC", "solid": "#FAB219"},
        "critical": {"fg": "#A32222", "bg": "#FCE6E6", "solid": "#D03B3B"},
        "info":     {"fg": "#1C5CAB", "bg": "#E3EEFB", "solid": "#2A78D6"},
        "neutral":  {"fg": "#4B5563", "bg": "#F0F2F5", "solid": "#9AA3B2"},
    },
}

DARK = {
    "mode": "dark",
    "bg": "#0D1117",
    "surface": "#161B22",
    "surface_2": "#1F252E",
    "border": "#2A313C",
    "border_strong": "#3A4350",
    "shadow": "none",
    "ink": "#E6E9EE",
    "ink_2": "#B3BAC5",
    "ink_3": "#8B94A3",
    "accent": "#3987E5",
    "grid": "#232A34",
    "axis": "#39414D",
    "context": "#6B7482",
    "series": ["#3987E5", "#D95926", "#199E70", "#C98500",
               "#D55181", "#008300", "#9085E9", "#E66767"],
    "neg": "#3987E5",
    "pos": "#E66767",
    "status": {
        "good":     {"fg": "#5FD35F", "bg": "rgba(12,163,12,.16)",  "solid": "#0CA30C"},
        "warning":  {"fg": "#FAB219", "bg": "rgba(250,178,25,.14)", "solid": "#FAB219"},
        "critical": {"fg": "#F28B8B", "bg": "rgba(208,59,59,.22)",  "solid": "#D03B3B"},
        "info":     {"fg": "#7FB2F0", "bg": "rgba(57,135,229,.18)", "solid": "#3987E5"},
        "neutral":  {"fg": "#B3BAC5", "bg": "#1F252E", "solid": "#6B7482"},
    },
}


# Icons. st.html strips inline <svg>, so icons are CSS masks: they take the text colour
# of whatever they sit in. Add an icon here, then use <i class="uk-i uk-i-NAME"></i>.
_S = 'fill="none" stroke="black" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"'
ICONS = {
    "good": f'<circle cx="6" cy="6" r="5.25" {_S}/><path d="M3.7 6.2l1.6 1.6 3-3.4" {_S}/>',
    "warning": f'<path d="M6 1.4l4.9 8.7H1.1L6 1.4z" {_S}/><path d="M6 4.8v2.4" {_S}/><circle cx="6" cy="8.6" r=".8"/>',
    "critical": f'<circle cx="6" cy="6" r="5.25" {_S}/><path d="M4.2 4.2l3.6 3.6M7.8 4.2L4.2 7.8" {_S}/>',
    "info": f'<circle cx="6" cy="6" r="5.25" {_S}/><path d="M6 5.6v3" {_S}/><circle cx="6" cy="3.6" r=".8"/>',
    "neutral": f'<circle cx="6" cy="6" r="5.25" {_S}/><path d="M3.8 6h4.4" {_S}/>',
    "check": '<path d="M2.6 6.4l2.3 2.3 4.6-5.2" fill="none" stroke="black" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>',
    "up": '<path d="M6 2l5 8H1z"/>',
    "down": '<path d="M6 10l5-8H1z"/>',
}


def _icons_css() -> str:
    rules = []
    for name, body in ICONS.items():
        svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 12 12">{body}</svg>'
        rules.append(f'.uk-i-{name}{{--uk-i:url("data:image/svg+xml,{quote(svg)}");}}')
    return "\n".join(rules)


def mode() -> str:
    """'light' or 'dark' - follows the viewer's Streamlit theme."""
    try:
        return "dark" if st.context.theme.type == "dark" else "light"
    except Exception:  # older Streamlit: no st.context.theme
        return "light"


def tokens() -> dict:
    """Tokens for the active mode. Call inside the script run, not at import."""
    return DARK if mode() == "dark" else LIGHT


# ----------------------------------------------------------------------------
# Global CSS. Only styles ui_kit's own classes (.uk-*) plus a few stable hooks.
# ----------------------------------------------------------------------------
_CSS = """
:root{
  --uk-bg:%(bg)s; --uk-surface:%(surface)s; --uk-surface-2:%(surface_2)s;
  --uk-border:%(border)s; --uk-border-strong:%(border_strong)s; --uk-shadow:%(shadow)s;
  --uk-ink:%(ink)s; --uk-ink-2:%(ink_2)s; --uk-ink-3:%(ink_3)s; --uk-accent:%(accent)s;
  --uk-context:%(context)s;
  --uk-good-fg:%(good_fg)s; --uk-good-bg:%(good_bg)s;
  --uk-warning-fg:%(warning_fg)s; --uk-warning-bg:%(warning_bg)s;
  --uk-critical-fg:%(critical_fg)s; --uk-critical-bg:%(critical_bg)s;
  --uk-info-fg:%(info_fg)s; --uk-info-bg:%(info_bg)s;
  --uk-neutral-fg:%(neutral_fg)s; --uk-neutral-bg:%(neutral_bg)s;
  --uk-radius:10px;
}

/* page: comfortable max width, less dead space on top */
[data-testid="stMainBlockContainer"]{max-width:1480px;padding-top:2.25rem;padding-bottom:3rem;}

.uk{font-family:%(font)s;color:var(--uk-ink);line-height:1.4;-webkit-font-smoothing:antialiased;}
.uk *{box-sizing:border-box;}
.uk-num{font-variant-numeric:tabular-nums;font-feature-settings:"tnum" 1,"cv11" 1;}
.uk-i{display:inline-block;flex:none;width:12px;height:12px;background:currentColor;
  -webkit-mask:var(--uk-i) center/contain no-repeat;mask:var(--uk-i) center/contain no-repeat;}
%(icons_css)s

/* ---------- page header ---------- */
.uk-header{display:flex;align-items:flex-end;justify-content:space-between;gap:24px;flex-wrap:wrap;
  padding-bottom:16px;border-bottom:1px solid var(--uk-border);}
.uk-eyebrow{font-size:12px;font-weight:600;letter-spacing:.06em;text-transform:uppercase;color:var(--uk-ink-3);margin-bottom:4px;}
.uk-title{font-size:24px;font-weight:650;letter-spacing:-.02em;line-height:1.2;margin:0;}
.uk-subtitle{font-size:14px;color:var(--uk-ink-2);margin-top:4px;}
.uk-meta{display:flex;align-items:center;gap:24px;flex-wrap:wrap;}
.uk-meta-item{display:flex;flex-direction:column;gap:2px;}
.uk-meta-label{font-size:11.5px;color:var(--uk-ink-3);}
.uk-meta-value{font-size:13.5px;font-weight:600;}

/* ---------- section heading ---------- */
.uk-section{display:flex;align-items:baseline;gap:10px;margin:10px 0 0;}
.uk-section-title{font-size:15px;font-weight:650;letter-spacing:-.01em;}
.uk-section-caption{font-size:12.5px;color:var(--uk-ink-3);}

/* ---------- cards (st.container wrappers created by ui.card) ---------- */
[class*="st-key-ukcard-"]{background:var(--uk-surface);border:1px solid var(--uk-border)!important;
  border-radius:var(--uk-radius)!important;box-shadow:var(--uk-shadow);padding:18px 20px 16px!important;}
.uk-card-head{display:flex;align-items:flex-start;justify-content:space-between;gap:12px;}
.uk-card-title{font-size:14px;font-weight:650;letter-spacing:-.005em;}
.uk-card-caption{font-size:12.5px;color:var(--uk-ink-3);margin-top:2px;}

/* ---------- KPI cards ---------- */
.uk-kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(168px,1fr));gap:14px;}
.uk-kpi{background:var(--uk-surface);border:1px solid var(--uk-border);border-radius:var(--uk-radius);
  box-shadow:var(--uk-shadow);padding:16px 18px 14px;display:flex;flex-direction:column;min-width:0;}
.uk-kpi-label{font-size:12.5px;font-weight:500;color:var(--uk-ink-3);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
.uk-kpi-value{font-size:28px;font-weight:650;letter-spacing:-.025em;line-height:1.15;margin-top:6px;white-space:nowrap;}
.uk-kpi-unit{font-size:15px;font-weight:550;color:var(--uk-ink-3);letter-spacing:0;margin-left:3px;}
.uk-kpi-foot{display:flex;align-items:center;gap:8px;margin-top:8px;font-size:12.5px;color:var(--uk-ink-3);min-height:22px;flex-wrap:wrap;}
.uk-kpi-spark{margin-top:auto;padding-top:12px;}
.uk-kpi-spark img{display:block;width:100%%;height:30px;}

/* ---------- delta chip ---------- */
.uk-delta{display:inline-flex;align-items:center;gap:3px;font-size:12px;font-weight:600;
  padding:1px 6px 1px 5px;border-radius:5px;white-space:nowrap;}
.uk-delta .uk-i{width:8px;height:8px;}
.uk-tone-good{color:var(--uk-good-fg);background:var(--uk-good-bg);}
.uk-tone-bad{color:var(--uk-critical-fg);background:var(--uk-critical-bg);}
.uk-tone-warn{color:var(--uk-warning-fg);background:var(--uk-warning-bg);}
.uk-tone-neutral{color:var(--uk-neutral-fg);background:var(--uk-neutral-bg);}

/* ---------- status pill (always icon + label, never colour alone) ---------- */
.uk-pill{display:inline-flex;align-items:center;gap:5px;font-size:12px;font-weight:600;line-height:1;
  padding:4px 9px 4px 7px;border-radius:999px;white-space:nowrap;}
.uk-pill-good{color:var(--uk-good-fg);background:var(--uk-good-bg);}
.uk-pill-warning{color:var(--uk-warning-fg);background:var(--uk-warning-bg);}
.uk-pill-critical{color:var(--uk-critical-fg);background:var(--uk-critical-bg);}
.uk-pill-info{color:var(--uk-info-fg);background:var(--uk-info-bg);}
.uk-pill-neutral{color:var(--uk-neutral-fg);background:var(--uk-neutral-bg);}

/* ---------- progress list (actual bar + planned tick) ---------- */
.uk-prog{display:flex;flex-direction:column;gap:14px;padding-top:4px;}
.uk-prog-row{display:grid;grid-template-columns:1fr auto;column-gap:12px;row-gap:6px;align-items:baseline;}
.uk-prog-label{font-size:13px;font-weight:500;color:var(--uk-ink);}
.uk-prog-val{font-size:13px;font-weight:600;}
.uk-prog-val small{font-size:12px;font-weight:500;color:var(--uk-ink-3);margin-left:6px;}
.uk-prog-track{grid-column:1 / -1;position:relative;height:8px;border-radius:4px;background:var(--uk-surface-2);}
.uk-prog-fill{position:absolute;left:0;top:0;bottom:0;border-radius:4px;background:var(--uk-accent);}
.uk-prog-fill.is-behind{background:var(--uk-critical-fg);}
.uk-prog-fill.is-watch{background:%(watch_bar)s;}
.uk-prog-tick{position:absolute;top:-4px;bottom:-4px;width:2px;border-radius:1px;background:var(--uk-ink);}
.uk-prog-legend{display:flex;gap:16px;font-size:12px;color:var(--uk-ink-3);margin-top:2px;}
.uk-prog-legend i{display:inline-block;vertical-align:middle;margin-right:6px;}
.uk-prog-legend .bar{width:14px;height:6px;border-radius:3px;background:var(--uk-accent);}
.uk-prog-legend .tick{width:2px;height:12px;background:var(--uk-ink);}

/* ---------- HTML table (small tables with pills) ---------- */
.uk-table{width:100%%;border-collapse:collapse;font-size:13px;}
.uk-table th{text-align:left;font-size:12px;font-weight:600;color:var(--uk-ink-3);padding:8px 12px 8px 0;
  border-bottom:1px solid var(--uk-border);white-space:nowrap;}
.uk-table td{padding:10px 12px 10px 0;border-bottom:1px solid var(--uk-border);color:var(--uk-ink-2);vertical-align:middle;}
.uk-table tr:last-child td{border-bottom:0;}
.uk-table td:first-child{color:var(--uk-ink);font-weight:500;}
.uk-table .r{text-align:right;padding-right:0;padding-left:12px;}
.uk-table th.r{padding-right:0;}

/* ---------- banner (page-level notice) ---------- */
.uk-banner{display:flex;align-items:flex-start;gap:10px;padding:10px 14px;border-radius:8px;font-size:13px;line-height:1.45;}
.uk-banner .uk-i{width:14px;height:14px;margin-top:2px;}
.uk-banner b{font-weight:650;margin-right:6px;}
.uk-banner-good{color:var(--uk-good-fg);background:var(--uk-good-bg);}
.uk-banner-warning{color:var(--uk-warning-fg);background:var(--uk-warning-bg);}
.uk-banner-critical{color:var(--uk-critical-fg);background:var(--uk-critical-bg);}
.uk-banner-info{color:var(--uk-info-fg);background:var(--uk-info-bg);}
.uk-banner-neutral{color:var(--uk-neutral-fg);background:var(--uk-neutral-bg);}

/* ---------- stepper ---------- */
.uk-steps{display:flex;align-items:center;gap:0;list-style:none;margin:0!important;padding:2px 0!important;}
.uk-steps li{margin:0!important;padding:0;}
.uk-step{display:flex;align-items:center;gap:8px;font-size:13px;font-weight:500;color:var(--uk-ink-3);white-space:nowrap;}
.uk-step-dot{display:inline-flex;align-items:center;justify-content:center;width:22px;height:22px;border-radius:50%%;
  font-size:11.5px;font-weight:650;border:1.5px solid var(--uk-border-strong);color:var(--uk-ink-3);background:var(--uk-surface);}
.uk-step.is-current{color:var(--uk-ink);font-weight:650;}
.uk-step.is-current .uk-step-dot{border-color:var(--uk-accent);background:var(--uk-accent);color:#fff;}
.uk-step.is-done{color:var(--uk-ink-2);}
.uk-step.is-done .uk-step-dot{border-color:var(--uk-accent);color:var(--uk-accent);}
.uk-step.is-done .uk-step-dot .uk-i{width:11px;height:11px;}
.uk-step-line{flex:1 1 24px;min-width:16px;max-width:72px;height:1.5px;background:var(--uk-border-strong);margin:0 12px;}
.uk-step-line.is-done{background:var(--uk-accent);}

/* ---------- stat strip (compact totals above a table) ---------- */
.uk-stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));background:var(--uk-surface);
  border:1px solid var(--uk-border);border-radius:var(--uk-radius);box-shadow:var(--uk-shadow);overflow:hidden;}
.uk-stat{display:flex;flex-direction:column;gap:3px;padding:12px 18px;box-shadow:-1px 0 0 var(--uk-border);min-width:0;}
.uk-stat-label{font-size:12px;font-weight:500;color:var(--uk-ink-3);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
.uk-stat-value{font-size:18px;font-weight:650;letter-spacing:-.015em;line-height:1.25;white-space:nowrap;}
.uk-stat-note{font-size:12px;color:var(--uk-ink-3);white-space:nowrap;}
.uk-stat-note.is-good{color:var(--uk-good-fg);} .uk-stat-note.is-bad{color:var(--uk-critical-fg);}
.uk-stat-note.is-warn{color:var(--uk-warning-fg);}

/* ---------- checklist ---------- */
.uk-check{list-style:none;margin:0!important;padding:0!important;}
.uk-check li{display:flex;align-items:flex-start;gap:12px;margin:0!important;padding:11px 0;border-bottom:1px solid var(--uk-border);}
.uk-check li:last-child{border-bottom:0;padding-bottom:2px;}
.uk-check-ico{display:inline-flex;align-items:center;justify-content:center;width:20px;height:20px;border-radius:50%%;flex:none;margin-top:1px;}
.uk-check-ico .uk-i{width:12px;height:12px;}
.uk-check-ico.is-good{color:var(--uk-good-fg);background:var(--uk-good-bg);}
.uk-check-ico.is-warning{color:var(--uk-warning-fg);background:var(--uk-warning-bg);}
.uk-check-ico.is-critical{color:var(--uk-critical-fg);background:var(--uk-critical-bg);}
.uk-check-ico.is-neutral,.uk-check-ico.is-info{color:var(--uk-neutral-fg);background:var(--uk-neutral-bg);}
.uk-check-body{flex:1;min-width:0;}
.uk-check-title{font-size:13.5px;font-weight:550;color:var(--uk-ink);}
.uk-check-detail{font-size:12.5px;color:var(--uk-ink-3);margin-top:1px;}
.uk-check-meta{font-size:12.5px;color:var(--uk-ink-3);white-space:nowrap;margin-top:2px;}

/* ---------- key / value facts ---------- */
.uk-kv{display:grid;grid-template-columns:repeat(var(--uk-kv-cols,2),minmax(0,1fr));gap:14px 24px;}
.uk-kv-item{display:flex;flex-direction:column;gap:2px;min-width:0;}
.uk-kv-label{font-size:12px;color:var(--uk-ink-3);}
.uk-kv-value{font-size:13.5px;font-weight:550;color:var(--uk-ink);overflow-wrap:anywhere;}

/* ---------- sidebar: app name and context sit above the navigation ---------- */
[data-testid="stSidebarContent"]{display:flex;flex-direction:column;}
[data-testid="stSidebarUserContent"]{order:1;padding-top:0;padding-bottom:.5rem;}
[data-testid="stSidebarNav"]{order:2;}
[data-testid="stSidebarNavSeparator"]{display:none;}
.uk-side{display:flex;flex-direction:column;gap:10px;padding:2px 0 6px;}
.uk-side-app{font-size:15px;font-weight:700;letter-spacing:-.01em;color:var(--uk-ink);}
.uk-side-box{border:1px solid var(--uk-border);border-radius:8px;padding:10px 12px;display:flex;flex-direction:column;gap:8px;background:var(--uk-surface);}
.uk-side-label{font-size:11px;font-weight:600;letter-spacing:.05em;text-transform:uppercase;color:var(--uk-ink-3);}
.uk-side-value{font-size:13px;font-weight:600;color:var(--uk-ink);line-height:1.3;}

/* ---------- empty state ---------- */
.uk-empty{display:flex;flex-direction:column;align-items:center;justify-content:center;gap:4px;
  padding:36px 16px;color:var(--uk-ink-3);font-size:13px;text-align:center;}
.uk-empty b{color:var(--uk-ink-2);font-size:14px;font-weight:600;}
"""


def css() -> str:
    t = tokens()
    flat = {k: v for k, v in t.items() if isinstance(v, str)}
    for name, s in t["status"].items():
        flat[f"{name}_fg"], flat[f"{name}_bg"] = s["fg"], s["bg"]
    flat["font"] = FONT
    flat["icons_css"] = _icons_css()
    flat["watch_bar"] = "#E09A00" if t["mode"] == "light" else t["status"]["warning"]["solid"]
    return _CSS % flat


def setup_page(title: str, *, icon: str | None = None, sidebar: str = "auto") -> None:
    """First Streamlit call of the app: wide layout + design-system CSS.
    Single-file app: call it at the top of that file. Multi-page app (st.navigation):
    call it once in the entry file, before st.navigation - not again in each page."""
    st.set_page_config(page_title=title, page_icon=icon, layout="wide",
                       initial_sidebar_state=sidebar)
    st.html(f"<style>{css()}</style>")
