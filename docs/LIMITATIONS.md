# SPORTZA — Limitations & Ethical Scope

This document details the scientific, technical, and operational boundaries of SPORTZA for academic evaluation.

---

## 1. Domain & Sport Specificity
- **Football/Soccer Specific:** The telemetry and normative baselines in SPORTZA originate exclusively from elite female soccer athletes competing in the Norwegian Toppserien (2020–2021 seasons).
- **Extensible Architecture, Not Multi-Sport Validation:** While the internal schema is adaptable to other intermittent team sports (e.g. rugby, basketball), multi-sport prediction claims must remain unvalidated until sport-specific external cohorts are ingested and independently evaluated.

---

## 2. Subjective Self-Report Limitations
- **Perceptual Biases:** Ratings of readiness (1–10), fatigue (1–5), and RPE (1–10) are subjective constructs. Factors such as upcoming match selection, personal stressors, or mood swings can introduce unobserved variance.
- **Reporting Missingness:** In professional athlete cohorts, athletes occasionally omit daily morning reports. Incomplete reporting (~15% missingness in SoccerMon) requires temporal imputation or explicit coverage gating rather than assuming missing days indicate perfect wellness.

---

## 3. Injury & Medical Governance
- **Pain Notifications vs Clinical Diagnoses:** In SoccerMon, injury logs represent player taps on an anatomical body silhouette (minor pain vs major pain). They lack clinical MRI/ultrasound verification, physician notes, or diagnostic codes (ICD-11 / OSICS).
- **Non-Diagnostic Scope:** SPORTZA does not provide medical diagnoses, treatment prescriptions, or unilateral return-to-play clearances. It provides decision support and triage flags for qualified sports clinicians and coaches.
- **Rare Event Modeling Hazard:** With only 306 injury entries spread across two seasons and 50 athletes, injuries are statistically rare events. Applying unconstrained deep neural networks on such sparse positive labels results in severe overfitting; SPORTZA enforces strict pre-flight gating.

---

## 4. Hardware & GPS Archive Size
- **92.3 GB Raw GNSS Tracking Archive:** The raw STATSports Apex 10Hz position data encompasses over six billion records. Running the system on resource-constrained consumer hardware or local development environments requires lazy scanning and summary caching. Positional small multiples degrade gracefully when raw GNSS files are unmounted.

