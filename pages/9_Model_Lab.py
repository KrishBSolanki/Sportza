"""
SPORTZA — Model Lab & Evaluation Suite
Interactive machine learning workbench with strict validation protocols, model cards, and artifacts.
"""
import numpy as np
import pandas as pd
import streamlit as st

from src.config import Config
from src.features.temporal import build_athlete_date_features
from src.models.evaluation import generate_model_card
from src.models.injury_event import InjuryEventAnalyzer
from src.models.performance import GamePerformanceForecaster
from src.models.readiness import ReadinessForecaster
from src.visualization.charts import actual_vs_predicted, feature_importance_chart
from src.visualization.theme import (
    apply_streamlit_theme,
    render_data_banner,
    render_disclaimer,
    render_kpi_card,
)

st.set_page_config(page_title="Model Lab | SPORTZA", page_icon="🤖", layout="wide")
apply_streamlit_theme()

st.title("🤖 Model Lab & Research Validation")
st.markdown("Benchmarking candidate machine learning models against naïve baselines on chronological holdouts.")

from app import load_data

data = load_data()
is_demo = data.get("_is_demo", True)
st.markdown(render_data_banner(is_demo, attribution=Config().DATASET_ATTRIBUTION), unsafe_allow_html=True)
st.markdown(render_disclaimer(), unsafe_allow_html=True)

wellness_df = data.get("wellness_daily", pd.DataFrame())
sessions_df = data.get("training_sessions", pd.DataFrame())
injury_df = data.get("injury_events", pd.DataFrame())
game_df = data.get("game_performance", pd.DataFrame())

# Task selector
task = st.selectbox(
    "Select Predictive Task",
    [
        "Task 1: Next-Day Readiness Regression (Prior 7-Day Window)",
        "Task 2: Match Performance Rating Forecast (Game Reports)",
        "Task 3: Injury/Pain Report Classification (7-Day Horizon)",
    ]
)

if "Task 1" in task:
    st.subheader("📈 Task 1: Next-Day Readiness Forecaster")
    st.markdown("""
    - **Target:** Next-day athlete self-reported readiness (1-10).
    - **Input Horizon:** Strict 7-day preceding rolling window (wellness + workload + lag features).
    - **Baselines:** 1) Last Observation Carried Forward (yesterday's readiness); 2) 7-day rolling mean.
    - **Model:** Gradient Boosting Regressor (200 estimators, max depth 4).
    """)

    adf = build_athlete_date_features(wellness_df, sessions_df)
    forecaster = ReadinessForecaster()
    features, target = forecaster.prepare_features(adf)

    all_dates = pd.to_datetime(features["date"]).sort_values()
    split_default = all_dates.iloc[int(len(all_dates) * 0.75)].date()
    split_date = st.date_input("Chronological Split Date", split_default)

    if st.button("Train Model & Benchmark vs Baseline", type="primary"):
        with st.spinner("Training readiness forecaster on pre-split records..."):
            metrics = forecaster.train(features, target, split_date=str(split_date))
            
            t_m = metrics["test_metrics"]
            locf_m = metrics["baseline_locf"]
            roll_m = metrics["baseline_roll7"]
            
            k1, k2, k3, k4 = st.columns(4)
            with k1:
                st.markdown(render_kpi_card("Gradient Boost MAE", f"{t_m['mae']:.2f}", f"RMSE: {t_m['rmse']:.2f}"), unsafe_allow_html=True)
            with k2:
                st.markdown(render_kpi_card("LOCF Naive MAE", f"{locf_m['mae']:.2f}", "Yesterday's value"), unsafe_allow_html=True)
            with k3:
                st.markdown(render_kpi_card("7-Day Mean MAE", f"{roll_m['mae']:.2f}", "Weekly mean baseline"), unsafe_allow_html=True)
            with k4:
                imp = t_m.get("mae_improvement_pct", 0.0)
                st.markdown(render_kpi_card("MAE Delta vs Naive", f"{imp:+.1f}%", "Improvement"), unsafe_allow_html=True)

            test_mask = features["date"] >= pd.Timestamp(split_date)
            y_test = target.loc[test_mask].values
            y_pred = forecaster.predict(features.loc[test_mask])

            c1, c2 = st.columns(2)
            with c1:
                st.plotly_chart(actual_vs_predicted(y_test, y_pred, title="Actual vs Predicted Readiness"), use_container_width=True)
            with c2:
                top_feats = list(metrics["top_10_features"].keys())
                top_vals = np.array(list(metrics["top_10_features"].values()))
                st.plotly_chart(feature_importance_chart(top_feats, top_vals, title="Top Predictive Features"), use_container_width=True)

            # Model Card
            st.divider()
            st.subheader("📄 Model Card (Generated)")
            card_md = generate_model_card(
                model_name="GradientBoostingReadinessForecaster_v1",
                task_description="Predict next-day readiness from 7-day preceding athlete wellness and workload",
                metrics_summary={"Model MAE": t_m["mae"], "LOCF MAE": locf_m["mae"], "Rolling 7d MAE": roll_m["mae"]},
                limitations_notes="Model is trained on self-reported readiness scale 1-10; subjective bias and missing report days affect accuracy.",
                target_definition="Readiness score on date t+1",
            )
            st.markdown(card_md)

elif "Task 2" in task:
    st.subheader("🎯 Task 2: Game Performance Rating Forecaster")
    st.markdown("""
    - **Target:** Post-match subjective performance score (Team, Offensive, Defensive ratings 1-10).
    - **Evaluation:** Gated by minimum report count (SoccerMon contains 248 game performance reports).
    """)
    perf_forecaster = GamePerformanceForecaster()
    adf = build_athlete_date_features(wellness_df, sessions_df)
    
    target_perf = st.selectbox("Select Target Rating", ["team_performance", "offensive_performance", "defensive_performance"])
    X_p, y_p = perf_forecaster.prepare_match_features(game_df, adf, target_col=target_perf)
    
    if len(X_p) < perf_forecaster.MIN_SAMPLES:
        st.warning(f"⚠️ Insufficient aligned match reports ({len(X_p)} available; minimum required is {perf_forecaster.MIN_SAMPLES}).")
    else:
        st.success(f"Aligned {len(X_p)} match performance observations with pre-match athlete status.")
        if st.button("Evaluate Match Rating Forecaster"):
            res = perf_forecaster.train_chronological(X_p, y_p)
            if res.get("trained"):
                k1, k2, k3 = st.columns(3)
                k1.metric("Model MAE", f"{res['model_mae']:.2f}")
                k2.metric("Historical Mean Baseline MAE", f"{res['baseline_mean_mae']:.2f}")
                k3.metric("MAE Improvement", f"{res['mae_improvement']:+.2f}")
                st.dataframe(pd.DataFrame(list(res["feature_importance"].items()), columns=["Feature", "Importance"]), use_container_width=True)

elif "Task 3" in task:
    st.subheader("🩹 Task 3: Injury/Pain Report Risk Model")
    inj_analyzer = InjuryEventAnalyzer()
    check = inj_analyzer.check_data_sufficiency(injury_df)
    
    if not check["sufficient"]:
        st.warning(f"⚠️ **Pre-flight Gate Blocked:** {check['reason']}")
        st.info("No validated clinical model can be trained responsibly under extreme class scarcity. Descriptive analysis remains active in the Injury Research tab.")
    else:
        st.success(f"✅ Pre-flight gate passed: {check['total_events']} events across {check['unique_players']} players.")
        st.markdown("Cross-validated logistic regression model with balanced class weighting available.")
