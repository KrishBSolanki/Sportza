import { queryOptions } from "@tanstack/react-query";

import {
  fetchAthlete,
  fetchAthletes,
  fetchCorrelations,
  fetchForecast,
  fetchInjuries,
  fetchModelAthletes,
  fetchModels,
  fetchOverview,
  fetchReadiness,
  fetchTeam,
  fetchWorkload,
} from "./sportza.functions";

export const overviewQueryOptions = queryOptions({
  queryKey: ["sportza", "overview"],
  queryFn: () => fetchOverview(),
});

export const athletesQueryOptions = queryOptions({
  queryKey: ["sportza", "athletes"],
  queryFn: () => fetchAthletes(),
});

export const athleteDetailQueryOptions = (athleteId: string) =>
  queryOptions({
    queryKey: ["sportza", "athlete", athleteId],
    queryFn: () => fetchAthlete({ data: athleteId }),
  });

export const readinessQueryOptions = (athleteId: string) =>
  queryOptions({
    queryKey: ["sportza", "readiness", athleteId],
    queryFn: () => fetchReadiness({ data: athleteId }),
  });

export const workloadQueryOptions = queryOptions({
  queryKey: ["sportza", "workload"],
  queryFn: () => fetchWorkload(),
});

export const injuriesQueryOptions = queryOptions({
  queryKey: ["sportza", "injuries"],
  queryFn: () => fetchInjuries(),
});

export const forecastQueryOptions = queryOptions({
  queryKey: ["sportza", "forecast"],
  queryFn: () => fetchForecast(),
});

export const teamQueryOptions = queryOptions({
  queryKey: ["sportza", "team"],
  queryFn: () => fetchTeam(),
});

export const correlationsQueryOptions = queryOptions({
  queryKey: ["sportza", "correlations"],
  queryFn: () => fetchCorrelations(),
});

export const modelsQueryOptions = queryOptions({
  queryKey: ["sportza", "models"],
  queryFn: () => fetchModels(),
});

export const modelAthletesQueryOptions = queryOptions({
  queryKey: ["sportza", "model-athletes"],
  queryFn: () => fetchModelAthletes(),
});
