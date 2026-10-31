import { createFileRoute } from "@tanstack/react-router";
import { useSuspenseQuery } from "@tanstack/react-query";
import { Fragment, useMemo } from "react";
import { Info } from "lucide-react";

import { correlationsQueryOptions } from "@/lib/api/queries";
import { DataBoundary } from "@/components/data-state";
import { PageHeader, SectionHeader } from "@/components/page-header";
import { ChartCard } from "@/components/chart-card";
import { fmtR, fmtNumber } from "@/lib/format";
import { correlationColor } from "@/lib/chart-theme";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import type { Correlations } from "@/lib/api/types";

export const Route = createFileRoute("/correlations")({
  head: () => ({
    meta: [
      { title: "Correlation Lab — SPORTZA" },
      { name: "description", content: "Pairwise associations between tracking variables" },
    ],
  }),
  loader: ({ context }) => context.queryClient.ensureQueryData(correlationsQueryOptions),
  component: CorrelationsPage,
});

function CorrelationsPage() {
  const { data: result } = useSuspenseQuery(correlationsQueryOptions);

  return (
    <div className="page-shell space-y-6 py-6">
      <PageHeader
        title="Correlation Lab"
        context="Pairwise associations between tracking variables"
      />
      <DataBoundary result={result}>{(data) => <CorrelationsContent data={data} />}</DataBoundary>
    </div>
  );
}

function CorrelationsContent({ data }: { data: Correlations }) {
  const vars = data.variables;

  const lookup = useMemo(() => {
    const map = new Map<string, { r: number; n: number }>();
    for (const p of data.pairs) {
      map.set(`${p.aId}:${p.bId}`, { r: p.r, n: p.n });
      map.set(`${p.bId}:${p.aId}`, { r: p.r, n: p.n });
    }
    return map;
  }, [data.pairs]);

  const sortedPairs = useMemo(
    () => [...data.pairs].sort((a, b) => Math.abs(b.r) - Math.abs(a.r)),
    [data.pairs],
  );

  return (
    <>
      {/* Causation reminder */}
      <div className="flex gap-2.5 rounded-md bg-tint-info px-3 py-2.5">
        <Info className="size-4 shrink-0 text-info" aria-hidden />
        <p className="text-sm text-foreground">
          Correlation coefficients describe linear associations between variables. They do not imply
          that changes in one variable cause changes in another.
        </p>
      </div>

      {/* Heatmap */}
      <ChartCard
        title="Correlation matrix"
        note="Green = positive association, red = negative; stronger color = stronger correlation"
      >
        <div className="overflow-x-auto -mx-4 px-4">
          <div
            style={{
              display: "grid",
              gridTemplateColumns: `8rem repeat(${vars.length}, minmax(3.5rem, 1fr))`,
              gap: 2,
            }}
          >
            {/* Header row */}
            <div />
            {vars.map((v) => (
              <div
                key={v.id}
                className="truncate px-1 text-center text-[11px] font-medium text-muted-foreground"
                title={v.label}
              >
                {v.label}
              </div>
            ))}

            {/* Data rows */}
            {vars.map((rowVar) => (
              <Fragment key={rowVar.id}>
                <div className="flex items-center justify-end pr-2 text-xs font-medium text-foreground">
                  {rowVar.label}
                </div>
                {vars.map((colVar) => {
                  const isDiag = rowVar.id === colVar.id;
                  const pair = isDiag ? null : lookup.get(`${rowVar.id}:${colVar.id}`);
                  const r = isDiag ? 1 : (pair?.r ?? null);

                  return (
                    <div
                      key={colVar.id}
                      className="flex aspect-square items-center justify-center rounded-sm text-xs font-medium tabular"
                      style={{
                        backgroundColor: r !== null ? correlationColor(r) : undefined,
                        color: r !== null && Math.abs(r) > 0.6 ? "#fff" : "#202923",
                      }}
                      title={
                        r !== null ? `${rowVar.label} × ${colVar.label}: r = ${fmtR(r)}` : undefined
                      }
                    >
                      {r !== null ? fmtR(r) : "—"}
                    </div>
                  );
                })}
              </Fragment>
            ))}
          </div>
        </div>

        <div className="mt-4 rounded border border-border/80 bg-secondary/50 p-2.5 text-[11px] leading-relaxed text-muted-foreground">
          <strong className="text-foreground">What this correlation matrix conveys:</strong> Quantifies linear pairwise associations via Pearson r (-1.0 to +1.0). Darker green indicates strong positive alignment (e.g. readiness with sleep quality); brick red indicates strong inverse relationships (e.g. fatigue with readiness). While correlation reveals co-movement across longitudinal observations, it does not confirm direct biological causation.
        </div>
      </ChartCard>

      {/* Pair details table */}
      <section className="space-y-3">
        <SectionHeader title="Pair details" description="Sorted by absolute correlation strength" />
        <div className="overflow-hidden rounded-lg border border-border bg-card">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Variable A</TableHead>
                <TableHead>Variable B</TableHead>
                <TableHead className="text-right">r</TableHead>
                <TableHead className="text-right">n</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {sortedPairs.map((p) => {
                const aLabel = vars.find((v) => v.id === p.aId)?.label ?? p.aId;
                const bLabel = vars.find((v) => v.id === p.bId)?.label ?? p.bId;
                return (
                  <TableRow key={`${p.aId}-${p.bId}`}>
                    <TableCell>{aLabel}</TableCell>
                    <TableCell>{bLabel}</TableCell>
                    <TableCell className="tabular text-right font-medium">{fmtR(p.r)}</TableCell>
                    <TableCell className="tabular text-right">{fmtNumber(p.n)}</TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </div>
      </section>
    </>
  );
}
