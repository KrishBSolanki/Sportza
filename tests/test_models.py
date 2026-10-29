"""Unit tests for ML models and evaluation."""
import numpy as np
import pandas as pd

from src.data.demo_generator import generate_demo_data
from src.features.temporal import build_athlete_date_features
from src.models.evaluation import evaluate_classification, evaluate_regression
from src.models.injury_event import InjuryEventAnalyzer
from src.models.readiness import ReadinessForecaster


def test_evaluate_regression():
    y_true = np.array([5.0, 6.0, 7.0, 8.0])
    y_pred = np.array([5.1, 5.9, 7.2, 7.8])
    y_base = np.array([6.5, 6.5, 6.5, 6.5])

    res = evaluate_regression(y_true, y_pred, baseline_pred=y_base)
    assert res["mae"] < res["baseline"]["mae"]
    assert res["rmse"] < res["baseline"]["rmse"]


def test_evaluate_classification():
    y_true = np.array([0, 0, 1, 1])
    y_prob = np.array([0.1, 0.2, 0.8, 0.9])

    res = evaluate_classification(y_true, y_prob)
    assert res["precision"] == 1.0
    assert res["recall"] == 1.0
    assert res["f1"] == 1.0


def test_readiness_forecaster_train():
    demo = generate_demo_data()
    adf = build_athlete_date_features(
        demo["wellness_daily"],
        demo["training_sessions"],
        demo["injury_events"],
        demo["illness_events"],
    )
    forecaster = ReadinessForecaster()
    features, target = forecaster.prepare_features(adf)
    assert not features.empty
    assert len(target) == len(features)

    # Chronological train
    split_date = "2021-06-01"
    metrics = forecaster.train(features, target, split_date=split_date)
    assert forecaster.is_trained
    assert "test_metrics" in metrics and "mae" in metrics["test_metrics"]
    assert "baseline_locf" in metrics and "mae" in metrics["baseline_locf"]


def test_injury_analyzer_sufficiency_gate():
    analyzer = InjuryEventAnalyzer()
    small_injuries = pd.DataFrame({
        "player_id": ["P1", "P2"],
        "body_location": ["knee", "ankle"],
    })
    check = analyzer.check_data_sufficiency(small_injuries)
    assert check["sufficient"] is False
    assert "Insufficient" in check["reason"]
