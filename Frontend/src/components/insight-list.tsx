import { CircleAlert, Info, TrendingUp } from "lucide-react";

import { cn } from "@/lib/utils";

import type { Insight } from "@/lib/api/types";

const toneStyles = {
  info: {
    wrap: "bg-tint-info text-info-foreground",
    icon: <Info className="size-4 shrink-0 text-info" aria-hidden />,
  },
  positive: {
    wrap: "bg-tint-positive",
    icon: <TrendingUp className="size-4 shrink-0 text-primary" aria-hidden />,
  },
  caution: {
    wrap: "bg-tint-caution",
    icon: <CircleAlert className="size-4 shrink-0 text-amber" aria-hidden />,
  },
} as const;

/** Concise, evidence-anchored insight entries — never marketing copy. */
export function InsightList({ insights }: { insights: Insight[] }) {
  if (insights.length === 0) return null;
  return (
    <ul className="flex flex-col gap-2">
      {insights.map((insight, i) => {
        const tone = toneStyles[insight.tone];
        return (
          <li key={i} className={cn("flex gap-2.5 rounded-md px-3 py-2.5", tone.wrap)}>
            {tone.icon}
            <div className="min-w-0">
              <p className="text-sm font-medium text-foreground">{insight.title}</p>
              <p className="mt-0.5 text-caption">{insight.body}</p>
            </div>
          </li>
        );
      })}
    </ul>
  );
}
