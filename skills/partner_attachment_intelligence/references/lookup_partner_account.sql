-- Lookup partner account by name using Cortex Search Service
-- Step 1: Use SEARCH_PREVIEW to fuzzy match partner name
-- Step 2: Get full partner details using the matched name
--
-- CRITICAL: Only request indexed columns from SEARCH_PREVIEW!
-- The PARTNER_ACCOUNT_NAME_SEARCH_SERVICE only indexes: name
-- DO NOT add salesforce_account_id, partner_id, etc. to the columns array - it will fail!
-- Join back to d_salesforce_account_customers to get additional columns.

-- Search for partner account name
WITH search_result AS (
    SELECT SNOWFLAKE.CORTEX.SEARCH_PREVIEW(
        'SALES.RAVEN.PARTNER_ACCOUNT_NAME_SEARCH_SERVICE',
        '{"query": ":partner_name", "columns": ["name"], "limit": 5}'
    ) AS result
),
matched_names AS (
    SELECT 
        PARSE_JSON(result)['results'][0]['name']::STRING AS matched_name_1,
        PARSE_JSON(result)['results'][1]['name']::STRING AS matched_name_2,
        PARSE_JSON(result)['results'][2]['name']::STRING AS matched_name_3,
        PARSE_JSON(result)['results'][3]['name']::STRING AS matched_name_4,
        PARSE_JSON(result)['results'][4]['name']::STRING AS matched_name_5
    FROM search_result
)
SELECT DISTINCT
    a.salesforce_account_id AS partner_salesforce_account_id,
    a.salesforce_account_name AS partner_name,
    a.type,
    a.segment,
    a.sales_area,
    a.territory,
    a.salesforce_owner_name AS partner_account_owner,
    a.is_dcp_partner,
    a.dcp_tier,
    a.is_dcs_partner,
    a.dcs_tier
FROM sales.raven.d_salesforce_account_customers a
CROSS JOIN matched_names m
WHERE a.salesforce_account_name IN (m.matched_name_1, m.matched_name_2, m.matched_name_3, m.matched_name_4, m.matched_name_5)
  AND a.type = 'Partner'
LIMIT 10;
