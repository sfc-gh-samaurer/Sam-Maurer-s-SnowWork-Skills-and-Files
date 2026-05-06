import { NextResponse } from "next/server";
import { query, SIS_DISTRICT_SQL, multiFilterSql, pmToDistrictSql } from "@/lib/snowflake";
import { PS_ROLES, ACV_BANDS } from "@/lib/constants";

export const dynamic = "force-dynamic";

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const district = searchParams.get("district") || null;
  const region = searchParams.get("region") || null;
  const segment = searchParams.get("segment") || null;
  const pm = searchParams.get("pm") || null;

  try {
    let sql = `
      SELECT
        ACCOUNT_NAME, USE_CASE_NAME, PS_ENGAGEMENT,
        USE_CASE_ACV, SEGMENT, ARR
      FROM PST.PS_APPS_DEV.SDA_USE_CASES_CACHE
      WHERE ${SIS_DISTRICT_SQL}
    `;
    sql += multiFilterSql("DISTRICT", district);
    sql += multiFilterSql("REGION", region);
    sql += multiFilterSql("SEGMENT", segment);
    sql += pmToDistrictSql(pm);

    const rows = await query<{
      ACCOUNT_NAME: string;
      USE_CASE_NAME: string;
      PS_ENGAGEMENT: string;
      USE_CASE_ACV: number | null;
      SEGMENT: string;
      ARR: number | null;
    }>(sql);

    const psEngaged = rows.filter((r) =>
      PS_ROLES.includes(r.PS_ENGAGEMENT as any)
    );

    // --- Attach Rate by ACV Band ---
    const acvBands = ACV_BANDS.map((band) => {
      const inBand = rows.filter((r) => {
        const arr = r.ARR || 0;
        return arr >= band.min && arr < band.max;
      });
      const engaged = inBand.filter((r) =>
        PS_ROLES.includes(r.PS_ENGAGEMENT as any)
      );
      return {
        band: band.label,
        total: inBand.length,
        engaged: engaged.length,
        rate: inBand.length > 0 ? engaged.length / inBand.length : 0,
      };
    });

    // --- Attach Rate by Customer Segment ---
    const segmentCounts: Record<string, { total: number; engaged: number }> = {};
    for (const r of rows) {
      const seg = r.SEGMENT || "Unknown";
      if (!segmentCounts[seg]) segmentCounts[seg] = { total: 0, engaged: 0 };
      segmentCounts[seg].total++;
      if (PS_ROLES.includes(r.PS_ENGAGEMENT as any)) {
        segmentCounts[seg].engaged++;
      }
    }

    // Top 6 segments by account count
    const segments = Object.entries(segmentCounts)
      .sort((a, b) => b[1].total - a[1].total)
      .slice(0, 6)
      .map(([seg, counts]) => ({
        segment: seg,
        total: counts.total,
        engaged: counts.engaged,
        rate: counts.total > 0 ? counts.engaged / counts.total : 0,
      }));

    return NextResponse.json({ acvBands, segments });
  } catch (err: any) {
    console.error("Cohorts API error:", err.message);
    return NextResponse.json({ error: err.message }, { status: 500 });
  }
}
