"""
SPORTZA — Injury & Health Events Research Interface
Exploratory body-location mapping, severity distribution, timeline, and gated research risk modeling.
"""
import pandas as pd
import streamlit as st

from src.config import Config
from src.models.injury_event import InjuryEventAnalyzer
from src.visualization.charts import injury_heatmap, injury_timeline
from src.visualization.theme import (
    apply_streamlit_theme,
    render_data_banner,
    render_disclaimer,
    render_kpi_card,
)

st.set_page_config(page_title="Injury Research | SPORTZA", page_icon="🩹", layout="wide")
apply_streamlit_theme()

st.title("🩹 Injury & Health Events (Research Interface)")
st.markdown("Exploratory epidemiological mapping of self-reported pain/injury notifications and conservative risk modeling.")

from app import load_data

data = load_data()
is_demo = data.get("_is_demo", True)
st.markdown(render_data_banner(is_demo, attribution=Config().DATASET_ATTRIBUTION), unsafe_allow_html=True)
st.markdown(render_disclaimer(), unsafe_allow_html=True)

injury_df = data.get("injury_events", pd.DataFrame())
wellness_df = data.get("wellness_daily", pd.DataFrame())

if injury_df.empty:
    st.info("No injury reports recorded in current dataset.")
    st.stop()

# Ensure standard columns
df_inj = injury_df.copy()
if "date" in df_inj.columns and "event_date" not in df_inj.columns:
    df_inj["event_date"] = df_inj["date"]
if "severity" in df_inj.columns and "reported_severity" not in df_inj.columns:
    df_inj["reported_severity"] = df_inj["severity"]

# Epidemiological KPIs
analyzer = InjuryEventAnalyzer()
desc = analyzer.build_descriptive_analysis(df_inj)

k1, k2, k3, k4 = st.columns(4)
with k1:
    st.markdown(render_kpi_card("Total Reports", str(desc["total_reports"]), "Self-reported pain events"), unsafe_allow_html=True)
with k2:
    top_loc = desc.get("top_location", "N/A")
    st.markdown(render_kpi_card("Most Reported Site", str(top_loc).replace("_", " ").title(), "Highest event count"), unsafe_allow_html=True)
with k3:
    major_cnt = desc["severity_counts"].get("major", 0)
    st.markdown(render_kpi_card("Major Severity", str(major_cnt), "Double-tap pain notification"), unsafe_allow_html=True)
with k4:
    minor_cnt = desc["severity_counts"].get("minor", 0)
    st.markdown(render_kpi_card("Minor Severity", str(minor_cnt), "Single-tap pain notification"), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Self-Report Disclaimer ───────────────────────────────────────────────
st.info(
    "📝 **Data Collection Context:** All injury records in SoccerMon were entered directly by athletes using "
    "the PmSys mobile body-silhouette interface (single tap = minor pain, double tap = major pain). "
    "These entries represent subjective pain symptoms and functional limitations, NOT formal medical diagnoses "
    "or clinical imaging results.",
    icon="ℹ️"
)

# ── Visualizations ───────────────────────────────────────────────────────
col_v1, col_v2 = st.columns([1, 1])
with col_v1:
    fig_heat = injury_heatmap(df_inj, title="Injury Count by Body Location & Severity")
    st.plotly_chart(fig_heat, use_container_width=True)

with col_v2:
    fig_time = injury_timeline(df_inj, title="Injury Report Timeline Across Squad")
    st.plotly_chart(fig_time, use_container_width=True)

st.divider()

# ── Gated Research Risk Model ─────────────────────────────────────────────
st.subheader("🤖 Research Risk Model Evaluation")
st.caption("Strictly gated by pre-flight sample size, positive event prevalence, and chronological holdouts.")

sufficiency = analyzer.check_data_sufficiency(df_inj)
if sufficiency["sufficient"]:
    st.success(f"✅ Pre-flight check passed: {sufficiency['reason']}")
    st.markdown("""
    **Model Specification:**
    - Target: Self-reported injury notification within the upcoming 7-day window.
    - Algorithm: Group-stratified Cross-Validated Logistic Regression (class-weighted).
    - Features: Lagged workload (ATL, CTL, ACWR) and baseline-subtracted wellness scores.
    """)
    if st.button("Run Research Risk Model Validation"):
        with st.spinner("Training cross-validated model across athlete groups..."):
            from src.features.temporal import build_athlete_date_features
            adf = build_athlete_date_features(wellness_df, data.get("training_sessions", pd.DataFrame()), df_inj)
            
            # Construct 7-day future target
            features_list = ["readiness", "fatigue", "soreness", "stress", "atl", "ctl_28", "acwr"]
            avail_f = [c for c in features_list if c in adf.columns]
            
            adf["target_inj_7d"] = adf.groupby("player_id")["reported_injury_today"].transform(
                lambda s: s.rolling(7, min_periods=1).max().shift(-7)
            ).fillna(0).astype(int)
            
            clean_df = adf[avail_f + ["target_inj_7d", "player_id"]].dropna()
            metrics = analyzer.train_risk_model(
                features=clean_df[avail_f],
                target=clean_df["target_inj_7d"],
                player_groups=clean_df["player_id"],
            )
            if metrics:
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Event Prevalence", f"{metrics['prevalence']*100:.1f}%")
                m2.metric("ROC-AUC", f"{metrics['roc_auc']:.3f}")
                m3.metric("Precision", f"{metrics['precision']:.3f}")
                m4.metric("Recall", f"{metrics['recall']:.3f}")
                st.caption(f"**Disclaimer:** {metrics['disclaimer']}")
            else:
                st.warning("Insufficient positive event rows after alignment to fit risk model.")
else:
    st.warning(f"⚠️ {sufficiency['reason']}")
    st.markdown("""
    > **Academic Note:** Sports science literature repeatedly cautions against training complex machine learning 
    > models on sparse sports injury datasets. High class imbalance (rare events) combined with repeated daily 
    > records from the same players frequently leads to spurious correlations and illusory test accuracy. 
    > SPORTZA safely falls back to descriptive epidemiological mapping when sample size criteria are not met.
    """)
