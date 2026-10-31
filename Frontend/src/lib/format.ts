import { format, parseISO } from "date-fns";

/** Plain, tabular-friendly number formatting for KPIs and tables. */
export function fmtNumber(value: number, precision = 0): string {
  return value.toLocaleString("en-GB", {
    minimumFractionDigits: precision,
    maximumFractionDigits: precision,
    useGrouping: true,
  });
}

export function fmtSigned(value: number, precision = 0): string {
  const sign = value > 0 ? "+" : value < 0 ? "−" : "";
  return `${sign}${fmtNumber(Math.abs(value), precision)}`;
}

export function fmtPercent(value: number, precision = 0): string {
  return `${fmtNumber(value, precision)}%`;
}

/** "2026-10-30" -> "30 Oct 2026" */
export function fmtDate(iso: string): string {
  try {
    return format(parseISO(iso), "d MMM yyyy");
  } catch {
    return iso;
  }
}

/** Short tick label for chart axes: "30 Oct". */
export function fmtTickDate(iso: string): string {
  try {
    return format(parseISO(iso), "d MMM");
  } catch {
    return iso;
  }
}

/** Correlation coefficient as plain text, e.g. "+0.42" / "−0.18". */
export function fmtR(r: number): string {
  const sign = r > 0 ? "+" : r < 0 ? "−" : "";
  return `${sign}${Math.abs(r).toFixed(2)}`;
}
