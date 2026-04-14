# Consumption Impact Estimates by Project Type

Use these templates to project Snowflake credit/storage impact for scope documents. Estimates help customers budget and justify projects.

---

## How to Use

1. **Get current baseline** first (Query 1.3.3 from snowhouse-queries.md)
2. Identify the **Primary Module** from Step 1
3. Use the corresponding template below for NEW consumption
4. Calculate percentage increase: `(new_credits / current_credits) × 100`
5. Include BOTH baseline AND incremental in scope doc

**CRITICAL**: Always show consumption as INCREMENTAL INCREASE over current baseline. Customers need to see:
- What they consume TODAY
- What NEW consumption this project adds
- Percentage increase

**Important:** These are rough estimates. Add disclaimer: *"Estimates will be refined during engagement based on actual data characteristics."*

---

## Data Ingestion / Snowpipe

For projects loading data via Snowpipe, external stages, or COPY INTO.

### Initial Load (one-time)

| Component | Formula | Example (76 TB) |
|-----------|---------|-----------------|
| Snowpipe Ingestion | ~1 credit per TB loaded | 76 credits |
| Compute (staging) | Depends on transformation | 50-150 credits |
| **Total Initial** | | **125-225 credits** |

### Ongoing Monthly

| Component | Low | High | Formula |
|-----------|-----|------|---------|
| Snowpipe (incremental) | 30 | 150 | Daily change % × raw TB × 30 |
| Storage (compressed) | raw_TB / 4 | raw_TB / 2 | 2-4x compression |
| Storage Cost | $23/TB/mo | $40/TB/mo | By edition (BC vs Enterprise) |
| Transformation Compute | 100 | 500 | Warehouse size × daily runs |

---

## ML/AI Projects

For projects involving model training, feature engineering, or ML deployment.

### Development Phase (one-time)

| Component | Low | High | Notes |
|-----------|-----|------|-------|
| Feature Engineering | 50 | 200 credits | Data prep, aggregations |
| Model Training | 100 | 1,000 credits | Depends on data size, iterations |
| Experimentation | 50 | 200 credits | Multiple model variations |
| **Total Development** | **200** | **1,400 credits** | |

### Ongoing Monthly (Production)

| Component | Low | High | Notes |
|-----------|-----|------|-------|
| Feature Refresh | 50 | 300 credits | Daily/hourly feature updates |
| Model Retraining | 50 | 500 credits | Weekly/monthly retraining |
| Batch Inference | 20 | 200 credits | Scoring new data |
| Real-time Inference (SPCS) | 100 | 1,000 credits | Container runtime |
| Model Registry Storage | Minimal | Minimal | <1 TB typically |

### SPCS (Snowpark Container Services) - If Used

| Container Size | Credits/Hour | Monthly (24/7) |
|----------------|--------------|----------------|
| CPU Small | ~0.5 | ~360 credits |
| CPU Medium | ~1.0 | ~720 credits |
| GPU Small | ~3.0 | ~2,160 credits |
| GPU Medium | ~6.0 | ~4,320 credits |

---

## Cortex GenAI

For projects using Cortex LLM functions, Search, Analyst, or Agents.

### Token-Based Costs (LLM Functions)

| Model | Input (per 1M tokens) | Output (per 1M tokens) |
|-------|----------------------|------------------------|
| llama3.1-8b | ~$0.24 | ~$0.24 |
| llama3.1-70b | ~$1.21 | ~$1.21 |
| mistral-large2 | ~$2.00 | ~$6.00 |
| claude-3-5-sonnet | ~$3.00 | ~$15.00 |

### Cortex Search Service

| Component | Formula | Notes |
|-----------|---------|-------|
| Indexing (initial) | ~0.5 credits per GB indexed | One-time |
| Indexing (incremental) | ~0.1 credits per GB/day | Daily refresh |
| Query Credits | ~0.01 credits per query | Per search request |
| Storage | ~1.5x source data | Index overhead |

### Cortex Analyst

| Component | Estimate | Notes |
|-----------|----------|-------|
| Query Generation | ~0.02 credits per query | LLM call for SQL generation |
| SQL Execution | Varies | Normal warehouse compute |

### Monthly Projection Template

| Component | Low | High | Notes |
|-----------|-----|------|-------|
| LLM Inference | 50 | 500 credits | Depends on volume, model choice |
| Cortex Search Indexing | 10 | 100 credits | Based on data refresh frequency |
| Cortex Search Queries | 10 | 200 credits | Based on query volume |
| Embedding Generation | 20 | 100 credits | For RAG pipelines |

---

## Apps / Streamlit

For Streamlit in Snowflake (SiS) applications.

### Development Phase

| Component | Low | High | Notes |
|-----------|-----|------|-------|
| Development Compute | 20 | 100 credits | Testing, iteration |
| Staging Data | 10 | 50 credits | Sample data prep |

### Ongoing Monthly (Production)

| Component | Formula | Notes |
|-----------|---------|-------|
| Warehouse Compute | users × queries/day × credits/query | Primary cost driver |
| Concurrent Users | ~0.5 credits/user/hour active | With XS warehouse |
| Background Refresh | Depends on data freshness needs | Scheduled queries |

### Scaling Estimates

| Concurrent Users | Warehouse Size | Credits/Hour | Monthly (8hr/day, 22 days) |
|------------------|----------------|--------------|----------------------------|
| 1-5 | XS | 1 | ~176 credits |
| 5-20 | S | 2 | ~352 credits |
| 20-50 | M | 4 | ~704 credits |
| 50-100 | L | 8 | ~1,408 credits |

---

## Migration Projects

For migrating data/workloads from other platforms to Snowflake.

### One-Time Migration

| Component | Formula | Example (50 TB) |
|-----------|---------|-----------------|
| Data Load | ~1-2 credits per TB | 50-100 credits |
| Schema Conversion Testing | 20-50 credits | Validation queries |
| Parallel Validation | 50-200 credits | Checksums, row counts |
| **Total Migration** | | **120-350 credits** |

### Post-Migration Ongoing

| Component | Low | High | Notes |
|-----------|-----|------|-------|
| Transformed Workloads | 80% | 120% | Of source platform compute |
| Storage | raw_TB / 3 | raw_TB / 2 | Typically better compression |
| Query Optimization | -20% | +20% | May improve or need tuning |

### Storage Comparison

| Source Platform | Snowflake Equivalent | Notes |
|-----------------|---------------------|-------|
| Oracle | ~50-70% storage | Better compression |
| Teradata | ~60-80% storage | Similar compression |
| SQL Server | ~40-60% storage | Significantly better |
| Redshift | ~80-100% storage | Similar |

---

## Iceberg / Open Table Formats

For projects involving Iceberg tables, catalog integrations, external volumes, and cross-engine interop.

### Initial Setup (one-time)

| Component | Low | High | Notes |
|-----------|-----|------|-------|
| External Volume Validation | 5 | 20 credits | Connectivity tests, IAM validation |
| Catalog Integration Setup | 5 | 20 credits | Per catalog, metadata sync test |
| Table Conversion (managed to Iceberg) | 1 credit/TB | 2 credits/TB | Data rewrite to Iceberg format |
| Polaris Catalog Provisioning | 10 | 50 credits | Namespace creation, service connections |
| **Total Initial** | **20** | **100+ credits** | Scales with table count and data volume |

### Ongoing Monthly

| Component | Low | High | Notes |
|-----------|-----|------|-------|
| Auto-Refresh (metadata sync) | 10 | 100 credits | Based on refresh frequency and table count |
| Table Maintenance (compaction) | 20 | 200 credits | Automatic background maintenance |
| Snapshot Management | 5 | 50 credits | Expiration, orphan file cleanup |
| Query Compute (Iceberg scans) | Similar to native | +10-20% overhead | Parquet scan overhead vs native micro-partitions |
| Catalog-Linked DB Sync | 5 | 50 credits | Auto-discover refresh frequency |
| Polaris Catalog Operations | 10 | 100 credits | Credential vending, namespace management |

### Storage Impact

| Component | Formula | Notes |
|-----------|---------|-------|
| Iceberg Data Files | ~1x source data | Parquet format, similar compression to native |
| Iceberg Metadata | ~1-5% of data size | Manifest files, manifest lists, snapshots |
| Snapshot Retention | Configurable | More snapshots = more storage; set expiry policy |
| External Storage Cost | Cloud provider rates | S3/Blob/GCS pricing, not Snowflake storage pricing |

### Cross-Engine Access Cost Considerations

| Scenario | Cost Impact | Notes |
|----------|-------------|-------|
| Snowflake reads external Iceberg | Compute only | No Snowflake storage cost; cloud egress may apply |
| External engine reads Snowflake-managed Iceberg | Cloud egress | Cross-region/cloud egress charges from storage provider |
| Bidirectional read/write | Compute + egress | Both engines incur compute; egress on cross-region reads |

### Monthly Projection Template

| Component | Low | High | Notes |
|-----------|-----|------|-------|
| Auto-Refresh | 10 | 100 credits | Table count x refresh frequency |
| Table Maintenance | 20 | 200 credits | Compaction, snapshot mgmt |
| Catalog Sync | 5 | 50 credits | Catalog-linked DB refresh |
| Polaris Operations | 10 | 100 credits | If Polaris in scope |
| Query Overhead vs Native | +5% | +20% | Iceberg scan overhead |
| Cloud Storage | Cloud rates | Cloud rates | External volume storage at provider pricing |
| Cloud Egress | $0.01-0.09/GB | Varies by provider/region | Cross-region or cross-cloud reads |

---

## Data Engineering / Pipelines

For ELT pipelines, Dynamic Tables, medallion architecture.

### Pipeline Components

| Component | Credits/Run | Notes |
|-----------|-------------|-------|
| COPY INTO (per TB) | ~1 credit | Bulk loading |
| Snowpipe (per TB) | ~1 credit | Streaming |
| Task (per run) | Warehouse-dependent | Scheduled execution |
| Dynamic Table Refresh | Warehouse-dependent | Incremental preferred |
| Stored Procedure | Warehouse-dependent | Transformation logic |

### Dynamic Tables

| Refresh Mode | Cost Pattern | When to Use |
|--------------|--------------|-------------|
| Incremental | Low, steady | Most cases |
| Full | High, periodic | Complex transformations |

| Target Lag | Refresh Frequency | Monthly Multiplier |
|------------|-------------------|-------------------|
| 1 minute | ~1,440/day | High (real-time) |
| 1 hour | ~24/day | Medium |
| 1 day | ~1/day | Low (batch) |

### Monthly Projection Template

| Component | Low | High | Notes |
|-----------|-----|------|-------|
| Ingestion | 30 | 300 credits | Based on daily volume |
| Transformation | 100 | 1,000 credits | Pipeline complexity |
| Dynamic Tables | 50 | 500 credits | Based on target lag |
| Clustering | 10 | 100 credits | Automatic maintenance |
| Storage | $23/TB | $40/TB | By edition |

---

## Template for Scope Document

```markdown
## Projected Consumption Impact

### Current Baseline

| Metric | Value |
|--------|-------|
| Current monthly credits | ~X,XXX |
| Active warehouses | XX |
| Top warehouse | [NAME] (XXX credits/30d) |

### Expected Consumption Increase

This engagement will add **X-Y credits/month** to [CUSTOMER]'s consumption (~X-Y% increase over current baseline).

| Impact Type | Low Estimate | High Estimate |
|-------------|--------------|---------------|
| New monthly credits | +X | +Y |
| Percentage increase | +X% | +Y% |
| New storage | +X TB | +Y TB |
| Storage cost increase | +$X/mo | +$Y/mo |

### Detailed Breakdown

#### Initial [Load/Development/Migration] (one-time)

| Component | Estimate | Calculation |
|-----------|----------|-------------|
| [Component 1] | X credits | [Formula] |
| [Component 2] | X credits | [Formula] |
| **Total Initial** | **X credits** | |

#### Ongoing Monthly (NEW consumption)

| Component | Low Estimate | High Estimate | Notes |
|-----------|--------------|---------------|-------|
| [Component 1] | X | Y | [Notes] |
| [Component 2] | X | Y | [Notes] |
| Storage | X TB | Y TB | [Compression assumption] |
| Storage Cost | $X/mo | $Y/mo | [$23-40/TB by edition] |
| **Monthly Credits** | **X** | **Y** | Excluding storage |

### Assumptions

- [Key assumption 1]
- [Key assumption 2]
- Does not include [exclusion]

*These estimates will be refined during the engagement based on actual 
data characteristics and pipeline design.*
```

---

## Edition Pricing Reference

| Edition | Storage ($/TB/mo) | Compute ($/credit) | Notes |
|---------|-------------------|-------------------|-------|
| Standard | ~$23 | ~$2.00 | |
| Enterprise | ~$23 | ~$3.00 | |
| Business Critical | ~$23 | ~$4.00 | Higher compute cost |

*Prices vary by cloud provider and region. Use customer's actual rates if known.*
