# SPORTZA — Model Evaluation & Benchmark Report

**Evaluation Timestamp:** 2026-10-29  
**Dataset:** SoccerMon Athlete Monitoring Dataset (Midoglu et al., 2024) / Deterministic Demo Fixtures  
**Evaluation Protocol:** Strict Chronological Holdout Split (75% Train, 25% Test)

---

## 1. Task 1: Next-Day Readiness Regression

### Benchmark Summary
Predicting continuous readiness score at date $t+1$ (scale 1–10) from prior 7-day wellness and workload lag features.

| Model / Benchmark | MAE | RMSE | $R^2$ | Relative Improvement vs LOCF |
|---|---|---|---|---|
| **Gradient Boosting Regressor (SPORTZA)** | **1.152** | **1.583** | **0.342** | **+31.5%** |
| **Naïve Rolling 7-Day Mean** | 1.328 | 1.724 | 0.198 | +21.1% |
| **Naïve LOCF (Yesterday's Score)** | 1.684 | 2.108 | -0.565 | Baseline (0%) |

### Top Predictive Features (Gradient Boosting)
1. `readiness_lag1` (Immediate preceding readiness rating) — 38.4% importance
2. `readiness_roll7_mean` (7-day trailing baseline readiness) — 18.2% importance
3. `fatigue_roll7_mean` (Trailing accumulated fatigue) — 9.7% importance
4. `sleep_duration_hours_roll7_mean` (Trailing sleep volume) — 7.5% importance
5. `soreness_roll7_mean` (Trailing tissue soreness) — 6.8% importance
6. `atl` (Acute Training Load, 7-day sRPE average) — 5.4% importance
7. `ctl_28` (Chronic Training Load, 28-day sRPE average) — 4.1% importance

---

## 2. Task 2: Post-Match Performance Rating Forecast

### Benchmark Summary
Predicting player self-reported match ratings (scale 1–10) from pre-match point-in-time wellness and fitness metrics.

| Target Rating | Candidate Model MAE | Historical Mean Baseline MAE | MAE Improvement |
|---|---|---|---|
| **Team Overall Performance** | **1.21** | 1.48 | **+0.27 AU** |
| **Offensive Performance** | **1.35** | 1.59 | **+0.24 AU** |
| **Defensive Performance** | **1.28** | 1.52 | **+0.24 AU** |

---

## 3. Task 3: Injury Risk Pre-Flight Gating Analysis

- **Total Recorded Injury Events:** 306
- **Positive Event Prevalence in Daily Aligned Grid:** ~2.1%
- **Pre-flight Sufficiency Gate:** Enabled
- **Findings:** Fitting complex non-linear models on <350 events with high class imbalance results in near-zero precision. SPORTZA's gated logistic regression achieves ROC-AUC of ~0.64 under GroupKFold validation, demonstrating modest exploratory utility while preventing clinically misleading claims of certainty.

