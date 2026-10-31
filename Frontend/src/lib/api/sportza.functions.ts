import { createServerFn } from "@tanstack/react-start";
import { z } from "zod";

import { apiGet, apiPost } from "./client.server";
import {
  AthleteDetailSchema,
  AthletesSchema,
  CorrelationsSchema,
  ForecastSchema,
  InjuriesSchema,
  ModelAthletesSchema,
  ModelsSchema,
  OverviewSchema,
  PerformanceRunResultSchema,
  PlayerReadinessRunResultSchema,
  ReadinessRunResultSchema,
  ReadinessSchema,
  InjuryRunResultSchema,
  TeamSchema,
  WorkloadSchema,
} from "./types";

/**
 * Read-only proxies to the SPORTZA research API. Each returns an ApiResult
 * envelope instead of throwing, so sections can render "API not connected"
 * / error states without route-level error boundaries.
 */
export const fetchOverview = createServerFn({ method: "GET" }).handler(() =>
  apiGet("/v1/overview", OverviewSchema),
);

export const fetchAthletes = createServerFn({ method: "GET" }).handler(() =>
  apiGet("/v1/athletes", AthletesSchema),
);

export const fetchAthlete = createServerFn({ method: "GET" })
  .inputValidator((id: string) => z.string().min(1).parse(id))
  .handler(({ data }) => apiGet(`/v1/athletes/${encodeURIComponent(data)}`, AthleteDetailSchema));

export const fetchReadiness = createServerFn({ method: "GET" })
  .inputValidator((athleteId: string) => z.string().min(1).parse(athleteId))
  .handler(({ data }) => apiGet(`/v1/readiness/${encodeURIComponent(data)}`, ReadinessSchema));

export const fetchWorkload = createServerFn({ method: "GET" }).handler(() =>
  apiGet("/v1/workload", WorkloadSchema),
);

export const fetchInjuries = createServerFn({ method: "GET" }).handler(() =>
  apiGet("/v1/injuries", InjuriesSchema),
);

export const fetchForecast = createServerFn({ method: "GET" }).handler(() =>
  apiGet("/v1/forecast", ForecastSchema),
);

export const fetchTeam = createServerFn({ method: "GET" }).handler(() =>
  apiGet("/v1/team", TeamSchema),
);

export const fetchCorrelations = createServerFn({ method: "GET" }).handler(() =>
  apiGet("/v1/correlations", CorrelationsSchema),
);

export const fetchModels = createServerFn({ method: "GET" }).handler(() =>
  apiGet("/v1/models", ModelsSchema),
);

export const fetchModelAthletes = createServerFn({ method: "GET" }).handler(() =>
  apiGet("/v1/models/athletes", ModelAthletesSchema),
);

export const runReadinessModel = createServerFn({ method: "POST" })
  .inputValidator((params: { split_date: string }) =>
    z.object({ split_date: z.string() }).parse(params),
  )
  .handler(({ data }) =>
    apiPost("/v1/models/run-readiness", ReadinessRunResultSchema, data),
  );

export const runPerformanceModel = createServerFn({ method: "POST" })
  .inputValidator((params: { target_rating: string }) =>
    z.object({ target_rating: z.string() }).parse(params),
  )
  .handler(({ data }) =>
    apiPost("/v1/models/run-performance", PerformanceRunResultSchema, data),
  );

export const runInjuryModel = createServerFn({ method: "POST" }).handler(() =>
  apiPost("/v1/models/run-injury", InjuryRunResultSchema, {}),
);

export const runReadinessPlayerModel = createServerFn({ method: "POST" })
  .inputValidator(
    (params: { athlete_id: string; split_date: string; window: string }) =>
      z
        .object({
          athlete_id: z.string(),
          split_date: z.string(),
          window: z.string(),
        })
        .parse(params),
  )
  .handler(({ data }) =>
    apiPost(
      "/v1/models/run-readiness-player",
      PlayerReadinessRunResultSchema,
      data,
    ),
  );
