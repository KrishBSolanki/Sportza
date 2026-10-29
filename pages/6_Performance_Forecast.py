"""
SPORTZA — Performance & Readiness Forecasting
Next-day readiness forecasting evaluated with chronological holdouts and naïve baseline benchmarking.
"""
import numpy as np
import pandas as pd
import streamlit as st

from src.config import Config
from src.features.temporal import build_athlete_date_features
from src.models.readiness import ReadinessForecaster
from src.visualization.charts import actual_vs_predicted, feature_importance_chart
from src.visualization.theme import (
    apply_streamlit_theme,
    render_data_banner,
    render_disclaimer,
    render_kpi_card,
)

st.set_page_config(page_title="Performance Forecast | SPORTZA", page_icon="🎯", layout="wide")
apply_streamlit_theme()

st.title("🎯 Performance & Readiness Forecasting")
st.markdown("Predicting next-day athlete readiness from prior 7-day wellness and workload trajectory.")

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

# Build features
with st.spinner("Extracting point-in-time temporal features..."):
    adf = build_athlete_date_features(wellness_df, sessions_df)

forecaster = ReadinessForecaster()
features, target = forecaster.prepare_features(adf)

if features.empty:
    st.warning("Insufficient sequential observations to generate lag features.")
    st.stop()

# Chronological split controls
all_dates = pd.to_datetime(features["date"]).sort_values()
min_d, max_d = all_dates.iloc[0], all_dates.iloc[-1]
default_split = all_dates.iloc[int(len(all_dates) * 0.75)].date()

c_s1, c_s2 = st.columns([1, 2])
with c_s1:
    split_date_selected = st.date_input(
        "Chronological Cutoff Date (Train / Test Split)",
        default_split,
        min_value=min_d.date(),
        max_value=max_d.date()
    )

with c_s2:
    st.caption(
        "⚠️ **Strict Temporal Split:** Training on observations strictly prior to cutoff; "
        "evaluating on future, unseen dates. Random cross-validation is strictly forbidden "
        "to prevent look-ahead leakage in time-series sports data."
    )

if st.button("Train & Evaluate Forecaster", type="primary"):
    with st.spinner("Training GradientBoostingRegressor model..."):
        try:
            metrics = forecaster.train(features, target, split_date=str(split_date_selected))
            
            # Metrics comparison cards
            t_m = metrics["test_metrics"]
            locf_m = metrics["baseline_locf"]
            roll_m = metrics["baseline_roll7"]
            
            k1, k2, k3, k4 = st.columns(4)
            with k1:
                st.markdown(render_kpi_card("Model MAE", f"{t_m['mae']:.2f}", f"RMSE: {t_m['rmse']:.2f}"), unsafe_allow_html=True)
            with k2:
                st.markdown(render_kpi_card("LOCF Naive MAE", f"{locf_m['mae']:.2f}", "Yesterday's value baseline"), unsafe_allow_html=True)
            with k3:
                st.markdown(render_kpi_card("7-Day Mean MAE", f"{roll_m['mae']:.2f}", "Weekly rolling baseline"), unsafe_allow_html=True)
            with k4:
                imp = metrics.get("test_metrics", {}).get("mae_improvement_pct", 0.0)
                st.markdown(render_kpi_card("Improvement vs Naive", f"{imp:+.1f}%", "Relative MAE reduction"), unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # Test predictions
            test_mask = features["date"] >= pd.Timestamp(split_date_selected)
            X_test = features.loc[test_mask, forecaster.feature_names].values
            y_test = target.loc[test_mask].values
            y_pred = forecaster.predict(features.loc[test_mask])

            # Charts
            col_p1, col_p2 = st.columns([1, 1])
            with col_p1:
                fig_res = actual_vs_predicted(y_test, y_pred, title="Actual vs Predicted Next-Day Readiness")
                st.plotly_chart(fig_res, use_container_width=True)

            with col_p2:
                top_feats = list(metrics["top_10_features"].keys())
                top_vals = np.array(list(metrics["top_10_features"].values()))
                fig_feat = feature_importance_chart(top_feats, top_vals, title="Top Predictive Features")
                st.plotly_chart(fig_feat, use_container_width=True)

        except Exception as e:
            st.error(f"Error during training: {e!s}")
else:
    st.info("Click **Train & Evaluate Forecaster** to run chronological model evaluation.")
