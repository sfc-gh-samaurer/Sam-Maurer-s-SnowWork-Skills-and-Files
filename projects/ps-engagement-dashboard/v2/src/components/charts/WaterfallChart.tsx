"use client";

import { ResponsiveBar } from "@nivo/bar";
import { CHART_COLORS } from "@/lib/constants";
import type { WaterfallPoint } from "@/lib/constants";

interface WaterfallChartProps {
  data: WaterfallPoint[];
}

export function WaterfallChart({ data }: WaterfallChartProps) {
  // Transform waterfall data into stacked bar format
  // Each bar has: invisible base + visible portion
  let runningTotal = 0;
  const chartData = data.map((d) => {
    if (d.type === "start" || d.type === "total") {
      const item = {
        label: d.label,
        base: 0,
        value: d.value,
      };
      runningTotal = d.value;
      return item;
    } else if (d.type === "decrease") {
      runningTotal -= Math.abs(d.value);
      return {
        label: d.label,
        base: runningTotal,
        value: Math.abs(d.value),
      };
    } else {
      // increase
      const item = {
        label: d.label,
        base: runningTotal,
        value: d.value,
      };
      runningTotal += d.value;
      return item;
    }
  });

  const colorMap: Record<string, string> = {};
  data.forEach((d) => {
    if (d.type === "start") colorMap[d.label] = CHART_COLORS.primary;
    else if (d.type === "decrease") colorMap[d.label] = CHART_COLORS.danger;
    else if (d.type === "increase") colorMap[d.label] = CHART_COLORS.success;
    else colorMap[d.label] = CHART_COLORS.accent;
  });

  return (
    <div className="bg-white rounded-xl border border-crystalline-border p-5 shadow-card">
      <h3 className="font-headline font-bold text-sm text-crystalline-text mb-4">
        Go-Live Quarter Movement
      </h3>
      <div className="h-56">
        <ResponsiveBar
          data={chartData}
          keys={["base", "value"]}
          indexBy="label"
          margin={{ top: 10, right: 20, bottom: 40, left: 50 }}
          padding={0.35}
          valueScale={{ type: "linear" }}
          colors={({ id, data: d }) => {
            if (id === "base") return "transparent";
            return colorMap[d.label as string] || CHART_COLORS.primary;
          }}
          borderRadius={4}
          axisBottom={{
            tickSize: 0,
            tickPadding: 8,
          }}
          axisLeft={{
            tickSize: 0,
            tickPadding: 8,
          }}
          enableLabel={true}
          label={({ id, value }) => (id === "base" ? "" : String(value))}
          labelTextColor="#ffffff"
          labelSkipWidth={20}
          enableGridY={true}
          theme={{
            text: { fontFamily: "Inter, system-ui, sans-serif", fontSize: 11 },
            grid: { line: { stroke: "#E2E8F0", strokeWidth: 1 } },
            axis: { ticks: { text: { fill: "#5A6578" } } },
          }}
          tooltip={({ id, value, indexValue }) => {
            if (id === "base") return null;
            return (
              <div className="bg-white shadow-lg rounded-lg px-3 py-2 text-xs border border-crystalline-border">
                <strong>{indexValue}</strong>: {value}
              </div>
            );
          }}
        />
      </div>
    </div>
  );
}
