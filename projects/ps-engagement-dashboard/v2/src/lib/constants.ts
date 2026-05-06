// PS Engagement role definitions — matches v1 Streamlit logic
export const PS_ROLES = [
  "Implementation",
  "Advisory",
  "Proposing",
  "Support",
  "Resident",
] as const;

export type PSRole = (typeof PS_ROLES)[number];

// ACV band definitions for cohort analytics
export const ACV_BANDS = [
  { label: "< 50K", min: 0, max: 50_000 },
  { label: "50K-250K", min: 50_000, max: 250_000 },
  { label: "250K-1M", min: 250_000, max: 1_000_000 },
  { label: "1M+", min: 1_000_000, max: Infinity },
] as const;

// Crystalline Lab color palette for charts
export const CHART_COLORS = {
  primary: "#006686",
  accent: "#29B5E8",
  muted: "#5A6578",
  success: "#10B981",
  warning: "#F59E0B",
  danger: "#EF4444",
  // Series palette for multi-bar charts
  series: [
    "#006686",
    "#29B5E8",
    "#94A3B8",
    "#10B981",
    "#F59E0B",
    "#8B5CF6",
  ],
} as const;

// KPI card types
export interface KpiData {
  label: string;
  value: string;
  delta?: string;
  deltaType?: "increase" | "decrease" | "neutral";
  icon?: string;
  subtitle?: string;
}

// District data
export interface DistrictData {
  district: string;
  engagedPct: number;
  eacv: number;
  ucCount: number;
}

// Use case row from Snowflake (matches DESCRIBE TABLE SDA_USE_CASES_CACHE)
export interface UseCase {
  ACCOUNT_NAME: string;
  USE_CASE_NAME: string;
  USE_CASE_STAGE: string | null;
  PS_ENGAGEMENT: string;
  USE_CASE_ACV: number | null;
  IS_PS_ENGAGED: boolean | null;
  IMPLEMENTER: string | null;
  WORKLOADS: string | null;
  DISTRICT: string;
  REGION: string;
  SUB_REGION: string | null;
  TERRITORY: string | null;
  SEGMENT: string;
  INDUSTRY: string;
  ARR: number | null;
  ACCOUNT_TIER: string;
  GO_LIVE_DATE: string | null;
  DAYS_IN_STAGE: number | null;
}

// Waterfall data point for Go-Live Quarter Movement
export interface WaterfallPoint {
  label: string;
  value: number;
  type: "start" | "increase" | "decrease" | "total";
}

// Risk row
export interface RiskRow {
  account: string;
  project: string;
  issue: string;
  action: string;
}
