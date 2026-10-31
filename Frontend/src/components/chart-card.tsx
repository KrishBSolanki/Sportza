import type { ReactNode } from "react";

import { cn } from "@/lib/utils";

/**
 * Flat chart surface with a descriptive title and a one-line note about what
 * the viewer should notice. Blends with the page: border, no shadow.
 */
export function ChartCard({
  title,
  note,
  actions,
  children,
  className,
  contentClassName,
}: {
  title: string;
  /** What to notice, one sentence. */
  note?: string | undefined;
  actions?: ReactNode;
  children: ReactNode;
  className?: string | undefined;
  contentClassName?: string | undefined;
}) {
  return (
    <section className={cn("rounded-lg border border-border bg-card", className)}>
      <header className="flex flex-wrap items-start justify-between gap-2 px-4 pb-2 pt-4">
        <div className="min-w-0">
          <h3 className="text-sm font-semibold text-foreground">{title}</h3>
          {note ? <p className="mt-0.5 max-w-xl text-caption">{note}</p> : null}
        </div>
        {actions ? <div className="flex items-center gap-2">{actions}</div> : null}
      </header>
      <div className={cn("px-4 pb-4", contentClassName)}>{children}</div>
    </section>
  );
}
