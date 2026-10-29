"""
SPORTZA — Sports Performance, Recovery & Team Intelligence Platform
Main Streamlit Application Entry Point

An explainable athlete wellness, recovery decision-support and performance
forecasting platform using SoccerMon data.

Data source: SoccerMon Dataset (Midoglu et al., 2024)
Licensed under CC BY 4.0
DOI: https://zenodo.org/doi/10.5281/zenodo.10033832
"""
import sys
from pathlib import Path

import streamlit as st

# Ensure src is importable
sys.path.insert(0, str(Path(__file__).parent))

from src.config import Config
from src.utils.provenance import get_data_mode_label, get_source_attribution
from src.visualization.theme import apply_streamlit_theme

# Page config must be first Streamlit call
st.set_page_config(
    page_title="SPORTZA — Sports Analytics Platform",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "About": (
            "**SPORTZA** v1.0\n\n"
            "An Explainable Athlete Wellness, Recovery Decision-Support "
            "and Performance Forecasting Platform.\n\n"
            "Academic project using SoccerMon data (CC BY 4.0).\n\n"
            "This is a research/decision-support tool, not a medical device."
        ),
    },
)

# Apply dark theme
apply_streamlit_theme()


@st.cache_data(ttl=300)
def load_data():
    """Load data based on configuration. Cached for performance."""
    config = Config()
    
    if config.demo_mode:
        from src.data.demo_generator import generate_demo_data
        data = generate_demo_data(seed=config.random_seed)
        data["_mode"] = "demo"
        data["_is_demo"] = True
        return data
    else:
        from src.data.discovery import get_data_status
        from src.data.soccermon_adapter import load_subjective_data
        
        status = get_data_status()
        data = load_subjective_data(config.data_dir)
        data["_mode"] = status.get("mode", "unknown")
        data["_is_demo"] = False
        data["_status"] = status
        return data


def main():
    """Main application entry point."""
    # Sidebar navigation
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 1rem 0;">
            <h1 style="color: #00D4AA; margin: 0; font-size: 2rem;">⚽ SPORTZA</h1>
            <p style="color: #9E9E9E; font-size: 0.8rem; margin: 0;">
                Sports Performance, Recovery<br>& Team Intelligence Platform
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        # Data mode indicator
        config = Config()
        mode_label = get_data_mode_label(config.demo_mode)
        st.caption(mode_label)
        
        if config.demo_mode:
            st.info(
                "Running in **demo mode** with synthetic data. "
                "Set `SPORTZA_DEMO_MODE=false` and configure "
                "`SPORTZA_DATA_DIR` to load real SoccerMon data.",
                icon="🧪"
            )
        
        st.divider()
        st.caption("Navigation")
        st.page_link("app.py", label="🏠 Home", icon="🏠")
        st.page_link("pages/1_Executive_Overview.py", label="📊 Executive Overview")
        st.page_link("pages/2_Athlete_Explorer.py", label="🏃 Athlete Explorer")
        st.page_link("pages/3_Readiness_Recovery.py", label="💚 Readiness & Recovery")
        st.page_link("pages/4_Workload_Analytics.py", label="📈 Workload Analytics")
        st.page_link("pages/5_Injury_Research.py", label="🩹 Injury Research")
        st.page_link("pages/6_Performance_Forecast.py", label="🎯 Performance Forecast")
        st.page_link("pages/7_Team_Position_Analysis.py", label="👥 Team & Position")
        st.page_link("pages/8_Correlation_Lab.py", label="🔬 Correlation Lab")
        st.page_link("pages/9_Model_Lab.py", label="🤖 Model Lab")
        st.page_link("pages/10_Data_Quality.py", label="📋 Data Quality")
        st.page_link("pages/11_Methodology.py", label="📖 Methodology")
        
        st.divider()
        st.caption(get_source_attribution())
    
    # Main content - Landing page
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0;">
        <h1 style="color: #00D4AA; font-size: 3rem; margin-bottom: 0.5rem;">⚽ SPORTZA</h1>
        <h3 style="color: #9E9E9E; font-weight: 400; margin-top: 0;">
            Sports Performance, Recovery & Team Intelligence Platform
        </h3>
        <p style="color: #757575; max-width: 700px; margin: 1rem auto;">
            An explainable athlete wellness, recovery decision-support and performance
            forecasting platform built on the SoccerMon dataset.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick navigation cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="kpi-card">
            <h4 style="color: #00D4AA;">📊 Overview</h4>
            <p style="color: #9E9E9E; font-size: 0.85rem;">
                Squad KPIs, readiness distribution, and attention alerts
            </p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Go to Overview →", key="nav_overview"):
            st.switch_page("pages/1_Executive_Overview.py")
    
    with col2:
        st.markdown("""
        <div class="kpi-card">
            <h4 style="color: #7C4DFF;">💚 Recovery Support</h4>
            <p style="color: #9E9E9E; font-size: 0.85rem;">
                Evidence-based recovery suggestions with full transparency
            </p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Go to Recovery →", key="nav_recovery"):
            st.switch_page("pages/3_Readiness_Recovery.py")
    
    with col3:
        st.markdown("""
        <div class="kpi-card">
            <h4 style="color: #FFB74D;">🤖 Model Lab</h4>
            <p style="color: #9E9E9E; font-size: 0.85rem;">
                ML model evaluation, metrics, and prediction analysis
            </p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Go to Models →", key="nav_models"):
            st.switch_page("pages/9_Model_Lab.py")
    
    st.divider()
    
    # Academic context
    st.markdown("""
    ### 📚 Academic Context
    
    **Project Title:** SPORTZA: An Explainable Athlete Wellness, Recovery Decision-Support 
    and Performance Forecasting Platform Using SoccerMon
    
    **Semester:** 7th Semester DSC Project
    
    **Key Principles:**
    - 🔍 **Transparency** — Every recommendation explains its reasoning
    - ⚕️ **Safety** — Never makes medical decisions or diagnoses injuries
    - 📊 **Evidence-based** — All metrics computed from real reported data
    - 🧪 **Reproducible** — Seeded demo mode, documented methodology
    - 🏗️ **Extensible** — Multi-sport ready architecture (currently validated for soccer only)
    """)
    
    # Non-medical disclaimer
    st.markdown("""
    ---
    > ⚕️ **Important:** SPORTZA is a decision-support research tool, not a medical device. 
    > All suggestions are based on reported data patterns and should be reviewed by a qualified 
    > sports clinician or coach. This system does not diagnose injuries, prescribe treatment, 
    > or clear athletes for participation.
    """)


if __name__ == "__main__":
    main()

