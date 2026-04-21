-- DCP Revenue & Consumption Breakdown
-- Breaks down partner-driven revenue by consumption type, partner, and time period
-- Sources: sales.raven.partner_dcp_consumption_view
--
-- MODE: Customer vs Partner
-- ┌─────────────────┬───────────────────────────────────────────────────────────────┐
-- │ CUSTOMER MODE   │ Filter: salesforce_account_id = :salesforce_account_id       │
-- │                 │ Shows: DCP revenue by partner for this customer              │
-- ├─────────────────┼───────────────────────────────────────────────────────────────┤
-- │ PARTNER MODE    │ Filter: partner_salesforce_account_id = :partner_id          │
-- │                 │ Shows: DCP revenue by customer for this partner              │
-- └─────────────────┴───────────────────────────────────────────────────────────────┘

-- =====================
-- CUSTOMER MODE QUERY
-- =====================
SELECT
    dcp.partner_name,
    dcp.partner_salesforce_account_name,
    dcp.dcp_consumption_type,
    dcp.app_source,
    dcp.app_type,
    dcp.dcp_pdm_name,
    dcp.dcp_managed_unmanaged,
    dcp.is_managed_account,
    SUM(CASE WHEN dcp.is_current_ytd = 'Y' THEN dcp.dcp_revenue ELSE 0 END) AS dcp_revenue_ytd,
    SUM(CASE WHEN dcp.is_current_qtd = 'Y' THEN dcp.dcp_revenue ELSE 0 END) AS dcp_revenue_qtd,
    SUM(CASE WHEN dcp.is_previous_ytd = 'Y' THEN dcp.dcp_revenue ELSE 0 END) AS dcp_revenue_prev_ytd,
    SUM(CASE WHEN dcp.is_current_ytd = 'Y' THEN dcp.dcp_credits ELSE 0 END) AS dcp_credits_ytd
FROM sales.raven.partner_dcp_consumption_view dcp
WHERE dcp.salesforce_account_id = :salesforce_account_id
GROUP BY
    dcp.partner_name, dcp.partner_salesforce_account_name, dcp.dcp_consumption_type,
    dcp.app_source, dcp.app_type, dcp.dcp_pdm_name, dcp.dcp_managed_unmanaged, dcp.is_managed_account
ORDER BY dcp_revenue_ytd DESC;

-- =====================
-- PARTNER MODE QUERY
-- =====================
SELECT
    dcp.customer_salesforce_account_name AS customer_name,
    dcp.salesforce_account_id AS customer_id,
    dcp.dcp_consumption_type,
    dcp.app_source,
    dcp.app_type,
    SUM(CASE WHEN dcp.is_current_ytd = 'Y' THEN dcp.dcp_revenue ELSE 0 END) AS dcp_revenue_ytd,
    SUM(CASE WHEN dcp.is_current_qtd = 'Y' THEN dcp.dcp_revenue ELSE 0 END) AS dcp_revenue_qtd,
    SUM(CASE WHEN dcp.is_current_ytd = 'Y' THEN dcp.dcp_credits ELSE 0 END) AS dcp_credits_ytd
FROM sales.raven.partner_dcp_consumption_view dcp
WHERE dcp.partner_salesforce_account_id = :partner_id
GROUP BY
    dcp.customer_salesforce_account_name, dcp.salesforce_account_id,
    dcp.dcp_consumption_type, dcp.app_source, dcp.app_type
ORDER BY dcp_revenue_ytd DESC;
