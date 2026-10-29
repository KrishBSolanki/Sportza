"""
SPORTZA Model Artifact Management.

Provides utilities for saving, loading, and tracking model artifacts
with full metadata for reproducibility.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import joblib


@dataclass
class ModelRun:
    """Record of a single model training run for audit and reproducibility.

    Attributes
    ----------
    task : str
        The prediction task (e.g. "readiness_forecast").
    target : str
        The target variable name.
    horizon : str
        Prediction horizon (e.g. "next_day", "next_7_days").
    split_date : str
        ISO date string of the chronological train/test split.
    metrics : dict
        Evaluation metrics from the run.
    timestamp : str
        ISO timestamp of the run.
    n_train : int
        Number of training samples.
    n_test : int
        Number of test samples.
    model_type : str
        Name of the model algorithm used.
    feature_count : int
        Number of features used.
    hyperparameters : dict
        Model hyperparameters.
    notes : str
        Free-text notes about the run.
    """

    task: str
    target: str
    horizon: str
    split_date: str
    metrics: dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(
        default_factory=lambda: datetime.now(UTC).isoformat()
    )
    n_train: int = 0
    n_test: int = 0
    model_type: str = ""
    feature_count: int = 0
    hyperparameters: dict[str, Any] = field(default_factory=dict)
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialisation."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ModelRun:
        """Reconstruct a ModelRun from a dictionary."""
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


def save_model_artifact(
    model: Any,
    metadata: dict[str, Any],
    path: Path,
) -> None:
    """Save a trained model and its metadata to disk.

    Creates two files:
    - ``<path>.joblib`` – the serialised model object.
    - ``<path>.meta.json`` – JSON metadata (metrics, hyperparameters, etc.).

    Parameters
    ----------
    model : Any
        The trained model object (must be picklable).
    metadata : dict
        Metadata dictionary (metrics, feature names, training info, etc.).
    path : Path
        Base path (without extension). Two files will be created.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    model_path = path.with_suffix(".joblib")
    meta_path = path.with_suffix(".meta.json")

    joblib.dump(model, model_path)

    # Ensure metadata is JSON-serialisable
    serialisable_meta = _make_json_safe(metadata)
    serialisable_meta["saved_at"] = datetime.now(UTC).isoformat()
    serialisable_meta["model_path"] = str(model_path)

    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(serialisable_meta, f, indent=2, default=str)


def load_model_artifact(path: Path) -> tuple[Any, dict[str, Any]]:
    """Load a model and its metadata from disk.

    Parameters
    ----------
    path : Path
        Base path (without extension). Expects ``.joblib`` and ``.meta.json``
        files to exist.

    Returns
    -------
    tuple of (model, metadata)
        The deserialised model object and its metadata dictionary.

    Raises
    ------
    FileNotFoundError
        If either the model file or metadata file is missing.
    """
    path = Path(path)
    model_path = path.with_suffix(".joblib")
    meta_path = path.with_suffix(".meta.json")

    if not model_path.exists():
        raise FileNotFoundError(f"Model file not found: {model_path}")
    if not meta_path.exists():
        raise FileNotFoundError(f"Metadata file not found: {meta_path}")

    model = joblib.load(model_path)

    with open(meta_path, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    return model, metadata


def _make_json_safe(obj: Any) -> Any:
    """Recursively convert numpy/pandas types to JSON-serialisable Python types."""
    import numpy as np
    import pandas as pd

    if isinstance(obj, dict):
        return {str(k): _make_json_safe(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [_make_json_safe(v) for v in obj]
    elif isinstance(obj, (np.integer,)):
        return int(obj)
    elif isinstance(obj, (np.floating,)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, pd.Timestamp):
        return obj.isoformat()
    elif isinstance(obj, (np.bool_,)):
        return bool(obj)
    elif isinstance(obj, (np.str_,)):
        return str(obj)
    elif isinstance(obj, (datetime,)):
        return obj.isoformat()
    elif isinstance(obj, Path):
        return str(obj)
    else:
        return obj
