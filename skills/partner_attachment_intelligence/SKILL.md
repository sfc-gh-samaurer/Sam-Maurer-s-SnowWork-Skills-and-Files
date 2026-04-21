---
name: partner_attachment_intelligence
description: Partner attachment analysis for accounts—attach rates, deal involvement, ecosystem connections, and co-sell opportunities. Use when: partner attach, partner involvement, DCP revenue, deal registrations, partner-attached opps, Crossbeam, co-sell, ecosystem connections, data sharing edges.
created_date: 2026-02-26
last_updated: 2026-02-28
owner_name: Sophy Huang
version: 1.1
---

# Partner Attachment Intelligence

Provides AEs and SEs with comprehensive partner attachment analysis—scorecard metrics, deal involvement, ecosystem consumption, and co-sell opportunities.

## Table of Contents
1. [When to Activate](#when-to-activate)
2. [Step 0: Identify Account & Mode](#step-0-identify-account--mode)
3. [Core Concepts](#core-concepts)
4. [Workflows](#workflows)
5. [Data Sources](#data-sources)

---

## When to Activate

Trigger this skill when the user asks about:
- Partner attachment, attach rates, partner involvement
- DCP revenue, DCP consumption, DCP partners
- Deal registrations, partner splits, partner-on-record
- Partner-attached opportunities, bookings, or use cases
- Ecosystem connections, Connected Apps, data sharing edges
- Crossbeam dark edges, co-sell opportunities, mutual customers
- Partner performance, partner rankings, partner ecosystem

**Semantic Views for Ad-Hoc Queries:**
- **`SALES.RAVEN.PARTNER_ECOSYSTEM_SEMANTIC_VIEW`** — DCP consumption/revenue, partner connections, data exchange edges, Crossbeam intelligence
- **`SALES.RAVEN.SDA_SEMANTIC_VIEW`** — Partner-attached opportunities, closed bookings with partner splits, deal registrations, use cases with partner involvement

---

## Step 0: Identify Account & Mode

This skill supports **two analysis modes** based on input type:

### Mode Selection

| Input Type | Mode | Description |
|------------|------|-------------|
| **Customer Account** | Customer Mode | Analyze which partners are attached to a customer's opportunities, deals, and ecosystem |
| **Partner Account** | Partner Mode | Analyze a partner's involvement across all their customer engagements |

### Account Lookup

**For Customer Accounts:**
- Use Cortex Search Service: `SALES.RAVEN.CUSTOMER_INDIVIDUAL_NAME_SEARCH_SERVICE`
- **Indexed column (ONLY request this):** `salesforce_account_name`
- Then lookup full details via `scripts/lookup_customer_account.sql`
- Filter key: `salesforce_account_id`

**For Partner Accounts:**
- Use Cortex Search Service: `SALES.RAVEN.PARTNER_ACCOUNT_NAME_SEARCH_SERVICE`
- **Indexed column (ONLY request this):** `name`
- Then lookup full details via `scripts/lookup_partner_account.sql`
- Filter key: `partner_salesforce_account_id` or `partner_id`

> **⚠️ CRITICAL: Cortex Search Services only return indexed columns.**
> - Customer service: ONLY `salesforce_account_name` is indexed
> - Partner service: ONLY `name` is indexed
> - DO NOT request `salesforce_account_id`, `ae_name`, `se_name`, etc. in SEARCH_PREVIEW - it will fail!
> - Use the lookup scripts which join back to the base table to get additional columns.

### Lookup Scripts

| Script | Use When |
|--------|----------|
| `scripts/lookup_customer_account.sql` | User specifies a customer account name |
| `scripts/lookup_partner_account.sql` | User specifies a partner account name |
| `scripts/lookup_user_accounts.sql` | Need to find accounts owned by the current user |

**Parameters:**
- Customer mode: `:account_name` → returns `salesforce_account_id`
- Partner mode: `:partner_name` → returns `partner_salesforce_account_id`

---

## Core Concepts

### Why Partner Attachment Matters
| Benefit | Description |
|---------|-------------|
| Higher win rates | Deals with partner involvement close at materially higher rates |
| Larger deal sizes | Partner-attached opportunities carry higher ACV due to broader scope |
| Faster cycles | Partners bring pre-existing relationships and implementation capacity |
| Consumption growth | Accounts connected to partner ecosystems consume more credits |
| Lower churn | Multi-product, partner-integrated accounts have higher retention |
| Co-sell leverage | Crossbeam dark edges reveal warm co-sell intro opportunities |

### Key Terms
| Term | Definition |
|------|------------|
| **Partner Attach Rate** | % of opportunities with a partner involved (referral, resale, co-sell, cloud) |
| **DCP** | Data Cloud Partner—partners driving consumption via Connected Apps, Data Sharing, Marketplace |
| **Stable Edge** | A data exchange connection that has been active for 28+ consecutive days |
| **Dark Edge** | Crossbeam intelligence showing a partner considers this account a mutual customer |
| **Deal Registration** | Formal partner claim of involvement—Referral/Resale or Cloud Deal Reg |
| **Partner Split** | The % revenue share a partner-on-record receives from a closed deal |

---

## Workflows

### Filter Keys by Mode

| Mode | Primary Filter Column | Description |
|------|----------------------|-------------|
| **Customer Mode** | `salesforce_account_id` | Customer's Salesforce Account ID |
| **Partner Mode** | `partner_salesforce_account_id` or `partner_id` | Partner's Salesforce Account ID |

### A. Scorecard & Benchmarking

| Script | Customer Mode | Partner Mode |
|--------|---------------|--------------|
| `scripts/partner_attach_summary.sql` | Filter on `salesforce_account_id` | Filter on `partner_id` |

### B. Deal & Pipeline Partner Involvement

| Script | Purpose | Customer Filter | Partner Filter |
|--------|---------|-----------------|----------------|
| `scripts/partner_roster.sql` | Partners attached with roles and deal counts | `salesforce_account_id` | `partner_id` |
| `scripts/partner_influenced_pipeline.sql` | Open opportunities with partner involvement | `salesforce_account_id` | `partner_id` |
| `scripts/deal_registrations.sql` | Partner deal registrations (approved, pending, expired) | `salesforce_account_id` | `partner_id` |
| `scripts/partner_attached_use_cases.sql` | Use cases with implementation/co-sell/DCP partners | `salesforce_account_id` | `ILIKE '%:partner_name%'` on partner_ls fields |

### C. Ecosystem & Consumption

| Script | Purpose | Customer Filter | Partner Filter |
|--------|---------|-----------------|----------------|
| `scripts/partner_connected_ecosystem.sql` | Connected Apps & Data Sharing connections | `salesforce_account_id` | `partner_account_id` |
| `scripts/dcp_revenue_breakdown.sql` | DCP revenue by partner, consumption type, YTD/QTD | `salesforce_account_id` | `partner_salesforce_account_id` |
| `scripts/stable_edges_marketplace.sql` | Data exchange edges and marketplace status | `salesforce_account_id` | `provider_salesforce_account_id` |

### D. Co-Sell & Engagement

| Script | Purpose | Customer Filter | Partner Filter |
|--------|---------|-----------------|----------------|
| `scripts/crossbeam_dark_edges.sql` | Partners identifying account as mutual customer | `salesforce_account_id` | N/A (customer-centric only) |
| `scripts/partner_engagement_signals.sql` | Recent activity with partner involvement flags | `salesforce_account_id` | N/A (no partner_id column) |

---

## Data Sources

| Source | Type | Description |
|--------|------|-------------|
| `sales.raven.d_salesforce_account_customers` | View | Account master with AE/SE assignments |
| `sales.raven.sda_opportunity_w_partner_split_view` | View | Partner-on-record splits per opportunity |
| `sales.raven.sda_deal_registration_view` | View | Partner deal registrations |
| `sales.raven.sda_use_case_view` | View | Use cases with partner fields |
| `sales.raven.partner_connections_view` | View | Connected App & Data Sharing connections |
| `sales.raven.partner_dcp_consumption_view` | View | DCP revenue & consumption |
| `sales.raven.sda_opportunity_snapshot_view` | View | Opportunity snapshot (current state) |
| `sales.raven.partner_edges_view` | View | Data exchange edges |
| `sales.raven.partner_crossbeam_view` | View | Crossbeam dark edge intelligence |
| `sales.raven.all_engagements_preped_view` | View | Engagement activity with partner flags |
| `SALES.RAVEN.PARTNER_ECOSYSTEM_SEMANTIC_VIEW` | Semantic View | Ad-hoc DCP/edge/connection analytics |
| `SALES.RAVEN.SDA_SEMANTIC_VIEW` | Semantic View | Ad-hoc partner-attached opps/bookings/use cases |

### Cortex Search Services

| Service | Purpose |
|---------|---------|
| `SALES.RAVEN.CUSTOMER_INDIVIDUAL_NAME_SEARCH_SERVICE` | Fuzzy search for customer account names |
| `SALES.RAVEN.PARTNER_ACCOUNT_NAME_SEARCH_SERVICE` | Fuzzy search for partner account names |

---
