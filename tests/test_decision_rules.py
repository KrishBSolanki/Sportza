"""Unit tests for the decision support rules engine."""
import pandas as pd

from src.decision_support.rules import (
    DataAdequacy,
    DecisionEngine,
    RecommendationStatus,
)


def test_decision_engine_insufficient_data():
    engine = DecisionEngine()
    # Only 2 days of history (below min required 7)
    wellness = pd.DataFrame({
        "player_id": ["P1", "P1"],
        "date": ["2020-01-01", "2020-01-02"],
        "readiness": [7.0, 7.0],
        "fatigue": [2.0, 2.0],
        "mood": [4.0, 4.0],
        "sleep_quality": [4.0, 4.0],
        "sleep_duration_hours": [8.0, 8.0],
        "soreness": [2.0, 2.0],
        "stress": [3.0, 3.0],
    })
    rec = engine.evaluate(
        player_id="P1",
        current_date="2020-01-02",
        wellness_history=wellness,
        training_history=pd.DataFrame(),
        injury_history=pd.DataFrame(),
        illness_history=pd.DataFrame(),
    )
    assert rec.status == RecommendationStatus.INSUFFICIENT_DATA
    assert rec.data_adequacy == DataAdequacy.INSUFFICIENT
    assert "non-medical" in rec.non_medical_note.lower()


def test_decision_engine_injury_escalation():
    engine = DecisionEngine()
    # 20 days of data
    dates = pd.date_range("2020-01-01", "2020-01-20", freq="D")
    wellness = pd.DataFrame({
        "player_id": ["P1"] * len(dates),
        "date": dates.strftime("%Y-%m-%d"),
        "readiness": [7.0] * len(dates),
        "fatigue": [2.0] * len(dates),
        "mood": [4.0] * len(dates),
        "sleep_quality": [4.0] * len(dates),
        "sleep_duration_hours": [8.0] * len(dates),
        "soreness": [2.0] * len(dates),
        "stress": [3.0] * len(dates),
    })
    # Major pain reported on current date
    injuries = pd.DataFrame({
        "player_id": ["P1"],
        "event_date": ["2020-01-20"],
        "reported_severity": ["major"],
        "body_location": ["right_knee"],
    })
    rec = engine.evaluate(
        player_id="P1",
        current_date="2020-01-20",
        wellness_history=wellness,
        training_history=pd.DataFrame(),
        injury_history=injuries,
        illness_history=pd.DataFrame(),
    )
    assert rec.status == RecommendationStatus.HUMAN_REVIEW
    assert any("right_knee" in flag for flag in rec.escalation_flags)
    assert "clinician" in rec.recommendation_text.lower()


def test_decision_engine_workload_trend_and_training_history():
    engine = DecisionEngine()
    dates = pd.date_range("2020-01-01", "2020-01-20", freq="D")
    wellness = pd.DataFrame({
        "player_id": ["P1"] * len(dates),
        "date": dates.strftime("%Y-%m-%d"),
        "readiness": [5.0] * len(dates),
        "fatigue": [4.0] * len(dates),
        "mood": [3.0] * len(dates),
        "sleep_quality": [3.0] * len(dates),
        "sleep_duration_hours": [7.0] * len(dates),
        "soreness": [4.0] * len(dates),
        "stress": [4.0] * len(dates),
    })
    training = pd.DataFrame({
        "player_id": ["P1"] * 7,
        "session_date": dates[-7:].strftime("%Y-%m-%d"),
        "session_type": ["training"] * 7,
        "duration_minutes": [60] * 7,
        "rpe": [5] * 7,
        "daily_load": [100.0, 150.0, 200.0, 250.0, 300.0, 350.0, 400.0],
    })
    rec = engine.evaluate(
        player_id="P1",
        current_date="2020-01-20",
        wellness_history=wellness,
        training_history=training,
        injury_history=pd.DataFrame(),
        illness_history=pd.DataFrame(),
    )
    assert rec.status in (
        RecommendationStatus.RECOVERY_FOCUSED,
        RecommendationStatus.MONITOR,
        RecommendationStatus.HUMAN_REVIEW,
    )
    assert rec.data_adequacy == DataAdequacy.GOOD
