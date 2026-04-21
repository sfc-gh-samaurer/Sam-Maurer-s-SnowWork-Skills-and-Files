## Source 4: Workload Classification & Whitespace

Workload Classification (WLC) and Whitespace share the same taxonomy: `functional_area` -> `top_category` -> `sub_category`. WLC Account Agg (4.1) provides the target account's workload breakdown; Whitespace (4.2) adds the peer benchmarking layer on top. Both are 8-week pre-aggregated snapshots with NO date filter.

---

### 4.1 WLC Account Agg
**Table**: `SALES.RAVEN.A360_WLC_ACCOUNT_AGG_VIEW`
**Best for**: Understanding what business functions customers use Snowflake for, industry workloads
**Granularity**: 8-week aggregated snapshot per account (NO date filter — pre-aggregated)
**Important**: CREDITS_PCT is already multiplied by 100. No date column to filter on.

| Column | Type | Description |
|--------|------|-------------|
| FUNCTIONAL_AREA | VARCHAR | Full label e.g. "(Finance) Investment Banking" |
| TOP_CATEGORY | VARCHAR | Broad business function: Finance, Marketing, HR, Supply Chain, Untracked |
| SUB_CATEGORY | VARCHAR | Specific workload within the business function |
| CATEGORY_CREDITS | FLOAT | Credits consumed by this workload category |
| TOTAL_ACCOUNT_CREDITS | FLOAT | Total credits across the entire account |
| CREDITS_PCT | FLOAT | Percentage of account credits (already x100, e.g. 25.3 means 25.3%) |
| CREDITS_4W_AVG | FLOAT | 4-week average credits for this category |
| WEEKS_WITH_DATA | NUMBER | Number of weeks with data in the 8-week window |
| EXAMPLE_WORKLOADS | VARCHAR | Example workload descriptions |
| SALESFORCE_ACCOUNT_ID | VARCHAR | SFDC 18-digit account ID |
| SALESFORCE_ACCOUNT_NAME | VARCHAR | Account name |
| INDUSTRY | VARCHAR | Customer industry |
| SUB_INDUSTRY | VARCHAR | Customer sub-industry |

**Example queries**:
```sql
-- What is customer using Snowflake for? (Functional Area)
SELECT functional_area, category_credits, credits_pct,
       example_workloads
FROM sales.raven.a360_wlc_account_agg_view
WHERE salesforce_account_name ILIKE '%customer_name%'
ORDER BY category_credits DESC;

-- Top business functions across an industry
SELECT top_category, SUM(category_credits) as total_credits
FROM sales.raven.a360_wlc_account_agg_view
WHERE industry ILIKE '%financial%'
  AND top_category != 'Untracked'
GROUP BY top_category
ORDER BY total_credits DESC;
```

**Sample Q&A**:

> **Q**: "What is Acme Corp using Snowflake for?"

**Key components to include in the answer**:
- Lead with business functions, not technical features (this is the "what" and "why")
- Show top functional areas ranked by credits share
- Include example workloads for the top areas to make it tangible
- Call out the Untracked percentage — high Untracked means limited WLC coverage
- Mention weeks_with_data to signal data recency/consistency

**Sample answer structure**:
> Based on workload classification (last 8 weeks), Acme Corp primarily uses Snowflake for:
> 1. **Finance — Risk Analytics** (35% of credits) — e.g., portfolio risk modeling, VaR calculations
> 2. **Engineering — Data Pipelines** (28%) — e.g., ETL orchestration, data lake ingestion
> 3. **Marketing — Customer Analytics** (15%) — e.g., segmentation, campaign attribution
>
> ~22% of their credits are Untracked (workloads not yet classified). This suggests their core use cases are finance and data engineering, with a growing marketing analytics practice.

---

### 4.2 WLC Whitespace & Peer Analysis
**Table**: `SALES.RAVEN.A360_WLC_WHITESPACE_VIEW`
**Best for**: Peer benchmarking, whitespace identification, competitive analysis across workload categories
**Granularity**: 8-week aggregated snapshot per account × functional_area (NO date filter — pre-aggregated)
**Important**: This view has NO raw credits — only `credits_pct`. No masking policy. Use as the peer lookup table.

> **⚠️ INTERNAL USE ONLY**: Every whitespace response MUST include this disclaimer prominently (bold, at the top of the results): *"Internal Use Only: Do NOT screenshot or share externally. You may reference peer data internally, but it is against our legal policy to share this heat map or numbers from this table outside Snowflake."*

| Column | Type | Description |
|--------|------|-------------|
| SALESFORCE_ACCOUNT_ID | VARCHAR | SFDC 18-digit account ID |
| SALESFORCE_ACCOUNT_NAME | VARCHAR | Account name |
| INDUSTRY | VARCHAR | Customer industry |
| SUB_INDUSTRY | VARCHAR | Customer sub-industry |
| FUNCTIONAL_AREA | VARCHAR | Full label e.g. "(Finance) Investment Banking" |
| TOP_CATEGORY | VARCHAR | Broad business function: Finance, Marketing, HR, etc. |
| SUB_CATEGORY | VARCHAR | Specific workload within the business function |
| CREDITS_PCT | FLOAT | Percentage of account credits (already x100) |
| EXAMPLE_WORKLOADS | VARCHAR | Example workload descriptions |
| ACCOUNT_RANK | NUMBER | Global rank by total credits (1 = largest account) |

#### Peer Selection & Join Logic
Peers are selected from `A360_WLC_WHITESPACE_VIEW` using the target account's `sub_industry` (fallback to `industry` if < 5 peers). Top 15 by `account_rank`. See the unified query below for the full pattern.

#### Default Behavior
1. **Granularity**: Always start at `sub_category` level (not `top_category`). This gives the most actionable whitespace view. **Always include `top_category` in sub_category-level tables** so the user can see which broad business function each sub-category belongs to. After showing results, offer to roll up to `top_category` if the user wants a summary.
2. **Peer count**: Default to top 15 peers by `account_rank` (lowest rank = largest). If peer group has < 15, use all available (must be >= 5). Always state the actual peer count.
3. **Peer definition**: Peers = all accounts in the same `sub_industry`. If sub_industry has < 5 accounts, fall back to `industry` to get at least 5.

#### Whitespace Identification
Whitespace = workload categories that the target account's top 15 peers use but the account either (a) does not use at all, or (b) uses significantly less. Rank whitespace opportunities by:

| Metric | Formula | Description |
|--------|---------|-------------|
| peer_avg_pct | SUM(peers.credits_pct) / total_peers | Average credits_pct across **ALL** qualified peers, treating missing categories as 0 |
| account_pct | target.credits_pct (0 if missing) | Target account's credits_pct |
| gap_pct | peer_avg_pct - account_pct | Gap between peer avg and account |
| peer_penetration | COUNT(peers using category) / total_peers | % of peers that use this category |

**CRITICAL — Zero-fill rule**: When calculating `peer_avg_pct`, you MUST include ALL qualified peers in the denominator, not just peers that have data for that category. Peers that don't use a category contribute 0 to the average. Use `functional_area` as the cross-join grain because it uniquely encodes both `top_category` and `sub_category` (e.g., "(Finance) Investment Banking"). Without this zero-fill, categories used by few peers will show inflated averages.

Order whitespace results by `gap_pct DESC`. Highlight:
- **Not using**: Categories where `account_pct = 0` and `peer_penetration > 50%`
- **Underweight**: Categories where `account_pct > 0` but `gap_pct` is large relative to `peer_avg_pct`

#### Query Architecture — Single Unified Pattern

The whitespace query uses one pattern with **3 layers**:

1. **`category_spine`**: Distinct `functional_area` values from the peer pool — this is the universe of categories. Both account and peers join to it.
2. **`peer_filled`**: CROSS JOIN `category_spine` × `top_peer_ids`, LEFT JOIN actual peer data → zero-filled credits_pct
3. **`acct_filled`**: LEFT JOIN account data to `category_spine` → zero-filled credits_pct
4. **`fa_stats`**: Aggregate at `functional_area` grain (always computed first)
5. **Final SELECT**: Control granularity by changing only the GROUP BY:
   - **`sub_category` level** (default): No further aggregation — select directly from `fa_stats`
   - **`top_category` level**: GROUP BY `top_category`, SUM the per-functional_area stats

**Example query — Unified whitespace analysis (with zero-fill)**:
```sql
WITH target AS (
    SELECT DISTINCT salesforce_account_id, sub_industry, industry
    FROM sales.raven.a360_wlc_account_agg_view
    WHERE salesforce_account_name ILIKE '%customer_name%'
    LIMIT 1
),
sub_ind_counts AS (
    SELECT sub_industry, COUNT(DISTINCT salesforce_account_id) as cnt
    FROM sales.raven.a360_wlc_whitespace_view
    WHERE sub_industry IS NOT NULL
    GROUP BY 1
),
peer_group AS (
    SELECT p.*
    FROM sales.raven.a360_wlc_whitespace_view p
    CROSS JOIN target t
    WHERE p.salesforce_account_id != t.salesforce_account_id
      AND (
            (EXISTS (SELECT 1 FROM sub_ind_counts s WHERE s.sub_industry = t.sub_industry AND s.cnt >= 5) AND p.sub_industry = t.sub_industry)
            OR
            (NOT EXISTS (SELECT 1 FROM sub_ind_counts s WHERE s.sub_industry = t.sub_industry AND s.cnt >= 5) AND p.industry = t.industry)
          )
    QUALIFY ROW_NUMBER() OVER (
        PARTITION BY p.salesforce_account_id, p.functional_area
        ORDER BY p.account_rank ASC
    ) = 1
),
distinct_peers AS (
    SELECT salesforce_account_id, MIN(account_rank) as account_rank
    FROM peer_group
    GROUP BY 1
),
top_peer_ids AS (
    SELECT salesforce_account_id
    FROM distinct_peers
    ORDER BY account_rank ASC
    LIMIT 15
),
total_peer_count AS (
    SELECT COUNT(*) as cnt FROM top_peer_ids
),
-- Layer 1: Category spine — universe of functional_areas from the peer pool
category_spine AS (
    SELECT functional_area, top_category, sub_category,
           ANY_VALUE(example_workloads) as sample_workloads
    FROM peer_group
    WHERE salesforce_account_id IN (SELECT salesforce_account_id FROM top_peer_ids)
      AND top_category != 'Untracked'
    GROUP BY functional_area, top_category, sub_category
),
-- Layer 2: Zero-filled peer data (CROSS JOIN spine × peers, LEFT JOIN actuals)
peer_filled AS (
    SELECT tp.salesforce_account_id, cs.functional_area, cs.top_category, cs.sub_category,
           COALESCE(pg.credits_pct, 0) as credits_pct
    FROM top_peer_ids tp
    CROSS JOIN category_spine cs
    LEFT JOIN peer_group pg
        ON tp.salesforce_account_id = pg.salesforce_account_id
        AND cs.functional_area = pg.functional_area
),
-- Layer 3: Zero-filled account data (LEFT JOIN account to spine)
acct_filled AS (
    SELECT cs.functional_area, cs.top_category, cs.sub_category,
           COALESCE(a.credits_pct, 0) as credits_pct
    FROM category_spine cs
    LEFT JOIN (
        SELECT functional_area, credits_pct
        FROM sales.raven.a360_wlc_account_agg_view
        WHERE salesforce_account_id = (SELECT salesforce_account_id FROM target)
    ) a ON cs.functional_area = a.functional_area
),
-- Always compute at functional_area grain first
fa_stats AS (
    SELECT p.functional_area, p.top_category, p.sub_category,
           AVG(p.credits_pct) as peer_avg_pct,
           COUNT(DISTINCT CASE WHEN p.credits_pct > 0 THEN p.salesforce_account_id END) as peers_using,
           MAX(a.credits_pct) as account_pct,
           MAX(cs.sample_workloads) as sample_workloads
    FROM peer_filled p
    JOIN acct_filled a ON p.functional_area = a.functional_area
    JOIN category_spine cs ON p.functional_area = cs.functional_area
    GROUP BY 1, 2, 3
)

-- ============================================================
-- GRANULARITY CONTROL: Pick ONE of the two SELECT blocks below
-- ============================================================

-- === OPTION A: sub_category level (default) ===
SELECT top_category, sub_category, functional_area,
       ROUND(peer_avg_pct, 2) as peer_avg_pct,
       ROUND(account_pct, 2) as account_pct,
       ROUND(peer_avg_pct - account_pct, 2) as gap_pct,
       peers_using,
       (SELECT cnt FROM total_peer_count) as total_peers,
       ROUND(DIV0(peers_using, (SELECT cnt FROM total_peer_count)) * 100, 0) as peer_penetration_pct,
       LEFT(sample_workloads, 200) as sample_workloads
FROM fa_stats
ORDER BY gap_pct DESC;

-- === OPTION B: top_category level (roll-up) ===
-- SELECT top_category,
--        ROUND(SUM(peer_avg_pct), 2) as peer_avg_pct,
--        ROUND(SUM(account_pct), 2) as account_pct,
--        ROUND(SUM(peer_avg_pct) - SUM(account_pct), 2) as gap_pct,
--        MAX(peers_using) as peers_using,
--        (SELECT cnt FROM total_peer_count) as total_peers,
--        ROUND(DIV0(MAX(peers_using), (SELECT cnt FROM total_peer_count)) * 100, 0) as peer_penetration_pct
-- FROM fa_stats
-- GROUP BY top_category
-- ORDER BY gap_pct DESC;
```

**Sample Q&A**:

> **Q**: "What's Acme Corp's whitespace?"

**Key components to include in the answer**:
- State peer group used (sub_industry or industry fallback) and peer count
- Show **sub_category** level by default, ranked by gap — **always include `top_category` column** so the user sees the parent business function
- Use a **consistent denominator** (all 15 peers) for peer_avg_pct — peers missing a category contribute 0
- Flag categories account is NOT using at all vs underweight
- Include peer penetration (peers_using / total_peers) to show how common the category is
- If user asks for a summary or top-level view, switch to OPTION B (top_category roll-up)
- **After key takeaways, offer to show sample workloads** — use `ask_user_question` to let the user request a detailed view with peer sample workloads and the account's own workload descriptions side-by-side, so they understand what each whitespace gap or strength actually represents in practice

**Sample answer structure (sub_category — default)**:
> **⚠️ Internal Use Only: Do NOT screenshot or share externally. You may reference peer data internally, but it is against our legal policy to share this heat map or numbers from this table outside Snowflake.**
>
> Comparing Acme Corp against its top 15 peers in **Financial Services** (sub_industry):
>
> | Top Category | Sub Category | Peer Avg % | Acme % | Gap | Peers Using / 15 | Sample Workloads |
> |---|---|---|---|---|---|---|
> | Marketing | Measurement / attribution | 7.7% | 0.0% | +7.7% | 11/15 (73%) | Campaign attribution, marketing mix modeling |
> | Customer Service | Customer service & support | 5.1% | 2.2% | +2.9% | 13/15 (87%) | Ticket resolution analytics, CX dashboards |
> | Data Governance | 3rd Party Data Acquisition | 1.6% | 0.0% | +1.6% | 9/15 (60%) | External data ingestion, third-party enrichment |
>
> **Key takeaways:**
> - [2-4 bullets interpreting the biggest gaps and strengths]
>
> Would you like to:
> - **See sample workloads** for each whitespace gap and strength? (shows what peers actually do in these categories and what the account does)
> - **Roll up to top-category** level for a summary?

When the user asks to see sample workloads, run a second query that extracts the `short` field from `example_workloads` JSON (`REGEXP_SUBSTR(example_workloads, '"short":"([^"]+)"', 1, 1, 'e')`) for both the peer spine and the account's own WLC data. Present side-by-side:

> | Top Category | Sub Category | Peer Avg % | Account % | Gap | Peer Sample Workloads | Account Workload |
> |---|---|---|---|---|---|---|
> | Finance | Market Data Analytics | 10.1% | 0.3% | +9.9% | Options market analytics | Cryptocurrency Staking Analytics |
> | Fraud Detection | Fraud Detection | 0.4% | 15.6% | -15.2% | TWINT fraud detection | Fraud Prevention Analytics |

This helps the user understand **what the categories actually mean** in concrete business terms — e.g., "Market Data Analytics" for peers means options/equities market feeds, while for a crypto company it might map to staking or on-chain data.

**Sample answer structure (top_category — when user asks for summary)**:
> **⚠️ Internal Use Only: Do NOT screenshot or share externally. You may reference peer data internally, but it is against our legal policy to share this heat map or numbers from this table outside Snowflake.**
>
> Comparing Acme Corp against its top 15 peers in **Financial Services** (sub_industry), rolled up to top category:
>
> | Top Category | Peer Avg % | Acme % | Gap | Peers Using / 15 |
> |---|---|---|---|---|
> | Customer Service | 5.2% | 2.2% | +3.0% | 13/15 (87%) |
> | Corporate Support | 2.3% | 0.1% | +2.2% | 11/15 (73%) |
> | Data Governance | 1.6% | 0.0% | +1.6% | 9/15 (60%) |
>
> Would you like to drill into any of these at the sub-category level?
