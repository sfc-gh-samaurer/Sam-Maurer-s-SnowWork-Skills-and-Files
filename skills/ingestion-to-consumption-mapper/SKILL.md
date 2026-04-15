---
name: ingestion-to-consumption-mapper
description: "Create end-to-end data lineage maps from source systems through Bronze, Silver, and Gold layers for Snowflake Medallion Architecture engagements. Generates a multi-sheet Excel workbook with source-to-domain mappings, dot matrices, and phase assignments. Use when: medallion architecture planning, data lineage mapping, Bronze-Silver-Gold design, domain modeling, source-to-consumption traceability, data flow mapping. Triggers: ingestion to consumption, source to gold mapping, medallion architecture, data lineage, bronze silver gold, domain mapping, consumption roadmap, data flow."
---

# Ingestion-to-Consumption Mapper

Generate a comprehensive data lineage Excel workbook mapping source systems through Bronze (raw ingestion), Silver (curated/integrated domains), and Gold (consumption/reporting domains) layers of a Snowflake Medallion Architecture.

## Prerequisites

- `openpyxl` Python library available
- Source system inventory (ideally from `bronze-layer-planner` output or customer discovery)
- Understanding of customer's reporting/analytics needs to define Gold domains

## Workflow

### Step 1: Gather Inputs

**Ask** the user for:
1. **Customer name**
2. **Source system list** — names, categories, ingestion patterns (or reference a Bronze Layer plan)
3. **Silver domain candidates** — curated business domains (e.g., General Ledger, Customer Master, Inventory, Shipping)
4. **Gold domain candidates** — consumption/reporting domains (e.g., Financial Reporting, Customer 360, Operations Dashboard)
5. **Phase assignments** (if known) — which sources/domains belong to which implementation phase
6. **Any existing data model documentation** — ERDs, data dictionaries, reporting requirements

If a Bronze Layer Implementation Excel exists, read it to extract the source list automatically.

**⚠️ STOP**: Confirm source list, Silver domains, and Gold domains before proceeding.

### Step 2: Design the Layer Mappings

**Bronze Layer (Source Data Ingestion):**
For each source, define:
- Source System name
- Category (ERP, CRM, Ecommerce, etc.)
- Ingestion Pattern (Openflow CDC, Snowpipe, API→S3, etc.)
- Bronze Schema name (e.g., `BRONZE_ORACLE_FUSION`, `BRONZE_SALESFORCE`)
- Key objects/tables ingested
- Phase assignment

**Silver Layer (Curated Data):**
For each Silver domain, define:
- Domain name (e.g., "General Ledger", "Customer Master", "Inventory")
- Category grouping (Financial, Supply Chain, Sales, Marketing, etc.)
- Source Bronze schemas that feed this domain
- Key transformations (dedup, normalize, merge, business rules)
- Technology (Dynamic Tables, dbt, Streams & Tasks)
- Phase assignment

**Gold Layer (Consumption):**
For each Gold domain, define:
- Domain name (e.g., "Financial Reporting", "Profitability Dashboard", "Customer 360")
- Category grouping (Executive, Operations, Marketing, etc.)
- Source Silver domains that feed this domain
- Consumption method (Semantic Views, Streamlit, BI tool, API)
- Phase assignment

### Step 3: Build the Dot Matrix

Create source-to-domain mapping matrices:
- **Source → Silver**: rows = sources, columns = Silver domains, cells = ● where source feeds domain
- **Silver → Gold**: rows = Silver domains, columns = Gold domains, cells = ● where Silver feeds Gold
- **Source → Gold** (transitive): rows = sources, columns = Gold domains, derived from the above two

### Step 4: Generate the Excel Workbook

Create a Python script using `openpyxl` that generates these sheets:

**Sheet 1: Information**
- Customer name, date, phase mapping legend, summary statistics
- Discovery items and notes

**Sheet 2: Source Data Ingestion (Bronze)**
- Columns: Source System, Category, Ingestion Pattern, Bronze Schema, Key Objects, Volume, Frequency, Phase, Notes
- Sorted by phase, then category
- Phase cells color-coded (suggest: Phase 1=blue, Phase 2=purple, Phase 3=pink, Parallel=orange)
- Section headers between phases

**Sheet 3: Curated Data (Silver)**
- Columns: Silver Domain, Category, Source Systems, Key Transformations, Technology, Phase, Notes
- Grouped by category

**Sheet 4: Consume (Gold)**
- Columns: Gold Domain, Category, Silver Sources, Consumption Method, Phase, Notes
- Grouped by category

**Sheet 5: Source → Domain Mapping (Dot Matrix)**
- Rows: All source systems
- Columns: All Silver domains + All Gold domains
- Cells: ● where a mapping exists
- Phase color-coding on row headers
- This is the key traceability artifact

**Sheet 6: Gold → Source Mapping**
- Rows: Gold domains
- Columns: Source systems
- Shows which sources feed each Gold domain (transitive through Silver)

**Sheet 7: Curated → Source Mapping**
- Rows: Silver domains
- Columns: Source systems
- Shows which sources feed each Silver domain

**Formatting:**
- Header row: dark blue fill (#11567F), white bold text
- Phase color-coding: configurable per engagement
- Dot matrix cells: centered ● with light fill
- Column auto-width, freeze panes
- Summary counts in Information sheet

**⚠️ STOP**: Present the layer summaries and dot matrix preview before generating Excel.

### Step 5: Generate and Deliver

1. Write the Python generation script
2. Execute to produce the Excel file
3. Report: total sources, Silver domains, Gold domains, phase distribution

**Output location**: `<customer_directory>/<Customer>_Ingestion_to_Consumption.xlsx`

## Stopping Points

- ✋ Step 1: Source/domain lists confirmed
- ✋ Step 4: Layer summaries and mappings reviewed

## Output

Multi-sheet Excel workbook with:
- Bronze, Silver, Gold layer inventories with phase assignments
- Source → Domain dot matrix for full traceability
- Reverse mappings (Gold → Source, Silver → Source)
- Phase color-coding and summary statistics

## Reference: Boxout Health Example

- 47 source systems, 33 Silver sub-domains, 25 Gold consumer domains
- 47×58 dot matrix (sources × all domains)
- 7 sheets with phase assignments across 4 phases
- Phase coloring: blue=Phase 1, purple=Phase 2, pink=Phase 3, orange=Parallel
