# Snowhouse Consumption Queries

Queries to get **current consumption baseline** for scoping documents. Use these to understand what the customer consumes TODAY, so you can project the incremental impact of the proposed engagement.

For **anticipated consumption** after the project, see `consumption-estimates.md`.

## Prerequisites

- Access to **Snowhouse** with PS roles (e.g. `SOLUTION_ARCHITECT`, `TECHNICAL_ACCOUNT_MANAGER`)
- Tables used:
  - `FINANCE.CUSTOMER.SUBSCRIPTION`
  - `FIVETRAN.SALESFORCE.ACCOUNT`
  - `SNOWHOUSE_IMPORT.PUBLIC.DEPLOYMENT_REGION_CLOUD`
  - `ORGANIZATION_USAGE.INTERNAL.METERING_DAILY_HISTORY`

---

## ⚠️ Critical: Active Subscription Filter

**`FINANCE.CUSTOMER.SUBSCRIPTION` contains ALL subscription records** (historical + current). Always filter for active subscriptions:

```sql
and (s.subscription_end_date is null or s.subscription_end_date >= current_date())
```

Without this filter, account counts will be drastically inflated.

---

## 1. Find Customer Accounts

### 1.1 Find accounts by Salesforce customer name

```sql
select
    a.name                                      as salesforce_account_name,
    s.organization_id,
    s.snowflake_account_name                    as account_locator,
    s.snowflake_deployment                      as deployment_code,
    d.schema_name                               as deployment_schema,
    s.snowflake_account_id                      as account_id,
    s.service_level                             as edition,
    'call pst.svcs.sp_set_account_context('
        || s.snowflake_account_id::string
        || ','''
        || d.schema_name
        || ''');'                              as set_account_code
from fivetran.salesforce.account a
join finance.customer.subscription s
  on a.id = s.salesforce_account_id
join snowhouse_import.public.deployment_region_cloud d
  on d.deployment = s.snowflake_deployment
where a.name ilike '%<CUSTOMER_NAME>%'
  and (s.subscription_end_date is null or s.subscription_end_date >= current_date())
group by all
order by a.name, s.snowflake_deployment;
```

Replace `<CUSTOMER_NAME>` with customer name (e.g. `%Paychex%`).

---

### 1.2 Top 5 accounts by credit usage (for scope doc)

```sql
with active_accounts as (
    select 
        s.snowflake_account_id,
        s.snowflake_account_name as account_locator,
        s.snowflake_deployment,
        s.service_level as edition,
        d.schema_name,
        d.snowflake_region
    from fivetran.salesforce.account a
    join finance.customer.subscription s
      on a.id = s.salesforce_account_id
    join snowhouse_import.public.deployment_region_cloud d
      on d.deployment = s.snowflake_deployment
    where a.name ilike '%<CUSTOMER_NAME>%'
      and (s.subscription_end_date is null or s.subscription_end_date >= current_date())
)
select 
    aa.account_locator,
    aa.snowflake_deployment,
    aa.edition,
    round(coalesce(sum(mdh.credits_used), 0), 0) as credits_30d
from active_accounts aa
left join organization_usage.internal.metering_daily_history mdh
  on mdh.account_locator = aa.account_locator
 and mdh.region = aa.snowflake_region
 and mdh.usage_date >= dateadd(day, -30, current_date())
group by aa.account_locator, aa.snowflake_deployment, aa.edition
order by credits_30d desc
limit 5;
```

Use this for the "Top 5 Accounts" table in scope documents.

---

## 2. Current Consumption Baseline

### 2.1 Total monthly credits (all active accounts)

**This is the key baseline for calculating incremental consumption impact.**

```sql
with active_accounts as (
    select 
        s.snowflake_account_name as account_locator,
        d.snowflake_region
    from fivetran.salesforce.account a
    join finance.customer.subscription s
      on a.id = s.salesforce_account_id
    join snowhouse_import.public.deployment_region_cloud d
      on d.deployment = s.snowflake_deployment
    where a.name ilike '%<CUSTOMER_NAME>%'
      and (s.subscription_end_date is null or s.subscription_end_date >= current_date())
)
select 
    round(sum(mdh.credits_used), 0) as total_credits_30d,
    round(sum(mdh.credits_used) * 12, 0) as annualized_credits
from active_accounts aa
join organization_usage.internal.metering_daily_history mdh
  on mdh.account_locator = aa.account_locator
 and mdh.region = aa.snowflake_region
 and mdh.usage_date >= dateadd(day, -30, current_date());
```

---

### 2.2 Storage footprint (requires PST.SVCS context)

First set account context, then run:

```sql
call pst.svcs.sp_set_account_context(<ACCOUNT_ID>, '<DEPLOYMENT_SCHEMA>');

select
    date_trunc('month', (storage_metrics.dpo:dataSet.startTime::timestamp_ltz)) as usage_month,
    avg((storage_metrics.dpo:dataSet.totalStorageBytes::number)) / 1e12 as avg_total_storage_tb
from snowhouse_import.<DEPLOYMENT_SCHEMA>.storage_metrics_etl_v as storage_metrics
where (storage_metrics.dpo:dataSet.startTime::timestamp_ltz)::date
          >= dateadd(month, -12, date_trunc('month', current_date()))
  and storage_metrics.dpo:accountId::int = $session_acct_id
group by 1
order by usage_month;
```

---

## 3. Using Results in Scope Documents

After running these queries, populate the scope doc:

| Scope Doc Section | Query to Use |
|-------------------|--------------|
| Customer Context → Active accounts | Query 1.1 |
| Customer Context → Top 5 accounts | Query 1.2 |
| Consumption Impact → Current baseline | Query 2.1 |
| Consumption Impact → Storage baseline | Query 2.2 |

Then use `consumption-estimates.md` to calculate NEW incremental consumption and percentage increase.
