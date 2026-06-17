"""
Snowflake PS SOW — Attachment Content Library

Provides transferable, reusable default content for each attachment type.
Content is derived from the JD Power v5 SOW (canonical reference) and
generalized to apply across engagements.

Each entry in ATTACHMENT_DEFAULTS contains:
  - title_default:                 Default attachment title suffix
  - scope_intro:                   Opening paragraph for the attachment
  - customer_responsibilities:     List of {category, items[]} dicts
  - exclusions:                    List of string exclusion bullets
  - assumptions:                   List of string assumption bullets
  - raci_default:                  List of {activity, sf, customer} dicts

User-provided JSON overrides (via *_extra or full replacement) always win.
"""

ATTACHMENT_DEFAULTS = {

    # ──────────────────────────────────────────────────────────────────────
    # PLATFORM IMPLEMENTATION
    # ──────────────────────────────────────────────────────────────────────
    "platform_implementation": {
        "title_default": "Platform Implementation",
        "scope_intro": (
            "During the Term, Snowflake will perform the Technical Services "
            "below related to the design, provisioning, and configuration of "
            "Customer's Snowflake platform."
        ),
        "customer_responsibilities": [
            {
                "category": "Before Kickoff",
                "items": [
                    "Designate a Project Sponsor responsible for engagement oversight, timely approvals, and budget-level decisions.",
                    "Assign a dedicated Customer Project Manager responsible for requirements clarification, SME coordination, and day-to-day decision-making.",
                    "Establish a regular status meeting cadence and escalation framework with Snowflake SD prior to the engagement start date.",
                    "Provide pre-defined requirements for RBAC (role hierarchy, service accounts, environment isolation), row access policies, and dynamic data masking ready for implementation at the start of the engagement.",
                    "Confirm target Snowflake account edition, region, and any encryption or compliance requirements (e.g., Business Critical, Private Link, Tri-Secret Secure) prior to engagement start.",
                    "Complete Snowflake University self-paced training before the SOW Effective Date.",
                    "Approve use of AI tools and meeting recordings to support knowledge transfer and documentation.",
                ]
            },
            {
                "category": "Week 1",
                "items": [
                    "Provision Snowflake environments (Dev, QA, Production) with appropriate access for all Snowflake SD resources.",
                    "Provide access to source system documentation including data dictionaries, ERDs, pipeline dependency maps, and any existing inventory outputs.",
                    "Ensure all required network, firewall, and VPN configurations are in place to allow Snowflake SD to connect to source and target environments.",
                    "Grant appropriate access to all accounts and internal systems required for environment and tooling setup.",
                ]
            },
            {
                "category": "Within First 4 Weeks",
                "items": [
                    "Define and confirm functional requirements for CI/CD pipeline (deployment gate criteria, environment promotion process) before migration begins.",
                    "Define and deliver all applicable data residency constraints and regulatory requirements prior to architecture design.",
                    "Provide a complete list of all in-scope objects by a mutually agreed date.",
                ]
            },
            {
                "category": "Throughout Engagement",
                "items": [
                    "Ensure consistent availability of key stakeholders and technical SMEs (platform admins, DBAs, security and compliance leads) throughout the engagement.",
                    "Respond to all issues raised by Snowflake within one (1) business day. Blockers unresolved beyond this window may impact milestone dates and could require a Change Order.",
                    "Ensure all Customer-owned security and compliance obligations are met for data in the Snowflake environment. MFA must be configured and enabled for all accounts Snowflake SD will access.",
                    "Share knowledge documentation and conduct architecture and technical deep dives as needed.",
                ]
            },
            {
                "category": "Post-Migration",
                "items": [
                    "Own legacy platform decommission. Infrastructure cost optimization, data archival, and related activities are Customer responsibility unless explicitly added via Change Order.",
                ]
            },
        ],
        "exclusions": [
            "Delivery of Snowflake platform engineering feature requests is excluded. New features or platform changes identified during the project do not impact the milestone payment schedule.",
            "Provisioning or configuration of technical components outside of the Snowflake platform — including network configurations, virtual machines, integration applications, storage configurations, and identity providers — is out of scope. Snowflake may advise; Customer is responsible for troubleshooting and issue resolution.",
        ],
        "assumptions": [
            "Customer has pre-defined RBAC requirements ready for implementation at the start of the engagement.",
            "All Snowflake environments will be provisioned with appropriate editions and account types prior to engagement start.",
            "AI tools and meeting recordings will be available to Snowflake SD to support knowledge transfer and documentation.",
            "Customer provides dedicated SMEs for architecture reviews, design approvals, and validation gates throughout the engagement.",
            "All work is performed during standard business hours in the Customer's local time zone unless otherwise agreed.",
        ],
        "raci_default": [
            {"activity": "Platform architecture design", "sf": "A/R", "customer": "C"},
            {"activity": "Platform architecture approval", "sf": "C", "customer": "A"},
            {"activity": "Environment provisioning", "sf": "C", "customer": "A/R"},
            {"activity": "RBAC framework design", "sf": "A/R", "customer": "C"},
            {"activity": "RBAC framework implementation", "sf": "C", "customer": "A/R"},
            {"activity": "Security policy design (masking, RAP)", "sf": "A/R", "customer": "C"},
            {"activity": "Security policy implementation", "sf": "C", "customer": "A/R"},
            {"activity": "Network connectivity (PrivateLink, VPN)", "sf": "C", "customer": "A/R"},
            {"activity": "Knowledge transfer sessions", "sf": "A/R", "customer": "C"},
            {"activity": "Milestone sign-off", "sf": "C", "customer": "A"},
        ],
    },

    # ──────────────────────────────────────────────────────────────────────
    # DATA INGESTION
    # ──────────────────────────────────────────────────────────────────────
    "data_ingestion": {
        "title_default": "Data Ingestion",
        "scope_intro": (
            "During the Term, Snowflake will perform the Technical Services "
            "below related to the design and deployment of Snowflake-native "
            "ingestion pipelines."
        ),
        "customer_responsibilities": [
            {
                "category": "Week 1",
                "items": [
                    "Export and deliver all existing connector configurations (host credentials, connection strings, storage paths) as part of Phase 0 discovery.",
                    "Provision read access to all source storage buckets (S3, GCS, Azure Blob) across all applicable cloud accounts.",
                    "Create, configure, and maintain all IAM roles, policies, and cross-account trust relationships required to enable Snowflake ingestion from in-scope source systems.",
                    "Provide an inventory of inbound file formats (CSV, GZIP, ZIP, AVRO, Parquet) including delivery frequency and compression method.",
                ]
            },
            {
                "category": "5 Days After Kickoff",
                "items": [
                    "Provide Snowflake SD with VPN access (or equivalent) and all necessary credentials for all in-scope data sources within 5 business days of kickoff.",
                ]
            },
            {
                "category": "By Week 4",
                "items": [
                    "Provide a complete inventory of all columns containing PII along with required masking and tokenization rules prior to ingestion pipeline design.",
                    "Deliver all applicable data residency constraints, including any regional requirements, for each data source prior to architecture design.",
                    "Provide a complete dependency map of all ingestion scheduling relationships and event trigger dependencies.",
                    "For data sources in non-standard formats (AVRO, ZIP, Excel, fixed-width), define and implement any required preprocessing or format conversion steps prior to Snowpipe ingestion.",
                ]
            },
            {
                "category": "Throughout Engagement",
                "items": [
                    "Build and own all RDBMS-to-staging extraction jobs. All extraction pipeline development (ETL tooling, custom scripts) and ongoing ownership rest entirely with Customer.",
                    "Maintain schema stability. Source tables are not expected to undergo frequent schema changes during migration. Provide advance notice of any schema changes; re-engineering required as a result of unannounced changes may trigger a Change Order.",
                    "Remediate upstream data quality issues. Snowflake SD will surface anomalies identified during validation but will not remediate upstream data quality defects.",
                    "Own cloud infrastructure IAM and cross-account configuration. Snowflake SD will provide required Snowflake external stage and storage integration specifications.",
                    "Ensure data residency compliance. All regulatory determinations rest with Customer legal and compliance teams.",
                ]
            },
            {
                "category": "Per Wave",
                "items": [
                    "Manage third-party vendor relationships. Notify all external vendors of updated delivery endpoints and coordinate switchover timing ahead of each wave cutover.",
                    "Execute go/no-go cutover per wave. Notify downstream consumers, manage rollback readiness, and document all issues identified during the parallel-run window.",
                ]
            },
            {
                "category": "Post-Migration",
                "items": [
                    "Own legacy ingestion platform decommission. Replatforming or decommissioning of existing scheduling infrastructure and legacy connectors is Customer responsibility.",
                ]
            },
        ],
        "exclusions": [
            "Development of RDBMS-to-staging extraction pipelines (ETL tooling, custom scripts) is excluded from Snowflake SD scope.",
            "Third-party vendor engagement to modify delivery contracts, update delivery endpoints, or negotiate firewall exceptions is out of scope for Snowflake SD.",
            "Preprocessing of non-standard file formats to a Snowpipe-compatible format is excluded unless explicitly included via Change Order.",
            "Replatforming or decommissioning of existing legacy scheduling infrastructure is Customer's responsibility.",
            "Remediation of upstream data quality defects is excluded. Snowflake SD will surface anomalies during validation; remediation ownership rests with Customer.",
            "Cloud IAM roles, bucket policies, and cross-account access controls are Customer's responsibility.",
            "PII classification within source systems is Customer's sole responsibility.",
        ],
        "assumptions": [
            "Source connector definitions (host credentials, connection strings, storage mappings) are accessible and will be made available to Snowflake SD as part of Phase 0 discovery.",
            "Source tables are not expected to undergo frequent schema changes during the migration window. Customer will provide advance notice of any schema changes.",
            "Source data will continue to land in existing storage locations (S3, GCS, SFTP) during the migration period.",
            "Data quality anomalies may exist in source systems. Snowflake SD will surface issues during ingestion validation but will not remediate upstream data quality defects.",
            "Data validation will consist of aggregated checks, row counts, schema matching, sample comparisons, null checks, and data loss evaluation at mutually agreed thresholds.",
        ],
        "raci_default": [
            {"activity": "Ingestion architecture design", "sf": "A/R", "customer": "C"},
            {"activity": "RDBMS-to-staging extraction pipelines", "sf": "I", "customer": "A/R"},
            {"activity": "Snowpipe / auto-ingest configuration", "sf": "A/R", "customer": "C"},
            {"activity": "External Access Integration (API sources)", "sf": "A/R", "customer": "C"},
            {"activity": "IAM and cross-account access configuration", "sf": "C", "customer": "A/R"},
            {"activity": "PII classification and masking definition", "sf": "C", "customer": "A/R"},
            {"activity": "Wave cutover go/no-go", "sf": "C", "customer": "A"},
        ],
    },

    # ──────────────────────────────────────────────────────────────────────
    # HISTORICAL DATA MIGRATION (DMVA)
    # ──────────────────────────────────────────────────────────────────────
    "historical_data_migration": {
        "title_default": "Historical Data Migration",
        "scope_intro": (
            "During the Term, Snowflake will perform the Technical Services "
            "below related to a one-time historical data migration from the "
            "Legacy Platform to the Target Platform using the Snowflake Data "
            "Migration and Validation Accelerator (DMVA)."
        ),
        "customer_responsibilities": [
            {
                "category": "Before Kickoff",
                "items": [
                    "Provide a dedicated virtual desktop environment or customer-managed laptop from which to execute all DMVA pipeline tasks. Environment variables required for DMVA must be stored on the same VM.",
                ]
            },
            {
                "category": "5 Days After Kickoff",
                "items": [
                    "Provide Snowflake SD resources with read access to all source systems within 5 business days of kickoff.",
                ]
            },
            {
                "category": "Week 1",
                "items": [
                    "Configure appropriate access permissions for Snowflake SD resources and the Snowflake account to read and write to the staging repository.",
                    "Provide a dedicated read-only service account on all source systems with privileges to read all in-scope tables, schemas, and databases.",
                    "Ensure DMVA network-level connectivity (ODBC/JDBC) is in place between the DMVA VM and all source systems.",
                    "Designate a technical point-of-contact (POC) with working knowledge of source system access, network administration, and data engineering.",
                ]
            },
            {
                "category": "Week 1–2",
                "items": [
                    "Provision a dedicated Snowflake warehouse for DMVA loading operations (Snowflake will provide sizing recommendations).",
                    "Grant the DMVA service account CREATE, DROP, SELECT, INSERT, UPDATE, DELETE privileges on all in-scope objects.",
                ]
            },
            {
                "category": "Weeks 1–6",
                "items": [
                    "Provide accurate and complete data volume estimates for all in-scope datasets prior to migration planning.",
                ]
            },
            {
                "category": "Before Pilot",
                "items": [
                    "Provide representative data in a lower environment for purposes of unit testing and controlled validation.",
                ]
            },
            {
                "category": "During Migration Phases",
                "items": [
                    "Freeze source system schemas for all in-scope objects during migration and validation phases. Communicate all planned schema changes with a minimum of five (5) business days notice.",
                    "Ensure source system stability. Source systems must remain stable (no material schema changes) during migration.",
                    "Provide a suitable static extraction window for tables where data must be static when performing validation.",
                    "Ensure sufficient network bandwidth across all transfer legs of the DMVA pipeline.",
                    "Provide table design information for incremental load processes (primary key definitions, columns identifying recently updated records).",
                    "Run data profiling scripts against source platform and provide results to Snowflake.",
                    "Notify Snowflake of any planned source system maintenance windows or outages no less than five (5) business days in advance.",
                ]
            },
            {
                "category": "Per Phase",
                "items": [
                    "Own validation sign-off. Customer is solely responsible and accountable for sign-off of data validation reports.",
                    "Raise SIT defects within thirty (30) days of code delivery for each given phase. Defects raised after this window may require a Change Order.",
                ]
            },
            {
                "category": "Production Phase",
                "items": [
                    "Own production DMVA execution. Execution of data migration and validation activities in the Customer production Snowflake environment is Customer responsibility. Snowflake will advise but will not perform hands-on setup in Production.",
                ]
            },
            {
                "category": "Post-Completion",
                "items": [
                    "Assume post-delivery ownership of all migrated data and delta catch-up pipeline configurations. DMVA is not a permanent enterprise replication solution.",
                ]
            },
            {
                "category": "Post-Migration",
                "items": [
                    "Own source platform decommission. Decommission of source infrastructure is excluded from Snowflake scope unless added via Change Order.",
                ]
            },
        ],
        "exclusions": [
            "No data transformation — data is migrated as-is from the Legacy Platform.",
            "Physical transfer of any data outside of the agreed DMVA pipeline.",
            "Non-scripted data validation.",
            "Validation of views, functions, procedures, or any objects other than tables.",
            "Migration of data to the Customer Snowflake Production environment (non-production only under this Attachment unless explicitly stated).",
            "Unstructured data, semi-structured data outside the agreed inventory, and new data sources identified after the agreed inventory cut-off date are excluded unless added via Change Order.",
            "Root cause analysis, remediation, and recovery of source system failures or data corruption are outside the scope of this SOW.",
            "Decommission of source infrastructure is excluded from this Attachment.",
            "Row-by-row and cell-by-cell validation are out of scope.",
            "Hands-on setup of DMVA in the Production environment is out of scope. Snowflake will advise Customer for setup in higher environments.",
            "DMVA is not a replication tool. Any SLAs requiring real-time or near-real-time refresh are out of scope.",
        ],
        "assumptions": [
            "Snowflake's recommended test cycles and standard validation tiers (schema, row count, statistical, data compare) within the DMVA validation accelerator are sufficient to meet a migrated object's definition of done.",
            "Customer environment for source data is stable and has adequate resources to support DMVA query loads.",
            "Environment variables required for DMVA are stored on the same VM as DMVA. Use and configuration of any external vault or secrets management solution is out of scope.",
            "Customer will provide a dedicated virtual desktop environment or laptop for DMVA pipeline execution; Snowflake resources will not use personal workstations for data extraction.",
            "Customer provides dedicated subject matter experts (SMEs) for transformation business logic validation throughout the engagement.",
            "Source systems remain stable (no material schema changes) during migration.",
            "DMVA data validation performs aggregate checks and not row-by-row and cell-by-cell validation.",
            "Any new validation requirement that requires new custom development to existing validation tooling will be additional effort and cost, and will not impact the payment schedule.",
        ],
        "raci_default": [
            {"activity": "DMVA setup and configuration", "sf": "A/R", "customer": "C"},
            {"activity": "Data type mapping and DDL generation", "sf": "A/R", "customer": "C"},
            {"activity": "Historical data migration execution (non-prod)", "sf": "A/R", "customer": "C"},
            {"activity": "DMVA validation report review and sign-off", "sf": "R", "customer": "A"},
            {"activity": "Production DMVA execution", "sf": "C", "customer": "A/R"},
            {"activity": "SIT defect logging and remediation", "sf": "C", "customer": "A/R"},
        ],
    },

    # ──────────────────────────────────────────────────────────────────────
    # CODE CONVERSION
    # ──────────────────────────────────────────────────────────────────────
    "code_conversion": {
        "title_default": "Code Conversion",
        "scope_intro": (
            "During the Term, Snowflake will perform the Technical Services "
            "below related to code conversion from the Legacy Platform(s) "
            "listed below. Snowflake SD serves as Architecture Authority over "
            "all conversion deliverables."
        ),
        "customer_responsibilities": [
            {
                "category": "Before Pilot",
                "items": [
                    "Complete all conversion tooling prerequisites and installation requirements.",
                    "Provide a complete inventory of all in-scope code objects. Customer will execute extraction scripts provided by Snowflake to deliver the code base.",
                ]
            },
            {
                "category": "5 Days After Kickoff",
                "items": [
                    "Provide Snowflake SD resources with read access to all source code repositories and environments within 5 business days of kickoff.",
                ]
            },
            {
                "category": "Throughout Engagement",
                "items": [
                    "Remediate missing code objects. Customer is responsible for providing a complete code base. Missing code discovered during conversion may result in extra effort and a Change Order.",
                ]
            },
            {
                "category": "Per Wave",
                "items": [
                    "Execute User Acceptance Testing (UAT) within thirty (30) days of code delivery for each workstream cohort.",
                    "Deploy converted code to higher environments (QA, Production). Code will be converted in lower non-production environments and handed to Customer for promotion.",
                    "Remediate functional gaps. Code Conversion does not cover dynamic SQL, formatting preservation, or performance-related issues; Customer is responsible for remediating remaining functional gaps.",
                    "Execute go/no-go cutover. Customer owns the cutover decision for each workstream cohort. No legacy system shall be decommissioned without Customer written approval.",
                    "Execute rollback procedures during the rollback window per Snowflake-provided runbooks.",
                    "Own downstream repointing. Customer owns all deployment, repointing, and change management activities (BI tools, APIs, downstream consumers).",
                    "Participate in parallel run. Customer must actively monitor and report issues during the parallel run period.",
                    "Perform SIT and data validation. Customer is responsible and accountable for System Integration Testing. SIT defects must be raised within thirty (30) days of code delivery.",
                ]
            },
        ],
        "exclusions": [
            "Dynamic SQL scenarios where referenced code is not available as part of the provided legacy code.",
            "Formatting of objects — the conversion process does not guarantee formatting will be preserved.",
            "Performance-related issues that do not apply to the entirety of the code base.",
            "Functional features with no Snowflake Service equivalent or automatable workaround.",
            "Orchestration and/or execution of converted objects and scripts.",
            "End-to-end ETL testing.",
            "Customer-owned deployment and repointing activities.",
            "UAT testing and production deployment.",
            "Any objects added to the source environment after the agreed inventory cut-off date are excluded unless a Change Order is executed.",
        ],
        "assumptions": [
            "Conversion tooling (e.g., SnowConvert, Snowpark Connect) is licensed and configured prior to pilot commencement.",
            "Code will be converted in lower non-production environments and handed to Customer to deploy in higher environments for SIT and UAT.",
            "Customer will provide a list of all in-scope objects by a mutually agreed date. One (1) incremental code sync is assumed after inventory is finalized.",
            "Customer will execute all UAT for each workstream cohort within thirty (30) days of delivery.",
            "Change Orders are required for scope additions beyond the agreed inventory.",
        ],
        "raci_default": [
            {"activity": "Conversion tooling configuration", "sf": "A/R", "customer": "C"},
            {"activity": "Code inventory extraction", "sf": "C", "customer": "A/R"},
            {"activity": "Automated code conversion", "sf": "A/R", "customer": "I"},
            {"activity": "Quality gate reviews and wave sign-off", "sf": "R", "customer": "A"},
            {"activity": "UAT and SIT execution", "sf": "C", "customer": "A/R"},
            {"activity": "Production deployment and repointing", "sf": "C", "customer": "A/R"},
            {"activity": "Parallel run coordination", "sf": "A", "customer": "R"},
            {"activity": "Knowledge transfer to Customer team", "sf": "A/R", "customer": "C"},
        ],
    },

    # ──────────────────────────────────────────────────────────────────────
    # SPCS / CONTAINER MIGRATION
    # ──────────────────────────────────────────────────────────────────────
    "spcs_container_migration": {
        "title_default": "Snowpark Container Services (SPCS) Migration",
        "scope_intro": (
            "During the Term, Snowflake will perform the Technical Services "
            "below related to the migration of containerized workloads from "
            "their current execution environment to Snowpark Container Services "
            "(SPCS), including configuration of EXECUTE JOB SERVICE, "
            "External Access Integrations, and validation of all migrated workloads."
        ),
        "customer_responsibilities": [
            {
                "category": "Before Kickoff",
                "items": [
                    "Deliver all Docker images, Dockerfiles, and container dependency manifests (e.g., package version manifests, requirements files) at or before engagement kickoff.",
                    "The named owner of Docker/container artifacts is responsible for artifact delivery and availability throughout the migration.",
                    "Confirm target Snowflake Business Critical account with Private Link enabled is provisioned prior to engagement start.",
                ]
            },
            {
                "category": "Week 1",
                "items": [
                    "Provide all cloud and external system credentials (e.g., database connection strings, API keys) required for External Access Integration (EAI) configuration.",
                    "Confirm all container dependencies use publicly available, standard libraries. Proprietary or licensed packages must be identified before kickoff.",
                ]
            },
            {
                "category": "Throughout Engagement",
                "items": [
                    "Maintain target external system (e.g., Aurora, RDS) availability for integration testing and dual-write validation. Downstream schema, tables, and read patterns must remain unchanged during the engagement.",
                    "Own compliance review and approval of all PHI/PCI-related configurations. Snowflake SD will produce relevant data flow documentation; compliance review and approval is Customer responsibility.",
                    "Ensure MFA and Private Link VPC peering are configured and active. Snowflake SD configures only the Snowflake-side network policy.",
                ]
            },
            {
                "category": "Post-Migration",
                "items": [
                    "Assume operational ownership of all SPCS-based workloads after knowledge transfer completion.",
                    "Own legacy execution environment decommission (e.g., AWS Elastic Beanstalk, ECS, EC2 shutdown) unless explicitly added via Change Order.",
                ]
            },
        ],
        "exclusions": [
            "Application code refactoring, schema changes, or business logic modifications. Migration is lift-and-shift only.",
            "Custom or proprietary package development for any runtime dependencies not available from standard public registries.",
            "Additional containers or jobs beyond those explicitly listed in the engagement scope.",
            "Web application or front-end layer changes. Downstream consuming applications continue to run unchanged.",
            "PHI/PCI/HIPAA compliance review and approval (Customer responsibility).",
            "Infrastructure-level networking outside of Snowflake (Private Link VPC peering, firewall configuration) is Customer responsibility.",
            "Modifications to downstream external system schemas, tables, or application read patterns.",
        ],
        "assumptions": [
            "All containers use standard, publicly available base images and dependencies. No proprietary or licensed libraries are assumed.",
            "Migration is lift-and-shift only; no application logic changes are in scope.",
            "Dual-write (if applicable) does not alter downstream external system schemas, tables, or consuming application read patterns.",
            "Customer provides all cloud and external system credentials required for External Access Integration configuration.",
            "Container resource profile (CPU, memory, runtime) is documented by the customer prior to SPCS compute pool sizing.",
            "All work is performed in a Snowflake Business Critical environment with Private Link enabled.",
        ],
        "raci_default": [
            {"activity": "Docker image analysis and SPCS compatibility assessment", "sf": "A/R", "customer": "C"},
            {"activity": "Docker artifacts delivery (images, Dockerfiles, manifests)", "sf": "I", "customer": "A/R"},
            {"activity": "SPCS compute pool configuration and EXECUTE JOB SERVICE setup", "sf": "A/R", "customer": "C"},
            {"activity": "External Access Integration (EAI) configuration", "sf": "A/R", "customer": "C"},
            {"activity": "Cloud credentials and EAI secrets provisioning", "sf": "I", "customer": "A/R"},
            {"activity": "Dual-write implementation and validation", "sf": "A/R", "customer": "C"},
            {"activity": "HIPAA/PHI data flow documentation", "sf": "R", "customer": "A"},
            {"activity": "Compliance review and approval", "sf": "I", "customer": "A/R"},
            {"activity": "Monitoring and scheduling configuration", "sf": "A/R", "customer": "C"},
            {"activity": "Knowledge transfer sessions", "sf": "A/R", "customer": "C"},
            {"activity": "Milestone sign-off", "sf": "C", "customer": "A"},
        ],
    },

    # ──────────────────────────────────────────────────────────────────────
    # ANALYTICS ENABLEMENT
    # Cortex AI/ML, Streamlit apps, semantic layers, dashboards, BI.
    # ──────────────────────────────────────────────────────────────────────
    "analytics_enablement": {
        "title_default": "Analytics Enablement",
        "scope_intro": (
            "During the Term, Snowflake will perform the Technical Services "
            "below related to the design and delivery of analytics solutions "
            "on the Snowflake platform, including dashboards, semantic layers, "
            "Cortex AI/ML features, and self-service enablement."
        ),
        "customer_responsibilities": [
            {
                "category": "Before Kickoff",
                "items": [
                    "Define and document the key business questions and KPIs the analytics solution must answer prior to kickoff.",
                    "Identify and confirm access to all data sources required for analytics use cases.",
                    "Designate business-side data owners and subject matter experts (SMEs) who will validate data definitions and business logic.",
                    "Confirm that the underlying Snowflake data platform (schemas, tables, refresh schedules) is stable and production-ready before analytics development begins.",
                ]
            },
            {
                "category": "Throughout Engagement",
                "items": [
                    "Provide timely feedback (within two (2) business days) on dashboard mockups, semantic layer drafts, and demo sessions.",
                    "Assign at least one dedicated business SME for each analytics use case to validate business logic and approve definitions.",
                    "Own all decisions related to data governance, access controls, and which metrics are appropriate for business-wide distribution.",
                    "Provide sample or representative data in a non-production environment for development and testing purposes.",
                ]
            },
            {
                "category": "Post-Delivery",
                "items": [
                    "Own ongoing dashboard maintenance, report scheduling, and self-service enablement after knowledge transfer.",
                    "Manage user access and row-level security configurations after delivery.",
                ]
            },
        ],
        "exclusions": [
            "Production deployment to external-facing portals or customer-facing applications is excluded unless explicitly scoped.",
            "BI tool licensing (Tableau, Power BI, Looker, etc.) is Customer responsibility. Snowflake SD does not procure or administer third-party BI licenses.",
            "Custom machine learning model training beyond Snowflake Cortex ML Functions is excluded unless separately scoped.",
            "Data quality remediation in source systems is excluded. Snowflake SD will surface data quality issues identified during development.",
            "Ongoing dashboard maintenance and report scheduling after knowledge transfer are Customer responsibility.",
        ],
        "assumptions": [
            "All required data is accessible in the Snowflake environment (bronze/silver/gold layers) at the start of this Attachment.",
            "Customer provides defined KPIs and business metric definitions before development begins. Undefined metrics discovered during development require scope re-evaluation.",
            "Customer designates business SMEs who are available for bi-weekly reviews during development.",
            "Dashboards and semantic layers are built in non-production environments and handed to Customer for production promotion.",
            "Customer manages all third-party BI tool configurations; Snowflake SD supports Snowflake-native interfaces only.",
        ],
        "raci_default": [
            {"activity": "KPI and metric definition", "sf": "C", "customer": "A/R"},
            {"activity": "Semantic layer / data model design", "sf": "A/R", "customer": "C"},
            {"activity": "Dashboard and Streamlit app development", "sf": "A/R", "customer": "C"},
            {"activity": "Business logic validation and sign-off", "sf": "C", "customer": "A/R"},
            {"activity": "User access and row-level security", "sf": "C", "customer": "A/R"},
            {"activity": "Production promotion and deployment", "sf": "C", "customer": "A/R"},
            {"activity": "Knowledge transfer sessions", "sf": "A/R", "customer": "C"},
        ],
    },

    # ──────────────────────────────────────────────────────────────────────
    # ADVISORY & ASSESSMENT
    # Architecture assessments, FinOps, WAF reviews, migration scoping.
    # ──────────────────────────────────────────────────────────────────────
    "advisory_assessment": {
        "title_default": "Advisory & Assessment",
        "scope_intro": (
            "During the Term, Snowflake will perform the Technical Services "
            "below related to a structured assessment and advisory engagement. "
            "Snowflake SD will evaluate the current state environment, conduct "
            "stakeholder interviews, and deliver a written recommendations report "
            "with actionable next steps."
        ),
        "customer_responsibilities": [
            {
                "category": "Before Kickoff",
                "items": [
                    "Designate a Customer technical lead who will coordinate access to source systems, documentation, and key stakeholders for the duration of the assessment.",
                    "Provide read-only or view-only access to current state infrastructure documentation, data catalogs, cost dashboards, and pipeline inventories prior to kickoff.",
                    "Identify the key stakeholders (data engineering, architecture, finance, security) who will participate in discovery interviews.",
                ]
            },
            {
                "category": "Throughout Assessment",
                "items": [
                    "Make key stakeholders available for scheduled discovery interviews. Each interview session is estimated at 60–90 minutes.",
                    "Provide written responses to pre-assessment questionnaires within five (5) business days of delivery.",
                    "Provide access to cost and usage data (e.g., cloud billing dashboards, Snowflake credit consumption reports) required for assessment analysis.",
                    "Review interim findings drafts within three (3) business days of delivery and provide written feedback.",
                ]
            },
            {
                "category": "Post-Delivery",
                "items": [
                    "Own all implementation decisions. The assessment delivers recommendations; implementation of those recommendations is Customer's decision and may require a separate engagement.",
                    "Validate that the final recommendations report is complete and accurate before sharing externally.",
                ]
            },
        ],
        "exclusions": [
            "Implementation of any recommendations is excluded from this Attachment. Implementing recommendations requires a separate Statement of Work.",
            "Proof-of-concept development is excluded unless explicitly listed as an in-scope deliverable in the Scope table.",
            "Hands-on configuration of Customer infrastructure, cloud services, or third-party tools is excluded.",
            "Assessment findings are based on information provided by Customer. Snowflake SD is not responsible for inaccuracies stemming from incomplete or incorrect information.",
            "Legal, compliance, or regulatory review of recommendations is Customer responsibility.",
        ],
        "assumptions": [
            "Customer will provide access to all documentation, cost data, and stakeholders required for the assessment within the timelines specified.",
            "Assessment findings and recommendations are based on current state information available at the time of the engagement. Future state changes not in scope may alter the recommendations.",
            "The assessment deliverable is an internal Snowflake SD document. External sharing requires Customer approval and is Customer's responsibility.",
            "Discovery interview scheduling is coordinated by the Customer technical lead.",
        ],
        "raci_default": [
            {"activity": "Current state documentation review", "sf": "A/R", "customer": "C"},
            {"activity": "Discovery interview facilitation", "sf": "A/R", "customer": "C"},
            {"activity": "Data and cost analysis", "sf": "A/R", "customer": "C"},
            {"activity": "Interim findings review and validation", "sf": "R", "customer": "A"},
            {"activity": "Final recommendations report", "sf": "A/R", "customer": "C"},
            {"activity": "Report sign-off and distribution", "sf": "C", "customer": "A"},
            {"activity": "Implementation of recommendations", "sf": "C", "customer": "A/R"},
        ],
    },

    # ──────────────────────────────────────────────────────────────────────
    # DATA GOVERNANCE
    # Masking policies, row access policies, data products, object tagging.
    # ──────────────────────────────────────────────────────────────────────
    "data_governance": {
        "title_default": "Data Governance",
        "scope_intro": (
            "During the Term, Snowflake will perform the Technical Services "
            "below related to the design and implementation of data governance "
            "policies, access controls, and data quality frameworks on the "
            "Snowflake platform."
        ),
        "customer_responsibilities": [
            {
                "category": "Before Kickoff",
                "items": [
                    "Provide a complete data classification inventory — identify all tables and columns containing PII, PHI, PCI, or other sensitive data categories prior to governance design.",
                    "Define business requirements for row-level access, dynamic data masking, and any regulatory constraints (GDPR, CCPA, HIPAA) that must be enforced.",
                    "Designate a Data Steward or Data Owner who has authority to approve governance policy decisions on behalf of the business.",
                    "Confirm the RBAC framework and role hierarchy are defined and provisioned prior to governance policy implementation.",
                ]
            },
            {
                "category": "Throughout Engagement",
                "items": [
                    "Review and approve all governance policy designs within three (3) business days of submission.",
                    "Provide representative test data in a non-production environment for policy testing and validation.",
                    "Ensure business stakeholders (legal, compliance, security) are available to review policy designs that have regulatory implications.",
                ]
            },
            {
                "category": "Post-Delivery",
                "items": [
                    "Own ongoing governance policy maintenance, data classification updates, and policy lifecycle management after delivery.",
                    "Own compliance review and sign-off for all governance policies related to regulated data.",
                ]
            },
        ],
        "exclusions": [
            "Data classification and PII identification within source systems outside of Snowflake is Customer responsibility.",
            "Legal or regulatory compliance review and approval is Customer responsibility. Snowflake SD implements policies per Customer-defined requirements.",
            "Third-party data catalog configuration (Alation, Collibra, Atlan, etc.) is excluded. Snowflake SD focuses on Snowflake-native governance features.",
            "Governance policy maintenance after delivery is Customer responsibility.",
            "Encryption key management (Tri-Secret Secure, Bring Your Own Key) is excluded unless separately scoped.",
        ],
        "assumptions": [
            "Customer has defined data classification requirements (PII, PHI, sensitive categories) before governance implementation begins.",
            "RBAC framework and role hierarchy are provisioned and stable. Governance policies are implemented on top of the existing RBAC design.",
            "Customer designates a Data Owner / Data Steward with policy approval authority for the duration of the engagement.",
            "Non-production test environment is available with representative data for policy validation.",
        ],
        "raci_default": [
            {"activity": "Data classification inventory and PII identification", "sf": "C", "customer": "A/R"},
            {"activity": "Governance policy design (masking, RAP, tagging)", "sf": "A/R", "customer": "C"},
            {"activity": "Governance policy implementation", "sf": "A/R", "customer": "C"},
            {"activity": "Policy testing and validation", "sf": "A/R", "customer": "C"},
            {"activity": "Policy approval (regulatory/compliance)", "sf": "I", "customer": "A/R"},
            {"activity": "Knowledge transfer and documentation", "sf": "A/R", "customer": "C"},
            {"activity": "Ongoing policy maintenance", "sf": "I", "customer": "A/R"},
        ],
    },

    # ──────────────────────────────────────────────────────────────────────
    # TRAINING & ENABLEMENT
    # Workshop delivery, knowledge transfer programs, Snowflake University.
    # ──────────────────────────────────────────────────────────────────────
    "training_enablement": {
        "title_default": "Training & Enablement",
        "scope_intro": (
            "During the Term, Snowflake will perform the Technical Services "
            "below related to structured training, knowledge transfer, and "
            "enablement of Customer's technical and business teams on the "
            "Snowflake platform."
        ),
        "customer_responsibilities": [
            {
                "category": "Before Kickoff",
                "items": [
                    "Identify and confirm the attendee list for each training session, including roles, technical skill levels, and business context.",
                    "Provide use cases, datasets, and business scenarios that will be used to customize hands-on exercises.",
                    "Provision Snowflake training environments (accounts, roles, sample data) for all workshop attendees prior to each session.",
                    "Confirm training schedule and attendee availability at least two (2) weeks prior to each session.",
                ]
            },
            {
                "category": "Throughout Engagement",
                "items": [
                    "Ensure attendees complete any pre-requisite Snowflake University modules before scheduled instructor-led sessions.",
                    "Maintain consistent attendance. Rescheduling requires at least five (5) business days notice; no-shows may result in a Change Order for additional sessions.",
                    "Provide feedback after each training session to allow Snowflake SD to adjust curriculum for subsequent sessions.",
                ]
            },
            {
                "category": "Post-Delivery",
                "items": [
                    "Own ongoing learning programs, additional Snowflake University course assignments, and certification tracking.",
                    "Customer retains all training materials for internal use only. Redistribution or commercial use of Snowflake-provided content requires written approval.",
                ]
            },
        ],
        "exclusions": [
            "Snowflake University certification exam fees are excluded. Certification is Customer's responsibility.",
            "Training sessions beyond the agreed number require a Change Order.",
            "Ongoing coaching or ad hoc support after delivery is excluded unless a hypercare or support engagement is separately scoped.",
            "Custom application or third-party tool training is excluded. Sessions cover Snowflake-native features only.",
        ],
        "assumptions": [
            "All attendees have completed Snowflake University fundamentals tracks prior to instructor-led sessions, or the curriculum is adjusted accordingly.",
            "Customer provides a suitable training environment with appropriate data for hands-on exercises.",
            "Sessions are conducted remotely via video conference unless on-site delivery is explicitly agreed in advance.",
            "Training materials and session recordings are for Customer's internal use only.",
        ],
        "raci_default": [
            {"activity": "Training curriculum design and customization", "sf": "A/R", "customer": "C"},
            {"activity": "Training environment provisioning", "sf": "C", "customer": "A/R"},
            {"activity": "Workshop delivery", "sf": "A/R", "customer": "C"},
            {"activity": "Hands-on exercise facilitation", "sf": "A/R", "customer": "C"},
            {"activity": "Attendee scheduling and coordination", "sf": "I", "customer": "A/R"},
            {"activity": "Post-session feedback collection", "sf": "A/R", "customer": "C"},
            {"activity": "Ongoing learning program management", "sf": "I", "customer": "A/R"},
        ],
    },

    # ──────────────────────────────────────────────────────────────────────
    # AI / ML FACTORY
    # Feature stores, model registry, ML pipelines, Cortex ML Functions.
    # ──────────────────────────────────────────────────────────────────────
    "ai_ml_factory": {
        "title_default": "AI / ML Factory",
        "scope_intro": (
            "During the Term, Snowflake will perform the Technical Services "
            "below related to the design and delivery of AI/ML pipelines, "
            "feature engineering, model training workflows, and model registry "
            "deployment on the Snowflake platform using Snowpark ML, "
            "Cortex ML Functions, and Snowflake Model Registry."
        ),
        "customer_responsibilities": [
            {
                "category": "Before Kickoff",
                "items": [
                    "Define and document business problem statements, target outcomes, and success criteria (KPIs) for each ML use case prior to kickoff.",
                    "Identify and confirm access to training datasets. All data must be accessible in the Snowflake environment before feature engineering begins.",
                    "Assign a Customer data scientist or ML engineer as the primary technical liaison for each ML use case.",
                    "Confirm the Snowflake platform environment is provisioned with appropriate editions and compute pools (Snowpark-Optimized Warehouses or SPCS GPU pools) for ML workloads.",
                ]
            },
            {
                "category": "Throughout Engagement",
                "items": [
                    "Provide domain expertise to validate feature definitions, model performance thresholds, and business logic in feature engineering pipelines.",
                    "Review model performance reports and provide approval at each milestone gate before proceeding to production.",
                    "Own the production deployment decision. Snowflake SD hands off model artifacts and deployment runbooks; Customer owns the go/no-go for production.",
                    "Provide access to historical data for model training and ground-truth labels for supervised learning use cases.",
                ]
            },
            {
                "category": "Post-Delivery",
                "items": [
                    "Own model retraining schedules, performance monitoring, and drift detection after delivery.",
                    "Own production ML operations including model serving, monitoring, and incident response.",
                ]
            },
        ],
        "exclusions": [
            "Model retraining after delivery is excluded. Automated retraining pipelines are in scope only if explicitly listed in the Scope table.",
            "Production ML operations and ongoing model monitoring are Customer responsibility after knowledge transfer.",
            "Custom GPU cluster provisioning outside Snowpark Container Services is excluded.",
            "Data labeling, annotation, or ground-truth generation is Customer responsibility.",
            "External ML platform integration (SageMaker, Azure ML, Databricks) is excluded unless explicitly scoped.",
            "Custom deep learning or large language model fine-tuning is excluded unless separately scoped with appropriate compute resources.",
        ],
        "assumptions": [
            "All training data is accessible in the Snowflake environment before feature engineering begins.",
            "Customer provides domain expertise and ground-truth labels for supervised learning models.",
            "Model performance thresholds and success criteria are defined by Customer before development begins. Threshold changes during development may require a Change Order.",
            "Snowflake Snowpark-Optimized Warehouses or SPCS compute pools are available for model training workloads.",
            "The engagement covers non-production development environments. Production deployment is Customer-owned.",
        ],
        "raci_default": [
            {"activity": "ML use case definition and success criteria", "sf": "C", "customer": "A/R"},
            {"activity": "Feature engineering and feature store design", "sf": "A/R", "customer": "C"},
            {"activity": "Model training pipeline development", "sf": "A/R", "customer": "C"},
            {"activity": "Model performance evaluation and reporting", "sf": "A/R", "customer": "C"},
            {"activity": "Model performance approval and milestone sign-off", "sf": "C", "customer": "A"},
            {"activity": "Model registry and deployment runbooks", "sf": "A/R", "customer": "C"},
            {"activity": "Production deployment decision", "sf": "I", "customer": "A/R"},
            {"activity": "Post-delivery model retraining and monitoring", "sf": "I", "customer": "A/R"},
        ],
    },

    # ──────────────────────────────────────────────────────────────────────
    # PROGRAM MANAGEMENT & CROSS-WORKSTREAM GOVERNANCE
    # Recommended as Attachment 1 for any SOW with 2+ work streams.
    # ──────────────────────────────────────────────────────────────────────
    "program_management": {
        "title_default": "Program Management & Cross-Workstream Governance",
        "scope_intro": (
            "During the Term, Snowflake will provide a dedicated Services Delivery Manager (SDM) "
            "embedded across all work streams. The SDM is responsible for program governance, "
            "milestone coordination, risk and issue management, escalation handling, and "
            "stakeholder communication throughout the engagement."
        ),
        "customer_responsibilities": [
            {
                "category": "Before Kickoff",
                "items": [
                    "Designate a Customer Project Sponsor with engagement-level budget authority and escalation authority. The Project Sponsor is the final decision-making authority for Customer on all engagement matters.",
                    "Assign a dedicated Customer Project Manager responsible for day-to-day coordination, SME availability, decision-making, and RAID log management throughout the engagement.",
                    "Establish weekly status meeting cadence and escalation path with Snowflake SD prior to the engagement start date.",
                    "Confirm all named Snowflake and Customer stakeholders and their availability commitments at kickoff.",
                ]
            },
            {
                "category": "Throughout Engagement",
                "items": [
                    "Customer Project Manager available for weekly status calls, milestone gate reviews, and ad-hoc escalation discussions throughout the engagement.",
                    "Respond to all issues and blockers raised by Snowflake within one (1) business day. Blockers unresolved beyond this window may impact milestone target dates.",
                    "Facilitate access to technical SMEs and business stakeholders required for each work stream on a timely basis.",
                    "Own all internal change management, stakeholder communications, and downstream repointing activities. Snowflake SD does not own Customer-side organizational change management.",
                    "Maintain a Customer-side RAID log. Snowflake SD will maintain the joint risk register; Customer owns resolution of Customer-side risks and issues.",
                ]
            },
        ],
        "exclusions": [
            "Program management does not replace Customer's own project management responsibilities. Customer remains accountable for internal coordination, UAT planning, and production go/no-go decisions.",
            "Snowflake SD program management scope is limited to coordination and governance of Snowflake-delivered work streams. Customer-owned work streams (deployment, repointing, change management) are not managed by Snowflake SD.",
        ],
        "assumptions": [
            "Customer assigns a dedicated Project Manager with decision-making authority for the full duration of the engagement.",
            "Weekly status meetings will be attended by named stakeholders from both Snowflake SD and Customer for the duration of the engagement.",
            "Escalation decisions can be made by the Customer Project Sponsor within two (2) business days of escalation.",
            "All work is performed remotely during standard business hours unless on-site sessions are mutually agreed in advance.",
        ],
        "raci_default": [
            {"activity": "Program kickoff and planning", "sf": "A/R", "customer": "C"},
            {"activity": "Weekly status reporting and risk log", "sf": "A/R", "customer": "C"},
            {"activity": "Milestone gate coordination and scheduling", "sf": "A/R", "customer": "C"},
            {"activity": "Change Request evaluation", "sf": "R", "customer": "A"},
            {"activity": "Customer internal change management", "sf": "I", "customer": "A/R"},
            {"activity": "Escalation decisions", "sf": "C", "customer": "A"},
            {"activity": "Wave sequencing and dependency management", "sf": "A/R", "customer": "C"},
        ],
    },

    # ──────────────────────────────────────────────────────────────────────
    # GENERIC / CUSTOM
    # ──────────────────────────────────────────────────────────────────────
    "generic": {
        "title_default": "Technical Services",
        "scope_intro": (
            "During the Term, Snowflake will perform the Technical Services "
            "described below."
        ),
        "customer_responsibilities": [
            {
                "category": "Before Kickoff",
                "items": [
                    "Designate a Project Sponsor and Customer Project Manager for the duration of the engagement.",
                    "Provision target environments and grant Snowflake SD appropriate access prior to engagement start.",
                ]
            },
            {
                "category": "Throughout Engagement",
                "items": [
                    "Ensure consistent availability of key stakeholders and technical SMEs throughout the engagement.",
                    "Respond to all issues raised by Snowflake within one (1) business day.",
                    "Ensure MFA is configured and enabled for all accounts Snowflake SD will access.",
                ]
            },
        ],
        "exclusions": [
            "Any activities not explicitly described in the scope of this Attachment.",
        ],
        "assumptions": [
            "All required environments and access will be provisioned by Customer prior to engagement start.",
            "Customer provides dedicated SMEs for reviews, approvals, and validation gates.",
        ],
        "raci_default": [
            {"activity": "Technical services delivery", "sf": "A/R", "customer": "C"},
            {"activity": "Milestone sign-off", "sf": "C", "customer": "A"},
        ],
    },
}


def get_attachment_defaults(att_type: str) -> dict:
    """Return the defaults dict for the given attachment type, falling back to generic."""
    return ATTACHMENT_DEFAULTS.get(att_type, ATTACHMENT_DEFAULTS["generic"])


def merge_customer_responsibilities(defaults: list, extras: list) -> list:
    """
    Merge default customer responsibility categories with user-provided extras.
    extras is a list of {category, items[]} — items are APPENDED to matching
    categories, or a new category is created if no match.
    """
    result = [{"category": c["category"], "items": list(c["items"])} for c in defaults]
    for extra_cat in extras:
        cat_name = extra_cat.get("category", "")
        matched = next((c for c in result if c["category"] == cat_name), None)
        if matched:
            matched["items"].extend(extra_cat.get("items", []))
        else:
            result.append({"category": cat_name, "items": list(extra_cat.get("items", []))})
    return result


def merge_list(defaults: list, extras: list) -> list:
    """Append extra items to the defaults list."""
    return list(defaults) + list(extras)
