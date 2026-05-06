import { NextResponse } from "next/server";
import { query, currentFYQuarter, dateToFYQuarterLabel, fmtAcv, fmtPct, fmtNumber, SIS_DISTRICT_SQL, multiFilterSql, pmToDistrictSql } from "@/lib/snowflake";
import { PS_ROLES } from "@/lib/constants";
import type { UseCase, KpiData } from "@/lib/constants";

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
    const fyq = currentFYQuarter();

    // Core use case data — scoped to SiS districts
    let sql = `
      SELECT
        ACCOUNT_NAME, USE_CASE_NAME, PS_ENGAGEMENT, USE_CASE_ACV,
        DISTRICT, REGION, SEGMENT, INDUSTRY, ARR, ACCOUNT_TIER,
        GO_LIVE_DATE, USE_CASE_STAGE, DAYS_IN_STAGE, IMPLEMENTER
      FROM PST.PS_APPS_DEV.SDA_USE_CASES_CACHE
      WHERE ${SIS_DISTRICT_SQL}
    `;
    sql += multiFilterSql("DISTRICT", district);
    sql += multiFilterSql("REGION", region);
    sql += multiFilterSql("SEGMENT", segment);
    sql += pmToDistrictSql(pm);

    const rows = await query<UseCase & { IMPLEMENTER: string | null }>(sql);

    // PS-Engaged = rows with a recognized PS role
    const psEngaged = rows.filter((r) =>
      PS_ROLES.includes(r.PS_ENGAGEMENT as any)
    );

    // EACV = sum of USE_CASE_ACV for PS-engaged
    const eacv = psEngaged.reduce(
      (sum, r) => sum + (r.USE_CASE_ACV || 0),
      0
    );

    // Unique accounts
    const allAccounts = new Set(rows.map((r) => r.ACCOUNT_NAME));
    const engagedAccounts = new Set(psEngaged.map((r) => r.ACCOUNT_NAME));

    // Attach rate = PS-engaged UCs / total UCs
    const attachRate = rows.length > 0 ? psEngaged.length / rows.length : 0;

    // Account penetration
    const accountPenetration =
      allAccounts.size > 0 ? engagedAccounts.size / allAccounts.size : 0;

    // Go-lives this quarter — derive quarter from GO_LIVE_DATE
    const goLivesThisQtr = psEngaged.filter(
      (r) => dateToFYQuarterLabel(r.GO_LIVE_DATE) === fyq.label
    ).length;

    // SF PS-Led: use cases where IMPLEMENTER contains "Snowflake SD"
    const sfPsLed = psEngaged.filter(
      (r) => r.IMPLEMENTER && r.IMPLEMENTER.includes("Snowflake SD")
    );
    const sfPsLedPct = psEngaged.length > 0 ? sfPsLed.length / psEngaged.length : 0;

    // At Risk: query PROJECT_HEALTH_SNAPSHOTS for Yellow/Red projects
    // that have a use case with a milestone stage in SiS districts
    let atRiskSql = `
      SELECT COUNT(DISTINCT h.PROJECT_ID) AS AT_RISK_COUNT
      FROM PST.PS_APPS_DEV.PROJECT_HEALTH_SNAPSHOTS h
      JOIN PST.PS_APPS_DEV.SDA_USE_CASES_CACHE u ON h.ACCOUNT_NAME = u.ACCOUNT_NAME
      WHERE h.SNAPSHOT_DATE = (SELECT MAX(SNAPSHOT_DATE) FROM PST.PS_APPS_DEV.PROJECT_HEALTH_SNAPSHOTS)
        AND h.PROJECT_STATUS IN ('Yellow','Red')
        AND u.USE_CASE_STAGE IN (${MILESTONE_STAGES.map(s => `'${s}'`).join(",")})
        AND u.${SIS_DISTRICT_SQL}
    `;
    atRiskSql += multiFilterSql("DISTRICT", district, "u");
    atRiskSql += multiFilterSql("REGION", region, "u");
    atRiskSql += multiFilterSql("SEGMENT", segment, "u");
    if (pm) {
      // pmToDistrictSql uses bare DISTRICT — need to prefix with u.
      const pmDistricts = pmToDistrictSql(pm);
      if (pmDistricts) atRiskSql += pmDistricts.replace(/DISTRICT IN/g, "u.DISTRICT IN");
    }

    const atRiskResult = await query<{ AT_RISK_COUNT: number }>(atRiskSql);
    const atRiskCount = atRiskResult[0]?.AT_RISK_COUNT || 0;

    const kpis: KpiData[] = [
      {
        label: "PS-Engaged EACV",
        value: fmtAcv(eacv),
        icon: "trending_up",
        subtitle: fyq.label,
      },
      {
        label: "PS-Engaged Use Cases",
        value: fmtNumber(psEngaged.length),
        icon: "add",
        subtitle: `of ${fmtNumber(rows.length)} total`,
      },
      {
        label: "UC Attach Rate",
        value: fmtPct(attachRate),
        icon: "bar_chart",
      },
      {
        label: "Account Penetration",
        value: fmtPct(accountPenetration),
        icon: "people",
        subtitle: `${engagedAccounts.size} of ${allAccounts.size}`,
      },
      {
        label: "Go-Lives This Qtr",
        value: fmtNumber(goLivesThisQtr),
        icon: "history",
        subtitle: fyq.label,
      },
      {
        label: "SF PS-Led",
        value: fmtNumber(sfPsLed.length),
        icon: "shield",
        subtitle: `${fmtPct(sfPsLedPct)} of engaged`,
      },
      {
        label: "At Risk",
        value: fmtNumber(atRiskCount),
        icon: "warning",
        deltaType: atRiskCount > 0 ? "decrease" : "neutral",
        subtitle: "Yellow/Red w/ milestone",
      },
    ];

    return NextResponse.json({ kpis, quarter: fyq });
  } catch (err: any) {
    console.error("KPI API error:", err.message);
    return NextResponse.json(
      { error: err.message },
      { status: 500 }
    );
  }
}
