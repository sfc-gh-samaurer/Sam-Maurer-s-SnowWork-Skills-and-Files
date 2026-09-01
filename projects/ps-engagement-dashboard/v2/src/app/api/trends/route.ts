import { NextResponse } from "next/server";
import { query } from "@/lib/snowflake";

export const dynamic = "force-dynamic";

export async function GET() {
  try {
    const rows = await query<{
      SNAPSHOT_DATE: string;
      PS_ENGAGED_EACV: number;
      PS_ENGAGED_COUNT: number;
    }>(`
      SELECT SNAPSHOT_DATE, PS_ENGAGED_EACV, PS_ENGAGED_COUNT
      FROM PST.PS_APPS_DEV.PS_DASHBOARD_SNAPSHOTS
      ORDER BY SNAPSHOT_DATE ASC
    `);

    const trend = rows.map((r) => ({
      date: r.SNAPSHOT_DATE,
      eacv: r.PS_ENGAGED_EACV,
      ucCount: r.PS_ENGAGED_COUNT,
    }));

    return NextResponse.json({ trend });
  } catch (err: any) {
    console.error("Trends API error:", err.message);
    return NextResponse.json({ error: err.message }, { status: 500 });
  }
}
