import { NextResponse } from "next/server";
import { query, fmtAcv, SIS_DISTRICT_SQL, multiFilterSql, pmToDistrictSql } from "@/lib/snowflake";
import { PS_ROLES } from "@/lib/constants";

export const dynamic = "force-dynamic";

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const district = searchParams.get("district") || null;
  const region = searchParams.get("region") || null;
  const segment = searchParams.get("segment") || null;
  const pm = searchParams.get("pm") || null;
  const limit = parseInt(searchParams.get("limit") || "20", 10);

  try {
    const psRolesIn = PS_ROLES.map((r) => `'${r}'`).join(",");
    const filterSql = multiFilterSql("DISTRICT", district)
      + multiFilterSql("REGION", region)
      + multiFilterSql("SEGMENT", segment)
      + pmToDistrictSql(pm);

    let sql = `
      SELECT ACCOUNT_NAME, USE_CASE_NAME, SEGMENT,
             USE_CASE_ACV, DISTRICT, REGION,
             PS_ENGAGEMENT, USE_CASE_STAGE
      FROM PST.PS_APPS_DEV.SDA_USE_CASES_CACHE
      WHERE (PS_ENGAGEMENT NOT IN (${psRolesIn}) OR PS_ENGAGEMENT IS NULL)
        AND USE_CASE_ACV > 0
        AND ${SIS_DISTRICT_SQL}
        ${filterSql}
      ORDER BY USE_CASE_ACV DESC NULLS LAST LIMIT ${limit}
    `;

    const countSql = `
      SELECT COUNT(*) AS TOTAL
      FROM PST.PS_APPS_DEV.SDA_USE_CASES_CACHE
      WHERE (PS_ENGAGEMENT NOT IN (${psRolesIn}) OR PS_ENGAGEMENT IS NULL)
        AND USE_CASE_ACV > 0
        AND ${SIS_DISTRICT_SQL}
        ${filterSql}
    `;

    const [rows, countResult] = await Promise.all([
      query<{
        ACCOUNT_NAME: string;
        USE_CASE_NAME: string;
        SEGMENT: string;
        USE_CASE_ACV: number | null;
        DISTRICT: string;
        REGION: string;
        PS_ENGAGEMENT: string | null;
        USE_CASE_STAGE: string | null;
      }>(sql),
      query<{ TOTAL: number }>(countSql),
    ]);

    const opportunities = rows.map((r) => ({
      account: r.ACCOUNT_NAME,
      useCase: r.USE_CASE_NAME,
      stage: r.USE_CASE_STAGE || r.PS_ENGAGEMENT || "Unengaged",
      eacv: r.USE_CASE_ACV || 0,
      eacvFormatted: fmtAcv(r.USE_CASE_ACV),
      pattern: inferPattern(r.SEGMENT, r.USE_CASE_ACV),
      district: r.DISTRICT,
    }));

    return NextResponse.json({
      opportunities,
      total: countResult[0]?.TOTAL || 0,
    });
  } catch (err: any) {
    console.error("Opportunities API error:", err.message);
    return NextResponse.json({ error: err.message }, { status: 500 });
  }
}

function inferPattern(segment: string, acv: number | null): string {
  if ((acv || 0) > 500_000) return "Migration Factory";
  if (segment === "Enterprise") return "Data Foundation";
  if (segment === "Majors") return "Quick Start";
  return "Discovery";
}
