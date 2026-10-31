import { describe, expect, it } from "vitest";

import {
  AthleteDetailSchema,
  AthletesSchema,
  CorrelationsSchema,
  ForecastSchema,
  InjuriesSchema,
  ModelsSchema,
  OverviewSchema,
  ReadinessSchema,
  TeamSchema,
  WorkloadSchema,
} from "../lib/api/types";

const BASE_URL = process.env["SPORTZA_API_BASE"] ?? "http://127.0.0.1:8000";

describe("Live API Conformance with Zod Schemas", () => {
  it("validates GET /v1/overview", async () => {
    const res = await fetch(`${BASE_URL}/v1/overview`);
    expect(res.status).toBe(200);
    const json = await res.json();
    const parsed = OverviewSchema.safeParse(json);
    if (!parsed.success) {
      console.error("Overview validation errors:", parsed.error.format());
    }
    expect(parsed.success).toBe(true);
  });

  it("validates GET /v1/athletes", async () => {
    const res = await fetch(`${BASE_URL}/v1/athletes`);
    expect(res.status).toBe(200);
    const json = await res.json();
    const parsed = AthletesSchema.safeParse(json);
    if (!parsed.success) {
      console.error("Athletes validation errors:", parsed.error.format());
    }
    expect(parsed.success).toBe(true);
  });

  it("validates GET /v1/athletes/:id", async () => {
    const rosterRes = await fetch(`${BASE_URL}/v1/athletes`);
    const roster = await rosterRes.json();
    const firstId = roster.athletes[0].id;

    const res = await fetch(`${BASE_URL}/v1/athletes/${encodeURIComponent(firstId)}`);
    expect(res.status).toBe(200);
    const json = await res.json();
    const parsed = AthleteDetailSchema.safeParse(json);
    if (!parsed.success) {
      console.error("AthleteDetail validation errors:", parsed.error.format());
    }
    expect(parsed.success).toBe(true);
  });

  it("validates GET /v1/readiness/:id", async () => {
    const rosterRes = await fetch(`${BASE_URL}/v1/athletes`);
    const roster = await rosterRes.json();
    const firstId = roster.athletes[0].id;

    const res = await fetch(`${BASE_URL}/v1/readiness/${encodeURIComponent(firstId)}`);
    expect(res.status).toBe(200);
    const json = await res.json();
    const parsed = ReadinessSchema.safeParse(json);
    if (!parsed.success) {
      console.error("Readiness validation errors:", parsed.error.format());
    }
    expect(parsed.success).toBe(true);
  });

  it("validates GET /v1/workload", async () => {
    const res = await fetch(`${BASE_URL}/v1/workload`);
    expect(res.status).toBe(200);
    const json = await res.json();
    const parsed = WorkloadSchema.safeParse(json);
    if (!parsed.success) {
      console.error("Workload validation errors:", parsed.error.format());
    }
    expect(parsed.success).toBe(true);
  });

  it("validates GET /v1/injuries", async () => {
    const res = await fetch(`${BASE_URL}/v1/injuries`);
    expect(res.status).toBe(200);
    const json = await res.json();
    const parsed = InjuriesSchema.safeParse(json);
    if (!parsed.success) {
      console.error("Injuries validation errors:", parsed.error.format());
    }
    expect(parsed.success).toBe(true);
  });

  it("validates GET /v1/forecast", async () => {
    const res = await fetch(`${BASE_URL}/v1/forecast`);
    expect(res.status).toBe(200);
    const json = await res.json();
    const parsed = ForecastSchema.safeParse(json);
    if (!parsed.success) {
      console.error("Forecast validation errors:", parsed.error.format());
    }
    expect(parsed.success).toBe(true);
  });

  it("validates GET /v1/team", async () => {
    const res = await fetch(`${BASE_URL}/v1/team`);
    expect(res.status).toBe(200);
    const json = await res.json();
    const parsed = TeamSchema.safeParse(json);
    if (!parsed.success) {
      console.error("Team validation errors:", parsed.error.format());
    }
    expect(parsed.success).toBe(true);
  });

  it("validates GET /v1/correlations", async () => {
    const res = await fetch(`${BASE_URL}/v1/correlations`);
    expect(res.status).toBe(200);
    const json = await res.json();
    const parsed = CorrelationsSchema.safeParse(json);
    if (!parsed.success) {
      console.error("Correlations validation errors:", parsed.error.format());
    }
    expect(parsed.success).toBe(true);
  });

  it("validates GET /v1/models", async () => {
    const res = await fetch(`${BASE_URL}/v1/models`);
    expect(res.status).toBe(200);
    const json = await res.json();
    const parsed = ModelsSchema.safeParse(json);
    if (!parsed.success) {
      console.error("Models validation errors:", parsed.error.format());
    }
    expect(parsed.success).toBe(true);
  });
});
