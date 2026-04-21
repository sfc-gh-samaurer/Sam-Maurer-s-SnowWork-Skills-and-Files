-- Crossbeam Dark Edges (Co-Sell Opportunities)
-- Shows partners that share this account as a joint customer via Crossbeam
-- Sources: sales.raven.partner_crossbeam_view
--
-- MODE: Customer vs Partner
-- ┌─────────────────┬───────────────────────────────────────────────────────────────┐
-- │ CUSTOMER MODE   │ Filter: salesforce_account_id = :salesforce_account_id       │
-- │                 │ Shows: Partners identifying this customer as mutual          │
-- ├─────────────────┼───────────────────────────────────────────────────────────────┤
-- │ PARTNER MODE    │ Filter: partner_name = :partner_name                         │
-- │                 │ Shows: Customers that this partner identifies as mutual     │
-- └─────────────────┴───────────────────────────────────────────────────────────────┘

-- =====================
-- CUSTOMER MODE QUERY
-- =====================
SELECT
    cb.partner_name,
    cb.partner_domain,
    cb.joint_customer_salesforce_account_name,
    cb.joint_customer_industry,
    cb.joint_customer_agreement_types,
    cb.has_stable_edge,
    cb.n_stable_edges,
    cb.stable_edges
FROM sales.raven.partner_crossbeam_view cb
WHERE cb.salesforce_account_id = :salesforce_account_id
ORDER BY cb.n_stable_edges DESC, cb.partner_name;

-- =====================
-- PARTNER MODE QUERY
-- =====================
SELECT
    cb.joint_customer_salesforce_account_name,
    cb.salesforce_account_id,
    cb.joint_customer_industry,
    cb.joint_customer_agreement_types,
    cb.has_stable_edge,
    cb.n_stable_edges,
    cb.stable_edges
FROM sales.raven.partner_crossbeam_view cb
WHERE cb.partner_name = :partner_name
ORDER BY cb.n_stable_edges DESC, cb.joint_customer_salesforce_account_name;
