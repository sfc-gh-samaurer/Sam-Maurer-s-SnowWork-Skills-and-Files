## Sources 1-3: Product Category, Billing & Tools

### Source 1: Product Category
**Table**: `SALES.RAVEN.A360_DAILY_ACCOUNT_PRODUCT_CATEGORY_REVENUE_VIEW`
**Best for**: Strategic product adoption, revenue by Snowflake feature/category, "is customer using X?"
**Granularity**: Daily, per account, per product hierarchy
**Taxonomy**: Product Category -> Use Case -> Feature (3-tier hierarchy)

| Column | Type | Description |
|--------|------|-------------|
| PRODUCT_CATEGORY | VARCHAR | Tier 1: AI/ML, Data Engineering, Analytics, Apps & Collaboration, Platform |
| USE_CASE | VARCHAR | Tier 2: Subcategories within each product category |
| FEATURE | VARCHAR | Tier 3: Specific features (Dynamic Tables, Snowpipe, Task, etc.) |
| REVENUE | FLOAT | Revenue in USD for the given date/account/feature |
| GENERAL_DATE | DATE | Date of the revenue data |
| SALESFORCE_ACCOUNT_ID | VARCHAR | SFDC 18-digit account ID |
| SALESFORCE_ACCOUNT_NAME | VARCHAR | Account name |
| SNOWFLAKE_ACCOUNT_ID | NUMBER | Snowflake account ID |
| SNOWFLAKE_ACCOUNT_NAME | VARCHAR | Snowflake account name |
| SNOWFLAKE_ACCOUNT_ALIAS | VARCHAR | Snowflake account alias |
| SNOWFLAKE_DEPLOYMENT | VARCHAR | Deployment identifier |

**Example queries**:
```sql
-- Top product categories by revenue for a customer last 30 days
SELECT product_category, SUM(revenue) as total_revenue
FROM sales.raven.a360_daily_account_product_category_revenue_view
WHERE salesforce_account_name ILIKE '%customer_name%'
  AND general_date >= CURRENT_DATE - 30
  AND general_date < CURRENT_DATE
GROUP BY product_category
ORDER BY total_revenue DESC;

-- Feature adoption: which features is a customer using?
SELECT feature, use_case, product_category, SUM(revenue) as total_revenue
FROM sales.raven.a360_daily_account_product_category_revenue_view
WHERE salesforce_account_name ILIKE '%customer_name%'
  AND general_date >= CURRENT_DATE - 30
  AND general_date < CURRENT_DATE
GROUP BY feature, use_case, product_category
ORDER BY total_revenue DESC;

-- AI/ML adoption trend by week
SELECT DATE_TRUNC('week', general_date) as week,
       SUM(revenue) as weekly_revenue
FROM sales.raven.a360_daily_account_product_category_revenue_view
WHERE salesforce_account_name ILIKE '%customer_name%'
  AND product_category = 'AI/ML'
  AND general_date >= CURRENT_DATE - 90
  AND general_date < CURRENT_DATE
GROUP BY week
ORDER BY week;
```

**Sample Q&A**:

> **Q**: "Is Acme Corp using AI/ML on Snowflake?"

**Key components to include in the answer**:
- Whether AI/ML revenue exists at all (yes/no adoption signal)
- Revenue magnitude relative to total spend (is it meaningful or negligible?)
- Which specific features within AI/ML are driving usage (Cortex Functions, ML Training, etc.)
- Trend direction — growing, stable, or declining over recent weeks
- Comparison to other product categories for context

**Sample answer structure**:
> Yes, Acme Corp has active AI/ML adoption. Over the last 30 days, AI/ML generated $X in revenue (~Y% of their total Snowflake spend). The primary features driving this are **Cortex Functions** ($A) and **ML Training** ($B). Weekly revenue has been trending [up/flat/down] over the past 90 days, from ~$W/week to ~$Z/week. For context, their largest product category is **Data Engineering** at $D, so AI/ML is [a growing complement / still early-stage / a significant pillar] of their usage.

---

### Source 2: Billing Product
**Table**: `SALES.RAVEN.A360_REVENUE_CONSUMPTION_VIEW`
**Best for**: Financial reporting, compute vs storage breakdown, revenue by cloud provider
**Granularity**: Daily, per account, per revenue category

| Column | Type | Description |
|--------|------|-------------|
| REVENUE_CATEGORY | VARCHAR | Billing category (compute, storage, etc.) |
| REVENUE | FLOAT | Revenue in USD |
| GENERAL_DATE | DATE | Date of the revenue data |
| CLOUD_PROVIDER | VARCHAR | Amazon (AWS), Google Cloud (GCP), Microsoft (Azure), Other/Unknown |
| SALESFORCE_ACCOUNT_ID | VARCHAR | SFDC 18-digit account ID |
| SALESFORCE_ACCOUNT_NAME | VARCHAR | Account name |
| SNOWFLAKE_ACCOUNT_ID | NUMBER | Snowflake account ID |
| SNOWFLAKE_ACCOUNT_NAME | VARCHAR | Snowflake account name |
| SNOWFLAKE_ACCOUNT_ALIAS | VARCHAR | Snowflake account alias |
| SNOWFLAKE_DEPLOYMENT | VARCHAR | Deployment identifier |

**Example queries**:
```sql
-- Revenue breakdown by billing category
SELECT revenue_category, SUM(revenue) as total_revenue
FROM sales.raven.a360_revenue_consumption_view
WHERE salesforce_account_name ILIKE '%customer_name%'
  AND general_date >= CURRENT_DATE - 30
  AND general_date < CURRENT_DATE
GROUP BY revenue_category
ORDER BY total_revenue DESC;

-- Revenue by cloud provider over time
SELECT cloud_provider, DATE_TRUNC('month', general_date) as month_start,
       SUM(revenue) as monthly_revenue
FROM sales.raven.a360_revenue_consumption_view
WHERE salesforce_account_name ILIKE '%customer_name%'
  AND general_date >= CURRENT_DATE - 180
  AND general_date < CURRENT_DATE
GROUP BY cloud_provider, month_start
ORDER BY month_start, monthly_revenue DESC;
```

**Sample Q&A**:

> **Q**: "How does Acme Corp's billing break down?"

**Key components to include in the answer**:
- Revenue by category with both absolute $ and % of total
- Highlight the dominant billing category (usually compute)
- Cloud provider split if multi-cloud
- Month-over-month trend for the top categories
- Flag any unusual patterns (e.g., storage growing faster than compute)

**Sample answer structure**:
> Acme Corp's last-30-day billing ($X total) breaks down as:
> - **Compute**: $A (72%) — the bulk of their spend, consistent with heavy warehouse usage
> - **Storage**: $B (18%) — steady, indicates significant data volumes
> - **Serverless**: $C (7%) — Snowpipe, Tasks, etc.
> - **Data Transfer**: $D (3%)
>
> They run exclusively on **AWS**. Month-over-month, compute is up ~8% while storage is flat, suggesting increased query workloads rather than data growth.

---

### Source 3: Tools & Clients
**Table**: `SALES.RAVEN.A360_ECOSYSTEM_CREDITS_DAILY_VIEW`
**Best for**: Which BI tools, ETL tools, connectors, or clients are driving consumption
**Granularity**: Daily, per account, per tool/client
**DATA LIMITATION**: No warehouse column exists. Cannot break down connector credits by warehouse. Do NOT join with A360_WAREHOUSE_COMPUTE — it creates invalid Cartesian products.

| Column | Type | Description |
|--------|------|-------------|
| TOOL | VARCHAR | Specific tool (Tableau, Streamlit, dbt, Looker, etc.) |
| TOOL_CATEGORY | VARCHAR | Tool grouping (BI Tools, Data Engineering Tools, ML/DS Tools, etc.) |
| CLIENT | VARCHAR | Connector/driver (Spark Connector, Go, ODBC, JDBC, Python, etc.) |
| CLIENT_CATEGORY | VARCHAR | Client grouping |
| TOTAL_CREDITS | FLOAT | Credits consumed |
| END_DATE | DATE | Date of the usage data |
| SALESFORCE_ACCOUNT_ID | VARCHAR | SFDC 18-digit account ID |
| SALESFORCE_ACCOUNT_NAME | VARCHAR | Account name |
| SNOWFLAKE_ACCOUNT_NAME | VARCHAR | Snowflake account name |
| SNOWFLAKE_ACCOUNT_ALIAS | VARCHAR | Snowflake account alias |

**Example queries**:
```sql
-- Top tools by credits for a customer
SELECT tool, tool_category, SUM(total_credits) as credits
FROM sales.raven.a360_ecosystem_credits_daily_view
WHERE salesforce_account_name ILIKE '%customer_name%'
  AND end_date >= CURRENT_DATE - 30
  AND end_date < CURRENT_DATE
GROUP BY tool, tool_category
ORDER BY credits DESC;

-- Client/connector breakdown
SELECT client, client_category, SUM(total_credits) as credits
FROM sales.raven.a360_ecosystem_credits_daily_view
WHERE salesforce_account_name ILIKE '%customer_name%'
  AND end_date >= CURRENT_DATE - 30
  AND end_date < CURRENT_DATE
GROUP BY client, client_category
ORDER BY credits DESC;
```

**Sample Q&A**:

> **Q**: "What tools and connectors does Acme Corp use with Snowflake?"

**Key components to include in the answer**:
- Separate tools (BI/ETL) from clients (connectors/drivers) — they answer different questions
- Rank by credits to show which tools drive the most consumption
- Group by tool_category for a cleaner narrative (BI Tools, Data Engineering Tools, etc.)
- Call out notable absences if relevant (e.g., no BI tool detected)
- Remind that connector credits ≠ warehouse-level attribution (data limitation)

**Sample answer structure**:
> Acme Corp's tool ecosystem (last 30 days):
>
> **BI Tools**: Tableau leads at X credits, followed by Looker (Y credits). They also have minor Streamlit usage.
> **Data Engineering**: dbt is their primary transformation tool (Z credits), with Airflow-driven Python connector activity.
> **Connectors**: JDBC dominates (W credits), likely from their Java-based microservices. Python connector is second, consistent with their data science workflows.
>
> *Note: Connector credits reflect total consumption through that driver but cannot be attributed to specific warehouses.*
