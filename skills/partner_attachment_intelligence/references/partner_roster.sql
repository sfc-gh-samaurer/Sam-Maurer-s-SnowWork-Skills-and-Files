-- Partner Roster & Roles
-- Lists partners/customers with their roles and deal involvement
-- Sources: sales.raven.sda_opportunity_w_partner_split_view
--
-- MODE: Customer vs Partner
-- ┌─────────────────┬───────────────────────────────────────────────────────────────┐
-- │ CUSTOMER MODE   │ Filter: salesforce_account_id = :salesforce_account_id       │
-- │                 │ Shows: All partners attached to this customer                │
-- ├─────────────────┼───────────────────────────────────────────────────────────────┤
-- │ PARTNER MODE    │ Filter: partner_id = :partner_id                             │
-- │                 │ Shows: All customers this partner is attached to             │
-- └─────────────────┴───────────────────────────────────────────────────────────────┘

-- =====================
-- CUSTOMER MODE QUERY
-- =====================
SELECT
    ps.partner_name,
    ps.parent_partner_name,
    ps.partner_subtype,
    ps.partner_programs_enrolled,
    COUNT(DISTINCT ps.opportunity_id) AS num_opportunities,
    COUNT(DISTINCT CASE WHEN ps.deal_reg_name IS NOT NULL THEN ps.opportunity_id END) AS deal_reg_count,
    LISTAGG(DISTINCT ps.partner_role, ', ') WITHIN GROUP (ORDER BY ps.partner_role) AS roles_played,
    MAX(ps.cloud_partner) AS cloud_partner,
    MAX(ps.channel_partner) AS channel_partner,
    MAX(ps.cosell_partner) AS cosell_partner
FROM sales.raven.sda_opportunity_w_partner_split_view ps
WHERE ps.salesforce_account_id = :salesforce_account_id
GROUP BY ps.partner_name, ps.parent_partner_name, ps.partner_subtype, ps.partner_programs_enrolled
ORDER BY num_opportunities DESC;

-- =====================
-- PARTNER MODE QUERY
-- =====================
SELECT
    ps.salesforce_account_name AS customer_name,
    ps.salesforce_account_id AS customer_id,
    COUNT(DISTINCT ps.opportunity_id) AS num_opportunities,
    COUNT(DISTINCT CASE WHEN ps.deal_reg_name IS NOT NULL THEN ps.opportunity_id END) AS deal_reg_count,
    LISTAGG(DISTINCT ps.partner_role, ', ') WITHIN GROUP (ORDER BY ps.partner_role) AS roles_played,
    MAX(ps.cloud_partner) AS cloud_partner,
    MAX(ps.channel_partner) AS channel_partner,
    MAX(ps.cosell_partner) AS cosell_partner
FROM sales.raven.sda_opportunity_w_partner_split_view ps
WHERE ps.partner_id = :partner_id
GROUP BY ps.salesforce_account_name, ps.salesforce_account_id
ORDER BY num_opportunities DESC;
