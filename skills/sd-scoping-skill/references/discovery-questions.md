# Discovery Questions by Module

This document provides discovery questions for each scoping module. Use these questions during customer conversations to gather requirements.

---

## Account Setup & RBAC

### Key Discovery Questions
1. What is your current identity provider (Okta, Azure AD, etc.)?
2. How many roles do you anticipate needing?
3. Do you have existing RBAC documentation or role hierarchy?
4. What compliance requirements apply (SOC2, HIPAA, PCI)?
5. How many users will need access?
6. Do you need functional roles vs access roles separation?
7. What is your network policy requirement (IP allowlisting)?

### Reference Documents
| Document | Location | Glean Search |
|----------|----------|--------------|
| RBAC Best Practices | `<TBD>` | `<TBD>` |
| SSO Configuration Guide | `<TBD>` | `<TBD>` |
| Security Questionnaire | `<TBD>` | `<TBD>` |

---

## Data Engineering

### Key Discovery Questions
1. What are your primary data sources (databases, APIs, files)?
2. What is the expected data volume (GB/TB per day)?
3. What latency requirements do you have (batch, near-real-time, real-time)?
4. Do you have existing ETL/ELT tools (Fivetran, dbt, Informatica)?
5. How many pipelines/data flows need to be built?
6. What is your medallion architecture preference (Bronze/Silver/Gold)?
7. Do you need change data capture (CDC)?

### Reference Documents
| Document | Location | Glean Search |
|----------|----------|--------------|
| Data Engineering Patterns | `<TBD>` | `<TBD>` |
| Pipeline Architecture Guide | `<TBD>` | `<TBD>` |
| dbt Best Practices | `<TBD>` | `<TBD>` |

---

## BC/DR (Business Continuity / Disaster Recovery)

### Key Discovery Questions
1. What is your target RTO (Recovery Time Objective)?
2. What is your target RPO (Recovery Point Objective)?
3. How many databases need DR protection?
4. What regions are you currently deployed in?
5. What is the secondary/failover region preference?
6. Do you have existing DR runbooks or playbooks?
7. What level of DR testing is required (tabletop, full failover)?
8. Are there compliance requirements driving DR (SOC2, regulatory)?

### Reference Documents
| Document | Location | Glean Search |
|----------|----------|--------------|
| BC/DR Planning Template | `<TBD>` | `<TBD>` |
| Replication Best Practices | `<TBD>` | `<TBD>` |
| Failover Runbook Template | `<TBD>` | `<TBD>` |

---

## Cortex AI

### Key Discovery Questions
1. What AI/ML use cases are you targeting?
2. Are preview features acceptable for your timeline?
3. How many personas/user groups will use the AI features?
4. Do you have existing data for semantic models?
5. What search/retrieval requirements do you have?
6. Do you need Snowflake Intelligence or Cortex Agents?
7. What is your LLM preference (Snowflake-hosted vs external)?

### Reference Documents
| Document | Location | Glean Search |
|----------|----------|--------------|
| Cortex AI Overview | `<TBD>` | `<TBD>` |
| Semantic Model Guide | `<TBD>` | `<TBD>` |
| Cortex Search Patterns | `<TBD>` | `<TBD>` |

---

## Dashboard/Analytics

### Key Discovery Questions
1. What BI tools are currently in use (Tableau, PowerBI, Looker)?
2. How many dashboards/reports need to be built?
3. Who are the target users (executives, analysts, operations)?
4. Do you need Streamlit apps or native BI connectivity?
5. What are the refresh frequency requirements?
6. Do you need semantic layer/metrics definitions?
7. What row-level security requirements exist?

### Reference Documents
| Document | Location | Glean Search |
|----------|----------|--------------|
| Streamlit Best Practices | `<TBD>` | `<TBD>` |
| BI Connectivity Guide | `<TBD>` | `<TBD>` |
| Dashboard Design Patterns | `<TBD>` | `<TBD>` |

---

## Machine Learning

### Key Discovery Questions
1. What ML use cases are you targeting (classification, regression, forecasting)?
2. Do you have existing models to deploy or need new model development?
3. What is your preferred ML framework (scikit-learn, XGBoost, PyTorch)?
4. Do you need feature engineering support?
5. What is your MLOps maturity (manual, automated, CI/CD)?
6. Do you need model registry and versioning?
7. What inference pattern is needed (batch, real-time)?

### Reference Documents
| Document | Location | Glean Search |
|----------|----------|--------------|
| Snowpark ML Guide | `<TBD>` | `<TBD>` |
| Feature Store Patterns | `<TBD>` | `<TBD>` |
| Model Registry Best Practices | `<TBD>` | `<TBD>` |

---

## Native Apps

### Key Discovery Questions
1. Is this for internal use or Marketplace distribution?
2. What functionality will the app provide?
3. How many consumers/tenants are expected?
4. What data sharing model is needed (reader accounts, listings)?
5. Do you need Streamlit UI components?
6. What security/isolation requirements exist?
7. What is the monetization model (free, paid, usage-based)?

### Reference Documents
| Document | Location | Glean Search |
|----------|----------|--------------|
| Native App Framework Guide | `<TBD>` | `<TBD>` |
| Marketplace Listing Guide | `<TBD>` | `<TBD>` |
| Multi-tenant Patterns | `<TBD>` | `<TBD>` |

---

## Migration

### Key Discovery Questions
1. What is the source platform (Oracle, Teradata, SQL Server, Redshift, Databricks)?
2. What is the total data volume to migrate?
3. How many objects need migration (tables, views, stored procedures)?
4. What is the migration timeline and cutover window?
5. Do you need parallel running during transition?
6. What ETL/orchestration tools need conversion?
7. Are there complex stored procedures or UDFs?
8. What validation/reconciliation requirements exist?

### Reference Documents
| Document | Location | Glean Search |
|----------|----------|--------------|
| Migration Assessment Template | `<TBD>` | `<TBD>` |
| SnowConvert Guide | `<TBD>` | `<TBD>` |
| Data Validation Patterns | `<TBD>` | `<TBD>` |

---

## Iceberg / Open Table Formats

### Key Discovery Questions
1. What is the primary driver for Iceberg adoption (open format portability, cross-engine access, cost optimization, vendor flexibility)?
2. Which external engines need to read or write Iceberg tables (Spark, Trino, Databricks, Flink, other)?
3. What catalog(s) are currently in use or planned (AWS Glue, Databricks Unity Catalog, Polaris, other REST catalog)?
4. Where does the data reside today (S3, Azure Blob, GCS)? Single region/cloud or multi-region/multi-cloud?
5. How many tables are candidates for Iceberg format? Are these new tables or conversions from existing managed tables?
6. What are the freshness/latency requirements for externally managed Iceberg tables (batch daily, hourly, near-real-time)?
7. Which engine is the "source of truth" writer for each table? Is bidirectional write access required?
8. Do you need a centralized catalog governance layer (Polaris) for multi-engine access control and credential vending?
9. What is the current IAM/networking posture for cross-account or cross-cloud storage access (trust policies, VPC endpoints, private link)?
10. Are there DR/replication requirements for Iceberg tables? Do you need Iceberg metadata replicated across regions?

### Reference Documents
| Document | Location | Glean Search |
|----------|----------|--------------|
| Iceberg Tables Overview | `<TBD>` | `<TBD>` |
| Catalog Integration Guide | `<TBD>` | `<TBD>` |
| External Volume Configuration | `<TBD>` | `<TBD>` |
| Polaris Catalog Documentation | `<TBD>` | `<TBD>` |

---

*Last Updated: 2026-03-03*
