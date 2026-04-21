## Supporting Tables

### Customer Dimension
**Table**: `SALES.RAVEN.D_SALESFORCE_ACCOUNT_CUSTOMERS`
**Purpose**: Join to get customer attributes, sales hierarchy, industry

Key columns:
| Column | Description |
|--------|-------------|
| SALESFORCE_ACCOUNT_ID | SFDC 18-digit ID (primary key for joining) |
| SALESFORCE_ACCOUNT_NAME | Account name |
| SALESFORCE_OWNER_NAME | Account Executive (AE) name — use for "my accounts" queries |
| SALESFORCE_OWNER_ID | AE's Salesforce user ID |
| INDUSTRY, SUB_INDUSTRY | Industry classification |
| SEGMENT | Customer segment |
| GEO | Geography |
| TERRITORY | Sales territory |
| DM | District Manager |
| RVP | Regional VP |
| GVP | Global VP |
| SUB_REGION_LEAD | Sub-region lead |
| ACCOUNT_TIER | Tier 1, Tier 2, Tier 3 |
| IS_G2K | Global 2000 flag |
| IS_CAPACITY_CUSTOMER | Capacity customer flag |
| IS_REVENUE_ACCOUNT | Revenue account flag |

**Sales hierarchy**: Theater=GVP, Region=RVP, Sub Region=Subregion Lead, District=DM, Patch=AE

**Join keys to data source tables**:
| Data Source Table | Join Column |
|---|---|
| A360_DAILY_ACCOUNT_PRODUCT_CATEGORY_REVENUE_VIEW | `SALESFORCE_ACCOUNT_ID` |
| A360_WLC_ACCOUNT_AGG_VIEW | `SALESFORCE_ACCOUNT_ID` |
| A360_REVENUE_CONSUMPTION_VIEW | `SALESFORCE_ACCOUNT_ID` |
| A360_ECOSYSTEM_CREDITS_DAILY_VIEW | `SALESFORCE_ACCOUNT_ID` |
| A360_SI_COMPANY_DAY_FACT_VIEW | `SALESFORCE_ACCOUNT_ID` |
| A360_SI_AGENT_DAY_FACT_VIEW | `SALESFORCE_ACCOUNT_ID` |
| A360_SI_USER_DAY_FACT_VIEW | `SALESFORCE_ACCOUNT_ID` |
| A360_CORTEX_CODE_ACCOUNT_DAY_FACT_VIEW | `SALESFORCE_ACCOUNT_ID` |
| A360_CORTEX_AGENTS_COMPANY_DAY_FACT_VIEW | `SALESFORCE_ACCOUNT_ID` |
| A360_CORTEX_AGENTS_AGENT_DAY_FACT_VIEW | `SALESFORCE_ACCOUNT_ID` |
| A360_CORTEX_AGENTS_USER_DAY_FACT_VIEW | `SALESFORCE_ACCOUNT_ID` |
| A360_WLC_WHITESPACE_VIEW | `SALESFORCE_ACCOUNT_ID` |

> **Note**: Cortex Code data (Source 5.2) also appears inside Cortex Agents (Source 5.3) as rows with `SOURCE = 'Coding Agent'`. SI data (Source 5.1) appears in Cortex Agents as `SOURCE = 'Snowflake Intelligence'`. You can query Cortex Agents tables to get a unified view across all agent sources, or use the dedicated SI/Cortex Code tables for source-specific analysis.

**Example**: Find all accounts for an AE, then query their product adoption:
```sql
SELECT b.product_category, SUM(b.revenue) AS total_revenue
FROM sales.raven.d_salesforce_account_customers a
JOIN sales.raven.a360_daily_account_product_category_revenue_view b
    ON a.salesforce_account_id = b.salesforce_account_id
WHERE a.salesforce_owner_name ILIKE '%ae_name%'
    AND b.general_date >= CURRENT_DATE - 30
    AND b.general_date < CURRENT_DATE
GROUP BY b.product_category
ORDER BY total_revenue DESC;
```

**Sample Q&A (Cross-source with Customer Dimension)**:

> **Q**: "What are my accounts using on Snowflake?" (where "my" = the AE asking)

**Key components to include in the answer**:
- First resolve the AE name using SALESFORCE_OWNER_NAME_SEARCH_SERVICE
- Join Customer Dimension to find all their accounts
- Then query one or more data sources (typically start with WLC or Product Category) joined via SALESFORCE_ACCOUNT_ID
- Present per-account breakdown so the AE sees each account's profile
- Summarize patterns across the portfolio (e.g., "3 of your 5 accounts are heavy Data Engineering users")

**Sample answer structure**:
> You own 5 accounts. Here's a product adoption summary (last 30 days):
>
> | Account | Top Product Category | Revenue | Notable Features |
> |---|---|---|---|
> | Acme Corp | Data Engineering ($X) | $Y total | Dynamic Tables, Snowpipe |
> | Beta Inc | Analytics ($A) | $B total | Dashboards, Streamlit |
> | Gamma Ltd | AI/ML ($C) | $D total | Cortex Functions, ML Training |
>
> **Pattern**: 3 of 5 accounts are heavy Data Engineering users. AI/ML is emerging in Gamma Ltd — could be an expansion opportunity.

---

### Fiscal Calendar
**Table**: `SALES.RAVEN.FISCAL_CALENDAR`
**Purpose**: Map dates to Snowflake fiscal periods
**Rule**: Fiscal year starts Feb 1, ends Jan 31. Example: 10/1/2025 is FY2026, 1/15/2026 is FY2026, 2/5/2026 is FY2027

| Column | Description |
|--------|-------------|
| _DATE | Calendar date |
| FISCAL_QUARTER_FYYYYY_QQ | e.g. FY2027-Q1 |
| FISCAL_QUARTER_ID | 1, 2, 3, or 4 |
| FISCAL_YEAR_FYYYYY | e.g. FY2027 |
| FISCAL_QUARTER_START | Quarter start date |
| FISCAL_QUARTER_END | Quarter end date |

**Fiscal quarters**:
- FY2026-Q3: 2025-08-01 to 2025-10-31
- FY2026-Q4: 2025-11-01 to 2026-01-31
- FY2027-Q1: 2026-02-01 to 2026-04-30
- FY2027-Q2: 2026-05-01 to 2026-07-31

**Join key**: `_DATE` joins to any date column in the data source tables (e.g., `GENERAL_DATE`, `END_DATE`, `DS`).

```sql
-- Example: Product adoption by fiscal quarter
SELECT fc.fiscal_quarter_fyyyyy_qq, SUM(r.revenue) AS quarterly_revenue
FROM sales.raven.a360_daily_account_product_category_revenue_view r
JOIN sales.raven.fiscal_calendar fc
    ON r.general_date = fc._date
WHERE r.salesforce_account_name ILIKE '%customer_name%'
GROUP BY fc.fiscal_quarter_fyyyyy_qq
ORDER BY fc.fiscal_quarter_fyyyyy_qq;
```

---

### Cortex Search Services (Name Resolution)
Use these search services to resolve user input to exact values instead of guessing with `ILIKE`. This prevents mismatches when users provide approximate names (e.g., "Sony" → "Sony Corporation of America").

| What to Resolve | Search Service | Search Column | Returns |
|---|---|---|---|
| Customer name | `SALES.RAVEN.CUSTOMER_INDIVIDUAL_NAME_SEARCH_SERVICE` | SALESFORCE_ACCOUNT_NAME | Exact account name |
| AE / Account owner | `SALES.RAVEN.SALESFORCE_OWNER_NAME_SEARCH_SERVICE` | SALESFORCE_OWNER_NAME | Exact owner name |
| Product category hierarchy | `SALES.RAVEN.PRODUCT_CATEGORY_SEARCH_SERVICE` | PRODUCT_CATEGORY_AGG | PRODUCT_CATEGORY, USE_CASE, PRIMARY_FEATURE |
| Feature name | `SALES.RAVEN.FEATURE_SEARCH_SERVICE` | FEATURE | PRODUCT_CATEGORY, USE_CASE, FEATURE |
| Tool / Client / Connector | `SALES.RAVEN.TOOL_CLIENT_CATEGORY_SEARCH_SERVICE` | TOOL_CLIENT_CATEGORY_AGG | TOOL, TOOL_CATEGORY, CLIENT, CLIENT_CATEGORY |
| WLC top category | `SALES.RAVEN.WLC_TOP_CATEGORY_SEARCH_SERVICE` | TOP_CATEGORY | TOP_CATEGORY |
| WLC sub category | `SALES.RAVEN.WLC_SUB_CATEGORY_SEARCH_SERVICE` | SUB_CATEGORY | TOP_CATEGORY, SUB_CATEGORY |
| Sales hierarchy (AE→DM→SRL→RVP→GVP) | `SALES.RAVEN.HIERARCHY_SEARCH_SERVICE` | HIERARCHY_AGG | Full hierarchy chain |
| DM name | `SALES.RAVEN.DM_SEARCH_SERVICE` | DM | DM |
| RVP name | `SALES.RAVEN.RVP_SEARCH_SERVICE` | RVP | RVP |
| Sub-region lead | `SALES.RAVEN.SUB_REGION_LEAD_SEARCH_SERVICE` | SUB_REGION_LEAD | SUB_REGION_LEAD |
| Industry | `SALES.RAVEN.INDUSTRY_SEARCH_SERVICE` | INDUSTRY_AGG | INDUSTRY, SUB_INDUSTRY |
| SE name | `SALES.RAVEN.LEAD_SALES_ENGINEER_NAME_SEARCH_SERVICE` | LEAD_SALES_ENGINEER_NAME | SE name |

**When to use**: Whenever a user provides a name, tool, feature, or category that needs to be matched against a column in a query. Use the search service to find the exact value first, then use that value in your SQL `WHERE` clause.

**Note on whitespace/WLC queries**: For whitespace analysis, you do NOT need the WLC category search services — the category spine is built dynamically from the peer pool in the query itself (see Source 4.2 in `wlc_sources.md`). Use `CUSTOMER_INDIVIDUAL_NAME_SEARCH_SERVICE` to resolve the target account name, and `INDUSTRY_SEARCH_SERVICE` if the user provides an industry/sub-industry filter.
