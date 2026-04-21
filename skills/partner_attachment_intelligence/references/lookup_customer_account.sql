-- Lookup customer account by name using Cortex Search Service
-- Step 1: Use SEARCH_PREVIEW to fuzzy match customer name
-- Step 2: Get full account details using the matched name
--
-- CRITICAL: Only request indexed columns from SEARCH_PREVIEW!
-- The CUSTOMER_INDIVIDUAL_NAME_SEARCH_SERVICE only indexes: salesforce_account_name
-- DO NOT add salesforce_account_id, ae_name, se_name, etc. to the columns array - it will fail!
-- Join back to d_salesforce_account_customers to get additional columns.

-- Search for customer account name
WITH search_result AS (
    SELECT SNOWFLAKE.CORTEX.SEARCH_PREVIEW(
        'SALES.RAVEN.CUSTOMER_INDIVIDUAL_NAME_SEARCH_SERVICE',
        '{"query": ":account_name", "columns": ["salesforce_account_name"], "limit": 5}'
    ) AS result
),
matched_names AS (
    SELECT 
        PARSE_JSON(result)['results'][0]['salesforce_account_name']::STRING AS matched_name_1,
        PARSE_JSON(result)['results'][1]['salesforce_account_name']::STRING AS matched_name_2,
        PARSE_JSON(result)['results'][2]['salesforce_account_name']::STRING AS matched_name_3,
        PARSE_JSON(result)['results'][3]['salesforce_account_name']::STRING AS matched_name_4,
        PARSE_JSON(result)['results'][4]['salesforce_account_name']::STRING AS matched_name_5
    FROM search_result
)
SELECT DISTINCT
    a.salesforce_account_id,
    a.salesforce_account_name,
    a.type,
    a.segment,
    a.sales_area,
    a.territory,
    a.salesforce_owner_name AS ae_name,
    a.lead_sales_engineer_name AS se_name,
    a.dm,
    a.rvp
FROM sales.raven.d_salesforce_account_customers a
CROSS JOIN matched_names m
WHERE a.salesforce_account_name IN (m.matched_name_1, m.matched_name_2, m.matched_name_3, m.matched_name_4, m.matched_name_5)
  AND a.type = 'Customer'
LIMIT 10;
