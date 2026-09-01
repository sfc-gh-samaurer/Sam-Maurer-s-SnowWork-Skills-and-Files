import snowflake from "snowflake-sdk";
import fs from "fs";

let connectionPool: snowflake.Connection | null = null;
let connectPromise: Promise<snowflake.Connection> | null = null;

const TOKEN_PATH = "/snowflake/session/token";

function getLoginToken(): string {
  if (fs.existsSync(TOKEN_PATH)) {
    return fs.readFileSync(TOKEN_PATH, "ascii").trim();
  }
  throw new Error(
    "SPCS token file not found at " + TOKEN_PATH + ". Are you running inside SPCS?"
  );
}

function getConnection(): Promise<snowflake.Connection> {
  if (connectionPool) return Promise.resolve(connectionPool);
  if (connectPromise) return connectPromise;

  const token = getLoginToken();

  const conn = snowflake.createConnection({
    accessUrl: "https://" + (process.env.SNOWFLAKE_HOST || ""),
    account: process.env.SNOWFLAKE_ACCOUNT || "",
    authenticator: "OAUTH",
    token,
    warehouse: process.env.SNOWFLAKE_WAREHOUSE || "PST_STEAMLIT_APPS",
    database: process.env.SNOWFLAKE_DATABASE || "PST",
    schema: process.env.SNOWFLAKE_SCHEMA || "PS_APPS_DEV",
  });

  connectPromise = new Promise((resolve, reject) => {
    conn.connect((err) => {
      if (err) {
        console.error("Snowflake connection error:", err.message);
        connectionPool = null;
        connectPromise = null;
        reject(err);
      } else {
        connectionPool = conn;
        resolve(conn);
      }
    });
  });

  return connectPromise;
}

export async function query<T = Record<string, unknown>>(
  sql: string,
  binds: snowflake.Binds = []
): Promise<T[]> {
  const conn = await getConnection();
  return new Promise((resolve, reject) => {
    conn.execute({
      sqlText: sql,
      binds,
      complete: (err, _stmt, rows) => {
        if (err) {
          console.error("Query error:", err.message);
          reject(err);
        } else {
          resolve((rows || []) as T[]);
        }
      },
    });
  });
}

// FY quarter logic: Snowflake fiscal year offset
// Feb=Q1, May=Q2, Aug=Q3, Nov=Q4
export function currentFYQuarter(): { fy: number; quarter: number; label: string } {
  const now = new Date();
  const month = now.getMonth() + 1; // 1-indexed
  const year = now.getFullYear();

  let fy: number;
  let quarter: number;

  if (month >= 2 && month <= 4) {
    quarter = 1;
    fy = year + 1; // Feb-Apr 2026 = Q1 FY27
  } else if (month >= 5 && month <= 7) {
    quarter = 2;
    fy = year + 1;
  } else if (month >= 8 && month <= 10) {
    quarter = 3;
    fy = year + 1;
  } else {
    // Nov, Dec, Jan
    quarter = 4;
    fy = month >= 11 ? year + 2 : year + 1;
  }

  return { fy, quarter, label: `Q${quarter} FY${fy % 100}` };
}

/** Derive FY quarter label from a date string (e.g. "2026-04-15" -> "Q1 FY27") */
export function dateToFYQuarterLabel(dateStr: string | null): string | null {
  if (!dateStr) return null;
  const d = new Date(dateStr);
  if (isNaN(d.getTime())) return null;
  const month = d.getMonth() + 1;
  const year = d.getFullYear();
  let fy: number, q: number;
  if (month >= 2 && month <= 4) { q = 1; fy = year + 1; }
  else if (month >= 5 && month <= 7) { q = 2; fy = year + 1; }
  else if (month >= 8 && month <= 10) { q = 3; fy = year + 1; }
  else { q = 4; fy = month >= 11 ? year + 2 : year + 1; }
  return `Q${q} FY${fy % 100}`;
}

// 43 SiS in-scope districts (from PS_DASHBOARD_SNAPSHOTS, China_Dist removed)
export const SIS_DISTRICTS = [
  "CanadaGrowth","CommFinServ1","CommFinServ2","CommHCLS",
  "CommMFG","CommRetailEast","CommRetailWest","CommTech1","CommTech2",
  "EntAcqEastCanada","EntBayArea","EntBayAreaTech1","EntBayAreaTech2",
  "EntEastCanada","EntGreatPlains","EntHCLSEast","EntHCLSWest",
  "EntLosAngeles","EntMidwest","EntNYNJ1","EntNYNJ2","EntNewEngland1",
  "EntNewEngland2","EntOhioValley","EntPacNorthwest","EntSECarolinas",
  "EntSEPhilly","EntSESoAtl","EntSEVirginia","EntSoCal","EntSouthWest",
  "EntTOLA","EntWestCanada","PubSecCanada","StratCanada",
  "USGrowthBayAreaExp","USGrowthMidAtlExp","USGrowthNCentExp",
  "USGrowthNEExp","USGrowthNWExp","USGrowthSCentExp","USGrowthSEExp",
  "USGrowthSWExp",
] as const;

/** SQL IN clause for SiS district scoping */
export const SIS_DISTRICT_SQL = `DISTRICT IN (${SIS_DISTRICTS.map(d => `'${d}'`).join(",")})`;

/**
 * Build a SQL condition from a comma-separated multi-select param.
 * Returns empty string if param is null/empty.
 * Example: multiFilterSql("REGION", "AMER,EMEA") => "UPPER(REGION) IN ('AMER','EMEA')"
 */
export function multiFilterSql(column: string, param: string | null, tableAlias?: string): string {
  if (!param) return "";
  const values = param.split(",").map(v => v.trim()).filter(Boolean);
  if (values.length === 0) return "";
  const col = tableAlias ? `${tableAlias}.${column}` : column;
  const inList = values.map(v => `'${v.replace(/'/g, "''")}'`).join(",");
  return ` AND UPPER(${col}) IN (${inList.toUpperCase()})`;
}

/** District → Practice Manager mapping (from PRM_FY27_TARGETS) */
export const DISTRICT_PM_MAP: Record<string, string> = {
  CanadaGrowth: "Sydney Fuller",
  CommFinServ1: "Alyssa Brown",
  CommFinServ2: "Alyssa Brown",
  CommHCLS: "Mark Godard",
  CommMFG: "Alyssa Brown",
  CommRetailEast: "Mark Godard",
  CommRetailWest: "Mark Godard",
  CommTech1: "Mark Godard",
  CommTech2: "Mark Godard",
  EntAcqEastCanada: "Brendan Owens",
  EntBayArea: "Deep Gill",
  EntBayAreaTech1: "Sam Maurer",
  EntBayAreaTech2: "Deep Gill",
  EntEastCanada: "Karan Lulla",
  EntGreatPlains: "Hugh Pham",
  EntHCLSEast: "TBD",
  EntHCLSWest: "Andrew Dunn",
  EntLosAngeles: "Russell Pekrul",
  EntMidwest: "Eli Kesic",
  EntNYNJ1: "Clark Whiteway",
  EntNYNJ2: "Clark Whiteway",
  EntNewEngland1: "TBD",
  EntNewEngland2: "TBD",
  EntOhioValley: "Eli Kesic",
  EntPacNorthwest: "Sam Maurer",
  EntSECarolinas: "Jamey Phillips",
  EntSEPhilly: "Carl Martin",
  EntSESoAtl: "Carl Martin",
  EntSEVirginia: "Carl Martin",
  EntSoCal: "Russell Pekrul",
  EntSouthWest: "Andrew Dunn",
  EntTOLA: "Hugh Pham",
  EntWestCanada: "Sydney Fuller",
  PubSecCanada: "Sydney Fuller",
  StratCanada: "Karan Lulla",
  USGrowthBayAreaExp: "Mack Singh",
  USGrowthMidAtlExp: "Vince Santacrose",
  USGrowthNCentExp: "Mack Singh",
  USGrowthNEExp: "Vince Santacrose",
  USGrowthNWExp: "Mack Singh",
  USGrowthSCentExp: "Mack Singh",
  USGrowthSEExp: "Vince Santacrose",
  USGrowthSWExp: "Mack Singh",
};

/** Get unique sorted list of practice managers */
export const PRACTICE_MANAGERS = [...new Set(Object.values(DISTRICT_PM_MAP))].sort();

/** Get districts for a given set of practice managers (comma-separated) */
export function pmToDistrictSql(pmParam: string | null): string {
  if (!pmParam) return "";
  const pms = pmParam.split(",").map(v => v.trim()).filter(Boolean);
  if (pms.length === 0) return "";
  const districts = Object.entries(DISTRICT_PM_MAP)
    .filter(([, pm]) => pms.includes(pm))
    .map(([d]) => `'${d}'`);
  if (districts.length === 0) return "";
  return ` AND DISTRICT IN (${districts.join(",")})`;
}

export function fmtAcv(val: number | null): string {
  if (val == null || isNaN(val)) return "N/A";
  if (val >= 1_000_000) return `$${(val / 1_000_000).toFixed(1)}M`;
  if (val >= 1_000) return `$${(val / 1_000).toFixed(0)}K`;
  return `$${val.toFixed(0)}`;
}

export function fmtPct(val: number | null): string {
  if (val == null || isNaN(val)) return "N/A";
  return `${(val * 100).toFixed(1)}%`;
}

export function fmtNumber(val: number | null): string {
  if (val == null || isNaN(val)) return "0";
  return val.toLocaleString("en-US");
}
