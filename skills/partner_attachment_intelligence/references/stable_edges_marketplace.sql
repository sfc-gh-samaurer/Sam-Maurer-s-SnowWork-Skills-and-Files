-- Stable Edges & Marketplace Connections
-- Shows data exchange edges and marketplace activity
-- Sources: sales.raven.partner_edges_view
--
-- MODE: Customer vs Partner
-- ┌─────────────────┬───────────────────────────────────────────────────────────────┐
-- │ CUSTOMER MODE   │ Filter: salesforce_account_id = :salesforce_account_id       │
-- │                 │ Shows: All partners providing data to this customer          │
-- ├─────────────────┼───────────────────────────────────────────────────────────────┤
-- │ PARTNER MODE    │ Filter: provider_salesforce_account_id = :partner_id         │
-- │                 │ Shows: All customers consuming data from this partner        │
-- └─────────────────┴───────────────────────────────────────────────────────────────┘

-- =====================
-- CUSTOMER MODE QUERY
-- =====================
SELECT
    pe.provider_salesforce_account_name AS partner_name,
    pe.edge_type,
    pe.edge_source,
    pe.edge_state,
    pe.is_28day_active,
    pe.is_stable,
    pe.is_currently_stable_edge,
    pe.is_current_marketplace_provider,
    pe.edge_created_on,
    pe.last_active,
    pe.last_stable_on,
    pe.dcp_pdm_name,
    pe.dcp_managed_flag,
    pe.count_of_listings,
    pe.count_edge_id
FROM sales.raven.partner_edges_view pe
WHERE pe.salesforce_account_id = :salesforce_account_id
ORDER BY pe.is_currently_stable_edge DESC, pe.is_28day_active DESC, pe.last_active DESC;

-- =====================
-- PARTNER MODE QUERY
-- =====================
SELECT
    pe.consumer_salesforce_account_name AS customer_name,
    pe.salesforce_account_id AS customer_id,
    pe.edge_type,
    pe.edge_source,
    pe.edge_state,
    pe.is_28day_active,
    pe.is_stable,
    pe.is_currently_stable_edge,
    pe.is_current_marketplace_provider,
    pe.edge_created_on,
    pe.last_active,
    pe.count_of_listings,
    pe.count_edge_id
FROM sales.raven.partner_edges_view pe
WHERE pe.provider_salesforce_account_id = :partner_id
ORDER BY pe.is_currently_stable_edge DESC, pe.is_28day_active DESC, pe.last_active DESC;
