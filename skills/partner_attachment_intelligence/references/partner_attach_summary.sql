-- Partner Attachment Summary
-- Provides a high-level overview of partner attachment metrics
-- Sources: sales.raven.sda_opportunity_snapshot_view, sales.raven.sda_opportunity_w_partner_split_view
--
-- MODE: Customer vs Partner
-- ┌─────────────────┬───────────────────────────────────────────────────────────────┐
-- │ CUSTOMER MODE   │ Filter: salesforce_account_id = :salesforce_account_id       │
-- │                 │ Shows: All partners attached to this customer's opps         │
-- ├─────────────────┼───────────────────────────────────────────────────────────────┤
-- │ PARTNER MODE    │ Filter: partner_id = :partner_id                             │
-- │                 │ Shows: All customers this partner is attached to             │
-- └─────────────────┴───────────────────────────────────────────────────────────────┘

-- =====================
-- CUSTOMER MODE QUERY
-- =====================
WITH account_opps AS (
    SELECT
        o.opportunity_id,
        o.opportunity_name,
        o.salesforce_account_id,
        o.account_name AS salesforce_account_name,
        o.stage_name,
        o.is_won,
        o.is_closed,
        o.close_date,
        o.total_acv,
        o.forecast_status
    FROM sales.raven.sda_opportunity_snapshot_view o
    WHERE o.salesforce_account_id = :salesforce_account_id
      AND o.ds = (SELECT MAX(ds) FROM sales.raven.sda_opportunity_snapshot_view)
),
partner_opps AS (
    SELECT
        ps.opportunity_id,
        ps.partner_name,
        ps.partner_role,
        ps.partner_subtype,
        ps.cloud_partner,
        ps.channel_partner,
        ps.cosell_partner,
        ps.partner_split,
        ps.deal_reg_name
    FROM sales.raven.sda_opportunity_w_partner_split_view ps
    WHERE ps.salesforce_account_id = :salesforce_account_id
)
SELECT
    ao.salesforce_account_id,
    ao.salesforce_account_name,
    COUNT(DISTINCT ao.opportunity_id) AS total_opportunities,
    COUNT(DISTINCT po.opportunity_id) AS partner_attached_opportunities,
    ROUND(COUNT(DISTINCT po.opportunity_id) * 100.0 / NULLIF(COUNT(DISTINCT ao.opportunity_id), 0), 1) AS partner_attach_rate_pct,
    COUNT(DISTINCT CASE WHEN ao.is_won THEN ao.opportunity_id END) AS total_won,
    COUNT(DISTINCT CASE WHEN ao.is_won AND po.opportunity_id IS NOT NULL THEN ao.opportunity_id END) AS partner_attached_won,
    SUM(CASE WHEN ao.is_won THEN ao.total_acv ELSE 0 END) AS total_won_acv,
    SUM(CASE WHEN ao.is_won AND po.opportunity_id IS NOT NULL THEN ao.total_acv ELSE 0 END) AS partner_attached_won_acv,
    COUNT(DISTINCT po.partner_name) AS distinct_partners_involved
FROM account_opps ao
LEFT JOIN partner_opps po ON ao.opportunity_id = po.opportunity_id
GROUP BY ao.salesforce_account_id, ao.salesforce_account_name;

-- =====================
-- PARTNER MODE QUERY
-- =====================
WITH partner_opps AS (
    SELECT
        ps.opportunity_id,
        ps.salesforce_account_id,
        ps.salesforce_account_name,
        ps.partner_name,
        ps.deal_reg_name
    FROM sales.raven.sda_opportunity_w_partner_split_view ps
    WHERE ps.partner_id = :partner_id
),
opp_details AS (
    SELECT o.opportunity_id, o.is_won, o.total_acv
    FROM sales.raven.sda_opportunity_snapshot_view o
    WHERE o.ds = (SELECT MAX(ds) FROM sales.raven.sda_opportunity_snapshot_view)
)
SELECT
    :partner_id AS partner_salesforce_account_id,
    MAX(po.partner_name) AS partner_name,
    COUNT(DISTINCT po.opportunity_id) AS total_opportunities_involved,
    COUNT(DISTINCT po.salesforce_account_id) AS distinct_customers,
    COUNT(DISTINCT CASE WHEN od.is_won THEN po.opportunity_id END) AS won_opportunities,
    SUM(CASE WHEN od.is_won THEN od.total_acv ELSE 0 END) AS total_won_acv,
    COUNT(DISTINCT po.deal_reg_name) AS deal_registrations
FROM partner_opps po
LEFT JOIN opp_details od ON po.opportunity_id = od.opportunity_id;
