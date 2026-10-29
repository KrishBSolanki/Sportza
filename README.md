# ⚽ SPORTZA — Sports Performance, Recovery & Team Intelligence Platform

> **Academic Project:** Semester 7 DSC  
> **Full Title:** *SPORTZA: An Explainable Athlete Wellness, Recovery Decision-Support and Performance Forecasting Platform Using SoccerMon*  
> **Dataset:** SoccerMon (Midoglu et al., 2024, Toppserien elite women's soccer cohort)  
> **License:** Creative Commons Attribution 4.0 International (CC BY 4.0)

---

## 📖 Executive Summary

**SPORTZA** is a decision-support and sports-analytics platform that converts athlete-monitoring telemetry into explainable evidence and cautious, actionable recovery options for coaching and clinical staff.

Key features:
1. **Daily Wellness & Readiness Monitoring:** Intra-individual rolling 28-day baselines ($z$-scores) for readiness, fatigue, sleep quality, soreness, and stress.
2. **Workload Management Analytics:** Quantification of internal training load via session RPE (sRPE), Acute Training Load (ATL, 7d), Chronic Training Load (CTL, 28d), ACWR, monotony, and strain.
3. **Recovery Decision Support Engine:** Deterministic rule matrix with structured clinical escalation flags and conservative non-medical review windows (e.g. 24–48 hours).
4. **Machine Learning Benchmarking:** Next-day readiness forecasting evaluated strictly via chronological holdouts against domain-standard naïve baselines (LOCF and rolling 7-day mean).
5. **Epidemiological Injury Research:** Body location and severity mapping with pre-flight gating to avoid overfitting on sparse positive events.
6. **Positional Locomotor Profiles:** Small multiples of running demands (total distance, high-speed running, sprinting, accelerations) across match positions (CD, FB, CM, WM, FW).

---

## 🚀 Quickstart & Local Installation

### 1. Prerequisites
- Python 3.11+
- Virtual environment tool (`venv`, `conda`, or `uv`)

### 2. Install Dependencies
```bash
# Using uv (recommended, fast)
uv pip install -r requirements.txt

# Or using standard pip
pip install -r requirements.txt
```

### 3. Run the Application
```bash
streamlit run app.py
```
The application will launch automatically in your browser at `http://localhost:8501`.

---

## 🧪 Operational Modes

### 1. Demo Mode (Out-of-the-Box)
SPORTZA ships with an integrated, deterministic synthetic demo generator (`seed=42`).
It automatically synthesizes two complete seasons of daily records across 20 athletes (Team A & Team B) so all 11 pages and ML workflows can be evaluated immediately without downloading external archives.
- Configured in `.env`:
  ```ini
  SPORTZA_DEMO_MODE=true
  SPORTZA_RANDOM_SEED=42
  ```

### 2. Real SoccerMon Dataset Mode
To attach the real Toppserien dataset:
1. Download the subjective dataset archive from Zenodo: [https://zenodo.org/records/10033832](https://zenodo.org/records/10033832).
2. Place the CSV and JSON metric files into `data/features/` or `input/features/`.
3. In `.env`, update:
   ```ini
   SPORTZA_DATA_DIR=data/
   SPORTZA_DEMO_MODE=false
   ```
4. Restart the Streamlit server. The application will detect and ingest real athlete telemetry.

### 3. Optional STATSports GNSS Archive (~92.3 GB)
- The raw 10Hz GNSS tracking files are approximately 92.3 GB.
- When absent, the application displays a graceful notification that GPS tracking files are not mounted, while all subjective wellness, training load, injury research, and recovery modules remain 100% operational.

---

## 🧪 Running Automated Tests

Run the full pytest suite (19 tests covering workload math, wellness baselines, decision rules, schema compliance, and ML models):
```bash
pytest -v
```

---

## 📐 System Architecture

```
sportza/
├── app.py                             # Landing page & cached data loader
├── pages/                             # 11 interactive Streamlit dashboard modules
│   ├── 1_Executive_Overview.py        # Squad KPIs & attention triage panel
│   ├── 2_Athlete_Explorer.py          # Longitudinal individual wellness & load history
│   ├── 3_Readiness_Recovery.py        # Explainable rules-based recovery decision engine
│   ├── 4_Workload_Analytics.py        # sRPE, ATL, CTL, ACWR, monotony, and strain
│   ├── 5_Injury_Research.py           # Body-location heatmap & gated risk modeling
│   ├── 6_Performance_Forecast.py      # Chronological next-day readiness forecasting
│   ├── 7_Team_Position_Analysis.py    # Team A vs Team B boxplots & positional demands
│   ├── 8_Correlation_Lab.py           # Pearson/Spearman heatmaps & collinearity checks
│   ├── 9_Model_Lab.py                 # Candidate ML models vs naïve baselines
│   ├── 10_Data_Quality.py             # Schema audit, missingness matrix & file inventory
│   └── 11_Methodology.py              # Academic governance, viva Q&A, and documentation
├── src/                               # Modular application backend
│   ├── config.py                      # Global configuration & data scales
│   ├── data/                          # Adapters, schema validators, demo generator
│   ├── decision_support/              # Rules engine, baseline math, audit trails
│   ├── features/                      # Workload, wellness, and point-in-time temporal pipeline
│   ├── models/                        # Readiness forecaster, performance forecaster, evaluation
│   ├── analytics/                     # Descriptive stats, correlations, positional profiles
│   ├── visualization/                 # Plotly chart builders & dark theme system
│   └── utils/                         # Logging & dataset attribution
├── tests/                             # 19 passing unit & integration tests
└── docs/                              # Comprehensive academic reports & model cards
```

---

## 🛡️ Medical & Ethical Disclaimer

> **Non-Medical Tool:** SPORTZA is an academic decision-support research tool, not a certified medical device. All recommendations represent statistical pattern analysis designed to assist qualified coaches and sports clinicians. The system does not diagnose injuries, prescribe medical treatments, or unilaterally clear athletes for competition.
