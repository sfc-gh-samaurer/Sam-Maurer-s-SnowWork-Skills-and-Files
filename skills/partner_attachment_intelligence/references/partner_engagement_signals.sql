-- Partner Engagement Signals from Activity Logs
-- Surfaces engagement activities that mention partner involvement
-- Sources: sales.raven.all_engagements_preped_view
-- Note: is_partner_involvement is an ARRAY column, so we check ARRAY_SIZE > 0
--
-- MODE: Customer vs Partner
-- ┌─────────────────┬───────────────────────────────────────────────────────────────┐
-- │ CUSTOMER MODE   │ Filter: salesforce_account_id = :salesforce_account_id       │
-- │                 │ Shows: Engagements for this customer with partner mentions   │
-- ├─────────────────┼───────────────────────────────────────────────────────────────┤
-- │ PARTNER MODE    │ Filter: is_partner_involvement array contains partner_name   │
-- │                 │ Shows: Engagements mentioning this partner across customers  │
-- └─────────────────┴───────────────────────────────────────────────────────────────┘

-- =====================
-- CUSTOMER MODE QUERY
-- =====================
SELECT
    e.activity_date,
    e.type,
    e.subject,
    e.participant_names,
    e.takeaways,
    e.is_partner_involvement,
    e.is_competitor,
    e.is_business_goals
FROM sales.raven.all_engagements_preped_view e
WHERE e.salesforce_account_id = :salesforce_account_id
  AND ARRAY_SIZE(e.is_partner_involvement) > 0
ORDER BY e.activity_date DESC
LIMIT 20;

-- =====================
-- PARTNER MODE QUERY
-- =====================
-- is_partner_involvement is an array of objects: [{"partner": "Name", "partner_type": "Type", "reasoning": "..."}]
-- Use FLATTEN to search for a specific partner name
SELECT
    e.salesforce_account_id,
    e.activity_date,
    e.type,
    e.subject,
    e.participant_names,
    e.takeaways,
    e.is_partner_involvement
FROM sales.raven.all_engagements_preped_view e,
     LATERAL FLATTEN(input => e.is_partner_involvement) p
WHERE p.value:partner::STRING ILIKE :partner_name
ORDER BY e.activity_date DESC
LIMIT 20;
