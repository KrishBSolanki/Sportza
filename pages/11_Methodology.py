"""
SPORTZA — Methodology, Limitations & Viva Highlights
Academic documentation of data sources, algorithms, decision architecture, and ethical boundaries.
"""
import streamlit as st

from src.config import Config
from src.visualization.theme import (
    apply_streamlit_theme,
    render_data_banner,
    render_disclaimer,
)

st.set_page_config(page_title="Methodology | SPORTZA", page_icon="📖", layout="wide")
apply_streamlit_theme()

st.title("📖 Methodology, Architecture & Academic Governance")
st.markdown("Defensible, transparent sports science engineering: from SoccerMon telemetry to auditable decision support.")

st.markdown(render_data_banner(True, attribution=Config().DATASET_ATTRIBUTION), unsafe_allow_html=True)
st.markdown(render_disclaimer(), unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs([
    "📐 System Architecture",
    "⚖️ Decision Support Rules",
    "🔬 Machine Learning Rigor",
    "🎓 Academic Viva Highlights"
])

with tab1:
    st.subheader("System Architecture & Data Pipelines")
    st.markdown("""
    SPORTZA adopts a multi-tier, decoupled architecture designed for reproducibility and safety:
    
    1. **Data Ingestion Tier (`src/data/`)**:
       - Multi-format adapters supporting raw Zenodo CSV/JSON distributions, upstream Excel workbooks, and deterministic synthetic demo fixtures.
       - Canonical schema validation (`schema.py`) ensuring type safety and graceful missing-file degradation.
    
    2. **Feature Engineering Tier (`src/features/`)**:
       - Point-in-time temporal alignment pipeline enforcing **zero future leakage**.
       - Intra-individual rolling baselines (28-day window) and z-score standardizations.
       - Standardized internal training load metrics: session sRPE, ATL (7-day mean), CTL (28-day mean), ACWR, monotony, and strain.
    
    3. **Decision Support Tier (`src/decision_support/`)**:
       - Deterministic rule precedence matrix preventing black-box recommendations.
       - Structured escalation triggers for athlete-reported pain/injury and systemic illness.
       - Complete in-memory audit log recording evaluation snapshots for clinical inspection.
    
    4. **Visualization & Analytics Tier (`src/visualization/`, `pages/`)**:
       - Plotly interactive dashboards in accessible dark mode.
       - Clear provenance tracking and non-medical disclaimers on every interface.
    """)

with tab2:
    st.subheader("Decision Support Engine Matrix")
    st.markdown("""
    Recommendations are generated through an explicit, auditable priority cascade:
    
    | Priority | Condition / Pattern | Status Output | Action / Review Window |
    |---|---|---|---|
    | **1 (Highest)** | Recent self-reported major pain, acute injury, or systemic illness | `Human review needed` | Escalation flag raised; prompt referral to qualified sports clinician or physician. |
    | **2** | Insufficient recent reporting (<7 days in 28-day window) | `Insufficient data` | Assessment suppressed to prevent erroneous conclusions; requests data completion. |
    | **3** | Rising chronic workload + concurrent degradation in readiness, soreness, or sleep | `Recovery-focused option` | Suggests active recovery, session intensity reduction; reassess within 24–48 hours. |
    | **4** | Isolated high workload without adverse wellness deviation | `Monitor` | Notes elevated exposure; recommends routine monitoring without alarmist clinical claims. |
    | **5 (Default)** | Metrics within normal intra-individual baseline bounds | `Monitor` | Normal cadence; reassess on next training day. |
    
    > **Non-Prescriptive Principle:** SPORTZA never outputs automated "take N rest days" prescriptions or unilateral clearance to play. All outputs are decision aids for qualified human practitioners.
    """)

with tab3:
    st.subheader("Machine Learning Validation Standards")
    st.markdown("""
    To avoid academic inflation and spurious claims, SPORTZA adheres to strict validation standards:
    
    - **Chronological Holdouts Only:** Random train/test shuffling in sequential sports data causes severe temporal autocorrelation leakage. All models are trained on past dates and evaluated on future dates.
    - **Naïve Baseline Benchmarking:** Every predictive regression model is benchmarked against Last Observation Carried Forward (LOCF) and rolling 7-day means. A model is only valuable if it beats these naïve heuristics.
    - **Pre-flight Gating on Rare Events:** With only 306 self-reported injury events in SoccerMon, fitting unconstrained deep learning models produces severe overfitting. SPORTZA gates risk modeling and transparently falls back to descriptive epidemiological analysis.
    """)

with tab4:
    st.subheader("Academic Viva Q&A Highlights")
    st.markdown("""
    **Q1: How does SPORTZA handle the subjectivity of athlete reports?**  
    *Answer:* Rather than assuming self-reported numbers (e.g. readiness 6/10) mean the same thing across athletes, SPORTZA standardizes every score against that athlete's personal 28-day rolling mean and standard deviation. A score of 6 for an athlete whose baseline is 8 represents a significant deviation, whereas for an athlete whose baseline is 5 it represents an improvement.
    
    **Q2: Why not use deep neural networks (e.g. LSTM) for all predictions?**  
    *Answer:* Empirical benchmarking on the SoccerMon dataset shows that Gradient Boosting regressors with carefully engineered rolling lag features achieve comparable or superior MAE without requiring massive hyperparameter tuning or black-box explainability risks. Furthermore, transparency and clinical interpretability are paramount in sports medicine.
    
    **Q3: How does SPORTZA ensure ethical safety?**  
    *Answer:* SPORTZA explicitly disclaims diagnostic authority, distinguishes between self-reported pain and clinical diagnosis, presents review windows (e.g. 24–48 hours) rather than mandatory rest days, and gates automated risk models when statistical power is insufficient.
    """)

