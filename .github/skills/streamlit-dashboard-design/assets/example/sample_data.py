"""Synthetic data for the reference dashboard. Entirely made up - replace with the
project's real data layer. Keep this shape: plain functions that return DataFrames
or dicts, already scaled to display units, with no Streamlit or UI code in them."""
from __future__ import annotations

import numpy as np
import pandas as pd

DATA_DATE = pd.Timestamp("2026-10-31")
BUDGET = 1240.0  # $M approved budget


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
