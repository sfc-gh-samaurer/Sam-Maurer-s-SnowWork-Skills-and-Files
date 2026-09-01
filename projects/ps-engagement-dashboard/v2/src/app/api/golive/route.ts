import { NextResponse } from "next/server";
import { query, currentFYQuarter, dateToFYQuarterLabel, SIS_DISTRICT_SQL, multiFilterSql, pmToDistrictSql } from "@/lib/snowflake";
import { PS_ROLES } from "@/lib/constants";

export const dynamic = "force-dynamic";

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const district = searchParams.get("district") || null;
  const region = searchParams.get("region") || null;
  const segment = searchParams.get("segment") || null;
  const pm = searchParams.get("pm") || null;
  const quarter = searchParams.get("quarter") || null;

  try {
    const fyq = currentFYQuarter();

    let sql = `
      SELECT ACCOUNT_NAME, USE_CASE_NAME, PS_ENGAGEMENT,
             GO_LIVE_DATE, USE_CASE_STAGE
      FROM PST.PS_APPS_DEV.SDA_USE_CASES_CACHE
      WHERE PS_ENGAGEMENT IN (${PS_ROLES.map((r) => `'${r}'`).join(",")})
        AND ${SIS_DISTRICT_SQL}
    `;
    sql += multiFilterSql("DISTRICT", district);
    sql += multiFilterSql("REGION", region);
    sql += multiFilterSql("SEGMENT", segment);
    sql += pmToDistrictSql(pm);

    const rows = await query<{
      ACCOUNT_NAME: string;
      USE_CASE_NAME: string;
      PS_ENGAGEMENT: string;
      GO_LIVE_DATE: string | null;
      USE_CASE_STAGE: string | null;
    }>(sql);

    // Go-live readiness: derive quarter from GO_LIVE_DATE
    const qtrCounts: Record<string, number> = {};
    for (const r of rows) {
      const q = dateToFYQuarterLabel(r.GO_LIVE_DATE) || "Unscheduled";
      qtrCounts[q] = (qtrCounts[q] || 0) + 1;
    }

    const readiness = Object.entries(qtrCounts)
      .map(([quarter, count]) => ({ quarter, count }))
      .sort((a, b) => a.quarter.localeCompare(b.quarter));

    // Use selected quarters or current quarter for waterfall
    const selectedQtrs = quarter ? quarter.split(",").map(q => q.trim()) : [fyq.label];
    let currentQtrCount = 0;
    for (const q of selectedQtrs) {
      currentQtrCount += qtrCounts[q] || 0;
    }
    const qtrLabel = selectedQtrs.length === 1 ? selectedQtrs[0] : `${selectedQtrs.length} Qtrs`;

    const waterfall = [
      { label: "START", value: currentQtrCount, type: "start" as const },
      { label: "Moved Out", value: 0, type: "decrease" as const },
      { label: "Moved In", value: 0, type: "increase" as const },
      { label: `NET (${qtrLabel})`, value: currentQtrCount, type: "total" as const },
    ];

    return NextResponse.json({ readiness, waterfall, quarter: fyq });
  } catch (err: any) {
    console.error("GoLive API error:", err.message);
    return NextResponse.json({ error: err.message }, { status: 500 });
  }
}
