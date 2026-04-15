## Iceberg / Open Table Formats

### Focus Areas
- Iceberg table strategy (Snowflake-managed vs externally managed, read/write patterns)
- Catalog integration architecture (REST catalog, AWS Glue, Databricks Unity, Polaris)
- Catalog-linked databases (auto-discover, sync, managed access to external catalogs)
- External volume configuration (S3, Azure Blob, GCS; IAM, trust policies, ALLOW_WRITES)
- Storage integration and cross-cloud access patterns
- Conversion from existing Snowflake managed tables to Iceberg format
- Migration of Iceberg workloads from external engines (Spark, Trino, Databricks) into Snowflake
- Cross-engine interoperability (read/write from Spark, Trino, Databricks, Flink against Snowflake-managed Iceberg)
- Polaris Catalog setup, namespace management, and credential vending
- Auto-refresh configuration and monitoring (metadata sync latency, freshness SLAs)
- Data lifecycle management (table maintenance, compaction, snapshot expiration, orphan file cleanup)

### Key Objects
- Iceberg tables (Snowflake-managed and externally managed)
- Catalog integrations (ICEBERG_REST, GLUE, UNITY_CATALOG, POLARIS)
- Catalog-linked databases (LINKED_CATALOG)
- External volumes (S3, Azure Blob, GCS)
- Storage integrations (IAM roles, trust policies, service principals)
- Polaris Catalog instances, namespaces, and service connections
- Auto-refresh configurations and notification integrations
- External stages (for migration / bulk load paths)
- Table maintenance tasks (compaction, snapshot management)

### Risk Areas
- Storage permission misconfiguration (IAM roles, trust policies, cross-account access)
- Auto-refresh latency exceeding freshness SLAs
- Non-replicated Iceberg metadata in DR scenarios
- Preview/GA feature boundary (some catalog types or capabilities may be in preview)
- Schema evolution conflicts between engines writing to the same tables
- Orphan file accumulation without proper lifecycle management
- Cross-engine write conflicts and transaction isolation limitations
- Catalog metadata sync failures or inconsistencies
- External volume connectivity issues (firewall, VPC endpoints, private link)
- Performance differences between Iceberg and native Snowflake table scans

### Complexity Drivers
- Number and type of catalog integrations
     (Single REST catalog vs multi-catalog spanning Glue + Unity + Polaris.)
- Data volume and table count
     (Dozens of tables vs thousands; GBs vs PBs of data on external storage.)
- Read/write access patterns
     (Snowflake read-only vs bidirectional read/write across multiple engines.)
- Number of external engines requiring interop
     (Snowflake-only consumers vs Spark + Trino + Databricks all reading/writing.)
- Storage topology
     (Single cloud/region vs multi-cloud or cross-region external volumes.)
- Migration complexity
     (Greenfield Iceberg adoption vs converting existing managed tables vs migrating external Iceberg workloads.)
- Polaris Catalog scope
     (Not using Polaris vs Polaris as centralized catalog for multi-engine governance.)
- Security and governance requirements
     (Basic access control vs fine-grained table/namespace-level policies, credential vending, audit.)
- Auto-refresh and freshness requirements
     (Daily batch sync vs near-real-time metadata refresh with strict SLAs.)
- Existing Snowflake maturity
     (New Snowflake customer adopting Iceberg vs mature customer adding Iceberg to existing workloads.)

### Typical Phases

- Phase 0 – Discovery & Assessment
- Phase 1 – Architecture & Catalog Design
- Phase 2 – Foundation Setup (External Volumes, Catalog Integrations)
- Phase 3 – Table Creation, Migration & Interop Configuration
- Phase 4 – Validation, Performance Tuning & Auto-Refresh
- Phase 5 – Handover, Runbooks & KT

#### Phase 0 – Discovery & Assessment
- Activities:
     Inventory existing data assets: tables, storage locations, engines, catalogs already in use.
     Assess current Iceberg adoption (if any): table formats, catalog metadata, engine versions.
     Identify target use cases: which tables need Iceberg, which engines need access, freshness requirements.
     Review cloud storage topology: regions, accounts, IAM/trust policy posture, network connectivity.
     Classify in-scope vs out-of-scope tables, catalogs, and engines.
     Evaluate Polaris Catalog requirements (centralized governance, credential vending, namespace design).
- Ownership:
     Customer: provide environment access, storage account details, IAM documentation, SMEs (data platform, cloud infra, engine teams).
     Snowflake/Partner: lead discovery workshops, analyze current state, document findings and initial recommendations.

#### Phase 1 – Architecture & Catalog Design
- Activities:
     Define Iceberg table strategy: Snowflake-managed vs externally managed per use case.
     Select catalog integration types per data domain (REST, Glue, Unity, Polaris).
     Design external volume topology: mapping storage locations to volumes, region/cloud alignment.
     Design Polaris Catalog namespace hierarchy and access control model (if in scope).
     Define auto-refresh strategy: notification-based vs polling, target latency per table/domain.
     Define cross-engine access patterns and write ownership (which engine is source of truth per table).
     Document architectural decisions, naming conventions, and governance model.
- Ownership:
     Snowflake/Partner (lead): architecture options, best practices, reference patterns, design decisions.
     Customer: validate priorities, approve catalog and storage design, confirm IAM/network constraints.

#### Phase 2 – Foundation Setup (External Volumes, Catalog Integrations)
- Activities:
     Create and configure external volumes with appropriate storage locations and IAM roles.
     Validate storage connectivity: trust policies, cross-account access, VPC endpoints.
     Create catalog integrations (REST, Glue, Unity, Polaris) and validate connectivity.
     Set up Polaris Catalog instance: namespaces, service connections, credential vending (if in scope).
     Create catalog-linked databases where applicable and validate auto-discovery.
     Implement monitoring for catalog sync and external volume health.
     Build first reference Iceberg table end-to-end as a template.
- Ownership:
     Snowflake/Partner (lead): configuration, integration setup, reference implementation, troubleshooting.
     Customer: IAM role creation, trust policy updates, network/firewall changes, cloud infra approvals.

#### Phase 3 – Table Creation, Migration & Interop Configuration
- Activities:
     Create Iceberg tables for prioritized use cases (Snowflake-managed and/or externally managed).
     Convert existing Snowflake managed tables to Iceberg format where applicable.
     Migrate external Iceberg workloads into Snowflake catalog management (if in scope).
     Configure cross-engine read/write access: validate Spark, Trino, Databricks connectivity.
     Implement table maintenance automation (compaction, snapshot expiration, orphan file cleanup).
     Configure auto-refresh and notification integrations for externally managed tables.
- Ownership:
     Snowflake/Partner (lead): table creation patterns, migration scripts, interop validation, automation.
     Customer: provide source data details, business rules for migration, validate engine access from their side.

#### Phase 4 – Validation, Performance Tuning & Auto-Refresh
- Activities:
     Validate data integrity: row counts, checksums, schema alignment across engines.
     Performance test Iceberg table scans vs baseline (native tables or source engine).
     Tune clustering, partition strategies, and file sizing for Iceberg tables.
     Validate auto-refresh latency against freshness SLAs.
     Test DR/replication behavior for Iceberg tables (if in scope).
     Conduct UAT with end users and downstream consumers.
- Ownership:
     Snowflake/Partner (lead): validation framework, performance analysis, tuning recommendations.
     Customer: UAT execution, acceptance sign-off, downstream consumer validation.

#### Phase 5 – Handover, Runbooks & KT
- Activities:
     Create runbooks: catalog integration management, external volume troubleshooting, auto-refresh monitoring, table maintenance.
     Document patterns for adding new Iceberg tables, onboarding new catalogs, and registering new engines.
     Conduct KT sessions for data platform, cloud infra, and engine teams.
     Define ongoing improvement backlog (additional migrations, new catalog types, Polaris expansion).
- Ownership:
     Snowflake/Partner (lead): documentation, runbooks, KT, short hypercare window.
     Customer: assume day-to-day ownership, integrate into internal support and monitoring.

### Effort Baseline

#### Small – Single Catalog, Limited Tables (S)
- Assumptions:
     1 Snowflake account, 1-2 environments (DEV + PROD).
     1 catalog integration type (e.g., Glue or REST).
     1 external volume, single cloud/region.
     5-20 Iceberg tables, primarily Snowflake-managed.
     Read-only cross-engine access (1 external engine) or Snowflake-only consumption.
     No Polaris Catalog. Basic auto-refresh requirements.
- Indicative effort:
     Snowflake/Partner: ~40-80 hours (1-2 weeks)
          Discovery & architecture design: 8-16h
          Foundation setup (external volume, catalog integration): 12-20h
          Table creation & basic interop: 12-24h
          Validation, KT & docs: 8-16h
     Customer: ~24-48 hours
          Cloud infra (IAM, storage, network), SMEs for workshops and testing, operational onboarding.

#### Medium – Multi-Catalog, Migration or Interop (M)
- Assumptions:
     1-3 accounts (DEV/TEST/PROD), standard SDLC.
     2-3 catalog integration types (e.g., Glue + REST + Unity).
     2-4 external volumes, possibly multi-region.
     20-100 Iceberg tables, mix of Snowflake-managed and externally managed.
     Read/write interop with 2-3 external engines.
     Some table conversions from existing managed tables.
     Polaris Catalog possible but limited scope. Moderate auto-refresh SLAs.
- Indicative effort:
     Snowflake/Partner: ~120-240 hours (3-6 weeks)
          Discovery & architecture: 20-40h
          Foundation setup (multiple volumes, catalogs, Polaris): 32-64h
          Table creation, migration & interop: 40-80h
          Validation & performance tuning: 16-32h
          KT & documentation: 12-24h
     Customer: ~80-160 hours
          Cloud infra across environments, engine team coordination, migration validation, UAT, operational onboarding.

#### Large / Complex – Multi-Cloud, Full Polaris, Heavy Interop (L+)
- Assumptions:
     Multi-account org (prod/non-prod, regional), strong governance.
     3+ catalog types, cross-cloud or cross-region storage topology.
     5+ external volumes, complex IAM/network configuration.
     100+ Iceberg tables, significant migration from managed tables or external engines.
     Bidirectional read/write with 3+ external engines, strict write-ownership governance.
     Full Polaris Catalog deployment: multi-namespace, credential vending, centralized governance.
     Strict auto-refresh SLAs (sub-minute to minutes), DR/replication requirements.
- Indicative effort:
     Snowflake/Partner: ~320-640+ hours (8-16+ weeks, often multi-sprint)
          Multi-wave discovery & architecture: 40-80h
          Foundation setup at scale (volumes, catalogs, Polaris, networking): 80-160h
          Table creation, migration & interop across domains: 120-260h
          Validation, performance tuning & auto-refresh: 48-96h
          KT, runbooks & extended hypercare: 32-48h
     Customer: comparable internal effort
          Cloud infra, security, engine platform teams, data engineering, program management across multiple teams.
