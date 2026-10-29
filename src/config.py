"""
SPORTZA configuration module.

Centralises all project-wide settings, directory paths, data-scale
definitions, and constants.  Values are loaded from environment variables
where applicable, with sensible defaults for local / demo usage.
"""

from __future__ import annotations

import os
from pathlib import Path

# ── Environment-driven settings ──────────────────────────────────────────────

PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent

SPORTZA_DATA_DIR: Path = Path(
    os.environ.get("SPORTZA_DATA_DIR", str(PROJECT_ROOT / "data"))
)

SPORTZA_DEMO_MODE: bool = (
    os.environ.get("SPORTZA_DEMO_MODE", "true").strip().lower()
    in {"true", "1", "yes"}
)

SPORTZA_RANDOM_SEED: int = int(os.environ.get("SPORTZA_RANDOM_SEED", "42"))


# ── Derived directory paths ──────────────────────────────────────────────────

RAW_DATA_DIR: Path = SPORTZA_DATA_DIR / "raw"
PROCESSED_DATA_DIR: Path = SPORTZA_DATA_DIR / "processed"
MODELS_DIR: Path = SPORTZA_DATA_DIR / "models"
REPORTS_DIR: Path = SPORTZA_DATA_DIR / "reports"
DEMO_DATA_DIR: Path = SPORTZA_DATA_DIR / "demo"


# ── Data-scale definitions ───────────────────────────────────────────────────
# Maps each wellness / workload metric to its valid range (inclusive).

DATA_SCALES: dict[str, tuple[float, float]] = {
    "readiness": (1.0, 10.0),
    "fatigue": (1.0, 5.0),
    "mood": (1.0, 5.0),
    "sleep_quality": (1.0, 5.0),
    "soreness": (1.0, 5.0),
    "stress": (1.0, 10.0),
    "rpe": (1.0, 10.0),
    "sleep_duration_hours": (0.0, 24.0),  # float, practical range ~4-12
}


# ── Scale direction ──────────────────────────────────────────────────────────
# "higher_is_better" → a high value is desirable.
# "higher_is_worse"  → a high value signals a problem.

SCALE_DIRECTION: dict[str, str] = {
    "readiness": "higher_is_better",
    "mood": "higher_is_better",
    "sleep_quality": "higher_is_better",
    "sleep_duration_hours": "higher_is_better",
    "fatigue": "higher_is_worse",
    "soreness": "higher_is_worse",
    "stress": "higher_is_worse",
}


# ── Dataset attribution ─────────────────────────────────────────────────────

DATASET_ATTRIBUTION: str = (
    "SoccerMon dataset by Lia Schultz, Nico Bettenburg, and Ahmed E. Hassan. "
    "Licensed under Creative Commons Attribution 4.0 International (CC BY 4.0). "
    "Available at https://zenodo.org/records/7529530. "
    "Citation: Schultz, L., Bettenburg, N., & Hassan, A. E. (2023). "
    "SoccerMon – A dataset of subjective athlete wellness and workload data "
    "[Data set]. Zenodo. https://doi.org/10.5281/zenodo.7529530"
)


class Config:
    """Convenience class wrapper exposing config settings as attributes/properties."""
    PROJECT_ROOT: Path = PROJECT_ROOT
    SPORTZA_DATA_DIR: Path = SPORTZA_DATA_DIR
    SPORTZA_DEMO_MODE: bool = SPORTZA_DEMO_MODE
    SPORTZA_RANDOM_SEED: int = SPORTZA_RANDOM_SEED
    RAW_DATA_DIR: Path = RAW_DATA_DIR
    PROCESSED_DATA_DIR: Path = PROCESSED_DATA_DIR
    MODELS_DIR: Path = MODELS_DIR
    REPORTS_DIR: Path = REPORTS_DIR
    DEMO_DATA_DIR: Path = DEMO_DATA_DIR
    DATA_SCALES: dict[str, tuple[float, float]] = DATA_SCALES
    SCALE_DIRECTION: dict[str, str] = SCALE_DIRECTION
    DATASET_ATTRIBUTION: str = DATASET_ATTRIBUTION

    @property
    def demo_mode(self) -> bool:
        return SPORTZA_DEMO_MODE

    @property
    def random_seed(self) -> int:
        return SPORTZA_RANDOM_SEED

    @property
    def data_dir(self) -> Path:
        return SPORTZA_DATA_DIR
