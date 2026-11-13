"""Synthetic data for the reference dashboard. Entirely made up - replace with the
project's real data layer. Keep this shape: plain functions that return DataFrames
or dicts, already scaled to display units, with no Streamlit or UI code in them."""
from __future__ import annotations

import numpy as np
import pandas as pd

PROJECT = "Kestrel Gas Plant Expansion"
DATA_DATE = pd.Timestamp("2026-10-31")
MONTH = pd.DateOffset(months=1)
BUDGET = 1240.0  # $M approved budget
AREAS = ["Process units", "Utilities & offsites", "Pipelines", "Buildings",
         "Electrical & instrumentation", "Owner's costs"]
CHANGE_STATUS = {"Approved": "good", "Pending": "warning", "In dispute": "critical", "Rejected": "neutral"}


def _logistic(n: int, mid: float, k: float) -> np.ndarray:
    x = np.arange(n)
    y = 1 / (1 + np.exp(-k * (x - mid)))
    return (y - y[0]) / (y[-1] - y[0])


def s_curve() -> pd.DataFrame:
    """Monthly cumulative $M: planned (PV), earned (EV), actual (AC), forecast."""
    months = pd.date_range("2025-01-31", "2027-12-31", freq="ME")
    n = len(months)
    planned = BUDGET * _logistic(n, mid=19.8, k=0.24)
    i = int(np.searchsorted(months, DATA_DATE))          # index of the data date
    earned = np.full(n, np.nan)
    earned[: i + 1] = planned[: i + 1] * np.linspace(1.0, 0.927, i + 1)
    actual = np.full(n, np.nan)
    actual[: i + 1] = earned[: i + 1] * np.linspace(1.0, 1.052, i + 1)
    forecast = np.full(n, np.nan)
    tail = _logistic(n - i + 3, mid=(n - i) / 2.4, k=0.32)[: n - i]
    forecast[i:] = earned[i] + (BUDGET - earned[i]) * tail / tail[-1]
    return pd.DataFrame({"month": months, "planned": planned, "earned": earned,
                         "actual": actual, "forecast": forecast})


def summary() -> dict:
    df = s_curve()
    row = df[df["month"] == DATA_DATE].iloc[0]
    pv, ev, ac = row["planned"], row["earned"], row["actual"]
    eac = 1286.0
    return {
        "budget": BUDGET, "eac": eac, "vac": BUDGET - eac,
        "pv": pv, "ev": ev, "ac": ac,
        "cpi": ev / ac, "spi": ev / pv,
        "pct_complete": ev / BUDGET, "pct_planned": pv / BUDGET,
        "contingency_total": 110.0, "contingency_left": 58.0,
    }


def index_history() -> pd.DataFrame:
    df = s_curve().dropna(subset=["actual"]).iloc[5:]
    rng = np.random.default_rng(7)
    wobble = lambda: np.r_[rng.normal(0, 0.006, len(df) - 1), 0.0]   # last point = reported value
    return pd.DataFrame({"month": df["month"],
                         "cpi": df["earned"] / df["actual"] + wobble(),
                         "spi": df["earned"] / df["planned"] + wobble()})


def kpi_history() -> dict:
    """Last 12 reporting periods for the KPI sparklines."""
    rng = np.random.default_rng(3)
    df = s_curve().dropna(subset=["actual"]).tail(12)
    return {
        "eac": (1240 + np.linspace(4, 46, 12) + rng.normal(0, 2.5, 12)).tolist(),
        "progress": (df["earned"] / BUDGET).tolist(),
        "contingency": (110 - np.linspace(18, 52, 12) - rng.normal(0, 1.5, 12).cumsum() * 0.3).tolist(),
    }


def area_variance() -> pd.DataFrame:
    """Forecast at completion minus budget, by area, $M (positive = over budget)."""
    return pd.DataFrame({
        "area": ["Process units", "Utilities & offsites", "Pipelines", "Buildings",
                 "Electrical & instrumentation", "Owner's costs"],
        "variance": [31.4, 12.8, -6.2, 3.1, 9.6, -4.7],
    })


def eac_bridge() -> list[tuple[str, float, str]]:
    return [("Approved budget", 1240.0, "total"), ("Approved changes", 18.0, "delta"),
            ("Pending changes", 14.0, "delta"), ("Productivity", 21.0, "delta"),
            ("Material savings", -7.0, "delta"), ("Forecast at completion", 0.0, "total")]


def discipline_progress() -> list[dict]:
    return [
        {"label": "Engineering", "actual": 0.96, "planned": 0.97},
        {"label": "Procurement", "actual": 0.84, "planned": 0.85},
        {"label": "Civil & structural", "actual": 0.71, "planned": 0.76},
        {"label": "Mechanical & piping", "actual": 0.37, "planned": 0.48},
        {"label": "Electrical & instrumentation", "actual": 0.21, "planned": 0.22},
        {"label": "Commissioning", "actual": 0.02, "planned": 0.02},
    ]


def milestones() -> pd.DataFrame:
    return pd.DataFrame({
        "milestone": ["Main compressor on site", "Piping 50% complete", "Substation energised",
                      "Mechanical completion", "Ready for start-up"],
        "baseline": pd.to_datetime(["2026-09-15", "2026-11-30", "2027-02-15", "2027-07-31", "2027-10-31"]),
        "forecast": pd.to_datetime(["2026-09-15", "2027-01-12", "2027-03-05", "2027-09-08", "2027-12-04"]),
    })


def change_log() -> list[dict]:
    return [
        {"id": "CR-0142", "title": "Flare header rerouting", "area": "Process units", "value": 6.4, "status": ("Pending", "warning")},
        {"id": "CR-0139", "title": "Additional piling, tank farm", "area": "Utilities & offsites", "value": 4.9, "status": ("Approved", "good")},
        {"id": "CR-0137", "title": "Control room HVAC upgrade", "area": "Buildings", "value": 1.2, "status": ("Approved", "good")},
        {"id": "CR-0133", "title": "Cable tray redesign", "area": "Electrical & instrumentation", "value": 2.7, "status": ("Rejected", "neutral")},
        {"id": "CR-0131", "title": "Compressor vendor delay claim", "area": "Process units", "value": 7.6, "status": ("In dispute", "critical")},
    ]


# ---------------------------------------------------------------------------
# App pages
# ---------------------------------------------------------------------------
def cost_activities() -> pd.DataFrame:
    """One row per cost activity, $M."""
    rows = [
        ("Process units", "Compression train", 212.0, 148.3, 196.5, 226.4, 0.66),
        ("Process units", "Gas treating unit", 168.0, 96.1, 141.0, 177.9, 0.55),
        ("Process units", "Dehydration and NGL recovery", 131.0, 71.4, 118.2, 138.1, 0.52),
        ("Utilities & offsites", "Power and steam", 96.0, 61.7, 88.0, 101.3, 0.63),
        ("Utilities & offsites", "Tank farm", 74.0, 47.9, 66.4, 78.9, 0.61),
        ("Utilities & offsites", "Flare and relief", 41.0, 19.6, 34.1, 43.6, 0.44),
        ("Pipelines", "Inlet pipeline", 88.0, 62.2, 80.5, 84.1, 0.74),
        ("Pipelines", "Export pipeline", 67.0, 44.0, 59.8, 64.7, 0.69),
        ("Buildings", "Control room and substations", 52.0, 30.8, 46.0, 54.2, 0.58),
        ("Buildings", "Workshops and warehouse", 29.0, 15.1, 24.4, 29.9, 0.51),
        ("Electrical & instrumentation", "Electrical distribution", 78.0, 33.6, 61.2, 83.9, 0.41),
        ("Electrical & instrumentation", "Instrumentation and controls", 62.0, 21.5, 44.7, 65.7, 0.33),
        ("Owner's costs", "Project management team", 86.0, 41.2, 41.2, 83.4, 0.48),
        ("Owner's costs", "Insurance and permits", 56.0, 11.2, 22.5, 53.9, 0.20),
    ]
    df = pd.DataFrame(rows, columns=["Area", "Activity", "Budget", "Actual", "Committed", "Forecast", "Progress"])
    df["Variance"] = (df["Forecast"] - df["Budget"]).round(1)
    comments = {"Compression train": "Vendor delay claim under review",
                "Electrical distribution": "Cable tray redesign, extra hours",
                "Inlet pipeline": "Material savings on line pipe"}
    df["Comment"] = df["Activity"].map(comments).fillna("")
    return df[["Area", "Activity", "Budget", "Actual", "Committed", "Forecast", "Variance", "Progress", "Comment"]]


def phasing() -> pd.DataFrame:
    """Per-month cost, $M: actual up to the data date, forecast after it, plan throughout."""
    c = s_curve()
    out = pd.DataFrame({"month": c["month"], "planned": c["planned"].diff().fillna(c["planned"])})
    out["actual"] = c["actual"].diff().fillna(c["actual"])
    out["forecast"] = c["forecast"].diff().clip(lower=0)      # months after the data date
    return out


def contingency() -> pd.DataFrame:
    months = pd.date_range("2025-01-31", "2027-12-31", freq="ME")
    n = len(months)
    planned = 110 * (1 - _logistic(n, mid=20, k=0.2))
    i = int(np.searchsorted(months, DATA_DATE))
    actual = np.full(n, np.nan)
    rng = np.random.default_rng(11)
    drift = np.clip(np.linspace(0, 1, i + 1) ** 1.4 + rng.normal(0, 0.04, i + 1), 0, None)
    drift = drift / drift[-1] * (planned[i] - 58.0)           # ends at the reported $58M
    actual[: i + 1] = planned[: i + 1] - drift
    return pd.DataFrame({"month": months, "planned": planned, "actual": actual})


def changes() -> pd.DataFrame:
    rows = [
        ("CR-0142", "Flare header rerouting", "Process units", 6.4, "Pending", "2026-10-21"),
        ("CR-0141", "Additional cathodic protection", "Pipelines", 0.9, "Pending", "2026-10-17"),
        ("CR-0139", "Additional piling, tank farm", "Utilities & offsites", 4.9, "Approved", "2026-10-06"),
        ("CR-0137", "Control room HVAC upgrade", "Buildings", 1.2, "Approved", "2026-09-28"),
        ("CR-0136", "Substation relocation", "Electrical & instrumentation", 3.8, "Approved", "2026-09-19"),
        ("CR-0133", "Cable tray redesign", "Electrical & instrumentation", 2.7, "Rejected", "2026-09-02"),
        ("CR-0131", "Compressor vendor delay claim", "Process units", 7.6, "In dispute", "2026-08-25"),
        ("CR-0128", "Warehouse racking scope", "Buildings", 0.6, "Rejected", "2026-08-11"),
        ("CR-0126", "Inlet separator upsizing", "Process units", 5.3, "Approved", "2026-07-30"),
    ]
    df = pd.DataFrame(rows, columns=["ID", "Change", "Area", "Value", "Status", "Raised"])
    df["Raised"] = pd.to_datetime(df["Raised"])
    return df


def column_mapping() -> pd.DataFrame:
    return pd.DataFrame({
        "Field": ["Posting date", "Activity code", "Amount", "Currency", "Vendor", "Document number"],
        "File column": ["Post_Date", "WBS_Element", "Amt_LC", "Curr", "Vendor_Name", "Doc_No"],
        "Required": [True, True, True, True, False, False],
    })


def import_review() -> dict:
    return {"rows": 1282, "matched": 1264, "unmatched": 18}


def unmatched_rows() -> pd.DataFrame:
    return pd.DataFrame({
        "Document": ["5100048812", "5100048846", "5100048901", "5100048977"],
        "Vendor": ["Northline Fabrication", "Halvorsen Electric", "Northline Fabrication", "Trident Survey"],
        "Activity code": ["KGP-4.2.9", "KGP-6.1.7", "KGP-4.2.9", "KGP-9.0.1"],
        "Amount": [0.21, 0.14, 0.18, 0.07],
        "Assign to activity": ["", "Electrical distribution", "", ""],
    })


def close_checklist() -> list[dict]:
    return [
        {"label": "Actuals and commitments imported", "status": "good",
         "detail": "1,264 rows applied for the period", "meta": "02 Nov"},
        {"label": "Contractor progress reports accepted", "status": "good",
         "detail": "6 of 6 submissions reviewed", "meta": "04 Nov"},
        {"label": "Forecast updated for every activity", "status": "warning",
         "detail": "2 activities still carry last month's forecast", "meta": "12 of 14"},
        {"label": "Budget, forecast and source totals reconcile", "status": "critical",
         "detail": "Imported actuals differ from the source total by $0.6M", "meta": "Blocking"},
        {"label": "Change register reviewed", "status": "good",
         "detail": "2 pending requests carried forward", "meta": "05 Nov"},
        {"label": "Period comments written", "status": "neutral",
         "detail": "Needed for the monthly report", "meta": "Not started"},
    ]
