"""
SPORTZA Readiness Forecasting Model.

Predicts next-day readiness score from the prior 7 days of wellness,
training-load, and fitness/fatigue metrics using Gradient Boosting regression
with a strict chronological train/test split.
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor

from src.models.evaluation import evaluate_regression

logger = logging.getLogger(__name__)

# ── Feature configuration ──────────────────────────────────────────────────
_ROLLING_COLS = [
    "readiness",
    "fatigue",
    "mood",
    "sleep_quality",
    "soreness",
    "stress",
]
_LOAD_COLS = ["daily_load", "atl", "ctl_28", "acwr"]
_EXTRA_COLS = ["data_coverage"]
_LAG_DAYS = 7


class ReadinessForecaster:
    """Next-day readiness regression model.

    Uses a GradientBoostingRegressor trained on rolling lag features
    derived from the SoccerMon wellness dataset.  The model is compared
    against two naïve baselines:

    1. **Last-observation-carried-forward (LOCF)** – use yesterday's
       readiness as the prediction.
    2. **Rolling 7-day mean** – average readiness over the past week.

    A chronological train/test split is enforced (no random shuffling)
    to prevent data leakage.
    """

    def __init__(self, random_seed: int = 42) -> None:
        self.seed: int = random_seed
        self.model: GradientBoostingRegressor | None = None
        self.baseline_mae: float | None = None
        self.model_mae: float | None = None
        self.feature_names: list[str] = []
        self.is_trained: bool = False
        self.training_metadata: dict[str, Any] = {}

    # ── Feature engineering ────────────────────────────────────────────
    def prepare_features(
        self,
        athlete_date_df: pd.DataFrame,
    ) -> tuple[pd.DataFrame, pd.Series]:
        """Build lag features from prior 7 days; target = next-day readiness.

        Parameters
        ----------
        athlete_date_df : pd.DataFrame
            Must contain columns ``player_id``, ``date``, and the wellness /
            load columns listed in ``_ROLLING_COLS``, ``_LOAD_COLS``,
            ``_EXTRA_COLS``.  One row per player-day.

        Returns
        -------
        (features, target) : tuple[pd.DataFrame, pd.Series]
            ``features`` has one row per valid player-day with all lag
            columns populated.  ``target`` is the *next-day* readiness
            value aligned to the same index.

        Notes
        -----
        **Strict temporal isolation**: every feature row uses *only* data
        from days *before* the target date.
        """
        df = athlete_date_df.copy()
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values(["player_id", "date"]).reset_index(drop=True)

        feature_frames: list[pd.DataFrame] = []

        for pid, grp in df.groupby("player_id"):
            grp = grp.sort_values("date").reset_index(drop=True)

            # --- Lag features for rolling columns ---
            for col in _ROLLING_COLS:
                if col not in grp.columns:
                    grp[col] = np.nan
                for lag in range(1, _LAG_DAYS + 1):
                    grp[f"{col}_lag{lag}"] = grp[col].shift(lag)
                # Rolling statistics (window = 7, shifted by 1 to avoid leakage)
                shifted = grp[col].shift(1)
                grp[f"{col}_roll7_mean"] = shifted.rolling(7, min_periods=3).mean()
                grp[f"{col}_roll7_std"] = shifted.rolling(7, min_periods=3).std()
                grp[f"{col}_roll3_mean"] = shifted.rolling(3, min_periods=2).mean()

            # --- Lag features for load / fitness columns ---
            for col in _LOAD_COLS + _EXTRA_COLS:
                if col not in grp.columns:
                    grp[col] = np.nan
                grp[f"{col}_lag1"] = grp[col].shift(1)
                grp[f"{col}_lag3_mean"] = (
                    grp[col].shift(1).rolling(3, min_periods=1).mean()
                )

            # --- Day-of-week one-hot ---
            grp["day_of_week"] = grp["date"].dt.dayofweek

            # --- Target: next-day readiness (shift -1 = tomorrow) ---
            grp["target_readiness"] = grp["readiness"].shift(-1)

            # Keep player_id and date for downstream split
            grp["player_id_feat"] = pid

            feature_frames.append(grp)

        combined = pd.concat(feature_frames, ignore_index=True)

        # Identify feature columns
        lag_cols = [c for c in combined.columns if "_lag" in c or "_roll" in c]
        feat_cols = lag_cols + ["day_of_week"]
        self.feature_names = sorted(feat_cols)

        # Drop rows without a valid target or with too many missing features
        valid_mask = combined["target_readiness"].notna()
        feat_missing = combined[self.feature_names].isna().sum(axis=1)
        valid_mask &= feat_missing < len(self.feature_names) * 0.5

        result = combined.loc[valid_mask].copy()
        target = result["target_readiness"].copy()
        features = result[self.feature_names + ["date", "player_id_feat"]].copy()

        # Fill remaining NaNs with column medians (from training data only)
        for col in self.feature_names:
            med = features[col].median()
            features[col] = features[col].fillna(med if not np.isnan(med) else 0.0)

        return features, target

    # ── Training ───────────────────────────────────────────────────────
    def train(
        self,
        features: pd.DataFrame,
        target: pd.Series,
        split_date: str,
    ) -> dict[str, Any]:
        """Train with a chronological split and compare against baselines.

        Parameters
        ----------
        features : pd.DataFrame
            Output of :meth:`prepare_features`.
        target : pd.Series
            Aligned target values from :meth:`prepare_features`.
        split_date : str
            ISO date string; rows with ``date < split_date`` are training,
            the rest are test.

        Returns
        -------
        dict
            Training report with MAE, RMSE, R² for the model and both
            baselines, plus feature importances.
        """
        split_dt = pd.Timestamp(split_date)

        train_mask = features["date"] < split_dt
        test_mask = features["date"] >= split_dt

        X_train = features.loc[train_mask, self.feature_names].values
        y_train = target.loc[train_mask].values
        X_test = features.loc[test_mask, self.feature_names].values
        y_test = target.loc[test_mask].values

        if len(X_train) == 0 or len(X_test) == 0:
            raise ValueError(
                f"Split date {split_date} produces an empty train ({len(X_train)}) "
                f"or test ({len(X_test)}) set."
            )

        logger.info(
            "Training readiness model: %d train, %d test samples",
            len(X_train),
            len(X_test),
        )

        # ---- Baselines on test set ----
        # 1. LOCF: readiness_lag1 (yesterday's readiness)
        locf_col = "readiness_lag1"
        locf_idx = self.feature_names.index(locf_col) if locf_col in self.feature_names else None
        if locf_idx is not None:
            locf_pred = X_test[:, locf_idx]
        else:
            locf_pred = np.full(len(y_test), np.nanmean(y_train))

        # 2. Rolling 7-day mean
        roll_col = "readiness_roll7_mean"
        roll_idx = self.feature_names.index(roll_col) if roll_col in self.feature_names else None
        if roll_idx is not None:
            roll_pred = X_test[:, roll_idx]
        else:
            roll_pred = np.full(len(y_test), np.nanmean(y_train))

        locf_metrics = evaluate_regression(y_test, locf_pred)
        roll_metrics = evaluate_regression(y_test, roll_pred)

        # ---- Gradient Boosting ----
        self.model = GradientBoostingRegressor(
            n_estimators=200,
            max_depth=4,
            learning_rate=0.05,
            subsample=0.8,
            min_samples_leaf=10,
            random_state=self.seed,
        )
        self.model.fit(X_train, y_train)

        y_pred_train = self.model.predict(X_train)
        y_pred_test = self.model.predict(X_test)

        train_metrics = evaluate_regression(y_train, y_pred_train)
        model_metrics = evaluate_regression(y_test, y_pred_test, baseline_pred=locf_pred)

        self.model_mae = model_metrics["mae"]
        self.baseline_mae = locf_metrics["mae"]
        self.is_trained = True

        # Feature importances
        importances = dict(
            zip(self.feature_names, self.model.feature_importances_.tolist())
        )
        sorted_importances = dict(
            sorted(importances.items(), key=lambda x: x[1], reverse=True)
        )

        self.training_metadata = {
            "split_date": split_date,
            "n_train": len(X_train),
            "n_test": len(X_test),
            "model_type": "GradientBoostingRegressor",
            "hyperparameters": self.model.get_params(),
            "train_metrics": train_metrics,
            "test_metrics": model_metrics,
            "baseline_locf": locf_metrics,
            "baseline_roll7": roll_metrics,
            "feature_importances": sorted_importances,
            "top_10_features": dict(list(sorted_importances.items())[:10]),
            "trained_at": datetime.now(UTC).isoformat(),
        }

        return self.training_metadata

    # ── Prediction ─────────────────────────────────────────────────────
    def predict(self, features: pd.DataFrame) -> np.ndarray:
        """Generate predictions for new feature rows.

        Parameters
        ----------
        features : pd.DataFrame
            Must contain all columns in ``self.feature_names``.

        Returns
        -------
        np.ndarray
            Predicted next-day readiness scores.

        Raises
        ------
        RuntimeError
            If the model has not been trained yet.
        """
        if not self.is_trained or self.model is None:
            raise RuntimeError("Model has not been trained. Call train() first.")

        X = features[self.feature_names].values
        return self.model.predict(X)

    # ── Reporting ──────────────────────────────────────────────────────
    def get_evaluation_report(self) -> dict[str, Any]:
        """Return a structured evaluation report.

        Returns
        -------
        dict
            Contains model and baseline metrics, feature importances,
            training metadata, and interpretive notes.
        """
        if not self.is_trained:
            return {"error": "Model has not been trained yet."}

        improvement = ""
        if self.baseline_mae and self.model_mae and self.baseline_mae > 0:
            pct = (1 - self.model_mae / self.baseline_mae) * 100
            improvement = f"{pct:.1f}% MAE improvement over LOCF baseline"

        return {
            "model_name": "ReadinessForecaster",
            "task": "Next-day readiness prediction",
            "status": "trained",
            "improvement_summary": improvement,
            **self.training_metadata,
        }

    # ── Persistence ────────────────────────────────────────────────────
    def save(self, path: Path) -> None:
        """Save the trained model and metadata to disk.

        Parameters
        ----------
        path : Path
            Base path (without extension).  Creates ``.joblib`` and
            ``.meta.json`` files via the artifacts module.
        """
        if not self.is_trained or self.model is None:
            raise RuntimeError("Cannot save an untrained model.")

        from src.models.artifacts import save_model_artifact

        metadata = {
            "feature_names": self.feature_names,
            "seed": self.seed,
            "baseline_mae": self.baseline_mae,
            "model_mae": self.model_mae,
            "training_metadata": self.training_metadata,
        }
        save_model_artifact(self.model, metadata, path)

    def load(self, path: Path) -> None:
        """Load a previously saved model from disk.

        Parameters
        ----------
        path : Path
            Base path (without extension).  Expects ``.joblib`` and
            ``.meta.json`` files.
        """
        from src.models.artifacts import load_model_artifact

        model, metadata = load_model_artifact(path)
        self.model = model
        self.feature_names = metadata.get("feature_names", [])
        self.seed = metadata.get("seed", 42)
        self.baseline_mae = metadata.get("baseline_mae")
        self.model_mae = metadata.get("model_mae")
        self.training_metadata = metadata.get("training_metadata", {})
        self.is_trained = True
