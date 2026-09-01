import { NextResponse } from "next/server";
import { query, fmtAcv, fmtPct, SIS_DISTRICT_SQL, multiFilterSql, pmToDistrictSql } from "@/lib/snowflake";
import { PS_ROLES } from "@/lib/constants";

export const dynamic = "force-dynamic";

const WORKLOAD_MAP: Record<string, string> = {
  Implementation: "Data Eng, AI/ML",
  Advisory: "Governance",
  Proposing: "HCLS, FinServ",
  Support: "Ops",
  Resident: "Platform",
};

const ACTIVITY_MAP: Record<string, string> = {
  Implementation: "Active project delivery",
  Advisory: "Architectural reviews",
  Proposing: "Scoping SOWs",
  Support: "Residency services",
  Resident: "Embedded support",
};

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const district = searchParams.get("district") || null;
  const region = searchParams.get("region") || null;
  const segment = searchParams.get("segment") || null;
  const pm = searchParams.get("pm") || null;

  try {
    let sql = `
      SELECT PS_ENGAGEMENT, USE_CASE_ACV, ARR
      FROM PST.PS_APPS_DEV.SDA_USE_CASES_CACHE
      WHERE PS_ENGAGEMENT IS NOT NULL
        AND ${SIS_DISTRICT_SQL}
    `;
    sql += multiFilterSql("DISTRICT", district);
    sql += multiFilterSql("REGION", region);
    sql += multiFilterSql("SEGMENT", segment);
    sql += pmToDistrictSql(pm);

    const rows = await query<{
      PS_ENGAGEMENT: string;
      USE_CASE_ACV: number | null;
      ARR: number | null;
    }>(sql);

    const totalUcs = rows.length;

    // Group by engagement type
    const typeMap: Record<string, { count: number; eacv: number }> = {};
    for (const r of rows) {
      const eng = r.PS_ENGAGEMENT || "Unspecified";
      if (!typeMap[eng]) typeMap[eng] = { count: 0, eacv: 0 };
      typeMap[eng].count++;
      typeMap[eng].eacv += r.USE_CASE_ACV || 0;
    }

    // Order by PS_ROLES first, then any extras
    const orderedTypes = [
      ...PS_ROLES.filter((r) => typeMap[r]),
      ...Object.keys(typeMap).filter(
        (k) => !PS_ROLES.includes(k as any)
      ),
    ];

    const engagementTypes = orderedTypes.map((type) => {
      const data = typeMap[type] || { count: 0, eacv: 0 };
      return {
        type: type === "Resident" ? "Resident" : type,
        useCases: data.count,
        eacv: data.eacv,
        eacvFormatted: fmtAcv(data.eacv),
        attachRate: totalUcs > 0 ? data.count / totalUcs : 0,
        attachRateFormatted: fmtPct(totalUcs > 0 ? data.count / totalUcs : 0),
        topWorkloads: WORKLOAD_MAP[type] || "Generic",
        activity: ACTIVITY_MAP[type] || "Entry point discovery",
      };
    });

    return NextResponse.json({ engagementTypes, totalUseCases: totalUcs });
  } catch (err: any) {
    console.error("Engagement Types API error:", err.message);
    return NextResponse.json({ error: err.message }, { status: 500 });
  }
}
