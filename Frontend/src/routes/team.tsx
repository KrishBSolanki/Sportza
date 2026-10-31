import { createFileRoute } from "@tanstack/react-router";
import { useSuspenseQuery } from "@tanstack/react-query";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import { useMemo } from "react";

import { teamQueryOptions } from "@/lib/api/queries";
import { DataBoundary } from "@/components/data-state";
import { PageHeader, SectionHeader } from "@/components/page-header";
import { ChartCard } from "@/components/chart-card";
import { fmtNumber } from "@/lib/format";
import {
  semanticColor,
  chartPalette,
  axisProps,
  gridProps,
  tooltipContentStyle,
  tooltipLabelStyle,
  tooltipItemStyle,
} from "@/lib/chart-theme";
import type { Team } from "@/lib/api/types";

export const Route = createFileRoute("/team")({
  head: () => ({
    meta: [
      { title: "Team Analysis — SPORTZA" },
      { name: "description", content: "Position-grouped comparisons across tracked metrics" },
    ],
  }),
  loader: ({ context }) => context.queryClient.ensureQueryData(teamQueryOptions),
  component: TeamPage,
});

function TeamPage() {
  const { data: result } = useSuspenseQuery(teamQueryOptions);

  return (
    <div className="page-shell space-y-6 py-6">
      <PageHeader
        title="Team Analysis"
        context="Position-grouped comparisons across tracked metrics"
      />
      <DataBoundary result={result}>{(data) => <TeamContent data={data} />}</DataBoundary>
    </div>
  );
}

function TeamContent({ data }: { data: Team }) {
  const positionMap = useMemo(() => {
    const map = new Map<string, string>();
    for (const p of data.positions) map.set(p.id, p.label);
    return map;
  }, [data.positions]);

  return (
    <>
      {/* Position overview */}
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-5">
        {data.positions.map((pos) => (
          <div key={pos.id} className="rounded-lg border border-border bg-card p-3">
            <p className="text-sm font-medium text-foreground">{pos.label}</p>
            <p className="mt-0.5 text-xs text-muted-foreground tabular">
              {pos.athleteCount} athlete{pos.athleteCount !== 1 ? "s" : ""}
            </p>
          </div>
        ))}
      </div>

      {/* Metric comparisons */}
      {data.metrics.map((metric) => {
        const chartData = metric.byPosition.map((bp) => ({
          position: positionMap.get(bp.positionId) ?? bp.positionId,
          mean: bp.mean,
          median: bp.median,
          n: bp.n,
        }));

        return (
          <ChartCard key={metric.id} title={metric.label} note={`Unit: ${metric.unit}`}>
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={chartData} margin={{ top: 8, right: 12, bottom: 4, left: 4 }}>
                <CartesianGrid {...gridProps} />
                <XAxis dataKey="position" {...axisProps} />
                <YAxis
                  {...axisProps}
                  label={{
                    value: metric.unit,
                    angle: -90,
                    position: "insideLeft",
                    style: { fill: axisProps.tick.fill, fontSize: 11 },
                  }}
                />
                <Tooltip
                  contentStyle={tooltipContentStyle}
                  labelStyle={tooltipLabelStyle}
                  itemStyle={tooltipItemStyle}
                  formatter={(value: number, name: string) => [fmtNumber(value, 1), name]}
                  content={({ active, payload, label }) => {
                    if (!active || !payload || payload.length === 0) return null;
                    const row = payload[0]?.payload as {
                      mean: number;
                      median?: number;
                      n: number;
                    };
                    return (
                      <div style={tooltipContentStyle} className="space-y-0.5 px-3 py-2">
                        <p className="text-xs font-semibold">{label}</p>
                        <p className="text-xs">
                          Mean: <span className="tabular">{fmtNumber(row.mean, 1)}</span>
                        </p>
                        {row.median !== undefined && (
                          <p className="text-xs">
                            Median: <span className="tabular">{fmtNumber(row.median, 1)}</span>
                          </p>
                        )}
                        <p className="text-xs text-muted-foreground">n = {row.n}</p>
                      </div>
                    );
                  }}
                />
                <Bar
                  dataKey="mean"
                  name="Mean"
                  fill={semanticColor.headline}
                  radius={[3, 3, 0, 0]}
                />
                {chartData.some((d) => d.median !== undefined) && (
                  <Bar
                    dataKey="median"
                    name="Median"
                    fill={chartPalette.sage}
                    radius={[3, 3, 0, 0]}
                  />
                )}
              </BarChart>
            </ResponsiveContainer>

            <div className="mt-3 rounded border border-border/80 bg-secondary/50 p-2.5 text-[11px] leading-relaxed text-muted-foreground">
              <strong className="text-foreground">What positional comparisons convey:</strong> Evaluates tactical role demands across Central Defenders, Full-Backs, Midfielders, and Forwards on identical scales. Central Midfielders and Full-Backs typically exhibit higher cumulative running loads, whereas Central Defenders endure distinct acceleration profiles. Comparing against positional norms prevents misclassifying positional demands as athlete fatigue.
            </div>
          </ChartCard>
        );
      })}

      {/* Fair scale note */}
      <p className="text-caption">
        All position groups compared on the same scale for each metric. Sample sizes (n) vary by
        position.
      </p>
    </>
  );
}
