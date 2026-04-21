-- Partner-Influenced Pipeline (Open Opportunities)
-- Shows currently open opportunities with partner involvement
-- Sources: sales.raven.sda_opportunity_snapshot_view, sales.raven.sda_opportunity_w_partner_split_view
--
-- MODE: Customer vs Partner
-- ┌─────────────────┬───────────────────────────────────────────────────────────────┐
-- │ CUSTOMER MODE   │ Filter: salesforce_account_id = :salesforce_account_id       │
-- │                 │ Shows: Open opps for this customer with partner attachment   │
-- ├─────────────────┼───────────────────────────────────────────────────────────────┤
-- │ PARTNER MODE    │ Filter: partner_id = :partner_id                             │
-- │                 │ Shows: All open opps this partner is attached to             │
-- └─────────────────┴───────────────────────────────────────────────────────────────┘

-- =====================
-- CUSTOMER MODE QUERY
-- =====================
SELECT
    o.opportunity_name,
    o.stage_name,
    o.forecast_status,
    o.close_date,
    o.total_acv AS acv,
    ps.partner_name,
    ps.partner_role,
    ps.partner_subtype,
    ps.cloud_partner,
    ps.channel_partner,
    ps.cosell_partner,
    ps.partner_split,
    ps.deal_reg_name
FROM sales.raven.sda_opportunity_snapshot_view o
INNER JOIN sales.raven.sda_opportunity_w_partner_split_view ps
    ON o.opportunity_id = ps.opportunity_id
WHERE o.salesforce_account_id = :salesforce_account_id
  AND o.is_closed = FALSE
  AND o.ds = (SELECT MAX(ds) FROM sales.raven.sda_opportunity_snapshot_view)
ORDER BY o.close_date ASC, o.total_acv DESC;

-- =====================
-- PARTNER MODE QUERY
-- =====================
SELECT
    o.opportunity_name,
    o.account_name AS customer_name,
    o.salesforce_account_id AS customer_id,
    o.stage_name,
    o.forecast_status,
    o.close_date,
    o.total_acv AS acv,
    ps.partner_role,
    ps.cloud_partner,
    ps.cosell_partner,
    ps.partner_split,
    ps.deal_reg_name
FROM sales.raven.sda_opportunity_snapshot_view o
INNER JOIN sales.raven.sda_opportunity_w_partner_split_view ps
    ON o.opportunity_id = ps.opportunity_id
WHERE ps.partner_id = :partner_id
  AND o.is_closed = FALSE
  AND o.ds = (SELECT MAX(ds) FROM sales.raven.sda_opportunity_snapshot_view)
ORDER BY o.close_date ASC, o.total_acv DESC;
