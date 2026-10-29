"""
SPORTZA Workload Feature Engineering Module

Calculates training load metrics following sports science standards (Foster et al.,
Impellizzeri et al., Gabbett et al.):
- session sRPE = duration_minutes * RPE
- daily load = sum of session sRPE per day
- acute training load (ATL) = 7-day rolling average of daily load
- chronic training load (CTL) = 28-day or 42-day rolling average of daily load
- acute:chronic workload ratio (ACWR) = ATL / CTL
- monotony = 7-day mean daily load / 7-day standard deviation
- strain = 7-day total load * monotony
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def compute_srpe(duration_minutes: float | pd.Series, rpe: float | pd.Series) -> float | pd.Series:
    """Calculate session Rating of Perceived Exertion (sRPE = duration * RPE).
    
    Negative or invalid values are clamped or treated safely.
    """
    if isinstance(duration_minutes, (pd.Series, np.ndarray)) or isinstance(rpe, (pd.Series, np.ndarray)):
        dur = pd.Series(duration_minutes).clip(lower=0.0)
        r = pd.Series(rpe).clip(lower=0.0, upper=10.0)
        return (dur * r).astype(float)
    
    d = max(0.0, float(duration_minutes)) if pd.notna(duration_minutes) else 0.0
    r = min(10.0, max(0.0, float(rpe))) if pd.notna(rpe) else 0.0
    return float(d * r)


def compute_daily_load(sessions_df: pd.DataFrame, date_col: str = "session_date", srpe_col: str = "srpe") -> pd.DataFrame:
    """Aggregate individual sessions to daily training load per player."""
    if sessions_df.empty:
        return pd.DataFrame(columns=["player_id", "date", "daily_load"])
    
    df = sessions_df.copy()
    if srpe_col not in df.columns:
        df[srpe_col] = compute_srpe(df["duration_minutes"], df["rpe"])
        
    df["date"] = pd.to_datetime(df[date_col])
    daily = (
        df.groupby(["player_id", "date"])[srpe_col]
        .sum()
        .reset_index()
        .rename(columns={srpe_col: "daily_load"})
    )
    return daily


def compute_rolling_load(daily_loads: pd.Series, window: int = 7) -> pd.Series:
    """Compute rolling sum of load over specified window days."""
    if daily_loads.empty:
        return pd.Series(dtype=float)
    return daily_loads.rolling(window=window, min_periods=1).sum()


def compute_atl(daily_loads: pd.Series, window: int = 7) -> pd.Series:
    """Compute Acute Training Load (ATL) as 7-day rolling average."""
    if daily_loads.empty:
        return pd.Series(dtype=float)
    return daily_loads.rolling(window=window, min_periods=1).mean()


def compute_ctl(daily_loads: pd.Series, window: int = 28) -> pd.Series:
    """Compute Chronic Training Load (CTL) as 28-day or 42-day rolling average."""
    if daily_loads.empty:
        return pd.Series(dtype=float)
    return daily_loads.rolling(window=window, min_periods=1).mean()


def compute_acwr(atl: pd.Series, ctl: pd.Series, min_ctl: float = 1.0) -> pd.Series:
    """Compute Acute:Chronic Workload Ratio (ACWR = ATL / CTL).
    
    Avoids division by zero or near-zero CTL by masking with NaN when CTL < min_ctl.
    """
    if atl.empty or ctl.empty:
        return pd.Series(dtype=float)
    
    valid_ctl = ctl.where(ctl >= min_ctl, np.nan)
    ratio = atl / valid_ctl
    return ratio.round(3)


def compute_monotony(daily_loads: pd.Series, window: int = 7) -> pd.Series:
    """Compute training monotony = rolling_mean / rolling_std over window.
    
    High monotony (>2.0) coupled with high strain signals inadequate recovery.
    """
    if daily_loads.empty:
        return pd.Series(dtype=float)
    
    r_mean = daily_loads.rolling(window=window, min_periods=3).mean()
    r_std = daily_loads.rolling(window=window, min_periods=3).std(ddof=1)
    
    # Avoid zero division
    valid_std = r_std.where(r_std > 1e-4, np.nan)
    monotony = r_mean / valid_std
    return monotony.round(2)


def compute_strain(weekly_load: pd.Series, monotony: pd.Series) -> pd.Series:
    """Compute training strain = weekly_load * monotony."""
    if weekly_load.empty or monotony.empty:
        return pd.Series(dtype=float)
    return (weekly_load * monotony).round(1)
