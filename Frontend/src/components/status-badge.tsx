import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

export type AthleteStatus = "available" | "limited" | "unavailable";
export type InjurySeverity = "mild" | "moderate" | "severe";

const statusStyles: Record<AthleteStatus, string> = {
  available: "bg-tint-positive text-primary",
  limited: "bg-tint-caution text-amber-foreground",
  unavailable: "bg-tint-negative text-brick",
};

export function AthleteStatusBadge({ status }: { status: AthleteStatus }) {
  return (
    <Badge variant="outline" className={cn("border-transparent font-medium", statusStyles[status])}>
      <span className="capitalize">{status}</span>
    </Badge>
  );
}

const severityStyles: Record<InjurySeverity, string> = {
  mild: "bg-tint-positive text-primary",
  moderate: "bg-tint-caution text-amber-foreground",
  severe: "bg-tint-negative text-brick",
};

export function SeverityBadge({ severity }: { severity: InjurySeverity }) {
  return (
    <Badge
      variant="outline"
      className={cn("border-transparent font-medium", severityStyles[severity])}
    >
      <span className="capitalize">{severity}</span>
    </Badge>
  );
}

export function SourceBadge({ source }: { source: "self_reported" | "clinical" }) {
  return (
    <Badge
      variant="outline"
      className="border-border bg-secondary font-medium text-secondary-foreground"
    >
      {source === "self_reported" ? "Self-reported" : "Clinical"}
    </Badge>
  );
}
