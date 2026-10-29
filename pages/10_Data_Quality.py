"""
SPORTZA — Data Quality, Schema Validation & Provenance
Audit tables, missingness matrices, schema compliance checks, and dataset mounting instructions.
"""
import pandas as pd
import streamlit as st

from src.config import Config
from src.data.discovery import get_data_status
from src.data.schema import validate_dataframe
from src.visualization.charts import missingness_heatmap
from src.visualization.theme import (
    apply_streamlit_theme,
    render_data_banner,
    render_disclaimer,
    render_kpi_card,
)

st.set_page_config(page_title="Data Quality & Provenance | SPORTZA", page_icon="📋", layout="wide")
apply_streamlit_theme()

st.title("📋 Data Quality, Provenance & Schema Audit")
st.markdown("Verifying dataset completeness, schema compliance, missingness rates, and source provenance.")

from app import load_data

data = load_data()
is_demo = data.get("_is_demo", True)
st.markdown(render_data_banner(is_demo, attribution=Config().DATASET_ATTRIBUTION), unsafe_allow_html=True)
st.markdown(render_disclaimer(), unsafe_allow_html=True)

# ── Data Discovery Status ────────────────────────────────────────────────
st.subheader("📁 Dataset Mount & Discovery Status")
status = get_data_status()

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(render_kpi_card("Current Mode", status.get("mode", "Demo").upper(), "Runtime configuration"), unsafe_allow_html=True)
with c2:
    f_count = len(status.get("files_found", []))
    st.markdown(render_kpi_card("Files Detected", str(f_count), "In SPORTZA_DATA_DIR"), unsafe_allow_html=True)
with c3:
    w_count = len(status.get("warnings", []))
    st.markdown(render_kpi_card("Validation Warnings", str(w_count), "Graceful degradations"), unsafe_allow_html=True)

if status.get("warnings"):
    with st.expander("⚠️ View Data Ingestion Warnings"):
        for w in status["warnings"]:
            st.markdown(f"- {w}")

st.divider()

# ── Schema Validation Audit ──────────────────────────────────────────────
st.subheader("🛡️ Schema Conformance Audit")
schema_results = []
for tbl_name in ["wellness_daily", "training_sessions", "injury_events", "illness_events", "game_performance"]:
    if tbl_name in data and isinstance(data[tbl_name], pd.DataFrame):
        df_tbl = data[tbl_name]
        errs = validate_dataframe(df_tbl, tbl_name)
        schema_results.append({
            "Table": tbl_name,
            "Row Count": len(df_tbl),
            "Column Count": len(df_tbl.columns),
            "Status": "✅ Compliant" if len(errs) == 0 else f"⚠️ {len(errs)} Warnings",
            "Missingness Avg": f"{df_tbl.isna().mean().mean() * 100:.1f}%",
        })
st.dataframe(pd.DataFrame(schema_results), use_container_width=True, hide_index=True)

st.divider()

# ── Missingness Heatmap ──────────────────────────────────────────────────
st.subheader("🔍 Athlete Wellness Data Coverage Matrix")
st.caption("Percentage of non-missing observations per athlete across key subjective dimensions.")

wellness_df = data.get("wellness_daily", pd.DataFrame())
if not wellness_df.empty:
    fig_miss = missingness_heatmap(
        wellness_df,
        player_col="player_id",
        value_cols=["readiness", "fatigue", "mood", "sleep_duration_hours", "sleep_quality", "soreness", "stress"],
        title="Athlete Wellness Reporting Completeness"
    )
    st.plotly_chart(fig_miss, use_container_width=True)

st.divider()

# ── Mounting Instructions for Real SoccerMon Data ─────────────────────────
st.subheader("📥 Real SoccerMon Dataset Mounting Instructions")
st.markdown("""
To run SPORTZA on the real Toppserien SoccerMon dataset:

1. **Download Subjective Reports:**
   - Obtain the SoccerMon subjective dataset archive from Zenodo: [https://zenodo.org/records/10033832](https://zenodo.org/records/10033832) (or GitHub: `simula/soccermon`).
   - Extract the CSV/JSON metric files into `data/features/` or `input/features/`.

2. **Configure Environment:**
   - In `.env`, set:
     ```bash
     SPORTZA_DATA_DIR=data/
     SPORTZA_DEMO_MODE=false
     ```

3. **Optional Objective GPS Tracking Data:**
   - The STATSports APEX GNSS archive is approximately **92.3 GB**.
   - If mounted under `data/gps/`, individual session summaries are lazily scanned and cached.
   - When absent, the application gracefully provides subjective analytics and warns that positional small multiples are unavailable.
""")
