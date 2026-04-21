-- Partner Connected Ecosystem (Connected Apps & Data Sharing)
-- Shows technical connections driving consumption
-- Sources: sales.raven.partner_connections_view
--
-- MODE: Customer vs Partner
-- ┌─────────────────┬───────────────────────────────────────────────────────────────┐
-- │ CUSTOMER MODE   │ Filter: salesforce_account_id = :salesforce_account_id       │
-- │                 │ Shows: All partners connected to this customer               │
-- ├─────────────────┼───────────────────────────────────────────────────────────────┤
-- │ PARTNER MODE    │ Filter: partner_account_id = :partner_id                     │
-- │                 │ Shows: All customers connected to this partner               │
-- └─────────────────┴───────────────────────────────────────────────────────────────┘

-- =====================
-- CUSTOMER MODE QUERY
-- =====================
SELECT
    pc.connection_type,
    pc.partner_account_name,
    pc.data_provider_customer_account_name,
    pc.dcp_pdm_name,
    pc.created_date,
    pc.last_connection_date,
    pc.total_credits_consumed,
    pc.total_connections_or_jobs,
    pc.active_edges_c,
    pc.stable_edges_c,
    pc.is_current_qtd,
    pc.is_current_ytd
FROM sales.raven.partner_connections_view pc
WHERE pc.salesforce_account_id = :salesforce_account_id
ORDER BY pc.total_credits_consumed DESC;

-- =====================
-- PARTNER MODE QUERY
-- =====================
SELECT
    pc.connection_type,
    pc.customer_account_name,
    pc.salesforce_account_id AS customer_id,
    pc.dcp_pdm_name,
    pc.created_date,
    pc.last_connection_date,
    pc.total_credits_consumed,
    pc.total_connections_or_jobs,
    pc.is_current_qtd,
    pc.is_current_ytd
FROM sales.raven.partner_connections_view pc
WHERE pc.partner_account_id = :partner_id
ORDER BY pc.total_credits_consumed DESC;
