# SPORTZA — Decision Engine Rules & Clinical Governance Matrix

SPORTZA implements an auditable, deterministic rules-based decision engine (`src/decision_support/rules.py`) that anchors all recommendations to intra-individual athlete baselines.

---

## 1. Principles of Governance
1. **Intra-Individual Standardization:** All wellness metrics are evaluated as z-score deviations against the athlete's personal 28-day rolling window ($z = \frac{x - \mu_{28}}{\sigma_{28}}$), rather than arbitrary universal thresholds.
2. **Directional Awareness:** 
   - *Higher is better:* Readiness, Mood, Sleep Duration, Sleep Quality ($z < -0.5 \implies$ adverse deviation).
   - *Higher is worse:* Fatigue, Soreness, Stress ($z > +0.5 \implies$ adverse deviation).
3. **Non-Medical Boundary:** The system produces planning review windows (e.g., "reassess in 24–48 hours"), never prescriptions or guaranteed rest durations.

---

## 2. Priority Rule Cascade

```
[Athlete Observation on Date t]
              │
              ▼
   [Data Adequacy Check]
   <7 records in 28 days? ───► YES ───► Status: INSUFFICIENT DATA
              │ NO
              ▼
   [Acute Health Event Check]
   Major pain / Illness? ───► YES ───► Status: HUMAN REVIEW NEEDED (Flagged to clinician)
              │ NO
              ▼
   [Multi-Metric Deviation Check]
   ≥2 wellness metrics adverse (z > 1.0)? ───► YES ───► Status: RECOVERY-FOCUSED OPTION
              │ NO
              ▼
   [Workload / Wellness Mismatch]
   Rising chronic workload + worsening wellness? ───► YES ───► Status: RECOVERY-FOCUSED OPTION
              │ NO
              ▼
   [Workload Spike Only]
   Load spike without adverse wellness? ───► YES ───► Status: MONITOR (Note load exposure)
              │ NO
              ▼
   [Baseline Stability]
   Normal fluctuations within bounds ───► Status: MONITOR (Routine training cadence)
```

---

## 3. Output Status Definitions

| Status | Meaning | Action / Output |
|---|---|---|
| **Monitor** | Observations reflect normal variation within the athlete's baseline bounds. | Continue planned training cadence; reassess at next scheduled morning wellness report. |
| **Recovery-focused option** | Significant adverse wellness deviations or workload-wellness mismatch detected. | Suggests low/moderate load alternatives; conservative review window (e.g. 24–48 hours). |
| **Human review needed** | Acute self-reported major pain, injury event, or systemic illness symptoms. | Escalates to team clinician/physician; suspends automated training intensity clearance. |
| **Insufficient data** | Too few recent submissions (<7 valid days in 28-day window) to compute baseline. | Suppresses recommendation; flags athlete to complete daily wellness reporting. |

