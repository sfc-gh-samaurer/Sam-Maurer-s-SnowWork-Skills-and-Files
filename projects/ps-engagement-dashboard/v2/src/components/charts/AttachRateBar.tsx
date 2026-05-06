"use client";

import { ResponsiveBar } from "@nivo/bar";
import { CHART_COLORS } from "@/lib/constants";

interface AttachRateBarProps {
  data: { band: string; rate: number; engaged: number; total: number }[];
  title: string;
  indexKey: string;
}

export function AttachRateBar({ data, title, indexKey }: AttachRateBarProps) {
  const chartData = data.map((d) => ({
    [indexKey]: (d as any)[indexKey] || (d as any).band || (d as any).segment,
    "Current": +(d.rate * 100).toFixed(1),
  }));

  return (
    <div className="bg-white rounded-xl border border-crystalline-border p-5 shadow-card">
      <h3 className="font-headline font-bold text-sm text-crystalline-text mb-1">
        {title}
      </h3>
      <p className="text-xs text-crystalline-muted mb-4">Target: 20%</p>
      <div className="h-56">
        <ResponsiveBar
          data={chartData}
          keys={["Current"]}
          indexBy={indexKey}
          margin={{ top: 10, right: 20, bottom: 40, left: 50 }}
          padding={0.4}
          valueScale={{ type: "linear" }}
          colors={[CHART_COLORS.primary]}
          borderRadius={4}
          axisBottom={{
            tickSize: 0,
            tickPadding: 8,
            tickRotation: -20,
          }}
          axisLeft={{
            tickSize: 0,
            tickPadding: 8,
            format: (v) => `${v}%`,
          }}
          labelFormat={(v) => `${v}%`}
          labelSkipWidth={20}
          labelTextColor="#ffffff"
          enableGridY={true}
          gridYValues={[0, 10, 20, 30, 40]}
          markers={[
            {
              axis: "y",
              value: 20,
              lineStyle: {
                stroke: CHART_COLORS.warning,
                strokeWidth: 2,
                strokeDasharray: "6 4",
              },
              legend: "Target",
              legendPosition: "top-right",
              textStyle: {
                fill: CHART_COLORS.warning,
                fontSize: 11,
              },
            },
          ]}
          theme={{
            text: { fontFamily: "Inter, system-ui, sans-serif", fontSize: 11 },
            grid: { line: { stroke: "#E2E8F0", strokeWidth: 1 } },
            axis: { ticks: { text: { fill: "#5A6578" } } },
          }}
          tooltip={({ id, value, indexValue }) => (
            <div className="bg-white shadow-lg rounded-lg px-3 py-2 text-xs border border-crystalline-border">
              <strong>{indexValue}</strong>: {value}%
            </div>
          )}
        />
      </div>
    </div>
  );
}
