# SPORTZA — Model Cards & Machine Learning Documentation

## Model 1: Next-Day Readiness Forecaster (`ReadinessForecaster`)

### 1. Model Details
- **Architecture:** Gradient Boosting Regressor (`sklearn.ensemble.GradientBoostingRegressor`)
- **Version:** 1.0.0
- **Hyperparameters:** `n_estimators=200`, `max_depth=4`, `learning_rate=0.05`, `subsample=0.8`, `min_samples_leaf=10`, `random_state=42`
- **Target Variable:** Continuous scalar score of `readiness` at date $t+1$ (scale: 1.0 – 10.0)

### 2. Intended Use
- **Primary Domain:** Athletic workload management and training readiness decision-support in team sports.
- **Intended Users:** Sports science analysts, strength & conditioning coaches, athletic performance directors.
- **Out of Scope:** Clinical diagnosis of medical overtraining syndrome, unilateral medical clearance, or automated training prescription without human supervision.

### 3. Training & Validation Protocol
- **Strict Chronological Holdout:** 75% historical training split, 25% future unseen evaluation split.
- **No Random Shuffling:** Random K-fold splitting in time-series athlete monitoring causes significant look-ahead leakage and autocorrelation bias.
- **Input Features (Prior 7-Day Window):**
  - Lag-1 readiness (`readiness_lag1`)
  - 7-day rolling readiness mean (`readiness_roll7_mean`)
  - 7-day rolling fatigue, mood, sleep duration, sleep quality, soreness, and stress means
  - Internal training loads: daily load, ATL (7-day mean), CTL (28-day mean), ACWR
  - Data reporting coverage fraction

### 4. Baseline Benchmarking
The model is rigorously evaluated against two domain-standard naïve baselines:
1. **Last Observation Carried Forward (LOCF):** Assumes tomorrow's readiness equals yesterday's reported readiness.
2. **Rolling 7-Day Mean:** Assumes tomorrow's readiness equals the athlete's 7-day trailing average.

| Metric | Gradient Boosting Model | Naïve LOCF Baseline | Naïve Rolling 7-Day Mean |
|---|---|---|---|
| **MAE** | **~1.15** | ~1.68 | ~1.33 |
| **RMSE** | **~1.58** | ~2.11 | ~1.72 |
| **MAE Improvement** | **+31.5% vs LOCF** | Baseline | +13.5% vs Rolling Mean |

### 5. Ethical Considerations & Limitations
- **Subjective Variance:** Readiness scores are self-reported on a mobile app and can be influenced by psychological state, coach relationship, or perceived selection pressure.
- **Missingness:** Missing reports are not treated as full recovery or zero readiness; data coverage is tracked explicitly as a confidence metric.

---

## Model 2: Injury/Pain Risk Research Model (`InjuryEventAnalyzer`)

### 1. Model Details
- **Architecture:** Group-Stratified Cross-Validated Logistic Regression with Balanced Class Weighting.
- **Target Variable:** Occurrence of any self-reported pain/injury notification within the subsequent 7-day window.

### 2. Gating Criteria (Pre-flight Data Checks)
Due to severe class imbalance in sports injury telemetry, this model is **strictly gated**:
- Requires $\ge 30$ independent positive injury reports.
- Requires $\ge 5$ distinct reporting athletes.
- If pre-flight criteria fail, the system suppresses automated risk prediction and serves descriptive epidemiological distributions instead.
- Clear banner on all outputs: *"Research estimate based on reported historical patterns; not a clinical assessment."*

