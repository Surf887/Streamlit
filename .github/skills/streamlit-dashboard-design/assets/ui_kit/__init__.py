"""ui_kit - the dashboard design system. Import as:  import ui_kit as ui

App code uses only what is exported here. If something is missing, add a
component to this package (see the skill's references/design-system.md)
instead of writing HTML/CSS in a page.
"""
from .theme import setup_page, tokens, mode
from .components import (
    page_header, section, kpi_row, kpi_card, card, pill, progress_list,
    status_table, empty_state, pill_html, delta_html, sparkline_img,
    money, pct, signed,
)
from .charts import (
    show, style, s_curve, variance_bars, bridge, index_trend, milestone_slip,
)

__all__ = [
    "setup_page", "tokens", "mode",
    "page_header", "section", "kpi_row", "kpi_card", "card", "pill", "progress_list",
    "status_table", "empty_state", "pill_html", "delta_html", "sparkline_img",
    "money", "pct", "signed",
    "show", "style", "s_curve", "variance_bars", "bridge", "index_trend", "milestone_slip",
]
