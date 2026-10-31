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

import { athleteDetailQueryOptions } from "@/lib/api/queries";
import { DataBoundary } from "@/components/data-state";
import { PageHeader, SectionHeader } from "@/components/page-header";
import { ChartCard } from "@/components/chart-card";
import { AthleteStatusBadge } from "@/components/status-badge";
import { fmtDate, fmtTickDate, fmtNumber } from "@/lib/format";
import {
  chartPalette,
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
import type { AthleteDetail, Series } from "@/lib/api/types";

const SERIES_COLORS = [
  chartPalette.primary,
  chartPalette.slate,
  chartPalette.amber,
  chartPalette.sage,
  chartPalette.brick,
];

export const Route = createFileRoute("/athletes/$athleteId")({
  head: () => ({
    meta: [
      { title: "Athlete Profile — SPORTZA" },
      { name: "description", content: "Athlete profile and longitudinal trends" },
    ],
  }),
  loader: ({ context, params }) =>
    context.queryClient.ensureQueryData(athleteDetailQueryOptions(params.athleteId)),
  component: AthleteDetailPage,
});

function AthleteDetailPage() {
  const { athleteId } = Route.useParams();
  const { data: result } = useSuspenseQuery(athleteDetailQueryOptions(athleteId));

  return (
    <div className="page-shell space-y-6 py-6">
      <DataBoundary result={result}>{(data) => <AthleteDetailContent data={data} />}</DataBoundary>
    </div>
  );
}

function AthleteDetailContent({ data }: { data: AthleteDetail }) {
  const { athlete, series, recentSessions } = data;

  const domains = groupByDomain(series);

  return (
    <>
      <PageHeader title={athlete.name} context={`${athlete.position} · ${athlete.status}`} />

      {/* Profile card */}
      <div className="rounded-lg border border-border bg-card p-4">
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-5">
          <ProfileField label="Position" value={athlete.position} />
          <ProfileField label="Status">
            <AthleteStatusBadge status={athlete.status} />
          </ProfileField>
          {athlete.ageYears !== undefined && (
            <ProfileField label="Age" value={`${athlete.ageYears} yrs`} />
          )}
          {athlete.heightCm !== undefined && (
            <ProfileField label="Height" value={`${athlete.heightCm} cm`} />
          )}
          {athlete.weightKg !== undefined && (
            <ProfileField label="Weight" value={`${athlete.weightKg} kg`} />
          )}
        </div>
      </div>

      {/* Recent sessions */}
      {recentSessions.length > 0 && (
        <section className="space-y-3">
          <SectionHeader title="Recent sessions" />
          <div className="overflow-hidden rounded-lg border border-border bg-card">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Date</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead className="text-right">Duration</TableHead>
                  <TableHead className="text-right">RPE</TableHead>
                  <TableHead className="text-right">sRPE</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {recentSessions.map((s, i) => (
                  <TableRow key={i}>
                    <TableCell className="tabular">{fmtDate(s.date)}</TableCell>
                    <TableCell>{s.type}</TableCell>
                    <TableCell className="tabular text-right">
                      {fmtNumber(s.durationMin)} min
                    </TableCell>
                    <TableCell className="tabular text-right">
                      {s.rpe !== undefined ? s.rpe : "—"}
                    </TableCell>
                    <TableCell className="tabular text-right">
                      {s.srpe !== undefined ? fmtNumber(s.srpe) : "—"}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </section>
      )}

      {/* Longitudinal series grouped by domain */}
      {(["wellness", "workload", "performance"] as const).map((domain) => {
        const group = domains[domain];
        if (!group || group.length === 0) return null;
        return (
          <section key={domain} className="space-y-3">
            <SectionHeader title={domain.charAt(0).toUpperCase() + domain.slice(1)} />
            <ChartCard
              title={`${domain.charAt(0).toUpperCase() + domain.slice(1)} trends`}
              note="All series for this domain overlaid on one chart"
            >
              <DomainChart series={group} />
            </ChartCard>
          </section>
        );
      })}
    </>
  );
}

function ProfileField({
  label,
  value,
  children,
}: {
  label: string;
  value?: string;
  children?: React.ReactNode;
}) {
  return (
    <div>
      <dt className="text-xs font-medium text-muted-foreground">{label}</dt>
      <dd className="mt-0.5 text-sm font-medium text-foreground">{children ?? value}</dd>
    </div>
  );
}

function DomainChart({ series }: { series: Series[] }) {
  // Merge all series points into a unified timeline keyed by date
  const dateMap = new Map<string, Record<string, number>>();
  for (const s of series) {
    for (const pt of s.points) {
      const existing = dateMap.get(pt.date) ?? {};
      existing[s.id] = pt.value;
      dateMap.set(pt.date, existing);
    }
  }
  const chartData = Array.from(dateMap.entries())
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([date, vals]) => ({ date, ...vals }));

  return (
    <>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={chartData} margin={{ top: 8, right: 12, bottom: 4, left: 4 }}>
          <CartesianGrid {...gridProps} />
          <XAxis dataKey="date" {...axisProps} tickFormatter={fmtTickDate} />
          <YAxis {...axisProps} />
          <Tooltip
            contentStyle={tooltipContentStyle}
            labelStyle={tooltipLabelStyle}
            itemStyle={tooltipItemStyle}
            labelFormatter={fmtTickDate}
          />
          <Legend />
          {series.map((s, i) => (
            <Line
              key={s.id}
              type="monotone"
              dataKey={s.id}
              name={`${s.label} (${s.unit})`}
              stroke={SERIES_COLORS[i % SERIES_COLORS.length]}
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 3 }}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>

      <div className="mt-3 rounded border border-border/80 bg-secondary/50 p-2.5 text-[11px] leading-relaxed text-muted-foreground">
        <strong className="text-foreground">What this longitudinal trend conveys:</strong> Tracks multi-week intra-individual variations for this athlete. Comparing reported readiness against fatigue, muscle soreness, and sRPE training load highlights individual recovery kinetics and tolerance to acute loading.
      </div>
    </>
  );
}

function groupByDomain(series: Series[]) {
  const groups: Record<string, Series[]> = {};
  for (const s of series) {
    const list = groups[s.domain] ?? [];
    list.push(s);
    groups[s.domain] = list;
  }
  return groups;
}
