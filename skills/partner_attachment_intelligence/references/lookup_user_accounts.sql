-- Lookup accounts by user email or name
-- Use to identify which accounts the current user owns/supports

SELECT DISTINCT
    salesforce_account_id,
    salesforce_account_name,
    segment,
    sales_area,
    territory,
    salesforce_owner_name AS ae_name,
    lead_sales_engineer_name AS se_name,
    dm,
    rvp
FROM sales.raven.d_salesforce_account_customers
WHERE LOWER(rep_email) = LOWER(:user_email)
   OR LOWER(salesforce_owner_name) LIKE LOWER('%:user_name%')
   OR LOWER(lead_sales_engineer_name) LIKE LOWER('%:user_name%')
LIMIT 20;
