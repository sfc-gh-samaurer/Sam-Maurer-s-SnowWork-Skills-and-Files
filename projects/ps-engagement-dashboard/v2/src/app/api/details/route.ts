import { NextResponse } from "next/server";
import { query } from "@/lib/snowflake";
import { PS_ROLES } from "@/lib/constants";

export const dynamic = "force-dynamic";

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const district = searchParams.get("district") || null;
  const tab = searchParams.get("tab") || "engaged"; // engaged | all | opportunities
  const limit = parseInt(searchParams.get("limit") || "100", 10);
  const offset = parseInt(searchParams.get("offset") || "0", 10);

  try {
    let whereClause = "";
    const conditions: string[] = [];

    if (district) {
      conditions.push(`UPPER(DISTRICT) = UPPER('${district.replace(/'/g, "''")}')`);
    }

    if (tab === "engaged") {
      conditions.push(
        `PS_ENGAGEMENT IN (${PS_ROLES.map((r) => `'${r}'`).join(",")})`
      );
    } else if (tab === "opportunities") {
      conditions.push(
        `PS_ENGAGEMENT NOT IN (${PS_ROLES.map((r) => `'${r}'`).join(",")})
         AND PS_ENGAGEMENT IS NOT NULL`
      );
    }

    if (conditions.length > 0) {
      whereClause = `WHERE ${conditions.join(" AND ")}`;
    }

    const sql = `
      SELECT ACCOUNT_NAME, USE_CASE_NAME, PS_ENGAGEMENT,
             USE_CASE_ACV, DISTRICT, REGION, SEGMENT,
             GO_LIVE_DATE, GO_LIVE_QUARTER, PROJECT_HEALTH
      FROM PST.PS_APPS_DEV.SDA_USE_CASES_CACHE
      ${whereClause}
      ORDER BY USE_CASE_ACV DESC NULLS LAST
      LIMIT ${limit} OFFSET ${offset}
    `;

    const countSql = `
      SELECT COUNT(*) AS TOTAL
      FROM PST.PS_APPS_DEV.SDA_USE_CASES_CACHE
      ${whereClause}
    `;

    const [rows, countResult] = await Promise.all([
      query<Record<string, unknown>>(sql),
      query<{ TOTAL: number }>(countSql),
    ]);

    return NextResponse.json({
      rows,
      total: countResult[0]?.TOTAL || 0,
      limit,
      offset,
    });
  } catch (err: any) {
    console.error("Details API error:", err.message);
    return NextResponse.json({ error: err.message }, { status: 500 });
  }
}
