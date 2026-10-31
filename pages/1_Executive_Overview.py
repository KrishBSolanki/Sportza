"""
SPORTZA — Executive Overview
High-level squad monitoring, attention triage, readiness distribution, and workload trends.
"""

import pandas as pd
import streamlit as st

from src.analytics.descriptive import compute_report_counts, compute_squad_summary
from src.config import Config
from src.decision_support.rules import DecisionEngine, RecommendationStatus
from src.visualization.charts import (
    load_trend_chart,
    squad_readiness_distribution,
)
from src.visualization.theme import (
    apply_streamlit_theme,
    render_data_banner,
    render_disclaimer,
    render_kpi_card,
)

# Page config
st.set_page_config(page_title="Executive Overview | SPORTZA", page_icon="📊", layout="wide")
apply_streamlit_theme()

st.title("📊 Executive Overview")
st.markdown("Squad-level readiness monitoring, workload trajectory, and attention flags.")

# Load data
from app import load_data

data = load_data()
is_demo = data.get("_is_demo", True)
st.markdown(render_data_banner(is_demo, attribution=Config().DATASET_ATTRIBUTION), unsafe_allow_html=True)
st.markdown(render_disclaimer(), unsafe_allow_html=True)

wellness_df = data.get("wellness_daily", pd.DataFrame())
sessions_df = data.get("training_sessions", pd.DataFrame())
injury_df = data.get("injury_events", pd.DataFrame())
illness_df = data.get("illness_events", pd.DataFrame())

if wellness_df.empty:
    st.warning("No wellness data available to display.")
    st.stop()

# Date filter
min_date = pd.to_datetime(wellness_df["date"]).min().date()
max_date = pd.to_datetime(wellness_df["date"]).max().date()

col_f1, col_f2 = st.columns([2, 1])
with col_f1:
    selected_range = st.date_input("Filter Date Range", (min_date, max_date), min_value=min_date, max_value=max_date)
with col_f2:
    teams = ["All Teams", "Team A", "Team B"]
    selected_team = st.selectbox("Select Team", teams)

# Filter data
if isinstance(selected_range, tuple) and len(selected_range) == 2:
    s_start, s_end = selected_range
    w_filtered = wellness_df[
        (pd.to_datetime(wellness_df["date"]).dt.date >= s_start) &
        (pd.to_datetime(wellness_df["date"]).dt.date <= s_end)
    ]
    s_filtered = sessions_df[
        (pd.to_datetime(sessions_df["session_date"]).dt.date >= s_start) &
        (pd.to_datetime(sessions_df["session_date"]).dt.date <= s_end)
    ] if not sessions_df.empty else pd.DataFrame()
    i_filtered = injury_df[
        (pd.to_datetime(injury_df["date" if "date" in injury_df.columns else "event_date"]).dt.date >= s_start) &
        (pd.to_datetime(injury_df["date" if "date" in injury_df.columns else "event_date"]).dt.date <= s_end)
    ] if not injury_df.empty else pd.DataFrame()
else:
    w_filtered, s_filtered, i_filtered = wellness_df, sessions_df, injury_df

if selected_team != "All Teams":
    team_prefix = "TeamA" if selected_team == "Team A" else "TeamB"
    w_filtered = w_filtered[w_filtered["player_id"].str.startswith(team_prefix)]
    if not s_filtered.empty:
        s_filtered = s_filtered[s_filtered["player_id"].str.startswith(team_prefix)]
    if not i_filtered.empty:
        i_filtered = i_filtered[i_filtered["player_id"].str.startswith(team_prefix)]

# ── Top KPIs ─────────────────────────────────────────────────────────────
counts = compute_report_counts(w_filtered, s_filtered, i_filtered)
summary = compute_squad_summary(w_filtered)
readiness_stats = summary.get("readiness", {})

k1, k2, k3, k4, k5 = st.columns(5)
with k1:
    st.markdown(render_kpi_card("Active Athletes", str(counts["unique_players"]), f"In {selected_team}"), unsafe_allow_html=True)
with k2:
    st.markdown(render_kpi_card("Wellness Reports", f"{counts['wellness_reports']:,}", f"{counts['start_date']} to {counts['end_date']}"), unsafe_allow_html=True)
with k3:
    st.markdown(render_kpi_card("Training Sessions", f"{counts['training_sessions']:,}", "Logged sessions in range"), unsafe_allow_html=True)
with k4:
    st.markdown(render_kpi_card("Reported Injuries", str(counts["injury_reports"]), "Self-reported pain/injury"), unsafe_allow_html=True)
with k5:
    mean_r = readiness_stats.get("mean", "N/A")
    st.markdown(render_kpi_card("Readiness Mean", f"{mean_r}/10" if mean_r != "N/A" else "N/A", f"Median: {readiness_stats.get('median', 'N/A')}"), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── What Needs Attention Today ───────────────────────────────────────────
st.subheader("⚠️ Attention Triage Panel")
st.caption("Automated rule-based detection of athletes exhibiting baseline deviations, recent injuries, or workload mismatches.")

latest_date = pd.to_datetime(w_filtered["date"]).max()
engine = DecisionEngine()
athletes = sorted(w_filtered["player_id"].unique())

attention_items = []
for pid in athletes:
    p_well = w_filtered[w_filtered["player_id"] == pid]
    p_sess = s_filtered[s_filtered["player_id"] == pid] if not s_filtered.empty else pd.DataFrame()
    p_inj = i_filtered[i_filtered["player_id"] == pid] if not i_filtered.empty else pd.DataFrame()
    p_ill = illness_df[illness_df["player_id"] == pid] if not illness_df.empty else pd.DataFrame()
    
    rec = engine.evaluate(
        player_id=pid,
        current_date=str(latest_date.date()),
        wellness_history=p_well,
        training_history=p_sess,
        injury_history=p_inj,
        illness_history=p_ill,
    )
    if rec.status in (RecommendationStatus.HUMAN_REVIEW, RecommendationStatus.RECOVERY_FOCUSED):
        attention_items.append(rec)

if attention_items:
    for item in attention_items[:6]:
        color = "#FF5252" if item.status == RecommendationStatus.HUMAN_REVIEW else "#FFB74D"
        with st.container():
            st.markdown(f"""
            <div style="background: #1E1E2E; border-left: 4px solid {color}; border-radius: 8px; padding: 1rem; margin-bottom: 0.75rem;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <strong style="font-size: 1.1rem; color: #E0E0E0;">Athlete {item.player_id}</strong>
                    <span style="background: rgba(255,255,255,0.1); color: {color}; padding: 0.2rem 0.6rem; border-radius: 12px; font-size: 0.8rem; font-weight: 600;">{item.status.value}</span>
                </div>
                <p style="color: #BDBDBD; margin: 0.5rem 0 0.2rem 0; font-size: 0.9rem;">{item.recommendation_text}</p>
                <small style="color: #9E9E9E;">Review window: <strong>{item.suggested_review_window}</strong></small>
            </div>
            """, unsafe_allow_html=True)
else:
    st.success("✅ No immediate high-priority flags detected on the latest observation date.")

st.divider()

# ── Visualizations ───────────────────────────────────────────────────────
col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    fig_readiness = squad_readiness_distribution(w_filtered, title="Squad Readiness Distribution")
    st.plotly_chart(fig_readiness)

with col_chart2:
    fig_trend = load_trend_chart(s_filtered, title=f"Squad Workload Trend ({selected_team})")
    st.plotly_chart(fig_trend)
