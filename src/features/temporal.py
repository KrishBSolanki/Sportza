"""
SPORTZA Temporal Feature Pipeline Module

Constructs a strictly point-in-time aligned athlete-date feature table
preventing any future leakage for forecasting and decision support.
"""
from __future__ import annotations

import pandas as pd

from src.features.wellness import (
    compute_data_coverage,
    compute_deviation_from_baseline,
    compute_personal_baseline,
)
from src.features.workload import (
    compute_acwr,
    compute_atl,
    compute_ctl,
    compute_daily_load,
    compute_monotony,
    compute_rolling_load,
    compute_strain,
)


def build_athlete_date_features(
    wellness_df: pd.DataFrame,
    sessions_df: pd.DataFrame,
    injury_df: pd.DataFrame | None = None,
    illness_df: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Merge and engineer features indexed by (player_id, date) with strict chronological order.
    
    Guarantees no future leakage: rolling statistics, baselines, and lags
    only incorporate information available on or prior to the evaluated date.
    """
    if wellness_df.empty:
        return pd.DataFrame()
    
    w_df = wellness_df.copy()
    w_df["date"] = pd.to_datetime(w_df["date"])
    
    # Process training sessions to daily loads
    daily_loads = compute_daily_load(sessions_df, date_col="session_date") if not sessions_df.empty else pd.DataFrame(columns=["player_id", "date", "daily_load"])
    if not daily_loads.empty:
        daily_loads["date"] = pd.to_datetime(daily_loads["date"])
    
    # Ensure all player dates are represented
    players = w_df["player_id"].unique()
    dfs_per_player = []
    
    for pid in players:
        p_well = w_df[w_df["player_id"] == pid].sort_values("date").set_index("date")
        
        # Complete date range for continuous rolling calculations
        full_dates = pd.date_range(p_well.index.min(), p_well.index.max(), freq="D")
        p_grid = pd.DataFrame(index=full_dates)
        p_grid.index.name = "date"
        p_grid["player_id"] = pid
        
        # Join wellness
        p_full = p_grid.join(p_well[[c for c in p_well.columns if c != "player_id"]])
        
        # Join daily workload
        if not daily_loads.empty:
            p_load = daily_loads[daily_loads["player_id"] == pid].set_index("date")[["daily_load"]]
            p_full = p_full.join(p_load)
            p_full["daily_load"] = p_full["daily_load"].fillna(0.0)
        else:
            p_full["daily_load"] = 0.0
            
        # Compute workload rolling indicators
        p_full["weekly_load"] = compute_rolling_load(p_full["daily_load"], window=7)
        p_full["atl"] = compute_atl(p_full["daily_load"], window=7)
        p_full["ctl_28"] = compute_ctl(p_full["daily_load"], window=28)
        p_full["acwr"] = compute_acwr(p_full["atl"], p_full["ctl_28"])
        p_full["monotony"] = compute_monotony(p_full["daily_load"], window=7)
        p_full["strain"] = compute_strain(p_full["weekly_load"], p_full["monotony"])
        
        # Compute wellness baselines & deviations
        wellness_cols = ["readiness", "fatigue", "mood", "sleep_duration_hours", "sleep_quality", "soreness", "stress"]
        for w_col in wellness_cols:
            if w_col in p_full.columns:
                p_full[f"{w_col}_base28"] = compute_personal_baseline(p_full[w_col], window=28, min_obs=7)
                p_full[f"{w_col}_dev"] = compute_deviation_from_baseline(p_full[w_col], p_full[f"{w_col}_base28"])
                p_full[f"{w_col}_cov28"] = compute_data_coverage(p_full[w_col], window=28)
                p_full[f"{w_col}_cov7"] = compute_data_coverage(p_full[w_col], window=7)
                
                # 1-day lag (prior observation)
                p_full[f"{w_col}_lag1"] = p_full[w_col].shift(1)
        
        # Injury and illness events
        p_full["reported_injury_today"] = 0
        if injury_df is not None and not injury_df.empty:
            p_inj = injury_df[injury_df["player_id"] == pid].copy()
            if not p_inj.empty:
                date_col = "event_date" if "event_date" in p_inj.columns else "date"
                inj_dates = pd.to_datetime(p_inj[date_col]).dt.normalize().unique()
                p_full["reported_injury_today"] = p_full.index.isin(inj_dates).astype(int)
        
        p_full["reported_illness_today"] = 0
        if illness_df is not None and not illness_df.empty:
            p_ill = illness_df[illness_df["player_id"] == pid].copy()
            if not p_ill.empty:
                date_col = "event_date" if "event_date" in p_ill.columns else "date"
                ill_dates = pd.to_datetime(p_ill[date_col]).dt.normalize().unique()
                p_full["reported_illness_today"] = p_full.index.isin(ill_dates).astype(int)
                
        # Target for next-day readiness forecasting (shift -1 strictly aligned)
        if "readiness" in p_full.columns:
            p_full["target_next_day_readiness"] = p_full["readiness"].shift(-1)
            
        dfs_per_player.append(p_full.reset_index())
        
    result_df = pd.concat(dfs_per_player, ignore_index=True)
    return result_df
