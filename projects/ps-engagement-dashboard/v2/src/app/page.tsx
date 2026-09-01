"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import { Card, Badge } from "@tremor/react";
import { KpiRow } from "@/components/cards/KpiRow";
import { AttachRateBar } from "@/components/charts/AttachRateBar";
import { EacvTrendLine } from "@/components/charts/EacvTrendLine";
import { WaterfallChart } from "@/components/charts/WaterfallChart";
import { EngagementTypeTable } from "@/components/tables/EngagementTypeTable";
import { OpportunityTable } from "@/components/tables/OpportunityTable";
import { RiskTable, DistrictTable } from "@/components/tables/DetailTables";
import type { KpiData, WaterfallPoint } from "@/lib/constants";
import {
  FunnelIcon,
  ChevronDownIcon,
  MagnifyingGlassIcon,
  BellIcon,
  Cog6ToothIcon,
  XMarkIcon,
} from "@heroicons/react/24/outline";

/* ------------------------------------------------------------------ */
/*  Types                                                              */
/* ------------------------------------------------------------------ */

interface Filters {
  quarter: string[];
  region: string[];
  district: string[];
  segment: string[];
  pm: string[];
}

interface FilterOptions {
  quarters: string[];
  currentQuarter: string;
  regions: string[];
  districts: string[];
  segments: string[];
  practiceManagers: string[];
}

interface EngagementType {
  type: string;
  useCases: number;
  eacv: number;
  eacvFormatted: string;
  attachRate: number;
  attachRateFormatted: string;
  topWorkloads: string;
  activity: string;
}

interface Opportunity {
  account: string;
  useCase: string;
  stage: string;
  eacv: number;
  eacvFormatted: string;
  pattern: string;
}

interface DashboardState {
  kpis: KpiData[];
  quarter: { fy: number; quarter: number; label: string } | null;
  acvBands: { band: string; rate: number; engaged: number; total: number }[];
  segments: { segment: string; rate: number; engaged: number; total: number }[];
  trend: { date: string; eacv: number }[];
  waterfall: WaterfallPoint[];
  districts: { district: string; engagedPct: number; eacv: number; ucCount: number; totalUcs: number }[];
  risks: { account: string; project: string; issue: string; action: string }[];
  engagementTypes: EngagementType[];
  opportunities: Opportunity[];
  opportunityTotal: number;
  loading: boolean;
}

const EMPTY_FILTERS: Filters = {
  quarter: [],
  region: [],
  district: [],
  segment: [],
  pm: [],
};

/* ------------------------------------------------------------------ */
/*  Multi-Select Dropdown                                              */
/* ------------------------------------------------------------------ */

function MultiSelect({
  label,
  selected,
  options,
  onChange,
}: {
  label: string;
  selected: string[];
  options: string[];
  onChange: (v: string[]) => void;
}) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  // Close on outside click
  useEffect(() => {
    function handler(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    }
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  const toggle = (val: string) => {
    if (selected.includes(val)) {
      onChange(selected.filter((v) => v !== val));
    } else {
      onChange([...selected, val]);
    }
  };

  const displayText =
    selected.length === 0
      ? "All"
      : selected.length <= 2
        ? selected.join(", ")
        : `${selected.length} selected`;

  return (
    <div ref={ref} className="relative">
      <label className="block text-xs font-medium text-crystalline-text mb-1">
        {label}
      </label>
      <button
        type="button"
        onClick={() => setOpen(!open)}
        className="w-full text-sm border border-crystalline-border rounded-lg px-3 py-2 bg-white text-crystalline-text focus:outline-none focus:ring-2 focus:ring-crystalline-accent text-left flex items-center justify-between"
      >
        <span className="truncate">{displayText}</span>
        <ChevronDownIcon className={`w-4 h-4 text-crystalline-muted transition-transform shrink-0 ${open ? "rotate-180" : ""}`} />
      </button>
      {open && (
        <div className="absolute z-50 mt-1 w-full bg-white border border-crystalline-border rounded-lg shadow-lg max-h-56 overflow-y-auto">
          {selected.length > 0 && (
            <button
              type="button"
              onClick={() => onChange([])}
              className="w-full text-left px-3 py-1.5 text-xs text-crystalline-accent hover:bg-crystalline-surface flex items-center gap-1 border-b border-crystalline-border"
            >
              <XMarkIcon className="w-3 h-3" /> Clear all
            </button>
          )}
          {options.map((opt) => (
            <label
              key={opt}
              className="flex items-center gap-2 px-3 py-1.5 text-sm hover:bg-crystalline-surface cursor-pointer"
            >
              <input
                type="checkbox"
                checked={selected.includes(opt)}
                onChange={() => toggle(opt)}
                className="rounded border-crystalline-border text-crystalline-primary focus:ring-crystalline-accent h-3.5 w-3.5"
              />
              <span className="truncate">{opt}</span>
            </label>
          ))}
          {options.length === 0 && (
            <p className="px-3 py-2 text-xs text-crystalline-muted">No options</p>
          )}
        </div>
      )}
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  Sidebar                                                            */
/* ------------------------------------------------------------------ */

function Sidebar({
  filters,
  setFilters,
  filterOptions,
  onApply,
}: {
  filters: Filters;
  setFilters: React.Dispatch<React.SetStateAction<Filters>>;
  filterOptions: FilterOptions;
  onApply: () => void;
}) {
  const totalActive = filters.quarter.length + filters.region.length +
    filters.district.length + filters.segment.length + filters.pm.length;

  return (
    <aside className="w-64 min-h-screen bg-white border-r border-crystalline-border flex flex-col shrink-0">
      {/* Brand */}
      <div className="px-5 py-5 border-b border-crystalline-border">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-crystalline-primary flex items-center justify-center">
            <span className="text-white text-xs font-bold">PS</span>
          </div>
          <div>
            <p className="font-headline font-extrabold text-sm text-crystalline-text leading-tight">
              PS Leadership
            </p>
            <p className="text-[10px] text-crystalline-muted">
              Engagement Analytics
            </p>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="px-5 py-4 flex-1 space-y-3 overflow-y-auto">
        <p className="text-[10px] font-semibold uppercase tracking-wider text-crystalline-muted">
          Filters {totalActive > 0 && <span className="text-crystalline-accent">({totalActive})</span>}
        </p>

        {/* Quarter */}
        <MultiSelect
          label="Quarter"
          selected={filters.quarter}
          options={filterOptions.quarters}
          onChange={(v) => setFilters((f) => ({ ...f, quarter: v }))}
        />

        {/* Region */}
        <MultiSelect
          label="Region"
          selected={filters.region}
          options={filterOptions.regions}
          onChange={(v) => setFilters((f) => ({ ...f, region: v }))}
        />

        {/* District */}
        <MultiSelect
          label="District"
          selected={filters.district}
          options={filterOptions.districts}
          onChange={(v) => setFilters((f) => ({ ...f, district: v }))}
        />

        {/* Customer Segment */}
        <MultiSelect
          label="Customer Segment"
          selected={filters.segment}
          options={filterOptions.segments}
          onChange={(v) => setFilters((f) => ({ ...f, segment: v }))}
        />

        {/* Practice Manager */}
        <MultiSelect
          label="Practice Manager"
          selected={filters.pm}
          options={filterOptions.practiceManagers}
          onChange={(v) => setFilters((f) => ({ ...f, pm: v }))}
        />

        <button
          onClick={onApply}
          className="w-full mt-2 px-4 py-2 bg-crystalline-primary text-white text-sm font-semibold rounded-lg hover:bg-opacity-90 transition-colors flex items-center justify-center gap-2"
        >
          <FunnelIcon className="w-4 h-4" />
          Apply Filters
        </button>

        {totalActive > 0 && (
          <button
            onClick={() => {
              setFilters({ ...EMPTY_FILTERS });
            }}
            className="w-full px-4 py-1.5 text-xs text-crystalline-muted hover:text-crystalline-text transition-colors flex items-center justify-center gap-1"
          >
            <XMarkIcon className="w-3 h-3" /> Reset All
          </button>
        )}
      </div>
    </aside>
  );
}

/* ------------------------------------------------------------------ */
/*  Helpers                                                            */
/* ------------------------------------------------------------------ */

function currentQuarterLabel(): string {
  const now = new Date();
  const month = now.getMonth() + 1;
  const year = now.getFullYear();
  let fy: number, q: number;
  if (month >= 2 && month <= 4) { q = 1; fy = year + 1; }
  else if (month >= 5 && month <= 7) { q = 2; fy = year + 1; }
  else if (month >= 8 && month <= 10) { q = 3; fy = year + 1; }
  else { q = 4; fy = month >= 11 ? year + 2 : year + 1; }
  return `Q${q} FY${fy % 100}`;
}

/* ------------------------------------------------------------------ */
/*  Main Dashboard                                                     */
/* ------------------------------------------------------------------ */

export default function Dashboard() {
  const [filters, setFilters] = useState<Filters>({ ...EMPTY_FILTERS });
  const [appliedFilters, setAppliedFilters] = useState<Filters>({ ...EMPTY_FILTERS });
  const [filterOptions, setFilterOptions] = useState<FilterOptions>({
    quarters: [],
    currentQuarter: "",
    regions: [],
    districts: [],
    segments: [],
    practiceManagers: [],
  });
  const [state, setState] = useState<DashboardState>({
    kpis: [],
    quarter: null,
    acvBands: [],
    segments: [],
    trend: [],
    waterfall: [],
    districts: [],
    risks: [],
    engagementTypes: [],
    opportunities: [],
    opportunityTotal: 0,
    loading: true,
  });
  const [povExpanded, setPovExpanded] = useState(false);

  // Load filter options once
  useEffect(() => {
    fetch("/api/filters")
      .then((r) => r.json())
      .then((data) => {
        setFilterOptions({
          quarters: data.quarters || [],
          currentQuarter: data.currentQuarter || "",
          regions: data.regions || [],
          districts: data.districts || [],
          segments: data.segments || [],
          practiceManagers: data.practiceManagers || [],
        });
      })
      .catch(console.error);
  }, []);

  const fetchData = useCallback(async () => {
    setState((s) => ({ ...s, loading: true }));
    const params = new URLSearchParams();
    if (appliedFilters.quarter.length > 0) params.set("quarter", appliedFilters.quarter.join(","));
    if (appliedFilters.district.length > 0) params.set("district", appliedFilters.district.join(","));
    if (appliedFilters.region.length > 0) params.set("region", appliedFilters.region.join(","));
    if (appliedFilters.segment.length > 0) params.set("segment", appliedFilters.segment.join(","));
    if (appliedFilters.pm.length > 0) params.set("pm", appliedFilters.pm.join(","));
    const qs = params.toString() ? `?${params.toString()}` : "";

    try {
      const [kpiRes, cohortRes, trendRes, goliveRes, districtRes, riskRes, engTypeRes, oppRes] =
        await Promise.all([
          fetch(`/api/kpis${qs}`),
          fetch(`/api/cohorts${qs}`),
          fetch(`/api/trends`),
          fetch(`/api/golive${qs}`),
          fetch(`/api/districts${qs}`),
          fetch(`/api/risk${qs}`),
          fetch(`/api/engagement-types${qs}`),
          fetch(`/api/opportunities${qs}`),
        ]);

      const [kpiData, cohortData, trendData, goliveData, districtData, riskData, engTypeData, oppData] =
        await Promise.all([
          kpiRes.json(),
          cohortRes.json(),
          trendRes.json(),
          goliveRes.json(),
          districtRes.json(),
          riskRes.json(),
          engTypeRes.json(),
          oppRes.json(),
        ]);

      setState({
        kpis: kpiData.kpis || [],
        quarter: kpiData.quarter || null,
        acvBands: cohortData.acvBands || [],
        segments: cohortData.segments || [],
        trend: trendData.trend || [],
        waterfall: goliveData.waterfall || [],
        districts: districtData.districts || [],
        risks: riskData.risks || [],
        engagementTypes: engTypeData.engagementTypes || [],
        opportunities: oppData.opportunities || [],
        opportunityTotal: oppData.total || 0,
        loading: false,
      });
    } catch (err) {
      console.error("Failed to fetch dashboard data:", err);
      setState((s) => ({ ...s, loading: false }));
    }
  }, [appliedFilters]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleApply = () => {
    setAppliedFilters({ ...filters });
  };

  // Build active filter label for header
  const filterParts: string[] = [];
  if (appliedFilters.quarter.length > 0) filterParts.push(appliedFilters.quarter.join(", "));
  if (appliedFilters.region.length > 0) filterParts.push(appliedFilters.region.join(", "));
  if (appliedFilters.district.length > 0) filterParts.push(`${appliedFilters.district.length} district${appliedFilters.district.length > 1 ? "s" : ""}`);
  if (appliedFilters.segment.length > 0) filterParts.push(appliedFilters.segment.join(", "));
  if (appliedFilters.pm.length > 0) filterParts.push(`PM: ${appliedFilters.pm.join(", ")}`);
  const activeFilterLabel = filterParts.length > 0 ? filterParts.join(" | ") : "All Districts";

  return (
    <div className="flex min-h-screen bg-crystalline-surface">
      {/* Left Sidebar */}
      <Sidebar
        filters={filters}
        setFilters={setFilters}
        filterOptions={filterOptions}
        onApply={handleApply}
      />

      {/* Main Content */}
      <main className="flex-1 min-w-0">
        {/* Header */}
        <header className="bg-white border-b border-crystalline-border px-6 py-3 sticky top-0 z-10">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="font-headline font-extrabold text-lg text-crystalline-text">
                PS Engagement & Go-Live Dashboard
              </h1>
              <p className="text-xs text-crystalline-muted">
                {activeFilterLabel} | {state.quarter?.label || "..."} |{" "}
                {new Date().toLocaleDateString("en-US", {
                  month: "long",
                  day: "numeric",
                  year: "numeric",
                })}
              </p>
            </div>
            <div className="flex items-center gap-3 text-crystalline-muted">
              <MagnifyingGlassIcon className="w-5 h-5 cursor-pointer hover:text-crystalline-text" />
              <BellIcon className="w-5 h-5 cursor-pointer hover:text-crystalline-text" />
              <Cog6ToothIcon className="w-5 h-5 cursor-pointer hover:text-crystalline-text" />
            </div>
          </div>
        </header>

        <div className="px-6 py-5 space-y-5">
          {/* Row 1: KPI Cards */}
          <KpiRow kpis={state.kpis} loading={state.loading} />

          {/* Row 2: Cohort Charts (2x2 grid) */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <AttachRateBar
              data={state.acvBands}
              title="Attach Rate by ACV Band"
              indexKey="band"
            />
            <AttachRateBar
              data={state.segments.map((s) => ({
                band: s.segment,
                rate: s.rate,
                engaged: s.engaged,
                total: s.total,
              }))}
              title="Attach Rate by Customer Segment"
              indexKey="band"
            />
            <EacvTrendLine data={state.trend} />
            <WaterfallChart data={state.waterfall} />
          </div>

          {/* Row 3: PS Impact by Engagement Type */}
          <EngagementTypeTable
            data={state.engagementTypes}
            loading={state.loading}
          />

          {/* Row 4: Regional Thematic POV (expandable) */}
          <Card className="ring-0">
            <button
              onClick={() => setPovExpanded(!povExpanded)}
              className="flex items-center justify-between w-full"
            >
              <h3 className="font-headline font-bold text-sm text-crystalline-text flex items-center gap-2">
                <span className="text-crystalline-accent">&#x2728;</span>
                Regional Thematic POV
              </h3>
              <ChevronDownIcon
                className={`w-5 h-5 text-crystalline-muted transition-transform ${
                  povExpanded ? "rotate-180" : ""
                }`}
              />
            </button>
            {povExpanded && (
              <div className="mt-4 p-4 bg-crystalline-surface rounded-lg">
                <p className="text-sm text-crystalline-muted italic">
                  Regional thematic narratives loaded from engagement themes
                  cache. AI-generated insights available after theme
                  accumulation.
                </p>
              </div>
            )}
          </Card>

          {/* Row 5: Engagement Opportunity */}
          <OpportunityTable
            data={state.opportunities}
            total={state.opportunityTotal}
            loading={state.loading}
          />

          {/* Row 6: Delivery Risk & Action */}
          <RiskTable risks={state.risks} loading={state.loading} />

          {/* Row 7: District Breakdown (footer) */}
          <DistrictTable
            districts={state.districts}
            loading={state.loading}
          />
        </div>
      </main>
    </div>
  );
}
