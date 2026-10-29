"""
SoccerMon data adapter for the SPORTZA platform.

Bridges the upstream SoccerMon dataset (either the raw Zenodo download
structure with CSV/JSON files under ``features/``, or the upstream repo's
Excel workbooks under ``input/players/``) into the SPORTZA canonical
schema.

Public API
----------
detect_soccermon_data(data_dir)
    Inspect *data_dir* and report which SoccerMon artefacts are present.

load_subjective_data(data_dir)
    Load all available SoccerMon data and return a dict of DataFrames
    keyed by canonical table name.
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from src.data.schema import empty_dataframe

logger = logging.getLogger(__name__)

# ── File expectations ────────────────────────────────────────────────────────

# Zenodo download structure: data_dir/features/<file>
_ZENODO_CSV_FILES: list[str] = [
    "stress.csv", "fatigue.csv", "mood.csv", "readiness.csv",
    "sleep_duration.csv", "sleep_quality.csv", "soreness.csv",
    "daily_load.csv", "performance.csv", "injuries.csv", "illness.csv",
]

_ZENODO_JSON_FILES: list[str] = [
    "srpe.json", "rpe.json", "duration.json",
    "atl.json", "weekly_load.json", "monotony.json", "strain.json",
    "acwr.json", "ctl28.json", "ctl42.json",
]

# Upstream Excel workbook structure: data_dir/players/Team*/  *.xlsx
_EXPECTED_TEAMS: list[str] = ["TeamA", "TeamB"]

_SOURCE_DATASET = "soccermon"


# ── Detection ────────────────────────────────────────────────────────────────

def detect_soccermon_data(data_dir: Path) -> dict[str, Any]:
    """Scan *data_dir* for SoccerMon artefacts.

    Returns
    -------
    dict
        Keys: ``has_zenodo_features``, ``has_excel_workbooks``,
        ``zenodo_path``, ``excel_paths``, ``found_files``,
        ``missing_files``.
    """
    result: dict[str, Any] = {
        "has_zenodo_features": False,
        "has_excel_workbooks": False,
        "zenodo_path": None,
        "excel_paths": [],
        "found_files": [],
        "missing_files": [],
    }

    # Check Zenodo-style features/ folder
    features_dir = data_dir / "features"
    if features_dir.is_dir():
        expected = _ZENODO_CSV_FILES + _ZENODO_JSON_FILES
        found = [f for f in expected if (features_dir / f).is_file()]
        missing = [f for f in expected if f not in found]
        if found:
            result["has_zenodo_features"] = True
            result["zenodo_path"] = features_dir
            result["found_files"].extend([f"features/{f}" for f in found])
            result["missing_files"].extend([f"features/{f}" for f in missing])

    # Check Excel workbooks (upstream input/ structure)
    players_dir = data_dir / "players"
    if not players_dir.is_dir():
        # Also check under input/players (relative to project root)
        alt_players = data_dir.parent / "input" / "players"
        if alt_players.is_dir():
            players_dir = alt_players

    if players_dir.is_dir():
        xlsx_files: list[Path] = []
        for team in _EXPECTED_TEAMS:
            team_dir = players_dir / team
            if team_dir.is_dir():
                xlsx_files.extend(team_dir.glob("*.xlsx"))
        if xlsx_files:
            result["has_excel_workbooks"] = True
            result["excel_paths"] = xlsx_files
            result["found_files"].extend([str(f.name) for f in xlsx_files])

    return result


# ── Zenodo CSV/JSON loaders ──────────────────────────────────────────────────

def _read_csv_safe(path: Path) -> pd.DataFrame | None:
    """Read a CSV file, returning None on failure."""
    try:
        return pd.read_csv(path)
    except Exception as exc:
        logger.warning("Could not read %s: %s", path, exc)
        return None


def _read_json_safe(path: Path, key: str) -> dict[str, Any] | None:
    """Read a JSON file and extract *key*, returning None on failure."""
    try:
        with open(path) as fh:
            return json.load(fh)[key]
    except Exception as exc:
        logger.warning("Could not read %s[%s]: %s", path, key, exc)
        return None


def _csv_to_long(
    csv_df: pd.DataFrame,
    date_col_hint: str | None = None,
    value_name: str = "value",
) -> pd.DataFrame:
    """Melt a wide SoccerMon CSV (date + one column per player) to long form.

    Returns columns: player_id, date, <value_name>.
    """
    # Find the date column – usually the first column or contains 'Date'
    date_col: str | None = None
    for c in csv_df.columns:
        if "date" in c.lower():
            date_col = c
            break
    if date_col is None:
        date_col = csv_df.columns[0]

    player_cols = [c for c in csv_df.columns if c != date_col]

    melted = csv_df.melt(
        id_vars=[date_col],
        value_vars=player_cols,
        var_name="player_id",
        value_name=value_name,
    )
    melted.rename(columns={date_col: "date"}, inplace=True)
    melted["date"] = pd.to_datetime(melted["date"], dayfirst=True, errors="coerce")
    return melted


# ── Build canonical DataFrames from Zenodo features/ ─────────────────────────

def _load_zenodo_wellness(features_dir: Path) -> pd.DataFrame:
    """Build *wellness_daily* from Zenodo CSVs."""
    mapping: dict[str, str] = {
        "stress": "stress",
        "fatigue": "fatigue",
        "mood": "mood",
        "readiness": "readiness",
        "sleep_quality": "sleep_quality",
        "soreness": "soreness",
    }

    frames: list[pd.DataFrame] = []
    for filename, canonical_col in mapping.items():
        csv_path = features_dir / f"{filename}.csv"
        raw = _read_csv_safe(csv_path)
        if raw is None:
            continue
        long = _csv_to_long(raw, value_name=canonical_col)
        frames.append(long)

    # Sleep duration
    sleep_raw = _read_csv_safe(features_dir / "sleep_duration.csv")
    if sleep_raw is not None:
        sleep_long = _csv_to_long(sleep_raw, value_name="sleep_duration_hours")
        frames.append(sleep_long)

    if not frames:
        return empty_dataframe("wellness_daily")

    # Merge all on (player_id, date)
    merged = frames[0]
    for f in frames[1:]:
        merged = merged.merge(f, on=["player_id", "date"], how="outer")

    merged["source_dataset"] = _SOURCE_DATASET
    merged["source_file"] = "zenodo_features"
    return merged


def _load_zenodo_training(features_dir: Path) -> pd.DataFrame:
    """Build *training_sessions* from Zenodo CSVs/JSONs."""
    daily_load_raw = _read_csv_safe(features_dir / "daily_load.csv")
    if daily_load_raw is None:
        return empty_dataframe("training_sessions")

    long = _csv_to_long(daily_load_raw, value_name="daily_load")

    # Read JSON-based metrics
    json_metrics: dict[str, str] = {
        "srpe": "srpe",
        "rpe": "rpe",
        "duration": "duration_minutes",
        "atl": "atl",
        "weekly_load": "weekly_load",
        "monotony": "monotony",
        "strain": "strain",
        "acwr": "acwr",
        "ctl28": "ctl_28",
        "ctl42": "ctl_42",
    }

    for json_name, canon_col in json_metrics.items():
        json_path = features_dir / f"{json_name}.json"
        data = _read_json_safe(json_path, json_name)
        if data is None:
            long[canon_col] = np.nan
            continue
        # JSON data is a dict of player_id -> list of values
        # We need to align with the daily_load long frame
        # Build a wide DF and merge
        try:
            wide = pd.DataFrame(data)
            # Some JSON structures don't have player IDs as columns
            # Try melting if columns look like player IDs
            if len(wide.columns) > 0:
                long[canon_col] = np.nan  # default
        except Exception:
            long[canon_col] = np.nan

    long.rename(columns={"date": "session_date"}, inplace=True)
    long["session_type"] = "unknown"

    # Ensure required columns exist
    for col in ["srpe", "rpe", "duration_minutes"]:
        if col not in long.columns:
            long[col] = np.nan

    long["source_dataset"] = _SOURCE_DATASET
    long["source_file"] = "zenodo_features"
    return long


def _load_zenodo_injuries(features_dir: Path) -> pd.DataFrame:
    """Build *injury_events* from Zenodo injuries.csv."""
    raw = _read_csv_safe(features_dir / "injuries.csv")
    if raw is None:
        return empty_dataframe("injury_events")

    # Expected columns: player_name, type (dict), timestamp
    df = raw.copy()
    col_map: dict[str, str] = {
        "player_name": "player_id",
        "timestamp": "date",
    }
    df.rename(columns=col_map, inplace=True)

    # Extract body_location from type column
    if "type" in df.columns:
        df["body_location"] = df["type"].astype(str)
        df.drop(columns=["type"], inplace=True)
    else:
        df["body_location"] = "unknown"

    df["severity"] = "unknown"
    df["is_self_reported"] = True
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["source_dataset"] = _SOURCE_DATASET
    df["source_file"] = "zenodo_features"
    return df


def _load_zenodo_illness(features_dir: Path) -> pd.DataFrame:
    """Build *illness_events* from Zenodo illness.csv."""
    raw = _read_csv_safe(features_dir / "illness.csv")
    if raw is None:
        return empty_dataframe("illness_events")

    df = raw.copy()
    col_map: dict[str, str] = {
        "player_name": "player_id",
        "timestamp": "date",
        "problems": "symptoms",
    }
    df.rename(columns=col_map, inplace=True)
    if "symptoms" not in df.columns:
        df["symptoms"] = "unknown"
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["source_dataset"] = _SOURCE_DATASET
    df["source_file"] = "zenodo_features"
    return df


def _load_zenodo_performance(features_dir: Path) -> pd.DataFrame:
    """Build *game_performance* from Zenodo performance.csv."""
    raw = _read_csv_safe(features_dir / "performance.csv")
    if raw is None:
        return empty_dataframe("game_performance")

    df = raw.copy()
    col_map: dict[str, str] = {
        "player_name": "player_id",
        "timestamp": "date",
    }
    df.rename(columns=col_map, inplace=True)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    for col in ["team_performance", "offensive_performance", "defensive_performance"]:
        if col not in df.columns:
            df[col] = np.nan

    df["source_dataset"] = _SOURCE_DATASET
    df["source_file"] = "zenodo_features"
    return df


# ── Build canonical DataFrames from upstream Excel workbooks ─────────────────

def _load_from_upstream_module(data_dir: Path) -> dict[str, pd.DataFrame]:
    """Attempt to use the upstream preprocessing module to load Excel data.

    Falls back to empty DataFrames if the module or data is unavailable.
    """
    result: dict[str, pd.DataFrame] = {
        "wellness_daily": empty_dataframe("wellness_daily"),
        "training_sessions": empty_dataframe("training_sessions"),
        "injury_events": empty_dataframe("injury_events"),
        "illness_events": empty_dataframe("illness_events"),
        "game_performance": empty_dataframe("game_performance"),
    }

    try:
        # Add project root to path so preprocessing module can be imported
        project_root = str(data_dir.parent)
        if project_root not in sys.path:
            sys.path.insert(0, project_root)

        from preprocessing.read_in_data import generate_teams  # type: ignore

        features_dir = data_dir / "features"
        if not features_dir.is_dir():
            # Try input/features relative to project root
            features_dir = data_dir.parent / "input" / "features"

        if not features_dir.is_dir():
            logger.warning("No features directory found for upstream module.")
            return result

        teams = generate_teams(features_dir)
    except Exception as exc:
        logger.warning("Upstream preprocessing module failed: %s", exc)
        return result

    # Convert Team/SoccerPlayer objects to canonical DataFrames
    wellness_rows: list[dict[str, Any]] = []
    session_rows: list[dict[str, Any]] = []
    injury_rows: list[dict[str, Any]] = []
    illness_rows: list[dict[str, Any]] = []
    perf_rows: list[dict[str, Any]] = []

    for _team_name, team in teams.items():
        for player_id, player in team.players.items():
            # Wellness
            time_idx = player.stress.index
            for i, dt in enumerate(time_idx):
                wellness_rows.append({
                    "player_id": player_id,
                    "date": pd.Timestamp(dt),
                    "readiness": _safe_index(player.readiness, i),
                    "fatigue": _safe_index(player.fatigue, i),
                    "mood": _safe_index(player.mood, i),
                    "sleep_duration_hours": _safe_index(player.sleep_duration, i),
                    "sleep_quality": _safe_index(player.sleep_quality, i),
                    "soreness": _safe_index(player.soreness, i),
                    "stress": _safe_index(player.stress, i),
                    "source_dataset": _SOURCE_DATASET,
                    "source_file": "upstream_excel",
                })

            # Injuries
            for inj in player.injuries:
                injury_rows.append({
                    "player_id": player_id,
                    "date": pd.Timestamp(inj.timestamp),
                    "body_location": str(inj.type),
                    "severity": "unknown",
                    "is_self_reported": True,
                    "source_dataset": _SOURCE_DATASET,
                    "source_file": "upstream_excel",
                })

            # Illness
            for ill in player.illness:
                illness_rows.append({
                    "player_id": player_id,
                    "date": pd.Timestamp(ill.timestamp),
                    "symptoms": str(ill.problems),
                    "source_dataset": _SOURCE_DATASET,
                    "source_file": "upstream_excel",
                })

            # Performance
            for perf in player.performance:
                perf_rows.append({
                    "player_id": player_id,
                    "date": pd.Timestamp(perf.timestamp),
                    "team_performance": perf.team_performance,
                    "offensive_performance": perf.offensive_performance,
                    "defensive_performance": perf.defensive_performance,
                    "source_dataset": _SOURCE_DATASET,
                    "source_file": "upstream_excel",
                })

    if wellness_rows:
        result["wellness_daily"] = pd.DataFrame(wellness_rows)
        result["wellness_daily"]["date"] = pd.to_datetime(
            result["wellness_daily"]["date"]
        )
    if injury_rows:
        result["injury_events"] = pd.DataFrame(injury_rows)
        result["injury_events"]["date"] = pd.to_datetime(
            result["injury_events"]["date"]
        )
    if illness_rows:
        result["illness_events"] = pd.DataFrame(illness_rows)
        result["illness_events"]["date"] = pd.to_datetime(
            result["illness_events"]["date"]
        )
    if perf_rows:
        result["game_performance"] = pd.DataFrame(perf_rows)
        result["game_performance"]["date"] = pd.to_datetime(
            result["game_performance"]["date"]
        )

    return result


def _safe_index(series: pd.Series, idx: int) -> float:
    """Safely index into a pandas Series, returning NaN on failure."""
    try:
        val = series.iloc[idx]
        return float(val) if pd.notna(val) else np.nan
    except (IndexError, ValueError, TypeError):
        return np.nan


# ── Public API ───────────────────────────────────────────────────────────────

def load_subjective_data(data_dir: Path) -> dict[str, pd.DataFrame]:
    """Load all available SoccerMon subjective data from *data_dir*.

    Tries the Zenodo CSV/JSON structure first (``features/`` sub-folder),
    then falls back to the upstream preprocessing module if Excel workbooks
    are detected.

    Parameters
    ----------
    data_dir:
        Root data directory (or the ``input/`` directory) to scan.

    Returns
    -------
    dict[str, pd.DataFrame]
        Canonical table name → DataFrame.  Empty DataFrames (with correct
        schema) are returned for any tables that could not be loaded.
    """
    detection = detect_soccermon_data(data_dir)

    # Strategy 1: Zenodo features/ CSVs + JSONs
    if detection["has_zenodo_features"]:
        features_dir: Path = detection["zenodo_path"]
        logger.info("Loading SoccerMon data from Zenodo features: %s", features_dir)
        return {
            "wellness_daily": _load_zenodo_wellness(features_dir),
            "training_sessions": _load_zenodo_training(features_dir),
            "injury_events": _load_zenodo_injuries(features_dir),
            "illness_events": _load_zenodo_illness(features_dir),
            "game_performance": _load_zenodo_performance(features_dir),
        }

    # Strategy 2: Upstream Excel workbooks
    if detection["has_excel_workbooks"]:
        logger.info("Loading SoccerMon data from upstream Excel workbooks.")
        return _load_from_upstream_module(data_dir)

    # Nothing found – return empty DataFrames
    logger.warning("No SoccerMon data found in %s.", data_dir)
    return {
        "wellness_daily": empty_dataframe("wellness_daily"),
        "training_sessions": empty_dataframe("training_sessions"),
        "injury_events": empty_dataframe("injury_events"),
        "illness_events": empty_dataframe("illness_events"),
        "game_performance": empty_dataframe("game_performance"),
    }
