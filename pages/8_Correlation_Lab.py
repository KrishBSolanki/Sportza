"""
SPORTZA — Correlation Lab & Research Insights
Interactive Pearson & Spearman correlation heatmaps, sample size tracking, and collinearity detection.
"""
import pandas as pd
import streamlit as st

from src.analytics.correlations import (
    compute_correlation_matrix,
    compute_pairwise_sample_sizes,
    flag_high_collinearity,
)
from src.config import Config
from src.features.temporal import build_athlete_date_features
from src.visualization.charts import correlation_heatmap
from src.visualization.theme import (
    apply_streamlit_theme,
    render_data_banner,
    render_disclaimer,
)

st.set_page_config(page_title="Correlation Lab | SPORTZA", page_icon="🔬", layout="wide")
apply_streamlit_theme()

st.title("🔬 Correlation Lab & Research Insights")
st.markdown("Inter-metric associations across subjective wellness, internal workload, and recovery indicators.")

from app import load_data

data = load_data()
is_demo = data.get("_is_demo", True)
st.markdown(render_data_banner(is_demo, attribution=Config().DATASET_ATTRIBUTION), unsafe_allow_html=True)
st.markdown(render_disclaimer(), unsafe_allow_html=True)

wellness_df = data.get("wellness_daily", pd.DataFrame())
sessions_df = data.get("training_sessions", pd.DataFrame())

if wellness_df.empty:
    st.warning("No wellness data available.")
    st.stop()

# Controls
c1, c2, c3 = st.columns([1, 1, 1])
with c1:
    corr_method = st.radio("Correlation Method", ["pearson", "spearman"], horizontal=True)
with c2:
    dataset_scope = st.selectbox("Metrics Scope", ["Wellness Only", "Wellness & Workload Combined"])
with c3:
    collin_thresh = st.slider("Collinearity Flag Threshold (|r|)", 0.70, 0.95, 0.85, 0.05)

# Prepare DataFrame
if dataset_scope == "Wellness Only":
    target_cols = ["readiness", "fatigue", "mood", "sleep_duration_hours", "sleep_quality", "soreness", "stress"]
    analysis_df = wellness_df[[c for c in target_cols if c in wellness_df.columns]]
else:
    with st.spinner("Aligning temporal features..."):
        adf = build_athlete_date_features(wellness_df, sessions_df)
    target_cols = [
        "readiness", "fatigue", "mood", "sleep_duration_hours", "sleep_quality", "soreness", "stress",
        "daily_load", "weekly_load", "atl", "ctl_28", "acwr", "monotony", "strain"
    ]
    analysis_df = adf[[c for c in target_cols if c in adf.columns]]

# ── Correlation Heatmap ──────────────────────────────────────────────────
st.subheader(f"📊 {corr_method.title()} Correlation Heatmap")
fig_corr = correlation_heatmap(
    analysis_df,
    method=corr_method,
    title=f"Correlation Matrix ({dataset_scope}) — Computed from Live Data"
)
st.plotly_chart(fig_corr)

# ── Collinearity Diagnostic ──────────────────────────────────────────────
st.subheader("⚠️ Multicollinearity Diagnostics")
corr_mat = compute_correlation_matrix(analysis_df, method=corr_method)
flagged_pairs = flag_high_collinearity(corr_mat, threshold=collin_thresh)

if flagged_pairs:
    st.warning(f"Detected {len(flagged_pairs)} pairs with high linear collinearity (|r| ≥ {collin_thresh:.2f}):")
    f_df = pd.DataFrame(flagged_pairs, columns=["Feature A", "Feature B", "Correlation (r)"])
    st.dataframe(f_df, hide_index=True)
    st.caption("ℹ️ **Modeling Tip:** Highly collinear variables (e.g. daily load, weekly load, and strain) should not be entered into the same linear regression simultaneously without regularization.")
else:
    st.success(f"No feature pairs exceed the |r| ≥ {collin_thresh:.2f} collinearity threshold.")

# ── Pairwise Sample Sizes ────────────────────────────────────────────────
with st.expander("🔢 View Pairwise Sample Sizes (Complete Observations)"):
    n_mat = compute_pairwise_sample_sizes(analysis_df)
    st.dataframe(n_mat)
