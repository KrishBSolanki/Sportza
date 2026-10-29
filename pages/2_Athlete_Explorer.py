"""
SPORTZA — Athlete Explorer
Deep-dive longitudinal athlete profiling, individual wellness trends, and workload cadence.
"""
import pandas as pd
import streamlit as st

from src.config import Config
from src.features.wellness import get_wellness_summary
from src.visualization.charts import (
    load_trend_chart,
    wellness_timeseries,
)
from src.visualization.theme import (
    apply_streamlit_theme,
    render_data_banner,
    render_disclaimer,
    render_kpi_card,
)

st.set_page_config(page_title="Athlete Explorer | SPORTZA", page_icon="🏃", layout="wide")
apply_streamlit_theme()

st.title("🏃 Athlete Explorer")
st.markdown("Longitudinal athlete tracking, baseline deviations, and missingness monitoring.")

from app import load_data

data = load_data()
is_demo = data.get("_is_demo", True)
st.markdown(render_data_banner(is_demo, attribution=Config().DATASET_ATTRIBUTION), unsafe_allow_html=True)
st.markdown(render_disclaimer(), unsafe_allow_html=True)

wellness_df = data.get("wellness_daily", pd.DataFrame())
sessions_df = data.get("training_sessions", pd.DataFrame())
injury_df = data.get("injury_events", pd.DataFrame())

if wellness_df.empty:
    st.warning("No wellness data available.")
    st.stop()

# Athlete selection
athletes = sorted(wellness_df["player_id"].unique())
col_s1, col_s2 = st.columns([1, 2])
with col_s1:
    selected_player = st.selectbox("Select Anonymized Athlete ID", athletes)

p_well = wellness_df[wellness_df["player_id"] == selected_player].sort_values("date")
p_sess = sessions_df[sessions_df["player_id"] == selected_player].sort_values("session_date") if not sessions_df.empty else pd.DataFrame()
p_inj = injury_df[injury_df["player_id"] == selected_player] if not injury_df.empty else pd.DataFrame()

# Athlete summary KPIs
summary = get_wellness_summary(wellness_df, selected_player)
m_stats = summary["metrics"]

with col_s2:
    st.markdown(f"""
    <div style="background: #1E1E2E; border: 1px solid #2D2D3F; border-radius: 8px; padding: 0.8rem 1.2rem; margin-top: 0.8rem;">
        <span style="color: #00D4AA; font-weight: bold; font-size: 1.1rem;">Profile: {selected_player}</span> | 
        <span style="color: #E0E0E0;">Total Reports: {summary['total_reports']}</span> | 
        <span style="color: #9E9E9E;">Observation Window: {summary['date_range'][0]} to {summary['date_range'][1]}</span>
    </div>
    """, unsafe_allow_html=True)

k1, k2, k3, k4 = st.columns(4)
with k1:
    r_val = m_stats.get("readiness", {}).get("mean", "N/A")
    st.markdown(render_kpi_card("Readiness Mean", f"{r_val}/10" if r_val != "N/A" else "N/A", "Scale 1-10"), unsafe_allow_html=True)
with k2:
    f_val = m_stats.get("fatigue", {}).get("mean", "N/A")
    st.markdown(render_kpi_card("Fatigue Mean", f"{f_val}/5" if f_val != "N/A" else "N/A", "Scale 1-5 (Higher = More fatigue)"), unsafe_allow_html=True)
with k3:
    s_val = m_stats.get("sleep_duration_hours", {}).get("mean", "N/A")
    st.markdown(render_kpi_card("Sleep Duration", f"{s_val} hrs" if s_val != "N/A" else "N/A", "Reported daily average"), unsafe_allow_html=True)
with k4:
    inj_cnt = len(p_inj)
    st.markdown(render_kpi_card("Injuries Logged", str(inj_cnt), "Self-reported pain/injury"), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Why This Matters Explanation ─────────────────────────────────────────
st.info(
    "💡 **Why This Matters:** High intra-individual variability in readiness or sleep quality often precedes "
    "elevated fatigue and tissue soreness. SPORTZA contrasts each observation against the athlete's personal "
    "rolling baseline rather than population universal cutoffs, respecting individual physiological norms.",
    icon="ℹ️"
)

# ── Wellness Time Series ─────────────────────────────────────────────────
st.subheader("📈 Longitudinal Wellness Trajectory")
metrics_to_plot = ["readiness", "fatigue", "sleep_duration_hours", "sleep_quality", "soreness", "stress"]
fig_wellness = wellness_timeseries(p_well, selected_player, metrics=metrics_to_plot, title=f"Wellness History for {selected_player}")
st.plotly_chart(fig_wellness, use_container_width=True)

# ── Workload Trajectory ──────────────────────────────────────────────────
st.subheader("🏋️ Workload History (sRPE)")
if not p_sess.empty:
    fig_load = load_trend_chart(p_sess, player_id=selected_player, title=f"Training Load Trend for {selected_player}")
    st.plotly_chart(fig_load, use_container_width=True)
else:
    st.info("No training session reports available for this athlete.")
