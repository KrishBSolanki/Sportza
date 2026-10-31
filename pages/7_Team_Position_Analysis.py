"""
SPORTZA — Team & Positional Demand Analysis
Squad distributions, inter-team comparisons (Team A vs Team B), and positional locomotor profiles.
"""
import pandas as pd
import plotly.express as px
import streamlit as st

from src.analytics.descriptive import compute_team_comparison
from src.analytics.positional import (
    check_gps_availability,
    generate_synthetic_positional_demands,
)
from src.config import Config
from src.visualization.charts import team_comparison_boxplot
from src.visualization.theme import (
    apply_streamlit_theme,
    get_plotly_layout,
    render_data_banner,
    render_disclaimer,
)

st.set_page_config(page_title="Team & Position Analysis | SPORTZA", page_icon="👥", layout="wide")
apply_streamlit_theme()

st.title("👥 Team & Positional Demand Analysis")
st.markdown("Inter-team longitudinal comparisons, training volume distribution, and field position locomotor requirements.")

from app import load_data

data = load_data()
is_demo = data.get("_is_demo", True)
st.markdown(render_data_banner(is_demo, attribution=Config().DATASET_ATTRIBUTION), unsafe_allow_html=True)
st.markdown(render_disclaimer(), unsafe_allow_html=True)

wellness_df = data.get("wellness_daily", pd.DataFrame())
sessions_df = data.get("training_sessions", pd.DataFrame())

# ── Inter-Team Comparison (Team A vs Team B) ─────────────────────────────
st.subheader("🏟️ Team A vs Team B Training Volume")
st.caption("Recreation of Fig. 7 from SoccerMon paper (Midoglu et al., 2024): annual training sessions per player by team and season.")

if not sessions_df.empty:
    fig_team_box = team_comparison_boxplot(sessions_df, title="Training Sessions Completed per Player (2020 vs 2021)")
    st.plotly_chart(fig_team_box)

    team_comp = compute_team_comparison(wellness_df, sessions_df)
    annual_data = team_comp.get("sessions", {}).get("annual_per_player", {})
    if annual_data:
        rows = []
        for (team, yr), stats in annual_data.items():
            rows.append({
                "Team": team,
                "Season": yr,
                "Athletes (n)": stats["count"],
                "Median Sessions": stats["median"],
                "Mean Sessions": round(stats["mean"], 1),
                "Min - Max": f"{stats['min']} - {stats['max']}",
            })
        st.dataframe(pd.DataFrame(rows), hide_index=True)

st.divider()

# ── Positional Locomotor Demands ─────────────────────────────────────────
st.subheader("📍 Positional Physical Demands (STATSports GNSS)")
gps_status = check_gps_availability()
st.info(f"🛰️ **GPS Dataset Status:** {gps_status['message']}", icon="ℹ️")

st.markdown("""
### Five-Panel Positional Analysis (Reference Research Benchmarks)
Characterization of match physical demands across playing positions:
**Central Defenders (CD)**, **Full-Backs (FB)**, **Central Midfielders (CM)**, **Wide Midfielders (WM)**, and **Forwards (FW)**.
*(Normative data based on Winther et al., 2021, Toppserien elite women's football)*.
""")

pos_df = generate_synthetic_positional_demands()

tabs = st.tabs(["Total Distance", "High-Speed Running (>4.44 m/s)", "Sprinting (>5.55 m/s)", "Accelerations / Decelerations", "Peak 1-Min vs 5-Min Locomotor"])

with tabs[0]:
    fig_td = px.box(
        pos_df, x="position", y="total_distance_m", color="position",
        points="all", title="Total Distance Covered by Position [meters]",
        labels={"total_distance_m": "Total Distance (m)", "position": "Position"},
    )
    fig_td.update_layout(**get_plotly_layout())
    st.plotly_chart(fig_td)

with tabs[1]:
    fig_hsr = px.box(
        pos_df, x="position", y="hsrd_m", color="position",
        points="all", title="High-Speed Running Distance (>4.44 m/s) [meters]",
        labels={"hsrd_m": "HSR Distance (m)", "position": "Position"},
    )
    fig_hsr.update_layout(**get_plotly_layout())
    st.plotly_chart(fig_hsr)

with tabs[2]:
    fig_spd = px.box(
        pos_df, x="position", y="sprint_distance_m", color="position",
        points="all", title="Sprint Distance (>5.55 m/s) [meters]",
        labels={"sprint_distance_m": "Sprint Distance (m)", "position": "Position"},
    )
    fig_spd.update_layout(**get_plotly_layout())
    st.plotly_chart(fig_spd)

with tabs[3]:
    fig_acc = px.box(
        pos_df, x="position", y="acc_distance_m", color="position",
        points="all", title="Distance Covered During Accelerations (>2.26 m/s²) [meters]",
        labels={"acc_distance_m": "Acc Distance (m)", "position": "Position"},
    )
    fig_acc.update_layout(**get_plotly_layout())
    st.plotly_chart(fig_acc)

with tabs[4]:
    # Peak 1-min vs Next 5-min vs Mean 5-min comparison
    peak_melted = pd.melt(
        pos_df,
        id_vars=["position"],
        value_vars=["peak_1min_td", "next_5min_td", "mean_5min_td"],
        var_name="Period",
        value_name="Distance",
    )
    period_labels = {
        "peak_1min_td": "Peak 1-Min",
        "next_5min_td": "Next 5-Min (Transient Fatigue)",
        "mean_5min_td": "Mean 5-Min Match Average",
    }
    peak_melted["Period"] = peak_melted["Period"].map(period_labels)
    fig_peak = px.box(
        peak_melted, x="position", y="Distance", color="Period",
        title="Peak 1-Min vs Subsequent 5-Min vs Match Average Locomotor Intensity",
        labels={"Distance": "Distance (m)", "position": "Position"},
    )
    fig_peak.update_layout(**get_plotly_layout())
    st.plotly_chart(fig_peak)
