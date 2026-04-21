-- Opportunity Monitoring Queries
-- Supports both sales managers (team view) and individual AEs (own opportunities view)
-- All rule queries use a unified scoping pattern via the team_members CTE:
--   - If :is_manager = TRUE  -> scopes to direct reports (MANAGER_EMAIL = :user_email)
--   - If :is_manager = FALSE -> scopes to the user's own opportunities (PRIMARY_WORK_EMAIL = :user_email)
-- Parameters :user_email and :is_manager are set by Query 0.
--
-- Query structure:
--   Query 0:   Identify user, set :user_email and :is_manager
--   Query 0.1: Team roster (managers only)
--   Query 1:   Consolidated detail — Rules 1, 3-11, 13 (all flags as boolean columns per opp)
--   Query 2:   Rule 2 detail — Next Steps staleness (requires snapshot join)
--   Query 3:   Consolidated summary counts — Rules 1-11, 13
--   Query 4:   Rule 12 detail — Manager deal change alerts (requires snapshot join, manager-only)
--   Query 4.1: Rule 12 summary counts (manager-only)

--------------------------------------------------------------------------------
-- Query 0: Identify User from Snowflake Login
-- Returns IS_MANAGER flag to determine scoping mode
-- Store EMPLOYEE_EMAIL as :user_email and IS_MANAGER as :is_manager
--------------------------------------------------------------------------------
SELECT 
    CURRENT_USER() as login_username,
    PRIMARY_WORK_EMAIL AS EMPLOYEE_EMAIL,
    EMPLOYEE_NAME,
    CASE WHEN NUM_ACTIVE_DIRECT_REPORTS > 0 THEN TRUE ELSE FALSE END AS IS_MANAGER,
    LOCATION AS REGION,
    NULL AS THEATER,
    DIRECT_REPORTS,
    MANAGER_NAME,
    BUSINESS_TITLE
FROM SALES.RAVEN.RAVEN_EMPLOYEE_WITH_REPORTING_CHAIN
WHERE IS_ACTIVE = TRUE
  AND UPPER(snowflake_username) = UPPER(CURRENT_USER())
LIMIT 1;

--------------------------------------------------------------------------------
-- Query 0.1: Get Team Roster (Managers Only)
-- Skip this query if :is_manager = FALSE
--------------------------------------------------------------------------------
SELECT 
    PRIMARY_WORK_EMAIL AS EMPLOYEE_EMAIL,
    EMPLOYEE_NAME,
    EMPLOYEE_ID,
    BUSINESS_TITLE,
    HIRE_DATE,
    LOCATION AS REGION
FROM SALES.RAVEN.RAVEN_EMPLOYEE_WITH_REPORTING_CHAIN
WHERE MANAGER_EMAIL = :user_email
  AND IS_ACTIVE = TRUE
ORDER BY EMPLOYEE_NAME;

--------------------------------------------------------------------------------
-- Query 1: Consolidated Compliance Detail (Rules 1, 3-11)
-- One row per violating opportunity with boolean flags for each rule.
-- Only returns opportunities that violate at least one rule.
-- Rules covered:
--   R1:  Close Date in Past
--   R3:  $0 Total ACV (Closing This Q)
--   R4:  Still in Early Stages (Closing This Q)
--   R5:  Pipeline Forecast Status (Closing This Q, month 2-3 only)
--   R6:  Committed Not in Negotiation+ (Closing This Q)
--   R7:  Stale Opportunities — Benchmarked (Closing This Q, ACV > $100K)
--   R8:  Close Date on Last Day of Quarter (Closing This Q)
--   R9:  No Tech Win at Negotiation+ (Closing This Q)
--   R10: TCV < ACV (Closing This Q)
--   R11: MEDDPICC Incomplete (ACV > $100K)
--   R13: MEDDPICC Score < 7 (any of 8 score fields < 7)
-- Rule 2 is separate (Query 2) because it requires a snapshot LEFT JOIN.
--------------------------------------------------------------------------------
WITH team_members AS (
    SELECT EMPLOYEE_NAME
    FROM SALES.RAVEN.RAVEN_EMPLOYEE_WITH_REPORTING_CHAIN
    WHERE IS_ACTIVE = TRUE
      AND (
          (:is_manager = TRUE AND MANAGER_EMAIL = :user_email)
          OR (:is_manager = FALSE AND PRIMARY_WORK_EMAIL = :user_email)
      )
),
fq AS (
    SELECT
        MIN(FQ_START) AS FQ_START,
        MIN(FQ_END)   AS FQ_END,
        DATEADD('month', 1, MIN(FQ_START)) AS FQ_MONTH2_START
    FROM SALES.RAVEN.SDA_OPPORTUNITY_VIEW
    WHERE DS = CURRENT_DATE() AND FQ_END >= CURRENT_DATE()
)
SELECT
    o.OPPORTUNITY_ID,
    o.OPPORTUNITY_NAME,
    o.ACCOUNT_NAME,
    o.STAGE_NAME,
    o.FORECAST_STATUS,
    o.CLOSE_DATE::DATE AS CLOSE_DATE,
    o.TOTAL_ACV,
    o.TCV,
    o.OPPORTUNITY_OWNER_NAME AS REP_NAME,
    o.DM AS DISTRICT_MANAGER,
    o.THEATER,
    o.NEXT_STEPS,
    o.DAYS_IN_STAGE,
    o.DAYS_IN_STAGE_BENCHMARK_P50,
    o.DAYS_IN_STAGE_BENCHMARK_P75,
    o.TECHNICAL_WIN,
    o.MEDDPICC_OVERALL_SCORE,
    o.CREATED_DATE,
    CASE WHEN o.CLOSE_DATE::DATE < CURRENT_DATE()
              AND o.CLOSE_DATE::DATE >= '2021-01-01'
              AND o.TOTAL_ACV > 0
              AND o.STAGE_NAME != 'Sales Ops Review'
              AND o.FORECAST_STATUS != 'Omitted'
         THEN TRUE ELSE FALSE
    END AS FLAG_R1_CLOSE_DATE_PAST,
    CASE WHEN o.TOTAL_ACV = 0
              AND o.CLOSE_DATE::DATE BETWEEN fq.FQ_START AND fq.FQ_END
              AND o.STAGE_NAME IN ('Discovery', 'Scope / Use Case', 'Technical / Business Impact Validation', 'Negotiation', 'Deal Review', 'Deal Imminent')
         THEN TRUE ELSE FALSE
    END AS FLAG_R3_ZERO_ACV,
    CASE WHEN o.TOTAL_ACV > 0
              AND o.FORECAST_STATUS != 'Omitted'
              AND o.THEATER != 'Corporate'
              AND o.CLOSE_DATE::DATE BETWEEN fq.FQ_START AND fq.FQ_END
              AND o.STAGE_NAME IN ('SDR Qualified: SQL', 'Sales Qualified Opportunity', 'Discovery', 'Scope / Use Case')
         THEN TRUE ELSE FALSE
    END AS FLAG_R4_EARLY_STAGE,
    CASE WHEN o.TOTAL_ACV > 0
              AND o.FORECAST_STATUS = 'Pipeline'
              AND o.THEATER != 'Corporate'
              AND o.CLOSE_DATE::DATE BETWEEN fq.FQ_START AND fq.FQ_END
              AND CURRENT_DATE() >= fq.FQ_MONTH2_START
         THEN TRUE ELSE FALSE
    END AS FLAG_R5_PIPELINE_STATUS,
    CASE WHEN o.FORECAST_STATUS = 'Commit'
              AND o.CLOSE_DATE::DATE BETWEEN fq.FQ_START AND fq.FQ_END
              AND o.STAGE_NAME IN ('SDR Qualified: SQL', 'Sales Qualified Opportunity', 'Discovery', 'Scope / Use Case', 'Technical / Business Impact Validation')
         THEN TRUE ELSE FALSE
    END AS FLAG_R6_COMMIT_EARLY_STAGE,
    CASE WHEN o.TOTAL_ACV > 100000
              AND o.FORECAST_STATUS != 'Omitted'
              AND o.CLOSE_DATE::DATE BETWEEN fq.FQ_START AND fq.FQ_END
              AND o.DAYS_IN_STAGE_BENCHMARK_P75 IS NOT NULL
              AND o.DAYS_IN_STAGE > o.DAYS_IN_STAGE_BENCHMARK_P75
         THEN TRUE ELSE FALSE
    END AS FLAG_R7_STALE_BENCHMARKED,
    CASE WHEN o.TOTAL_ACV > 0
              AND o.FORECAST_STATUS != 'Omitted'
              AND o.CLOSE_DATE::DATE = fq.FQ_END
         THEN TRUE ELSE FALSE
    END AS FLAG_R8_LAST_DAY_OF_Q,
    CASE WHEN o.TOTAL_ACV > 0
              AND o.FORECAST_STATUS != 'Omitted'
              AND o.CLOSE_DATE::DATE BETWEEN fq.FQ_START AND fq.FQ_END
              AND o.STAGE_NAME IN ('Negotiation', 'Deal Review', 'Deal Imminent')
              AND (o.TECHNICAL_WIN = FALSE OR o.TECHNICAL_WIN IS NULL)
         THEN TRUE ELSE FALSE
    END AS FLAG_R9_NO_TECH_WIN,
    CASE WHEN o.TOTAL_ACV > 0
              AND o.FORECAST_STATUS != 'Omitted'
              AND o.TCV < o.TOTAL_ACV
              AND o.CLOSE_DATE::DATE BETWEEN fq.FQ_START AND fq.FQ_END
         THEN TRUE ELSE FALSE
    END AS FLAG_R10_TCV_LT_ACV,
    CASE WHEN o.TOTAL_ACV > 100000
              AND (
                  COALESCE(TRIM(o.MEDDPICC_METRICS), '') = ''
                  OR COALESCE(TRIM(o.MEDDPICC_ECONOMIC_BUYER), '') = ''
                  OR COALESCE(TRIM(o.MEDDPICC_DECISION_PROCESS), '') = ''
                  OR COALESCE(TRIM(o.MEDDPICC_DECISION_CRITERIA), '') = ''
                  OR COALESCE(TRIM(o.MEDDPICC_IDENTIFY_PAIN), '') = ''
                  OR COALESCE(TRIM(o.MEDDPICC_PAPER_PROCESS), '') = ''
                  OR COALESCE(TRIM(o.MEDDPICC_CHAMPION), '') = ''
                  OR COALESCE(TRIM(o.MEDDPICC_PRIMARY_COMPETITOR), '') = ''
              )
         THEN TRUE ELSE FALSE
    END AS FLAG_R11_MEDDPICC_INCOMPLETE,
    CASE WHEN COALESCE(TRIM(o.MEDDPICC_METRICS), '') = '' THEN 'Metrics' END AS MISSING_METRICS,
    CASE WHEN COALESCE(TRIM(o.MEDDPICC_ECONOMIC_BUYER), '') = '' THEN 'Economic Buyer' END AS MISSING_ECONOMIC_BUYER,
    CASE WHEN COALESCE(TRIM(o.MEDDPICC_DECISION_PROCESS), '') = '' THEN 'Decision Process' END AS MISSING_DECISION_PROCESS,
    CASE WHEN COALESCE(TRIM(o.MEDDPICC_DECISION_CRITERIA), '') = '' THEN 'Decision Criteria' END AS MISSING_DECISION_CRITERIA,
    CASE WHEN COALESCE(TRIM(o.MEDDPICC_IDENTIFY_PAIN), '') = '' THEN 'Identify Pain' END AS MISSING_IDENTIFY_PAIN,
    CASE WHEN COALESCE(TRIM(o.MEDDPICC_PAPER_PROCESS), '') = '' THEN 'Paper Process' END AS MISSING_PAPER_PROCESS,
    CASE WHEN COALESCE(TRIM(o.MEDDPICC_CHAMPION), '') = '' THEN 'Champion' END AS MISSING_CHAMPION,
    CASE WHEN COALESCE(TRIM(o.MEDDPICC_PRIMARY_COMPETITOR), '') = '' THEN 'Competition' END AS MISSING_COMPETITION,
    CASE WHEN o.IS_CAPACITY = TRUE
              AND o.IS_CLOSED = FALSE
              AND (
                  COALESCE(o.MEDDPICC_METRICS_SCORE, 0) < 7
                  OR COALESCE(o.MEDDPICC_ECONOMIC_BUYER_SCORE, 0) < 7
                  OR COALESCE(o.MEDDPICC_DECISION_CRITERIA_SCORE, 0) < 7
                  OR COALESCE(o.MEDDPICC_DECISION_PROCESS_SCORE, 0) < 7
                  OR COALESCE(o.MEDDPICC_PAPER_PROCESS_SCORE, 0) < 7
                  OR COALESCE(o.MEDDPICC_IDENTIFIED_PAIN_SCORE, 0) < 7
                  OR COALESCE(o.MEDDPICC_CHAMPION_SCORE, 0) < 7
                  OR COALESCE(o.MEDDPICC_COMPETITION_SCORE, 0) < 7
              )
         THEN TRUE ELSE FALSE
    END AS FLAG_R13_MEDDPICC_SCORE_LOW,
    CASE WHEN COALESCE(o.MEDDPICC_METRICS_SCORE, 0) < 7 THEN 'Metrics(' || COALESCE(o.MEDDPICC_METRICS_SCORE, 0) || ')' END AS LOW_SCORE_METRICS,
    CASE WHEN COALESCE(o.MEDDPICC_ECONOMIC_BUYER_SCORE, 0) < 7 THEN 'Economic Buyer(' || COALESCE(o.MEDDPICC_ECONOMIC_BUYER_SCORE, 0) || ')' END AS LOW_SCORE_ECONOMIC_BUYER,
    CASE WHEN COALESCE(o.MEDDPICC_DECISION_CRITERIA_SCORE, 0) < 7 THEN 'Decision Criteria(' || COALESCE(o.MEDDPICC_DECISION_CRITERIA_SCORE, 0) || ')' END AS LOW_SCORE_DECISION_CRITERIA,
    CASE WHEN COALESCE(o.MEDDPICC_DECISION_PROCESS_SCORE, 0) < 7 THEN 'Decision Process(' || COALESCE(o.MEDDPICC_DECISION_PROCESS_SCORE, 0) || ')' END AS LOW_SCORE_DECISION_PROCESS,
    CASE WHEN COALESCE(o.MEDDPICC_PAPER_PROCESS_SCORE, 0) < 7 THEN 'Paper Process(' || COALESCE(o.MEDDPICC_PAPER_PROCESS_SCORE, 0) || ')' END AS LOW_SCORE_PAPER_PROCESS,
    CASE WHEN COALESCE(o.MEDDPICC_IDENTIFIED_PAIN_SCORE, 0) < 7 THEN 'Identify Pain(' || COALESCE(o.MEDDPICC_IDENTIFIED_PAIN_SCORE, 0) || ')' END AS LOW_SCORE_IDENTIFIED_PAIN,
    CASE WHEN COALESCE(o.MEDDPICC_CHAMPION_SCORE, 0) < 7 THEN 'Champion(' || COALESCE(o.MEDDPICC_CHAMPION_SCORE, 0) || ')' END AS LOW_SCORE_CHAMPION,
    CASE WHEN COALESCE(o.MEDDPICC_COMPETITION_SCORE, 0) < 7 THEN 'Competition(' || COALESCE(o.MEDDPICC_COMPETITION_SCORE, 0) || ')' END AS LOW_SCORE_COMPETITION,
    o.DAYS_IN_STAGE - o.DAYS_IN_STAGE_BENCHMARK_P75 AS DAYS_OVER_BENCHMARK,
    o.TOTAL_ACV - o.TCV AS ACV_TCV_GAP,
    DATEDIFF('day', o.CLOSE_DATE::DATE, CURRENT_DATE()) AS DAYS_PAST_CLOSE,
    'https://snowforce.my.salesforce.com/' || o.OPPORTUNITY_ID AS SFDC_LINK
FROM SALES.RAVEN.SDA_OPPORTUNITY_VIEW o
INNER JOIN team_members tm ON o.OPPORTUNITY_OWNER_NAME = tm.EMPLOYEE_NAME
CROSS JOIN fq
WHERE o.DS = CURRENT_DATE()
  AND o.IS_CAPACITY = TRUE
  AND o.IS_CLOSED = FALSE
  AND (
      (o.CLOSE_DATE::DATE < CURRENT_DATE()
       AND o.CLOSE_DATE::DATE >= '2021-01-01'
       AND o.TOTAL_ACV > 0
       AND o.STAGE_NAME != 'Sales Ops Review'
       AND o.FORECAST_STATUS != 'Omitted')
      OR (o.TOTAL_ACV = 0
          AND o.CLOSE_DATE::DATE BETWEEN fq.FQ_START AND fq.FQ_END
          AND o.STAGE_NAME IN ('Discovery', 'Scope / Use Case', 'Technical / Business Impact Validation', 'Negotiation', 'Deal Review', 'Deal Imminent'))
      OR (o.TOTAL_ACV > 0
          AND o.FORECAST_STATUS != 'Omitted'
          AND o.THEATER != 'Corporate'
          AND o.CLOSE_DATE::DATE BETWEEN fq.FQ_START AND fq.FQ_END
          AND o.STAGE_NAME IN ('SDR Qualified: SQL', 'Sales Qualified Opportunity', 'Discovery', 'Scope / Use Case'))
      OR (o.TOTAL_ACV > 0
          AND o.FORECAST_STATUS = 'Pipeline'
          AND o.THEATER != 'Corporate'
          AND o.CLOSE_DATE::DATE BETWEEN fq.FQ_START AND fq.FQ_END
          AND CURRENT_DATE() >= fq.FQ_MONTH2_START)
      OR (o.FORECAST_STATUS = 'Commit'
          AND o.CLOSE_DATE::DATE BETWEEN fq.FQ_START AND fq.FQ_END
          AND o.STAGE_NAME IN ('SDR Qualified: SQL', 'Sales Qualified Opportunity', 'Discovery', 'Scope / Use Case', 'Technical / Business Impact Validation'))
      OR (o.TOTAL_ACV > 100000
          AND o.FORECAST_STATUS != 'Omitted'
          AND o.CLOSE_DATE::DATE BETWEEN fq.FQ_START AND fq.FQ_END
          AND o.DAYS_IN_STAGE_BENCHMARK_P75 IS NOT NULL
          AND o.DAYS_IN_STAGE > o.DAYS_IN_STAGE_BENCHMARK_P75)
      OR (o.TOTAL_ACV > 0
          AND o.FORECAST_STATUS != 'Omitted'
          AND o.CLOSE_DATE::DATE = fq.FQ_END)
      OR (o.TOTAL_ACV > 0
          AND o.FORECAST_STATUS != 'Omitted'
          AND o.CLOSE_DATE::DATE BETWEEN fq.FQ_START AND fq.FQ_END
          AND o.STAGE_NAME IN ('Negotiation', 'Deal Review', 'Deal Imminent')
          AND (o.TECHNICAL_WIN = FALSE OR o.TECHNICAL_WIN IS NULL))
      OR (o.TOTAL_ACV > 0
          AND o.FORECAST_STATUS != 'Omitted'
          AND o.TCV < o.TOTAL_ACV
          AND o.CLOSE_DATE::DATE BETWEEN fq.FQ_START AND fq.FQ_END)
      OR (o.TOTAL_ACV > 100000
          AND (
              COALESCE(TRIM(o.MEDDPICC_METRICS), '') = ''
              OR COALESCE(TRIM(o.MEDDPICC_ECONOMIC_BUYER), '') = ''
              OR COALESCE(TRIM(o.MEDDPICC_DECISION_PROCESS), '') = ''
              OR COALESCE(TRIM(o.MEDDPICC_DECISION_CRITERIA), '') = ''
              OR COALESCE(TRIM(o.MEDDPICC_IDENTIFY_PAIN), '') = ''
              OR COALESCE(TRIM(o.MEDDPICC_PAPER_PROCESS), '') = ''
              OR COALESCE(TRIM(o.MEDDPICC_CHAMPION), '') = ''
              OR COALESCE(TRIM(o.MEDDPICC_PRIMARY_COMPETITOR), '') = ''
          ))
      OR (
          COALESCE(o.MEDDPICC_METRICS_SCORE, 0) < 7
          OR COALESCE(o.MEDDPICC_ECONOMIC_BUYER_SCORE, 0) < 7
          OR COALESCE(o.MEDDPICC_DECISION_CRITERIA_SCORE, 0) < 7
          OR COALESCE(o.MEDDPICC_DECISION_PROCESS_SCORE, 0) < 7
          OR COALESCE(o.MEDDPICC_PAPER_PROCESS_SCORE, 0) < 7
          OR COALESCE(o.MEDDPICC_IDENTIFIED_PAIN_SCORE, 0) < 7
          OR COALESCE(o.MEDDPICC_CHAMPION_SCORE, 0) < 7
          OR COALESCE(o.MEDDPICC_COMPETITION_SCORE, 0) < 7
      )
  )
ORDER BY o.TOTAL_ACV DESC;

--------------------------------------------------------------------------------
-- Query 2: Rule 2 Detail — No Next Step Update L7D (Closing This Q)
-- Separate query because it requires a LEFT JOIN to SDA_OPPORTUNITY_SNAPSHOT_VIEW
-- to compare NEXT_STEPS across snapshots.
-- Capacity opps closing this Q at Tech Validation+ with stale/missing next steps.
--------------------------------------------------------------------------------
WITH team_members AS (
    SELECT EMPLOYEE_NAME
    FROM SALES.RAVEN.RAVEN_EMPLOYEE_WITH_REPORTING_CHAIN
    WHERE IS_ACTIVE = TRUE
      AND (
          (:is_manager = TRUE AND MANAGER_EMAIL = :user_email)
          OR (:is_manager = FALSE AND PRIMARY_WORK_EMAIL = :user_email)
      )
)
SELECT
    cur.OPPORTUNITY_ID,
    cur.OPPORTUNITY_NAME,
    cur.ACCOUNT_NAME,
    cur.STAGE_NAME,
    cur.FORECAST_STATUS,
    cur.CLOSE_DATE::DATE AS CLOSE_DATE,
    cur.TOTAL_ACV,
    cur.OPPORTUNITY_OWNER_NAME AS REP_NAME,
    cur.DM AS DISTRICT_MANAGER,
    cur.NEXT_STEPS,
    prev.NEXT_STEPS AS PREV_NEXT_STEPS,
    cur.DAYS_IN_STAGE,
    CASE WHEN cur.NEXT_STEPS IS NULL OR TRIM(cur.NEXT_STEPS) = '' THEN TRUE ELSE FALSE END AS FLAG_MISSING_NEXT_STEPS,
    CASE WHEN cur.NEXT_STEPS IS NOT NULL AND TRIM(cur.NEXT_STEPS) != '' AND (prev.OPPORTUNITY_ID IS NULL OR cur.NEXT_STEPS = prev.NEXT_STEPS) THEN TRUE ELSE FALSE END AS FLAG_STALE_NEXT_STEPS,
    'https://snowforce.my.salesforce.com/' || cur.OPPORTUNITY_ID AS SFDC_LINK
FROM SALES.RAVEN.SDA_OPPORTUNITY_VIEW cur
LEFT JOIN SALES.RAVEN.SDA_OPPORTUNITY_SNAPSHOT_VIEW prev
    ON cur.OPPORTUNITY_ID = prev.OPPORTUNITY_ID
    AND prev.DS = CURRENT_DATE() - 7
INNER JOIN team_members tm ON cur.OPPORTUNITY_OWNER_NAME = tm.EMPLOYEE_NAME
WHERE cur.DS = CURRENT_DATE()
  AND cur.IS_CAPACITY = TRUE
  AND cur.IS_CLOSED = FALSE
  AND cur.FORECAST_STATUS != 'Omitted'
  AND cur.CLOSE_DATE::DATE BETWEEN (SELECT MIN(FQ_START) FROM SALES.RAVEN.SDA_OPPORTUNITY_VIEW WHERE DS = CURRENT_DATE() AND FQ_END >= CURRENT_DATE())
                                AND (SELECT MIN(FQ_END)   FROM SALES.RAVEN.SDA_OPPORTUNITY_VIEW WHERE DS = CURRENT_DATE() AND FQ_END >= CURRENT_DATE())
  AND cur.STAGE_NAME IN (
      'Technical / Business Impact Validation',
      'Negotiation',
      'Deal Review',
      'Deal Imminent'
  )
  AND (
      prev.OPPORTUNITY_ID IS NULL
      OR cur.NEXT_STEPS IS NULL
      OR TRIM(cur.NEXT_STEPS) = ''
      OR cur.NEXT_STEPS = prev.NEXT_STEPS
  )
ORDER BY cur.TOTAL_ACV DESC;

--------------------------------------------------------------------------------
-- Query 3: Consolidated Compliance Summary (Rules 1-11, 13)
-- Single summary row with violation counts and ACV at risk per rule.
-- Includes R13 (MEDDPICC Score < 7) alongside R1-R11.
-- Uses the same team_members CTE for unified scoping.
-- Rule 2 requires its own snapshot join so it is computed in a subquery.
--------------------------------------------------------------------------------
WITH team_members AS (
    SELECT EMPLOYEE_NAME
    FROM SALES.RAVEN.RAVEN_EMPLOYEE_WITH_REPORTING_CHAIN
    WHERE IS_ACTIVE = TRUE
      AND (
          (:is_manager = TRUE AND MANAGER_EMAIL = :user_email)
          OR (:is_manager = FALSE AND PRIMARY_WORK_EMAIL = :user_email)
      )
),
fq AS (
    SELECT
        MIN(FQ_START) AS FQ_START,
        MIN(FQ_END)   AS FQ_END,
        DATEADD('month', 1, MIN(FQ_START)) AS FQ_MONTH2_START
    FROM SALES.RAVEN.SDA_OPPORTUNITY_VIEW
    WHERE DS = CURRENT_DATE() AND FQ_END >= CURRENT_DATE()
),
base AS (
    SELECT o.*
    FROM SALES.RAVEN.SDA_OPPORTUNITY_VIEW o
    INNER JOIN team_members tm ON o.OPPORTUNITY_OWNER_NAME = tm.EMPLOYEE_NAME
    WHERE o.DS = CURRENT_DATE()
      AND o.IS_CAPACITY = TRUE
      AND o.IS_CLOSED = FALSE
),
r2 AS (
    SELECT
        COUNT(*) AS R2_COUNT,
        COALESCE(SUM(cur.TOTAL_ACV), 0) AS R2_ACV
    FROM SALES.RAVEN.SDA_OPPORTUNITY_VIEW cur
    LEFT JOIN SALES.RAVEN.SDA_OPPORTUNITY_SNAPSHOT_VIEW prev
        ON cur.OPPORTUNITY_ID = prev.OPPORTUNITY_ID
        AND prev.DS = CURRENT_DATE() - 7
    INNER JOIN team_members tm ON cur.OPPORTUNITY_OWNER_NAME = tm.EMPLOYEE_NAME
    CROSS JOIN fq
    WHERE cur.DS = CURRENT_DATE()
      AND cur.IS_CAPACITY = TRUE
      AND cur.IS_CLOSED = FALSE
      AND cur.FORECAST_STATUS != 'Omitted'
      AND cur.CLOSE_DATE::DATE BETWEEN fq.FQ_START AND fq.FQ_END
      AND cur.STAGE_NAME IN ('Technical / Business Impact Validation', 'Negotiation', 'Deal Review', 'Deal Imminent')
      AND (
          prev.OPPORTUNITY_ID IS NULL
          OR cur.NEXT_STEPS IS NULL
          OR TRIM(cur.NEXT_STEPS) = ''
          OR cur.NEXT_STEPS = prev.NEXT_STEPS
      )
)
SELECT
    COUNT(CASE WHEN o.CLOSE_DATE::DATE < CURRENT_DATE()
                    AND o.CLOSE_DATE::DATE >= '2021-01-01'
                    AND o.TOTAL_ACV > 0
                    AND o.STAGE_NAME != 'Sales Ops Review'
                    AND o.FORECAST_STATUS != 'Omitted'
               THEN 1 END) AS R1_CLOSE_DATE_PAST_COUNT,
    COALESCE(SUM(CASE WHEN o.CLOSE_DATE::DATE < CURRENT_DATE()
                           AND o.CLOSE_DATE::DATE >= '2021-01-01'
                           AND o.TOTAL_ACV > 0
                           AND o.STAGE_NAME != 'Sales Ops Review'
                           AND o.FORECAST_STATUS != 'Omitted'
                      THEN o.TOTAL_ACV END), 0) AS R1_ACV_AT_RISK,
    MAX(r2.R2_COUNT) AS R2_STALE_NEXT_STEPS_COUNT,
    MAX(r2.R2_ACV) AS R2_ACV_AT_RISK,
    COUNT(CASE WHEN o.TOTAL_ACV = 0
                    AND o.CLOSE_DATE::DATE BETWEEN fq.FQ_START AND fq.FQ_END
                    AND o.STAGE_NAME IN ('Discovery', 'Scope / Use Case', 'Technical / Business Impact Validation', 'Negotiation', 'Deal Review', 'Deal Imminent')
               THEN 1 END) AS R3_ZERO_ACV_COUNT,
    COUNT(CASE WHEN o.TOTAL_ACV > 0
                    AND o.FORECAST_STATUS != 'Omitted'
                    AND o.THEATER != 'Corporate'
                    AND o.CLOSE_DATE::DATE BETWEEN fq.FQ_START AND fq.FQ_END
                    AND o.STAGE_NAME IN ('SDR Qualified: SQL', 'Sales Qualified Opportunity', 'Discovery', 'Scope / Use Case')
               THEN 1 END) AS R4_EARLY_STAGE_COUNT,
    COALESCE(SUM(CASE WHEN o.TOTAL_ACV > 0
                           AND o.FORECAST_STATUS != 'Omitted'
                           AND o.THEATER != 'Corporate'
                           AND o.CLOSE_DATE::DATE BETWEEN fq.FQ_START AND fq.FQ_END
                           AND o.STAGE_NAME IN ('SDR Qualified: SQL', 'Sales Qualified Opportunity', 'Discovery', 'Scope / Use Case')
                      THEN o.TOTAL_ACV END), 0) AS R4_ACV_AT_RISK,
    COUNT(CASE WHEN o.TOTAL_ACV > 0
                    AND o.FORECAST_STATUS = 'Pipeline'
                    AND o.THEATER != 'Corporate'
                    AND o.CLOSE_DATE::DATE BETWEEN fq.FQ_START AND fq.FQ_END
                    AND CURRENT_DATE() >= fq.FQ_MONTH2_START
               THEN 1 END) AS R5_PIPELINE_STATUS_COUNT,
    COALESCE(SUM(CASE WHEN o.TOTAL_ACV > 0
                           AND o.FORECAST_STATUS = 'Pipeline'
                           AND o.THEATER != 'Corporate'
                           AND o.CLOSE_DATE::DATE BETWEEN fq.FQ_START AND fq.FQ_END
                           AND CURRENT_DATE() >= fq.FQ_MONTH2_START
                      THEN o.TOTAL_ACV END), 0) AS R5_ACV_AT_RISK,
    COUNT(CASE WHEN o.FORECAST_STATUS = 'Commit'
                    AND o.CLOSE_DATE::DATE BETWEEN fq.FQ_START AND fq.FQ_END
                    AND o.STAGE_NAME IN ('SDR Qualified: SQL', 'Sales Qualified Opportunity', 'Discovery', 'Scope / Use Case', 'Technical / Business Impact Validation')
               THEN 1 END) AS R6_COMMIT_EARLY_STAGE_COUNT,
    COALESCE(SUM(CASE WHEN o.FORECAST_STATUS = 'Commit'
                           AND o.CLOSE_DATE::DATE BETWEEN fq.FQ_START AND fq.FQ_END
                           AND o.STAGE_NAME IN ('SDR Qualified: SQL', 'Sales Qualified Opportunity', 'Discovery', 'Scope / Use Case', 'Technical / Business Impact Validation')
                      THEN o.TOTAL_ACV END), 0) AS R6_ACV_AT_RISK,
    COUNT(CASE WHEN o.TOTAL_ACV > 100000
                    AND o.FORECAST_STATUS != 'Omitted'
                    AND o.CLOSE_DATE::DATE BETWEEN fq.FQ_START AND fq.FQ_END
                    AND o.DAYS_IN_STAGE_BENCHMARK_P75 IS NOT NULL
                    AND o.DAYS_IN_STAGE > o.DAYS_IN_STAGE_BENCHMARK_P75
               THEN 1 END) AS R7_STALE_BENCHMARKED_COUNT,
    COALESCE(SUM(CASE WHEN o.TOTAL_ACV > 100000
                           AND o.FORECAST_STATUS != 'Omitted'
                           AND o.CLOSE_DATE::DATE BETWEEN fq.FQ_START AND fq.FQ_END
                           AND o.DAYS_IN_STAGE_BENCHMARK_P75 IS NOT NULL
                           AND o.DAYS_IN_STAGE > o.DAYS_IN_STAGE_BENCHMARK_P75
                      THEN o.TOTAL_ACV END), 0) AS R7_ACV_AT_RISK,
    COUNT(CASE WHEN o.TOTAL_ACV > 0
                    AND o.FORECAST_STATUS != 'Omitted'
                    AND o.CLOSE_DATE::DATE = fq.FQ_END
               THEN 1 END) AS R8_LAST_DAY_OF_Q_COUNT,
    COALESCE(SUM(CASE WHEN o.TOTAL_ACV > 0
                           AND o.FORECAST_STATUS != 'Omitted'
                           AND o.CLOSE_DATE::DATE = fq.FQ_END
                      THEN o.TOTAL_ACV END), 0) AS R8_ACV_AT_RISK,
    COUNT(CASE WHEN o.TOTAL_ACV > 0
                    AND o.FORECAST_STATUS != 'Omitted'
                    AND o.CLOSE_DATE::DATE BETWEEN fq.FQ_START AND fq.FQ_END
                    AND o.STAGE_NAME IN ('Negotiation', 'Deal Review', 'Deal Imminent')
                    AND (o.TECHNICAL_WIN = FALSE OR o.TECHNICAL_WIN IS NULL)
               THEN 1 END) AS R9_NO_TECH_WIN_COUNT,
    COALESCE(SUM(CASE WHEN o.TOTAL_ACV > 0
                           AND o.FORECAST_STATUS != 'Omitted'
                           AND o.CLOSE_DATE::DATE BETWEEN fq.FQ_START AND fq.FQ_END
                           AND o.STAGE_NAME IN ('Negotiation', 'Deal Review', 'Deal Imminent')
                           AND (o.TECHNICAL_WIN = FALSE OR o.TECHNICAL_WIN IS NULL)
                      THEN o.TOTAL_ACV END), 0) AS R9_ACV_AT_RISK,
    COUNT(CASE WHEN o.TOTAL_ACV > 0
                    AND o.FORECAST_STATUS != 'Omitted'
                    AND o.TCV < o.TOTAL_ACV
                    AND o.CLOSE_DATE::DATE BETWEEN fq.FQ_START AND fq.FQ_END
               THEN 1 END) AS R10_TCV_LT_ACV_COUNT,
    COALESCE(SUM(CASE WHEN o.TOTAL_ACV > 0
                           AND o.FORECAST_STATUS != 'Omitted'
                           AND o.TCV < o.TOTAL_ACV
                           AND o.CLOSE_DATE::DATE BETWEEN fq.FQ_START AND fq.FQ_END
                      THEN o.TOTAL_ACV END), 0) AS R10_ACV_AT_RISK,
    COUNT(CASE WHEN o.TOTAL_ACV > 100000
                    AND (
                        COALESCE(TRIM(o.MEDDPICC_METRICS), '') = ''
                        OR COALESCE(TRIM(o.MEDDPICC_ECONOMIC_BUYER), '') = ''
                        OR COALESCE(TRIM(o.MEDDPICC_DECISION_PROCESS), '') = ''
                        OR COALESCE(TRIM(o.MEDDPICC_DECISION_CRITERIA), '') = ''
                        OR COALESCE(TRIM(o.MEDDPICC_IDENTIFY_PAIN), '') = ''
                        OR COALESCE(TRIM(o.MEDDPICC_PAPER_PROCESS), '') = ''
                        OR COALESCE(TRIM(o.MEDDPICC_CHAMPION), '') = ''
                        OR COALESCE(TRIM(o.MEDDPICC_PRIMARY_COMPETITOR), '') = ''
                    )
               THEN 1 END) AS R11_MEDDPICC_INCOMPLETE_COUNT,
    COALESCE(SUM(CASE WHEN o.TOTAL_ACV > 100000
                           AND (
                               COALESCE(TRIM(o.MEDDPICC_METRICS), '') = ''
                               OR COALESCE(TRIM(o.MEDDPICC_ECONOMIC_BUYER), '') = ''
                               OR COALESCE(TRIM(o.MEDDPICC_DECISION_PROCESS), '') = ''
                               OR COALESCE(TRIM(o.MEDDPICC_DECISION_CRITERIA), '') = ''
                               OR COALESCE(TRIM(o.MEDDPICC_IDENTIFY_PAIN), '') = ''
                               OR COALESCE(TRIM(o.MEDDPICC_PAPER_PROCESS), '') = ''
                               OR COALESCE(TRIM(o.MEDDPICC_CHAMPION), '') = ''
                               OR COALESCE(TRIM(o.MEDDPICC_PRIMARY_COMPETITOR), '') = ''
                           )
                      THEN o.TOTAL_ACV END), 0) AS R11_ACV_AT_RISK,
    COUNT(CASE WHEN (
                        COALESCE(o.MEDDPICC_METRICS_SCORE, 0) < 7
                        OR COALESCE(o.MEDDPICC_ECONOMIC_BUYER_SCORE, 0) < 7
                        OR COALESCE(o.MEDDPICC_DECISION_CRITERIA_SCORE, 0) < 7
                        OR COALESCE(o.MEDDPICC_DECISION_PROCESS_SCORE, 0) < 7
                        OR COALESCE(o.MEDDPICC_PAPER_PROCESS_SCORE, 0) < 7
                        OR COALESCE(o.MEDDPICC_IDENTIFIED_PAIN_SCORE, 0) < 7
                        OR COALESCE(o.MEDDPICC_CHAMPION_SCORE, 0) < 7
                        OR COALESCE(o.MEDDPICC_COMPETITION_SCORE, 0) < 7
                    )
               THEN 1 END) AS R13_MEDDPICC_SCORE_LOW_COUNT,
    COALESCE(SUM(CASE WHEN (
                               COALESCE(o.MEDDPICC_METRICS_SCORE, 0) < 7
                               OR COALESCE(o.MEDDPICC_ECONOMIC_BUYER_SCORE, 0) < 7
                               OR COALESCE(o.MEDDPICC_DECISION_CRITERIA_SCORE, 0) < 7
                               OR COALESCE(o.MEDDPICC_DECISION_PROCESS_SCORE, 0) < 7
                               OR COALESCE(o.MEDDPICC_PAPER_PROCESS_SCORE, 0) < 7
                               OR COALESCE(o.MEDDPICC_IDENTIFIED_PAIN_SCORE, 0) < 7
                               OR COALESCE(o.MEDDPICC_CHAMPION_SCORE, 0) < 7
                               OR COALESCE(o.MEDDPICC_COMPETITION_SCORE, 0) < 7
                           )
                      THEN o.TOTAL_ACV END), 0) AS R13_ACV_AT_RISK
FROM base o
CROSS JOIN fq
CROSS JOIN r2;

--------------------------------------------------------------------------------
-- Query 4: Rule 12 — Manager Deal Change Alerts (Detail)
-- Manager-only. Skip if :is_manager = FALSE.
-- Compares current snapshot to 7 days ago. Flags:
--   A) Close date pushed >= 1 month or >= 1 quarter
--   B) Close date within first 2 weeks of next Q start
--   C) Close date on a weekend
--   D) TCV < ACV
--   E) ACV changed > 10%
--------------------------------------------------------------------------------
WITH fq AS (
    SELECT
        MIN(FQ_START) AS FQ_START,
        MIN(FQ_END)   AS FQ_END
    FROM SALES.RAVEN.SDA_OPPORTUNITY_VIEW
    WHERE DS = CURRENT_DATE() AND FQ_END >= CURRENT_DATE()
),
next_fq AS (
    SELECT MIN(FQ_START) AS NEXT_FQ_START
    FROM SALES.RAVEN.SDA_OPPORTUNITY_VIEW
    WHERE DS = CURRENT_DATE() AND FQ_START > (SELECT FQ_END FROM fq)
)
SELECT
    cur.OPPORTUNITY_ID,
    cur.OPPORTUNITY_NAME,
    cur.ACCOUNT_NAME,
    cur.STAGE_NAME,
    cur.FORECAST_STATUS,
    cur.CLOSE_DATE::DATE AS CLOSE_DATE,
    prev.CLOSE_DATE::DATE AS PREV_CLOSE_DATE,
    cur.TOTAL_ACV,
    prev.TOTAL_ACV AS PREV_TOTAL_ACV,
    cur.TCV,
    cur.OPPORTUNITY_OWNER_NAME AS REP_NAME,
    cur.DM AS DISTRICT_MANAGER,
    cur.NEXT_STEPS,
    cur.DAYS_IN_STAGE,
    CASE WHEN prev.CLOSE_DATE IS NOT NULL
              AND cur.CLOSE_DATE::DATE >= DATEADD('month', 1, prev.CLOSE_DATE::DATE)
         THEN TRUE ELSE FALSE
    END AS FLAG_CLOSE_DATE_PUSHED_1M,
    CASE WHEN prev.CLOSE_DATE IS NOT NULL
              AND cur.CLOSE_DATE::DATE >= DATEADD('month', 3, prev.CLOSE_DATE::DATE)
         THEN TRUE ELSE FALSE
    END AS FLAG_CLOSE_DATE_PUSHED_1Q,
    CASE WHEN cur.CLOSE_DATE::DATE BETWEEN (SELECT NEXT_FQ_START FROM next_fq)
                                       AND DATEADD('day', 13, (SELECT NEXT_FQ_START FROM next_fq))
         THEN TRUE ELSE FALSE
    END AS FLAG_CLOSE_DATE_EARLY_NEXT_Q,
    CASE WHEN DAYOFWEEK(cur.CLOSE_DATE::DATE) IN (0, 6)
         THEN TRUE ELSE FALSE
    END AS FLAG_CLOSE_DATE_WEEKEND,
    CASE WHEN cur.TCV < cur.TOTAL_ACV AND cur.TOTAL_ACV > 0
         THEN TRUE ELSE FALSE
    END AS FLAG_TCV_LESS_THAN_ACV,
    CASE WHEN prev.TOTAL_ACV IS NOT NULL
              AND prev.TOTAL_ACV > 0
              AND ABS(cur.TOTAL_ACV - prev.TOTAL_ACV) / prev.TOTAL_ACV > 0.10
         THEN TRUE ELSE FALSE
    END AS FLAG_ACV_CHANGED_10PCT,
    CASE WHEN prev.TOTAL_ACV IS NOT NULL AND prev.TOTAL_ACV > 0
         THEN ROUND((cur.TOTAL_ACV - prev.TOTAL_ACV) / prev.TOTAL_ACV * 100, 1)
         ELSE NULL
    END AS ACV_CHANGE_PCT,
    'https://snowforce.my.salesforce.com/' || cur.OPPORTUNITY_ID AS SFDC_LINK
FROM SALES.RAVEN.SDA_OPPORTUNITY_VIEW cur
LEFT JOIN SALES.RAVEN.SDA_OPPORTUNITY_SNAPSHOT_VIEW prev
    ON cur.OPPORTUNITY_ID = prev.OPPORTUNITY_ID
    AND prev.DS = CURRENT_DATE() - 7
WHERE cur.DS = CURRENT_DATE()
  AND cur.IS_CAPACITY = TRUE
  AND cur.IS_CLOSED = FALSE
  AND cur.OPPORTUNITY_OWNER_NAME IN (
      SELECT EMPLOYEE_NAME
      FROM SALES.RAVEN.RAVEN_EMPLOYEE_WITH_REPORTING_CHAIN
      WHERE MANAGER_EMAIL = :user_email
        AND IS_ACTIVE = TRUE
  )
  AND (
      (prev.CLOSE_DATE IS NOT NULL AND cur.CLOSE_DATE::DATE >= DATEADD('month', 1, prev.CLOSE_DATE::DATE))
      OR (cur.CLOSE_DATE::DATE BETWEEN (SELECT NEXT_FQ_START FROM next_fq)
                                    AND DATEADD('day', 13, (SELECT NEXT_FQ_START FROM next_fq)))
      OR (DAYOFWEEK(cur.CLOSE_DATE::DATE) IN (0, 6))
      OR (cur.TCV < cur.TOTAL_ACV AND cur.TOTAL_ACV > 0 AND cur.FORECAST_STATUS != 'Omitted')
      OR (prev.TOTAL_ACV IS NOT NULL AND prev.TOTAL_ACV > 0 AND ABS(cur.TOTAL_ACV - prev.TOTAL_ACV) / prev.TOTAL_ACV > 0.10)
  )
ORDER BY cur.TOTAL_ACV DESC;

--------------------------------------------------------------------------------
-- Query 4.1: Rule 12 — Manager Deal Change Alerts (Summary)
-- Manager-only. Skip if :is_manager = FALSE.
--------------------------------------------------------------------------------
WITH fq AS (
    SELECT
        MIN(FQ_START) AS FQ_START,
        MIN(FQ_END)   AS FQ_END
    FROM SALES.RAVEN.SDA_OPPORTUNITY_VIEW
    WHERE DS = CURRENT_DATE() AND FQ_END >= CURRENT_DATE()
),
next_fq AS (
    SELECT MIN(FQ_START) AS NEXT_FQ_START
    FROM SALES.RAVEN.SDA_OPPORTUNITY_VIEW
    WHERE DS = CURRENT_DATE() AND FQ_START > (SELECT FQ_END FROM fq)
)
SELECT
    COUNT(*) AS TOTAL_FLAGGED,
    COUNT(DISTINCT cur.OPPORTUNITY_OWNER_NAME) AS REPS_AFFECTED,
    SUM(cur.TOTAL_ACV) AS TOTAL_ACV_FLAGGED,
    COUNT(CASE WHEN prev.CLOSE_DATE IS NOT NULL AND cur.CLOSE_DATE::DATE >= DATEADD('month', 1, prev.CLOSE_DATE::DATE) THEN 1 END) AS CLOSE_DATE_PUSHED_COUNT,
    COUNT(CASE WHEN cur.CLOSE_DATE::DATE BETWEEN (SELECT NEXT_FQ_START FROM next_fq) AND DATEADD('day', 13, (SELECT NEXT_FQ_START FROM next_fq)) THEN 1 END) AS EARLY_NEXT_Q_COUNT,
    COUNT(CASE WHEN DAYOFWEEK(cur.CLOSE_DATE::DATE) IN (0, 6) THEN 1 END) AS WEEKEND_CLOSE_DATE_COUNT,
    COUNT(CASE WHEN cur.TCV < cur.TOTAL_ACV AND cur.TOTAL_ACV > 0 AND cur.FORECAST_STATUS != 'Omitted' THEN 1 END) AS TCV_LT_ACV_COUNT,
    COUNT(CASE WHEN prev.TOTAL_ACV IS NOT NULL AND prev.TOTAL_ACV > 0 AND ABS(cur.TOTAL_ACV - prev.TOTAL_ACV) / prev.TOTAL_ACV > 0.10 THEN 1 END) AS ACV_CHANGED_10PCT_COUNT
FROM SALES.RAVEN.SDA_OPPORTUNITY_VIEW cur
LEFT JOIN SALES.RAVEN.SDA_OPPORTUNITY_SNAPSHOT_VIEW prev
    ON cur.OPPORTUNITY_ID = prev.OPPORTUNITY_ID
    AND prev.DS = CURRENT_DATE() - 7
WHERE cur.DS = CURRENT_DATE()
  AND cur.IS_CAPACITY = TRUE
  AND cur.IS_CLOSED = FALSE
  AND cur.OPPORTUNITY_OWNER_NAME IN (
      SELECT EMPLOYEE_NAME
      FROM SALES.RAVEN.RAVEN_EMPLOYEE_WITH_REPORTING_CHAIN
      WHERE MANAGER_EMAIL = :user_email
        AND IS_ACTIVE = TRUE
  )
  AND (
      (prev.CLOSE_DATE IS NOT NULL AND cur.CLOSE_DATE::DATE >= DATEADD('month', 1, prev.CLOSE_DATE::DATE))
      OR (cur.CLOSE_DATE::DATE BETWEEN (SELECT NEXT_FQ_START FROM next_fq) AND DATEADD('day', 13, (SELECT NEXT_FQ_START FROM next_fq)))
      OR (DAYOFWEEK(cur.CLOSE_DATE::DATE) IN (0, 6))
      OR (cur.TCV < cur.TOTAL_ACV AND cur.TOTAL_ACV > 0 AND cur.FORECAST_STATUS != 'Omitted')
      OR (prev.TOTAL_ACV IS NOT NULL AND prev.TOTAL_ACV > 0 AND ABS(cur.TOTAL_ACV - prev.TOTAL_ACV) / prev.TOTAL_ACV > 0.10)
  );
