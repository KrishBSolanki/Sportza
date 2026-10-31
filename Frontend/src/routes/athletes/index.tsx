import { createFileRoute, Link } from "@tanstack/react-router";
import { useSuspenseQuery } from "@tanstack/react-query";

import { athletesQueryOptions } from "@/lib/api/queries";
import { DataBoundary, EmptyState } from "@/components/data-state";
import { PageHeader } from "@/components/page-header";
import { AthleteStatusBadge } from "@/components/status-badge";
import { fmtDate } from "@/lib/format";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import type { Athletes } from "@/lib/api/types";

export const Route = createFileRoute("/athletes/")({
  head: () => ({
    meta: [
      { title: "Athletes — SPORTZA" },
      { name: "description", content: "Roster overview with availability status" },
    ],
  }),
  loader: ({ context }) => context.queryClient.ensureQueryData(athletesQueryOptions),
  component: AthletesPage,
});

function AthletesPage() {
  const { data: result } = useSuspenseQuery(athletesQueryOptions);

  return (
    <div className="page-shell space-y-6 py-6">
      <PageHeader title="Athletes" context="Roster overview with availability status" />
      <DataBoundary result={result}>{(data) => <AthletesContent data={data} />}</DataBoundary>
    </div>
  );
}

function AthletesContent({ data }: { data: Athletes }) {
  if (data.athletes.length === 0) {
    return <EmptyState message="No athletes in the dataset." />;
  }

  return (
    <div className="overflow-hidden rounded-lg border border-border bg-card">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Name</TableHead>
            <TableHead>Position</TableHead>
            <TableHead className="hidden sm:table-cell">Squad</TableHead>
            <TableHead>Status</TableHead>
            <TableHead className="hidden md:table-cell">Age</TableHead>
            <TableHead className="hidden md:table-cell">Last session</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {data.athletes.map((a) => (
            <TableRow key={a.id} className="cursor-pointer transition-colors hover:bg-accent/50">
              <TableCell>
                <Link
                  to="/athletes/$athleteId"
                  params={{ athleteId: a.id }}
                  className="font-medium text-foreground hover:underline"
                >
                  {a.name}
                </Link>
              </TableCell>
              <TableCell className="text-muted-foreground">{a.position}</TableCell>
              <TableCell className="hidden text-muted-foreground sm:table-cell">
                {a.squad ?? "—"}
              </TableCell>
              <TableCell>
                <AthleteStatusBadge status={a.status} />
              </TableCell>
              <TableCell className="hidden tabular md:table-cell">
                {a.ageYears !== undefined ? `${a.ageYears} yrs` : "—"}
              </TableCell>
              <TableCell className="hidden tabular md:table-cell">
                {a.lastSessionDate ? fmtDate(a.lastSessionDate) : "—"}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
