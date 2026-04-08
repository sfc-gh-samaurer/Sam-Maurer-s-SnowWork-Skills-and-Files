---
name: bronze-layer-planner
description: "Create Bronze Layer Implementation plans for Snowflake data platform engagements. Inventory source systems, assign Snowflake ingestion patterns, estimate effort, and generate a comprehensive Excel workbook. Use when: planning data ingestion, bronze layer design, source system inventory, ingestion pattern selection, effort estimation for data onboarding. Triggers: bronze layer, source inventory, ingestion plan, data onboarding plan, source system assessment, ingestion patterns, bronze implementation."
---

# Bronze Layer Implementation Planner

Generate a comprehensive Bronze Layer Implementation Excel workbook for a Snowflake data platform engagement. Inventories all source systems, assigns optimal Snowflake ingestion patterns, estimates effort by activity type, and produces a multi-sheet Excel deliverable.

## Prerequisites

- `openpyxl` Python library available
- Customer source system information (from discovery, notes, or existing documentation)

## Workflow

### Step 1: Gather Customer Context

**Ask** the user for:
1. **Customer name** and industry
2. **Source system list** — names, types (ERP, CRM, ecommerce, etc.), and any known details (API availability, volume, format)
3. **Any existing documentation** — scoping notes, architecture diagrams, prior discovery artifacts
4. **Compliance requirements** — HIPAA, PCI, SOX, etc. (affects ingestion pattern choices)
5. **Known constraints** — sunset timelines, legacy systems, API limitations

If the user provides a file (Excel, PDF, notes), read it to extract source system information.

**⚠️ STOP**: Confirm the source list and any missing information before proceeding.

### Step 2: Classify Sources and Assign Ingestion Patterns

For each source system, determine:

**Source Classification:**
- Category: ERP/Core, CRM, Ecommerce, Marketplace, Digital Marketing, Collaboration, Legacy DB, Integration/ETL, BI/Reporting, Telco/Contact Center, TMS/Logistics, Pricing/Sourcing, WMS/WES, Other
- Data format: API (REST/GraphQL/SOAP), JDBC, CDC, File (CSV/JSON/Parquet/EDI), Manual (Excel/PDF)
- Volume estimate: Low (<1 GB), Medium (1-10 GB), High (10+ GB)
- Frequency: Real-time, Near real-time, Batch (daily/hourly), One-time

**Ingestion Pattern Selection** (use this reference):

| Pattern | Best For | Key Components |
|---------|----------|---------------|
| **Openflow CDC** | ERP/CRM with change data capture needs (Oracle, SAP, Salesforce) | Openflow connector → Snowflake tables |
| **Openflow JDBC** | Database extraction (Oracle, SQL Server, PostgreSQL) | Openflow JDBC connector → Snowflake |
| **Snowpipe (S3/Azure/GCS)** | File-based and API-extracted data landing in cloud storage | Cloud Storage → Snowpipe → Raw tables |
| **API → Lambda/Function → S3 → Snowpipe** | REST/GraphQL APIs requiring transformation before loading | API → Serverless function → S3 → Snowpipe |
| **Marketplace / Data Share** | Third-party data providers with Snowflake Marketplace listings | Snowflake Marketplace → Shared database |
| **Direct Share** | Partner/vendor with Snowflake account willing to share | Snowflake Data Sharing → Shared database |
| **Cortex AI (AI_PARSE_DOCUMENT)** | Unstructured documents: PDF, images, scanned contracts | S3 → Cortex AI_PARSE_DOCUMENT → Structured tables |
| **Snowpark Python** | Complex parsing: Excel with formulas, nested JSON, custom formats | Snowpark Python UDF/Procedure → Tables |
| **EDI X12 Parser** | EDI documents (850 PO, 856 Ship Notice, 810 Invoice) | EDI files → Custom parser → Snowpipe → Tables |
| **BCP / Legacy Export** | Legacy/EOL systems (SQL Server 2005, Access, etc.) | BCP/Export → S3 → Snowpipe |
| **Reverse-Engineer SQL + dbt Migration** | Legacy BI tools (Crystal Reports, Access queries) | Extract SQL → dbt models |
| **Native SF Migration** | Replace existing ETL (SSIS, Alteryx, Informatica) with Snowflake-native | Analyze → Replace with dbt/Snowpark/Tasks |

**Effort Estimation** per source (hours by activity):

| Activity | Typical Range | Notes |
|----------|--------------|-------|
| Discovery & Assessment | 4-12 hrs | Schema analysis, API evaluation, volume profiling |
| Connection Setup | 2-8 hrs | Credentials, network, connector config |
| Schema Design (Bronze) | 2-6 hrs | Raw table design, variant vs structured |
| Pipeline Development | 8-24 hrs | Build ingestion pipeline, error handling |
| Data Quality Rules | 4-8 hrs | Row counts, schema validation, freshness checks |
| Testing & Validation | 4-12 hrs | Reconciliation, edge cases, monitoring |
| Documentation | 2-4 hrs | Runbook, pipeline docs |

Adjust based on: API complexity, data volume, number of objects/tables, custom parsing needs, legacy system challenges.

### Step 3: Generate the Excel Workbook

Create a Python script using `openpyxl` that generates an Excel workbook with these sheets:

**Sheet 1: Bronze Implementation Plan** (main detail)
- Columns: Source System, Category, Ingestion Pattern, Objects/Tables, Data Format, Volume, Frequency, Discovery (hrs), Connection (hrs), Schema (hrs), Pipeline (hrs), DQ Rules (hrs), Testing (hrs), Documentation (hrs), Total (hrs), Risk/Notes
- One row per source system
- Sorted by category, then by source name
- Auto-sum for total hours
- Conditional formatting: high-effort sources highlighted

**Sheet 2: Summary by Source**
- Columns: Source System, Category, Ingestion Pattern, Total Hours, Priority, Phase (if known), Risk Level
- Summary view sorted by phase/priority

**Sheet 3: Effort by Activity Type**
- Pivot: Activity type (Discovery, Connection, Schema, Pipeline, DQ, Testing, Docs) × total hours
- Shows effort distribution across activities

**Sheet 4: Ingestion Pattern Reference**
- Pattern name, description, when to use, key components, Snowflake features
- Reference sheet for customer education

**Sheet 5: Discovery Questions** (per source)
- Source-specific discovery questions to validate assumptions
- Covers: API access, credentials, volume, schema, SLAs, dependencies

**Formatting:**
- Header row: dark blue fill (#11567F), white bold text
- Alternating row shading
- Column auto-width
- Freeze panes on header row
- Named ranges for totals

**⚠️ STOP**: Present the source inventory table to the user for review before generating the Excel.

### Step 4: Generate and Deliver

1. Write the Python generation script
2. Execute to produce the Excel file
3. Report: total sources, total estimated hours, ingestion pattern distribution

**Output location**: `<customer_directory>/<Customer>_Bronze_Layer_Implementation.xlsx`

## Stopping Points

- ✋ Step 1: Source list confirmed
- ✋ Step 3: Source inventory reviewed before Excel generation

## Output

Multi-sheet Excel workbook with:
- Detailed Bronze implementation plan with per-source effort estimates
- Summary views by source and activity type
- Ingestion pattern reference guide
- Discovery questions for validation

## Reference: Boxout Health Example

The Boxout Health engagement produced a Bronze Layer plan with:
- 47 source systems across 10 categories
- 337 implementation steps
- ~2,079 total estimated hours
- 10 distinct ingestion patterns used
- File: `Boxout_Health_Bronze_Layer_Implementation.xlsx`
