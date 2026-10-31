import { createFileRoute } from "@tanstack/react-router";
import { useSuspenseQuery } from "@tanstack/react-query";
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  ComposedChart,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
  ReferenceLine,
} from "recharts";

import { workloadQueryOptions } from "@/lib/api/queries";
import { DataBoundary } from "@/components/data-state";
import { PageHeader, SectionHeader } from "@/components/page-header";
import { ChartCard } from "@/components/chart-card";
import { fmtTickDate, fmtNumber } from "@/lib/format";
import {
  semanticColor,
  chartChrome,
  axisProps,
  gridProps,
  tooltipContentStyle,
  tooltipLabelStyle,
  tooltipItemStyle,
} from "@/lib/chart-theme";
import type { Workload } from "@/lib/api/types";

export const Route = createFileRoute("/workload")({
  head: () => ({
    meta: [
      { title: "Training Workload — SPORTZA" },
      {
        name: "description",
        content: "Session load tracking, acute-chronic ratios, and session distribution",
      },
    ],
  }),
  loader: ({ context }) => context.queryClient.ensureQueryData(workloadQueryOptions),
  component: WorkloadPage,
});

function WorkloadPage() {
  const { data: result } = useSuspenseQuery(workloadQueryOptions);

  return (
    <div className="page-shell space-y-6 py-6">
      <PageHeader
        title="Training Workload"
        context="Session load tracking, acute-chronic ratios, and session distribution"
      />
      <DataBoundary result={result}>{(data) => <WorkloadContent data={data} />}</DataBoundary>
    </div>
  );
}

function WorkloadContent({ data }: { data: Workload }) {
  return (
    <>
      {/* sRPE trends */}
      {data.trends.map((trend) => (
        <ChartCard key={trend.id} title={trend.title} note={trend.description}>
          <ResponsiveContainer width="100%" height={280}>
            <LineChart data={trend.points} margin={{ top: 8, right: 12, bottom: 4, left: 4 }}>
              <CartesianGrid {...gridProps} />
              <XAxis dataKey="date" {...axisProps} tickFormatter={fmtTickDate} />
              <YAxis
                {...axisProps}
                label={{
                  value: trend.unit,
                  angle: -90,
                  position: "insideLeft",
                  style: { fill: axisProps.tick.fill, fontSize: 11 },
                }}
              />
              <Tooltip
                contentStyle={tooltipContentStyle}
                labelStyle={tooltipLabelStyle}
                itemStyle={tooltipItemStyle}
                labelFormatter={fmtTickDate}
              />
              <Line
                type="monotone"
                dataKey="value"
                name={trend.title}
                stroke={semanticColor.headline}
                strokeWidth={2}
                dot={false}
                activeDot={{ r: 4 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </ChartCard>
      ))}

      {/* Acute vs Chronic workload ratio */}
      {data.acuteChronic.length > 0 && (
        <ChartCard
          title="Acute vs chronic workload ratio"
          note="Values between 0.8–1.3 are generally considered a moderate training zone"
        >
          <ResponsiveContainer width="100%" height={300}>
            <ComposedChart
              data={data.acuteChronic}
              margin={{ top: 8, right: 12, bottom: 4, left: 4 }}
            >
              <CartesianGrid {...gridProps} />
              <XAxis dataKey="date" {...axisProps} tickFormatter={fmtTickDate} />
              <YAxis
                yAxisId="load"
                {...axisProps}
                label={{
                  value: "Load (AU)",
                  angle: -90,
                  position: "insideLeft",
                  style: { fill: axisProps.tick.fill, fontSize: 11 },
                }}
              />
              <YAxis
                yAxisId="ratio"
                orientation="right"
                {...axisProps}
                domain={[0, 2]}
                label={{
                  value: "ACWR",
                  angle: 90,
                  position: "insideRight",
                  style: { fill: axisProps.tick.fill, fontSize: 11 },
                }}
              />
              <Tooltip
                contentStyle={tooltipContentStyle}
                labelStyle={tooltipLabelStyle}
                itemStyle={tooltipItemStyle}
                labelFormatter={fmtTickDate}
              />
              <Legend />
              <ReferenceLine
                yAxisId="ratio"
                y={0.8}
                stroke={chartChrome.referenceLine}
                strokeDasharray="4 4"
              />
              <ReferenceLine
                yAxisId="ratio"
                y={1.3}
                stroke={chartChrome.referenceLine}
                strokeDasharray="4 4"
              />
              <Line
                yAxisId="load"
                type="monotone"
                dataKey="acuteLoad"
                name="Acute load"
                stroke={semanticColor.headline}
                strokeWidth={2}
                dot={false}
              />
              <Line
                yAxisId="load"
                type="monotone"
                dataKey="chronicLoad"
                name="Chronic load"
                stroke={semanticColor.context}
                strokeWidth={2}
                dot={false}
              />
              <Line
                yAxisId="ratio"
                type="monotone"
                dataKey="ratio"
                name="ACWR"
                stroke={semanticColor.attention}
                strokeWidth={2}
                dot={false}
              />
            </ComposedChart>
          </ResponsiveContainer>

          <div className="mt-3 rounded border border-border/80 bg-secondary/50 p-2.5 text-[11px] leading-relaxed text-muted-foreground">
            <strong className="text-foreground">What this chart conveys to coaching staff:</strong> Compares 7-day Acute Load (fatigue, green) against 28-day Chronic Load (fitness, grey) on the left axis (AU = duration &times; sRPE). The amber curve tracks the ACWR ratio on the right axis. Ratios between the two dashed lines (0.8–1.3) signify the safe progressive conditioning sweet spot; exceeding 1.5 indicates an acute workload spike associated with higher injury vulnerability.
          </div>
        </ChartCard>
      )}

      {/* Session distribution */}
      {data.sessionsByType.length > 0 && (
        <ChartCard title="Sessions by type" note="Total sessions and time per training category">
          <ResponsiveContainer width="100%" height={Math.max(200, data.sessionsByType.length * 44)}>
            <BarChart
              data={data.sessionsByType}
              layout="vertical"
              margin={{ top: 4, right: 24, bottom: 4, left: 80 }}
            >
              <CartesianGrid {...gridProps} horizontal={false} vertical />
              <XAxis type="number" {...axisProps} />
              <YAxis type="category" dataKey="type" {...axisProps} width={76} />
              <Tooltip
                contentStyle={tooltipContentStyle}
                labelStyle={tooltipLabelStyle}
                itemStyle={tooltipItemStyle}
                formatter={(value: number, name: string) =>
                  name === "sessions"
                    ? [fmtNumber(value), "Sessions"]
                    : [fmtNumber(value) + " min", "Total time"]
                }
              />
              <Legend />
              <Bar
                dataKey="sessions"
                name="Sessions"
                fill={semanticColor.headline}
                radius={[0, 3, 3, 0]}
              />
            </BarChart>
          </ResponsiveContainer>

          <div className="mt-3 rounded border border-border/80 bg-secondary/50 p-2.5 text-[11px] leading-relaxed text-muted-foreground">
            <strong className="text-foreground">What this distribution conveys:</strong> Breaks down squad exposure across Team tactical sessions, Individual conditioning, and Official Competition fixtures to assess periodization balance.
          </div>
        </ChartCard>
      )}

      {/* Technical definitions */}
      {data.definitions.length > 0 && (
        <section className="space-y-2">
          <SectionHeader title="Glossary" />
          <div className="rounded-lg border border-border bg-card p-4">
            <dl className="grid gap-3 sm:grid-cols-2">
              {data.definitions.map((d) => (
                <div key={d.term}>
                  <dt className="text-sm font-medium text-foreground">{d.term}</dt>
                  <dd className="text-caption">{d.explanation}</dd>
                </div>
              ))}
            </dl>
          </div>
        </section>
      )}
    </>
  );
}
