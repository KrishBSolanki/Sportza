import type { z } from "zod";

import type { ApiResult } from "./types";

/**
 * Server-only helper that talks to the SPORTZA research API.
 * The base URL is read from SPORTZA_API_BASE inside the handler so it is
 * never bundled into client code.
 */
export function getApiBase(): string | null {
  const base = process.env["SPORTZA_API_BASE"];
  if (!base) return null;
  return base.replace(/\/+$/, "");
}

const TIMEOUT_MS = 15_000;

export async function apiGet<T>(
  path: string,
  schema: z.ZodType<T, z.ZodTypeDef, unknown>,
): Promise<ApiResult<T>> {
  const base = getApiBase();
  if (!base) {
    return {
      ok: false,
      reason: "not_configured",
      message: "SPORTZA_API_BASE is not set, so no data source is connected.",
    };
  }

  let response: Response;
  try {
    response = await fetch(`${base}${path}`, {
      headers: { Accept: "application/json" },
      signal: AbortSignal.timeout(TIMEOUT_MS),
    });
  } catch (error) {
    return {
      ok: false,
      reason: "unreachable",
      message: error instanceof Error ? error.message : "Request failed",
    };
  }

  if (!response.ok) {
    let detail = `API responded with status ${response.status}`;
    try {
      const body = (await response.json()) as { error?: unknown };
      if (typeof body?.error === "string" && body.error.length > 0) {
        detail = body.error;
      }
    } catch {
      // Non-JSON error body: keep the status-based detail.
    }
    return { ok: false, reason: "unreachable", message: detail };
  }

  let json: unknown;
  try {
    json = await response.json();
  } catch {
    return { ok: false, reason: "invalid", message: "API returned non-JSON data" };
  }

  const parsed = schema.safeParse(json);
  if (!parsed.success) {
    return {
      ok: false,
      reason: "invalid",
      message: "API response did not match the expected data shape",
    };
  }

  return { ok: true, data: parsed.data };
}

export async function apiPost<T>(
  path: string,
  schema: z.ZodType<T, z.ZodTypeDef, unknown>,
  body: Record<string, unknown> = {},
): Promise<ApiResult<T>> {
  const base = getApiBase();
  if (!base) {
    return {
      ok: false,
      reason: "not_configured",
      message: "SPORTZA_API_BASE is not set, so no data source is connected.",
    };
  }

  let response: Response;
  try {
    response = await fetch(`${base}${path}`, {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "application/json" },
      body: JSON.stringify(body),
      signal: AbortSignal.timeout(120_000), // models can be slow
    });
  } catch (error) {
    return {
      ok: false,
      reason: "unreachable",
      message: error instanceof Error ? error.message : "Request failed",
    };
  }

  if (!response.ok) {
    let detail = `API responded with status ${response.status}`;
    try {
      const raw = (await response.json()) as { detail?: unknown; error?: unknown };
      const msg = raw?.detail ?? raw?.error;
      if (typeof msg === "string" && msg.length > 0) {
        detail = msg;
      }
    } catch {
      // Non-JSON error body: keep the status-based detail.
    }
    return { ok: false, reason: "unreachable", message: detail };
  }

  let json: unknown;
  try {
    json = await response.json();
  } catch {
    return { ok: false, reason: "invalid", message: "API returned non-JSON data" };
  }

  const parsed = schema.safeParse(json);
  if (!parsed.success) {
    return {
      ok: false,
      reason: "invalid",
      message: "API response did not match the expected data shape",
    };
  }

  return { ok: true, data: parsed.data };
}
