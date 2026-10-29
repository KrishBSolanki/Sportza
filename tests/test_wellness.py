"""Unit tests for SPORTZA wellness calculations."""
import numpy as np
import pandas as pd

from src.features.wellness import (
    compute_data_coverage,
    compute_deviation_from_baseline,
    compute_personal_baseline,
    get_wellness_summary,
)


def test_personal_baseline_and_deviation():
    # 30 days of data
    s = pd.Series([7.0] * 20 + [5.0] * 10)
    baseline = compute_personal_baseline(s, window=28, min_obs=7)
    dev = compute_deviation_from_baseline(s, baseline)
    assert pd.notna(baseline.iloc[20])
    assert dev.iloc[-1] < 0  # Recent drop of 5.0 below baseline


def test_data_coverage():
    # 5 out of 10 days non-null
    s = pd.Series([7.0, np.nan, 8.0, np.nan, 6.0, np.nan, 7.0, np.nan, 8.0, np.nan])
    cov = compute_data_coverage(s, window=10)
    assert cov.iloc[-1] == 0.5


def test_wellness_summary():
    df = pd.DataFrame({
        "player_id": ["P1", "P1", "P1", "P2"],
        "date": ["2020-01-01", "2020-01-02", "2020-01-03", "2020-01-01"],
        "readiness": [8.0, 7.0, 9.0, 6.0],
        "fatigue": [2.0, 3.0, 1.0, 4.0],
    })
    summ = get_wellness_summary(df, "P1")
    assert summ["total_reports"] == 3
    assert summ["metrics"]["readiness"]["mean"] == 8.0
    assert summ["metrics"]["readiness"]["direction"] == "higher_is_better"
    assert summ["metrics"]["fatigue"]["direction"] == "higher_is_worse"
