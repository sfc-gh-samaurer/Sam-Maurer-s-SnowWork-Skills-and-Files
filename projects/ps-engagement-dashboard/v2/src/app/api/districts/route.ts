import { NextResponse } from "next/server";
import { query, SIS_DISTRICT_SQL, multiFilterSql, pmToDistrictSql } from "@/lib/snowflake";
import { PS_ROLES } from "@/lib/constants";

export const dynamic = "force-dynamic";

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const district = searchParams.get("district") || null;
  const region = searchParams.get("region") || null;
  const segment = searchParams.get("segment") || null;
  const pm = searchParams.get("pm") || null;

  try {
    let sql = `
      SELECT DISTRICT, ACCOUNT_NAME, USE_CASE_NAME,
             PS_ENGAGEMENT, USE_CASE_ACV
      FROM PST.PS_APPS_DEV.SDA_USE_CASES_CACHE
      WHERE ${SIS_DISTRICT_SQL}
    `;
    sql += multiFilterSql("DISTRICT", district);
    sql += multiFilterSql("REGION", region);
    sql += multiFilterSql("SEGMENT", segment);
    sql += pmToDistrictSql(pm);

    const rows = await query<{
      DISTRICT: string;
      ACCOUNT_NAME: string;
      USE_CASE_NAME: string;
      PS_ENGAGEMENT: string;
      USE_CASE_ACV: number | null;
    }>(sql);

    // Group by district
    const districtMap: Record<string, { total: number; engaged: number; eacv: number }> = {};
    for (const r of rows) {
      const d = r.DISTRICT || "Unknown";
      if (!districtMap[d]) districtMap[d] = { total: 0, engaged: 0, eacv: 0 };
      districtMap[d].total++;
      if (PS_ROLES.includes(r.PS_ENGAGEMENT as any)) {
        districtMap[d].engaged++;
        districtMap[d].eacv += r.USE_CASE_ACV || 0;
      }
    }

    const districts = Object.entries(districtMap)
      .map(([name, d]) => ({
        district: name,
        engagedPct: d.total > 0 ? d.engaged / d.total : 0,
        eacv: d.eacv,
        ucCount: d.engaged,
        totalUcs: d.total,
      }))
      .sort((a, b) => b.eacv - a.eacv);

    return NextResponse.json({ districts });
  } catch (err: any) {
    console.error("Districts API error:", err.message);
    return NextResponse.json({ error: err.message }, { status: 500 });
  }
}
