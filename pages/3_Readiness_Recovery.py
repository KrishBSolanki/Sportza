"""
SPORTZA — Daily Readiness & Recovery Decision Support
Explainable, rules-based decision engine comparing athlete observations to personal baselines.
"""
import pandas as pd
import streamlit as st

from src.config import Config
from src.decision_support.explanation import (
    generate_decision_audit,
)
from src.decision_support.rules import (
    DecisionEngine,
    RecommendationStatus,
)
from src.visualization.theme import (
    apply_streamlit_theme,
    render_data_banner,
    render_disclaimer,
)

st.set_page_config(page_title="Readiness & Recovery | SPORTZA", page_icon="💚", layout="wide")
apply_streamlit_theme()

st.title("💚 Daily Readiness & Recovery Decision Support")
st.markdown("Auditable, evidence-based training and recovery guidance anchored to intra-individual baselines.")

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
    st.warning("No wellness data available.")
    st.stop()

# Controls
athletes = sorted(wellness_df["player_id"].unique())
c1, c2 = st.columns([1, 1])
with c1:
    selected_player = st.selectbox("Select Athlete", athletes)

p_well = wellness_df[wellness_df["player_id"] == selected_player].sort_values("date")
dates_available = pd.to_datetime(p_well["date"]).dt.date.unique()

with c2:
    selected_date = st.selectbox("Select Evaluation Date", sorted(dates_available, reverse=True))

p_sess = sessions_df[sessions_df["player_id"] == selected_player] if not sessions_df.empty else pd.DataFrame()
p_inj = injury_df[injury_df["player_id"] == selected_player] if not injury_df.empty else pd.DataFrame()
p_ill = illness_df[illness_df["player_id"] == selected_player] if not illness_df.empty else pd.DataFrame()

# Run Decision Engine
engine = DecisionEngine()
rec = engine.evaluate(
    player_id=selected_player,
    current_date=str(selected_date),
    wellness_history=p_well,
    training_history=p_sess,
    injury_history=p_inj,
    illness_history=p_ill,
)

# Render Recommendation Card
status_colors = {
    RecommendationStatus.MONITOR: ("#69F0AE", "rgba(105, 240, 174, 0.1)"),
    RecommendationStatus.RECOVERY_FOCUSED: ("#FFB74D", "rgba(255, 183, 77, 0.1)"),
    RecommendationStatus.HUMAN_REVIEW: ("#FF5252", "rgba(255, 82, 82, 0.1)"),
    RecommendationStatus.INSUFFICIENT_DATA: ("#9E9E9E", "rgba(158, 158, 158, 0.1)"),
}
accent_color, bg_color = status_colors.get(rec.status, ("#9E9E9E", "rgba(158, 158, 158, 0.1)"))

st.markdown(f"""
<div style="background: {bg_color}; border: 2px solid {accent_color}; border-radius: 12px; padding: 1.5rem; margin: 1.5rem 0;">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.8rem;">
        <h3 style="color: {accent_color}; margin: 0;">Status: {rec.status.value}</h3>
        <span style="background: #1E1E2E; color: #E0E0E0; border: 1px solid #2D2D3F; padding: 0.3rem 0.8rem; border-radius: 15px; font-size: 0.85rem;">
            Data Adequacy: {rec.data_adequacy.value}
        </span>
    </div>
    <h4 style="color: #FFFFFF; font-weight: 500; margin: 0.5rem 0 1rem 0;">
        {rec.recommendation_text}
    </h4>
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-top: 1rem; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 0.8rem;">
        <div>
            <strong style="color: #9E9E9E; font-size: 0.85rem;">RECOMMENDED REVIEW WINDOW:</strong>
            <p style="color: #E0E0E0; margin: 0.2rem 0; font-size: 1.1rem; font-weight: bold;">{rec.suggested_review_window}</p>
        </div>
        <div>
            <strong style="color: #9E9E9E; font-size: 0.85rem;">BASELINE COMPARISON PERIOD:</strong>
            <p style="color: #E0E0E0; margin: 0.2rem 0; font-size: 0.95rem;">{rec.baseline_comparison_period}</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Escalation Flags if any
if rec.escalation_flags:
    for flag in rec.escalation_flags:
        st.error(f"🚨 **Escalation Flag:** {flag}")

# Rationale & Observed Factors
col_rat, col_fact = st.columns([1, 1])

with col_rat:
    st.subheader("📋 Decision Rationale")
    for r in rec.rationale:
        st.markdown(f"- {r}")

    st.subheader("🚫 What The System Cannot Infer")
    for w in rec.what_system_cannot_infer:
        st.markdown(f"- <small style='color: #9E9E9E;'>{w}</small>", unsafe_allow_html=True)

with col_fact:
    st.subheader("🔍 Observed Metrics vs Personal Baseline")
    factors_data = []
    for f in rec.observed_factors:
        factors_data.append({
            "Metric": f.name.replace("_", " ").title(),
            "Observed": f"{f.current_value:.1f}" if f.current_value is not None else "Missing",
            "Personal Base": f"{f.baseline_value:.1f}" if f.baseline_value is not None else "N/A",
            "Deviation (z)": f"{f.deviation:+.2f}" if f.deviation is not None else "N/A",
            "Interpretation": f.interpretation,
        })
    st.dataframe(pd.DataFrame(factors_data), use_container_width=True, hide_index=True)

# Decision Audit Trace
with st.expander("🔎 View Full Decision Audit Record (JSON)"):
    audit_record = generate_decision_audit(rec)
    st.json(audit_record)
