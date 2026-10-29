# SPORTZA — Data Dictionary & Canonical Schema

This document formalizes the canonical data tables, variable definitions, measurement units, and scale directions used throughout SPORTZA.

---

## 1. Table: `wellness_daily`
Daily athlete subjective wellness questionnaires collected via PmSys.

| Column | Data Type | Valid Range | Unit / Scale | Direction | Description |
|---|---|---|---|---|---|
| `player_id` | String | e.g. `TeamA_P01` | Anonymized ID | N/A | Unique athlete identifier. |
| `date` | Date / DateTime | 2020-01-01 to 2021-12-31 | YYYY-MM-DD | N/A | Reporting calendar date. |
| `readiness` | Float | 1.0 – 10.0 | Likert 1–10 | Higher is Better | Self-reported readiness to train. |
| `fatigue` | Float | 1.0 – 5.0 | Likert 1–5 | Higher is Worse | Level of physical/mental fatigue. |
| `mood` | Float | 1.0 – 5.0 | Likert 1–5 | Higher is Better | General psychological mood state. |
| `sleep_duration_hours` | Float | 0.0 – 24.0 | Hours | Higher is Better | Self-reported sleep duration. |
| `sleep_quality` | Float | 1.0 – 5.0 | Likert 1–5 | Higher is Better | Perceived sleep restorative quality. |
| `soreness` | Float | 1.0 – 5.0 | Likert 1–5 | Higher is Worse | Muscle soreness and stiffness. |
| `stress` | Float | 1.0 – 10.0 | Likert 1–10 | Higher is Worse | Psychological stress level (source scale 1–10). |
| `source_dataset` | String | `soccermon` / `synthetic_demo` | String | N/A | Provenance tracking flag. |
| `source_file` | String | File path / name | String | N/A | Origin file. |

---

## 2. Table: `training_sessions`
Individual activity, training, and competition session logs.

| Column | Data Type | Valid Range | Formula / Unit | Description |
|---|---|---|---|---|
| `player_id` | String | e.g. `TeamA_P01` | Anonymized ID | Unique athlete identifier. |
| `session_date` | Date / DateTime | 2020-01-01 to 2021-12-31 | YYYY-MM-DD | Date session was completed. |
| `session_type` | String | `team`, `individual`, `competition` | Category | Context of training session. |
| `duration_minutes` | Float | > 0 | Minutes | Duration of training session. |
| `rpe` | Float | 1.0 – 10.0 | Borg CR-10 | Rate of Perceived Exertion. |
| `srpe` | Float | > 0 | `duration_minutes * rpe` [AU] | Session RPE internal workload. |
| `daily_load` | Float | ≥ 0 | `∑ srpe` per day [AU] | Cumulative daily training dose. |
| `weekly_load` | Float | ≥ 0 | `∑ daily_load` (7 days) [AU] | Acute 7-day cumulative load. |
| `atl` | Float | ≥ 0 | Rolling 7-day mean of `daily_load` [AU] | Acute Training Load (fatigue). |
| `ctl_28` | Float | ≥ 0 | Rolling 28-day mean of `daily_load` [AU] | Chronic Training Load (fitness). |
| `acwr` | Float | > 0 (NaN if CTL < 1.0) | `atl / ctl_28` (Unitless ratio) | Acute:Chronic Workload Ratio. |
| `monotony` | Float | > 0 | `mean(daily_load) / std(daily_load)` | Training day-to-day variability. |
| `strain` | Float | ≥ 0 | `weekly_load * monotony` [AU] | Overall weekly physiological strain. |

---

## 3. Table: `injury_events`
Self-reported injury and pain notifications logged via the PmSys body-map screen.

| Column | Data Type | Valid Values | Description |
|---|---|---|---|
| `player_id` | String | Anonymized ID | Reporting athlete identifier. |
| `date` / `event_date` | Date / DateTime | YYYY-MM-DD | Date pain/injury was logged. |
| `body_location` | String | 22 anatomical zones (e.g. `left_knee`, `right_hamstring`, `groin`, `ankle`) | Tapped location on body silhouette. |
| `severity` / `reported_severity` | String | `minor`, `major` | Tap count: single tap = minor; double tap = major. |
| `is_self_reported` | Boolean | `True` | Flags that record is athlete-reported, not a clinical diagnosis. |

---

## 4. Table: `illness_events`
Self-reported systemic illness notifications.

| Column | Data Type | Description |
|---|---|---|
| `player_id` | String | Reporting athlete identifier. |
| `date` / `event_date` | Date / DateTime | Date symptoms were reported. |
| `symptoms` | String | Reported symptoms (e.g. fever, headache, cough, sore throat). |
| `is_self_reported` | Boolean | Flags that record is athlete-reported, not a clinical diagnosis. |

---

## 5. Table: `game_performance`
Post-match subjective evaluation ratings.

| Column | Data Type | Scale | Description |
|---|---|---|---|
| `player_id` | String | Anonymized ID | Reporting athlete identifier. |
| `date` | Date / DateTime | YYYY-MM-DD | Match date. |
| `team_performance` | Float | 1.0 – 10.0 | Self-rated overall team match performance. |
| `offensive_performance` | Float | 1.0 – 10.0 | Self-rated individual offensive performance. |
| `defensive_performance` | Float | 1.0 – 10.0 | Self-rated individual defensive performance. |

