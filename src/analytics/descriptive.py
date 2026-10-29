"""
SPORTZA Descriptive Statistics & Squad Analytics Module
"""
from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd


def compute_squad_summary(wellness_df: pd.DataFrame) -> dict[str, Any]:
    """Compute squad-level aggregates (mean, median, IQR, std) across wellness metrics."""
    if wellness_df.empty:
        return {}

    metric_cols = [
        "readiness", "fatigue", "mood", "sleep_duration_hours",
        "sleep_quality", "soreness", "stress"
    ]
    summary = {}
    for col in metric_cols:
        if col in wellness_df.columns:
            s = wellness_df[col].dropna()
            if not s.empty:
                q25 = float(np.percentile(s, 25))
                q75 = float(np.percentile(s, 75))
                summary[col] = {
                    "count": len(s),
                    "mean": round(float(s.mean()), 2),
                    "median": round(float(s.median()), 2),
                    "std": round(float(s.std()), 2) if len(s) > 1 else 0.0,
                    "q25": round(q25, 2),
                    "q75": round(q75, 2),
                    "iqr": round(q75 - q25, 2),
                    "min": round(float(s.min()), 2),
                    "max": round(float(s.max()), 2),
                }
    return summary


def compute_team_comparison(
    wellness_df: pd.DataFrame,
    sessions_df: pd.DataFrame,
) -> dict[str, Any]:
    """Compare distributions between Team A and Team B."""
    out = {"wellness": {}, "sessions": {}}
    
    # Process wellness by team
    if not wellness_df.empty and "player_id" in wellness_df.columns:
        w = wellness_df.copy()
        w["team"] = w["player_id"].apply(lambda x: "Team A" if "TeamA" in str(x) else "Team B")
        
        for col in ["readiness", "fatigue", "soreness", "stress", "sleep_duration_hours"]:
            if col in w.columns:
                g = w.groupby("team")[col].agg(["count", "mean", "median", "std"]).to_dict("index")
                out["wellness"][col] = g

    # Process sessions by team
    if not sessions_df.empty and "player_id" in sessions_df.columns:
        s = sessions_df.copy()
        s["team"] = s["player_id"].apply(lambda x: "Team A" if "TeamA" in str(x) else "Team B")
        s["session_date"] = pd.to_datetime(s["session_date"])
        s["year"] = s["session_date"].dt.year
        
        counts = s.groupby(["player_id", "team", "year"]).size().reset_index(name="session_count")
        annual = counts.groupby(["team", "year"])["session_count"].agg(
            ["count", "mean", "median", "std", "min", "max"]
        ).to_dict("index")
        out["sessions"]["annual_per_player"] = annual

    return out


def compute_report_counts(
    wellness_df: pd.DataFrame,
    sessions_df: pd.DataFrame,
    injury_df: pd.DataFrame | None = None,
    illness_df: pd.DataFrame | None = None,
    game_df: pd.DataFrame | None = None,
) -> dict[str, Any]:
    """Calculate totals, unique athletes, and date ranges across all report types."""
    counts = {
        "wellness_reports": len(wellness_df) if wellness_df is not None else 0,
        "training_sessions": len(sessions_df) if sessions_df is not None else 0,
        "injury_reports": len(injury_df) if injury_df is not None else 0,
        "illness_reports": len(illness_df) if illness_df is not None else 0,
        "game_reports": len(game_df) if game_df is not None else 0,
    }
    
    # Player count
    all_players = set()
    for df in [wellness_df, sessions_df, injury_df, illness_df, game_df]:
        if df is not None and not df.empty and "player_id" in df.columns:
            all_players.update(df["player_id"].dropna().unique())
            
    counts["unique_players"] = len(all_players)
    counts["players_list"] = sorted(all_players)
    
    # Date range
    if wellness_df is not None and not wellness_df.empty and "date" in wellness_df.columns:
        counts["start_date"] = str(wellness_df["date"].min())
        counts["end_date"] = str(wellness_df["date"].max())
    else:
        counts["start_date"] = None
        counts["end_date"] = None
        
    return counts
