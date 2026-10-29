"""
SPORTZA Wellness Feature Engineering Module

Computes athlete-specific baseline deviations, rolling statistics,
and data sufficiency metrics.
"""
from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from src.config import SCALE_DIRECTION


def compute_personal_baseline(
    series: pd.Series,
    window: int = 28,
    min_obs: int = 7,
    statistic: str = "mean",
) -> pd.Series:
    """Compute rolling personal baseline for a wellness metric.
    
    Parameters
    ----------
    series : pd.Series
        Time-indexed or chronologically ordered values for a single player.
    window : int
        Rolling window in days (default: 28).
    min_obs : int
        Minimum number of non-null observations required (default: 7).
    statistic : str
        'mean' or 'median'.
    """
    if series.empty:
        return pd.Series(dtype=float)
    
    rolling = series.rolling(window=window, min_periods=min_obs)
    if statistic == "median":
        return rolling.median().round(2)
    return rolling.mean().round(2)


def compute_deviation_from_baseline(
    values: pd.Series,
    baseline: pd.Series,
    as_zscore: bool = False,
    std_series: pd.Series | None = None,
) -> pd.Series:
    """Compute difference between current observed value and personal baseline.
    
    If as_zscore=True and std_series is provided, computes (val - base) / std.
    """
    if values.empty or baseline.empty:
        return pd.Series(dtype=float)
    
    diff = values - baseline
    if as_zscore and std_series is not None and not std_series.empty:
        valid_std = std_series.where(std_series > 1e-4, np.nan)
        return (diff / valid_std).round(2)
    return diff.round(2)


def compute_data_coverage(
    series: pd.Series,
    window: int = 28,
) -> pd.Series:
    """Compute fraction of non-null days in the given rolling window."""
    if series.empty:
        return pd.Series(dtype=float)
    
    is_valid = series.notna().astype(float)
    coverage = is_valid.rolling(window=window, min_periods=1).mean()
    return coverage.round(3)


def get_wellness_summary(wellness_df: pd.DataFrame, player_id: str) -> dict[str, Any]:
    """Return summary statistics of wellness metrics for an individual player."""
    pdf = wellness_df[wellness_df["player_id"] == player_id].copy()
    if pdf.empty:
        return {
            "player_id": player_id,
            "total_reports": 0,
            "date_range": (None, None),
            "metrics": {},
        }
    
    pdf = pdf.sort_values("date")
    metric_cols = [
        "readiness", "fatigue", "mood", "sleep_duration_hours",
        "sleep_quality", "soreness", "stress"
    ]
    
    metrics_summary = {}
    for col in metric_cols:
        if col in pdf.columns:
            s = pdf[col].dropna()
            metrics_summary[col] = {
                "count": int(s.count()),
                "mean": float(s.mean()) if len(s) else None,
                "median": float(s.median()) if len(s) else None,
                "std": float(s.std()) if len(s) > 1 else None,
                "min": float(s.min()) if len(s) else None,
                "max": float(s.max()) if len(s) else None,
                "direction": SCALE_DIRECTION.get(col, "unknown"),
            }
            
    return {
        "player_id": player_id,
        "total_reports": len(pdf),
        "date_range": (str(pdf["date"].min()), str(pdf["date"].max())),
        "metrics": metrics_summary,
    }
