# Architectural Decisions by Project Type

Resolve key architectural decisions early in the engagement. Unclear decisions lead to scope creep and rework.

---

## How to Use

1. Identify **Primary Module** from Step 1
2. Review decisions for that module
3. Surface any unclear decisions to user in Step 2
4. Document resolved decisions in Assumptions section

**⚠️ STOPPING POINT**: If architectural decisions are unclear, ask user before proceeding to effort estimation.

---

## Data Engineering

| Decision | Options | Impact | Questions to Ask |
|----------|---------|--------|------------------|
| **Multi-tenant data model** | Consolidated tables (tenant_id) vs Tenant-isolated (separate objects) | Object count, RBAC complexity, query patterns | How many tenants? Tenant-specific queries needed? Cross-tenant analytics? |
| **Medallion layer boundaries** | Transform in bronze vs silver vs gold | Pipeline complexity, reprocessing flexibility | Where does cleansing happen? Who owns each layer? |
| **Ingestion pattern** | Batch vs streaming vs micro-batch | Latency, cost, complexity | What latency is acceptable? How frequently does source update? |
| **Error handling** | Fail-fast vs dead-letter vs retry | Recovery time, data completeness | Is partial data acceptable? Who monitors failures? |
| **Partitioning strategy** | Date-based vs tenant-based vs hybrid | Query performance, clustering cost | Primary query patterns? Data retention policy? |
| **Schema evolution** | Schema-on-read vs strict schema | Flexibility vs data quality | How often do sources change schema? |

---

## ML/AI Projects

| Decision | Options | Impact | Questions to Ask |
|----------|---------|--------|------------------|
| **Inference pattern** | Batch scoring vs real-time API vs embedded UDF | Latency, cost, complexity | How quickly are predictions needed? Volume of predictions? |
| **Feature store approach** | Snowflake Feature Store vs custom tables vs external | Consistency, reusability, ops overhead | Feature reuse across models? Online vs offline features? |
| **Model serving** | Snowpark ML vs SPCS containers vs external | Control, cost, latency | Model framework? GPU requirements? |
| **MLOps pattern** | Manual retraining vs scheduled vs triggered | Freshness, ops overhead | How often does data drift? Retraining frequency? |
| **Experiment tracking** | Snowflake ML Registry vs MLflow vs other | Governance, reproducibility | Compliance requirements? Team collaboration needs? |
| **Model versioning** | Replace vs A/B vs shadow | Risk tolerance, rollback needs | How to validate new models? Rollback strategy? |

---

## Cortex GenAI

| Decision | Options | Impact | Questions to Ask |
|----------|---------|--------|------------------|
| **Knowledge approach** | RAG vs fine-tuning vs prompt engineering | Accuracy, cost, freshness | How specialized is the domain? Data update frequency? |
| **Embedding model** | Snowflake e5 vs external vs custom | Quality, cost, latency | Multilingual needs? Domain-specific vocabulary? |
| **Chunking strategy** | Fixed size vs semantic vs document-aware | Retrieval quality, cost | Document structure? Average document length? |
| **LLM model choice** | Llama vs Mistral vs Claude/GPT | Cost, quality, latency | Accuracy requirements? Budget constraints? |
| **Grounding approach** | Cortex Search vs direct context vs hybrid | Accuracy, token cost | Context window limits? Source diversity? |
| **Agent orchestration** | Single agent vs multi-agent vs human-in-loop | Complexity, reliability | Task complexity? Error tolerance? |
| **Guardrails** | Content filtering vs output validation vs both | Safety, latency | Compliance requirements? User-facing? |

---

## Apps / Streamlit

| Decision | Options | Impact | Questions to Ask |
|----------|---------|--------|------------------|
| **App architecture** | Single-page vs multi-page | Complexity, navigation | How many distinct workflows? User mental model? |
| **Session state** | Stateless vs session-cached vs persistent | Performance, complexity | User expectations for continuity? Data sensitivity? |
| **Caching strategy** | Query cache vs data cache vs none | Performance, freshness | Data update frequency? Query complexity? |
| **Authentication** | Snowflake native vs SSO vs public | Security, user experience | Who are the users? Compliance requirements? |
| **Data access pattern** | Direct query vs materialized views vs APIs | Performance, freshness | Query complexity? Concurrent users? |
| **Deployment model** | SiS (Snowflake-hosted) vs external | Control, integration | Need external integrations? Custom domains? |
| **Multi-tenant UI** | Role-based filtering vs separate apps | Maintenance, isolation | How different are tenant needs? |

---

## Migration Projects

| Decision | Options | Impact | Questions to Ask |
|----------|---------|--------|------------------|
| **Migration strategy** | Lift-and-shift vs re-architect vs hybrid | Effort, optimization | Timeline pressure? Technical debt tolerance? |
| **Cutover approach** | Big bang vs phased vs parallel run | Risk, duration, cost | Downtime tolerance? Rollback requirements? |
| **Data validation** | Row counts vs checksums vs full reconciliation | Confidence, effort | Audit requirements? Data sensitivity? |
| **Historical data** | Full history vs recent only vs archive | Storage cost, migration time | Retention requirements? Query patterns on history? |
| **Stored procedure conversion** | Rewrite vs translate vs Snowpark | Effort, maintainability | Procedure complexity? Long-term ownership? |
| **ETL migration** | Same tool vs Snowflake-native vs hybrid | Vendor lock-in, capabilities | Current tool satisfaction? Snowflake feature fit? |
| **Rollback plan** | Keep source active vs backup vs point-in-time | Safety, cost | Risk tolerance? Source system constraints? |

---

## Iceberg / Open Table Formats

| Decision | Options | Impact | Questions to Ask |
|----------|---------|--------|------------------|
| **Table management model** | Snowflake-managed vs externally managed vs mixed | Write ownership, metadata control, maintenance responsibility | Who writes to these tables? Does Snowflake or an external engine own the data? |
| **Catalog type** | AWS Glue vs REST catalog vs Unity Catalog vs Polaris vs multiple | Integration complexity, multi-engine compatibility, governance | What catalogs do existing engines already use? Need centralized governance? |
| **Polaris Catalog scope** | No Polaris vs Polaris for new tables vs Polaris as centralized catalog | Governance, credential vending, operational overhead | How many engines need access? Is centralized access control required? |
| **External volume topology** | Single volume vs per-domain vs per-region/cloud | Blast radius, IAM complexity, cross-region costs | How many storage locations? Single or multi-cloud? Data residency constraints? |
| **Storage location ownership** | Customer-owned buckets vs Snowflake-managed storage | Cost control, access patterns, egress | Who manages storage lifecycle? Need direct access from non-Snowflake engines? |
| **Auto-refresh strategy** | Notification-based (SNS/EventGrid) vs polling vs manual | Latency, cost, operational complexity | What freshness SLA? How frequently do external writers update tables? |
| **Table conversion approach** | In-place ALTER to Iceberg vs CREATE AS Iceberg vs parallel tables | Downtime, validation, rollback | Can we tolerate downtime? Need parallel validation period? |
| **Cross-engine write governance** | Single writer per table vs multi-writer with conflict resolution | Data consistency, complexity, recovery | Multiple engines writing same tables? How to handle conflicts? |
| **Snapshot retention policy** | Minimal (cost savings) vs extended (time travel / audit) | Storage cost, recovery flexibility | Compliance requirements? Need point-in-time recovery? How far back? |
| **Migration strategy** | Big bang conversion vs phased by domain vs hybrid | Risk, duration, validation effort | Timeline pressure? Can downstream consumers handle gradual migration? |

---

## Security / RBAC

| Decision | Options | Impact | Questions to Ask |
|----------|---------|--------|------------------|
| **Role hierarchy** | Flat vs nested vs functional+data split | Complexity, maintainability | Organization structure? Role proliferation concerns? |
| **Access pattern** | Role-based vs tag-based vs hybrid | Flexibility, governance | How dynamic are access rules? Data classification maturity? |
| **Masking approach** | Static vs dynamic vs tokenization | Security, performance | Data sensitivity levels? Cross-environment needs? |
| **Row-level security** | Row access policies vs secure views vs mapping tables | Performance, maintainability | How many tenants/segments? Query patterns? |
| **Service account strategy** | Shared vs per-application vs per-environment | Security, ops overhead | Audit requirements? Blast radius concerns? |
| **Privileged access** | Just-in-time vs standing vs break-glass | Security, operational friction | Compliance requirements? Incident response needs? |

---

## Cross-Cutting Decisions (All Projects)

| Decision | Options | Impact | Questions to Ask |
|----------|---------|--------|------------------|
| **Environment strategy** | Dev/Test/Prod vs Dev/Prod vs single | Cost, safety, velocity | Deployment frequency? Testing requirements? |
| **CI/CD approach** | Snowflake CLI vs Terraform vs SchemaChange vs manual | Automation, consistency | Team DevOps maturity? Existing tooling? |
| **Monitoring** | Snowflake native vs external vs hybrid | Visibility, cost | Existing observability stack? Alert routing? |
| **Cost allocation** | Tags vs resource monitors vs both | Governance, accountability | Chargeback requirements? Budget ownership? |
| **Documentation** | In-repo vs Confluence vs Snowflake comments | Discoverability, maintenance | Team documentation culture? Compliance needs? |
