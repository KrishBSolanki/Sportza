import { createFileRoute } from "@tanstack/react-router";
import { useSuspenseQuery } from "@tanstack/react-query";
import { useMemo } from "react";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

import { injuriesQueryOptions } from "@/lib/api/queries";
import { DataBoundary, EmptyState } from "@/components/data-state";
import { PageHeader, SectionHeader } from "@/components/page-header";
import { ChartCard } from "@/components/chart-card";
import { SeverityBadge, SourceBadge } from "@/components/status-badge";
import { fmtDate, fmtNumber } from "@/lib/format";
import {
  semanticColor,
  severityColor,
  axisProps,
  gridProps,
  tooltipContentStyle,
  tooltipLabelStyle,
  tooltipItemStyle,
} from "@/lib/chart-theme";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import type { Injuries } from "@/lib/api/types";

export const Route = createFileRoute("/injuries")({
  head: () => ({
    meta: [
      { title: "Injury Research — SPORTZA" },
      {
        name: "description",
        content: "Injury records with severity, body location, and reporting source",
      },
    ],
  }),
  loader: ({ context }) => context.queryClient.ensureQueryData(injuriesQueryOptions),
  component: InjuriesPage,
});

function InjuriesPage() {
  const { data: result } = useSuspenseQuery(injuriesQueryOptions);

  return (
    <div className="page-shell space-y-6 py-6">
      <PageHeader
        title="Injury Research"
        context="Injury records with severity, body location, and reporting source"
      />
      <DataBoundary result={result}>{(data) => <InjuriesContent data={data} />}</DataBoundary>
    </div>
  );
}

function InjuriesContent({ data }: { data: Injuries }) {
  const records = data.records;

  const sorted = useMemo(
    () => [...records].sort((a, b) => b.date.localeCompare(a.date)),
    [records],
  );

  const severityCounts = useMemo(() => {
    const counts = { mild: 0, moderate: 0, severe: 0 };
    for (const r of records) counts[r.severity]++;
    return counts;
  }, [records]);

  const sourceCounts = useMemo(() => {
    let clinical = 0;
    let selfReported = 0;
    for (const r of records) {
      if (r.source === "clinical") clinical++;
      else selfReported++;
    }
    return { clinical, selfReported };
  }, [records]);

  const locationData = useMemo(() => {
    const map = new Map<string, number>();
    for (const r of records) {
      map.set(r.bodyLocation, (map.get(r.bodyLocation) ?? 0) + 1);
    }
    return Array.from(map.entries())
      .map(([location, count]) => ({ location, count }))
      .sort((a, b) => b.count - a.count);
  }, [records]);

  if (records.length === 0) {
    return <EmptyState message="No injury records in the dataset." />;
  }

  return (
    <>
      {/* Summary cards */}
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        <SummaryCard label="Total injuries" value={fmtNumber(records.length)} />
        <SummaryCard
          label="By severity"
          value={`${severityCounts.mild} mild · ${severityCounts.moderate} mod · ${severityCounts.severe} sev`}
        />
        <SummaryCard label="Clinical" value={fmtNumber(sourceCounts.clinical)} />
        <SummaryCard label="Self-reported" value={fmtNumber(sourceCounts.selfReported)} />
      </div>

      {/* Body location chart */}
      <ChartCard title="Injuries by body location" note="Count of recorded injuries per body site">
        <ResponsiveContainer width="100%" height={Math.max(200, locationData.length * 40)}>
          <BarChart
            data={locationData}
            layout="vertical"
            margin={{ top: 4, right: 24, bottom: 4, left: 90 }}
          >
            <CartesianGrid {...gridProps} horizontal={false} vertical />
            <XAxis type="number" {...axisProps} allowDecimals={false} />
            <YAxis type="category" dataKey="location" {...axisProps} width={86} />
            <Tooltip
              contentStyle={tooltipContentStyle}
              labelStyle={tooltipLabelStyle}
              itemStyle={tooltipItemStyle}
            />
            <Bar
              dataKey="count"
              name="Injuries"
              fill={semanticColor.headline}
              radius={[0, 3, 3, 0]}
            />
          </BarChart>
        </ResponsiveContainer>
      </ChartCard>

      {/* Injury timeline */}
      <ChartCard
        title="Injury timeline"
        note="Each bar represents injuries on that date; color indicates severity"
      >
        <TimelineChart records={sorted} />
      </ChartCard>

      {/* Records table */}
      <section className="space-y-3">
        <SectionHeader title="All records" />
        <div className="overflow-hidden rounded-lg border border-border bg-card">
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Date</TableHead>
                  <TableHead>Athlete</TableHead>
                  <TableHead>Body location</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead>Severity</TableHead>
                  <TableHead>Source</TableHead>
                  <TableHead className="text-right">Days out</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {sorted.map((r) => (
                  <TableRow key={r.id}>
                    <TableCell className="tabular">{fmtDate(r.date)}</TableCell>
                    <TableCell>{r.athleteName ?? r.athleteId}</TableCell>
                    <TableCell>{r.bodyLocation}</TableCell>
                    <TableCell>{r.type}</TableCell>
                    <TableCell>
                      <SeverityBadge severity={r.severity} />
                    </TableCell>
                    <TableCell>
                      <SourceBadge source={r.source} />
                    </TableCell>
                    <TableCell className="tabular text-right">
                      {r.daysOut !== undefined ? `${r.daysOut} days` : "—"}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </div>
      </section>
    </>
  );
}

function SummaryCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg border border-border bg-card p-3">
      <p className="text-xs font-medium text-muted-foreground">{label}</p>
      <p className="mt-1 text-sm font-semibold tabular text-foreground">{value}</p>
    </div>
  );
}

function TimelineChart({ records }: { records: Injuries["records"] }) {
  // Group by date and severity
  const dateMap = new Map<string, { mild: number; moderate: number; severe: number }>();
  for (const r of records) {
    const existing = dateMap.get(r.date) ?? { mild: 0, moderate: 0, severe: 0 };
    existing[r.severity]++;
    dateMap.set(r.date, existing);
  }
  const chartData = Array.from(dateMap.entries())
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([date, counts]) => ({ date, ...counts }));

  return (
    <ResponsiveContainer width="100%" height={240}>
      <BarChart data={chartData} margin={{ top: 8, right: 12, bottom: 4, left: 4 }}>
        <CartesianGrid {...gridProps} />
        <XAxis
          dataKey="date"
          {...axisProps}
          tickFormatter={(d: string) => fmtDate(d).split(" ").slice(0, 2).join(" ")}
        />
        <YAxis {...axisProps} allowDecimals={false} />
        <Tooltip
          contentStyle={tooltipContentStyle}
          labelStyle={tooltipLabelStyle}
          itemStyle={tooltipItemStyle}
          labelFormatter={fmtDate}
        />
        <Bar dataKey="mild" name="Mild" stackId="sev" fill={severityColor.mild} />
        <Bar dataKey="moderate" name="Moderate" stackId="sev" fill={severityColor.moderate} />
        <Bar
          dataKey="severe"
          name="Severe"
          stackId="sev"
          fill={severityColor.severe}
          radius={[3, 3, 0, 0]}
        />
      </BarChart>
    </ResponsiveContainer>
  );
}
