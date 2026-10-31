# SPORTZA — Build & Theme Plan

## Goal

Build the full SPORTZA sports-science frontend in this (currently blank) TanStack Start project: nine sections, one restrained premium light-only theme, all data flowing through a typed client for your Python API — which is not deployed yet, so the contract is designed here and the base URL is switchable.

## Approach

### 1. API layer (contract-first)

- Design a documented REST contract (written to `docs/api-contract.md`) with JSON shapes for every section; your backend implements to it.
- All API calls go through TanStack server functions (`src/lib/*.functions.ts`) that read the base URL from `process.env.SPORTZA_API_BASE` — no CORS issues now or after publish, no keys needed (open API).
- Route loaders use TanStack Query (`ensureQueryData` / `useSuspenseQuery`); every section has proper loading, empty and error states in the same visual system. A persistent "API not connected" state shows when the base URL is unset or unreachable — no fabricated data, no fake metrics anywhere.
- Typed response schemas with zod in `src/lib/api/types.ts` shared by client and server.

Endpoints (drafted in the contract doc):

- `GET /v1/overview` — dataset summary, KPIs, recent trends, insight strings
- `GET /v1/athletes`, `GET /v1/athletes/:id` — roster, profile, longitudinal wellness/workload series
- `GET /v1/readiness/:athleteId` — readiness score, recent changes, contributing factors, recovery recommendation
- `GET /v1/workload` — sRPE trends, acute/chronic load, session distribution
- `GET /v1/injuries` — records with body location, severity, self-reported vs clinical flag
- `GET /v1/forecast` — actual vs predicted series, horizon, error metrics
- `GET /v1/team` — position-grouped comparison series
- `GET /v1/correlations` — variable pair matrix
- `GET /v1/models` — model list, validation method, metrics, baseline comparison

### 2. Theme system (light only, no theme switcher)

- All tokens in `src/styles.css` using your palette: page bg `#F6F7F4`, white surfaces, `#EEF1ED` secondary, charcoal `#202923` text, slate `#65716A` secondary text, grey-green borders `#DCE3DC`, forest green `#27634B` primary, sage `#8DA996`, amber `#C58A3A`, brick `#B95750`, blue-grey `#58778A` (converted to oklch for the token file).
- Inter loaded via `<link>` in `src/routes/__root.tsx`; tabular numerals for all measurements/KPIs.
- Restyle shadcn primitives (button, input, select, badge, table, tabs, tooltip, etc.) via variants/tokens — flat surfaces, subtle borders, modest radii, minimal shadows. Shared primitives: page header, section header, KPI row, chart card, empty/loading/error states.

### 3. App shell & routes

- Slim text-led left sidebar with clear active state (no emojis; small Lucide icons), top area with page title + context, centered content with max-width; responsive to mobile (sidebar collapses to a drawer).
- Routes created in one batch: `/` (Overview), `/athletes`, `/athletes/$athleteId`, `/readiness`, `/workload`, `/injuries`, `/forecast`, `/team`, `/correlations`, `/models`. Each with its own head() metadata.

### 4. Sections (all nine, per your brief)

Each section: descriptive chart titles + one-line "what to notice", consistent metric colors, plain-language explanations of technical terms, non-medical disclaimers kept but visually quiet.

- **Overview** — restrained KPI row, 1–2 key trends, concise insight area.
- **Athletes** — selection list, profile context, grouped longitudinal trends (not a chart per variable).
- **Readiness** — current context, recent change, contributing factors behind any recommendation.
- **Workload** — sRPE / ACWR trends with units, session distribution.
- **Injury Research** — severity encoding, body-location summary, timeline; self-reported vs clinical distinguished.
- **Forecast** — actual vs predicted with reference line, error context, no exaggerated badges.
- **Team** — position comparisons on fair scales.
- **Correlation Lab** — diverging heatmap centered at zero + correlation ≠ causation reminder.
- **Models** — compact model selection, validation method, baseline comparison, diagnostics.

### 5. Charts

Recharts (already installed) styled through a shared chart theme: white/transparent plot areas, very light gridlines, dark axis labels with units, the five-color metric palette applied consistently, readable legends and tooltips, proper heights. Heatmap via a custom grid of colored cells (no extra library).

## Constraints honored

No backend/ML changes (yours), no mock data standing in for API data, no dark mode or theme selector, no new UI libraries, no marketing copy or invented metrics; accessibility: keyboard focus, contrast, readable sizes, labeled charts.

## Checks before done

Lint + typecheck + production build via project scripts; Playwright pass through all routes (desktop 1280px and mobile 390px) checking layout, overflow, focus states, empty/API-not-connected states, responsive sidebar; `src/test/` updated with a test asserting the light-theme tokens and route wiring.
