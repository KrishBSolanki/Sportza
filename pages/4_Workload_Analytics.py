"""
SPORTZA — Workload & Training Analytics
Comprehensive load quantification: sRPE, ATL (7d), CTL (28d), ACWR, Monotony, and Strain.
"""
import pandas as pd
import plotly.express as px
import streamlit as st

from src.config import Config
from src.visualization.charts import load_trend_chart, team_comparison_boxplot
from src.visualization.theme import (
    COLORS,
    apply_streamlit_theme,
    get_plotly_layout,
    render_data_banner,
    render_disclaimer,
    render_kpi_card,
)

st.set_page_config(page_title="Workload Analytics | SPORTZA", page_icon="📈", layout="wide")
apply_streamlit_theme()

st.title("📈 Workload & Training Analytics")
st.markdown("Quantifying internal training load (sRPE), chronic fitness-fatigue dynamics, and session distribution.")

from app import load_data

data = load_data()
is_demo = data.get("_is_demo", True)
st.markdown(render_data_banner(is_demo, attribution=Config().DATASET_ATTRIBUTION), unsafe_allow_html=True)
st.markdown(render_disclaimer(), unsafe_allow_html=True)

sessions_df = data.get("training_sessions", pd.DataFrame())

if sessions_df.empty:
    st.warning("No training session data available.")
    st.stop()

# Filters
athletes = ["All Athletes"] + sorted(sessions_df["player_id"].unique().tolist())
c1, c2 = st.columns([1, 1])
with c1:
    selected_player = st.selectbox("Select Athlete Focus", athletes)

sub_df = sessions_df if selected_player == "All Athletes" else sessions_df[sessions_df["player_id"] == selected_player]

# Top Workload KPIs
total_sessions = len(sub_df)
mean_dur = sub_df["duration_minutes"].mean() if "duration_minutes" in sub_df.columns else 0
mean_rpe = sub_df["rpe"].mean() if "rpe" in sub_df.columns else 0
mean_srpe = sub_df["srpe"].mean() if "srpe" in sub_df.columns else 0

k1, k2, k3, k4 = st.columns(4)
with k1:
    st.markdown(render_kpi_card("Total Sessions", f"{total_sessions:,}", "In dataset"), unsafe_allow_html=True)
with k2:
    st.markdown(render_kpi_card("Mean Duration", f"{mean_dur:.0f} mins", "Per session"), unsafe_allow_html=True)
with k3:
    st.markdown(render_kpi_card("Mean RPE", f"{mean_rpe:.1f}/10", "Perceived exertion"), unsafe_allow_html=True)
with k4:
    st.markdown(render_kpi_card("Mean sRPE", f"{mean_srpe:.0f} AU", "RPE × Duration [AU]"), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Scientific Methodological Caveat ──────────────────────────────────────
st.warning(
    "⚠️ **Methodological Context:** The Acute:Chronic Workload Ratio (ACWR) and session monotony/strain are descriptive "
    "workload management indicators, NOT deterministic injury predictors. High training load alone does not cause injury; "
    "it must be interpreted alongside wellness context, fixture congested periods, and individual recovery capacity.",
    icon="🔬"
)

# ── Workload Trajectory ──────────────────────────────────────────────────
st.subheader("📊 Load Trajectory (Daily sRPE, 7-Day Sum, 28-Day Baseline)")
pid_arg = None if selected_player == "All Athletes" else selected_player
fig_trend = load_trend_chart(sub_df, player_id=pid_arg, title=f"Training Load Dynamics ({selected_player})")
st.plotly_chart(fig_trend, use_container_width=True)

# ── Session Type Breakdown & Comparisons ──────────────────────────────────
col_b1, col_b2 = st.columns(2)

with col_b1:
    st.subheader("⚽ Load by Session Type")
    if "session_type" in sub_df.columns:
        type_agg = sub_df.groupby("session_type")["srpe"].agg(["count", "mean", "sum"]).reset_index()
        fig_pie = px.pie(
            type_agg, values="sum", names="session_type",
            color_discrete_sequence=[COLORS["primary"], COLORS["secondary"], COLORS["warning"]],
            title="Cumulative Workload by Session Type",
        )
        fig_pie.update_layout(**get_plotly_layout())
        st.plotly_chart(fig_pie, use_container_width=True)

with col_b2:
    st.subheader("👥 Annual Sessions per Player")
    fig_box = team_comparison_boxplot(sessions_df, title="Sessions per Player by Team/Year")
    st.plotly_chart(fig_box, use_container_width=True)
