import { NextResponse } from "next/server";
import { query, SIS_DISTRICT_SQL, PRACTICE_MANAGERS, currentFYQuarter } from "@/lib/snowflake";

export const dynamic = "force-dynamic";

export async function GET() {
  try {
    // Only return filter values for rows within SiS district scope
    const [regions, segments, districts] = await Promise.all([
      query<{ REGION: string }>(`
        SELECT DISTINCT REGION
        FROM PST.PS_APPS_DEV.SDA_USE_CASES_CACHE
        WHERE REGION IS NOT NULL AND REGION != ''
          AND ${SIS_DISTRICT_SQL}
        ORDER BY REGION
      `),
      query<{ SEGMENT: string }>(`
        SELECT DISTINCT SEGMENT
        FROM PST.PS_APPS_DEV.SDA_USE_CASES_CACHE
        WHERE SEGMENT IS NOT NULL AND SEGMENT != ''
          AND ${SIS_DISTRICT_SQL}
        ORDER BY SEGMENT
      `),
      query<{ DISTRICT: string }>(`
        SELECT DISTINCT DISTRICT
        FROM PST.PS_APPS_DEV.SDA_USE_CASES_CACHE
        WHERE DISTRICT IS NOT NULL AND DISTRICT != ''
          AND ${SIS_DISTRICT_SQL}
        ORDER BY DISTRICT
      `),
    ]);

    // Build quarter options: current quarter ± 2
    const fyq = currentFYQuarter();
    const quarters: string[] = [];
    for (let offset = -2; offset <= 2; offset++) {
      let q = fyq.quarter + offset;
      let fy = fyq.fy;
      while (q < 1) { q += 4; fy--; }
      while (q > 4) { q -= 4; fy++; }
      quarters.push(`Q${q} FY${fy % 100}`);
    }

    return NextResponse.json({
      regions: regions.map((r) => r.REGION),
      segments: segments.map((s) => s.SEGMENT),
      districts: districts.map((d) => d.DISTRICT),
      practiceManagers: PRACTICE_MANAGERS,
      quarters,
      currentQuarter: fyq.label,
    });
  } catch (err: any) {
    console.error("Filters API error:", err.message);
    return NextResponse.json({ error: err.message }, { status: 500 });
  }
}
