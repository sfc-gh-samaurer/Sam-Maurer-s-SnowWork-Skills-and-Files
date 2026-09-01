import { NextResponse } from "next/server";
import { query, SIS_DISTRICT_SQL, multiFilterSql, pmToDistrictSql } from "@/lib/snowflake";

export const dynamic = "force-dynamic";

// Use case stages that represent a milestone (won or in delivery)
const MILESTONE_STAGES = [
  "4 - Use Case Won / Migration Plan",
  "5 - Implementation In Progress",
  "6 - Implementation Complete",
  "7 - Deployed",
];

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const district = searchParams.get("district") || null;
  const region = searchParams.get("region") || null;
  const segment = searchParams.get("segment") || null;
  const pm = searchParams.get("pm") || null;

  try {
    let sql = `
      SELECT DISTINCT
        h.ACCOUNT_NAME,
        h.PROJECT_NAME,
        h.PROJECT_STATUS,
        h.HEALTH_SCORE,
        h.SCOPE_HEALTH,
        h.SCHEDULE_HEALTH,
        h.CONSUMPTION_HEALTH,
        h.HRS_REM
      FROM PST.PS_APPS_DEV.PROJECT_HEALTH_SNAPSHOTS h
      JOIN PST.PS_APPS_DEV.SDA_USE_CASES_CACHE u ON h.ACCOUNT_NAME = u.ACCOUNT_NAME
      WHERE h.SNAPSHOT_DATE = (SELECT MAX(SNAPSHOT_DATE) FROM PST.PS_APPS_DEV.PROJECT_HEALTH_SNAPSHOTS)
        AND h.PROJECT_STATUS IN ('Yellow','Red')
        AND u.USE_CASE_STAGE IN (${MILESTONE_STAGES.map(s => `'${s}'`).join(",")})
        AND u.${SIS_DISTRICT_SQL}
    `;
    sql += multiFilterSql("DISTRICT", district, "u");
    sql += multiFilterSql("REGION", region, "u");
    sql += multiFilterSql("SEGMENT", segment, "u");
    if (pm) {
      const pmSql = pmToDistrictSql(pm);
      if (pmSql) sql += pmSql.replace(/DISTRICT IN/g, "u.DISTRICT IN");
    }
    sql += ` ORDER BY h.HEALTH_SCORE ASC NULLS FIRST LIMIT 50`;

    const rows = await query<{
      ACCOUNT_NAME: string;
      PROJECT_NAME: string;
      PROJECT_STATUS: string;
      HEALTH_SCORE: number | null;
      SCOPE_HEALTH: string | null;
      SCHEDULE_HEALTH: string | null;
      CONSUMPTION_HEALTH: string | null;
      HRS_REM: number | null;
    }>(sql);

    const risks = rows.map((r) => {
      // Build issue description from health dimensions
      const issues: string[] = [];
      if (r.SCOPE_HEALTH === "Red" || r.SCOPE_HEALTH === "Yellow") issues.push(`Scope: ${r.SCOPE_HEALTH}`);
      if (r.SCHEDULE_HEALTH === "Red" || r.SCHEDULE_HEALTH === "Yellow") issues.push(`Schedule: ${r.SCHEDULE_HEALTH}`);
      if (r.CONSUMPTION_HEALTH === "Red" || r.CONSUMPTION_HEALTH === "Yellow") issues.push(`Consumption: ${r.CONSUMPTION_HEALTH}`);
      const issueStr = issues.length > 0 ? issues.join(", ") : `Status: ${r.PROJECT_STATUS}`;

      return {
        account: r.ACCOUNT_NAME,
        project: r.PROJECT_NAME,
        issue: issueStr,
        action: r.PROJECT_STATUS === "Red" ? "Escalation Required" : "Leadership Review",
      };
    });

    return NextResponse.json({ risks, count: risks.length });
  } catch (err: any) {
    console.error("Risk API error:", err.message);
    return NextResponse.json({ error: err.message }, { status: 500 });
  }
}
