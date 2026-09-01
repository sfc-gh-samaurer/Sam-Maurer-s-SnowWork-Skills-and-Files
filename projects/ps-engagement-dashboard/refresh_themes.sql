-- Refresh Engagement Themes Cache (4-Level)
-- Synthesizes PM status comments into thematic insights using Cortex COMPLETE.
-- Model: claude-4-sonnet (all levels)
--
-- Level 1: District × Engagement Type — extract from raw status texts
-- Level 2: Region × Engagement Type — synthesize district themes
-- Level 3: National × Engagement Type — synthesize region themes
-- Level 4: Regional POV (_POV) — cross-engagement-type narrative per region
--
-- Run weekly (after refresh_cache.sql). Execute statements in order.
--   Step 1: CTAS (district × engagement type — ~160 groups)
--   Step 2: INSERT (region × engagement type — synthesizes step 1)
--   Step 3: INSERT (national × engagement type — synthesizes step 2)
--   Step 4: INSERT (regional POV — synthesizes step 2)
--
-- Prerequisites: SDA_USE_CASES_CACHE must be current.

-- ══════════════════════════════════════════════════════════
-- STEP 1: District × Engagement Type (raw → district themes)
-- ══════════════════════════════════════════════════════════
CREATE OR REPLACE TABLE PST.PS_APPS_DEV.ENGAGEMENT_THEMES_CACHE AS
WITH ps_accounts AS (
    SELECT DISTINCT
        uc.REGION,
        uc.DISTRICT,
        uc.ACCOUNT_NAME,
        CASE
            WHEN uc.PS_ENGAGEMENT IN ('Implementation','Advisory','Proposing','Support')
            THEN uc.PS_ENGAGEMENT
            ELSE 'Unspecified'
        END AS ENGAGEMENT_TYPE
    FROM PST.PS_APPS_DEV.SDA_USE_CASES_CACHE uc
    WHERE uc.PS_ENGAGEMENT IN ('Implementation','Advisory','Proposing','Support')
       OR uc.IS_PS_ENGAGED = TRUE
),
project_statuses AS (
    SELECT
        ACCOUNT_NAME,
        LEFT(PROJECT_STATUS_COMMENTS, 400) AS STATUS_EXCERPT
    FROM SMARTSHEET_DB.RAW_SMARTSHEET.SHEET_1030823650217860_SFDC_CONNECTOR_SHEET_PROJECTS
    WHERE ACTIVE = 'true'
      AND TRIM(NVL(PROJECT_STATUS_COMMENTS, '')) != ''
),
grouped AS (
    SELECT
        pa.REGION,
        pa.DISTRICT,
        pa.ENGAGEMENT_TYPE,
        COUNT(DISTINCT pa.ACCOUNT_NAME) AS ACCOUNT_COUNT,
        COUNT(DISTINCT ps.ACCOUNT_NAME) AS ACCOUNTS_WITH_STATUS,
        LISTAGG(ps.STATUS_EXCERPT, '\n')
            WITHIN GROUP (ORDER BY pa.ACCOUNT_NAME) AS STATUS_BLOCK
    FROM ps_accounts pa
    JOIN project_statuses ps ON pa.ACCOUNT_NAME = ps.ACCOUNT_NAME
    GROUP BY pa.REGION, pa.DISTRICT, pa.ENGAGEMENT_TYPE
)
SELECT
    DISTRICT,
    REGION,
    ENGAGEMENT_TYPE,
    ACCOUNT_COUNT,
    ACCOUNTS_WITH_STATUS,
    SNOWFLAKE.CORTEX.COMPLETE(
        'claude-4-sonnet',
        'You are analyzing PS project status updates for the "'
        || ENGAGEMENT_TYPE || '" engagement type in the ' || DISTRICT || ' district.\n\n'
        || CASE ENGAGEMENT_TYPE
            WHEN 'Implementation' THEN 'IMPLEMENTATION means hands-on building: migrations, deployments, data pipeline construction, ETL development, go-live execution, environment setup, code development, testing (SIT/UAT).'
            WHEN 'Advisory' THEN 'ADVISORY means strategic guidance: architecture reviews, best-practice workshops, design sessions, roadmap planning, POCs, governance frameworks, performance tuning recommendations.'
            WHEN 'Proposing' THEN 'PROPOSING means pre-sales scoping: discovery workshops, requirements gathering, solution design, proposal development, feasibility assessments, value engineering.'
            WHEN 'Support' THEN 'SUPPORT means ongoing assistance: troubleshooting, optimization, operational reviews, incident resolution, upgrade planning, knowledge transfer, runbook creation.'
            ELSE 'UNSPECIFIED means PS is engaged but the specific role is not yet categorized.'
           END
        || '\n\nFrom the status updates below, extract 3-5 activities that specifically match this engagement type. '
        || 'Only include activities ACTUALLY DESCRIBED in the text — do not infer or generalize. '
        || 'IGNORE activities that belong to other engagement types. '
        || 'Be precise — name the specific technology, platform, or deliverable. '
        || 'Return ONLY a comma-separated list. No account names. No sentences.\n\n'
        || LEFT(STATUS_BLOCK, 4000)
    ) AS THEME_SUMMARY,
    CURRENT_TIMESTAMP() AS REFRESHED_AT
FROM grouped;

-- ══════════════════════════════════════════════════════════
-- STEP 2: Region × Engagement Type (synthesize district themes)
-- ══════════════════════════════════════════════════════════
INSERT INTO PST.PS_APPS_DEV.ENGAGEMENT_THEMES_CACHE
SELECT
    NULL AS DISTRICT,
    REGION,
    ENGAGEMENT_TYPE,
    SUM(ACCOUNT_COUNT) AS ACCOUNT_COUNT,
    SUM(ACCOUNTS_WITH_STATUS) AS ACCOUNTS_WITH_STATUS,
    SNOWFLAKE.CORTEX.COMPLETE(
        'claude-4-sonnet',
        'Below are PS activity lists from different districts in the '
        || REGION || ' region for ' || ENGAGEMENT_TYPE || ' engagements.\n\n'
        || 'Identify the 3-5 most common SPECIFIC activities across districts. '
        || 'Only include activities that actually appear in the input — do not infer or generalize. '
        || 'Return ONLY a comma-separated list. No district names. No sentences.\n\n'
        || LISTAGG(DISTRICT || ': ' || THEME_SUMMARY, '\n')
            WITHIN GROUP (ORDER BY DISTRICT)
    ) AS THEME_SUMMARY,
    CURRENT_TIMESTAMP() AS REFRESHED_AT
FROM PST.PS_APPS_DEV.ENGAGEMENT_THEMES_CACHE
WHERE DISTRICT IS NOT NULL
GROUP BY REGION, ENGAGEMENT_TYPE;

-- ══════════════════════════════════════════════════════════
-- STEP 3: National × Engagement Type (synthesize region themes)
-- ══════════════════════════════════════════════════════════
INSERT INTO PST.PS_APPS_DEV.ENGAGEMENT_THEMES_CACHE
SELECT
    NULL AS DISTRICT,
    'NATIONAL' AS REGION,
    ENGAGEMENT_TYPE,
    SUM(ACCOUNT_COUNT) AS ACCOUNT_COUNT,
    SUM(ACCOUNTS_WITH_STATUS) AS ACCOUNTS_WITH_STATUS,
    SNOWFLAKE.CORTEX.COMPLETE(
        'claude-4-sonnet',
        'Below are PS activity lists from different regions for '
        || ENGAGEMENT_TYPE || ' engagements.\n\n'
        || 'Identify the 3-5 most common SPECIFIC activities across regions '
        || 'that are DISTINCTIVE to the ' || ENGAGEMENT_TYPE || ' role. '
        || 'Only include activities that actually appear in the input — do not add new ones. '
        || 'Avoid generic activities that could apply to any engagement type. '
        || 'Return ONLY a comma-separated list. No region names. No sentences.\n\n'
        || LISTAGG(REGION || ': ' || THEME_SUMMARY, '\n')
            WITHIN GROUP (ORDER BY REGION)
    ) AS THEME_SUMMARY,
    CURRENT_TIMESTAMP() AS REFRESHED_AT
FROM PST.PS_APPS_DEV.ENGAGEMENT_THEMES_CACHE
WHERE DISTRICT IS NULL AND REGION != 'NATIONAL' AND ENGAGEMENT_TYPE != '_POV'
GROUP BY ENGAGEMENT_TYPE;

-- ══════════════════════════════════════════════════════════
-- STEP 4: Regional POV (cross-engagement-type narrative per region)
-- Reads step 2 results and synthesizes across engagement types.
-- ══════════════════════════════════════════════════════════
INSERT INTO PST.PS_APPS_DEV.ENGAGEMENT_THEMES_CACHE
SELECT
    NULL AS DISTRICT,
    REGION,
    '_POV' AS ENGAGEMENT_TYPE,
    NULL AS ACCOUNT_COUNT,
    NULL AS ACCOUNTS_WITH_STATUS,
    SNOWFLAKE.CORTEX.COMPLETE(
        'claude-4-sonnet',
        'You are a PS leadership advisor. Below are specific PS activities '
        || 'by engagement type for the ' || REGION || ' region. '
        || 'Synthesize into 3-5 cross-cutting THEMES with a one-sentence narrative each. '
        || 'Only reference activities actually listed below — do not add new ones. '
        || 'Format each as: **Theme Name** — one sentence narrative. '
        || 'No bullet points. Separate themes with two newlines.\n\n'
        || LISTAGG(ENGAGEMENT_TYPE || ': ' || THEME_SUMMARY, '\n')
            WITHIN GROUP (ORDER BY ENGAGEMENT_TYPE)
    ) AS THEME_SUMMARY,
    CURRENT_TIMESTAMP() AS REFRESHED_AT
FROM PST.PS_APPS_DEV.ENGAGEMENT_THEMES_CACHE
WHERE DISTRICT IS NULL AND REGION != 'NATIONAL' AND ENGAGEMENT_TYPE != '_POV'
GROUP BY REGION;
