"""
SPORTZA Game Performance Forecasting Module

Forecasts post-match player-reported ratings (team, offensive, defensive)
using chronological splits and strict baseline comparisons.
"""
from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, root_mean_squared_error


class GamePerformanceForecaster:
    """Forecaster for self-reported match performance ratings."""

    MIN_SAMPLES: int = 40

    def __init__(self, random_seed: int = 42):
        self.seed = random_seed
        self.model: GradientBoostingRegressor | None = None
        self.feature_names: list[str] = []
        self.is_trained: bool = False
        self.metrics: dict[str, Any] = {}

    def prepare_match_features(
        self,
        game_df: pd.DataFrame,
        athlete_features_df: pd.DataFrame,
        target_col: str = "team_performance",
    ) -> tuple[pd.DataFrame, pd.Series]:
        """Align prior point-in-time wellness/workload features with match date ratings."""
        if game_df.empty or athlete_features_df.empty:
            return pd.DataFrame(), pd.Series(dtype=float)

        gdf = game_df.copy()
        date_col = "match_timestamp" if "match_timestamp" in gdf.columns else ("date" if "date" in gdf.columns else "session_date")
        if date_col not in gdf.columns:
            return pd.DataFrame(), pd.Series(dtype=float)
        gdf["match_date"] = pd.to_datetime(gdf[date_col]).dt.normalize()
        
        adf = athlete_features_df.copy()
        adf["date"] = pd.to_datetime(adf["date"]).dt.normalize()

        # Merge on player and date
        merged = pd.merge(
            gdf,
            adf,
            left_on=["player_id", "match_date"],
            right_on=["player_id", "date"],
            how="inner",
        )

        candidate_features = [
            "readiness", "fatigue", "mood", "sleep_duration_hours",
            "sleep_quality", "soreness", "stress",
            "daily_load", "weekly_load", "atl", "ctl_28", "acwr"
        ]
        available_features = [c for c in candidate_features if c in merged.columns]

        if target_col not in merged.columns or len(available_features) == 0:
            return pd.DataFrame(), pd.Series(dtype=float)

        clean = merged[available_features + [target_col, "match_date"]].dropna()
        clean = clean.sort_values("match_date")

        X = clean[available_features]
        y = clean[target_col]
        return X, y

    def train_chronological(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        train_ratio: float = 0.75,
    ) -> dict[str, Any] | None:
        """Train model using strictly chronological holdout split."""
        if len(X) < self.MIN_SAMPLES:
            return {
                "trained": False,
                "reason": f"Sample size ({len(X)}) is below minimum required ({self.MIN_SAMPLES}) for reliable validation.",
            }

        split_idx = int(len(X) * train_ratio)
        X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
        y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]

        # Baseline 1: Mean baseline
        mean_pred = np.full(len(y_test), y_train.mean())
        base_mae = float(mean_absolute_error(y_test, mean_pred))
        base_rmse = float(root_mean_squared_error(y_test, mean_pred))

        # Model: Gradient Boosting
        self.model = GradientBoostingRegressor(
            n_estimators=50, max_depth=3, random_state=self.seed
        )
        self.model.fit(X_train, y_train)
        y_pred = self.model.predict(X_test)

        model_mae = float(mean_absolute_error(y_test, y_pred))
        model_rmse = float(root_mean_squared_error(y_test, y_pred))

        self.feature_names = list(X.columns)
        self.is_trained = True
        self.metrics = {
            "trained": True,
            "train_samples": len(X_train),
            "test_samples": len(X_test),
            "baseline_mean_mae": round(base_mae, 3),
            "baseline_mean_rmse": round(base_rmse, 3),
            "model_mae": round(model_mae, 3),
            "model_rmse": round(model_rmse, 3),
            "mae_improvement": round(base_mae - model_mae, 3),
            "feature_importance": dict(zip(X.columns, [round(float(v), 4) for v in self.model.feature_importances_])),
        }
        return self.metrics
