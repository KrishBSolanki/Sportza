"""Personal baseline computation for player wellness and performance metrics.

Computes rolling statistics for each player so that current observations
can be compared against their own historical norms rather than population
averages.
"""

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass
class BaselineResult:
    """Result of a baseline computation for a single metric."""

    mean: float | None
    std: float | None
    n_observations: int
    is_sufficient: bool
    window_start: str | None
    window_end: str | None


class PersonalBaseline:
    """Computes rolling personal-baseline statistics for a player.

    The baseline represents a player's *normal* range for each metric
    over a configurable look-back window.  All comparisons are expressed
    as z-scores (standard deviations from the player's own mean).
    """

    DEFAULT_WINDOW: int = 28  # days
    DEFAULT_MIN_OBS: int = 7  # minimum non-NaN observations

    # ------------------------------------------------------------------ #
    # Core computation
    # ------------------------------------------------------------------ #
    @staticmethod
    def compute(
        series: pd.Series,
        window: int = DEFAULT_WINDOW,
        min_obs: int = DEFAULT_MIN_OBS,
    ) -> BaselineResult:
        """Compute rolling baseline statistics for a metric series.

        Parameters
        ----------
        series : pd.Series
            Time-indexed series of metric values (may contain NaN).
        window : int
            Number of most-recent observations to include.
        min_obs : int
            Minimum non-NaN values required for a reliable baseline.

        Returns
        -------
        BaselineResult
            Contains mean, std, observation count, and sufficiency flag.
        """
        if series is None or series.empty:
            return BaselineResult(
                mean=None,
                std=None,
                n_observations=0,
                is_sufficient=False,
                window_start=None,
                window_end=None,
            )

        # Take the last `window` entries and drop NaN
        recent = series.tail(window).dropna()

        n_obs = len(recent)
        if n_obs == 0:
            return BaselineResult(
                mean=None,
                std=None,
                n_observations=0,
                is_sufficient=False,
                window_start=None,
                window_end=None,
            )

        is_sufficient = n_obs >= min_obs
        mean_val = float(np.nanmean(recent.values))

        # Handle constant series (std == 0) gracefully
        std_val = float(np.nanstd(recent.values, ddof=1)) if n_obs > 1 else 0.0
        if np.isnan(std_val):
            std_val = 0.0

        # Determine window boundaries
        window_start = str(recent.index.min()) if hasattr(recent.index, "min") else None
        window_end = str(recent.index.max()) if hasattr(recent.index, "max") else None

        return BaselineResult(
            mean=mean_val,
            std=std_val,
            n_observations=n_obs,
            is_sufficient=is_sufficient,
            window_start=window_start,
            window_end=window_end,
        )

    # ------------------------------------------------------------------ #
    # Z-score
    # ------------------------------------------------------------------ #
    @staticmethod
    def get_z_score(
        current_value: float | None,
        baseline_mean: float | None,
        baseline_std: float | None,
    ) -> float | None:
        """Compute how many SDs the current value is from the baseline mean.

        Parameters
        ----------
        current_value : float | None
            Today's observed value for the metric.
        baseline_mean : float | None
            Player's personal baseline mean.
        baseline_std : float | None
            Player's personal baseline standard deviation.

        Returns
        -------
        float | None
            Signed z-score, or ``None`` if inputs are missing or std is zero.
        """
        if current_value is None or baseline_mean is None or baseline_std is None:
            return None

        if np.isnan(current_value) or np.isnan(baseline_mean):
            return None

        # When std is 0 (constant series) we cannot compute a meaningful
        # z-score.  Return 0.0 if the value equals the mean, else None.
        if baseline_std == 0.0 or np.isnan(baseline_std):
            return 0.0 if current_value == baseline_mean else None

        return (current_value - baseline_mean) / baseline_std

    # ------------------------------------------------------------------ #
    # Convenience: compute baseline + z-score in one call
    # ------------------------------------------------------------------ #
    @classmethod
    def evaluate_metric(
        cls,
        series: pd.Series,
        current_value: float | None,
        window: int = DEFAULT_WINDOW,
        min_obs: int = DEFAULT_MIN_OBS,
    ) -> tuple[BaselineResult, float | None]:
        """Compute baseline and z-score for a metric in one step.

        Returns
        -------
        tuple[BaselineResult, float | None]
            The baseline result and the z-score (or ``None``).
        """
        baseline = cls.compute(series, window=window, min_obs=min_obs)
        z = cls.get_z_score(current_value, baseline.mean, baseline.std)
        return baseline, z
