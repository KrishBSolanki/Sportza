import { QueryClient } from "@tanstack/react-query";
import { createRouter, rootRouteId } from "@tanstack/react-router";
import { describe, expect, it } from "vitest";

import { routeTree } from "@/routeTree.gen";

describe("App routing", () => {
  function makeRouter() {
    return createRouter({
      routeTree,
      context: { queryClient: new QueryClient() },
    });
  }

  const routes = [
    "/",
    "/athletes",
    "/readiness",
    "/workload",
    "/injuries",
    "/forecast",
    "/team",
    "/correlations",
    "/models",
  ];

  for (const path of routes) {
    it(`matches a page for ${path} instead of falling back to not found`, () => {
      const router = makeRouter();
      const matches = router.matchRoutes(path);
      expect(matches.at(-1)?.routeId).not.toBe(rootRouteId);
    });
  }

  it("matches a dynamic athlete detail route", () => {
    const router = makeRouter();
    const matches = router.matchRoutes("/athletes/a-01");
    expect(matches.at(-1)?.routeId).not.toBe(rootRouteId);
  });
});

describe("Light theme tokens", () => {
  it("defines the SPORTZA palette CSS variables in :root", async () => {
    const fs = await import("node:fs");
    const path = await import("node:path");
    const css = fs.readFileSync(path.resolve(__dirname, "../styles.css"), "utf-8");

    // Core palette variables must exist
    expect(css).toContain("--background:");
    expect(css).toContain("--foreground:");
    expect(css).toContain("--primary:");
    expect(css).toContain("--sage:");
    expect(css).toContain("--amber:");
    expect(css).toContain("--brick:");
    expect(css).toContain("--info:");

    // Must use oklch (the plan's requirement)
    expect(css).toContain("oklch(");

    // Must NOT reference dark mode
    expect(css).not.toContain(".dark");
    expect(css).not.toContain("prefers-color-scheme: dark");
  });
});
