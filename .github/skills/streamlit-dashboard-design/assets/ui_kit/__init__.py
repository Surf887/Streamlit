"""ui_kit - the app design system. Import as:  import ui_kit as ui

App code uses only what is exported here. If something is missing, add a
component to this package (see the skill's references/design-system.md)
instead of writing HTML/CSS in a page.
"""
from .theme import setup_page, tokens, mode
from .components import (
    # page structure
    page_header, section, card, banner, stepper, sidebar_context, empty_state,
    # numbers and status
    kpi_row, kpi_card, stat_strip, pill, progress_list, checklist, key_value,
    # tables
    status_table, grid, editor, col_money, col_number, col_pct, col_progress, col_text,
    # building blocks and formatters
    pill_html, delta_html, sparkline_img, money, pct, signed,
)
from .charts import (
    show, style, s_curve, variance_bars, bridge, index_trend, milestone_slip,
    rundown, monthly_bars,
)

__all__ = [
    "setup_page", "tokens", "mode",
    "page_header", "section", "card", "banner", "stepper", "sidebar_context", "empty_state",
    "kpi_row", "kpi_card", "stat_strip", "pill", "progress_list", "checklist", "key_value",
    "status_table", "grid", "editor", "col_money", "col_number", "col_pct", "col_progress", "col_text",
    "pill_html", "delta_html", "sparkline_img", "money", "pct", "signed",
    "show", "style", "s_curve", "variance_bars", "bridge", "index_trend", "milestone_slip",
    "rundown", "monthly_bars",
]
