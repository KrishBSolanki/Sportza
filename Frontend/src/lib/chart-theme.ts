/**
 * Shared chart language: one restrained palette, the same metric always in
 * the same color, publication-quality defaults for every Recharts surface.
 */
export const chartPalette = {
  primary: "#27634B", // forest green — headline metric, positive/selected
  slate: "#58778A", // calm blue-grey — secondary/comparative series
  amber: "#C58A3A", // warm amber — attention values
  brick: "#B95750", // muted brick — negative/alert values
  sage: "#8DA996", // muted sage — neutral/context series
} as const;

export const chartChrome = {
  grid: "#E4EAE5", // very light grey-green gridlines
  axis: "#65716A", // muted slate axis labels
  axisLine: "#DCE3DC",
  tooltipSurface: "#FFFFFF",
  tooltipBorder: "#DCE3DC",
  tooltipText: "#202923",
  referenceLine: "#B3BFB8",
} as const;

/** Semantic assignments used consistently across all pages. */
export const semanticColor = {
  headline: chartPalette.primary,
  compare: chartPalette.slate,
  attention: chartPalette.amber,
  negative: chartPalette.brick,
  context: chartPalette.sage,
} as const;

/** Severity ramp for injury severity encoding. */
export const severityColor = {
  mild: chartPalette.sage,
  moderate: chartPalette.amber,
  severe: chartPalette.brick,
} as const;

/**
 * Diverging correlation color: balanced around zero — brick for negative,
 * neutral paper for zero, forest green for positive.
 */
export function correlationColor(r: number): string {
  const clamped = Math.max(-1, Math.min(1, r));
  const t = Math.abs(clamped) ** 0.8; // ease so mid-range correlations stay readable
  if (clamped >= 0) {
    return mix("#F6F7F4", chartPalette.primary, t);
  }
  return mix("#F6F7F4", chartPalette.brick, t);
}

function mix(fromHex: string, toHex: string, t: number): string {
  const from = parseHex(fromHex);
  const to = parseHex(toHex);
  const out = from.map((c, i) => Math.round(c + ((to[i] ?? c) - c) * t));
  return `#${out.map((c) => c.toString(16).padStart(2, "0")).join("")}`;
}

function parseHex(hex: string): [number, number, number] {
  return [
    parseInt(hex.slice(1, 3), 16),
    parseInt(hex.slice(3, 5), 16),
    parseInt(hex.slice(5, 7), 16),
  ];
}

/** Shared Recharts props so every chart shares the same chrome. */
export const axisProps = {
  stroke: chartChrome.axisLine,
  tick: { fill: chartChrome.axis, fontSize: 12 },
  tickLine: false,
} as const;

export const gridProps = {
  stroke: chartChrome.grid,
  strokeDasharray: "0",
  vertical: false,
} as const;

export const tooltipContentStyle = {
  backgroundColor: chartChrome.tooltipSurface,
  border: `1px solid ${chartChrome.tooltipBorder}`,
  borderRadius: 6,
  fontSize: 13,
  color: chartChrome.tooltipText,
  boxShadow: "0 2px 8px rgba(32, 41, 35, 0.08)",
} as const;

export const tooltipLabelStyle = {
  color: chartChrome.tooltipText,
  fontWeight: 600,
  marginBottom: 4,
} as const;

export const tooltipItemStyle = { padding: 0 } as const;
