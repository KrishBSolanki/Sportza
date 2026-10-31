import { z } from "zod";

/**
 * Typed shapes for the SPORTZA research API (docs/api-contract.md).
 * Schemas are deliberately tolerant: optional fields stay optional so a
 * backend that omits a non-essential field still validates.
 */

export type ApiResult<T> =
  | { ok: true; data: T }
  | {
      ok: false;
      reason: "not_configured" | "unreachable" | "invalid";
      message?: string;
    };

const isoDate = z.string().min(8);

export const KpiSchema = z.object({
  id: z.string(),
  label: z.string(),
  value: z.number(),
  unit: z.string().optional(),
  precision: z.number().int().min(0).max(4).optional(),
  delta: z.number().optional(),
  deltaDirection: z.enum(["up", "down", "flat"]).optional(),
  context: z.string().optional(),
});

export const TrendPointSchema = z.object({ date: isoDate, value: z.number() });

export const TrendSchema = z.object({
  id: z.string(),
  title: z.string(),
  unit: z.string(),
  description: z.string().optional(),
  points: z.array(TrendPointSchema),
  baseline: z.array(TrendPointSchema).optional(),
});

export const InsightSchema = z.object({
  title: z.string(),
  body: z.string(),
  tone: z.enum(["info", "positive", "caution"]).default("info"),
});

export const OverviewSchema = z.object({
  dataset: z.object({
    athletes: z.number(),
    sessions: z.number(),
    dateFrom: isoDate,
    dateTo: isoDate,
  }),
  kpis: z.array(KpiSchema),
  trends: z.array(TrendSchema).max(4),
  insights: z.array(InsightSchema),
});

export const AthleteSchema = z.object({
  id: z.string(),
  name: z.string(),
  position: z.string(),
  squad: z.string().optional(),
  status: z.enum(["available", "limited", "unavailable"]),
  ageYears: z.number().optional(),
  heightCm: z.number().optional(),
  weightKg: z.number().optional(),
  lastSessionDate: isoDate.optional(),
});

export const AthletesSchema = z.object({ athletes: z.array(AthleteSchema) });

export const SeriesSchema = z.object({
  id: z.string(),
  label: z.string(),
  unit: z.string(),
  domain: z.enum(["wellness", "workload", "performance"]),
  points: z.array(TrendPointSchema),
});

export const SessionSchema = z.object({
  date: isoDate,
  type: z.string(),
  durationMin: z.number(),
  rpe: z.number().optional(),
  srpe: z.number().optional(),
});

export const AthleteDetailSchema = z.object({
  athlete: AthleteSchema,
  series: z.array(SeriesSchema),
  recentSessions: z.array(SessionSchema),
});

export const ReadinessFactorSchema = z.object({
  label: z.string(),
  direction: z.enum(["positive", "negative", "neutral"]),
  detail: z.string().optional(),
});

export const ReadinessSchema = z.object({
  athleteId: z.string(),
  date: isoDate,
  score: z.number(),
  baselineScore: z.number(),
  factors: z.array(ReadinessFactorSchema),
  recommendation: z
    .object({
      headline: z.string(),
      body: z.string(),
      basis: z.array(z.string()),
    })
    .optional(),
  disclaimer: z.string().optional(),
});

export const WorkloadSchema = z.object({
  trends: z.array(TrendSchema),
  acuteChronic: z.array(
    z.object({
      date: isoDate,
      acuteLoad: z.number(),
      chronicLoad: z.number(),
      ratio: z.number(),
    }),
  ),
  sessionsByType: z.array(
    z.object({ type: z.string(), sessions: z.number(), minutes: z.number() }),
  ),
  definitions: z.array(z.object({ term: z.string(), explanation: z.string() })),
});

export const InjuriesSchema = z.object({
  records: z.array(
    z.object({
      id: z.string(),
      date: isoDate,
      athleteId: z.string(),
      athleteName: z.string().optional(),
      bodyLocation: z.string(),
      severity: z.enum(["mild", "moderate", "severe"]),
      source: z.enum(["self_reported", "clinical"]),
      type: z.string(),
      daysOut: z.number().optional(),
    }),
  ),
});

export const ForecastSchema = z.object({
  metric: z.string(),
  unit: z.string(),
  horizonDays: z.number(),
  generatedAt: isoDate.optional(),
  points: z.array(
    z.object({
      date: isoDate,
      actual: z.number().optional(),
      predicted: z.number().optional(),
      lower: z.number().optional(),
      upper: z.number().optional(),
    }),
  ),
  metrics: z.array(z.object({ name: z.string(), value: z.number(), unit: z.string().optional() })),
  baseline: z
    .object({
      name: z.string(),
      metrics: z.array(
        z.object({ name: z.string(), value: z.number(), unit: z.string().optional() }),
      ),
    })
    .optional(),
  notes: z.array(z.string()).default([]),
});

export const TeamSchema = z.object({
  positions: z.array(z.object({ id: z.string(), label: z.string(), athleteCount: z.number() })),
  metrics: z.array(
    z.object({
      id: z.string(),
      label: z.string(),
      unit: z.string(),
      byPosition: z.array(
        z.object({
          positionId: z.string(),
          mean: z.number(),
          median: z.number().optional(),
          n: z.number(),
        }),
      ),
    }),
  ),
});

export const CorrelationsSchema = z.object({
  variables: z.array(z.object({ id: z.string(), label: z.string(), unit: z.string().optional() })),
  pairs: z.array(
    z.object({
      aId: z.string(),
      bId: z.string(),
      r: z.number().min(-1).max(1),
      n: z.number(),
    }),
  ),
});

export const ModelsSchema = z.object({
  models: z.array(
    z.object({
      id: z.string(),
      name: z.string(),
      task: z.string(),
      status: z.enum(["production", "candidate", "archived"]),
      trainedAt: isoDate.optional(),
      validation: z.object({
        method: z.string(),
        folds: z.number().optional(),
        window: z.string().optional(),
      }),
      metrics: z.array(
        z.object({
          name: z.string(),
          value: z.number(),
          unit: z.string().optional(),
          baselineValue: z.number().optional(),
        }),
      ),
      notes: z.string().optional(),
    }),
  ),
  activeModelId: z.string().optional(),
});

export type Kpi = z.infer<typeof KpiSchema>;
export type Trend = z.infer<typeof TrendSchema>;
export type Insight = z.infer<typeof InsightSchema>;
export type Overview = z.infer<typeof OverviewSchema>;
export type Athlete = z.infer<typeof AthleteSchema>;
export type Athletes = z.infer<typeof AthletesSchema>;
export type Series = z.infer<typeof SeriesSchema>;
export type AthleteDetail = z.infer<typeof AthleteDetailSchema>;
export type Readiness = z.infer<typeof ReadinessSchema>;
export type Workload = z.infer<typeof WorkloadSchema>;
export type Injuries = z.infer<typeof InjuriesSchema>;
export type Forecast = z.infer<typeof ForecastSchema>;
export type Team = z.infer<typeof TeamSchema>;
export type Correlations = z.infer<typeof CorrelationsSchema>;
export type Models = z.infer<typeof ModelsSchema>;
export type ModelEntry = Models["models"][number];

// ── Model Lab interactive run schemas ────────────────────────────────────

export const ReadinessRunResultSchema = z.object({
  task: z.string(),
  modelType: z.string(),
  splitDate: z.string(),
  trainSamples: z.number(),
  testSamples: z.number(),
  modelMetrics: z.object({
    mae: z.number(),
    rmse: z.number(),
    r2: z.number(),
    maeImprovementPct: z.number(),
  }),
  baselineLocf: z.object({ mae: z.number(), rmse: z.number() }),
  baselineRoll7: z.object({ mae: z.number(), rmse: z.number() }),
  scatter: z.array(z.object({ actual: z.number(), predicted: z.number() })),
  importances: z.array(z.object({ feature: z.string(), importance: z.number() })),
});

export const PerformanceRunResultSchema = z.object({
  task: z.string(),
  targetRating: z.string(),
  trained: z.boolean(),
  reason: z.string().optional(),
  availableSamples: z.number().optional(),
  trainSamples: z.number().optional(),
  testSamples: z.number().optional(),
  modelMae: z.number().optional(),
  modelRmse: z.number().optional(),
  baselineMeanMae: z.number().optional(),
  baselineMeanRmse: z.number().optional(),
  maeImprovement: z.number().optional(),
  importances: z.array(z.object({ feature: z.string(), importance: z.number() })).optional(),
});

export const InjuryRunResultSchema = z.object({
  task: z.string(),
  gatePassed: z.boolean(),
  gateReason: z.string(),
  totalEvents: z.number(),
  uniquePlayers: z.number(),
  descriptive: z.object({
    totalReports: z.number(),
    topLocation: z.string().nullable().optional(),
    locations: z.record(z.string(), z.number()).optional(),
    severityCounts: z.record(z.string(), z.number()).optional(),
  }),
});

export const PlayerReadinessRunResultSchema = z.object({
  athleteId: z.string(),
  window: z.string(),
  trained: z.boolean(),
  reason: z.string().optional(),
  splitDate: z.string().optional(),
  trainSamples: z.number().optional(),
  testSamples: z.number().optional(),
  windowSamples: z.number().optional(),
  matchDatesCount: z.number().optional(),
  modelMae: z.number().optional(),
  modelRmse: z.number().optional(),
  baselineMae: z.number().optional(),
  maeImprovementPct: z.number().optional(),
  timeline: z.array(z.object({
    date: z.string(),
    actual: z.number(),
    predicted: z.number(),
  })).optional(),
  importances: z.array(z.object({ feature: z.string(), importance: z.number() })).optional(),
});

export const ModelAthletesSchema = z.object({
  athletes: z.array(z.object({
    id: z.string(),
    name: z.string(),
    position: z.string(),
    squad: z.string().optional(),
  })),
});

export type ReadinessRunResult = z.infer<typeof ReadinessRunResultSchema>;
export type PerformanceRunResult = z.infer<typeof PerformanceRunResultSchema>;
export type InjuryRunResult = z.infer<typeof InjuryRunResultSchema>;
export type PlayerReadinessRunResult = z.infer<typeof PlayerReadinessRunResultSchema>;
export type ModelAthletes = z.infer<typeof ModelAthletesSchema>;
