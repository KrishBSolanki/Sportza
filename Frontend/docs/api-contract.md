# SPORTZA API Contract (v1)

The frontend calls this REST API through server functions; the base URL is
configured with the `SPORTZA_API_BASE` environment variable (e.g.
`https://api.sportza.example`). All endpoints are `GET`, return JSON, and use
UTF-8. All dates are `YYYY-MM-DD`. All numeric values are plain JSON numbers
(no strings for numbers).

If `SPORTZA_API_BASE` is unset or a request fails, the frontend shows
"API not connected" / error states. It never substitutes sample data.

## Endpoints

### `GET /v1/overview`

```json
{
  "dataset": { "athletes": 24, "sessions": 1840, "dateFrom": "2025-09-01", "dateTo": "2026-10-30" },
  "kpis": [
    {
      "id": "avg-readiness",
      "label": "Mean readiness",
      "value": 76.4,
      "unit": "score",
      "precision": 1,
      "delta": -2.1,
      "deltaDirection": "down",
      "context": "vs previous 7 days"
    }
  ],
  "trends": [
    {
      "id": "weekly-load",
      "title": "Weekly training load",
      "unit": "AU",
      "points": [{ "date": "2026-10-01", "value": 2380 }],
      "baseline": [{ "date": "2026-10-01", "value": 2200 }]
    }
  ],
  "insights": [{ "title": "Recent workload increased", "body": "…", "tone": "caution" }]
}
```

- `kpis[].delta` is the change vs the comparison the `context` text describes; omit when not meaningful. `deltaDirection` is the _desirable_ reading direction (`up` = rising value, not necessarily good).
- `trends[].baseline` (optional) is a reference series plotted as a light line.
- `insights[].tone`: `info` | `positive` | `caution`.

### `GET /v1/athletes`

```json
{
  "athletes": [
    {
      "id": "a-01",
      "name": "A. Mensah",
      "position": "Midfielder",
      "squad": "Senior",
      "status": "available",
      "ageYears": 22,
      "lastSessionDate": "2026-10-29"
    }
  ]
}
```

- `status`: `available` | `limited` | `unavailable`.

### `GET /v1/athletes/{id}`

```json
{
  "athlete": {
    "id": "a-01",
    "name": "A. Mensah",
    "position": "Midfielder",
    "status": "available",
    "ageYears": 22,
    "heightCm": 178,
    "weightKg": 71.5
  },
  "series": [
    {
      "id": "daily-load",
      "label": "Daily load",
      "unit": "AU",
      "domain": "workload",
      "points": [{ "date": "2026-10-01", "value": 420 }]
    }
  ],
  "recentSessions": [
    { "date": "2026-10-29", "type": "Conditioning", "durationMin": 75, "rpe": 6, "srpe": 450 }
  ]
}
```

- `series[].domain`: `wellness` | `workload` | `performance`. Grouped by domain in the UI.

### `GET /v1/readiness/{athleteId}`

```json
{
  "athleteId": "a-01",
  "date": "2026-10-30",
  "score": 68,
  "baselineScore": 78,
  "factors": [
    { "label": "Sleep quality", "direction": "negative", "detail": "3 nights below usual range" }
  ],
  "recommendation": {
    "headline": "Reduce intensity today",
    "body": "Readiness is lower than this athlete's recent baseline.",
    "basis": ["7-day load 18% above 28-day baseline", "Sleep quality below usual range"]
  },
  "disclaimer": "Readiness scores are training-guidance indicators, not medical assessments."
}
```

- `direction`: `positive` | `negative` | `neutral` (contribution to the current readiness picture).

### `GET /v1/workload`

```json
{
  "trends": [{ "id": "srpe-daily", "title": "Daily sRPE", "unit": "AU", "points": [] }],
  "acuteChronic": [{ "date": "2026-10-30", "acuteLoad": 2450, "chronicLoad": 2280, "ratio": 1.07 }],
  "sessionsByType": [{ "type": "Skills", "sessions": 42, "minutes": 3150 }],
  "definitions": [
    { "term": "sRPE", "explanation": "Session rating of perceived exertion × duration (AU)." }
  ]
}
```

### `GET /v1/injuries`

```json
{
  "records": [
    {
      "id": "i-120",
      "date": "2026-09-14",
      "athleteId": "a-07",
      "athleteName": "R. Iyer",
      "bodyLocation": "Hamstring",
      "severity": "moderate",
      "source": "clinical",
      "type": "Strain",
      "daysOut": 18
    }
  ]
}
```

- `severity`: `mild` | `moderate` | `severe`. `source`: `self_reported` | `clinical`.

### `GET /v1/forecast`

```json
{
  "metric": "Weekly load",
  "unit": "AU",
  "horizonDays": 14,
  "generatedAt": "2026-10-30",
  "points": [
    { "date": "2026-10-24", "actual": 2380, "predicted": 2410, "lower": 2210, "upper": 2610 }
  ],
  "metrics": [{ "name": "MAE", "value": 96.4, "unit": "AU" }],
  "baseline": {
    "name": "Season mean",
    "metrics": [{ "name": "MAE", "value": 132.1, "unit": "AU" }]
  },
  "notes": ["Predictions are estimates from historical workload patterns."]
}
```

- `actual` present for past dates, `predicted`/`lower`/`upper` for all dates.

### `GET /v1/team`

```json
{
  "positions": [{ "id": "mid", "label": "Midfielders", "athleteCount": 7 }],
  "metrics": [
    {
      "id": "weekly-load",
      "label": "Weekly load",
      "unit": "AU",
      "byPosition": [{ "positionId": "mid", "mean": 2450, "median": 2390, "n": 7 }]
    }
  ]
}
```

### `GET /v1/correlations`

```json
{
  "variables": [{ "id": "sleep", "label": "Sleep quality", "unit": "score" }],
  "pairs": [{ "aId": "sleep", "bId": "readiness", "r": 0.42, "n": 640 }]
}
```

- `r` is Pearson correlation in [-1, 1]. The UI shows a correlation ≠ causation reminder.

### `GET /v1/models`

```json
{
  "models": [
    {
      "id": "load-forecast-gbr",
      "name": "Load forecast — gradient boosting",
      "task": "forecast",
      "status": "production",
      "trainedAt": "2026-10-20",
      "validation": { "method": "Rolling-origin cross-validation", "folds": 5 },
      "metrics": [{ "name": "MAE", "value": 96.4, "unit": "AU", "baselineValue": 132.1 }],
      "notes": "Retrained after October data refresh."
    }
  ],
  "activeModelId": "load-forecast-gbr"
}
```

- `status`: `production` | `candidate` | `archived`.

## Error responses

Non-2xx status with a JSON body `{ "error": "message" }` is treated as an API
error and surfaced in the section's error state. The frontend retries on user
action, never automatically in a loop.
