---
name: sales_knowledge
description: >
  Search Sales Knowledge Assistant and Confluence for product knowledge,
  competitive positioning, value propositions, sales processes, customer
  stories, and industry knowledge. Use when product knowledge, competitive
  positioning, value proposition, how to sell, customer story, sales process,
  pricing, contracting, sales blueprint, industry knowledge, partner, SE
  resources. Do NOT use for meeting history, account data, consumption,
  product launch timelines, org chart, support cases.
created_date: 2026-03-10
last_updated: 2026-03-16
owner_name: Jake Kambourian
version: 1.0.0
---

# Knowledge Discovery & Self-Training

Powered by Sales Knowledge Assistant and Confluence (via Rovo Search) for AE/Sales Reps and SE/Solution Engineers.

## Table of Contents
1. [When to Use](#when-to-use)
2. [When NOT to Use](#when-not-to-use)
3. [Example Questions](#example-questions)
4. [Data Sources](#data-sources)
5. [Workflow](#workflow)
6. [Stopping Points](#stopping-points)
7. [Tools Used](#tools-used)
8. [Tips](#tips)
9. [Error Handling](#error-handling)
10. [Output](#output)

## When to Use

- **Product knowledge & features** - Snowflake product capabilities, value propositions, best practices (e.g., "What is the value of Iceberg Tables?")
- **Snowflake solutions** - Solution architectures, use-case-specific guidance, industry solutions (e.g., "What are common data platform security requirements in healthcare?")
- **Customer success stories** - Customer presentations, case studies with context on customer goals, challenges, and outcomes
- **Competitive positioning** - How to position Snowflake against competitors, selling points, differentiation (e.g., "Top three competitive selling points against Databricks focused on governance, total cost, and serverless")
- **Sales processes & playbooks** - Sales Blueprint, pricing, deal making, contracting, escalation paths
- **Sales tooling** - Internal tools available to sales teams (e.g., Salesforce, Clari, Gong) and their purpose
- **Training & enablement** - Sales training materials, onboarding content, self-training resources
- **Partner knowledge** - Snowflake partner ecosystem, joint solutions, partner programs
- **Industry-specific knowledge** - Vertical-specific requirements, certifications, compliance (e.g., healthcare, financial services)
- **Customer support knowledge** - General resolution guides, troubleshooting best practices, support knowledge base articles (for specific case details, use SUPPORT_CASES tools)

## When NOT to Use

- **News or current events** — use web search
- **Meeting history, transcripts, or participant questions** — use engagement tools
- **Real-time account data** (consumption, revenue, ARR) — use Salesforce/Raven data tools
- **Opportunity or deal data** (pipeline, bookings, forecasts) — use SALES_DATA_ASSISTANT
- **Account team or ownership lookups** — use ACCOUNT_LOOKUP
- **Product launch timelines or GA dates** ("When is X GA?") — use PLT tools
- **Org chart or reporting structure** — use ORGCHART tools
- **Support case details** — use SUPPORT_CASES tools

## Example Questions

- "What is the value of Iceberg Tables?"
- "What sales tools are available for account research?"
- "Give me the top three competitive selling points against Databricks. Focus on governance, total cost and Databricks serverless."
- "What are the common data platform security requirements, processes and certifications in the healthcare industry?"
- "How does Snowflake position against BigQuery for AI/ML workloads?"
- "Tell me about a customer success story in financial services"
- "What is the Sales Blueprint process?"

## Data Sources

### Sales Knowledge Assistant (Cortex Search Service)

**Service:** `SALES.KNOWLEDGE_ASSISTANT.FILE_SEARCH_SERVICE_PAGENUM_PROD`
**Search column:** `CHUNK_TEXT`
**Key columns:** `FILE_NAME`, `FILE_TYPE`, `FILE_PATH`, `DESCRIPTION`, `PAGE_NUM`, `SEISMIC_LINK`, `FILE_NAME_WITH_PAGE_NUM`, `FLAG_EX_OR_IN`
**~50K indexed chunks** covering:
- Snowflake products & features documentation
- Snowflake solutions & value propositions
- Sales training materials & enablement content
- Competitive positioning & battlecards
- Sales processes (Sales Blueprint, pricing, deal making, contracting)
- Customer presentations & success stories (with customer context, goals, outcomes)
- Customer support knowledge base articles & training material
- Partner ecosystem documentation
- Industry-specific Snowflake knowledge (healthcare, financial services, etc.)

### Confluence (via Rovo Search)

Rovo Search provides semantic search across all Confluence spaces (no space filtering needed). It understands query intent rather than matching keywords, returning results from any relevant space including SE, SALES, GTM, SKE, gsrl, CustomerSupport, FLOW, EN, and others.

**Why Rovo over CQL:** Evaluated in a 4-way controlled experiment (naive CQL, enhanced CQL, Rovo Search, expanded CQL). Rovo Search achieved 4.1/5 relevance vs CQL's best 2.4/5 — semantic understanding is the primary differentiator, not space coverage.

## Workflow

### Step 1: Understand the Request

**If the user's intent is clear**, skip directly to Step 1b. Only print the topic menu below when the user's message is broad or exploratory (e.g., "help me learn", "what can you search?"):

```
I can help with:
- Product knowledge - Features, capabilities, value propositions, best practices
- Snowflake solutions - Solution architectures, use-case guidance, industry solutions
- Customer stories - Success stories, customer presentations, case studies
- Competitive positioning - Battlecards, selling points, differentiation
- Sales process/playbook - Sales Blueprint, pricing, contracting, deal making
- Sales tooling - Internal tools available to sales teams
- Training & enablement - Sales training, onboarding, self-training
- Industry knowledge - Vertical-specific requirements, certifications, compliance
- General search - Open-ended knowledge discovery
```

**Parse the user's message directly.** The user's question is already provided in their message. Only use `ask_user_question` if genuine clarification is needed (e.g., the message is too vague to form a search query). Extract from it:
- Topic or question
- Specific product, competitor, or industry (if applicable)
- Customer name or vertical (if applicable)

If the user's message is too vague to search (e.g., just "help" with no topic), ask for clarification before searching.

**Routing note:** If a user asks about sales tooling, they are asking about tools available to them as end users (e.g., Salesforce, Clari, Gong). Use the Cortex Search Service to find information about internal tools available to sales teams. Only answer from retrieved content — do not supplement with general knowledge.

### Step 1b: Route by Intent

After parsing the request, classify the intent and route to the appropriate source(s). **You MUST state which route you are taking and why before executing any searches** (e.g., "Routing: both_parallel — competitive positioning question needs battlecards from KA and field notes from Confluence"). This ensures routing decisions are deliberate, not defaulted.

**Check for boundary questions FIRST.** Before classifying intent, check if the question falls outside this skill's scope:

| Boundary Signal | Example Patterns | Action |
|----------------|------------------|--------|
| **GA dates, release timelines, feature availability** | "When is X GA?", "timeline for X", "is X in preview?" | **Redirect to PLT tools.** Say: "Product launch timelines are maintained by the PLT team. Use the PLT skill for authoritative dates. Here's what I found in sales materials about [X] capabilities:" then provide a brief KA-only search for context. |
| **Real-time pricing calculations, credit estimates** | "How much will X cost per month?", "estimate credits for Y" | **Redirect to cost tools.** Say: "For real-time cost estimates, use the cost calculator or pricing tools. Here's what sales materials say about [X] pricing model:" then provide a brief KA-only search. |
| **Account-specific data, consumption, ARR** | "What's [Company]'s consumption?", "ARR for [account]" | **Redirect to Raven/Salesforce tools.** Do not search KA or Confluence for account-specific metrics. |
| **Meeting history, transcripts, call notes** | "What did we discuss with [Company]?", "last meeting notes" | **Redirect to engagement tools.** Do not search. |

If the question is NOT a boundary question, classify intent using this routing table:

| Intent | Route | Rationale |
|--------|-------|-----------|
| **Pricing, cost, credits** | **KA first** — skip Confluence unless KA results are thin | KA has curated pricing decks, cost models, credit tables. Confluence rarely has better pricing info. (Eval: KA won 64% of pricing queries) |
| **Competitive positioning, vs competitor** | **All three in parallel (KA + Confluence + web_search)** | Neither internal source alone is sufficient — KA has battlecards, Confluence has field notes, and `web_search` provides current competitor documentation (see Step 3). |
| **Value propositions, positioning** | **Confluence first** — add KA if Confluence is thin | Confluence has richer, more current value prop content. (Eval: Confluence won 44% vs KA 22%) |
| **How-to, process, playbook, blueprint** | **Confluence first** — add KA for supporting decks | Confluence has living process docs maintained by teams. KA may have stale snapshots. (Eval: Confluence won 4x more than KA on how-to queries) |
| **Product explainer (what is X, explain X)** | **Both in parallel** | Split evenly — KA has official product docs, Confluence has SRRs and best-practice guides. |
| **Customer story, case study, migration example** | **KA first** — add Confluence for recent/niche stories | KA has curated case study decks. Confluence supplements with field-submitted stories. (Eval: KA won 50% of customer story queries) |
| **Deck, slide, presentation, material** | **KA first** — skip Confluence unless KA has no match | KA indexes Seismic content (PPTs, PDFs). Confluence rarely has downloadable decks. |
| **Industry-specific, vertical** | **Both in parallel** | Weak signal from either source alone — need both for coverage. (Eval: 40% of industry queries had neither source sufficient) |
| **Named account or company** | **Both in parallel** | KA may have account-specific decks; Confluence may have field notes or project pages. |
| **Non-English queries** | **Both in parallel** | Both sources struggle — cast a wide net. Consider translating to English for a supplementary search. |

**Default (unclear intent):** Search both in parallel.

**"Skip Confluence" / "Skip KA" means:** Do not search that source in the initial round. If the primary source returns < 3 relevant results (relevance score < 3), then search the skipped source as a fallback in Step 6.

### Step 2: Search Cortex Search Service (Internal Sales Knowledge Assistant)

Search KA when the routing table above includes it for the detected intent. It contains ~50K chunks of internal sales docs, battlecards, presentations, and also includes Snowflake product documentation.

**Execute search using SQL:**

```sql
SELECT
  r.value:FILE_NAME::STRING AS FILE_NAME,
  r.value:FILE_TYPE::STRING AS FILE_TYPE,
  r.value:DESCRIPTION::STRING AS DESCRIPTION,
  r.value:PAGE_NUM::STRING AS PAGE_NUM,
  r.value:SEISMIC_LINK::STRING AS SEISMIC_LINK,
  r.value:FILE_NAME_WITH_PAGE_NUM::STRING AS FILE_NAME_WITH_PAGE_NUM,
  r.value:FLAG_EX_OR_IN::STRING AS FLAG_EX_OR_IN,
  r.value:CHUNK_TEXT::STRING AS CHUNK_TEXT
FROM TABLE(FLATTEN(
  PARSE_JSON(
    SNOWFLAKE.CORTEX.SEARCH_PREVIEW(
      'SALES.KNOWLEDGE_ASSISTANT.FILE_SEARCH_SERVICE_PAGENUM_PROD',
      '{
        "query": "<user_query>",
        "columns": ["FILE_NAME", "FILE_TYPE", "DESCRIPTION", "PAGE_NUM",
                     "SEISMIC_LINK", "FILE_NAME_WITH_PAGE_NUM", "FLAG_EX_OR_IN", "CHUNK_TEXT"],
        "limit": 10
      }'
    )
  ):results
)) r;
```

**Extract from results:**
- Relevant document names and descriptions
- Key content chunks that answer the question
- Seismic links for full document access
- Page numbers for precise references
- `FLAG_EX_OR_IN` — **External** means the content is approved to share with customers/clients. **Internal** means use with caution: mask account names, redact sensitive info, and do not share directly with customers.

### Step 3: Search Competitor Documentation (Web Search)

Search competitor documentation when the routing table in Step 1b includes `web_search` for the detected intent (primarily competitive positioning queries).

#### Web Fetch Guardrail

**CRITICAL — NEVER use `web_fetch` in this skill.** Rely exclusively on `web_search` results (titles, URLs, and any available snippets) for all competitor intelligence. Even when snippets are empty, the result titles and URLs reveal competitor feature names, documentation structure, and product capabilities — use these signals to inform your competitive positioning answers.

**Rules:**
1. **NEVER use `web_fetch` on competitor domains under any circumstances.** Competitors include but are not limited to: Databricks, Amazon Redshift, ClickHouse, Firebolt, Google BigQuery, Google (Platform), Microsoft Fabric / Azure Synapse, Oracle, Teradata, IBM, Cloudera, Vertica, Dremio, Starburst, Palantir, Greenplum, Yellowbrick, Exasol, Actian, Microfocus (OpenText), SAP, Fivetran, dbt Labs, or any other data/cloud/AI vendor that competes with Snowflake. This is a strict compliance requirement.
2. If `web_search` results lack detail (empty snippets or vague titles), run additional `web_search` queries with more specific keywords instead of fetching pages. Try variations: include the competitor product name, specific feature names, or version numbers.

#### Key Competitors

| Competitor | Key Differentiators | Search Query |
|------------|---------------------|--------------|
| **Databricks** | Lakehouse, ML/AI, Spark, Unity Catalog | `web_search` → `site:docs.databricks.com {topic}` |
| **Amazon Redshift** | AWS native, Spectrum, ML | `web_search` → `site:docs.aws.amazon.com/redshift {topic}` |
| **ClickHouse** | Real-time analytics, columnar storage, open source | `web_search` → `site:clickhouse.com/docs {topic}` |
| **Firebolt** | Sub-second analytics, decoupled storage/compute, indexing | `web_search` → `site:docs.firebolt.io {topic}` |
| **Google BigQuery** | Serverless, ML integration, Looker | `web_search` → `site:cloud.google.com bigquery {topic}` |
| **Google (Platform)** | Vertex AI, AlloyDB, Cloud Spanner, GCS | `web_search` → `site:cloud.google.com data analytics {topic}` |
| **Microsoft Fabric / Azure Synapse** | Microsoft ecosystem, Fabric | `web_search` → `site:learn.microsoft.com azure synapse {topic}` |
| **Oracle** | Autonomous Database, Exadata, enterprise ERP integration | `web_search` → `site:docs.oracle.com autonomous database {topic}` |
| **Teradata** | Enterprise DW, VantageCloud, hybrid multi-cloud | `web_search` → `site:docs.teradata.com vantage {topic}` |
| **IBM** | Db2 Warehouse, watsonx.data, Netezza, mainframe integration | `web_search` → `site:ibm.com/docs db2 warehouse {topic}` |
| **Cloudera** | Hybrid data platform, open source Hadoop/Spark, CDP | `web_search` → `site:docs.cloudera.com cdp {topic}` |
| **Vertica** | Columnar analytics, on-prem/cloud, Vertica Accelerator | `web_search` → `site:vertica.com documentation {topic}` |
| **Dremio** | Data lakehouse, Apache Iceberg native, Arrow Flight | `web_search` → `site:docs.dremio.com lakehouse {topic}` |
| **Starburst** | Trino-based, federated queries, data mesh, Galaxy SaaS | `web_search` → `site:docs.starburst.io trino {topic}` |
| **Palantir** | Foundry platform, AIP, ontology-driven analytics | `web_search` → `site:palantir.com/docs foundry {topic}` |
| **Greenplum** | MPP PostgreSQL, open source analytics, VMware Tanzu | `web_search` → `site:greenplum.org documentation {topic}` |
| **Yellowbrick** | Hybrid cloud DW, Kubernetes-native, real-time analytics | `web_search` → `site:yellowbrick.com documentation {topic}` |
| **Exasol** | In-memory analytics, high performance, European market | `web_search` → `site:docs.exasol.com {topic}` |
| **Actian** | Vector analytics, HCL integration, hybrid deployments | `web_search` → `site:docs.actian.com {topic}` |
| **Microfocus (OpenText)** | Vertica (parent), enterprise data management, COBOL | `web_search` → `site:microfocus.com documentation {topic}` |

#### Competitor Research Process

When answering competitive positioning questions, supplement internal knowledge (Sales Knowledge Assistant + Confluence) with competitor documentation:

1. **Identify the competitor** from the user's query and find it in the table above
2. **Use `web_search`** with the site-scoped query from the Search Query column, replacing `{topic}` with the specific feature or capability being compared. Use **either** `site:domain.com` in the query string **or** the `allowed_domains` parameter — never both together (combining them causes the search to fail).
3. **Extract intelligence from results** — `web_search` returns titles, URLs, and occasionally text snippets. Snippets may be empty depending on the search engine backend. When snippets are available, use them directly. When they are not, infer competitor capabilities from page titles and URL paths (e.g., a title like "Unity Catalog Governance in Action: Monitoring, Reporting, and Lineage" confirms Databricks offers governance monitoring and lineage features). Do NOT follow up with `web_fetch` to load full pages.
4. **Run follow-up searches if needed** — if the first query returns only generic results, run a second `web_search` with narrower terms (e.g., add specific feature names, version numbers, or "vs Snowflake") to surface more targeted pages
5. **Merge findings** with internal Sales Knowledge Assistant and Confluence results to produce a balanced, well-sourced answer

### Step 4: Search Confluence (Rovo Search)

Search Confluence when the routing table in Step 1b includes it for the detected intent. Rovo is a semantic search engine — it understands query intent, so you can pass natural language queries directly (no keyword decomposition needed).

#### 4a. Run Rovo Search

Use `mcp_atlassian-mcp_search` with the user's question as the query:
- `query`: the user's question or a refined version of it

Rovo searches across all Confluence spaces and also returns Jira results. **Filter results mentally to Confluence pages** — ignore Jira issues in the results.

Examples:
| User Question | Rovo Query |
|---------------|------------|
| "What is the value of Iceberg Tables?" | `Iceberg Tables value proposition` |
| "Top competitive selling points against Databricks" | `Databricks competitive positioning selling points` |
| "What is the Sales Blueprint process?" | `Sales Blueprint process` |
| "How to handle pricing objections?" | `pricing objection handling` |

#### 4b. Evaluate Results

Rovo returns results ranked by semantic relevance. Review the top results and identify the **3-5 most relevant Confluence pages** based on:
- Title relevance to the user's question
- Excerpt content matching the topic
- Content type (prefer playbooks, guides, battlecards over meeting notes)

If results are sparse or off-topic, try a **refined query** — rephrase the question, use specific product names, or break a multi-part question into separate searches.

#### 4c. Read Full Page Content

For the **top 1-2 most relevant results**, fetch full page content using `mcp_atlassian-mcp_getConfluencePage`:
- `cloudId`: `6020aaef-9082-4a4e-a21a-d47b98ba3ddc` (Snowflake Atlassian instance)
- `pageId`: the page ID from search results
- `contentFormat`: `markdown`

**Note the `lastModified` date** on each Confluence result — include it when presenting sources so users can gauge content freshness. (Note: KA `DS` is a batch ingest date, not comparable to Confluence edit dates.)

### Step 5: Synthesize with Source Conflict Resolution

**This is the critical step.** When sources (KA, Confluence, and/or web_search) return information on the same topic, they may disagree. Use the following resolution logic.

**Web search results are supplementary, not authoritative.** For Snowflake positioning and messaging, always prefer KA and Confluence over web search. Web search provides the competitor's perspective — use it to verify competitor claims and identify features to position against, not as the basis for Snowflake's value proposition.

#### 5a. Check for Agreement

If both sources say essentially the same thing, combine them into a single answer with citations from both. This is the common case — proceed to presenting results.

#### 5b. Resolve Conflicts

When sources disagree, apply two categories of resolution signals:

**Category 1: Metadata-based signals** (apply using structured fields from search results):

| Signal | Rule | Rationale |
|--------|------|-----------|
| **Query type: Value propositions, competitive positioning, sales messaging** | **Prefer KA** | KA contains curated Seismic content — polished, approved battlecards and decks. Confluence may have informal or outdated field notes on these topics. |
| **Query type: Processes, playbooks, team-specific procedures** | **Prefer Confluence** | Confluence has living process docs maintained by teams. KA may have stale snapshots of older process decks. |
| **`FLAG_EX_OR_IN` = External** | **Weight KA result higher** | External content is approved to share with customers. Internal content may contain sensitive account names or confidential details — use with caution and redact before sharing. |

**Category 2: LLM-evaluated signals** (assess by reading the actual content returned from both sources):

| Signal | Rule | Rationale |
|--------|------|-----------|
| **Completeness** | **Prefer the more thorough answer** | If one source provides a comprehensive answer and the other has only a fragment or tangential mention, prefer the complete one. |
| **Professionalism / polish** | **Prefer polished, official content** | A formatted battlecard or slide deck with structured messaging is more reliable than informal wiki notes or meeting minutes. |

**Important: Date-based recency is NOT a usable signal.** The KA `DS` field is a batch ingest date (when the ETL pipeline processed the file), not a content publish or modification date. Confluence `lastModified` is a true edit date. These measure different things and cannot be meaningfully compared.

#### 5c. Transparency

**Always disclose conflicts to the user.** When sources disagree:

```
**Source Conflict Detected**

**Sales Knowledge Assistant** says: [summary of KA position]
**Confluence** says: [summary of Confluence position]

**Recommended answer:** [resolution based on signals above]
**Why:** [which signal(s) drove the resolution]
```

Do NOT silently pick one source. The user needs to know when sources conflict so they can apply their own judgment.

#### 5d. Present Results

Every answer MUST include all four sections below. Do not skip any section — this is the skill's output contract.

**1. Direct Answer** — Concise answer to the user's question (with conflict disclosure if applicable). Lead with the answer, not preamble.

**2. Source Documents** — Table of relevant documents with clickable links. Every row MUST have a working URL (Seismic link for KA results, Confluence page URL for Confluence results). If a Seismic link is unavailable, note the file name and page number instead.

   | Source | Document | Link | Relevance |
   |--------|----------|------|-----------|
   | Sales Knowledge Assistant | [File Name] | [Seismic Link] | [Brief note] |
   | Confluence | [Page Title] | [Page URL] | [Brief note] |
   | Web Search | [Result Title] | [Result URL] | [Brief note] |

**3. Key Excerpts** — Include at least one direct quote (blockquote `>`) from each source used. These give the user verifiable evidence without requiring them to click through. If only one source was used, include at least two excerpts from it.

**4. Related Topics** — Always suggest 2-3 follow-up searches the user could run. Frame as actionable questions, e.g.:
   - "Want to go deeper? Try: 'Iceberg Tables vs Delta Lake competitive positioning'"
   - "Related: 'Customer objection handling for governance features'"
   Even if the topic seems fully covered, suggest adjacent topics or deeper dives.

**If no results found:**
- Suggest alternative search terms
- Recommend specific Confluence spaces to browse manually
- Offer to search with broader or narrower terms

### Step 6: Iterative Cross-Source Search (Automatic)

**Automatically trigger this step when ANY of these conditions are true:**

- **Single-source answer** — If only KA or only Confluence was searched/returned results, ALWAYS search the other source before presenting the final answer. This is the most common gap in answer quality.
- **Routing fallback** — Step 1b skipped a source, but the primary source returned < 3 relevant results. Search the skipped source now.
- **Multi-part questions** — e.g., "Tell me about Iceberg Tables and how to handle customer objections" requires both product knowledge AND objection-handling content
- **Gaps in initial results** — Step 5 synthesis reveals missing angles (e.g., found product features but no competitive positioning or objection responses)
- **New terms or context discovered** — initial results surface specific terminology, competitor names, customer names, or document titles that can be used as better search queries

**Process:**

1. **Identify gaps** from Step 5 synthesis — what aspects of the user's question remain unanswered?
2. **Formulate refined queries** using context from initial results. Examples:
   - Initial query: "Iceberg Tables objection handling"
   - From Step 2 results, learned the product is also called "Apache Iceberg" and competes with "Delta Lake"
   - Refined query for Sales Knowledge Assistant: "Iceberg Tables objection handling Delta Lake compete"
   - Refined Rovo query for Confluence: "Iceberg Tables objection handling Delta Lake"
3. **Run targeted searches** across the most relevant source(s):
   - Use Sales Knowledge Assistant (Step 2 SQL) with the refined query
   - Use Confluence (Step 4a-4b) with a refined Rovo query
   - Use `web_search` (Step 3) with refined competitor queries
4. **Merge new findings** into the existing synthesis from Step 5, applying the same conflict resolution rules

**Stop iterating when:**
- All facets of the user's question are addressed
- Two search rounds have been completed (max 2 iterations to avoid excessive latency)
- Additional searches return no new relevant information

### Step 7: Deep Dive (On Request)

If user wants more detail on a specific result:

1. **For Sales Knowledge Assistant results:** Search again with refined query targeting the specific document
2. **For Confluence pages:** Fetch full page content using `mcp_atlassian-mcp_getConfluencePage`
3. **Cross-reference:** Search for the same topic in the other source to find complementary information

## Stopping Points

- After Step 1: If the user's message is too vague, ask for clarification inline (no dialog) before searching
- After Step 5: Present initial results; automatically proceed to Step 6 if gaps are identified
- After Step 6: Present complete results and ask if user needs a deep dive (Step 7)

## Tools Used

| Tool | Purpose |
|------|---------|
| `snowflake_sql_execute` | Query Cortex Search Service via `SNOWFLAKE.CORTEX.SEARCH_PREVIEW` for internal sales knowledge |
| `mcp_atlassian-mcp_search` | Search Confluence pages via Rovo semantic search |
| `mcp_atlassian-mcp_getConfluencePage` | Read full Confluence page content by page ID |
| `web_search` | Search competitor documentation for competitive positioning (see Key Competitors table in Step 3) |

**NEVER use `web_fetch` for competitor research.** See the Web Fetch Guardrail in Step 3 for the full compliance policy.

## Tips

- **Combine sources:** Cortex Search has sales enablement docs (PDFs, PPTs); Confluence has living knowledge base pages. Use both for comprehensive answers.
- **Page numbers matter:** Use `FILE_NAME_WITH_PAGE_NUM` to give users precise references into long documents.
- **Seismic links:** Always include `SEISMIC_LINK` when available - these give direct access to the full document in Seismic.
- **Rovo Search:** Pass natural language queries directly — Rovo understands intent, so no keyword decomposition is needed. If results are poor, try rephrasing or using more specific product/feature names. Filter results to Confluence pages (ignore Jira issues).
- **Always cite sources:** For all answers, include links (Seismic links, Confluence URLs, etc) so users can verify and explore further.
- **Conflict transparency:** Never silently resolve a source conflict. Always show the user what each source said and why you chose one.

### Category-Specific Depth Guidance

- **Customer stories:** Include the customer name (or anonymized vertical), the challenge they faced, the Snowflake solution deployed, and quantified outcomes where available. Thin answers here erode trust — aim for a narrative arc, not just bullet points.
- **Competitive positioning:** Always include both offensive (why Snowflake wins) and defensive (handling objections) angles. Include the competitor name explicitly in your answer. Use `web_search` with site-scoped queries from the Key Competitors table (Step 3) to supplement internal sources with current competitor documentation.
- **Industry-specific:** These questions often have weak signal from both sources. If initial results are thin, run a second search with specific compliance frameworks, regulations, or certifications mentioned in the first round.
- **Boundary questions:** When redirecting, still provide a brief (2-3 sentence) summary of what sales materials say about the topic so the user isn't left empty-handed.

## Error Handling

- **Cortex Search Service fails or returns 0 results:** Tell the user the Sales Knowledge Assistant is unavailable, search Confluence only, and note the reduced coverage.
- **Rovo Search fails or returns 0 results:** Tell the user Confluence search is unavailable, proceed with KA results only, and note the reduced coverage.
- **Both sources fail:** Inform the user that both search services are unavailable and suggest they try again later or search Seismic/Confluence directly.
- **Rovo returns only Jira issues (no Confluence pages):** Treat as 0 Confluence results — do not synthesize from Jira issues.
- **Web search fails, returns 0 results, or is unavailable:** Proceed with KA and Confluence results only. Note to the user that competitor documentation was not available for this answer. Do not fall back to `web_fetch`.

## Output

Every answer MUST contain these four sections (see Step 5d for details):

1. **Direct Answer** — Lead with the answer. Include conflict disclosure if sources disagree.
2. **Source Documents** — Table with clickable Seismic/Confluence links for every cited document.
3. **Key Excerpts** — At least one blockquote (`>`) per source used.
4. **Related Topics** — 2-3 follow-up questions the user could ask next.
