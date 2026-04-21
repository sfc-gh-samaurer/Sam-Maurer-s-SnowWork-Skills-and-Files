---
name: semantic-extraction
description: "Extract semantic definitions from Tableau, Looker, Power BI, Denodo, and/or SAP Business Objects and convert them to Snowflake Semantic View YAML, HTML reports, and Excel workbooks. Use when: migrating from Tableau/Looker/Power BI/Denodo/Business Objects to Snowflake semantic layer, auditing BI semantic inventory, extracting dashboard metadata, generating semantic view YAML from BI tools. Triggers: tableau extraction, looker extraction, power bi extraction, powerbi, pbix, DAX, semantic extraction, BI migration, LookML to semantic view, tableau to snowflake, power bi to snowflake, denodo extraction, denodo to snowflake, VQL, business objects extraction, SAP BO, universe extraction, .unv, .unx, semantic audit, dashboard inventory, BI semantic mapping, seed data, sample data, synthetic data, si agent, snowflake intelligence agent, cortex agent from BI, generate agent, SI artifacts."
---

# Semantic Extraction

Extract semantic definitions from **Tableau**, **Looker**, **Power BI**, **Denodo**, and/or **SAP Business Objects**, audit the full BI landscape, and produce Snowflake Semantic View YAML + a mapping file (Excel + JSON).

## When to Use

- Migrating from Tableau/Looker/Power BI/Denodo/Business Objects to Snowflake's semantic layer
- Auditing all dashboards, metrics, and calculated fields across a BI estate
- Generating the mapping/documentation artifact for a migration engagement
- Extracting from Looker/LookML (Snowflake Autopilot does not support Looker)
- Extracting from Power BI / DAX models (Autopilot does not support Power BI)
- Extracting from Denodo data virtualization layers (Autopilot does not support Denodo)
- Extracting from SAP Business Objects universes (Autopilot does not support BO)
- Large-scale Tableau extraction (Autopilot is manual, one workbook at a time)

## Relationship to Snowflake Semantic View Autopilot

Snowflake's **Semantic View Autopilot** can ingest Tableau `.twb`/`.tds`/`.twbx` files directly in Snowsight UI — but it is manual (one workbook at a time), does not support Looker, Power BI, Denodo, or Business Objects, and does not produce a mapping/audit artifact.

This skill complements Autopilot:
- **Audit ALL sources first** → produce the mapping file → **qualify** what to migrate
- **Looker**: Generate YAML directly (no Autopilot path)
- **Power BI**: Generate YAML directly (no Autopilot path)
- **Denodo**: Generate YAML directly (no Autopilot path) — infers dim/measure from heuristics since Denodo has no native classification
- **Business Objects**: Generate YAML directly (no Autopilot path) — leverages BO's native Dimension/Detail/Measure object types
- **Tableau**: After qualification, use Autopilot for individual `.twb` files or generate YAML here
- **Multi-tool**: Unified extraction + documentation across all five BI tools

## Prerequisites

- Python 3.11+ with dependencies from `requirements.txt` (install via `pip install -r requirements.txt` in the skill directory)
- Core deps: `lkml`, `requests`, `pyyaml`, `openpyxl`
- Optional deps: `pbixray` (for .pbix), `jaydebeapi` + JVM (for Denodo JDBC)
- For Tableau files: `.twb`, `.tds`, or `.twbx` files on disk
- For Looker files: Full LookML project directory (model + view + manifest files)
- For Power BI files: `.pbix` files on disk, or `.bim` / `database.json` model files, or `.pbip` project folder
- For Denodo files: VQL export (`DESC VQL DATABASE`) text files, or JDBC connection to VDP server
- For Business Objects files: `.unx` (IDT) or `.unv` (UDT) universe files exported to JSON, or `.biar` archive
- For API access: Tableau REST API token, Looker API client_id/client_secret, Power BI service principal / OAuth token, Denodo Data Catalog credentials, or BO REST API credentials
- For Snowflake target resolution: Active Snowflake connection (optional — can use manual mapping)
- For deployment: `CREATE SEMANTIC VIEW` privilege on target schema

## Python Automation Modules

This skill includes Python modules under `modules/` that handle deterministic extraction work. CoCo invokes them via bash — they emit structured JSON to stdout and detailed logs to `~/.snowflake/cortex/logs/semantic-extraction/`.

**Setup** (run once per environment):
```bash
cd <skill_directory>
pip install -r requirements.txt
```

**CLI entry point**: `python -m modules.cli <command>`

| Command | Purpose | Example |
|---------|---------|---------|
| `crawl` | Discover source files | `python3 -m modules.cli crawl /path/to/files --type tableau` |
| `parse` | Parse files → inventory JSON | `python3 -m modules.cli parse /path/to/file.twb --type tableau -o inventory.json` |
| `classify` | Run complexity classification | `python3 -m modules.cli classify inventory.json -o classified.json` |
| `generate` | Produce Semantic View YAML + business questions | `python3 -m modules.cli generate inventory.json -o ./yaml_output/` |
| `test-connection` | Validate API/JDBC connectivity | `python3 -m modules.cli test-connection --type denodo --config conn.json` |
| `report` | Generate HTML assessment + Excel workbook + business questions | `python3 -m modules.cli report inventory.json -o ./output/ --customer Acme` |
| `compare` | Diff two inventory versions | `python3 -m modules.cli compare old.json new.json -o diff.json` |
| `generate-from-workbook` | Regenerate YAML from edited Excel | `python3 -m modules.cli generate-from-workbook workbook.xlsx -o ./yaml_output/` |
| `seed-data` | Generate synthetic INSERT SQL for testing | `python3 -m modules.cli seed-data inventory.json -o ./seed/ --rows 100` |
| `si-agent` | Generate Snowflake Intelligence agent artifacts | `python3 -m modules.cli si-agent inventory.json --database MY_DB --schema PUBLIC` |
| `synthesize` | AI-driven semantic view synthesis pipeline | `python3 -m modules.cli synthesize inventory.json --customer Acme` |

All commands return JSON with `status`, results, and `errors` array. Partial results are preserved on failure — a broken file doesn't abort the entire extraction.

**When to use modules vs LLM reasoning:**
- **Use modules**: File crawling, XML/JSON/LookML parsing, DAX/VQL/BO complexity classification, YAML template generation, API connectivity testing
- **Use LLM**: Source detection decisions, user interaction, audit review, qualification judgment, manual translation proposals, description inference

## Workflow

### Step 1: Source & Mode Detection

**Ask** the user:

```
Which BI tool(s) are we extracting from?
1. Tableau only
2. Looker only
3. Power BI only
4. Denodo only
5. SAP Business Objects only
6. Multiple tools (any combination of the above)

How will we access the content?
A. Files on disk (recommended)
B. API access (Tableau Server/Cloud, Looker API, Power BI REST API / XMLA, Denodo Data Catalog, or BO REST API)
C. Both files and API
```

**If Tableau only + small scope (1-3 workbooks) + Snowflake access available:**
Recommend Autopilot as the simpler path. Continue with this skill only if the user needs the audit/mapping artifact or has scale requirements.

**If Power BI:** **Load** `references/powerbi_extraction.md` for file formats, DAX parsing, and API patterns.

**If Denodo:** **Load** `references/denodo_extraction.md` for VQL parsing, JDBC stored procedures, Data Catalog API, and column classification heuristics. Note: Denodo has no native dimension/measure distinction — classification is inferred via heuristics.

**If Business Objects:** **Load** `references/businessobjects_extraction.md` for universe file formats, @function resolution, extraction paths, and object type mapping. Note: BO has native Dimension/Detail/Measure classification — leverage it directly.

---

### Step 2: Input Collection & Validation

**For all file-based sources**, use the Python modules to crawl and validate:
```bash
# Discover source files
python -m modules.cli crawl /path/to/source/files --type <tableau|looker|powerbi|denodo|businessobjects>
```
This returns a JSON file list with paths, sizes, and detected types. Review with the user.

**For API-based sources**, test connectivity first:
```bash
# Test API connection (provide a JSON config with credentials)
python -m modules.cli test-connection --type <source_type> --config connection_config.json
```
Connection config format varies by source — see API client docs in each module.

**Source-specific validation notes:**

- **Tableau**: `.twbx`/`.tdsx` are auto-unzipped by the parser. Ask: "Are there published data sources on Tableau Server not included in these files?"
- **Looker**: Needs the **full project directory**. Check for `manifest.lkml` (may import other projects — flag as external dependency).
- **Power BI**: Parser auto-detects format (.pbit/.pbip/.bim/.pbix). For `.pbix`, `pbixray` is used if available; otherwise recommend `pbi-tools extract` first.
- **Denodo (VQL export)**: Files from `DESC VQL DATABASE`. Ask: "Do you have Data Catalog access? Catalog tags enrich classification."
- **Denodo (JDBC)**: Get host/port/database/credentials. Requires `jaydebeapi` + Denodo JDBC driver JAR.
- **Business Objects (JSON — recommended)**: From `starschema/business-objects-universe-extractor`. Ask: "Multiple Contexts? May generate separate semantic views per context."
- **Business Objects (manual)**: `.unv` files are binary — need UDT or the extractor. `.unx` needs SL Java SDK or IDT export.

**Load** the appropriate reference for LLM context:
- Tableau: `references/tableau_extraction.md`
- Looker: `references/looker_extraction.md`
- Power BI: `references/powerbi_extraction.md`
- Denodo: `references/denodo_extraction.md`
- Business Objects: `references/businessobjects_extraction.md`

> **CHECKPOINT**: Confirm all inputs are valid and scope is agreed.

---

### Step 3: Dashboard & Report Inventory

**Before extracting individual fields**, map the dashboard/report landscape.

**Goal**: Produce a list of ALL dashboards/reports with inferred descriptions of what each one does.

**For Tableau** (from XML):
- Parse all `<dashboard>` elements → extract name
- For each dashboard, parse `<zone>` elements to find sheet references
- Parse `<worksheet>` elements → extract name, referenced data source
- Infer a description from: dashboard title, sheet names, filters, field usage patterns

**For Looker** (from files):
- Parse `.dashboard.lkml` files → extract dashboard name, tile/element definitions, explore references
- For each tile, extract field references and filters
- Infer description from: dashboard title, tile titles, explore names, field selection

**For API** (any tool):
- Tableau: Query `dashboards` and `sheets` via GraphQL
- Looker: Use `all_dashboards` → `dashboard_elements` → `query.fields`
- Power BI: Use `GET /groups/{groupId}/reports` + `GET /groups/{groupId}/datasets` → map reports to datasets

**For Power BI** (from files/model):
- Parse `model.tables` → extract table names, source queries, partitions
- Parse report pages from the report layout JSON (inside `.pbix` or `.pbip`)
- For each page, extract visual elements and their field references
- Infer description from: report name, page names, visual types, field selection

**For Denodo** (from VQL or JDBC):
- Build the view inventory using `build_view_inventory()` from `references/denodo_extraction.md`
- List all Interface Views first (these are the published/user-facing layer)
- For each Interface View, trace implementation views via `VIEW_DEPENDENCIES()`
- Group views by database and folder (if Data Catalog categories are available)
- Infer description from: view names, column names, Data Catalog descriptions/tags
- Note: Denodo has no "dashboard" concept — the inventory is view-based, not report-based

**For Business Objects** (from JSON/SDK):
- Parse universe Class hierarchy — each top-level Class is analogous to a dashboard/report domain
- List all Classes with their object counts (Dimensions, Details, Measures)
- Identify Contexts — each Context represents a distinct query path through the schema
- Infer description from: Class names, object names, universe description
- Note: BO has no "dashboard" in the universe — the inventory is Class/Context-based. If WebI reports are in scope, use the REST API to enumerate reports separately.

**Present to user:**
```
Found N dashboards:

1. "Revenue Dashboard" (5 sheets) — appears to show revenue KPIs by provider/region
2. "User Engagement" (3 sheets) — appears to track daily/weekly active users
3. "Pipeline Overview" (4 sheets) — appears to show sales pipeline stages
...

Does this look complete? Are there dashboards we're missing?
```

> **CHECKPOINT**: User confirms dashboard inventory is complete.

---

### Step 4: Full Semantic Extraction

**Load** `references/concept_mapping.md` for mapping context.

**Use the Python modules to parse and extract:**
```bash
# Parse source files into a unified inventory
python -m modules.cli parse /path/to/source --type <source_type> -o inventory.json --database TARGET_DB --schema PUBLIC
```

This runs the full extraction pipeline: file parsing → field extraction → complexity classification → unified inventory. The output JSON contains tables, dimensions, facts, metrics, relationships, flagged items, and a complexity summary.

**Review the CLI output** — it reports:
- Table count, dimension count, fact count, metric count
- Flagged item count (items needing manual review)
- Complexity summary (simple / needs_translation / manual_required)
- Any parse errors encountered (with partial results preserved)

Extract ALL semantic objects into the structured inventory. **Associate every field with which dashboards use it.** Flag orphaned fields (defined but not used in any dashboard).

**Completeness check** at dashboard level:
- Every field used in a dashboard should appear in the inventory
- If a dashboard references fields not in the inventory, investigate

**Present summary:**
```
Extraction complete:
- X data sources across Y files
- Z joins/relationships
- A dimensions, B measures, C calculated fields
- D fields flagged as needing manual conversion
- E orphaned fields (defined but not used in any dashboard)
```

> **CHECKPOINT**: User confirms inventory summary looks right.

---

### Step 5: Resolve Snowflake Targets

**Load** `references/semantic_view_yaml_spec.md` for target structure context.

**5a. With Snowflake access** (preferred):

1. For each extracted data source/table, query Snowflake:
   ```sql
   SELECT TABLE_CATALOG, TABLE_SCHEMA, TABLE_NAME
   FROM INFORMATION_SCHEMA.TABLES
   WHERE LOWER(TABLE_NAME) LIKE LOWER('%source_table_name%')
   ORDER BY TABLE_CATALOG, TABLE_SCHEMA, TABLE_NAME;
   ```
2. Fuzzy-match: try exact name, then case-insensitive, then with/without `DIM_`/`FACT_`/`STG_` prefixes
3. For confirmed table matches, query columns:
   ```sql
   SELECT COLUMN_NAME, DATA_TYPE
   FROM INFORMATION_SCHEMA.COLUMNS
   WHERE TABLE_CATALOG = '...' AND TABLE_SCHEMA = '...' AND TABLE_NAME = '...'
   ORDER BY ORDINAL_POSITION;
   ```
4. Cross-reference extracted fields with Snowflake columns

**Present side-by-side:**
```
Source Table → Snowflake Candidates:

1. "claims" → ANALYTICS.BILLING.FACT_CLAIMS ✓ (15/18 columns match)
2. "providers" → ANALYTICS.CRM.DIM_PROVIDERS ✓ (all columns match)
3. "custom_calc_table" → No match found (manual mapping needed)
```

**5b. Without Snowflake access:**
1. Generate a mapping template (JSON/YAML) with source names and blank target fields
2. User fills in or provides a separate mapping file
3. Skip column-level validation

> **CHECKPOINT**: User approves complete source→target mapping.

---

### Step 6: Audit & Flag

Classify every extracted field:

| Category | Criteria | Action |
|----------|----------|--------|
| **Auto-convertible** | Simple column reference, basic SUM/COUNT/AVG | Proceed automatically |
| **Needs translation** | Tableau functions (ZN, ATTR, DATETRUNC) / Looker types (tier, case, yesno) / VQL date functions (ADDDAY, GETMONTH, FORMATDATE) / BO @functions (@Select, @Prompt, @Aggregate_Aware) | Apply function translation from `concept_mapping.md`, present for approval |
| **Manual required** | Tableau LOD expressions, Looker Liquid SQL, nested calcs 3+ levels deep, Denodo FLATTEN/NEST/UNNEST, BO @Script, BO nested @Select chains | Present original formula, explain what it does, ask user for Snowflake SQL |
| **Duplicate** | Same metric defined differently across workbooks/explores | Flag both versions, user picks canonical |
| **Orphaned** | Defined but not used in any dashboard | Include in mapping file but mark as unused |

**Volume check**: If a semantic view would exceed ~100 columns, recommend splitting into domain-specific views.

**Present audit summary:**
```
Audit Results:
- X fields auto-convertible (ready to go)
- Y fields need translation (I'll propose conversions for your review)
- Z fields need manual SQL (LOD expressions, Liquid templates)
- W duplicate definitions found
- V orphaned fields

Shall I proceed with translating the Y fields and presenting them for review?
```

> **CHECKPOINT**: User resolves flagged items.

---

### Step 7: Qualify

Present the full audit at the **dashboard level** for triage:

```
Dashboard Qualification:

1. "Revenue Dashboard" (5 sheets, 23 fields, 2 manual items) → Migrate / Skip / Defer?
2. "User Engagement" (3 sheets, 15 fields, 0 manual items) → Migrate / Skip / Defer?
3. "Legacy Report Q1" (2 sheets, 8 fields, 5 manual items) → Migrate / Skip / Defer?
...
```

For each dashboard marked **Migrate**, its associated data sources, joins, and fields will be included in the output.

For each dashboard marked **Skip**, record the reason in the mapping file.

For each dashboard marked **Defer**, include in mapping file as "future scope."

> **CHECKPOINT**: Migration scope confirmed.

---

### Step 8: Generate Outputs

**Always produce two artifacts:**

#### 8a. Mapping File (Excel + JSON)

Generate an Excel workbook using `openpyxl` with these tabs:

| Tab | Contents |
|-----|----------|
| **Dashboards** | Name, source tool, description (inferred), sheet/tile count, field count, qualification (Migrate/Skip/Defer), migration path (Autopilot/YAML/Manual) |
| **Sheets & Tiles** | Parent dashboard, name, description, dimensions used, measures used |
| **Table Mappings** | Source table → Snowflake target (database.schema.table), status (confirmed/candidate/unmapped), matching column count |
| **Field Inventory** | Name, type (dim/measure/calc), source formula, target Snowflake SQL expression, complexity, dashboards using it, resolution status |
| **Flagged Items** | Item, reason (LOD/Liquid/duplicate/unmapped/orphan), suggested action, user resolution |
| **Semantic Views** | Generated view name, source dashboards, table count, dim/metric counts, migration path |

Format the Excel with:
- Header row: bold, dark blue background (#11567F), white text
- Alternating row colors for readability
- Auto-width columns
- Freeze top row
- Data validation dropdowns for status columns where applicable

Also save the JSON version for machine consumption.

#### 8b. Semantic View YAML

**Use the Python modules to generate YAML from the classified inventory:**
```bash
# Generate Semantic View YAML files
python -m modules.cli generate inventory.json -o ./yaml_output/
```

This produces one or more `.yaml` files. If the inventory exceeds ~100 columns, it auto-splits by table into domain-specific views.

For **qualified Looker sources** → YAML generated directly.
For **qualified Tableau sources** → YAML generated AND note which `.twb` files to feed to Autopilot.
For **qualified Denodo sources** → YAML generated directly. Inferred dim/measure classifications from the classifier are embedded. Present for user review before finalizing.
For **qualified Business Objects sources** → YAML generated directly. Native Dimension/Detail/Measure types are used. If multiple Contexts exist, one semantic view per Context is generated.

Use the YAML structure from `references/semantic_view_yaml_spec.md`.

Validate each generated YAML with `cortex reflect <file.yaml>` if available.

> **CHECKPOINT**: User reviews mapping file + YAML before deployment.

---

### Step 9: Deploy & Validate (Optional)

Only proceed if user has Snowflake access and wants to deploy now.

**For generated YAML (Looker sources):**
1. Upload YAML to a Snowflake stage
2. Deploy one at a time:
   ```sql
   CALL SYSTEM$CREATE_SEMANTIC_VIEW_FROM_YAML(
     'DATABASE.SCHEMA.VIEW_NAME',
     '@stage/path/to/file.yaml'
   );
   ```
3. After each successful deploy, run a sample Cortex Analyst query to smoke-test
4. If deployment fails → show error, fix YAML, retry (max 3 attempts)

**For Tableau sources:**
- Guide user to Snowsight → AI & ML → Cortex Analyst → Semantic View Wizard
- Upload the specific `.twb` file identified in Step 7
- Autopilot will generate a draft view — user can refine in the UI

**Post-deployment:**
- Recommend `$semantic-view` skill for ongoing optimization, auditing, and debugging
- Use `SYSTEM$READ_YAML_FROM_SEMANTIC_VIEW` to export and version-control
- Consider `Snowflake-Labs/dbt_semantic_view` package for CI/CD integration

> **OUTPUT**: Mapping file (Excel + JSON, always produced) + Semantic View YAML files + deployed views (if requested).

---

## Stopping Points

- ✋ Step 2: Inputs validated, scope confirmed
- ✋ Step 3: Dashboard inventory confirmed complete
- ✋ Step 4: Extraction summary confirmed
- ✋ Step 5: Source→target mapping approved
- ✋ Step 6: Flagged items resolved
- ✋ Step 7: Migration scope qualified
- ✋ Step 8: Outputs reviewed before deployment

## Output

1. **Mapping File** (Excel `.xlsx` + JSON) — complete audit of all dashboards, fields, table mappings, flagged items, and semantic view definitions
2. **Semantic View YAML** files — ready for deployment or Autopilot refinement
3. **Extraction inventory** (JSON) — raw structured data for machine consumption
4. **HTML assessment report** — visual dashboard-level readiness with overlap analysis and consolidation candidates
5. **Business questions** — per-page eval questions generated via Cortex LLM, embedded in report and workbook
6. **Seed data SQL** — synthetic INSERT/GENERATOR statements for populating Snowflake tables to support semantic view testing
7. **SI agent artifacts** — Cortex Agent specification JSON, semantic view DDL per domain, and deployment SQL script

---

## Business Questions (Eval Framework)

The `report` command automatically generates per-page business questions using Cortex LLM. These questions serve as an **evaluation framework** — they represent the questions each dashboard page was designed to answer, and can be used to verify that the migrated semantic model supports the same analytical needs.

**How it works:**
1. During report generation, `analyze_report_narrative()` builds page profiles from the inventory — field names, types, inferred purpose
2. `generate_business_questions()` sends each page profile to Cortex Complete (default model: `claude-3.5-sonnet`) to generate 3-5 natural-language business questions per page
3. Questions are embedded in both the HTML report (per-page section) and the Excel workbook

**Report command options for question generation:**
- `--connection NAME` — Snowflake connection for Cortex Complete (required for LLM-generated questions)
- `--questions-model MODEL` — Cortex LLM model (default: `claude-3.5-sonnet`)

**Without a Snowflake connection**, questions are omitted from the report. The rest of the report generates normally.

**Use cases:**
- **Pre-migration validation** — Confirm the semantic model covers all business questions before decommissioning the BI tool
- **Acceptance testing** — Run each question through Cortex Analyst after deploying semantic views to verify correct answers
- **Stakeholder sign-off** — Share the question list with dashboard owners to confirm completeness

---

## Post-Extraction Commands

### Seed Data Generation (`seed-data`)

Generate synthetic Snowflake SQL to populate tables referenced by the extracted semantic model. Useful for testing semantic views and Cortex Analyst queries without production data.

```bash
python3 -m modules.cli seed-data inventory.json -o ./seed/ --rows 100
```

**Options:**
- `--rows N` — Rows per table (default: 100)
- `--pages "Page1,Page2"` — Scope to specific dashboard pages
- `--tables "TABLE1,TABLE2"` — Scope to specific tables
- `--all` — Seed every column, not just page-referenced ones
- `--assess-only` — Print column/type assessment only, no SQL
- `--execute` — Execute SQL directly against Snowflake
- `--connection NAME` — Snowflake connection for `--execute`
- `--database DB` / `--schema SCHEMA` — Override target location

The generator infers column types from inventory metadata (data types, expressions, names) and produces appropriate Snowflake-native random generators (UNIFORM, RANDSTR, DATEADD, etc.).

### Snowflake Intelligence Agent (`si-agent`)

Generate a complete Snowflake Intelligence deployment from an extracted inventory — domain-grouped semantic views, a Cortex Agent specification, and deployment SQL.

```bash
python3 -m modules.cli si-agent inventory.json --database MY_DB --schema PUBLIC
```

**Options:**
- `--agent-name NAME` — Agent name (default: BI_ANALYTICS_AGENT)
- `--database DB` / `--schema SCHEMA` — Target Snowflake location
- `--domains '{"Sales": ["FACT_SALES", "DIM_CUSTOMER"]}'` — Explicit domain grouping (JSON)
- `--assess-only` — Print domain assessment only, no artifacts
- `--execute` — Execute deployment SQL against Snowflake
- `--connection NAME` — Snowflake connection for `--execute`

**What it produces:**
1. **Domain assessment** — Tables grouped into logical domains with column counts and feasibility warnings
2. **Semantic View DDL** — One `CREATE SEMANTIC VIEW` per domain with dimensions, facts, metrics, and relationships
3. **Agent specification** — JSON spec with orchestration/response instructions and one `cortex_analyst_text_to_sql` tool per domain
4. **Deployment SQL** — Complete script: role/grants setup, semantic view DDL, and `CREATE AGENT` DDL

**Domain grouping** (auto or explicit):
- Priority 1: Explicit `--domains` JSON override
- Priority 2: Page-based clustering (union-find on overlapping table sets)
- Priority 3: Table name prefix heuristic (DIM_/FACT_/VW_ patterns)
- Priority 4: Single-domain fallback

Target: 5-10 tools per agent, ~50-100 columns per semantic view. The assessment warns when domains exceed these limits.

---

### AI-Driven Synthesis (`synthesize`)

The **synthesize** command is the flagship pipeline — it replaces the manual "report + generate" workflow with an AI-driven approach where CoCo/Opus makes conflict resolution decisions, infers subject-area domains, and generates deployment-ready semantic view YAMLs.

**User intent mapping**: When an SA says "analyze this inventory", "build the semantic views", or "generate the report", CoCo runs `synthesize`.

```bash
python3 -m modules.cli synthesize inventory.json --customer "Acme Corp"
```

**Options:**
- `--customer NAME` — Customer name for report header and output folder naming
- `--source-label LABEL` — Source description for report header
- `--connection NAME` — Snowflake connection name
- `--decisions FILE` — JSON file with CoCo conflict resolution decisions (from Phase 2)
- `--domains FILE` — JSON file with CoCo domain assignment (from Phase 2)

**How it works (two-pass pipeline):**

**Pass 1 — Context preparation** (run without `--decisions` / `--domains`):
1. Loads inventory and runs local analysis (conflicts, reuse, narrative)
2. Scores conflicts by business impact (dashboard breadth, expression divergence, type mismatches)
3. Prepares enriched **resolution context** for each conflict group — expression lineage, dashboard usage, eval question refs
4. Prepares **domain context** — heuristic proposals (page clustering, prefix matching) + eval-informed proposals (business question themes)
5. Prepares **question context** — page profiles with full table/column detail for Opus question generation
6. Writes `*_synthesis_context.json` — CoCo reads this and reasons over it

**CoCo/Opus reasoning** (between passes):
- CoCo reads the synthesis context file
- **Conflict resolution**: For each conflict group, Opus decides which definition to keep, with reasoning and business impact. Returns structured decisions JSON.
- **Domain inference**: Opus evaluates heuristic and eval-informed proposals, acts as a judge, and produces a final domain assignment with reasoning.
- **Business questions**: Opus generates verified queries from the question context with full inventory awareness.

**Pass 2 — Apply + generate** (re-run with `--decisions` and `--domains`):
1. Applies conflict resolutions to inventory (winners included, losers excluded)
2. Generates one Semantic View YAML per domain (50-100 column budget, Snowflake spec compliant)
3. Annotates inventory with `semantic_view`, `status`, `excluded_reason` fields
4. Generates Sharp-quality HTML report with sections: Data Profile, Impact, What We Built, Decisions Made, What Still Needs Review, Dashboard-SV-Source Lineage
5. Generates Excel workbook with "Semantic View" and "Status" columns

**Output:**
- `*_synthesis_context.json` — Context for CoCo reasoning (Pass 1)
- `*_annotated_inventory.json` — Inventory with SV assignments and status
- `*_report.html` — Sharp-quality narrative report
- `*_workbook.xlsx` — Excel with SV + Status columns
- `semantic_views/` — Domain-aligned YAML files

---

## Snowflake Skill Ecosystem

The semantic extraction utility integrates with other Snowflake CoCo skills for a complete end-to-end workflow:

| Skill / Tool | Role in Pipeline |
|------|--------|
| **`semantic-extraction`** (this skill) | Full pipeline: Extract + Synthesize |
| **`semantic-view`** (bundled CoCo skill) | Post-generation: validate/debug YAMLs, enrich VQRs, suggest filters/metrics, debug SQL generation |
| **`cortex-agent`** (bundled CoCo skill) | Post-generation: create/deploy/debug Snowflake Intelligence agents from generated specs |
| **`cortex reflect`** | Pre-deployment YAML validation |
| **Cortex Analyst** | Post-deployment acceptance testing via verified queries |
| **Semantic View Autopilot** | Complementary UI-based path for Tableau-only customers |

**Recommended post-synthesis workflow:**
1. Run `synthesize` to generate domain YAMLs and the narrative report
2. Invoke the **`semantic-view` skill** to validate each YAML and enrich with VQR suggestions
3. Use **`cortex reflect`** for pre-deployment validation
4. Deploy semantic views and run acceptance tests with **Cortex Analyst**
5. Optionally invoke **`cortex-agent` skill** to create an SI agent from the generated agent spec

## Notes

- Tableau LOD expressions, Looker Liquid SQL templates, complex DAX patterns (row context iteration, CALCULATE with multiple filters), Denodo FLATTEN/NEST/UNNEST operations, and BO @Script macros cannot be auto-converted — always flagged for manual review
- Denodo has no native dimension/measure distinction — classification is inferred via data type, naming conventions, aggregation patterns, Data Catalog tags, and optional user override JSON
- SAP BO .unv files (Universe Design Tool) are proprietary binary — cannot be parsed without UDT or the starschema extractor. .unx files (Information Design Tool) require the SL Java SDK or IDT export
- SAP BO Contexts (multiple join paths through the same schema) may require generating separate semantic views per Context
- SAP BO @Aggregate_Aware with 3+ arguments and nested @Select chains (2+ levels) are flagged as manual
- Semantic views work best with ~50-100 total columns for Cortex Analyst performance
- No bulk `CREATE SEMANTIC VIEW` API — must deploy sequentially
- `dbt_semantic_view` package (v1.0.3+) available for CI/CD integration
- `SYSTEM$EXPORT_TDS_FROM_SEMANTIC_VIEW` can generate a `.tds` file from a deployed semantic view for Tableau consumption (bidirectional)
- Power BI `.pbix` files may be compressed differently across PBI Desktop versions — `pbi-tools extract` is the most reliable extraction method

## Troubleshooting Python Modules

| Issue | Cause | Fix |
|-------|-------|-----|
| `ModuleNotFoundError: lkml` | Missing dependency | `pip install -r requirements.txt` in the skill directory |
| `ModuleNotFoundError: jaydebeapi` | Denodo JDBC optional dep | `pip install jaydebeapi` + ensure JVM is installed |
| `ModuleNotFoundError: pbixray` | Power BI .pbix optional dep | `pip install pbixray` or use `.pbit`/`.bim` instead |
| `ConnectionError: ... after 3 attempts` | API/JDBC unreachable | Check credentials, network, firewall. Run `test-connection` to diagnose. |
| `ParseError: Failed to parse ...` | Corrupt or unexpected file format | Check the `errors` array in output — partial results are preserved. Try a different file. |
| `YAML has >100 columns` warning | Large BI model | The generator auto-splits by table. Review split views with user. |
| CLI returns `status: error` | Any unhandled failure | Check log file at `~/.snowflake/cortex/logs/semantic-extraction/` for full traceback. |
| `FileDiscoveryError: Root path does not exist` | Wrong path | Verify the path exists and is accessible. Check for typos. |
| Denodo column classification wrong | Heuristic mismatch | Provide a user override JSON: `{"COLUMN_NAME": "dimension"}` and re-run classify. |
| BO @Function not resolved | Missing object reference | Check the `unresolved` list in output. The referenced object may not be in the export. |
