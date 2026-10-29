"""
Canonical data-schema definitions and validation for the SPORTZA platform.

Each table schema is expressed as a list of (column_name, dtype, required)
tuples.  ``validate_dataframe`` checks that required columns exist and that
their dtypes are compatible with the declared type.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

# ── Schema definitions ───────────────────────────────────────────────────────
# (column_name, expected_dtype_kind, required)
#
# dtype_kind uses numpy dtype *kind* codes:
#   "f" → float, "i" → int, "O" → object/string, "M" → datetime64,
#   "b" → bool, "U" → unicode string
# We also accept "numeric" as a shorthand for either int or float.

_SchemaEntry = tuple[str, str, bool]

CANONICAL_SCHEMAS: dict[str, list[_SchemaEntry]] = {
    "wellness_daily": [
        ("player_id", "O", True),
        ("date", "M", True),
        ("readiness", "numeric", False),
        ("fatigue", "numeric", False),
        ("mood", "numeric", False),
        ("sleep_duration_hours", "numeric", False),
        ("sleep_quality", "numeric", False),
        ("soreness", "numeric", False),
        ("stress", "numeric", False),
        ("source_dataset", "O", False),
        ("source_file", "O", False),
    ],
    "training_sessions": [
        ("player_id", "O", True),
        ("session_date", "M", True),
        ("session_type", "O", True),
        ("duration_minutes", "numeric", True),
        ("rpe", "numeric", True),
        ("srpe", "numeric", False),
        ("daily_load", "numeric", False),
        ("weekly_load", "numeric", False),
        ("atl", "numeric", False),
        ("ctl_28", "numeric", False),
        ("ctl_42", "numeric", False),
        ("acwr", "numeric", False),
        ("monotony", "numeric", False),
        ("strain", "numeric", False),
        ("source_dataset", "O", False),
        ("source_file", "O", False),
    ],
    "injury_events": [
        ("player_id", "O", True),
        ("date", "M", True),
        ("body_location", "O", True),
        ("severity", "O", True),
        ("is_self_reported", "b", False),
        ("source_dataset", "O", False),
        ("source_file", "O", False),
    ],
    "illness_events": [
        ("player_id", "O", True),
        ("date", "M", True),
        ("symptoms", "O", True),
        ("source_dataset", "O", False),
        ("source_file", "O", False),
    ],
    "game_performance": [
        ("player_id", "O", True),
        ("date", "M", True),
        ("team_performance", "numeric", True),
        ("offensive_performance", "numeric", True),
        ("defensive_performance", "numeric", True),
        ("source_dataset", "O", False),
        ("source_file", "O", False),
    ],
}

# ── Dtype compatibility map ──────────────────────────────────────────────────

_COMPATIBLE_KINDS: dict[str, set[str]] = {
    "f": {"f", "i", "u"},          # float accepts int/uint too
    "i": {"i", "u", "f"},          # int column may be stored as float (NaN)
    "O": {"O", "U", "S"},          # object / string
    "M": {"M"},                    # datetime
    "b": {"b", "O", "i", "u"},     # bool may be stored as object or int
    "U": {"U", "O", "S"},          # unicode string
    "numeric": {"f", "i", "u"},    # convenience alias
}


def _kinds_match(expected_kind: str, actual_kind: str) -> bool:
    """Return True when *actual_kind* is compatible with *expected_kind*."""
    allowed = _COMPATIBLE_KINDS.get(expected_kind, {expected_kind})
    return actual_kind in allowed


# ── Public API ───────────────────────────────────────────────────────────────

def validate_dataframe(
    df: pd.DataFrame,
    schema_name: str,
) -> list[str]:
    """Validate *df* against the canonical schema for *schema_name*.

    Parameters
    ----------
    df:
        The DataFrame to validate.
    schema_name:
        Key into :data:`CANONICAL_SCHEMAS`.

    Returns
    -------
    list[str]
        A list of human-readable validation errors.  An empty list means
        the DataFrame passed all checks.

    Raises
    ------
    KeyError
        If *schema_name* is not found in :data:`CANONICAL_SCHEMAS`.
    """
    if schema_name not in CANONICAL_SCHEMAS:
        raise KeyError(
            f"Unknown schema '{schema_name}'. "
            f"Available: {sorted(CANONICAL_SCHEMAS.keys())}"
        )

    schema = CANONICAL_SCHEMAS[schema_name]
    errors: list[str] = []

    for col_name, expected_kind, required in schema:
        if col_name not in df.columns:
            if required:
                errors.append(
                    f"Missing required column '{col_name}' in '{schema_name}'."
                )
            continue

        actual_kind = df[col_name].dtype.kind
        if not _kinds_match(expected_kind, actual_kind):
            errors.append(
                f"Column '{col_name}' in '{schema_name}' has dtype kind "
                f"'{actual_kind}' but expected compatible with '{expected_kind}'."
            )

    return errors


def empty_dataframe(schema_name: str) -> pd.DataFrame:
    """Return an empty DataFrame with columns matching *schema_name*.

    The returned DataFrame has zero rows but the correct column names
    and sensible default dtypes.
    """
    if schema_name not in CANONICAL_SCHEMAS:
        raise KeyError(
            f"Unknown schema '{schema_name}'. "
            f"Available: {sorted(CANONICAL_SCHEMAS.keys())}"
        )

    _DTYPE_DEFAULTS: dict[str, Any] = {
        "f": np.float64,
        "i": np.int64,
        "O": object,
        "M": "datetime64[ns]",
        "b": bool,
        "U": str,
        "numeric": np.float64,
    }

    schema = CANONICAL_SCHEMAS[schema_name]
    data: dict[str, pd.Series] = {}
    for col_name, kind, _req in schema:
        dtype = _DTYPE_DEFAULTS.get(kind, object)
        data[col_name] = pd.Series(dtype=dtype)

    return pd.DataFrame(data)
