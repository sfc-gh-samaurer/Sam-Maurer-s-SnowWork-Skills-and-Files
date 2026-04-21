-- Partner-Attached Use Cases
-- Shows use cases that have partner involvement (implementation, co-sell, or DCP partners)
-- Sources: sales.raven.sda_use_case_view
--
-- MODE: Customer vs Partner
-- ┌─────────────────┬───────────────────────────────────────────────────────────────┐
-- │ CUSTOMER MODE   │ Filter: salesforce_account_id = :salesforce_account_id       │
-- │                 │ Shows: Use cases for this customer with partner involvement  │
-- ├─────────────────┼───────────────────────────────────────────────────────────────┤
-- │ PARTNER MODE    │ Filter: ILIKE '%:partner_name%' on partner_ls fields         │
-- │                 │ Shows: All use cases where this partner is involved          │
-- │                 │ Fields: implementation_services_partner_ls,                  │
-- │                 │         co_sell_services_partner_ls, dcp_partner_ls          │
-- └─────────────────┴───────────────────────────────────────────────────────────────┘

-- =====================
-- CUSTOMER MODE QUERY
-- =====================
SELECT
    uc.use_case_name,
    uc.use_case_number,
    uc.use_case_status,
    uc.use_case_stage,
    uc.account_name,
    uc.salesforce_account_id,
    uc.industry_use_case,
    uc.workloads,
    uc.use_case_acv,
    uc.partners,
    uc.implementer,
    uc.implementation_services_partner_ls,
    uc.co_sell_services_partner_ls,
    uc.dcp_partner_ls,
    uc.partner_comments,
    uc.owner_name,
    uc.is_won,
    uc.is_in_pursuit,
    uc.is_in_implementation,
    uc.is_in_production,
    uc.go_live_date,
    uc.decision_date
FROM sales.raven.sda_use_case_view uc
WHERE uc.salesforce_account_id = :salesforce_account_id
  AND (
    uc.partners IS NOT NULL
    OR uc.implementer IS NOT NULL
    OR uc.implementation_services_partner_ls IS NOT NULL
    OR uc.co_sell_services_partner_ls IS NOT NULL
    OR uc.dcp_partner_ls IS NOT NULL
  )
ORDER BY
    CASE WHEN uc.is_in_pursuit THEN 1
         WHEN uc.is_in_implementation THEN 2
         WHEN uc.is_in_production THEN 3
         WHEN uc.is_won THEN 4
         ELSE 5
    END,
    uc.use_case_acv DESC;

-- =====================
-- PARTNER MODE QUERY
-- =====================
SELECT
    uc.use_case_name,
    uc.use_case_number,
    uc.use_case_status,
    uc.use_case_stage,
    uc.account_name AS customer_name,
    uc.salesforce_account_id AS customer_id,
    uc.use_case_acv,
    uc.implementer,
    uc.implementation_services_partner_ls,
    uc.co_sell_services_partner_ls,
    uc.dcp_partner_ls,
    uc.is_won,
    uc.is_in_pursuit,
    uc.is_in_implementation,
    uc.is_in_production
FROM sales.raven.sda_use_case_view uc
WHERE uc.implementation_services_partner_ls ILIKE '%:partner_name%'
   OR uc.co_sell_services_partner_ls ILIKE '%:partner_name%'
   OR uc.dcp_partner_ls ILIKE '%:partner_name%'
ORDER BY uc.use_case_acv DESC;
