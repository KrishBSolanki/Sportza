"""Unit tests for SPORTZA workload calculations."""
import pandas as pd

from src.features.workload import (
    compute_acwr,
    compute_atl,
    compute_ctl,
    compute_daily_load,
    compute_monotony,
    compute_rolling_load,
    compute_srpe,
    compute_strain,
)


def test_compute_srpe_scalar():
    assert compute_srpe(60, 5) == 300.0
    assert compute_srpe(90, 7) == 630.0
    assert compute_srpe(0, 5) == 0.0
    assert compute_srpe(60, 0) == 0.0
    # Negative / out of bounds handling
    assert compute_srpe(-10, 5) == 0.0
    assert compute_srpe(60, -2) == 0.0
    assert compute_srpe(60, 15) == 600.0  # RPE capped at 10


def test_compute_srpe_series():
    durations = pd.Series([60, 45, 90])
    rpes = pd.Series([5, 6, 8])
    expected = pd.Series([300.0, 270.0, 720.0])
    pd.testing.assert_series_equal(compute_srpe(durations, rpes), expected)


def test_compute_daily_load():
    df = pd.DataFrame({
        "player_id": ["P1", "P1", "P1", "P2"],
        "session_date": ["2020-01-01", "2020-01-01", "2020-01-02", "2020-01-01"],
        "duration_minutes": [60, 30, 90, 60],
        "rpe": [5, 4, 7, 6],
    })
    daily = compute_daily_load(df)
    assert len(daily) == 3
    # P1 on 2020-01-01 has 60*5 + 30*4 = 300 + 120 = 420
    p1_day1 = daily[(daily["player_id"] == "P1") & (daily["date"] == pd.to_datetime("2020-01-01"))]
    assert p1_day1["daily_load"].values[0] == 420.0


def test_compute_atl_ctl_acwr():
    # 28 days of constant load 400
    loads = pd.Series([400.0] * 28)
    atl = compute_atl(loads, window=7)
    ctl = compute_ctl(loads, window=28)
    acwr = compute_acwr(atl, ctl)

    assert atl.iloc[-1] == 400.0
    assert ctl.iloc[-1] == 400.0
    assert acwr.iloc[-1] == 1.0


def test_compute_acwr_zero_ctl_safety():
    atl = pd.Series([300.0, 400.0])
    ctl = pd.Series([0.0, 0.5])  # below min_ctl threshold
    acwr = compute_acwr(atl, ctl, min_ctl=1.0)
    assert acwr.isna().all()


def test_compute_monotony_and_strain():
    # High monotony (low variance)
    stable_loads = pd.Series([300.0, 310.0, 300.0, 305.0, 300.0, 310.0, 305.0])
    monotony = compute_monotony(stable_loads, window=7)
    assert monotony.iloc[-1] > 2.0  # Mean / small std => high monotony

    weekly_load = compute_rolling_load(stable_loads, window=7)
    strain = compute_strain(weekly_load, monotony)
    assert strain.iloc[-1] == round(weekly_load.iloc[-1] * monotony.iloc[-1], 1)
