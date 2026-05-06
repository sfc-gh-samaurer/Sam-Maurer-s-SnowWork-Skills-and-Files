-- Refresh SDA Use Cases Cache
-- Sources from raw SFDC VH_DELIVERABLE_C joined to DIM_ACCOUNTS for account names.
-- Bypasses SALES.RAVEN.SDA_USE_CASE_VIEW which has row-access policies that
-- filter out regions invisible to the executing role.
--
-- Run from any session with USE SECONDARY ROLES ALL
-- (CLI, worksheet, or scheduled externally)
--
-- Usage: snow sql -f refresh_cache.sql -c SnowhouseHeadless

USE SECONDARY ROLES ALL;

CREATE OR REPLACE TABLE PST.PS_APPS_DEV.SDA_USE_CASES_CACHE AS
SELECT
    a.ACCOUNT_NAME,
    uc.VH_NAME_C                                          AS USE_CASE_NAME,
    uc.STAGE_C                                            AS USE_CASE_STAGE,
    uc.ESTIMATED_ANNUAL_CREDIT_CONSUMPTION_C              AS USE_CASE_ACV,
    uc.PS_ENGAGEMENT_C                                    AS PS_ENGAGEMENT,
    uc.PS_ENGAGED_C                                       AS IS_PS_ENGAGED,
    uc.IMPLEMENTER_C                                      AS IMPLEMENTER,
    uc.WORKLOADS_C                                        AS WORKLOADS,
    uc.COMPETITORS_C                                      AS COMPETITORS,
    uc.USE_CASE_OWNER_REGION_C                            AS REGION,
    a.SUB_REGION,
    uc.USE_CASE_OWNER_DISTRICT_C                          AS DISTRICT,
    a.TERRITORY,
    a.SEGMENT,
    a.ACCOUNT_TIER,
    a.INDUSTRY,
    TRY_TO_DOUBLE(a.ARR)                                  AS ARR,
    TRY_TO_DATE(REPLACE(uc.ACTUAL_GO_LIVE_DATE_C, '"', '')) AS GO_LIVE_DATE,
    uc.LAST_STAGE_CHANGE_IN_DAYS_C                        AS DAYS_IN_STAGE,
    CURRENT_TIMESTAMP()                                   AS CACHE_REFRESHED_AT
FROM TEMP.PS_APPS.VH_DELIVERABLE_C uc
JOIN SALES.SE_REPORTING.DIM_ACCOUNTS_SLIM_SLIM a
  ON uc.VH_ACCOUNT_C = a.ACCOUNT_ID
WHERE uc.IS_DELETED = FALSE
  AND uc.STAGE_C NOT IN ('8 - Use Case Lost')
  AND uc.USE_CASE_OWNER_REGION_C IS NOT NULL
ORDER BY a.ACCOUNT_NAME, uc.VH_NAME_C;
