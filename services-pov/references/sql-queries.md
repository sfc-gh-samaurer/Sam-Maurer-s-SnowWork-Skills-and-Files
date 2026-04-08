# SQL Query Reference — Services POV

All Raven queries require `USE ROLE SALES_RAVEN_RO_RL;` first, then `USE WAREHOUSE SNOWHOUSE;` prepended to queries.

**Note:** `AC_WH` warehouse is not accessible for all roles. Use `SNOWHOUSE` as the default. Run `SHOW WAREHOUSES` if neither works.

---

## Query 7 — Account Finder (SFDC Resolution)

```sql
SELECT
  SALESFORCE_ACCOUNT_ID, SALESFORCE_ACCOUNT_NAME, SALESFORCE_PARENT_NAME,
  TYPE, SUB_TYPE, IS_CAPACITY_CUSTOMER, IS_REVENUE_ACCOUNT,
  INDUSTRY, SUB_INDUSTRY, SEGMENT, TERRITORY, GEO, SALES_AREA, COUNTRY,
  SALESFORCE_OWNER_NAME, REP_EMAIL, LEAD_SALES_ENGINEER_NAME,
  SALES_ENGINEER_ACCOUNT_TEAM, SE_DIRECTOR_NAME, SE_VP_NAME,
  DM, DM_EMAIL, RVP, RVP_EMAIL, GVP, GVP_EMAIL,
  ACCOUNT_TIER, NUMBER_OF_EMPLOYEES, ANNUAL_REVENUE, TECH_STACK,
  GLOBAL_2000_RANK, IS_G2K, FIRST_CAPACITY_CUSTOMER_FY
FROM sales.raven.d_salesforce_account_customers
WHERE UPPER(SALESFORCE_ACCOUNT_NAME) LIKE '%' || UPPER('<COMPANY>') || '%'
ORDER BY IS_CAPACITY_CUSTOMER DESC, IS_REVENUE_ACCOUNT DESC, ANNUAL_REVENUE DESC NULLS LAST
LIMIT 10;
```

## Query 8 — Firmographics

```sql
SELECT * FROM TABLE(SALES.RAVEN.GET_3P_DATA('<ACCOUNT_ID>'));
```

## Query 10 — Contract Status

```sql
SELECT c.contract_start_date, c.contract_end_date,
  round(c.capacity_purchased, 2) AS capacity_purchased,
  round(c.total_capacity, 2) AS total_capacity_available,
  greatest(0, round(c.total_capacity - c.total_revenue, 4)) AS capacity_usage_remaining,
  greatest(0, round(c.perc_capacity_available, 4)) AS total_capacity_util_pct
FROM sales.raven.dim_contract_view AS c
WHERE c.salesforce_account_id = '<ACCOUNT_ID>'
  AND current_date() BETWEEN c.contract_start_date AND c.contract_end_date
  AND c.agreement_type = 'Capacity';
```

## Query 11 — Over/Under Prediction

```sql
SELECT CASE WHEN day_of_overage IS NOT NULL THEN 'overage' ELSE 'underage' END AS predicted_status,
  u.overage_underage_prediction, u.day_of_overage, u.days_till_overage
FROM sales.raven.a360_overage_underage_prediction_view AS u
WHERE u.salesforce_account_id = '<ACCOUNT_ID>';
```

## Query 12 — Active Use Cases

```sql
SELECT u.use_case_name, u.use_case_acv, u.use_case_stage, u.use_case_status,
  u.decision_date, u.go_live_date
FROM sales.raven.sda_use_case_view AS u
WHERE u.salesforce_account_id = '<ACCOUNT_ID>'
  AND u.use_case_status NOT IN ('Not In Pursuit', 'Production')
ORDER BY u.use_case_acv DESC NULLS LAST;
```

### Query 12b — All Use Cases (including deployed and lost)

```sql
SELECT u.use_case_name, u.use_case_acv, u.use_case_stage, u.use_case_status,
  u.decision_date, u.go_live_date
FROM sales.raven.sda_use_case_view AS u
WHERE u.salesforce_account_id = '<ACCOUNT_ID>'
ORDER BY u.use_case_acv DESC NULLS LAST;
```

## Query 13 — Open Pipeline

```sql
SELECT p.opportunity_name, p.opportunity_type, p.close_date,
  sum(p.total_acv) AS total_acv, p.stage_name, p.days_in_stage, p.forecast_status
FROM sales.raven.sda_opportunity_view AS p
WHERE p.salesforce_account_id = '<ACCOUNT_ID>'
  AND p.is_open = 1 AND p.is_lost = false AND p.is_won = false
GROUP BY ALL ORDER BY sum(p.total_acv) DESC NULLS LAST;
```

## Query 14 — Product Revenue Breakdown (L7D/L30D)

```sql
SELECT p.product_category, p.use_case, p.feature,
  SUM(CASE WHEN p.general_date >= DATEADD(DAY, -30, CURRENT_DATE()) AND p.general_date < CURRENT_DATE() THEN COALESCE(p.revenue, 0) ELSE 0 END) AS revenue_l30d,
  SUM(CASE WHEN p.general_date >= DATEADD(DAY, -7, CURRENT_DATE()) AND p.general_date < CURRENT_DATE() THEN COALESCE(p.revenue, 0) ELSE 0 END) AS revenue_l7d
FROM sales.raven.a360_daily_account_product_category_revenue_view AS p
WHERE p.salesforce_account_id = '<ACCOUNT_ID>'
  AND p.general_date >= DATEADD(DAY, -30, CURRENT_DATE()) AND p.general_date < CURRENT_DATE()
  AND COALESCE(p.revenue, 0) > 0
GROUP BY p.product_category, p.use_case, p.feature
ORDER BY revenue_l7d DESC;
```

## Query 15 — Monthly Consumption Trend (12 months)

```sql
SELECT DATE_TRUNC('month', c.general_date)::date AS month_ts, ROUND(SUM(c.revenue), 2) AS revenue_monthly
FROM sales.raven.a360_revenue_consumption_view AS c
WHERE c.salesforce_account_id = '<ACCOUNT_ID>'
  AND c.general_date < CURRENT_DATE()
  AND c.general_date >= DATEADD('month', -11, DATE_TRUNC('month', CURRENT_DATE()))
GROUP BY 1 ORDER BY 1;
```

## Query 16 — Support Cases (90 days)

```sql
SELECT csc.sfdc_case_number, csc.subject, csc.severity, csc.status, csc.created_date
FROM sales.raven.a360_cust_support_cases_view AS csc
WHERE csc.salesforce_account_id = '<ACCOUNT_ID>'
  AND csc.created_date >= DATEADD(DAY, -90, CURRENT_DATE())
ORDER BY csc.created_date DESC LIMIT 10;
```

## Query 17 — Warehouse Anomaly Detection (14-day window)

```sql
WITH daily AS (
  SELECT WAREHOUSE_ID, USAGE_DATE::DATE AS day, SUM(CREDITS) AS credits
  FROM SALES.RAVEN.A360_WAREHOUSE_COMPUTE_VIEW
  WHERE SALESFORCE_ACCOUNT_ID = '<ACCOUNT_ID>' AND USAGE_DATE >= DATEADD(DAY, -49, CURRENT_DATE())
  GROUP BY 1, 2
), stats AS (
  SELECT WAREHOUSE_ID, day, credits,
    AVG(credits) OVER (PARTITION BY WAREHOUSE_ID ORDER BY day ROWS BETWEEN 28 PRECEDING AND 1 PRECEDING) AS baseline_avg,
    STDDEV(credits) OVER (PARTITION BY WAREHOUSE_ID ORDER BY day ROWS BETWEEN 28 PRECEDING AND 1 PRECEDING) AS baseline_std,
    LAG(credits, 7) OVER (PARTITION BY WAREHOUSE_ID ORDER BY day) AS credits_7d_ago
  FROM daily
), flagged AS (
  SELECT *, CASE WHEN baseline_std > 0 THEN (credits - baseline_avg) / baseline_std ELSE 0 END AS z_score,
    CASE WHEN credits_7d_ago > 0 THEN (credits - credits_7d_ago) / credits_7d_ago * 100 ELSE 0 END AS wow_pct,
    CASE WHEN (CASE WHEN baseline_std > 0 THEN (credits - baseline_avg) / baseline_std ELSE 0 END) > 2
      OR (CASE WHEN credits_7d_ago > 0 THEN (credits - credits_7d_ago) / credits_7d_ago * 100 ELSE 0 END) > 30 THEN 'SPIKE'
    WHEN (CASE WHEN baseline_std > 0 THEN (credits - baseline_avg) / baseline_std ELSE 0 END) < -2
      OR (CASE WHEN credits_7d_ago > 0 THEN (credits - credits_7d_ago) / credits_7d_ago * 100 ELSE 0 END) < -30 THEN 'DROP'
    ELSE NULL END AS category
  FROM stats WHERE day >= DATEADD(DAY, -14, CURRENT_DATE())
)
SELECT WAREHOUSE_ID, day, ROUND(credits, 2) AS credits, ROUND(z_score, 2) AS z_score,
  ROUND(wow_pct, 1) AS wow_pct, category
FROM flagged WHERE category IS NOT NULL ORDER BY z_score DESC LIMIT 20;
```

## Query 19 — Goals & Pain Points (AI-Generated)

```sql
CALL SALES.RAVEN.RECO_FOR_PROSPECTING_SP_SALES(
  '<ACCOUNT_ID>', '<COMPANY_PROFILE_SUMMARY>', '<RECENT_NEWS_SUMMARY>'
);
```

**Parameters:**
- `<ACCOUNT_ID>`: SFDC account ID
- `<COMPANY_PROFILE_SUMMARY>`: 2-3 sentence summary of the company from web research
- `<RECENT_NEWS_SUMMARY>`: Recent news or events (can be brief)
