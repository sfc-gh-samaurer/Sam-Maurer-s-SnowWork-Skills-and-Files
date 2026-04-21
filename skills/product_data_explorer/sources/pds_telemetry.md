## Source 5: PDS Agent (Feature/Tool-Specific Telemetry)

**Table routing guide:**

| Question about | Use these tables | Notes |
|---|---|---|
| Snowflake Intelligence only | `a360_si_*_day_fact_view` (5.1) | Filtered view: `source = 'Snowflake Intelligence'` |
| Cortex Code (users, origin breakdown) | `a360_cortex_code_account_day_fact_view` (5.2) | User-facing metrics by CLI/Desktop/UI |
| All Cortex Agents sources (SI + Direct API + Coding Agent + MCP + MS Teams + Inline Copilot) | `a360_cortex_agents_*_day_fact_view` (5.3) | Parent tables; SI views filter from these |
| Cortex Code via Agents API lens | `a360_cortex_agents_*_day_fact_view` with `source = 'Coding Agent'` | Higher counts than 5.2 (includes backend calls) |
| Non-SI agent adoption (API, MCP, etc.) | `a360_cortex_agents_*_day_fact_view` with `source != 'Snowflake Intelligence'` | |

#### 5.1 Snowflake Intelligence (SI)
SI views are filtered views over `a360_cortex_agents_*_day_fact_view` tables with `WHERE source = 'Snowflake Intelligence'`.

**5.1a Company-Level**: `SALES.RAVEN.A360_SI_COMPANY_DAY_FACT_VIEW`
**Best for**: Company-level SI adoption, daily active users, total requests, credits

| Column | Type | Description |
|--------|------|-------------|
| DS | DATE | Date |
| SOURCE | VARCHAR | Always 'Snowflake Intelligence' in SI views |
| SALESFORCE_ACCOUNT_NAME | VARCHAR | Account name |
| SALESFORCE_ACCOUNT_ID | VARCHAR | SFDC account ID |
| ACCOUNT_ID | NUMBER | Snowflake account ID |
| SNOWFLAKE_ACCOUNT_NAME | VARCHAR | Snowflake account name |
| CLOUD | VARCHAR | Cloud provider |
| NUM_DAILY_ACTIVE_USERS | NUMBER | Daily active users of SI |
| NUM_SI_ONLY_ACTIVE_USERS | NUMBER | Users who only use SI (not other Cortex Agent sources) |
| NUM_TOTAL_REQUESTS | NUMBER | Total SI requests |
| NUM_TOTAL_TRACES | NUMBER | Total traces (conversation threads) |
| TOTAL_INPUT_TOKENS | NUMBER | Input tokens consumed |
| TOTAL_OUTPUT_TOKENS | NUMBER | Output tokens generated |
| TOTAL_TURNS | NUMBER | Total conversation turns |
| NUM_UNIQUE_AGENTS | NUMBER | Number of unique agents used |
| NUM_TOTAL_REQUESTS_ANALYST_AND_SEARCH | NUMBER | Requests using both Analyst and Search tools |
| NUM_TOTAL_REQUESTS_ANALYST_ONLY | NUMBER | Requests using only Cortex Analyst |
| NUM_TOTAL_REQUESTS_SEARCH_ONLY | NUMBER | Requests using only Cortex Search |
| NUM_TOTAL_REQUESTS_NO_TOOL | NUMBER | Requests using no tools |
| AVG_DURATION_MS | FLOAT | Average request duration in ms |
| AVG_TTFT_MS | FLOAT | Average time to first token in ms |
| TOTAL_ORCHESTRATION_CREDITS | FLOAT | Orchestration credits |
| TOTAL_CORTEX_ANALYST_TOKEN_CREDITS | FLOAT | Cortex Analyst token credits |
| TOTAL_CORTEX_ANALYST_WAREHOUSE_CREDITS | FLOAT | Cortex Analyst warehouse credits |
| TOTAL_CORTEX_ANALYST_CREDITS | FLOAT | Total Cortex Analyst credits |
| TOTAL_CORTEX_SEARCH_CREDITS | FLOAT | Cortex Search credits |
| TOTAL_CREDITS | FLOAT | Total credits consumed |

**5.1b Agent-Level**: `SALES.RAVEN.A360_SI_AGENT_DAY_FACT_VIEW`
**Best for**: Per-agent metrics, tool invocation breakdown, performance (latency)

Key additional columns beyond company-level:
| Column | Type | Description |
|--------|------|-------------|
| AGENT_NAME | VARCHAR | Name of the specific agent |
| MOST_USED_MODEL | VARCHAR | Most commonly used LLM model |
| NUM_TRACES | NUMBER | Traces for this agent |
| NUM_REQUESTS | NUMBER | Requests for this agent |
| NUM_UNIQUE_USERS | NUMBER | Unique users of this agent |
| NUM_CORTEX_SEARCH_CALLS | NUMBER | Cortex Search invocations |
| NUM_CORTEX_ANALYST_CALLS | NUMBER | Cortex Analyst invocations |
| NUM_SQL_EXEC_CALLS | NUMBER | SQL execution calls |
| NUM_GENERIC_TOOL_CALLS | NUMBER | Generic tool calls |
| NUM_SYSTEM_VIEW_CALLS | NUMBER | System view calls |
| AVG_DURATION_MS | FLOAT | Average request duration in ms |
| P50_DURATION_MS | FLOAT | Median request duration |
| P90_DURATION_MS | FLOAT | 90th percentile duration |
| AVG_TTFT_MS | FLOAT | Average time to first token |
| P50_TTFT_MS | FLOAT | Median time to first token |
| P90_TTFT_MS | FLOAT | 90th percentile time to first token |

**5.1c User-Level**: `SALES.RAVEN.A360_SI_USER_DAY_FACT_VIEW`
**Best for**: Per-user SI adoption, power users, user-level activity

Key additional columns beyond company-level:
| Column | Type | Description |
|--------|------|-------------|
| USER_ID | VARCHAR | User identifier |
| USER_NAME | VARCHAR | User name |
| IS_INTERNAL_ORGANIZATION | BOOLEAN | Internal org flag |
| IS_SI_ONLY_USER | BOOLEAN | True if user only uses SI (not other Cortex Agent sources) |
| NUM_UNIQUE_MODELS | NUMBER | Number of unique LLM models used |
| P50_DURATION_MS | NUMBER | Median request duration |
| P90_DURATION_MS | NUMBER | 90th percentile duration |
| P50_TTFT_MS | NUMBER | Median time to first token |
| P90_TTFT_MS | NUMBER | 90th percentile time to first token |
| TOTAL_ORCHESTRATION_CREDITS | FLOAT | Orchestration credits |

**Example queries**:
```sql
-- SI adoption for a customer over time
SELECT ds, num_daily_active_users, num_total_requests, total_credits
FROM sales.raven.a360_si_company_day_fact_view
WHERE salesforce_account_name ILIKE '%customer_name%'
ORDER BY ds DESC
LIMIT 30;

-- Top agents by usage for a customer
SELECT agent_name, SUM(num_requests) as total_requests,
       SUM(num_unique_users) as total_users,
       AVG(avg_duration_ms) as avg_latency_ms
FROM sales.raven.a360_si_agent_day_fact_view
WHERE salesforce_account_name ILIKE '%customer_name%'
  AND ds >= CURRENT_DATE - 30
  AND ds < CURRENT_DATE
GROUP BY agent_name
ORDER BY total_requests DESC;

-- Power users of SI
SELECT user_name, SUM(num_requests) as total_requests,
       SUM(num_traces) as total_traces
FROM sales.raven.a360_si_user_day_fact_view
WHERE salesforce_account_name ILIKE '%customer_name%'
  AND ds >= CURRENT_DATE - 30
  AND ds < CURRENT_DATE
GROUP BY user_name
ORDER BY total_requests DESC
LIMIT 20;
```

**Sample Q&A (SI)**:

> **Q**: "How is Acme Corp using Snowflake Intelligence?"

**Key components to include in the answer**:
- Adoption signal: number of daily active users and trend direction
- Volume: total requests and traces (conversations) over the period
- Tool mix: what percentage use Analyst vs Search vs both vs no tools — this reveals how they interact with SI
- Agent breakdown: which named agents exist and their relative usage
- Credits: total SI credits and breakdown (orchestration, Analyst, Search)
- Performance: avg latency (AVG_DURATION_MS) — flag if P90 is high

**Sample answer structure**:
> Acme Corp has **active SI adoption** with ~X daily active users over the last 30 days, generating Y total requests across Z conversation threads.
>
> **How they use SI**: 45% of requests use Cortex Analyst (text-to-SQL), 30% use Cortex Search (document retrieval), 15% use both, and 10% use neither (direct LLM chat). This suggests a data-query-heavy use pattern.
>
> **Top agents**: "Finance Analyst" (A requests, B users) and "HR Bot" (C requests, D users). Average latency is Xms (P90: Yms) — [within normal range / worth investigating].
>
> **Credits**: Total SI credits = $N, split across orchestration ($O), Analyst ($P), and Search ($Q).

---

#### 5.2 Cortex Code
Cortex Code has its own dedicated table (below) AND appears in `a360_cortex_agents_*_day_fact_view` as `source = 'Coding Agent'`. Use the Cortex Code table for user-facing metrics; use the Cortex Agents tables for API-level call volume (counts will be higher due to backend calls).

**5.2a Account-Level**: `SALES.RAVEN.A360_CORTEX_CODE_ACCOUNT_DAY_FACT_VIEW`
**Best for**: Account-level Cortex Code adoption, broken down by origin (CLI, Desktop, UI)
**Schema note**: Metrics are column-prefixed by origin (CLI_, DESKTOP_, UI_) plus TOTAL_ aggregates. There is NO `ORIGIN` row-level column.

Key columns:
| Column | Type | Description |
|--------|------|-------------|
| DS | DATE | Date |
| DEPLOYMENT | VARCHAR | Deployment |
| ACCOUNT_ID | NUMBER | Snowflake account ID |
| SNOWFLAKE_ACCOUNT_NAME | VARCHAR | Snowflake account name |
| SALESFORCE_ACCOUNT_ID | VARCHAR | SFDC account ID |
| SALESFORCE_ACCOUNT_NAME | VARCHAR | Account name |
| INDUSTRY | VARCHAR | Industry |
| SUB_INDUSTRY | VARCHAR | Sub-industry |
| CLI_ACTIVE_USERS | NUMBER | CLI active users |
| CLI_DAILY_REQUESTS | NUMBER | CLI requests |
| CLI_DAILY_USER_PROMPTS | NUMBER | CLI user prompts |
| CLI_TOTAL_TOKENS | NUMBER | CLI total tokens |
| DESKTOP_ACTIVE_USERS | NUMBER | Desktop active users |
| DESKTOP_DAILY_REQUESTS | NUMBER | Desktop requests |
| DESKTOP_TOTAL_TOKENS | NUMBER | Desktop total tokens |
| UI_ACTIVE_USERS | NUMBER | UI (Snowsight) active users |
| UI_DAILY_REQUESTS | NUMBER | UI requests |
| UI_TOTAL_TOKENS | NUMBER | UI total tokens |
| UI_CODING_AGENT_REQUESTS | NUMBER | UI coding agent requests |
| UI_REASONING_AGENT_REQUESTS | NUMBER | UI reasoning agent requests |
| TOTAL_ACTIVE_USERS | NUMBER | Total active users across all origins |
| TOTAL_DAILY_REQUESTS | NUMBER | Total requests across all origins |
| TOTAL_DAILY_USER_PROMPTS | NUMBER | Total user prompts |
| TOTAL_TOKENS | NUMBER | Total tokens across all origins |

**Example queries**:
```sql
-- Cortex Code adoption for an account by origin
SELECT ds,
       cli_active_users, cli_daily_requests,
       desktop_active_users, desktop_daily_requests,
       ui_active_users, ui_daily_requests,
       total_active_users, total_daily_requests
FROM sales.raven.a360_cortex_code_account_day_fact_view
WHERE salesforce_account_name ILIKE '%customer_name%'
  AND ds >= CURRENT_DATE - 30
  AND ds < CURRENT_DATE
ORDER BY ds DESC;

-- Cortex Code weekly usage trend
SELECT DATE_TRUNC('week', ds) as week,
       SUM(total_active_users) as total_users,
       SUM(total_daily_requests) as total_requests,
       SUM(cli_daily_requests) as cli_requests,
       SUM(desktop_daily_requests) as desktop_requests,
       SUM(ui_daily_requests) as ui_requests
FROM sales.raven.a360_cortex_code_account_day_fact_view
WHERE salesforce_account_name ILIKE '%customer_name%'
  AND ds >= CURRENT_DATE - 60
  AND ds < CURRENT_DATE
GROUP BY week
ORDER BY week;
```

**Sample Q&A (Cortex Code)**:

> **Q**: "Is Acme Corp using Cortex Code?"

**Key components to include in the answer**:
- Adoption signal: total active users and whether it's growing
- Origin breakdown: CLI vs Desktop vs UI — this reveals developer workflow preferences
- Volume: total requests and user prompts (prompts = user-initiated, requests = total including system)
- Trend: weekly trend over 4-8 weeks to show adoption trajectory
- Agent features: if UI_CODING_AGENT_REQUESTS or UI_REASONING_AGENT_REQUESTS are non-zero, highlight agentic usage

**Sample answer structure**:
> Yes, Acme Corp has **X total active Cortex Code users** over the last 30 days with Y total requests.
>
> **By origin**:
> - **CLI**: A users, B requests — indicates developer adoption via terminal/IDE
> - **Desktop**: C users, D requests — native app usage
> - **UI (Snowsight)**: E users, F requests — browser-based usage
>
> Weekly usage has [grown from W to Z requests/week over the past 6 weeks / remained steady / declined]. They have G coding agent requests and H reasoning agent requests, showing [early agentic adoption / no agentic usage yet].

---

#### 5.3 Cortex Agents (All Sources)
Parent tables covering ALL Cortex Agent sources. SI views (5.1) are filtered views over these.
Source values: `'Snowflake Intelligence'`, `'Direct'`, `'Coding Agent'` (= Cortex Code), `'MCP'`, `'MS Teams'`, `'Inline Copilot'`

**5.3a Company-Level**: `SALES.RAVEN.A360_CORTEX_AGENTS_COMPANY_DAY_FACT_VIEW`
**Best for**: Cross-source comparison, total Cortex Agents adoption, non-SI agent usage
Same schema as `a360_si_company_day_fact_view` (5.1a) plus `SOURCE` column distinguishes the source.

**5.3b Agent-Level**: `SALES.RAVEN.A360_CORTEX_AGENTS_AGENT_DAY_FACT_VIEW`
**Best for**: Per-agent metrics across all sources, tool invocation breakdown
Same schema as `a360_si_agent_day_fact_view` (5.1b) plus `SOURCE` column.

**5.3c User-Level**: `SALES.RAVEN.A360_CORTEX_AGENTS_USER_DAY_FACT_VIEW`
**Best for**: Per-user activity across all sources

Same schema as 5.1c plus `SOURCE` column and these additional account-dimension columns:

| Additional Column | Type | Description |
|--------|------|-------------|
| AGREEMENT_TYPE | VARCHAR | Agreement type |
| SNOWFLAKE_ACCOUNT_TYPE | VARCHAR | Account type |
| ACCOUNT_STATUS | VARCHAR | Account status |
| INDUSTRY | VARCHAR | Industry |
| SUB_INDUSTRY | VARCHAR | Sub-industry |
| SEGMENT | VARCHAR | Customer segment |
| HAS_REVENUE_ON_DATE | BOOLEAN | Whether account has revenue on that date |
| SERVICE_LEVEL | VARCHAR | Service level |
| IS_ACTIVE_CAPACITY_FINANCE | BOOLEAN | Active capacity finance flag |
| BILLING_COUNTRY | VARCHAR | Billing country |

**Example queries**:
```sql
-- All Cortex Agents usage by source for a customer
SELECT ds, source, SUM(num_total_requests) as requests, SUM(total_credits) as credits
FROM sales.raven.a360_cortex_agents_company_day_fact_view
WHERE salesforce_account_name ILIKE '%customer_name%'
  AND ds >= CURRENT_DATE - 30
  AND ds < CURRENT_DATE
GROUP BY ds, source
ORDER BY ds, source;

-- Non-SI agent adoption (Direct API, MCP, Coding Agent, etc.)
SELECT source, SUM(num_total_requests) as requests,
       MAX(num_daily_active_users) as peak_dau
FROM sales.raven.a360_cortex_agents_company_day_fact_view
WHERE salesforce_account_name ILIKE '%customer_name%'
  AND source != 'Snowflake Intelligence'
  AND ds >= CURRENT_DATE - 30
  AND ds < CURRENT_DATE
GROUP BY source
ORDER BY requests DESC;
```
