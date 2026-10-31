import { createFileRoute } from "@tanstack/react-router";
import { useSuspenseQuery } from "@tanstack/react-query";
import { useMemo } from "react";
import {
  ComposedChart,
  Line,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";

import { forecastQueryOptions } from "@/lib/api/queries";
import { DataBoundary } from "@/components/data-state";
import { PageHeader, SectionHeader } from "@/components/page-header";
import { ChartCard } from "@/components/chart-card";
import { fmtTickDate, fmtNumber } from "@/lib/format";
import {
  semanticColor,
  axisProps,
  gridProps,
  tooltipContentStyle,
  tooltipLabelStyle,
  tooltipItemStyle,
} from "@/lib/chart-theme";
import type { Forecast } from "@/lib/api/types";

export const Route = createFileRoute("/forecast")({
  head: () => ({
    meta: [
      { title: "Performance Forecast — SPORTZA" },
      { name: "description", content: "Actual vs predicted performance with confidence intervals" },
    ],
  }),
  loader: ({ context }) => context.queryClient.ensureQueryData(forecastQueryOptions),
  component: ForecastPage,
});

function ForecastPage() {
  const { data: result } = useSuspenseQuery(forecastQueryOptions);

  return (
    <div className="page-shell space-y-6 py-6">
      <DataBoundary result={result}>{(data) => <ForecastContent data={data} />}</DataBoundary>
    </div>
  );
}

function ForecastContent({ data }: { data: Forecast }) {
  const contextLine = `${data.metric} forecast over a ${data.horizonDays}-day horizon`;

  // Transform data for the confidence band (Recharts range area uses [low, high] tuple)
  const chartData = useMemo(
    () =>
      data.points.map((pt) => ({
        ...pt,
        band: pt.lower !== undefined && pt.upper !== undefined ? [pt.lower, pt.upper] : undefined,
      })),
    [data.points],
  );

  return (
    <>
      <PageHeader title="Performance Forecast" context={contextLine} />

      {/* Error metrics */}
      {data.metrics.length > 0 && (
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4">
          {data.metrics.map((m) => {
            const baselineMetric = data.baseline?.metrics.find((bm) => bm.name === m.name);
            return (
              <div key={m.name} className="rounded-lg border border-border bg-card p-3">
                <p className="text-xs font-medium text-muted-foreground">{m.name}</p>
                <p className="mt-1 text-lg font-semibold tabular text-foreground">
                  {fmtNumber(m.value, 1)}
                  {m.unit ? (
                    <span className="ml-1 text-xs font-normal text-muted-foreground">{m.unit}</span>
                  ) : null}
                </p>
                {baselineMetric && (
                  <p className="mt-0.5 text-xs text-muted-foreground">
                    Baseline ({data.baseline?.name}): {fmtNumber(baselineMetric.value, 1)}
                    {baselineMetric.unit ? ` ${baselineMetric.unit}` : ""}
                  </p>
                )}
              </div>
            );
          })}
        </div>
      )}

      {/* Forecast chart */}
      <ChartCard
        title="Actual vs predicted"
        note="Shaded area shows prediction confidence interval"
      >
        <ResponsiveContainer width="100%" height={340}>
          <ComposedChart data={chartData} margin={{ top: 8, right: 12, bottom: 4, left: 4 }}>
            <CartesianGrid {...gridProps} />
            <XAxis dataKey="date" {...axisProps} tickFormatter={fmtTickDate} />
            <YAxis
              {...axisProps}
              label={{
                value: data.unit,
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
              formatter={(value: unknown, name: string) => {
                if (name === "Confidence band" && Array.isArray(value)) {
                  return [
                    `${fmtNumber(value[0] as number)} – ${fmtNumber(value[1] as number)}`,
                    name,
                  ];
                }
                return [typeof value === "number" ? fmtNumber(value) : String(value), name];
              }}
            />
            <Legend />
            <Area
              type="monotone"
              dataKey="band"
              name="Confidence band"
              stroke="none"
              fill={semanticColor.context}
              fillOpacity={0.25}
              activeDot={false}
              legendType="rect"
            />
            <Line
              type="monotone"
              dataKey="actual"
              name="Actual"
              stroke={semanticColor.headline}
              strokeWidth={2}
              dot={{ r: 3, fill: semanticColor.headline }}
              activeDot={{ r: 4 }}
              connectNulls={false}
            />
            <Line
              type="monotone"
              dataKey="predicted"
              name="Predicted"
              stroke={semanticColor.attention}
              strokeWidth={2}
              strokeDasharray="6 3"
              dot={false}
            />
          </ComposedChart>
        </ResponsiveContainer>

        <div className="mt-3 rounded border border-border/80 bg-secondary/50 p-2.5 text-[11px] leading-relaxed text-muted-foreground">
          <strong className="text-foreground">What this forecast conveys:</strong> Evaluates predictions over a chronological holdout period. The solid green line represents ground-truth actual daily training load (AU = duration &times; sRPE), the dashed amber line indicates the model's forecast, and the shaded grey envelope reflects the 95% confidence interval.
        </div>
      </ChartCard>

      {/* Notes */}
      {data.notes.length > 0 && (
        <section className="space-y-2">
          <SectionHeader title="Notes" />
          <div className="rounded-lg border border-dashed border-border bg-card px-4 py-3">
            {data.notes.map((note, i) => (
              <p key={i} className="text-caption">
                {note}
              </p>
            ))}
          </div>
        </section>
      )}
    </>
  );
}
