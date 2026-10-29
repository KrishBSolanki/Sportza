# SPORTZA — Project Audit & Implementation Status

## 1. Project Overview
- **Project Name:** SPORTZA — Sports Performance, Recovery & Team Intelligence Platform
- **Academic Context:** Semester 7 DSC Project
- **Full Title:** *SPORTZA: An Explainable Athlete Wellness, Recovery Decision-Support and Performance Forecasting Platform Using SoccerMon*
- **Primary Data Source:** SoccerMon (Toppserien elite women's football dataset, 2020–2021)
- **Licensing:** Creative Commons Attribution 4.0 International (CC BY 4.0)

---

## 2. Architecture & File Inventory

```
sportza/
├── app.py                             # Main application entry point & data cache
├── requirements.txt                   # Pinned production dependencies
├── .env / .env.example                # Runtime environment configuration
├── preprocessing/                     # Preserved upstream SoccerMon loaders
│   ├── data_loader.py
│   ├── read_in_data.py
│   └── run_team_pickle_generation.py
├── pages/                             # 11 interactive Streamlit dashboard modules
│   ├── 1_Executive_Overview.py
│   ├── 2_Athlete_Explorer.py
│   ├── 3_Readiness_Recovery.py
│   ├── 4_Workload_Analytics.py
│   ├── 5_Injury_Research.py
│   ├── 6_Performance_Forecast.py
│   ├── 7_Team_Position_Analysis.py
│   ├── 8_Correlation_Lab.py
│   ├── 9_Model_Lab.py
│   ├── 10_Data_Quality.py
│   └── 11_Methodology.py
├── src/
│   ├── config.py                      # Global paths, data scales, attribution
│   ├── data/
│   │   ├── demo_generator.py          # Deterministic synthetic data generator (seed=42)
│   │   ├── discovery.py               # Dataset discovery & validation reporting
│   │   ├── schema.py                  # Canonical table schemas & type checks
│   │   └── soccermon_adapter.py       # Dual-format adapter (Zenodo CSV/JSON + Excel)
│   ├── decision_support/
│   │   ├── audit.py                   # In-memory append-only decision audit logging
│   │   ├── baseline.py                # Intra-individual rolling baselines & z-scores
│   │   ├── explanation.py             # Human-readable cards and audit formatters
│   │   └── rules.py                   # Deterministic prioritization decision engine
│   ├── features/
│   │   ├── temporal.py                # Leakage-free point-in-time feature pipeline
│   │   ├── wellness.py                # Baseline deviations, data coverage metrics
│   │   └── workload.py                # sRPE, ATL, CTL, ACWR, monotony, strain
│   ├── models/
│   │   ├── artifacts.py               # Serialization & ModelRun metadata container
│   │   ├── evaluation.py              # Regression & classification evaluation utilities
│   │   ├── injury_event.py            # Gated injury risk analysis & pre-flight checks
│   │   ├── performance.py             # Game performance post-match rating forecasting
│   │   └── readiness.py               # Next-day readiness GradientBoosting forecaster
│   ├── analytics/
│   │   ├── correlations.py            # Pearson/Spearman matrices & collinearity checks
│   │   ├── descriptive.py             # Squad and team distribution aggregations
│   │   └── positional.py              # Five-panel positional & peak locomotor demand models
│   ├── visualization/
│   │   ├── charts.py                  # Plotly interactive chart builders
│   │   └── theme.py                   # Dark theme design system, KPI cards, banners
│   └── utils/
│       ├── logging.py                 # Structured system logging
│       └── provenance.py              # Data citation & ingestion timestamp metadata
├── tests/                             # 19 passing unit & integration tests
│   ├── test_data_loader.py            # Upstream loader tests
│   ├── test_decision_rules.py         # Rules engine & escalation tests
│   ├── test_demo_generator.py         # Demo data & schema validation tests
│   ├── test_models.py                 # ML training & baseline benchmark tests
│   ├── test_wellness.py               # Personal baseline & deviation tests
│   └── test_workload.py               # Workload equations (sRPE, ATL, CTL, ACWR)
└── docs/                              # Academic documentation & specifications
    ├── PROJECT_AUDIT.md
    ├── DATA_DICTIONARY.md
    ├── MODEL_CARD.md
    ├── DECISION_RULES.md
    ├── METHODOLOGY.md
    └── LIMITATIONS.md
```

---

## 3. Verified Phase Checklist

- [x] **Phase 0 — Audit:** Audited existing repo structure, preserved upstream loaders, established canonical data schema.
- [x] **Phase 1 — Skeleton & Demo Mode:** Implemented dark theme, multi-page routing, and deterministic synthetic demo fixtures.
- [x] **Phase 2 — Data Ingestion:** Implemented `soccermon_adapter.py` supporting both raw Zenodo exports and Excel workbook formats.
- [x] **Phase 3 — Data Quality & EDA:** Missingness matrices, schema validators, descriptive analytics, and inter-team comparisons.
- [x] **Phase 4 — Feature Engineering:** Workload metrics (sRPE, ATL, CTL, ACWR, monotony, strain) and point-in-time temporal pipeline without look-ahead leakage.
- [x] **Phase 5 — Recovery Decision Engine:** Intra-individual rolling z-scores, priority-based triage, clinical escalation flags, and non-prescriptive review windows.
- [x] **Phase 6 — ML Evaluation:** Next-day readiness regression benchmarked against LOCF and rolling mean baselines using chronological holdouts.
- [x] **Phase 7 — Dashboard Polish:** 11 interactive Plotly pages with responsive layouts, KPI summary cards, and source banners.
- [x] **Phase 8 — Reproducibility & QA:** 19 automated unit tests passing in pytest; complete documentation created.

