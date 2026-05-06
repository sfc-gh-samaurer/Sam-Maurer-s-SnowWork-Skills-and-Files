"use client";

import { ResponsiveLine } from "@nivo/line";
import { CHART_COLORS } from "@/lib/constants";

interface EacvTrendProps {
  data: { date: string; eacv: number }[];
}

export function EacvTrendLine({ data }: EacvTrendProps) {
  const hasData = data.length >= 2;

  if (!hasData) {
    return (
      <div className="bg-white rounded-xl border border-crystalline-border p-5 shadow-card">
        <h3 className="font-headline font-bold text-sm text-crystalline-text mb-1">
          PS-Engaged EACV Trend (WoW)
        </h3>
        <div className="h-56 flex items-center justify-center">
          <p className="text-sm text-crystalline-muted italic">
            Available after 2+ weekly snapshots
          </p>
        </div>
      </div>
    );
  }

  const lineData = [
    {
      id: "EACV",
      data: data.map((d, i) => ({
        x: `WK ${String(i + 1).padStart(2, "0")}`,
        y: d.eacv / 1_000_000, // Display in $M
      })),
    },
  ];

  return (
    <div className="bg-white rounded-xl border border-crystalline-border p-5 shadow-card">
      <h3 className="font-headline font-bold text-sm text-crystalline-text mb-1">
        PS-Engaged EACV Trend (WoW)
      </h3>
      <p className="text-xs text-crystalline-muted mb-4">
        {data.length} week trend
      </p>
      <div className="h-56">
        <ResponsiveLine
          data={lineData}
          margin={{ top: 10, right: 20, bottom: 40, left: 55 }}
          xScale={{ type: "point" }}
          yScale={{ type: "linear", min: "auto", max: "auto" }}
          curve="monotoneX"
          colors={[CHART_COLORS.accent]}
          lineWidth={3}
          pointSize={8}
          pointColor={CHART_COLORS.accent}
          pointBorderWidth={2}
          pointBorderColor="#ffffff"
          enableArea={true}
          areaBaselineValue={Math.min(...data.map((d) => d.eacv / 1_000_000)) * 0.95}
          areaOpacity={0.08}
          axisBottom={{
            tickSize: 0,
            tickPadding: 8,
          }}
          axisLeft={{
            tickSize: 0,
            tickPadding: 8,
            format: (v) => `$${v}M`,
          }}
          enableGridX={false}
          theme={{
            text: { fontFamily: "Inter, system-ui, sans-serif", fontSize: 11 },
            grid: { line: { stroke: "#E2E8F0", strokeWidth: 1 } },
            axis: { ticks: { text: { fill: "#5A6578" } } },
            crosshair: { line: { stroke: CHART_COLORS.primary, strokeWidth: 1 } },
          }}
          tooltip={({ point }) => (
            <div className="bg-white shadow-lg rounded-lg px-3 py-2 text-xs border border-crystalline-border">
              <strong>{point.data.xFormatted}</strong>: ${String(point.data.yFormatted)}M
            </div>
          )}
        />
      </div>
    </div>
  );
}
