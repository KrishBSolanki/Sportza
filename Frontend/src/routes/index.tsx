import { createFileRoute } from "@tanstack/react-router";
import { useSuspenseQuery } from "@tanstack/react-query";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";

import { overviewQueryOptions } from "@/lib/api/queries";
import { DataBoundary } from "@/components/data-state";
import { PageHeader, SectionHeader } from "@/components/page-header";
import { KpiRow } from "@/components/kpi";
import { ChartCard } from "@/components/chart-card";
import { InsightList } from "@/components/insight-list";
import { fmtTickDate, fmtNumber } from "@/lib/format";
import {
  semanticColor,
  axisProps,
  gridProps,
  tooltipContentStyle,
  tooltipLabelStyle,
  tooltipItemStyle,
} from "@/lib/chart-theme";
import type { Overview } from "@/lib/api/types";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "Overview — SPORTZA" },
      { name: "description", content: "Dataset summary, key metrics, and recent trends" },
    ],
  }),
  loader: ({ context }) => context.queryClient.ensureQueryData(overviewQueryOptions),
  component: OverviewPage,
});

function OverviewPage() {
  const { data: result } = useSuspenseQuery(overviewQueryOptions);

  return (
    <div className="page-shell space-y-6 py-6">
      <DataBoundary result={result}>{(data) => <OverviewContent data={data} />}</DataBoundary>
    </div>
  );
}

function OverviewContent({ data }: { data: Overview }) {
  const ctx = data.dataset;
  const contextLine = `${fmtNumber(ctx.athletes)} athletes · ${fmtNumber(ctx.sessions)} sessions · ${ctx.dateFrom} – ${ctx.dateTo}`;

  return (
    <>
      <PageHeader title="Overview" context={contextLine} />

      <KpiRow kpis={data.kpis} />

      {data.trends.length > 0 && (
        <section className="space-y-4">
          <SectionHeader title="Recent trends" />
          <div className="grid gap-4 lg:grid-cols-2">
            {data.trends.slice(0, 2).map((trend) => (
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
                    <Legend />
                    <Line
                      type="monotone"
                      dataKey="value"
                      name={trend.title}
                      stroke={semanticColor.headline}
                      strokeWidth={2}
                      dot={false}
                      activeDot={{ r: 4 }}
                    />
                    {trend.baseline && trend.baseline.length > 0 && (
                      <Line
                        type="monotone"
                        data={trend.baseline}
                        dataKey="value"
                        name="Baseline"
                        stroke={semanticColor.context}
                        strokeWidth={1.5}
                        strokeDasharray="4 4"
                        dot={false}
                      />
                    )}
                  </LineChart>
                </ResponsiveContainer>

                <div className="mt-3 rounded border border-border/80 bg-secondary/50 p-2.5 text-[11px] leading-relaxed text-muted-foreground">
                  <strong className="text-foreground">What this conveys:</strong> {trend.id === "weekly-load" ? "Tracks squad-wide average weekly training load in Arbitrary Units (AU = session duration × sRPE rating 1–10) relative to the season baseline. Sudden spikes highlight acute match fixture congestion." : "Tracks average squad readiness (0–100 composite scale) relative to the season mean. Dips below baseline indicate systemic fatigue requiring targeted recovery days."}
                </div>
              </ChartCard>
            ))}
          </div>
        </section>
      )}

      {data.insights.length > 0 && (
        <section className="space-y-3">
          <SectionHeader title="Insights" />
          <InsightList insights={data.insights} />
        </section>
      )}
    </>
  );
}
