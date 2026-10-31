"""Transparent, configurable rules-based decision engine.

Evaluates a player's current wellness / workload state against their personal
baseline and produces an auditable recommendation with human-readable
rationale.  Every recommendation carries the non-medical disclaimer.
"""

from dataclasses import dataclass
from datetime import timedelta
from enum import Enum

import numpy as np
import pandas as pd

from .baseline import PersonalBaseline

# ======================================================================
# Enums & data classes
# ======================================================================

class RecommendationStatus(Enum):
    """Possible recommendation outcomes."""

    MONITOR = "Monitor"
    RECOVERY_FOCUSED = "Recovery-focused option"
    HUMAN_REVIEW = "Human review needed"
    INSUFFICIENT_DATA = "Insufficient data"


class DataAdequacy(Enum):
    """Describes how much data the engine had to work with."""

    GOOD = "Good - sufficient recent observations"
    LIMITED = "Limited - some data gaps"
    INSUFFICIENT = "Insufficient - too few observations for reliable assessment"


@dataclass
class ObservedFactor:
    """A single wellness / workload factor evaluated by the engine."""

    name: str
    current_value: float | None
    baseline_value: float | None
    deviation: float | None  # z-score
    direction: str  # 'higher_is_better' or 'higher_is_worse'
    interpretation: str  # human-readable description


@dataclass
class Recommendation:
    """Full recommendation output for one player on one date."""

    player_id: str
    date: str
    status: RecommendationStatus
    observed_factors: list[ObservedFactor]
    baseline_comparison_period: str
    recommendation_text: str
    rationale: list[str]
    what_system_cannot_infer: list[str]
    suggested_review_window: str
    data_adequacy: DataAdequacy
    escalation_flags: list[str]
    non_medical_note: str = (
        "This is a non-medical, non-diagnostic decision-support tool. "
        "All suggestions should be reviewed by a qualified sports "
        "clinician or coach before implementation."
    )


# ======================================================================
# Engine
# ======================================================================

class DecisionEngine:
    """Transparent rules-based decision engine for recovery / training
    recommendations.

    All thresholds are expressed relative to the player's own baseline
    so that recommendations are personalised.
    """

    # Configurable thresholds (standard deviations from personal baseline)
    DEVIATION_THRESHOLD_MODERATE: float = 0.5
    DEVIATION_THRESHOLD_SIGNIFICANT: float = 1.0

    # Baseline parameters
    MIN_BASELINE_OBSERVATIONS: int = 7
    BASELINE_WINDOW_DAYS: int = 28

    # Scale directions
    HIGHER_IS_BETTER: list[str] = [
        "readiness",
        "mood",
        "sleep_quality",
        "sleep_duration_hours",
    ]
    HIGHER_IS_WORSE: list[str] = [
        "fatigue",
        "soreness",
        "stress",
    ]

    # Workload column expected in training_history
    WORKLOAD_COL: str = "daily_load"
    WORKLOAD_TREND_WINDOW: int = 7  # days for short-term workload trend

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #
    def evaluate(
        self,
        player_id: str,
        current_date: str,
        wellness_history: pd.DataFrame,
        training_history: pd.DataFrame,
        injury_history: pd.DataFrame,
        illness_history: pd.DataFrame,
    ) -> Recommendation:
        """Produce a recommendation for *player_id* on *current_date*.

        Parameters
        ----------
        player_id : str
            Unique player identifier.
        current_date : str
            ISO-format date string (``YYYY-MM-DD``).
        wellness_history : pd.DataFrame
            Must contain columns: ``date`` plus wellness metric columns
            (readiness, mood, sleep_quality, sleep_duration_hours,
            fatigue, soreness, stress).  One row per day.
        training_history : pd.DataFrame
            Must contain columns: ``date``, ``daily_load``.
        injury_history : pd.DataFrame
            Must contain columns: ``date``, ``body_part``, ``severity``.
        illness_history : pd.DataFrame
            Must contain columns: ``date``, ``type``, ``severity``.

        Returns
        -------
        Recommendation
        """
        cur_dt = pd.Timestamp(current_date)

        # ---- Step 1: Check data adequacy --------------------------------
        adequacy, adequacy_detail = self._assess_data_adequacy(
            wellness_history, cur_dt
        )
        if adequacy == DataAdequacy.INSUFFICIENT:
            return self._insufficient_data_recommendation(
                player_id, current_date, adequacy_detail
            )

        # ---- Step 2 & 3: Compute baseline & compare ---------------------
        wellness_metrics = [
            m for m in self.HIGHER_IS_BETTER + self.HIGHER_IS_WORSE
            if m in wellness_history.columns
        ]
        observed_factors, baseline_period = self._compute_factors(
            wellness_history, wellness_metrics, cur_dt
        )

        # ---- Step 4: Check recent injury / illness ----------------------
        recent_injury = self._check_recent_injury(injury_history, cur_dt)
        recent_illness = self._check_recent_illness(illness_history, cur_dt)

        # ---- Step 5: Check workload trend --------------------------------
        workload_rising = self._check_workload_trend(training_history, cur_dt)

        # ---- Step 6: Apply priority rules --------------------------------
        return self._apply_rules(
            player_id=player_id,
            current_date=current_date,
            observed_factors=observed_factors,
            baseline_period=baseline_period,
            recent_injury=recent_injury,
            recent_illness=recent_illness,
            workload_rising=workload_rising,
            data_adequacy=adequacy,
        )

    # ------------------------------------------------------------------ #
    # Internal helpers
    # ------------------------------------------------------------------ #

    def _assess_data_adequacy(
        self, wellness: pd.DataFrame, cur_dt: pd.Timestamp
    ) -> tuple[DataAdequacy, str]:
        """Determine whether we have enough data to make a recommendation."""
        if wellness is None or wellness.empty:
            return DataAdequacy.INSUFFICIENT, "No wellness data available."

        if "date" not in wellness.columns:
            return DataAdequacy.INSUFFICIENT, "Wellness data missing 'date' column."

        wellness = wellness.copy()
        wellness["date"] = pd.to_datetime(wellness["date"])
        window_start = cur_dt - timedelta(days=self.BASELINE_WINDOW_DAYS)
        in_window = wellness[
            (wellness["date"] >= window_start) & (wellness["date"] <= cur_dt)
        ]

        n_days = len(in_window)
        if n_days < self.MIN_BASELINE_OBSERVATIONS:
            return (
                DataAdequacy.INSUFFICIENT,
                f"Only {n_days} day(s) of data in the last "
                f"{self.BASELINE_WINDOW_DAYS} days "
                f"(minimum {self.MIN_BASELINE_OBSERVATIONS} required).",
            )

        # Check metric coverage
        metric_cols = [
            c
            for c in self.HIGHER_IS_BETTER + self.HIGHER_IS_WORSE
            if c in in_window.columns
        ]
        if not metric_cols:
            return DataAdequacy.INSUFFICIENT, "No recognised wellness metric columns."

        non_null_counts = in_window[metric_cols].notna().sum()
        all_sufficient = (non_null_counts >= self.MIN_BASELINE_OBSERVATIONS).all()

        if all_sufficient:
            return DataAdequacy.GOOD, "Sufficient recent data."
        return DataAdequacy.LIMITED, "Some metrics have fewer observations than ideal."

    # ------------------------------------------------------------------ #
    def _compute_factors(
        self,
        wellness: pd.DataFrame,
        metrics: list[str],
        cur_dt: pd.Timestamp,
    ) -> tuple[list[ObservedFactor], str]:
        """Compute personal baseline and current deviation for each metric."""
        wellness = wellness.copy()
        wellness["date"] = pd.to_datetime(wellness["date"])
        wellness = wellness.sort_values("date")

        window_start = cur_dt - timedelta(days=self.BASELINE_WINDOW_DAYS)

        # Baseline data: everything in the window *before* current date
        baseline_data = wellness[
            (wellness["date"] >= window_start) & (wellness["date"] < cur_dt)
        ]
        # Current day row(s)
        current_data = wellness[wellness["date"] == cur_dt]

        baseline_period = (
            f"{window_start.strftime('%Y-%m-%d')} to "
            f"{(cur_dt - timedelta(days=1)).strftime('%Y-%m-%d')}"
        )

        factors: list[ObservedFactor] = []
        for metric in metrics:
            direction = (
                "higher_is_better"
                if metric in self.HIGHER_IS_BETTER
                else "higher_is_worse"
            )

            # Current value
            current_val: float | None = None
            if not current_data.empty and metric in current_data.columns:
                raw = current_data[metric].iloc[-1]
                current_val = None if pd.isna(raw) else float(raw)

            # Baseline
            if metric in baseline_data.columns:
                series = baseline_data.set_index("date")[metric]
            else:
                series = pd.Series(dtype=float)

            baseline_result, z_score = PersonalBaseline.evaluate_metric(
                series,
                current_val,
                window=self.BASELINE_WINDOW_DAYS,
                min_obs=self.MIN_BASELINE_OBSERVATIONS,
            )

            interpretation = self._interpret_factor(
                metric, current_val, baseline_result.mean, z_score, direction
            )

            factors.append(
                ObservedFactor(
                    name=metric,
                    current_value=current_val,
                    baseline_value=baseline_result.mean,
                    deviation=z_score,
                    direction=direction,
                    interpretation=interpretation,
                )
            )

        return factors, baseline_period

    # ------------------------------------------------------------------ #
    def _interpret_factor(
        self,
        name: str,
        current: float | None,
        baseline_mean: float | None,
        z_score: float | None,
        direction: str,
    ) -> str:
        """Generate a human-readable interpretation of one factor."""
        pretty = name.replace("_", " ").title()

        if current is None:
            return f"{pretty}: no current observation available."
        if baseline_mean is None or z_score is None:
            return f"{pretty}: current value {current:.1f}, insufficient baseline data for comparison."

        abs_z = abs(z_score)
        if abs_z < self.DEVIATION_THRESHOLD_MODERATE:
            return (
                f"{pretty}: {current:.1f} (baseline {baseline_mean:.1f}) — "
                f"within normal range."
            )

        # Determine if the deviation is *adverse*
        if direction == "higher_is_better":
            adverse = z_score < 0  # below baseline is bad
        else:
            adverse = z_score > 0  # above baseline is bad

        severity = (
            "significantly" if abs_z >= self.DEVIATION_THRESHOLD_SIGNIFICANT else "moderately"
        )
        trend = "worse than" if adverse else "better than"

        return (
            f"{pretty}: {current:.1f} (baseline {baseline_mean:.1f}) — "
            f"{severity} {trend} baseline ({abs_z:.1f} SD)."
        )

    # ------------------------------------------------------------------ #
    def _check_recent_injury(
        self, injury_df: pd.DataFrame, cur_dt: pd.Timestamp
    ) -> str | None:
        """Return a description if there is a recent major injury."""
        if injury_df is None or injury_df.empty:
            return None

        injury_df = injury_df.copy()
        date_col = "date" if "date" in injury_df.columns else "event_date"
        if date_col not in injury_df.columns:
            return None
        injury_df["norm_date"] = pd.to_datetime(injury_df[date_col])
        lookback = cur_dt - timedelta(days=7)
        recent = injury_df[
            (injury_df["norm_date"] >= lookback) & (injury_df["norm_date"] <= cur_dt)
        ]

        if recent.empty:
            return None

        sev_col = "severity" if "severity" in recent.columns else ("reported_severity" if "reported_severity" in recent.columns else None)
        if sev_col:
            major = recent[
                recent[sev_col].astype(str).str.lower().isin(
                    ["major", "high", "severe"]
                )
            ]
            if not major.empty:
                row = major.iloc[-1]
                body = row.get("body_location", row.get("body_part", "unspecified area"))
                return (
                    f"Major injury reported on {row['norm_date'].strftime('%Y-%m-%d')}: "
                    f"{body} ({row[sev_col]})."
                )

        return None

    # ------------------------------------------------------------------ #
    def _check_recent_illness(
        self, illness_df: pd.DataFrame, cur_dt: pd.Timestamp
    ) -> str | None:
        """Return a description if there is a recent illness report."""
        if illness_df is None or illness_df.empty:
            return None

        illness_df = illness_df.copy()
        date_col = "date" if "date" in illness_df.columns else ("event_date" if "event_date" in illness_df.columns else None)
        if date_col is None:
            return None
        illness_df["norm_date"] = pd.to_datetime(illness_df[date_col])
        lookback = cur_dt - timedelta(days=7)
        recent = illness_df[
            (illness_df["norm_date"] >= lookback) & (illness_df["norm_date"] <= cur_dt)
        ]

        if recent.empty:
            return None

        if "severity" in recent.columns:
            major = recent[
                recent["severity"].astype(str).str.lower().isin(
                    ["major", "high", "severe"]
                )
            ]
            if not major.empty:
                row = major.iloc[-1]
                illness_type = row.get("type", row.get("symptoms", "unspecified"))
                return (
                    f"Illness reported on {row['norm_date'].strftime('%Y-%m-%d')}: "
                    f"{illness_type} ({row['severity']})."
                )

        return None

    # ------------------------------------------------------------------ #
    def _check_workload_trend(
        self, training_df: pd.DataFrame, cur_dt: pd.Timestamp
    ) -> bool:
        """Return True if short-term workload is trending upward."""
        if training_df is None or training_df.empty:
            return False

        workload_col = None
        for col in [self.WORKLOAD_COL, "daily_load", "srpe"]:
            if col in training_df.columns:
                workload_col = col
                break
        if workload_col is None:
            return False

        df = training_df.copy()
        date_col = "session_date" if "session_date" in df.columns else ("date" if "date" in df.columns else None)
        if date_col is None:
            return False

        df["_date"] = pd.to_datetime(df[date_col])
        df = df.sort_values("_date")

        window_start = cur_dt - timedelta(days=self.WORKLOAD_TREND_WINDOW)
        recent = df[
            (df["_date"] >= window_start) & (df["_date"] <= cur_dt)
        ]

        if len(recent) < 3:
            return False

        loads = recent[workload_col].dropna().values
        if len(loads) < 3:
            return False

        # Simple linear trend: positive slope indicates rising workload
        x = np.arange(len(loads), dtype=float)
        slope, _ = np.polyfit(x, loads, 1)
        return bool(slope > 0)

    # ------------------------------------------------------------------ #
    # Priority-ordered rule application
    # ------------------------------------------------------------------ #
    def _apply_rules(
        self,
        player_id: str,
        current_date: str,
        observed_factors: list[ObservedFactor],
        baseline_period: str,
        recent_injury: str | None,
        recent_illness: str | None,
        workload_rising: bool,
        data_adequacy: DataAdequacy,
    ) -> Recommendation:
        """Apply rules in strict priority order and build the Recommendation."""

        rationale: list[str] = []
        escalation_flags: list[str] = []
        what_cannot_infer: list[str] = [
            "Psychological readiness and motivation",
            "Contextual factors (e.g. upcoming competition importance)",
            "Exact clinical diagnosis or prognosis",
            "Nutritional intake and hydration status",
        ]

        # Classify factor deviations
        significantly_worse: list[ObservedFactor] = []
        moderately_worse: list[ObservedFactor] = []
        improving: list[ObservedFactor] = []

        for f in observed_factors:
            if f.deviation is None:
                continue
            abs_z = abs(f.deviation)
            is_adverse = (
                (f.direction == "higher_is_better" and f.deviation < 0)
                or (f.direction == "higher_is_worse" and f.deviation > 0)
            )
            if is_adverse and abs_z >= self.DEVIATION_THRESHOLD_SIGNIFICANT:
                significantly_worse.append(f)
            elif is_adverse and abs_z >= self.DEVIATION_THRESHOLD_MODERATE:
                moderately_worse.append(f)
            elif not is_adverse and abs_z >= self.DEVIATION_THRESHOLD_MODERATE:
                improving.append(f)

        # --- Rule 2: Recent major injury or illness → HUMAN_REVIEW ------
        if recent_injury is not None:
            rationale.append(f"Recent injury detected: {recent_injury}")
            escalation_flags.append(f"Injury within last 7 days: {recent_injury}")
            rationale.append(
                "Recommendation: refer to sports clinician for clearance "
                "before resuming normal training."
            )
            return Recommendation(
                player_id=player_id,
                date=current_date,
                status=RecommendationStatus.HUMAN_REVIEW,
                observed_factors=observed_factors,
                baseline_comparison_period=baseline_period,
                recommendation_text=(
                    "A recent major injury has been recorded. "
                    "Please consult with the sports clinician or "
                    "medical team before making training decisions. "
                    "Reassess in 24-48 hours."
                ),
                rationale=rationale,
                what_system_cannot_infer=what_cannot_infer,
                suggested_review_window="24-48 hours",
                data_adequacy=data_adequacy,
                escalation_flags=escalation_flags,
            )

        if recent_illness is not None:
            rationale.append(f"Recent illness detected: {recent_illness}")
            escalation_flags.append(f"Illness within last 7 days: {recent_illness}")
            rationale.append(
                "Recommendation: refer to medical staff for clearance."
            )
            return Recommendation(
                player_id=player_id,
                date=current_date,
                status=RecommendationStatus.HUMAN_REVIEW,
                observed_factors=observed_factors,
                baseline_comparison_period=baseline_period,
                recommendation_text=(
                    "A recent illness has been recorded. "
                    "Please consult with the medical team before "
                    "making training decisions. Reassess in 24-48 hours."
                ),
                rationale=rationale,
                what_system_cannot_infer=what_cannot_infer,
                suggested_review_window="24-48 hours",
                data_adequacy=data_adequacy,
                escalation_flags=escalation_flags,
            )

        # --- Rule 3: Multiple significant deviations → RECOVERY_FOCUSED -
        if len(significantly_worse) >= 2:
            names = [f.name.replace("_", " ").title() for f in significantly_worse]
            rationale.append(
                f"Multiple wellness metrics significantly worse than baseline: "
                f"{', '.join(names)}."
            )
            rationale.append(
                "Pattern suggests the player may benefit from a "
                "recovery-focused session rather than high-intensity work."
            )
            return Recommendation(
                player_id=player_id,
                date=current_date,
                status=RecommendationStatus.RECOVERY_FOCUSED,
                observed_factors=observed_factors,
                baseline_comparison_period=baseline_period,
                recommendation_text=(
                    f"Several wellness indicators ({', '.join(names)}) are "
                    f"significantly below the player's personal baseline. "
                    f"Consider a recovery-focused session (e.g. light "
                    f"mobility, active recovery) and reassess in 24-48 hours."
                ),
                rationale=rationale,
                what_system_cannot_infer=what_cannot_infer,
                suggested_review_window="24-48 hours",
                data_adequacy=data_adequacy,
                escalation_flags=escalation_flags,
            )

        # --- Rule 4: Rising workload + worsening wellness → HUMAN_REVIEW -
        any_worse = significantly_worse + moderately_worse
        if workload_rising and len(any_worse) >= 1:
            names = [f.name.replace("_", " ").title() for f in any_worse]
            rationale.append(
                "Training workload has been trending upward over the last "
                f"{self.WORKLOAD_TREND_WINDOW} days."
            )
            rationale.append(
                f"Concurrently, wellness metric(s) are declining: "
                f"{', '.join(names)}."
            )
            rationale.append(
                "This workload-wellness mismatch warrants coaching review."
            )
            escalation_flags.append("Workload/wellness mismatch")
            return Recommendation(
                player_id=player_id,
                date=current_date,
                status=RecommendationStatus.HUMAN_REVIEW,
                observed_factors=observed_factors,
                baseline_comparison_period=baseline_period,
                recommendation_text=(
                    "Rising training workload combined with declining "
                    f"wellness ({', '.join(names)}) detected. "
                    "Recommend coaching staff review the current "
                    "training plan. Reassess in 24-48 hours."
                ),
                rationale=rationale,
                what_system_cannot_infer=what_cannot_infer,
                suggested_review_window="24-48 hours",
                data_adequacy=data_adequacy,
                escalation_flags=escalation_flags,
            )

        # --- Rule 5: Single moderate deviation → MONITOR with note --------
        if len(moderately_worse) >= 1 or len(significantly_worse) == 1:
            flagged = significantly_worse + moderately_worse
            names = [f.name.replace("_", " ").title() for f in flagged]
            rationale.append(
                f"Minor deviation detected in: {', '.join(names)}. "
                "Currently within monitoring range."
            )
            return Recommendation(
                player_id=player_id,
                date=current_date,
                status=RecommendationStatus.MONITOR,
                observed_factors=observed_factors,
                baseline_comparison_period=baseline_period,
                recommendation_text=(
                    f"Slight deviation noted in {', '.join(names)}. "
                    "No immediate action required — continue current plan "
                    "and monitor. Reassess in 24-48 hours."
                ),
                rationale=rationale,
                what_system_cannot_infer=what_cannot_infer,
                suggested_review_window="24-48 hours",
                data_adequacy=data_adequacy,
                escalation_flags=escalation_flags,
            )

        # --- Rule 6: Stable / improving → MONITOR (no notable deviation) --
        if improving:
            names = [f.name.replace("_", " ").title() for f in improving]
            rationale.append(
                f"Improving trend observed in: {', '.join(names)}."
            )
        rationale.append("No notable deviation from personal baseline detected.")

        return Recommendation(
            player_id=player_id,
            date=current_date,
            status=RecommendationStatus.MONITOR,
            observed_factors=observed_factors,
            baseline_comparison_period=baseline_period,
            recommendation_text=(
                "All wellness indicators are within the player's normal "
                "range. Continue with the current training plan."
            ),
            rationale=rationale,
            what_system_cannot_infer=what_cannot_infer,
            suggested_review_window="Next scheduled check-in",
            data_adequacy=data_adequacy,
            escalation_flags=escalation_flags,
        )

    # ------------------------------------------------------------------ #
    # Insufficient-data shortcut
    # ------------------------------------------------------------------ #
    def _insufficient_data_recommendation(
        self, player_id: str, current_date: str, detail: str
    ) -> Recommendation:
        """Return a recommendation when data is insufficient."""
        return Recommendation(
            player_id=player_id,
            date=current_date,
            status=RecommendationStatus.INSUFFICIENT_DATA,
            observed_factors=[],
            baseline_comparison_period="N/A",
            recommendation_text=(
                "There is not enough data to generate a reliable "
                "recommendation. Please ensure wellness data is "
                "logged consistently."
            ),
            rationale=[detail],
            what_system_cannot_infer=[
                "All inferences — insufficient data to assess any factor."
            ],
            suggested_review_window="Once sufficient data is available",
            data_adequacy=DataAdequacy.INSUFFICIENT,
            escalation_flags=[],
        )
