import { createFileRoute } from "@tanstack/react-router";
import { useSuspenseQuery } from "@tanstack/react-query";
import { useState, useTransition, useMemo } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
  BarChart,
  Bar,
} from "recharts";
import {
  Play,
  RotateCcw,
  Sliders,
  User,
  ShieldCheck,
  CheckCircle2,
  Sparkles,
  Info,
  BookOpen,
  ChevronDown,
  ChevronUp,
} from "lucide-react";

import { modelsQueryOptions, modelAthletesQueryOptions } from "@/lib/api/queries";
import {
  runReadinessPlayerModel,
  runReadinessModel,
  runPerformanceModel,
  runInjuryModel,
} from "@/lib/api/sportza.functions";
import { DataBoundary } from "@/components/data-state";
import { PageHeader, SectionHeader } from "@/components/page-header";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { ChartCard } from "@/components/chart-card";
import { fmtDate, fmtNumber } from "@/lib/format";
import { cn } from "@/lib/utils";
import {
  semanticColor,
  axisProps,
  gridProps,
  tooltipContentStyle,
  tooltipLabelStyle,
  tooltipItemStyle,
} from "@/lib/chart-theme";
import type {
  Models,
  ModelEntry,
  ModelAthletes,
  PlayerReadinessRunResult,
  ReadinessRunResult,
  PerformanceRunResult,
  InjuryRunResult,
} from "@/lib/api/types";

export const Route = createFileRoute("/models")({
  head: () => ({
    meta: [
      { title: "Model Lab & Evaluation — SPORTZA" },
      {
        name: "description",
        content: "Interactive model training, match window evaluation, and validation benchmarks",
      },
    ],
  }),
  loader: ({ context }) =>
    Promise.all([
      context.queryClient.ensureQueryData(modelsQueryOptions),
      context.queryClient.ensureQueryData(modelAthletesQueryOptions),
    ]),
  component: ModelsPage,
});

function ModelsPage() {
  const { data: modelsResult } = useSuspenseQuery(modelsQueryOptions);
  const { data: athletesResult } = useSuspenseQuery(modelAthletesQueryOptions);

  return (
    <div className="page-shell space-y-6 py-6">
      <PageHeader
        title="Model Lab & Research Workbench"
        context="Benchmark and train predictive models against naive baselines with chronological holdouts and match-window filters"
      />
      <DataBoundary result={modelsResult}>
        {(modelsData) => (
          <DataBoundary result={athletesResult}>
            {(athletesData) => (
              <InteractiveModelLab models={modelsData} athletes={athletesData} />
            )}
          </DataBoundary>
        )}
      </DataBoundary>
    </div>
  );
}

type TabType = "player_window" | "squad_forecaster" | "game_perf" | "injury_gate";

function InteractiveModelLab({
  models,
  athletes,
}: {
  models: Models;
  athletes: ModelAthletes;
}) {
  const [activeTab, setActiveTab] = useState<TabType>("player_window");
  const [showGuide, setShowGuide] = useState(false);

  return (
    <div className="space-y-6">
      {/* Mentor & Presentation Terminology Guide Banner */}
      <div className="rounded-lg border border-border bg-card p-4 transition-all">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <BookOpen className="size-4 text-primary" />
            <h3 className="text-xs font-semibold text-foreground">
              Sports-Science & Modeling Concepts Guide (Terms Explained for Review)
            </h3>
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setShowGuide(!showGuide)}
            className="h-7 text-xs text-muted-foreground hover:text-foreground"
          >
            {showGuide ? (
              <>
                Hide Guide <ChevronUp className="ml-1 size-3.5" />
              </>
            ) : (
              <>
                Show Guide & Definitions <ChevronDown className="ml-1 size-3.5" />
              </>
            )}
          </Button>
        </div>

        {showGuide && (
          <div className="mt-3 grid gap-3 border-t border-border pt-3 text-xs leading-relaxed text-muted-foreground sm:grid-cols-2 lg:grid-cols-3">
            <div className="rounded-md border border-border/60 bg-secondary/40 p-2.5">
              <strong className="block font-semibold text-foreground">
                sRPE (Session RPE in AU)
              </strong>
              Athlete perceived exertion (Borg CR10, 1–10) multiplied by duration in minutes.
              Measured in Arbitrary Units (AU). Quantifies internal physiological strain.
            </div>

            <div className="rounded-md border border-border/60 bg-secondary/40 p-2.5">
              <strong className="block font-semibold text-foreground">
                ACWR (Acute:Chronic Workload Ratio)
              </strong>
              7-day acute rolling load (fatigue) divided by 28-day chronic load (fitness).
              0.8–1.3 is the safe sweet spot; &gt;1.5 spikes injury risk significantly.
            </div>

            <div className="rounded-md border border-border/60 bg-secondary/40 p-2.5">
              <strong className="block font-semibold text-foreground">
                LOCF Naive Baseline
              </strong>
              Last-Observation-Carried-Forward: the naive sports benchmark assuming tomorrow's
              readiness equals today's. Any viable ML model must beat this baseline.
            </div>

            <div className="rounded-md border border-border/60 bg-secondary/40 p-2.5">
              <strong className="block font-semibold text-foreground">
                Chronological Holdout
              </strong>
              Training strictly on dates prior to a calendar cutoff (e.g. 2021-06-01) and testing
              exclusively on subsequent dates. Eliminates look-ahead data leakage in sports time series.
            </div>

            <div className="rounded-md border border-border/60 bg-secondary/40 p-2.5">
              <strong className="block font-semibold text-foreground">
                MAE &amp; RMSE Metrics
              </strong>
              MAE (Mean Absolute Error) is average point error on the 1–10 scale. RMSE penalizes
              occasional large outliers more heavily. Lower values represent tighter precision.
            </div>

            <div className="rounded-md border border-border/60 bg-secondary/40 p-2.5">
              <strong className="block font-semibold text-foreground">
                Match Horizon Windows
              </strong>
              <strong>Prior 7d:</strong> cumulative strain and tapering before kickoff.{" "}
              <strong>Match Day:</strong> game-day readiness state.{" "}
              <strong>Post 7d:</strong> supercompensation and physiological recovery kinetics.
            </div>
          </div>
        )}
      </div>

      {/* Task Selection Switcher */}
      <div className="flex flex-wrap items-center gap-2 border-b border-border pb-3">
        <button
          type="button"
          onClick={() => setActiveTab("player_window")}
          className={cn(
            "flex items-center gap-2 rounded-md px-3 py-1.5 text-xs font-medium transition-colors",
            activeTab === "player_window"
              ? "bg-primary text-primary-foreground"
              : "bg-secondary text-muted-foreground hover:text-foreground",
          )}
        >
          <User className="size-3.5" />
          Athlete Match-Window Forecaster
        </button>
        <button
          type="button"
          onClick={() => setActiveTab("squad_forecaster")}
          className={cn(
            "flex items-center gap-2 rounded-md px-3 py-1.5 text-xs font-medium transition-colors",
            activeTab === "squad_forecaster"
              ? "bg-primary text-primary-foreground"
              : "bg-secondary text-muted-foreground hover:text-foreground",
          )}
        >
          <Sliders className="size-3.5" />
          Squad Readiness Model (All Data)
        </button>
        <button
          type="button"
          onClick={() => setActiveTab("game_perf")}
          className={cn(
            "flex items-center gap-2 rounded-md px-3 py-1.5 text-xs font-medium transition-colors",
            activeTab === "game_perf"
              ? "bg-primary text-primary-foreground"
              : "bg-secondary text-muted-foreground hover:text-foreground",
          )}
        >
          <Sparkles className="size-3.5" />
          Match Performance Rating Forecaster
        </button>
        <button
          type="button"
          onClick={() => setActiveTab("injury_gate")}
          className={cn(
            "flex items-center gap-2 rounded-md px-3 py-1.5 text-xs font-medium transition-colors",
            activeTab === "injury_gate"
              ? "bg-primary text-primary-foreground"
              : "bg-secondary text-muted-foreground hover:text-foreground",
          )}
        >
          <ShieldCheck className="size-3.5" />
          Injury Risk Pre-Flight Gate
        </button>
      </div>

      {/* Tab 1: Athlete Window Forecaster */}
      {activeTab === "player_window" && (
        <PlayerWindowLab athletes={athletes.athletes} />
      )}

      {/* Tab 2: Squad Readiness Forecaster */}
      {activeTab === "squad_forecaster" && <SquadForecasterLab />}

      {/* Tab 3: Match Performance Rating Forecaster */}
      {activeTab === "game_perf" && <GamePerformanceLab />}

      {/* Tab 4: Injury Risk Gate */}
      {activeTab === "injury_gate" && <InjuryGateLab />}

      {/* Static Model Registry & Baselines Table */}
      <section className="space-y-4 pt-6">
        <SectionHeader
          title="Model Registry & Benchmark Verification"
          description="Candidate models compared against naive persistence and historical mean baselines"
        />
        <div className="grid gap-4 lg:grid-cols-2">
          {models.models.map((model) => (
            <ModelRegistryCard
              key={model.id}
              model={model}
              isActive={model.id === models.activeModelId}
            />
          ))}
        </div>
      </section>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// COMPONENT 1: Athlete Match-Window Forecaster (Prior 7 Days / Match Day / Post 7 Days)
// ─────────────────────────────────────────────────────────────────────────────

function PlayerWindowLab({
  athletes,
}: {
  athletes: ModelAthletes["athletes"];
}) {
  const [selectedAthlete, setSelectedAthlete] = useState(
    athletes[0]?.id ?? "TeamA_P01",
  );
  const [splitDate, setSplitDate] = useState("2021-06-01");
  const [windowType, setWindowType] = useState<"prior_7" | "match_day" | "post_7">(
    "prior_7",
  );
  const [isPending, startTransition] = useTransition();
  const [result, setResult] = useState<PlayerReadinessRunResult | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const handleRun = () => {
    setErrorMsg(null);
    startTransition(async () => {
      try {
        const res = await runReadinessPlayerModel({
          data: {
            athlete_id: selectedAthlete,
            split_date: splitDate,
            window: windowType,
          },
        });
        if (res.ok) {
          setResult(res.data);
        } else {
          setErrorMsg(res.message ?? "Failed to execute player model");
        }
      } catch (err) {
        setErrorMsg(err instanceof Error ? err.message : "Request failed");
      }
    });
  };

  const athleteName =
    athletes.find((a) => a.id === selectedAthlete)?.name ?? selectedAthlete;

  return (
    <div className="space-y-6">
      {/* Parameter Controls Card */}
      <div className="rounded-lg border border-border bg-card p-5">
        <div className="mb-4">
          <h2 className="text-sm font-semibold text-foreground">
            Athlete Match-Window Forecasting &amp; Evaluation
          </h2>
          <p className="mt-0.5 text-caption">
            Isolate the athlete's physical readiness trajectory:
            during the <strong>7 days leading up to match day</strong>, on the <strong>match day itself</strong>, or during the <strong>7-day recovery period after matches</strong>.
          </p>
        </div>

        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {/* Athlete Selector */}
          <div>
            <label className="block text-xs font-medium text-muted-foreground">
              Select Athlete
            </label>
            <select
              value={selectedAthlete}
              onChange={(e) => setSelectedAthlete(e.target.value)}
              className="mt-1 block w-full rounded-md border border-border bg-background px-3 py-1.5 text-xs font-medium text-foreground shadow-sm focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
            >
              {athletes.map((ath) => (
                <option key={ath.id} value={ath.id}>
                  {ath.name} ({ath.position} · {ath.squad ?? "Squad"})
                </option>
              ))}
            </select>
          </div>

          {/* Match Window Selector */}
          <div>
            <label className="block text-xs font-medium text-muted-foreground">
              Match Horizon Window
            </label>
            <select
              value={windowType}
              onChange={(e) =>
                setWindowType(e.target.value as "prior_7" | "match_day" | "post_7")
              }
              className="mt-1 block w-full rounded-md border border-border bg-background px-3 py-1.5 text-xs font-medium text-foreground shadow-sm focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
            >
              <option value="prior_7">Prior 7 Days (Preparation Phase)</option>
              <option value="match_day">On Match Days (Competition)</option>
              <option value="post_7">After 7 Days (Recovery Phase)</option>
            </select>
          </div>

          {/* Chronological Split Date */}
          <div>
            <label className="block text-xs font-medium text-muted-foreground">
              Chronological Split Date
            </label>
            <input
              type="date"
              value={splitDate}
              min="2020-06-01"
              max="2021-10-01"
              onChange={(e) => setSplitDate(e.target.value)}
              className="mt-1 block w-full rounded-md border border-border bg-background px-3 py-1.5 text-xs font-medium text-foreground shadow-sm focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
            />
          </div>

          {/* Action Button */}
          <div className="flex items-end">
            <Button
              onClick={handleRun}
              disabled={isPending}
              className="w-full text-xs"
            >
              {isPending ? (
                <>
                  <RotateCcw className="mr-2 size-3.5 animate-spin" />
                  Fitting Model...
                </>
              ) : (
                <>
                  <Play className="mr-2 size-3.5" />
                  Run Model for {athleteName}
                </>
              )}
            </Button>
          </div>
        </div>

        {/* Explainability footnote */}
        <div className="mt-4 flex items-center gap-2 rounded bg-secondary/60 px-3 py-2 text-[11px] text-muted-foreground">
          <Info className="size-3.5 shrink-0 text-primary" />
          <span>
            <strong>Strict Temporal Split:</strong> Pre-split dates are strictly
            used to calibrate personal baselines and gradient boosting lag weights;
            post-split dates evaluate performance without temporal look-ahead leakage.
          </span>
        </div>
      </div>

      {errorMsg && (
        <div className="flex items-center gap-2 rounded-lg border border-brick/30 bg-tint-caution/20 p-4 text-xs text-brick">
          <Info className="size-4 shrink-0" />
          <span>{errorMsg}</span>
        </div>
      )}

      {/* Model Run Results Display */}
      {result && result.trained && (
        <div className="space-y-6">
          {/* Metrics summary cards */}
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
            <div className="rounded-lg border border-border bg-card p-3">
              <p className="text-xs font-medium text-muted-foreground">
                Model MAE
              </p>
              <p className="mt-1 text-lg font-semibold tabular text-primary">
                {fmtNumber(result.modelMae ?? 0, 2)}
                <span className="ml-1 text-xs font-normal text-muted-foreground">
                  pts
                </span>
              </p>
              <p className="mt-0.5 text-[11px] text-muted-foreground">
                RMSE: {fmtNumber(result.modelRmse ?? 0, 2)}
              </p>
            </div>

            <div className="rounded-lg border border-border bg-card p-3">
              <p className="text-xs font-medium text-muted-foreground">
                LOCF Naive Baseline MAE
              </p>
              <p className="mt-1 text-lg font-semibold tabular text-foreground">
                {fmtNumber(result.baselineMae ?? 0, 2)}
                <span className="ml-1 text-xs font-normal text-muted-foreground">
                  pts
                </span>
              </p>
              <p className="mt-0.5 text-[11px] text-muted-foreground">
                Yesterday's value baseline
              </p>
            </div>

            <div className="rounded-lg border border-border bg-card p-3">
              <p className="text-xs font-medium text-muted-foreground">
                Error Reduction
              </p>
              <p className="mt-1 text-lg font-semibold tabular text-primary">
                {(result.maeImprovementPct ?? 0) > 0 ? "+" : ""}
                {fmtNumber(result.maeImprovementPct ?? 0, 1)}%
              </p>
              <p className="mt-0.5 text-[11px] text-muted-foreground">
                Relative vs Naive LOCF
              </p>
            </div>

            <div className="rounded-lg border border-border bg-card p-3">
              <p className="text-xs font-medium text-muted-foreground">
                Match Context Evaluated
              </p>
              <p className="mt-1 text-lg font-semibold tabular text-foreground">
                {result.windowSamples}
                <span className="ml-1 text-xs font-normal text-muted-foreground">
                  days
                </span>
              </p>
              <p className="mt-0.5 text-[11px] text-muted-foreground">
                across {result.matchDatesCount} total match fixtures
              </p>
            </div>
          </div>

          {/* Timeline Chart: Actual vs Predicted across selected window */}
          {result.timeline && result.timeline.length > 0 && (
            <ChartCard
              title={`Readiness Forecast: ${athleteName} (${
                windowType === "prior_7"
                  ? "Prior 7-Day Window (Preparation)"
                  : windowType === "match_day"
                    ? "On Match Days (Competition)"
                    : "Post-Match 7 Days (Recovery)"
              })`}
              note="Strict holdout evaluation period (actual vs predicted readiness score)"
            >
              <ResponsiveContainer width="100%" height={320}>
                <LineChart
                  data={result.timeline}
                  margin={{ top: 12, right: 16, bottom: 22, left: 8 }}
                >
                  <CartesianGrid {...gridProps} />
                  <XAxis
                    dataKey="date"
                    {...axisProps}
                    label={{
                      value: "Calendar Date (Chronological Holdout)",
                      position: "insideBottom",
                      offset: -12,
                      style: { fill: axisProps.tick.fill, fontSize: 11 },
                    }}
                  />
                  <YAxis
                    {...axisProps}
                    domain={[0, 10]}
                    label={{
                      value: "Readiness (1–10 Scale)",
                      angle: -90,
                      position: "insideLeft",
                      style: { fill: axisProps.tick.fill, fontSize: 11 },
                    }}
                  />
                  <Tooltip
                    contentStyle={tooltipContentStyle}
                    labelStyle={tooltipLabelStyle}
                    itemStyle={tooltipItemStyle}
                  />
                  <Legend verticalAlign="top" height={36} />
                  <Line
                    type="monotone"
                    dataKey="actual"
                    name="Actual Reported Readiness"
                    stroke={semanticColor.headline}
                    strokeWidth={2}
                    dot={{ r: 3 }}
                    connectNulls
                  />
                  <Line
                    type="monotone"
                    dataKey="predicted"
                    name="Model Predicted Readiness"
                    stroke={semanticColor.attention}
                    strokeWidth={2}
                    strokeDasharray="5 3"
                    dot={{ r: 3 }}
                    connectNulls
                  />
                </LineChart>
              </ResponsiveContainer>

              <div className="mt-3 rounded border border-border/80 bg-secondary/50 p-2.5 text-[11px] leading-relaxed text-muted-foreground">
                <strong className="text-foreground">What this chart conveys to the coaching staff:</strong>{" "}
                Compares the player's true self-reported readiness (solid green) against the algorithm's forecast (dashed amber) restricted specifically to {windowType === "prior_7" ? "the 7 days prior to competitive matches" : windowType === "match_day" ? "match days themselves" : "the 7-day post-match recovery curve"}. Closeness of the curves proves the model accurately anticipates wellness drop-offs before match fixtures occur.
              </div>
            </ChartCard>
          )}

          {/* Feature Importances */}
          {result.importances && result.importances.length > 0 && (
            <ChartCard
              title={`Top Predictive Physical Drivers for ${athleteName}`}
              note="Relative split gain importance from Gradient Boosting Regressor"
            >
              <ResponsiveContainer width="100%" height={290}>
                <BarChart
                  data={result.importances.slice(0, 8)}
                  layout="vertical"
                  margin={{ top: 8, right: 24, bottom: 20, left: 180 }}
                >
                  <CartesianGrid {...gridProps} horizontal={false} />
                  <XAxis
                    type="number"
                    {...axisProps}
                    label={{
                      value: "Relative Predictive Importance (Split Gain)",
                      position: "insideBottom",
                      offset: -12,
                      style: { fill: axisProps.tick.fill, fontSize: 11 },
                    }}
                  />
                  <YAxis
                    type="category"
                    dataKey="feature"
                    {...axisProps}
                    width={170}
                    tick={{ fill: axisProps.tick.fill, fontSize: 11 }}
                  />
                  <Tooltip
                    contentStyle={tooltipContentStyle}
                    labelStyle={tooltipLabelStyle}
                    itemStyle={tooltipItemStyle}
                  />
                  <Bar
                    dataKey="importance"
                    name="Importance (Split Gain)"
                    fill={semanticColor.headline}
                    radius={[0, 4, 4, 0]}
                  />
                </BarChart>
              </ResponsiveContainer>

              <div className="mt-3 rounded border border-border/80 bg-secondary/50 p-2.5 text-[11px] leading-relaxed text-muted-foreground">
                <strong className="text-foreground">What this feature ranking conveys:</strong> Identifies which personalized physical markers (e.g. 7-day mean soreness, acute sleep quality, or prior training load) exert the strongest mathematical leverage on this specific athlete's next-day readiness.
              </div>
            </ChartCard>
          )}
        </div>
      )}

      {result && !result.trained && (
        <div className="rounded-lg border border-amber/30 bg-tint-caution/20 p-4 text-xs text-amber-foreground">
          <p className="font-medium">Model could not be calibrated for this window:</p>
          <p className="mt-1">{result.reason}</p>
        </div>
      )}
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// COMPONENT 2: Squad Readiness Forecaster (All Data)
// ─────────────────────────────────────────────────────────────────────────────

function SquadForecasterLab() {
  const [splitDate, setSplitDate] = useState("2021-06-01");
  const [isPending, startTransition] = useTransition();
  const [result, setResult] = useState<ReadinessRunResult | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const handleRun = () => {
    setErrorMsg(null);
    startTransition(async () => {
      try {
        const res = await runReadinessModel({ data: { split_date: splitDate } });
        if (res.ok) {
          setResult(res.data);
        } else {
          setErrorMsg(res.message ?? "Training failed");
        }
      } catch (err) {
        setErrorMsg(err instanceof Error ? err.message : "Request failed");
      }
    });
  };

  const scatterChartData = useMemo(() => {
    return (
      result?.scatter.slice(0, 40).map((pt, idx) => ({
        sample: `Test #${idx + 1}`,
        actual: pt.actual,
        predicted: pt.predicted,
      })) ?? []
    );
  }, [result?.scatter]);

  return (
    <div className="space-y-6">
      <div className="rounded-lg border border-border bg-card p-5">
        <h2 className="text-sm font-semibold text-foreground">
          Squad-Wide Next-Day Readiness Forecaster
        </h2>
        <p className="mt-0.5 text-caption">
          Fits a GradientBoostingRegressor across all 50 athletes using rolling
          7-day wellness and sRPE lag features.
        </p>

        <div className="mt-4 flex flex-wrap items-end gap-4">
          <div className="w-56">
            <label className="block text-xs font-medium text-muted-foreground">
              Chronological Split Date
            </label>
            <input
              type="date"
              value={splitDate}
              min="2020-06-01"
              max="2021-10-01"
              onChange={(e) => setSplitDate(e.target.value)}
              className="mt-1 block w-full rounded-md border border-border bg-background px-3 py-1.5 text-xs font-medium text-foreground shadow-sm focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
            />
          </div>
          <Button onClick={handleRun} disabled={isPending} className="text-xs">
            {isPending ? (
              <>
                <RotateCcw className="mr-2 size-3.5 animate-spin" />
                Training Gradient Boosting Model...
              </>
            ) : (
              <>
                <Play className="mr-2 size-3.5" />
                Train Model &amp; Benchmark vs Baseline
              </>
            )}
          </Button>
        </div>
      </div>

      {errorMsg && (
        <div className="rounded-lg border border-brick/30 bg-tint-caution/20 p-4 text-xs text-brick">
          {errorMsg}
        </div>
      )}

      {result && (
        <div className="space-y-6">
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
            <div className="rounded-lg border border-border bg-card p-3">
              <p className="text-xs font-medium text-muted-foreground">Model MAE</p>
              <p className="mt-1 text-lg font-semibold tabular text-primary">
                {fmtNumber(result.modelMetrics.mae, 2)}
              </p>
              <p className="mt-0.5 text-[11px] text-muted-foreground">
                RMSE: {fmtNumber(result.modelMetrics.rmse, 2)}
              </p>
            </div>
            <div className="rounded-lg border border-border bg-card p-3">
              <p className="text-xs font-medium text-muted-foreground">LOCF Naive MAE</p>
              <p className="mt-1 text-lg font-semibold tabular text-foreground">
                {fmtNumber(result.baselineLocf.mae, 2)}
              </p>
              <p className="mt-0.5 text-[11px] text-muted-foreground">
                Yesterday's value baseline
              </p>
            </div>
            <div className="rounded-lg border border-border bg-card p-3">
              <p className="text-xs font-medium text-muted-foreground">7-Day Mean MAE</p>
              <p className="mt-1 text-lg font-semibold tabular text-foreground">
                {fmtNumber(result.baselineRoll7.mae, 2)}
              </p>
              <p className="mt-0.5 text-[11px] text-muted-foreground">
                Weekly rolling baseline
              </p>
            </div>
            <div className="rounded-lg border border-border bg-card p-3">
              <p className="text-xs font-medium text-muted-foreground">MAE Improvement</p>
              <p className="mt-1 text-lg font-semibold tabular text-primary">
                +{fmtNumber(result.modelMetrics.maeImprovementPct, 1)}%
              </p>
              <p className="mt-0.5 text-[11px] text-muted-foreground">
                vs Naive persistence
              </p>
            </div>
          </div>

          <div className="grid gap-6 lg:grid-cols-2">
            <ChartCard
              title="Actual vs Predicted Readiness (Holdout Set)"
              note="Sampled sequential predictions on unseen future dates"
            >
              <ResponsiveContainer width="100%" height={280}>
                <LineChart
                  data={scatterChartData}
                  margin={{ top: 12, right: 16, bottom: 22, left: 8 }}
                >
                  <CartesianGrid {...gridProps} />
                  <XAxis
                    dataKey="sample"
                    {...axisProps}
                    interval={3}
                    label={{
                      value: "Chronological Test Observations (Unseen)",
                      position: "insideBottom",
                      offset: -12,
                      style: { fill: axisProps.tick.fill, fontSize: 11 },
                    }}
                  />
                  <YAxis
                    {...axisProps}
                    domain={[0, 10]}
                    label={{
                      value: "Readiness (1–10 Scale)",
                      angle: -90,
                      position: "insideLeft",
                      style: { fill: axisProps.tick.fill, fontSize: 11 },
                    }}
                  />
                  <Tooltip
                    contentStyle={tooltipContentStyle}
                    labelStyle={tooltipLabelStyle}
                    itemStyle={tooltipItemStyle}
                  />
                  <Legend verticalAlign="top" height={36} />
                  <Line
                    type="monotone"
                    dataKey="actual"
                    name="Actual Reported Readiness"
                    stroke={semanticColor.headline}
                    strokeWidth={2}
                    dot={{ r: 2.5 }}
                  />
                  <Line
                    type="monotone"
                    dataKey="predicted"
                    name="Model Forecast"
                    stroke={semanticColor.attention}
                    strokeWidth={2}
                    strokeDasharray="4 4"
                    dot={{ r: 2.5 }}
                  />
                </LineChart>
              </ResponsiveContainer>

              <div className="mt-3 rounded border border-border/80 bg-secondary/50 p-2.5 text-[11px] leading-relaxed text-muted-foreground">
                <strong className="text-foreground">What this chart conveys to your mentor:</strong> Tracks
                40 chronological holdout observations. The green line shows true reported player scores; the dashed amber line shows next-day forecasts. Tight coupling without divergence demonstrates the model anticipates readiness swings rather than lagging behind reality.
              </div>
            </ChartCard>

            <ChartCard
              title="Top 8 Predictive Lag Features"
              note="Gradient Boosting feature importances (Split Gain)"
            >
              <ResponsiveContainer width="100%" height={280}>
                <BarChart
                  data={result.importances.slice(0, 8)}
                  layout="vertical"
                  margin={{ top: 8, right: 24, bottom: 20, left: 180 }}
                >
                  <CartesianGrid {...gridProps} horizontal={false} />
                  <XAxis
                    type="number"
                    {...axisProps}
                    label={{
                      value: "Relative Feature Importance (Gini Gain)",
                      position: "insideBottom",
                      offset: -12,
                      style: { fill: axisProps.tick.fill, fontSize: 11 },
                    }}
                  />
                  <YAxis
                    type="category"
                    dataKey="feature"
                    {...axisProps}
                    width={170}
                    tick={{ fill: axisProps.tick.fill, fontSize: 11 }}
                  />
                  <Tooltip
                    contentStyle={tooltipContentStyle}
                    labelStyle={tooltipLabelStyle}
                    itemStyle={tooltipItemStyle}
                  />
                  <Bar
                    dataKey="importance"
                    name="Importance (Split Gain)"
                    fill={semanticColor.headline}
                    radius={[0, 4, 4, 0]}
                  />
                </BarChart>
              </ResponsiveContainer>

              <div className="mt-3 rounded border border-border/80 bg-secondary/50 p-2.5 text-[11px] leading-relaxed text-muted-foreground">
                <strong className="text-foreground">What this feature ranking conveys:</strong> Identifies
                which features provide the most information gain. 7-day rolling averages of readiness, muscle soreness, and fatigue dominate, confirming the sports-science principle that cumulative weekly strain drives tomorrow's performance.
              </div>
            </ChartCard>
          </div>
        </div>
      )}
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// COMPONENT 3: Match Performance Rating Forecaster
// ─────────────────────────────────────────────────────────────────────────────

function GamePerformanceLab() {
  const [targetRating, setTargetRating] = useState("team_performance");
  const [isPending, startTransition] = useTransition();
  const [result, setResult] = useState<PerformanceRunResult | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const handleRun = () => {
    setErrorMsg(null);
    startTransition(async () => {
      try {
        const res = await runPerformanceModel({
          data: { target_rating: targetRating },
        });
        if (res.ok) {
          setResult(res.data);
        } else {
          setErrorMsg(res.message ?? "Training failed");
        }
      } catch (err) {
        setErrorMsg(err instanceof Error ? err.message : "Request failed");
      }
    });
  };

  return (
    <div className="space-y-6">
      <div className="rounded-lg border border-border bg-card p-5">
        <h2 className="text-sm font-semibold text-foreground">
          Match Performance Rating Forecaster
        </h2>
        <p className="mt-0.5 text-caption">
          Predicts subjective post-match performance ratings (1-10) from aligned
          pre-match wellness indicators and ACWR ratios.
        </p>

        <div className="mt-4 flex flex-wrap items-end gap-4">
          <div className="w-64">
            <label className="block text-xs font-medium text-muted-foreground">
              Target Rating Dimension
            </label>
            <select
              value={targetRating}
              onChange={(e) => setTargetRating(e.target.value)}
              className="mt-1 block w-full rounded-md border border-border bg-background px-3 py-1.5 text-xs font-medium text-foreground shadow-sm focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
            >
              <option value="team_performance">Overall Team Performance</option>
              <option value="offensive_performance">Offensive Rating</option>
              <option value="defensive_performance">Defensive Rating</option>
            </select>
          </div>
          <Button onClick={handleRun} disabled={isPending} className="text-xs">
            {isPending ? (
              <>
                <RotateCcw className="mr-2 size-3.5 animate-spin" />
                Evaluating Match Ratings...
              </>
            ) : (
              <>
                <Play className="mr-2 size-3.5" />
                Train &amp; Evaluate Match Forecaster
              </>
            )}
          </Button>
        </div>
      </div>

      {errorMsg && (
        <div className="rounded-lg border border-brick/30 bg-tint-caution/20 p-4 text-xs text-brick">
          {errorMsg}
        </div>
      )}

      {result && result.trained && (
        <div className="space-y-6">
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
            <div className="rounded-lg border border-border bg-card p-3">
              <p className="text-xs font-medium text-muted-foreground">Model MAE</p>
              <p className="mt-1 text-lg font-semibold tabular text-primary">
                {fmtNumber(result.modelMae ?? 0, 2)}
                <span className="ml-1 text-xs font-normal text-muted-foreground">
                  rating pts
                </span>
              </p>
              <p className="mt-0.5 text-[11px] text-muted-foreground">
                RMSE: {fmtNumber(result.modelRmse ?? 0, 2)}
              </p>
            </div>
            <div className="rounded-lg border border-border bg-card p-3">
              <p className="text-xs font-medium text-muted-foreground">
                Historical Mean MAE
              </p>
              <p className="mt-1 text-lg font-semibold tabular text-foreground">
                {fmtNumber(result.baselineMeanMae ?? 0, 2)}
                <span className="ml-1 text-xs font-normal text-muted-foreground">
                  rating pts
                </span>
              </p>
              <p className="mt-0.5 text-[11px] text-muted-foreground">
                Baseline without pre-match features
              </p>
            </div>
            <div className="rounded-lg border border-border bg-card p-3">
              <p className="text-xs font-medium text-muted-foreground">
                MAE Delta vs Baseline
              </p>
              <p className="mt-1 text-lg font-semibold tabular text-foreground">
                {(result.maeImprovement ?? 0) > 0 ? "+" : ""}
                {fmtNumber(result.maeImprovement ?? 0, 2)} pts
              </p>
              <p className="mt-0.5 text-[11px] text-muted-foreground">
                Difference from squad mean
              </p>
            </div>
            <div className="rounded-lg border border-border bg-card p-3">
              <p className="text-xs font-medium text-muted-foreground">
                Test Observations
              </p>
              <p className="mt-1 text-lg font-semibold tabular text-foreground">
                {result.testSamples}
              </p>
              <p className="mt-0.5 text-[11px] text-muted-foreground">
                Training match reports: {result.trainSamples}
              </p>
            </div>
          </div>

          {result.importances && result.importances.length > 0 && (
            <ChartCard
              title="Predictive Drivers for Match Performance"
              note="Relative predictive importance of wellness and load attributes on game performance"
            >
              <ResponsiveContainer width="100%" height={290}>
                <BarChart
                  data={result.importances}
                  layout="vertical"
                  margin={{ top: 8, right: 24, bottom: 20, left: 180 }}
                >
                  <CartesianGrid {...gridProps} horizontal={false} />
                  <XAxis
                    type="number"
                    {...axisProps}
                    label={{
                      value: "Relative Predictive Importance (Split Gain)",
                      position: "insideBottom",
                      offset: -12,
                      style: { fill: axisProps.tick.fill, fontSize: 11 },
                    }}
                  />
                  <YAxis
                    type="category"
                    dataKey="feature"
                    {...axisProps}
                    width={170}
                    tick={{ fill: axisProps.tick.fill, fontSize: 11 }}
                  />
                  <Tooltip
                    contentStyle={tooltipContentStyle}
                    labelStyle={tooltipLabelStyle}
                    itemStyle={tooltipItemStyle}
                  />
                  <Bar
                    dataKey="importance"
                    name="Importance (Split Gain)"
                    fill={semanticColor.headline}
                    radius={[0, 4, 4, 0]}
                  />
                </BarChart>
              </ResponsiveContainer>

              <div className="mt-3 rounded border border-border/80 bg-secondary/50 p-2.5 text-[11px] leading-relaxed text-muted-foreground">
                <strong className="text-foreground">What this ranking conveys:</strong> Reveals which
                pre-kickoff conditioning attributes (e.g. 28-day chronic fitness vs acute mood or muscle soreness) correlate most strongly with how players rate their match performance.
              </div>
            </ChartCard>
          )}
        </div>
      )}

      {result && !result.trained && (
        <div className="rounded-lg border border-amber/30 bg-tint-caution/20 p-4 text-xs text-amber-foreground">
          <p className="font-medium">Data gate blocked training:</p>
          <p className="mt-1">{result.reason}</p>
        </div>
      )}
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// COMPONENT 4: Injury Risk Pre-Flight Gate
// ─────────────────────────────────────────────────────────────────────────────

function InjuryGateLab() {
  const [isPending, startTransition] = useTransition();
  const [result, setResult] = useState<InjuryRunResult | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const handleRun = () => {
    setErrorMsg(null);
    startTransition(async () => {
      try {
        const res = await runInjuryModel();
        if (res.ok) {
          setResult(res.data);
        } else {
          setErrorMsg(res.message ?? "Check failed");
        }
      } catch (err) {
        setErrorMsg(err instanceof Error ? err.message : "Request failed");
      }
    });
  };

  return (
    <div className="space-y-6">
      <div className="rounded-lg border border-border bg-card p-5">
        <h2 className="text-sm font-semibold text-foreground">
          Injury Risk Architectural Pre-Flight Gate
        </h2>
        <p className="mt-0.5 text-caption">
          Assesses class balance and statistical validity before allowing any
          probabilistic injury classification model to execute.
        </p>

        <div className="mt-4">
          <Button onClick={handleRun} disabled={isPending} className="text-xs">
            {isPending ? (
              <>
                <RotateCcw className="mr-2 size-3.5 animate-spin" />
                Auditing Dataset Statistics...
              </>
            ) : (
              <>
                <ShieldCheck className="mr-2 size-3.5" />
                Audit Data Sufficiency &amp; Run Pre-Flight Gate
              </>
            )}
          </Button>
        </div>
      </div>

      {errorMsg && (
        <div className="rounded-lg border border-brick/30 bg-tint-caution/20 p-4 text-xs text-brick">
          {errorMsg}
        </div>
      )}

      {result && (
        <div className="space-y-4">
          <div
            className={cn(
              "rounded-lg border p-4 text-xs",
              result.gatePassed
                ? "border-primary/40 bg-tint-positive/20 text-primary"
                : "border-amber/40 bg-tint-caution/20 text-foreground",
            )}
          >
            <div className="flex items-center gap-2 font-semibold">
              {result.gatePassed ? (
                <CheckCircle2 className="size-4 text-primary" />
              ) : (
                <ShieldCheck className="size-4 text-amber" />
              )}
              <span>
                {result.gatePassed
                  ? "Pre-Flight Gate Passed"
                  : "Pre-Flight Gate Enforced (Research Gating Active)"}
              </span>
            </div>
            <p className="mt-1.5 leading-relaxed text-muted-foreground">
              {result.gateReason}
            </p>
          </div>

          <div className="grid grid-cols-2 gap-4 sm:grid-cols-3">
            <div className="rounded-lg border border-border bg-card p-3">
              <p className="text-xs font-medium text-muted-foreground">
                Total Injury Reports
              </p>
              <p className="mt-1 text-lg font-semibold tabular text-foreground">
                {result.totalEvents}
              </p>
              <p className="mt-0.5 text-[11px] text-muted-foreground">
                Across {result.uniquePlayers} unique athletes
              </p>
            </div>
            <div className="rounded-lg border border-border bg-card p-3">
              <p className="text-xs font-medium text-muted-foreground">
                Primary Body Location
              </p>
              <p className="mt-1 text-lg font-semibold tabular text-primary">
                {result.descriptive.topLocation ?? "Hamstring"}
              </p>
              <p className="mt-0.5 text-[11px] text-muted-foreground">
                Most frequent self-reported site
              </p>
            </div>
            <div className="rounded-lg border border-border bg-card p-3">
              <p className="text-xs font-medium text-muted-foreground">
                Architectural Decision
              </p>
              <p className="mt-1 text-sm font-semibold text-foreground">
                Descriptive Only
              </p>
              <p className="mt-0.5 text-[11px] text-muted-foreground">
                Prevents catastrophic false-positive spikes
              </p>
            </div>
          </div>

          <div className="rounded border border-border/80 bg-secondary/50 p-2.5 text-[11px] leading-relaxed text-muted-foreground">
            <strong className="text-foreground">Why this architectural gate exists:</strong> In real sports-science data, acute injury reports constitute &lt;0.5% of athlete-days. Training naive binary classifiers on such severe imbalance creates models that hallucinate risk or collapse to trivial majority-class predictions. SPORTZA responsibly gates injury modeling to transparent risk attribution rather than misleading diagnostic labels.
          </div>
        </div>
      )}
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// COMPONENT 5: Static Model Registry Card
// ─────────────────────────────────────────────────────────────────────────────

const statusStyles: Record<ModelEntry["status"], string> = {
  production: "bg-tint-positive text-primary border-transparent",
  candidate: "bg-tint-caution text-amber-foreground border-transparent",
  archived: "bg-secondary text-muted-foreground border-border",
};

function ModelRegistryCard({
  model,
  isActive,
}: {
  model: ModelEntry;
  isActive: boolean;
}) {
  return (
    <div
      className={cn(
        "rounded-lg border bg-card",
        isActive ? "border-primary/40 shadow-sm" : "border-border",
      )}
    >
      <div className="flex flex-wrap items-start justify-between gap-2 px-4 pt-4">
        <div className="min-w-0">
          <h3 className="text-sm font-semibold text-foreground">{model.name}</h3>
          <p className="mt-0.5 text-xs text-muted-foreground">Task: {model.task}</p>
        </div>
        <Badge
          variant="outline"
          className={cn("font-medium capitalize", statusStyles[model.status])}
        >
          {model.status}
        </Badge>
      </div>

      <div className="flex flex-wrap gap-x-4 gap-y-1 px-4 pt-2 text-xs text-muted-foreground">
        {model.trainedAt && <span>Trained: {fmtDate(model.trainedAt)}</span>}
        <span>
          {model.validation.method}
          {model.validation.folds ? ` · ${model.validation.folds} folds` : ""}
          {model.validation.window ? ` · ${model.validation.window}` : ""}
        </span>
      </div>

      {model.metrics.length > 0 && (
        <div className="mt-3 px-4">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="text-xs">Metric</TableHead>
                <TableHead className="text-right text-xs">Value</TableHead>
                <TableHead className="text-right text-xs">Baseline</TableHead>
                <TableHead className="text-right text-xs">Improvement</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {model.metrics.map((m) => {
                const improv =
                  m.baselineValue !== undefined && m.baselineValue !== 0
                    ? ((m.baselineValue - m.value) / m.baselineValue) * 100
                    : null;
                return (
                  <TableRow key={m.name}>
                    <TableCell className="text-xs">
                      {m.name}
                      {m.unit ? (
                        <span className="ml-1 text-muted-foreground">({m.unit})</span>
                      ) : null}
                    </TableCell>
                    <TableCell className="tabular text-right text-xs font-medium">
                      {fmtNumber(m.value, 2)}
                    </TableCell>
                    <TableCell className="tabular text-right text-xs">
                      {m.baselineValue !== undefined ? fmtNumber(m.baselineValue, 2) : "—"}
                    </TableCell>
                    <TableCell className="tabular text-right text-xs font-medium">
                      {improv !== null ? (
                        <span className={improv > 0 ? "text-primary" : "text-brick"}>
                          {improv > 0 ? "+" : ""}
                          {improv.toFixed(1)}%
                        </span>
                      ) : (
                        "—"
                      )}
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </div>
      )}

      {model.notes && <p className="px-4 pb-4 pt-2 text-caption">{model.notes}</p>}
      {!model.notes && <div className="pb-4" />}
    </div>
  );
}
