import {
  Activity,
  FlaskConical,
  HeartPulse,
  LayoutDashboard,
  Stethoscope,
  TrendingUp,
  Trophy,
  Users,
  UsersRound,
  Waypoints,
} from "lucide-react";
import type { LucideIcon } from "lucide-react";

export interface NavItem {
  to: string;
  label: string;
  icon: LucideIcon;
  /** Exact matching avoids "/" matching every route. */
  exact?: boolean;
  description: string;
}

export const navItems: NavItem[] = [
  {
    to: "/",
    label: "Overview",
    icon: LayoutDashboard,
    exact: true,
    description: "Dataset summary and current athlete/team state",
  },
  {
    to: "/athletes",
    label: "Athletes",
    icon: Users,
    description: "Roster, profiles and longitudinal trends",
  },
  {
    to: "/readiness",
    label: "Recovery Planner",
    icon: HeartPulse,
    description: "Readiness context and recovery guidance",
  },
  {
    to: "/workload",
    label: "Training Workload",
    icon: Activity,
    description: "sRPE trends and acute/chronic load",
  },
  {
    to: "/injuries",
    label: "Injury Research",
    icon: Stethoscope,
    description: "Injury records, severity and body locations",
  },
  {
    to: "/forecast",
    label: "Performance Forecast",
    icon: TrendingUp,
    description: "Actual vs predicted performance",
  },
  {
    to: "/team",
    label: "Team Analysis",
    icon: Trophy,
    description: "Position-grouped comparisons",
  },
  {
    to: "/correlations",
    label: "Correlation Lab",
    icon: Waypoints,
    description: "Associations between tracking variables",
  },
  {
    to: "/models",
    label: "Model Evaluation",
    icon: FlaskConical,
    description: "Model selection, validation and diagnostics",
  },
];

export const icon = { UsersRound, Activity };
