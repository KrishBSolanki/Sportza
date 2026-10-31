import { useQueryClient } from "@tanstack/react-query";
import { CircleAlert, CircleHelp, Inbox } from "lucide-react";
import type { ReactNode } from "react";

import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import type { ApiResult } from "@/lib/api/types";

/**
 * Renders API results in one shared visual system:
 * loading skeleton, "API not connected", error with retry, or content.
 * Sections handle their own empty-data rendering via <EmptyState>.
 */
export function DataBoundary<T>({
  result,
  children,
  skeletonHeight = "20rem",
}: {
  result: ApiResult<T> | undefined;
  children: (data: T) => ReactNode;
  skeletonHeight?: string;
}) {
  const queryClient = useQueryClient();

  if (result === undefined) {
    return <Skeleton style={{ height: skeletonHeight }} className="rounded-lg" />;
  }

  if (!result.ok) {
    if (result.reason === "not_configured") {
      return <ApiNotConnected detail={result.message} />;
    }
    return (
      <StateBlock
        icon={<CircleAlert className="size-5 text-brick" aria-hidden />}
        title="Data could not be loaded"
        body={
          result.message
            ? `The research API reported: ${result.message}`
            : "The research API could not be reached."
        }
        action={
          <Button variant="outline" size="sm" onClick={() => queryClient.invalidateQueries()}>
            Try again
          </Button>
        }
      />
    );
  }

  return <>{children(result.data)}</>;
}

export function ApiNotConnected({ detail }: { detail?: string | undefined }) {
  return (
    <StateBlock
      icon={<CircleHelp className="size-5 text-info" aria-hidden />}
      title="API not connected"
      body={
        detail ??
        "The SPORTZA research API is not configured, so this section has no data to show yet."
      }
    >
      <p className="max-w-md text-caption">
        Set the{" "}
        <code className="rounded bg-secondary px-1 py-0.5 text-[12px]">SPORTZA_API_BASE</code>{" "}
        environment variable to the research API's base URL (see{" "}
        <code className="rounded bg-secondary px-1 py-0.5 text-[12px]">docs/api-contract.md</code>)
        and reload.
      </p>
    </StateBlock>
  );
}

export function EmptyState({ message }: { message: string }) {
  return (
    <StateBlock
      icon={<Inbox className="size-5 text-muted-foreground" aria-hidden />}
      body={message}
    />
  );
}

function StateBlock({
  icon,
  title,
  body,
  action,
  children,
}: {
  icon: ReactNode;
  title?: string;
  body?: string;
  action?: ReactNode;
  children?: ReactNode;
}) {
  return (
    <div className="flex min-h-40 flex-col items-center justify-center gap-2 rounded-lg border border-dashed border-border bg-card px-6 py-10 text-center">
      {icon}
      {title ? <p className="text-sm font-medium text-foreground">{title}</p> : null}
      {body ? <p className="max-w-md text-caption">{body}</p> : null}
      {children}
      {action ? <div className="mt-1">{action}</div> : null}
    </div>
  );
}
