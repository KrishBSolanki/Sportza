"""
SPORTZA Model Evaluation Utilities.

Provides standardized evaluation functions for regression and classification
models, plus model card generation for transparency and documentation.
"""

from __future__ import annotations

from typing import Any

import numpy as np
from sklearn.metrics import (
    auc,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    precision_recall_curve,
    precision_score,
    r2_score,
    recall_score,
)


def evaluate_regression(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    baseline_pred: np.ndarray | None = None,
) -> dict[str, Any]:
    """Evaluate a regression model with MAE, RMSE, R² and optional baseline comparison.

    Parameters
    ----------
    y_true : np.ndarray
        Ground-truth target values.
    y_pred : np.ndarray
        Model predictions.
    baseline_pred : np.ndarray, optional
        Baseline predictions (e.g. LOCF or rolling mean) for comparison.

    Returns
    -------
    dict
        Dictionary with model metrics and, if provided, baseline metrics and
        improvement ratios.
    """
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)

    # Remove NaN pairs
    mask = ~(np.isnan(y_true) | np.isnan(y_pred))
    y_true_clean = y_true[mask]
    y_pred_clean = y_pred[mask]

    if len(y_true_clean) == 0:
        return {
            "n_samples": 0,
            "mae": np.nan,
            "rmse": np.nan,
            "r2": np.nan,
            "error": "No valid samples after removing NaNs",
        }

    mae = float(mean_absolute_error(y_true_clean, y_pred_clean))
    rmse = float(np.sqrt(mean_squared_error(y_true_clean, y_pred_clean)))
    r2 = float(r2_score(y_true_clean, y_pred_clean))

    result: dict[str, Any] = {
        "n_samples": len(y_true_clean),
        "mae": round(mae, 4),
        "rmse": round(rmse, 4),
        "r2": round(r2, 4),
    }

    if baseline_pred is not None:
        baseline_pred = np.asarray(baseline_pred, dtype=float)
        baseline_mask = mask & ~np.isnan(baseline_pred)
        y_true_b = y_true[baseline_mask]
        y_pred_b = y_pred[baseline_mask]
        baseline_b = baseline_pred[baseline_mask]

        if len(y_true_b) > 0:
            baseline_mae = float(mean_absolute_error(y_true_b, baseline_b))
            baseline_rmse = float(
                np.sqrt(mean_squared_error(y_true_b, baseline_b))
            )
            baseline_r2 = float(r2_score(y_true_b, baseline_b))

            model_mae_b = float(mean_absolute_error(y_true_b, y_pred_b))

            result["baseline"] = {
                "mae": round(baseline_mae, 4),
                "rmse": round(baseline_rmse, 4),
                "r2": round(baseline_r2, 4),
            }
            if baseline_mae > 0:
                result["mae_improvement_pct"] = round(
                    (1 - model_mae_b / baseline_mae) * 100, 2
                )
            else:
                result["mae_improvement_pct"] = 0.0

    return result


def evaluate_classification(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    threshold: float = 0.5,
) -> dict[str, Any]:
    """Evaluate a binary classification model with precision, recall, F1, PR-AUC.

    Parameters
    ----------
    y_true : np.ndarray
        Binary ground-truth labels (0 or 1).
    y_prob : np.ndarray
        Predicted probabilities for the positive class.
    threshold : float
        Decision threshold for converting probabilities to labels.

    Returns
    -------
    dict
        Dictionary with classification metrics and prevalence.
    """
    y_true = np.asarray(y_true, dtype=int)
    y_prob = np.asarray(y_prob, dtype=float)

    # Remove NaN pairs
    mask = ~(np.isnan(y_true.astype(float)) | np.isnan(y_prob))
    y_true_clean = y_true[mask]
    y_prob_clean = y_prob[mask]

    if len(y_true_clean) == 0:
        return {
            "n_samples": 0,
            "prevalence": np.nan,
            "error": "No valid samples after removing NaNs",
        }

    prevalence = float(np.mean(y_true_clean))
    y_pred_labels = (y_prob_clean >= threshold).astype(int)

    n_positive = int(y_true_clean.sum())
    n_negative = int(len(y_true_clean) - n_positive)

    # Handle edge cases for metrics
    if n_positive == 0 or n_negative == 0:
        return {
            "n_samples": len(y_true_clean),
            "n_positive": n_positive,
            "n_negative": n_negative,
            "prevalence": round(prevalence, 4),
            "warning": "Only one class present in y_true; metrics unreliable.",
            "precision": np.nan,
            "recall": np.nan,
            "f1": np.nan,
            "pr_auc": np.nan,
        }

    prec = float(precision_score(y_true_clean, y_pred_labels, zero_division=0))
    rec = float(recall_score(y_true_clean, y_pred_labels, zero_division=0))
    f1 = float(f1_score(y_true_clean, y_pred_labels, zero_division=0))

    # PR-AUC
    precision_curve, recall_curve, _ = precision_recall_curve(
        y_true_clean, y_prob_clean
    )
    pr_auc = float(auc(recall_curve, precision_curve))

    return {
        "n_samples": len(y_true_clean),
        "n_positive": n_positive,
        "n_negative": n_negative,
        "prevalence": round(prevalence, 4),
        "threshold": threshold,
        "precision": round(prec, 4),
        "recall": round(rec, 4),
        "f1": round(f1, 4),
        "pr_auc": round(pr_auc, 4),
        "baseline_f1_random": round(2 * prevalence / (1 + prevalence), 4),
    }


def generate_model_card(
    model_name: str,
    task: str,
    metrics: dict[str, Any],
    limitations: list[str],
    data_description: str,
) -> str:
    """Generate a Markdown model card for transparency and documentation.

    Parameters
    ----------
    model_name : str
        Human-readable name of the model.
    task : str
        Description of the prediction task.
    metrics : dict
        Evaluation metrics dictionary.
    limitations : list of str
        Known limitations and caveats.
    data_description : str
        Description of training data source and size.

    Returns
    -------
    str
        Formatted Markdown model card.
    """
    lines = [
        f"# Model Card: {model_name}",
        "",
        "## Task",
        f"{task}",
        "",
        "## Data",
        f"{data_description}",
        "",
        "## Metrics",
        "",
        "| Metric | Value |",
        "|--------|-------|",
    ]

    for key, value in metrics.items():
        if isinstance(value, dict):
            for sub_key, sub_value in value.items():
                lines.append(f"| {key}.{sub_key} | {sub_value} |")
        else:
            lines.append(f"| {key} | {value} |")

    lines.extend(["", "## Limitations", ""])
    for limitation in limitations:
        lines.append(f"- {limitation}")

    lines.extend(
        [
            "",
            "## Intended Use",
            "",
            "This model is intended for **research and coaching support** only.",
            "It should NOT be used as the sole basis for medical, selection,",
            "or contractual decisions.",
            "",
            "---",
            "*Generated by SPORTZA Analytics Platform*",
        ]
    )

    return "\n".join(lines)
