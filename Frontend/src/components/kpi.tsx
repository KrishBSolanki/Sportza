import { ArrowDownRight, ArrowUpRight, Minus } from "lucide-react";

import { cn } from "@/lib/utils";
import { fmtNumber, fmtSigned } from "@/lib/format";

import type { Kpi } from "@/lib/api/types";

export function KpiRow({ kpis }: { kpis: Kpi[] }) {
  if (kpis.length === 0) return null;
  return (
    <dl className="grid grid-cols-2 gap-px overflow-hidden rounded-lg border border-border bg-border sm:grid-cols-3 xl:grid-cols-5">
      {kpis.map((kpi) => (
        <KpiCell key={kpi.id} kpi={kpi} />
      ))}
    </dl>
  );
}

function KpiCell({ kpi }: { kpi: Kpi }) {
  const precision = kpi.precision ?? 0;
  const direction = kpi.deltaDirection ?? "flat";
  return (
    <div className="bg-card p-4">
      <dt className="text-xs font-medium text-muted-foreground">{kpi.label}</dt>
      <dd className="mt-1.5 flex items-baseline gap-1.5">
        <span className="text-2xl font-semibold tabular tracking-tight text-foreground">
          {fmtNumber(kpi.value, precision)}
        </span>
        {kpi.unit ? <span className="text-xs text-muted-foreground">{kpi.unit}</span> : null}
      </dd>
      {kpi.delta !== undefined ? (
        <dd className="mt-1 flex items-center gap-1 text-xs">
          <DeltaChip delta={kpi.delta} direction={direction} precision={precision} />
          {kpi.context ? <span className="text-muted-foreground">{kpi.context}</span> : null}
        </dd>
      ) : kpi.context ? (
        <dd className="mt-1 text-xs text-muted-foreground">{kpi.context}</dd>
      ) : null}
    </div>
  );
}

function DeltaChip({
  delta,
  direction,
  precision,
}: {
  delta: number;
  direction: "up" | "down" | "flat";
  precision: number;
}) {
  const Icon = direction === "up" ? ArrowUpRight : direction === "down" ? ArrowDownRight : Minus;
  const tone =
    direction === "up"
      ? "bg-tint-positive text-primary"
      : direction === "down"
        ? "bg-tint-negative text-brick"
        : "bg-secondary text-muted-foreground";
  return (
    <span className={cn("inline-flex items-center gap-0.5 rounded px-1 py-0.5 font-medium", tone)}>
      <Icon className="size-3" aria-hidden />
      {fmtSigned(delta, precision)}
    </span>
  );
}
