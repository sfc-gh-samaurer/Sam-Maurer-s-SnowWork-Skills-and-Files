-- Deal Registrations
-- Shows all partner deal registrations (approved, pending, expired, rejected)
-- Sources: sales.raven.sda_deal_registration_view
--
-- MODE: Customer vs Partner
-- ┌─────────────────┬───────────────────────────────────────────────────────────────┐
-- │ CUSTOMER MODE   │ Filter: salesforce_account_id = :salesforce_account_id       │
-- │                 │ Shows: All deal regs filed for this customer                 │
-- ├─────────────────┼───────────────────────────────────────────────────────────────┤
-- │ PARTNER MODE    │ Filter: partner_id = :partner_id                             │
-- │                 │ Shows: All deal regs filed by this partner                   │
-- └─────────────────┴───────────────────────────────────────────────────────────────┘

-- =====================
-- CUSTOMER MODE QUERY
-- =====================
SELECT
    dr.deal_reg_name,
    dr.deal_reg_type,
    dr.deal_reg_status,
    dr.partner_name,
    dr.parent_partner_name,
    dr.partner_estimated_acv,
    dr.deal_reg_owner,
    dr.deal_reg_created_date,
    dr.days_from_expiration,
    dr.opportunity_id,
    dr.opportunity_name
FROM sales.raven.sda_deal_registration_view dr
WHERE dr.salesforce_account_id = :salesforce_account_id
ORDER BY dr.deal_reg_created_date DESC;

-- =====================
-- PARTNER MODE QUERY
-- =====================
SELECT
    dr.deal_reg_name,
    dr.deal_reg_type,
    dr.deal_reg_status,
    dr.salesforce_account_name AS customer_name,
    dr.salesforce_account_id AS customer_id,
    dr.partner_estimated_acv,
    dr.deal_reg_owner,
    dr.deal_reg_created_date,
    dr.days_from_expiration,
    dr.opportunity_name
FROM sales.raven.sda_deal_registration_view dr
WHERE dr.partner_id = :partner_id
ORDER BY dr.deal_reg_created_date DESC;
