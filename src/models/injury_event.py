"""
SPORTZA Injury Event Research Model & Descriptive Analytics

Gated research-oriented injury association / risk modeling.
Strictly non-diagnostic: evaluates whether past workload/wellness indicators
exhibit statistical associations with subsequent self-reported injury notifications.
"""
from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    confusion_matrix,
    precision_recall_fscore_support,
    roc_auc_score,
)
from sklearn.model_selection import GroupKFold


class InjuryEventAnalyzer:
    """Injury risk research model gated by strict pre-flight data checks."""

    MIN_EVENTS_FOR_MODEL: int = 30
    MIN_PLAYERS: int = 5

    def __init__(self, random_seed: int = 42):
        self.seed = random_seed
        self.model: LogisticRegression | None = None
        self.feature_names: list[str] = []
        self.is_trained: bool = False
        self.metrics: dict[str, Any] = {}

    def check_data_sufficiency(self, injury_df: pd.DataFrame) -> dict[str, Any]:
        """Pre-flight check: determine if event counts allow defensible risk modeling."""
        if injury_df.empty:
            return {
                "sufficient": False,
                "reason": "No injury reports present in dataset.",
                "total_events": 0,
                "unique_players": 0,
            }
        
        n_events = len(injury_df)
        n_players = injury_df["player_id"].nunique()
        
        sufficient = (n_events >= self.MIN_EVENTS_FOR_MODEL) and (n_players >= self.MIN_PLAYERS)
        reason = (
            "Sufficient independent reports for exploratory research modeling."
            if sufficient
            else f"Insufficient sample size ({n_events} events, {n_players} players; "
                 f"minimum threshold is {self.MIN_EVENTS_FOR_MODEL} events and {self.MIN_PLAYERS} players). "
                 "Risk model disabled to prevent severe overfitting. Descriptive analysis active."
        )
        return {
            "sufficient": sufficient,
            "reason": reason,
            "total_events": n_events,
            "unique_players": n_players,
        }

    def build_descriptive_analysis(
        self,
        injury_df: pd.DataFrame,
        wellness_df: pd.DataFrame | None = None
    ) -> dict[str, Any]:
        """Always-available descriptive statistics and body-location breakdown."""
        if injury_df.empty:
            return {
                "total_reports": 0,
                "locations": {},
                "severity_counts": {},
                "by_player": {},
            }

        locations = injury_df["body_location"].value_counts().to_dict()
        severities = injury_df["reported_severity"].value_counts().to_dict() if "reported_severity" in injury_df.columns else {}
        by_player = injury_df["player_id"].value_counts().to_dict()

        return {
            "total_reports": len(injury_df),
            "locations": locations,
            "severity_counts": severities,
            "by_player": by_player,
            "top_location": next(iter(locations.keys()), None),
        }

    def train_risk_model(
        self,
        features: pd.DataFrame,
        target: pd.Series,
        player_groups: pd.Series,
    ) -> dict[str, Any] | None:
        """Train cross-validated logistic regression model with group-aware splitting.
        
        Evaluated strictly against naive prevalence baseline.
        """
        n_positives = int(target.sum())
        if n_positives < self.MIN_EVENTS_FOR_MODEL or len(np.unique(player_groups)) < self.MIN_PLAYERS:
            return None

        # Clean NaNs
        clean_mask = features.notna().all(axis=1) & target.notna() & player_groups.notna()
        X = features.loc[clean_mask].copy()
        y = target.loc[clean_mask].astype(int)
        groups = player_groups.loc[clean_mask]

        if len(y.unique()) < 2:
            return None

        self.feature_names = list(X.columns)
        n_splits = min(5, len(np.unique(groups)))
        gkf = GroupKFold(n_splits=n_splits)

        y_true_all = []
        y_prob_all = []

        for train_idx, test_idx in gkf.split(X, y, groups):
            X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
            y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

            if len(np.unique(y_train)) < 2:
                continue

            clf = LogisticRegression(class_weight="balanced", random_state=self.seed, max_iter=500)
            clf.fit(X_train, y_train)
            probs = clf.predict_proba(X_test)[:, 1]

            y_true_all.extend(y_test)
            y_prob_all.extend(probs)

        if not y_true_all:
            return None

        y_true = np.array(y_true_all)
        y_prob = np.array(y_prob_all)
        y_pred = (y_prob >= 0.5).astype(int)

        prevalence = float(np.mean(y_true))
        prec, rec, f1, _ = precision_recall_fscore_support(y_true, y_pred, average="binary", zero_division=0)
        try:
            auc = float(roc_auc_score(y_true, y_prob))
        except ValueError:
            auc = 0.5

        cm = confusion_matrix(y_true, y_pred).tolist()

        # Fit final model on full set
        self.model = LogisticRegression(class_weight="balanced", random_state=self.seed, max_iter=500)
        self.model.fit(X, y)
        self.is_trained = True

        self.metrics = {
            "prevalence": round(prevalence, 4),
            "naive_baseline_accuracy": round(1.0 - prevalence, 4),
            "precision": round(float(prec), 4),
            "recall": round(float(rec), 4),
            "f1": round(float(f1), 4),
            "roc_auc": round(auc, 4),
            "confusion_matrix": cm,
            "disclaimer": "Research estimate based on reported historical patterns; not a clinical assessment.",
        }
        return self.metrics
