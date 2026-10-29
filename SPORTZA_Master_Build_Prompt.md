# MASTER BUILD PROMPT — SPORTZA
## Semester 7 DSC | Athlete Wellness, Recovery Decision Support, Injury Research & Sports Performance Forecasting

You are Claude Code acting as a senior full-stack engineer, ML engineer, sports-data analyst, UX designer, test engineer, and technical writer. Build a complete, working, reproducible, demo-ready academic DSC project named **SPORTZA — Sports Performance, Recovery & Team Intelligence Platform**.

Do not just produce a plan, mockup, or a pile of disconnected code. Inspect the existing workspace and supplied material, implement in small verifiable phases, run tests, fix defects, and leave a fully runnable repository with documentation. Never claim a feature works until you have run it or clearly mark it as not verified. Do not stop after scaffolding.

---

# 1. PRIMARY MISSION

Build a decision-oriented sports analytics platform that turns SoccerMon athlete-monitoring data into understandable evidence and cautious, actionable suggestions for:

1. Daily wellness and readiness monitoring.
2. Training-load trends and workload-management insights.
3. Recovery planning suggestions expressed as **review windows and low/moderate/high load options**, never a medical prescription or a guaranteed number of rest days.
4. Research-oriented injury-event risk modelling, only if valid pre-event labels and sufficient examples exist.
5. Player performance forecasting, including future readiness and available game-performance ratings.
6. Squad-level, player-level, and positional analysis.
7. Clear explanations of why each recommendation was produced, how confident it is, what data is missing, and what a coach/medical professional should review.

The project should look and feel like a polished, modern sports-science product, not a basic college dashboard. The goal is a strong, defensible academic submission—not inflated scores, fake clinical certainty, or hardcoded data disguised as real analytics.

## Academic project title
**SPORTZA: An Explainable Athlete Wellness, Recovery Decision-Support and Performance Forecasting Platform Using SoccerMon**

Use “multi-sport extensible” in the architecture, but be honest: SoccerMon is football/soccer data. Do not claim validated multi-sport prediction until sport-specific datasets have actually been integrated and independently evaluated.

---

# 2. FIRST ACTION: INSPECT THE INPUTS AND EXISTING WORKSPACE

Before creating/editing files:

1. Inspect the repository and determine whether an implementation already exists.
2. Inspect all provided project context files, especially `sportza.txt`, plus the supplied figures/screenshots:
   - Readiness/wellness/training-load correlation heatmap.
   - Position-wise peak 1-minute, next 5-minute and mean 5-minute load distributions for total distance, high-speed running, sprinting, acceleration and deceleration.
   - Training-session count boxplot by team/year.
   - Injury count heatmap by body location and severity.
   - PmSys-style game performance reporting workflow.
   - Injury body-map reporting and review screens.
   - Session RPE reporting workflow.
3. Treat screenshots as reference material for proposed features and chart selection, not as proof that the supplied project already has these functionalities.
4. Inspect the official repository: https://github.com/simula/soccermon
   - Read its README, environment, preprocessing modules, tests, and data format assumptions.
   - Reuse or adapt its preprocessing thoughtfully with attribution and preserve the upstream license.
   - Confirm the upstream repository is a loader/processing code repository; the data must be separately downloaded and mounted/provided. Do not pretend data exists in the GitHub clone.
   - Do not copy data or binary archives into Git.
5. Inventory files, dependencies, current app entrypoints and run commands. Preserve useful existing code rather than overwriting blindly.
6. Create `docs/PROJECT_AUDIT.md` with current structure, assumptions, source coverage, gaps, and a phase checklist.
7. Create `docs/DATA_DICTIONARY.md` and `docs/MODEL_CARD.md` early; update them to match the actual implementation.

If a source file or column is not available, state that explicitly and implement graceful dataset detection rather than guessing its schema. The final app must run in a **demo-data mode** even before the full dataset is mounted.

---

# 3. SOURCE DATA AND NON-NEGOTIABLE DATA TRUTH

## Primary source: SoccerMon

Repository and paper:
- GitHub code: https://github.com/simula/soccermon
- Dataset: https://zenodo.org/records/10033832
- Paper: https://pmc.ncbi.nlm.nih.gov/articles/PMC11139986/

The paper describes data collected from two elite Norwegian women’s soccer teams during the 2020 and 2021 seasons. It reports:
- 33,849 subjective reports: 16,261 training-load reports, 17,002 wellness reports, 306 individual injury entries, 32 illness-symptom entries and 248 game-performance reports.
- 10,075 objective GPS reports, containing more than six billion position/sensor measurements in aggregate.
- Subjective dataset size about 9.3 MB and objective files about 92.3 GB.
- The underlying source is licensed CC BY 4.0; credit the authors and dataset, and include the attribution and source link wherever the dataset is discussed.
- Subjective values include training duration/type/RPE, fatigue, mood, readiness, sleep duration/quality, soreness, stress, injury body location/severity, illness symptoms, and player-reported team/defensive/offensive match ratings.
- Objective sensor fields can include heart rate, lat/lon, speed, GPS quality, acceleration, and gyroscope values.
- These injury entries are player-reported pain/location/severity notifications and are **not medical diagnoses**.
- Wellness reporting is incomplete for some days.
- Player identifiers are anonymized; do not try to re-identify anyone.
- The upstream repository restructuring script expects separate subjectively organized input files and does not bundle the full data.
- Some original values may be stored per metric in CSV/JSON; objective session files can be Parquet and organized hierarchically. Inspect the actual download; do not assume one flat CSV.

## Optional auxiliary sources

Design adapters so that additional public sources can be integrated later. Do not make them required for the initial working version. Potential examples:
- PhysioNet wearable data, only if the required files/labels/license are verified.
- Public runner-injury data only after its exact record, label definition, source provenance and license are verified.
- Free sports statistics API only if keys and quota are configured by the user. Live match data is a separate domain from athlete health; never fabricate a link between a public match player and an anonymized SoccerMon athlete.

If auxiliary sources cannot be downloaded or their labels are not suitable, record the limitation and complete the core project with SoccerMon plus synthetic demo data explicitly labeled as synthetic.

---

# 4. REQUIRED PRODUCT EXPERIENCE

Build a responsive application for desktop and tablet, suitable for a project demonstration. Default to a clean, minimal, high-quality dark theme with tasteful accent colors, strong contrast, clear typography, compact filters, polished data visualizations and no decorative chart clutter. It must still be legible and usable in light mode if implemented.

## Application sections

### A. Executive Overview
- KPIs: number of players available in the loaded data, reports in selected date range, percentage of expected wellness reports present, sessions in range, injury/pain reports in range, latest readiness median/mean where meaningful.
- “What needs attention today” panel driven by transparent rules.
- Squad readiness distribution and 7/28-day load trend.
- Clear dataset status (real dataset / demo data), refresh/update timestamp, source attribution.
- Never imply public historic data is live or current.

### B. Athlete Explorer
- Search/filter by anonymized player ID, team, date range, and sport if available.
- Player detail: recent wellness, sleep, fatigue, mood, readiness, soreness, stress, session RPE, session duration and training-load summaries.
- For each plot show a meaningful title, correct axis labels/units, tooltip, accessible colors, legend, data-source note and missingness treatment.
- Show data sufficiency and latest observation date.
- Display a “why this matters” explanation that distinguishes observed measures from model estimates.
- Do not show fake player names, ages, sex, positions or biometric data unless the source contains them.

### C. Daily Readiness & Recovery Decision Support
This is a primary differentiator. Provide an explainable recommendation engine with:
- Current wellness snapshot.
- Change relative to the player’s own recent baseline, where enough history exists.
- Workload in the last 1, 7, and 28 days; ATL/CTL/ACWR/monotony/strain only where defined and supported by the source data.
- Confidence/data coverage status.
- Human-readable suggested training/recovery options.
- Factors that increased or decreased the suggestion.
- Suggested next review time/date only as a planning aid.
- Escalation when injury/pain or illness was reported.
- A transparent “review with sports clinician/qualified coach” statement for injury/illness flags.

**Recovery-days requirement:** The system may recommend a conservative review window such as “consider a recovery-focused day and reassess tomorrow” or “reduce high-intensity load until reviewed,” but must not diagnose injury, guarantee recovery duration, prescribe an exact rest-day count as a medical fact, or clear anyone to play. A number of days can be displayed only as a non-medical, adjustable planning window with clear caveat, and should preferably be a range such as “review over the next 24–48 hours.” The engine must not make medical decisions.

Use transparent rules first, and only add a learned model when appropriate data and validation exist. Do not use a made-up weighted score and call it medically validated. If a composite readiness index is shown, label it “experimental dashboard index,” disclose components and weighting, and keep the original reported readiness visible.

### D. Workload & Training Analytics
- Daily/weekly load, session duration, RPE and sRPE.
- Monotony and strain if they can be calculated properly.
- Acute and chronic load summaries with explicit window definitions.
- Position-wise physical-demand analysis if position and GPS session mapping are available.
- Peak locomotor periods: peak 1-minute vs following 5-minute vs mean 5-minute periods, using definitions and thresholds documented in the source/paper or derived from a configurable method.
- Load by session type and team/year.
- Explain that correlation does not establish causation and ACWR is not a deterministic injury test.
- Avoid duplicate information due to high collinearity among features derived from RPE/duration.

### E. Injury & Health Events (research interface)
- Injury/pain report counts over time, body-location/severity heatmap and event timeline.
- Make clear reports are self-reported, not clinically diagnosed.
- Do not merge consecutive-day entries silently. Provide configurable event grouping and document that grouping changes target counts.
- Show label imbalance (there are relatively few injury entries), event count and uncertainty.
- Risk modelling must be optional and gated by pre-flight data checks:
  - Define target window (for example, a future 7-day report event) before training.
  - Build one row per player-date or player-week with predictor values strictly preceding the target date.
  - Choose negative examples from eligible player-date windows with no event during target horizon.
  - Handle recurrent events and same-day events explicitly.
  - Exclude features recorded after or simultaneously with the target event.
  - Prevent temporal leakage and player leakage; report a chronological holdout and, when feasible, grouped player holdout.
  - Compare against a naive prevalence baseline and a simple interpretable model.
  - Report precision, recall, F1, PR-AUC, confusion matrix and calibration when feasible.
  - Do not oversample before data splitting. Do not present accuracy alone.
  - If the number of independent events is too small for a credible model, disable prediction and show exploratory association analysis instead.
- Explicit statement: “Research estimate based on reported historical patterns; not a clinical assessment.”

### F. Performance Forecasting
- Forecast source-supported target values only, such as next-day readiness, next-day wellness value or future player-reported match ratings where enough points exist.
- Include a baseline such as last-observation-carried-forward or seasonal/rolling mean.
- Compare against a simple ML model. LSTM/complex deep learning is optional only if the data volume, chronological validation and compute budget justify it.
- Use a time-respecting split, such as earlier dates train, later dates validation/test, never random row splitting for temporal targets.
- Report MAE/RMSE for regression; show actual vs forecast, residuals, uncertainty if defensible, forecast horizon and baseline performance.
- Do not claim exact match outcomes or “fitness levels” if the target does not measure those.

### G. Team / Position Analysis
- Squad distribution of readiness, wellness and load.
- Between-team/year comparison where supported.
- Positional demand plots for CB/FB/CM/WM/FW only if position metadata and appropriate GPS session data are present. Do not assume that positions exist in all files.
- Boxplots or violin plots with raw points, sample sizes and distribution statistics.
- Clearly display sample size and suppress strong comparisons when n is too small.
- Use statistical significance stars only when a defined test, multiple-comparison handling and sample-size check are implemented; otherwise show effect sizes and confidence intervals.
- The user’s supplied reference image with Team A/B yearly session-count boxplots should be recreated if matching metadata can be computed. Do not hand-code the plotted values.

### H. Correlation & Research Insights
- Interactive Pearson and Spearman correlation heatmaps, choose pairwise complete observations and report sample sizes.
- Optional partial correlation / multivariable models only if meaningful.
- Use supplied reference heatmap as a visual benchmark, but calculate the result from real loaded data; never hardcode its values.
- Clearly distinguish descriptive correlation from predictive or causal conclusions.
- Check collinearity and do not feed derivations of the same source fields indiscriminately into the same model.

### I. Data Quality & Provenance
- File inventory; row counts and schema per file.
- Missing-value heatmap/table; duplicate and range checks; timestamp gaps; unit inconsistencies; count by report type.
- Data freshness and source attribution.
- Download/mount instructions for SoccerMon data.
- Validation messages for missing optional input files; the app should not crash merely because GPS objective data or optional injury files are absent.
- When GPS data is not loaded due to size, tell the user that the GPS/position visualizations are unavailable and the subjective modules are still active.

### J. Model Lab / Evaluation
- Model/task selector; target; prediction horizon; number of rows/features; split date; baseline and candidate metrics.
- Confusion matrix and PR curve for classification; calibration curve if supported.
- Actual-vs-predicted and residual plots for regression.
- Feature importance or SHAP only if the model and installed library support it; no fabricated explainability.
- Save model, preprocessing pipeline, feature list, config, timestamp, target definition, evaluation metrics and source metadata together.
- “No validated model available” state when training criteria fail.

### K. Project Research & Reproducibility
- Dataset card; licensing and citation.
- Methods and limitations.
- Experiment log and model card.
- Export cleaned aggregates/reports without exposing identity.
- “About this project” page explaining academic scope and the difference between observations, estimates and decision support.

---

# 5. CHART SPECIFICATIONS AND REFERENCES

Use the supplied screenshots as design/research references and recreate the strongest applicable charts from real data. A chart is accepted only when data columns, units, and intended inference are valid.

Required charts:
1. Readiness/wellness/load correlation heatmap (Pearson/Spearman toggle).
2. Player readiness, sleep quality, fatigue, stress and soreness time series with missingness markers.
3. Session RPE and sRPE time series.
4. Daily/weekly/28-day load trends.
5. Load distribution by team/year/session type with boxplot or violin plot and raw observations.
6. Injury/pain report severity × body-location heatmap.
7. Injury timeline with minor/major category clearly identified as self-reported severity.
8. Position-wise small multiples for total distance, high-speed running distance, sprint distance, acceleration and deceleration. Recreate the supplied five-panel plot concept only when GPS features and player positions can be aligned.
9. Peak 1-min vs next 5-min vs mean 5-min physical demand comparisons by position, using a well-documented and computationally manageable algorithm.
10. Actual-vs-predicted readiness chart for temporal validation and residual analysis.
11. Team A/Team B season and year comparison with sample sizes, confidence intervals/effect sizes where appropriate.
12. Missingness/data coverage matrix for reports by player/date.
13. Feature importance chart for validated models.
14. Decision explanation: factor contributions displayed as rule reasons, not pseudo-SHAP.
15. Dashboard KPI cards with explicit dates and counts.

Use Plotly for interactive charts where possible. Use readable axes, units, responsive layout, consistent semantic colors, meaningful tooltips and no misleading truncated axes. All chart computation belongs in Python/data layer; UI must not create fake metrics.

---

# 6. DATA ENGINEERING AND CANONICAL SCHEMA

Preserve raw source data and create derived, tidy tables. Implement data adapters because report types may have different schemas/granularity.

Target canonical tables:

## `wellness_daily`
- `player_id` (anonymized)
- `date`
- `readiness` (source scale, 1–10)
- `sleep_duration_hours`
- `sleep_quality` (source scale, 1–5)
- `fatigue` (source scale, 1–5)
- `mood` (source scale, actual source scale)
- `soreness` (source scale, 1–5)
- `stress` (use actual source scale; do not assume the same 1–5 scale—the supplied source describes stress as 1–10)
- `menstruation` only if present and appropriate, access-restricted and excluded from default dashboards unless the research purpose warrants it
- `source_file`, `source_dataset`, `ingested_at`

## `training_sessions`
- `player_id`
- `session_timestamp`, `session_date`
- `session_type`, `session_keywords`
- `duration_minutes`
- `rpe` (1–10)
- `srpe = duration_minutes * rpe`
- `daily_load`, `weekly_load`, `atl`, `ctl_28`, `ctl_42`, `acwr`, `monotony`, `strain` when calculable or in the source
- `source_dataset`, `source_file`

**Unit definition:** internally use minutes consistently for duration and sRPE units; if comparing against source-calculated metrics that use another duration unit, reconcile and document that before use. Do not blindly mix minute-based and hour-based sRPE. Validate derived results against upstream values.

## `injury_events`
- `player_id`, `event_timestamp`, `event_date`
- `body_location`
- `reported_severity` (minor/major from player report)
- `is_self_reported = true`
- `grouped_event_id` only when an explicitly selected grouping procedure is used
- `source_dataset`, `source_file`

## `illness_events`
- `player_id`, `event_timestamp`, `symptom`
- `is_self_reported = true`
- source metadata

## `game_performance`
- `player_id`, `match_timestamp`
- `team_performance`, `offensive_performance`, `defensive_performance` (source scale 1–10)
- `source_dataset`, `source_file`

## `gps_sessions` / `gps_features`
Do not materialize the six-billion-row source as one pandas DataFrame.
- Store only selected-session summary features in Parquet.
- Use chunked reads, lazy scans or PyArrow/Polars where appropriate.
- Candidate summaries: total distance, maximum speed, high-speed distance, sprint count/distance, accelerations/decelerations, duration, heart-rate summaries and signal-quality indicators—only if they can be correctly calculated from the raw columns.
- Track each summary’s derivation parameters, thresholds and version.
- Treat time zones and timestamp precision consistently.
- Avoid displaying precise coordinates except where the intended, documented research function requires them.

## Other tables
- `athlete_date_features`: one player/date row for temporal models.
- `model_runs`: task, target, horizon, split, metrics, model version and time.
- `decision_log`: input snapshot, applied rules, recommendation text/category, data completeness and timestamp; never write private health or identity details beyond necessary anonymized IDs.

Preserve a `raw/`, `processed/`, `models/`, `reports/` data separation. Avoid committing data files or model blobs unless tiny and intentionally included demo artifacts.

---

# 7. FEATURE ENGINEERING AND TARGET DEFINITIONS

Implement a transparent, tested feature pipeline.

## Workout features
- session sRPE from RPE × duration.
- daily sum of session sRPE.
- rolling 7-day load and longer 28-day/42-day average load.
- load variability/monotony using a documented seven-day definition.
- strain using weekly load × monotony.
- workload ratio only where denominator is non-zero and window policy is explicit.
- optional 7-day versus 28-day/42-day comparison as descriptive workload trend, not an injury verdict.

## Wellness features
- latest wellness values and change from player’s personal rolling baseline.
- rolling means/medians for 7 and 28 days only where adequate observations exist.
- sleep quality/duration deviations, fatigue/soreness/stress changes and readiness trend.
- days since last wellness report, data coverage fraction and recent-report count.
- Do not treat missing reports as good wellness or a score of zero.

## GPS features
- summarize by session, after checking raw structure and measurement frequency.
- configurable thresholds; clearly state which published thresholds are followed.
- high-speed-running/sprint labels must be based on documented thresholds and the correct speed units.
- acceleration/deceleration detection requires smoothing, threshold definition, minimum event duration and validation against the paper where possible.
- do not calculate distance by naïvely summing GPS latitude/longitude differences in degrees.
- handle duplicate timestamps and low GPS quality.

## Predictive tasks
Task 1: next-day readiness regression using prior 7 days of valid observations as a starting baseline. Compare against last-observation and rolling-mean baselines.
Task 2: optional future self-reported injury/pain report within a user-specified fixed horizon, only after target-construction audits and enough events.
Task 3: forecast supported game-performance rating or supported GPS session summary, using chronological splits and adequate temporal points.
Task 4: optional PhysioNet source-defined exercise/stress classification, independently evaluated and not blended into injury model.

For injury forecasting:
- Use player-date snapshots.
- Features must end strictly before the forecast origin time.
- Define target as an injury/pain report in the following H days.
- Carefully prevent overlapping label windows and target leakage.
- If only an event timestamp without a clinically verified diagnosis exists, name the target “future self-reported injury/pain report,” not “injury diagnosis.”
- Use player-group and time-based evaluation where sample permits.
- Show prevalence and a no-skill baseline. Avoid overfitting with 306 injury entries and highly repeated daily rows.
- If data volume or event count is insufficient, do not train/serve the injury risk model. Show descriptive analysis and mark prediction “not supported by available evidence.”

---

# 8. DECISION ENGINE: USEFUL, EXPLAINABLE, SAFE

Implement a deterministic, configurable rules engine as `src/decision_support/` with unit tests. Separate:
1. Observed values.
2. Personal-baseline deviations.
3. Suggested coaching discussion/options.
4. Injury/illness review flags.
5. Optional model estimates.

Build a transparent decision matrix using the data’s known scales and personal baselines rather than universal medical cut-offs:

- Latest readiness is low relative to the player’s own recent baseline AND fatigue/soreness/stress is higher than their baseline → suggestion: consider a lower-intensity or recovery-oriented session and review wellness again the following day.
- Recent sleep-quality/duration deterioration plus a readiness decline → suggest discussing sleep and recovery habits, and reduce high-intensity exposure if the broader training context supports it.
- Rising workload plus worsening wellness or increased self-reported soreness → flag workload/wellness mismatch for human review; do not call it a diagnosed injury.
- Self-reported major pain, persistent/increasing pain, or illness symptoms → prioritize qualified medical/clinical review; do not recommend return to training or assign an automatic recovery day count.
- Isolated training-load spike without worsening wellness or injury information → say “workload above personal trend; monitor and review context,” not “high injury risk.”
- Stable wellness and sufficient recent observations → report “no notable deviation from personal baseline detected,” not “medically fit.”
- Insufficient observations → show “insufficient recent data” and ask for data collection; do not infer the player is recovered.

Use personal rolling baseline (for example, previous 28 available days) with a configurable minimum number of observations and robust statistics. Clearly define whether a higher numeric scale means better or worse for each variable (readiness/sleep quality versus fatigue/soreness/stress). Do not normalize all scales in a way that erases their meaning.

Every recommendation card must include:
- status (`Monitor`, `Recovery-focused option`, `Human review needed`, or `Insufficient data`);
- observed factors;
- baseline comparison and date;
- recommendation rationale;
- what the system cannot infer;
- suggested re-check time window;
- confidence/data adequacy badge based on data sufficiency, not model confidence unless calibrated;
- explicit non-medical, non-diagnostic note.

Do NOT produce a forced “take exactly N rest days” answer. If showing a duration, present a non-medical reassessment window such as “reassess in 24 hours” or “review over 24–48 hours,” and make a clinician/coach responsible for training clearance.

Include a “decision audit” page so an evaluator can trace why the engine issued a suggestion.

---

# 9. MODEL VALIDATION / RESEARCH QUALITY

- Every model must be compared with a simple baseline and evaluated on a never-before-seen chronological holdout.
- Avoid random train_test_split for temporal predictions.
- Use GroupKFold or group-aware validation where suitable; don't mix records from the same individual across folds if that leads to leakage for the intended generalization claim.
- Store target definition, time horizon, cutoff dates and training data signature.
- Regression: MAE, RMSE, R² where appropriate, naïve baseline comparison, predicted vs actual and residual plots.
- Classification: prevalence, PR-AUC, precision, recall, F1, confusion matrix, ROC-AUC only as a secondary metric when useful, calibration where possible.
- Address injury class imbalance with class weighting and threshold selection on validation data. Never tune the test set or oversample before split.
- Avoid target-derived features and post-event records.
- Include feature correlation/VIF or an equivalent collinearity check when appropriate.
- Use random seeds and a reproducible environment.
- Model uncertainty: use calibrated uncertainty or prediction intervals only when justified. Otherwise show no unsupported confidence interval.
- No promises of 99% accuracy or high-grade outcomes. Report actual outcomes, limitations, and failure cases.
- Produce `reports/model_evaluation.md` and `docs/MODEL_CARD.md`.

---

# 10. TECH STACK AND ENGINEERING STANDARDS

Prefer the following unless the inspected workspace establishes a good reason to differ:
- Python 3.11-compatible stack.
- Streamlit for the application.
- Pandas, NumPy, PyArrow (or Polars for large-scale Parquet scans).
- Plotly for interactive charts.
- Scikit-learn for preprocessing, baselines and ML.
- XGBoost only if justified and dependency installation works.
- Statsmodels/SciPy for statistical summaries as needed.
- Pytest for tests.
- Ruff for lint/format.
- Joblib for small model/pipeline artifacts.
- SQLite only for demo/log data when persistence is helpful.
- `requirements.txt` with bounded/known-compatible versions; don't install a huge dependency stack without need.

Requirements:
- Modular structure, type hints for core functions, meaningful docstrings.
- Config through `.env` or environment variables with safe defaults.
- Useful logging and clear, actionable error messages.
- No secrets or user data committed to Git.
- No fragile absolute paths; use pathlib and config.
- Avoid silent exception swallowing.
- Avoid a single giant script.
- Make the core analysis work on CPU; deep learning is optional and should not be necessary to run the app.
- Add `README.md`, `CONTRIBUTING.md` optional, `LICENSE` only if appropriate, `.gitignore`, `requirements.txt`, `.env.example`, `Makefile` or equivalent run commands, and data-download/mount instructions.
- Follow source data/software licenses and provide precise attribution.

Potential repo layout (adapt after the audit):

sportza/
  app.py
  pages/
    1_Executive_Overview.py
    2_Athlete_Explorer.py
    3_Readiness_Recovery.py
    4_Workload_Analytics.py
    5_Injury_Research.py
    6_Performance_Forecast.py
    7_Team_Position_Analysis.py
    8_Correlation_Lab.py
    9_Model_Lab.py
    10_Data_Quality.py
    11_Methodology.py
  src/
    config.py
    data/
      discovery.py
      soccermon_adapter.py
      validation.py
      schema.py
      preprocessing.py
      gps_features.py
      storage.py
    features/
      workload.py
      wellness.py
      temporal.py
    models/
      readiness.py
      injury_event.py
      performance.py
      evaluation.py
      artifacts.py
    decision_support/
      rules.py
      baseline.py
      explanation.py
      audit.py
    analytics/
      descriptive.py
      correlations.py
      positional.py
      peak_periods.py
    visualization/
      charts.py
      theme.py
    utils/
      logging.py
      provenance.py
  tests/
    unit/
    integration/
    model_quality/
  notebooks/
    01_data_audit.ipynb (optional)
    02_exploratory_analysis.ipynb (optional)
    03_model_evaluation.ipynb (optional)
  data/
    raw/.gitkeep
    processed/.gitkeep
    demo/.gitkeep
  models/.gitkeep
  reports/
  docs/
    PROJECT_AUDIT.md
    DATA_DICTIONARY.md
    MODEL_CARD.md
    DECISION_RULES.md
    METHODOLOGY.md
    LIMITATIONS.md

You may adapt page naming to fit the installed Streamlit version; prioritize a functional cohesive application rather than this exact tree.

---

# 11. DEMO DATA, FULL DATA, AND RESOURCE MANAGEMENT

The app must be useful in three states:

1. **Demo mode:** immediately runnable with seeded, clearly synthetic sample data sufficient to exercise all pages. Every screen must label this as synthetic. Never combine synthetic and real rows silently.
2. **Subjective-data mode:** user can mount/download subjective SoccerMon reports; wellness/training/injury/game-report features should activate where available.
3. **GPS/objective-data mode:** optional and lazy-loaded. Because the objective archive is ~92.3 GB, do not ask the user to load everything into RAM. Provide filtering by team/date/session, lazy reads and per-session feature caching. Never assume a local laptop or Colab can hold the entire archive in memory.
4. Use environment variables such as `SPORTZA_DATA_DIR` and a settings panel for data root.
5. Provide dry-run ingestion and a data audit before any expensive transformation.
6. Provide a small seeded demo fixture in repo; ensure any fabricated synthetic examples are clearly documented and not used to claim model performance on real data.

---

# 12. TESTING AND DEFINITION OF DONE

Create tests for:
- sRPE and load-window calculations with known examples.
- zero/negative/invalid durations and RPE bounds.
- missing data and irregular reporting cadence.
- baseline calculations and directionality for each wellness measure.
- recovery-rule precedence when injury/illness is reported.
- date/time alignment and no future leakage.
- target construction around injury events and event-window boundaries.
- temporal/group splits and model-baseline comparison.
- API-optional behavior and missing key.
- no GPS archive present.
- empty/malformed data; invalid schema; duplicate reports.
- chart builders handling empty data and missing categories.
- demo-mode flag and visible source banner.
- loading processed files after app restart.
- deterministic demo dataset.
- basic Streamlit startup or import smoke test.
- export functions and data attribution.

Add a single simple test command (e.g. `pytest -q`) and run it. Also run a lint check. Fix failures. If environment doesn't allow a command, record exactly what couldn't run and why.

Definition of done:
- `streamlit run app.py` starts the app.
- Demo mode can be browsed without downloading data.
- Data can be loaded from a user-configured directory and validated with a clear report.
- At least the core wellness/workload charts use computed demo or real inputs.
- Prediction pages use models genuinely trained/evaluated or clearly show they are unavailable.
- Decision-engine suggestions have traceable factors and explicit limitations.
- Data quality page and methodology/model documentation exist.
- tests pass (or any limitation is honestly documented).
- repository contains no large private/raw datasets or API secrets.
- readme gets a new developer from clone to running demo in a small number of commands.
- Provide a clear summary of implemented features, tests run, data requirements, and known limitations.

---

# 13. EXECUTION WORKFLOW — DO NOT STOP AFTER PLANNING

Work in phases, leaving the project runnable after each phase.

**Phase 0 — Audit:** inspect workspace, source notes, upstream repository, screenshot assets, dependencies. Write audit and plan.

**Phase 1 — Skeleton & Demo Mode:** create app entry point, theme, navigation, seeded synthetic fixtures, source-status banner, tests and run instructions. Verify startup.

**Phase 2 — Data Ingestion:** implement SoccerMon adapter and robust schema detection for CSV/JSON/Parquet. Reuse upstream conventions only after inspection. Support user path and graceful missing files.

**Phase 3 — Data Quality & EDA:** build summaries, missingness, descriptive charts, reference heatmap and seasonal/position charts where data supports them.

**Phase 4 — Feature Engineering:** implement tested workload, wellness, rolling baseline, GPS aggregation and data-coverage features.

**Phase 5 — Recovery Decision Engine:** implement transparent rules, explanations, audit records, UI, and tests before any complicated model.

**Phase 6 — ML Evaluation:** readiness forecast first, performance forecast second, injury-risk model only if data-quality and sample-size gates pass. Persist evaluations/model cards.

**Phase 7 — Dashboard polish:** all key pages, filters, interactive Plotly charts, responsive layout, exports, empty states and error states.

**Phase 8 — Reproducibility & QA:** run end-to-end tests, lint, smoke test, verify a clean install, update documentation, inspect user interface screenshots if tooling permits.

At the end of every phase:
- List exact files changed.
- Run relevant tests.
- Fix errors before advancing.
- Keep the app runnable.
- Do not fabricate success.

If a material ambiguity occurs, make a reasonable documented decision and continue rather than stopping for confirmation. Do not use external paid APIs or require credentials for core functionality.

---

# 14. ACADEMIC REPORT AND DEMO DELIVERABLES

Generate or prepare:
- Project problem statement, motivation and objectives.
- Literature/data source discussion with proper citations.
- System architecture diagram.
- Data-flow diagram and ER/canonical schema diagram.
- Preprocessing methodology.
- Feature engineering and model selection explanation.
- Baseline vs selected model comparison using actual run metrics.
- Screenshots of the implemented dashboard if the environment permits.
- Results, error analysis, limitations and future work.
- Ethical and responsible use section.
- Reproducibility instructions.
- A 5–7 minute demo sequence plus likely viva questions/answers.
- `reports/model_evaluation.md`, `docs/METHODOLOGY.md`, `docs/LIMITATIONS.md`, `docs/DECISION_RULES.md`.

Do not fabricate research references, experiment results, chart findings, accuracy values, model metrics, or medical recommendations.

---

# 15. FINAL RESPONSE FROM THE CODING AGENT

After implementation, respond with:
1. What was actually implemented (not intended).
2. Commands to install and run locally.
3. How to enable demo mode and attach SoccerMon subjective data.
4. Exact files and steps for optional GPS data.
5. Test and lint commands and actual outcomes.
6. Models trained, target definitions, metrics, split design and baseline comparisons.
7. Features not finished and why.
8. Important academic limitations.
9. Suggested final demo path and viva highlights.

Start now by auditing the current workspace, attached `sportza.txt`, the seven supplied chart/screen references, and `simula/soccermon`. Then implement Phase 0 and continue through the phases in this environment. Build the real system; do not return only another plan.
