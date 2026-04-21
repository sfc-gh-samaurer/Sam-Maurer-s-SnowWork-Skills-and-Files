# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "snowflake-connector-python[secure-local-storage]>=3.0.0",
# ]
# ///
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import date, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _report_utils import build_html  # noqa: E402

import snowflake.connector


def connect() -> snowflake.connector.SnowflakeConnection:
    conn_name = os.getenv("SNOWFLAKE_CONNECTION_NAME") or "default"
    return snowflake.connector.connect(
        connection_name=conn_name,
        client_store_temporary_credential=True,
    )


def run_query(conn: snowflake.connector.SnowflakeConnection, sql: str) -> list[dict]:
    cur = conn.cursor()
    cur.execute("USE ROLE SD_USER_RO_RL")
    cur.execute("USE WAREHOUSE SNOWADHOC")
    cur.execute(sql)
    cols = [c[0] for c in cur.description]
    rows = cur.fetchall()
    return [dict(zip(cols, r)) for r in rows]


def query_use_case_compliance(conn: snowflake.connector.SnowflakeConnection) -> list[dict]:
    sql = """
    SELECT
        m.SALESFORCE_PROFESSIONAL_SERVICES_MILESTONE_ID AS milestone_id,
        m.SALESFORCE_PROFESSIONAL_SERVICES_MILESTONE_NAME AS milestone_name,
        m.SALESFORCE_PROFESSIONAL_SERVICES_PROJECT_NAME AS project_name,
        m.SALESFORCE_PROFESSIONAL_SERVICES_PROJECT_MANAGER_NAME AS project_manager,
        u.SALESFORCE_USER_NAME AS owner_name,
        u.SALESFORCE_USER_ROLE_NAME AS owner_role,
        u.SALESFORCE_USER_EMAIL AS owner_email,
        m.SALESFORCE_ACCOUNT_NAME AS account_name,
        m.SALESFORCE_PROFESSIONAL_SERVICES_MILESTONE_STATUS AS milestone_status,
        m.SALESFORCE_USE_CASE_ID AS use_case_id,
        m.IS_SALESFORCE_PROFESSIONAL_SERVICES_PROJECT_ACTIVE AS is_project_active,
        CASE
            WHEN m.SALESFORCE_USE_CASE_ID IS NULL OR TRIM(m.SALESFORCE_USE_CASE_ID) = '' THEN 'Blank Use Case ID'
            WHEN uc.SALESFORCE_USE_CASE_ID IS NULL THEN 'Invalid Use Case ID'
        END AS reason
    FROM SNOW_CERTIFIED.PROFESSIONAL_SERVICES.DD_PROFESSIONAL_SERVICES_MILESTONE m
    LEFT JOIN SNOW_CERTIFIED.SALESFORCE_USE_CASE.DD_SALESFORCE_USE_CASE uc
        ON uc.SALESFORCE_USE_CASE_ID = m.SALESFORCE_USE_CASE_ID
    LEFT JOIN SNOW_CERTIFIED.SALESFORCE_USER.DD_SALESFORCE_USER u
        ON u.SALESFORCE_USER_ID = m.SALESFORCE_PROFESSIONAL_SERVICES_MILESTONE_OWNER_ID
    WHERE m.SALESFORCE_PROFESSIONAL_SERVICES_MILESTONE_TYPE = 'Use Case'
      AND (
          m.SALESFORCE_USE_CASE_ID IS NULL
          OR TRIM(m.SALESFORCE_USE_CASE_ID) = ''
          OR uc.SALESFORCE_USE_CASE_ID IS NULL
      )
    ORDER BY
        m.IS_SALESFORCE_PROFESSIONAL_SERVICES_PROJECT_ACTIVE DESC,
        m.SALESFORCE_PROFESSIONAL_SERVICES_PROJECT_NAME,
        m.SALESFORCE_PROFESSIONAL_SERVICES_MILESTONE_NAME
    """
    return run_query(conn, sql)


def query_summary(conn: snowflake.connector.SnowflakeConnection) -> dict:
    sql = """
    SELECT
        SUM(CASE WHEN m.SALESFORCE_USE_CASE_ID IS NULL OR TRIM(m.SALESFORCE_USE_CASE_ID) = '' THEN 1 ELSE 0 END) AS blank_use_case_id,
        SUM(CASE WHEN m.SALESFORCE_USE_CASE_ID IS NOT NULL AND TRIM(m.SALESFORCE_USE_CASE_ID) != '' AND uc.SALESFORCE_USE_CASE_ID IS NULL THEN 1 ELSE 0 END) AS invalid_use_case_id
    FROM SNOW_CERTIFIED.PROFESSIONAL_SERVICES.DD_PROFESSIONAL_SERVICES_MILESTONE m
    LEFT JOIN SNOW_CERTIFIED.SALESFORCE_USE_CASE.DD_SALESFORCE_USE_CASE uc
        ON uc.SALESFORCE_USE_CASE_ID = m.SALESFORCE_USE_CASE_ID
    WHERE m.SALESFORCE_PROFESSIONAL_SERVICES_MILESTONE_TYPE = 'Use Case'
    """
    rows = run_query(conn, sql)
    return rows[0] if rows else {}


def _json_serial(obj):
    if isinstance(obj, (date, datetime)):
        return obj.isoformat()
    if hasattr(obj, "as_integer_ratio"):
        return float(obj)
    if isinstance(obj, bool):
        return obj
    raise TypeError(f"Type {type(obj)} not serializable")


def main():
    parser = argparse.ArgumentParser(description="Generate Use Case Compliance HTML report")
    default_output = str(Path(__file__).resolve().parent.parent / "output" / "use_case_compliance_report.html")
    parser.add_argument("--output", default=default_output)
    parser.add_argument("--dump-json", default=None, help="Dump intermediate JSON data to this path")
    args = parser.parse_args()

    conn = connect()
    print("Querying use case compliance...")
    milestones = query_use_case_compliance(conn)
    print(f"  {len(milestones)} non-compliant milestones found")
    print("Querying summary statistics...")
    summary = query_summary(conn)
    print(f"  Blank: {summary.get('BLANK_USE_CASE_ID', '?')} · Invalid: {summary.get('INVALID_USE_CASE_ID', '?')}")
    conn.close()

    data = {
        "milestones": milestones,
        "summary": summary,
    }

    if args.dump_json:
        Path(args.dump_json).write_text(json.dumps(data, default=_json_serial, indent=2))
        print(f"JSON data written to {args.dump_json}")

    html = build_html(data)
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(html)
    print(f"Report written to {args.output}")
    print(f"Open with: open {args.output}")


if __name__ == "__main__":
    main()
