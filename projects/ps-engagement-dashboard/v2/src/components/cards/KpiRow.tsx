"use client";

import { Card, Badge } from "@tremor/react";
import type { KpiData } from "@/lib/constants";
import {
  ArrowTrendingUpIcon,
  PlusIcon,
  ChartBarIcon,
  UserGroupIcon,
  CalendarDaysIcon,
  ExclamationTriangleIcon,
  ShieldCheckIcon,
} from "@heroicons/react/24/outline";

const ICON_MAP: Record<string, React.ComponentType<{ className?: string }>> = {
  trending_up: ArrowTrendingUpIcon,
  add: PlusIcon,
  bar_chart: ChartBarIcon,
  people: UserGroupIcon,
  history: CalendarDaysIcon,
  warning: ExclamationTriangleIcon,
  shield: ShieldCheckIcon,
};

interface KpiCardProps {
  kpi: KpiData;
}

export function KpiCard({ kpi }: KpiCardProps) {
  const IconComponent = kpi.icon ? ICON_MAP[kpi.icon] : null;

  return (
    <Card className="ring-0 px-4 py-3">
      <div className="flex items-start justify-between gap-2">
        <div className="min-w-0 flex-1">
          <p className="text-crystalline-muted font-body text-[11px] leading-tight truncate">
            {kpi.label}
          </p>
          <p className="mt-1 text-xl font-headline font-extrabold text-crystalline-text leading-tight">
            {kpi.value}
          </p>
        </div>
        {IconComponent && (
          <div className="shrink-0 w-7 h-7 rounded-lg bg-crystalline-surface flex items-center justify-center">
            <IconComponent className="w-4 h-4 text-crystalline-primary" />
          </div>
        )}
      </div>
      <div className="mt-1.5 flex items-center gap-2 flex-wrap">
        {kpi.delta && kpi.deltaType && kpi.deltaType !== "neutral" && (
          <Badge
            color={kpi.deltaType === "increase" ? "green" : "red"}
            size="xs"
          >
            {kpi.delta}
          </Badge>
        )}
        {kpi.subtitle && (
          <p className="text-[10px] text-crystalline-muted truncate">
            {kpi.subtitle}
          </p>
        )}
      </div>
    </Card>
  );
}

interface KpiRowProps {
  kpis: KpiData[];
  loading?: boolean;
}

export function KpiRow({ kpis, loading }: KpiRowProps) {
  if (loading) {
    return (
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-3">
        {Array.from({ length: 7 }).map((_, i) => (
          <Card key={i} className="ring-0 animate-pulse px-4 py-3">
            <div className="h-3 w-16 bg-crystalline-border rounded mb-2" />
            <div className="h-6 w-20 bg-crystalline-border rounded" />
          </Card>
        ))}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-3">
      {kpis.map((kpi) => (
        <KpiCard key={kpi.label} kpi={kpi} />
      ))}
    </div>
  );
}
