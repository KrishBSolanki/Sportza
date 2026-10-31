import { createFileRoute } from "@tanstack/react-router";
import { useSuspenseQuery, useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { ArrowDownRight, ArrowUpRight, Minus } from "lucide-react";

import { athletesQueryOptions, readinessQueryOptions } from "@/lib/api/queries";
import { DataBoundary, EmptyState } from "@/components/data-state";
import { PageHeader } from "@/components/page-header";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Progress } from "@/components/ui/progress";
import { Skeleton } from "@/components/ui/skeleton";
import { fmtDate, fmtNumber } from "@/lib/format";
import { cn } from "@/lib/utils";
import type { Readiness } from "@/lib/api/types";

export const Route = createFileRoute("/readiness")({
  head: () => ({
    meta: [
      { title: "Recovery Planner — SPORTZA" },
      {
        name: "description",
        content: "Readiness context, contributing factors, and recovery guidance",
      },
    ],
  }),
  loader: ({ context }) => context.queryClient.ensureQueryData(athletesQueryOptions),
  component: ReadinessPage,
});

function ReadinessPage() {
  const { data: rosterResult } = useSuspenseQuery(athletesQueryOptions);
  const [selectedId, setSelectedId] = useState<string | null>(null);

  return (
    <div className="page-shell space-y-6 py-6">
      <PageHeader
        title="Recovery Planner"
        context="Readiness context, contributing factors, and recovery guidance"
      />

      <DataBoundary result={rosterResult}>
        {(roster) => (
          <>
            <div className="max-w-xs">
              <Select value={selectedId ?? ""} onValueChange={(v) => setSelectedId(v || null)}>
                <SelectTrigger>
                  <SelectValue placeholder="Select an athlete…" />
                </SelectTrigger>
                <SelectContent>
                  {roster.athletes.map((a) => (
                    <SelectItem key={a.id} value={a.id}>
                      {a.name} — {a.position}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {selectedId ? (
              <ReadinessPanel athleteId={selectedId} />
            ) : (
              <EmptyState message="Select an athlete above to view their readiness profile." />
            )}
          </>
        )}
      </DataBoundary>
    </div>
  );
}

function ReadinessPanel({ athleteId }: { athleteId: string }) {
  const { data: result, isLoading } = useQuery(readinessQueryOptions(athleteId));

  if (isLoading || result === undefined) {
    return <Skeleton className="h-80 rounded-lg" />;
  }

  return <DataBoundary result={result}>{(data) => <ReadinessContent data={data} />}</DataBoundary>;
}

function ReadinessContent({ data }: { data: Readiness }) {
  const diff = data.score - data.baselineScore;

  return (
    <div className="space-y-4">
      {/* Score overview */}
      <div className="rounded-lg border border-border bg-card p-5">
        <div className="flex flex-wrap items-start gap-6">
          <div>
            <p className="text-xs font-medium text-muted-foreground">
              Readiness score · {fmtDate(data.date)}
            </p>
            <p className="mt-1 text-4xl font-bold tabular text-foreground">
              {fmtNumber(data.score)}
            </p>
            <p className="mt-1 text-xs text-muted-foreground">
              Baseline {fmtNumber(data.baselineScore)} ({diff >= 0 ? "+" : "−"}
              {fmtNumber(Math.abs(diff))} from baseline)
            </p>
          </div>
          <div className="flex-1 space-y-1 pt-4" style={{ minWidth: 160 }}>
            <Progress value={data.score} className="h-2" />
            <div className="flex justify-between text-[11px] text-muted-foreground">
              <span>0</span>
              <span>100</span>
            </div>
          </div>
        </div>
      </div>

      {/* Contributing factors */}
      {data.factors.length > 0 && (
        <div className="space-y-2">
          <h3 className="text-sm font-semibold text-foreground">Contributing factors</h3>
          <ul className="flex flex-col gap-2">
            {data.factors.map((f, i) => {
              const icon =
                f.direction === "positive" ? (
                  <ArrowUpRight className="size-4 shrink-0 text-primary" aria-hidden />
                ) : f.direction === "negative" ? (
                  <ArrowDownRight className="size-4 shrink-0 text-brick" aria-hidden />
                ) : (
                  <Minus className="size-4 shrink-0 text-muted-foreground" aria-hidden />
                );
              const bg =
                f.direction === "positive"
                  ? "bg-tint-positive"
                  : f.direction === "negative"
                    ? "bg-tint-negative"
                    : "bg-secondary";

              return (
                <li key={i} className={cn("flex gap-2.5 rounded-md px-3 py-2.5", bg)}>
                  {icon}
                  <div className="min-w-0">
                    <p className="text-sm font-medium text-foreground">{f.label}</p>
                    {f.detail && <p className="mt-0.5 text-caption">{f.detail}</p>}
                  </div>
                </li>
              );
            })}
          </ul>
        </div>
      )}

      {/* Recommendation */}
      {data.recommendation && (
        <div className="rounded-lg border border-border bg-card p-4">
          <h3 className="text-sm font-semibold text-foreground">{data.recommendation.headline}</h3>
          <p className="mt-1 text-caption">{data.recommendation.body}</p>
          {data.recommendation.basis.length > 0 && (
            <ul className="mt-2 list-inside list-disc space-y-0.5 text-caption">
              {data.recommendation.basis.map((b, i) => (
                <li key={i}>{b}</li>
              ))}
            </ul>
          )}
        </div>
      )}

      {/* Disclaimer */}
      {data.disclaimer && <p className="text-caption">{data.disclaimer}</p>}
    </div>
  );
}
