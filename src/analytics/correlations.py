"""
SPORTZA Correlation & Collinearity Analysis Module

Implements Pearson and Spearman correlation matrices, pairwise sample size tracking,
and collinearity diagnostic helpers.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def compute_correlation_matrix(
    df: pd.DataFrame,
    method: str = "pearson",
    min_periods: int = 10,
) -> pd.DataFrame:
    """Compute pairwise correlation matrix for numeric columns."""
    num_df = df.select_dtypes(include=[np.number])
    if num_df.empty:
        return pd.DataFrame()
    return num_df.corr(method=method, min_periods=min_periods).round(3)


def compute_pairwise_sample_sizes(df: pd.DataFrame) -> pd.DataFrame:
    """Compute pairwise count of complete observations (non-null in both columns)."""
    num_df = df.select_dtypes(include=[np.number])
    if num_df.empty:
        return pd.DataFrame()
    valid = num_df.notna().astype(int)
    return valid.T.dot(valid)


def flag_high_collinearity(
    corr_matrix: pd.DataFrame,
    threshold: float = 0.85,
) -> list[tuple[str, str, float]]:
    """Identify pairs of features with absolute correlation >= threshold."""
    if corr_matrix.empty:
        return []
    
    flagged = []
    cols = corr_matrix.columns
    for i in range(len(cols)):
        for j in range(i + 1, len(cols)):
            val = corr_matrix.iloc[i, j]
            if pd.notna(val) and abs(val) >= threshold:
                flagged.append((cols[i], cols[j], round(float(val), 3)))
    return flagged
