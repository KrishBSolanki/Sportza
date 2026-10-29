"""
Data discovery module for the SPORTZA platform.

Provides a single entry-point – :func:`get_data_status` – that inspects
the configured data directory and returns a comprehensive inventory of
available data, mode selection, row counts, and any warnings.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import pandas as pd

from src.config import SPORTZA_DATA_DIR, SPORTZA_DEMO_MODE
from src.data.demo_generator import generate_demo_data
from src.data.schema import CANONICAL_SCHEMAS, empty_dataframe
from src.data.soccermon_adapter import detect_soccermon_data, load_subjective_data

logger = logging.getLogger(__name__)

# Canonical table names
_TABLE_NAMES: list[str] = list(CANONICAL_SCHEMAS.keys())


def get_data_status() -> dict[str, Any]:
    """Return a comprehensive inventory of available data.

    Returns
    -------
    dict
        Keys:

        * ``mode`` – one of ``"demo"``, ``"subjective"``, ``"full"``
        * ``data_dir`` – the resolved data directory path
        * ``files_found`` – list of data files/sources found
        * ``files_missing`` – list of expected but missing files
        * ``row_counts`` – dict mapping table name → int (row count)
        * ``tables`` – dict mapping table name → pd.DataFrame
        * ``warnings`` – list of human-readable warning strings
    """
    data_dir: Path = SPORTZA_DATA_DIR
    warnings_list: list[str] = []
    files_found: list[str] = []
    files_missing: list[str] = []
    row_counts: dict[str, int] = {}
    tables: dict[str, pd.DataFrame] = {}

    # Determine mode
    detection = detect_soccermon_data(data_dir)
    has_real_data = (
        detection["has_zenodo_features"] or detection["has_excel_workbooks"]
    )

    # Also check the project-level input/ directory
    if not has_real_data:
        project_root = data_dir.parent
        input_dir = project_root / "input"
        if input_dir.is_dir():
            detection = detect_soccermon_data(input_dir)
            has_real_data = (
                detection["has_zenodo_features"]
                or detection["has_excel_workbooks"]
            )
            if has_real_data:
                data_dir = input_dir

    files_found.extend(detection.get("found_files", []))
    files_missing.extend(detection.get("missing_files", []))

    if has_real_data and not SPORTZA_DEMO_MODE:
        mode = "subjective"
        try:
            tables = load_subjective_data(data_dir)
        except Exception as exc:
            warnings_list.append(
                f"Failed to load subjective data: {exc}. "
                "Falling back to demo mode."
            )
            mode = "demo"
            tables = generate_demo_data()
    else:
        if SPORTZA_DEMO_MODE:
            if has_real_data:
                warnings_list.append(
                    "Real SoccerMon data was detected but SPORTZA_DEMO_MODE "
                    "is enabled.  Using synthetic demo data.  Set "
                    "SPORTZA_DEMO_MODE=false to use real data."
                )
        else:
            warnings_list.append(
                "No SoccerMon data found in the configured data directory.  "
                "Using synthetic demo data.  Place the Zenodo download in "
                f"'{SPORTZA_DATA_DIR}' or set SPORTZA_DEMO_MODE=true."
            )
        mode = "demo"
        tables = generate_demo_data()

    # Ensure all canonical tables exist (fill blanks)
    for tbl_name in _TABLE_NAMES:
        if tbl_name not in tables:
            tables[tbl_name] = empty_dataframe(tbl_name)
            warnings_list.append(f"Table '{tbl_name}' is empty.")

    # Compute row counts
    for tbl_name in _TABLE_NAMES:
        row_counts[tbl_name] = len(tables[tbl_name])

    return {
        "mode": mode,
        "data_dir": str(data_dir),
        "files_found": files_found,
        "files_missing": files_missing,
        "row_counts": row_counts,
        "tables": tables,
        "warnings": warnings_list,
    }
