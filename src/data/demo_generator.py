"""
Synthetic demo-data generator for the SPORTZA platform.

Generates two years (2020-01-01 → 2021-12-31) of realistic but entirely
synthetic data for 20 players across two teams, with deterministic
reproducibility via ``seed=42``.

Public API
----------
generate_demo_data() -> dict[str, pd.DataFrame]
    Keys: wellness_daily, training_sessions, injury_events,
          illness_events, game_performance.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from src.config import SPORTZA_RANDOM_SEED
from src.features.workload import (
    compute_acwr,
    compute_atl,
    compute_ctl,
    compute_monotony,
    compute_strain,
)

# ── Constants ────────────────────────────────────────────────────────────────

_TEAMS: list[str] = ["TeamA", "TeamB"]
_PLAYERS_PER_TEAM: int = 10
_DATE_START: str = "2020-01-01"
_DATE_END: str = "2021-12-31"
_MISSINGNESS_RATE: float = 0.15

_SESSION_TYPES: list[str] = ["team", "individual", "competition"]
_BODY_LOCATIONS: list[str] = [
    "left_knee", "right_knee", "left_ankle", "right_ankle",
    "left_hamstring", "right_hamstring", "lower_back", "hip",
    "groin", "left_calf", "right_calf",
]
_SEVERITIES: list[str] = ["minor", "major"]
_SYMPTOMS: list[str] = ["headache", "sore_throat", "fever", "fatigue", "cough"]

_SOURCE_DATASET: str = "synthetic_demo"
_SOURCE_FILE: str = "demo_generator"


# ── Helpers ──────────────────────────────────────────────────────────────────

def _player_ids() -> list[str]:
    """Return a sorted list of 20 canonical player IDs."""
    ids: list[str] = []
    for team in _TEAMS:
        for i in range(1, _PLAYERS_PER_TEAM + 1):
            ids.append(f"{team}_P{i:02d}")
    return sorted(ids)


def _generate_wellness(
    rng: np.random.Generator,
    players: list[str],
    dates: pd.DatetimeIndex,
) -> pd.DataFrame:
    """Generate the *wellness_daily* table."""
    rows: list[dict[str, Any]] = []
    for pid in players:
        # per-player baseline offsets for realism
        base_readiness = rng.uniform(5, 8)
        base_fatigue = rng.uniform(1.5, 3.5)
        base_mood = rng.uniform(2.5, 4.5)
        base_sleep_dur = rng.uniform(6.5, 8.5)
        base_sleep_qual = rng.uniform(2.5, 4.5)
        base_soreness = rng.uniform(1.0, 3.0)
        base_stress = rng.uniform(2.0, 6.0)

        for d in dates:
            row: dict[str, Any] = {
                "player_id": pid,
                "date": d,
                "readiness": np.clip(
                    rng.normal(base_readiness, 1.5), 1, 10
                ).round(1),
                "fatigue": np.clip(
                    rng.normal(base_fatigue, 0.8), 1, 5
                ).round(1),
                "mood": np.clip(
                    rng.normal(base_mood, 0.7), 1, 5
                ).round(1),
                "sleep_duration_hours": np.clip(
                    rng.normal(base_sleep_dur, 0.9), 5, 10
                ).round(2),
                "sleep_quality": np.clip(
                    rng.normal(base_sleep_qual, 0.6), 1, 5
                ).round(1),
                "soreness": np.clip(
                    rng.normal(base_soreness, 0.7), 1, 5
                ).round(1),
                "stress": np.clip(
                    rng.normal(base_stress, 1.2), 1, 10
                ).round(1),
                "source_dataset": _SOURCE_DATASET,
                "source_file": _SOURCE_FILE,
            }
            rows.append(row)

    df = pd.DataFrame(rows)
    df["date"] = pd.to_datetime(df["date"])

    # Apply ~15% random missingness to wellness columns (not player_id/date)
    wellness_cols = [
        "readiness", "fatigue", "mood", "sleep_duration_hours",
        "sleep_quality", "soreness", "stress",
    ]
    mask = rng.random(size=(len(df), len(wellness_cols))) < _MISSINGNESS_RATE
    for idx, col in enumerate(wellness_cols):
        df.loc[mask[:, idx], col] = np.nan

    return df


def _generate_training_sessions(
    rng: np.random.Generator,
    players: list[str],
    dates: pd.DatetimeIndex,
) -> pd.DataFrame:
    """Generate the *training_sessions* table with workload metrics."""
    rows: list[dict[str, Any]] = []
    for pid in players:
        for d in dates:
            n_sessions = rng.choice([0, 1, 1, 1, 2, 2, 3])  # 0-3, skewed to 1-2
            for _ in range(n_sessions):
                session_type = rng.choice(_SESSION_TYPES)
                duration = int(rng.integers(30, 121))
                rpe = int(rng.integers(1, 11))
                srpe = duration * rpe
                rows.append({
                    "player_id": pid,
                    "session_date": d,
                    "session_type": session_type,
                    "duration_minutes": duration,
                    "rpe": rpe,
                    "srpe": srpe,
                    "source_dataset": _SOURCE_DATASET,
                    "source_file": _SOURCE_FILE,
                })

    df = pd.DataFrame(rows)
    if df.empty:
        # Return with all expected columns
        return pd.DataFrame(columns=[
            "player_id", "session_date", "session_type", "duration_minutes",
            "rpe", "srpe", "daily_load", "weekly_load", "atl", "ctl_28",
            "ctl_42", "acwr", "monotony", "strain",
            "source_dataset", "source_file",
        ])

    df["session_date"] = pd.to_datetime(df["session_date"])

    # Compute per-player daily load aggregates
    daily_agg = (
        df.groupby(["player_id", "session_date"])["srpe"]
        .sum()
        .reset_index()
        .rename(columns={"srpe": "daily_load", "session_date": "date"})
    )

    # Build a full player × date grid for rolling calculations
    all_records: list[pd.DataFrame] = []
    for pid in players:
        player_daily = daily_agg.loc[daily_agg["player_id"] == pid].copy()
        full_idx = pd.DataFrame({"date": dates})
        full_idx["player_id"] = pid
        player_daily = full_idx.merge(
            player_daily, on=["player_id", "date"], how="left"
        )
        player_daily["daily_load"] = player_daily["daily_load"].fillna(0.0)

        daily_loads = player_daily.set_index("date")["daily_load"]

        player_daily["weekly_load"] = (
            daily_loads.rolling(7, min_periods=1).sum().values
        )
        player_daily["atl"] = compute_atl(daily_loads).values
        player_daily["ctl_28"] = compute_ctl(daily_loads, window=28).values
        player_daily["ctl_42"] = compute_ctl(daily_loads, window=42).values
        player_daily["acwr"] = compute_acwr(
            player_daily["atl"], player_daily["ctl_28"]
        ).values
        mono = compute_monotony(daily_loads, window=7)
        player_daily["monotony"] = mono.values
        player_daily["strain"] = compute_strain(
            player_daily["weekly_load"], player_daily["monotony"]
        ).values

        all_records.append(player_daily)

    workload_df = pd.concat(all_records, ignore_index=True)
    workload_df.rename(columns={"date": "session_date"}, inplace=True)

    # Merge workload metrics back onto sessions
    merge_cols = [
        "daily_load", "weekly_load", "atl", "ctl_28", "ctl_42",
        "acwr", "monotony", "strain",
    ]
    df = df.merge(
        workload_df[["player_id", "session_date"] + merge_cols],
        on=["player_id", "session_date"],
        how="left",
    )

    return df


def _generate_injury_events(
    rng: np.random.Generator,
    players: list[str],
    dates: pd.DatetimeIndex,
    n_events: int = 15,
) -> pd.DataFrame:
    """Generate the *injury_events* table."""
    rows: list[dict[str, Any]] = []
    chosen_players = rng.choice(players, size=n_events, replace=True)
    chosen_dates = rng.choice(dates, size=n_events, replace=False)

    for pid, d in zip(chosen_players, sorted(chosen_dates)):
        rows.append({
            "player_id": pid,
            "date": d,
            "body_location": rng.choice(_BODY_LOCATIONS),
            "severity": rng.choice(_SEVERITIES),
            "is_self_reported": True,
            "source_dataset": _SOURCE_DATASET,
            "source_file": _SOURCE_FILE,
        })

    df = pd.DataFrame(rows)
    df["date"] = pd.to_datetime(df["date"])
    return df


def _generate_illness_events(
    rng: np.random.Generator,
    players: list[str],
    dates: pd.DatetimeIndex,
    n_events: int = 5,
) -> pd.DataFrame:
    """Generate the *illness_events* table."""
    rows: list[dict[str, Any]] = []
    chosen_players = rng.choice(players, size=n_events, replace=True)
    chosen_dates = rng.choice(dates, size=n_events, replace=False)

    for pid, d in zip(chosen_players, sorted(chosen_dates)):
        n_symptoms = rng.integers(1, 4)
        symptom_list = rng.choice(
            _SYMPTOMS, size=n_symptoms, replace=False
        ).tolist()
        rows.append({
            "player_id": pid,
            "date": d,
            "symptoms": ", ".join(symptom_list),
            "source_dataset": _SOURCE_DATASET,
            "source_file": _SOURCE_FILE,
        })

    df = pd.DataFrame(rows)
    df["date"] = pd.to_datetime(df["date"])
    return df


def _generate_game_performance(
    rng: np.random.Generator,
    players: list[str],
    dates: pd.DatetimeIndex,
    matches_per_team: int = 12,
) -> pd.DataFrame:
    """Generate the *game_performance* table."""
    rows: list[dict[str, Any]] = []

    for team in _TEAMS:
        team_players = [p for p in players if p.startswith(team)]
        match_dates = sorted(
            rng.choice(dates, size=matches_per_team, replace=False)
        )
        for md in match_dates:
            team_perf = float(np.clip(rng.normal(6.0, 1.5), 1, 10).round(1))
            off_perf = float(np.clip(rng.normal(5.5, 1.8), 1, 10).round(1))
            def_perf = float(np.clip(rng.normal(6.0, 1.5), 1, 10).round(1))
            for pid in team_players:
                rows.append({
                    "player_id": pid,
                    "date": md,
                    "team_performance": team_perf,
                    "offensive_performance": off_perf,
                    "defensive_performance": def_perf,
                    "source_dataset": _SOURCE_DATASET,
                    "source_file": _SOURCE_FILE,
                })

    df = pd.DataFrame(rows)
    df["date"] = pd.to_datetime(df["date"])
    return df


# ── Public API ───────────────────────────────────────────────────────────────

def generate_demo_data(seed: int | None = None) -> dict[str, pd.DataFrame]:
    """Generate a complete set of synthetic demo data.

    Parameters
    ----------
    seed : int, optional
        Random seed for reproducibility. Defaults to SPORTZA_RANDOM_SEED.

    Returns
    -------
    dict[str, pd.DataFrame]
        Keys: ``wellness_daily``, ``training_sessions``,
        ``injury_events``, ``illness_events``, ``game_performance``.
    """
    rng = np.random.default_rng(seed if seed is not None else SPORTZA_RANDOM_SEED)
    players = _player_ids()
    dates = pd.date_range(start=_DATE_START, end=_DATE_END, freq="D")

    wellness = _generate_wellness(rng, players, dates)
    sessions = _generate_training_sessions(rng, players, dates)
    injuries = _generate_injury_events(rng, players, dates)
    illnesses = _generate_illness_events(rng, players, dates)
    games = _generate_game_performance(rng, players, dates)

    return {
        "wellness_daily": wellness,
        "training_sessions": sessions,
        "injury_events": injuries,
        "illness_events": illnesses,
        "game_performance": games,
    }
