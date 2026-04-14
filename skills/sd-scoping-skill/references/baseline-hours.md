# Baseline Hours by Deliverable Type

## Data Engineering

| Object Type | SA Hours | SC Hours | Notes |
|-------------|----------|----------|-------|
| Table (simple) | 1 | 2 | Single source |
| Table (complex) | 2 | 4 | Multiple sources, transformations |
| View | 0.5 | 1 | Standard view |
| Dynamic Table | 1 | 3 | Includes refresh config |
| Stream | 0.5 | 2 | Change data capture |
| Task | 1 | 2 | Scheduled execution |
| Stored Procedure | 2 | 4-8 | Varies by complexity |

## Apps & Dashboards

| Object Type | SA Hours | SC Hours | Notes |
|-------------|----------|----------|-------|
| Streamlit Page (simple) | 2 | 4 | Single data source |
| Streamlit Page (complex) | 4 | 8 | Multiple sources, interactivity |
| Dashboard | 2 | 4-8 | Per dashboard |
| Report | 1 | 2 | Per report |

## ML/AI

| Object Type | SA Hours | SC Hours | Notes |
|-------------|----------|----------|-------|
| Notebook | 2 | 4 | Per notebook |
| ML Model (simple) | 8 | 16 | Single model training |
| ML Model (complex) | 16 | 32 | Feature engineering, tuning |
| Feature Table | 2 | 4 | Per feature set |

## GenAI / Cortex

| Object Type | SA Hours | SC Hours | Notes |
|-------------|----------|----------|-------|
| Cortex Search Service | 4 | 8 | Per service |
| Semantic Model | 4 | 8 | Per model |
| Cortex Agent | 8 | 16 | Per agent |
| LLM Function | 2 | 4 | Per function |

## Integrations

| Object Type | SA Hours | SC Hours | Notes |
|-------------|----------|----------|-------|
| Native Connector | 2 | 4 | Fivetran, Airbyte, etc. |
| Custom Connector | 8 | 16 | API integration |
| External Stage | 1 | 2 | Cloud storage |
| External Function | 4 | 8 | API gateway |

## Iceberg / Open Table Formats

| Object Type | SA Hours | SC Hours | Notes |
|-------------|----------|----------|-------|
| External Volume | 2 | 4 | IAM, trust policies, connectivity validation |
| Catalog Integration (Glue/REST) | 2 | 4 | Per catalog, includes connectivity test |
| Catalog Integration (Unity/Polaris) | 4 | 8 | More complex auth and namespace config |
| Catalog-Linked Database | 2 | 4 | Auto-discover setup and validation |
| Iceberg Table (Snowflake-managed) | 1 | 2 | Per table, standard creation |
| Iceberg Table (externally managed) | 2 | 4 | Per table, includes auto-refresh config |
| Table Conversion (managed to Iceberg) | 2 | 4 | Per table, includes validation |
| Polaris Namespace | 1 | 2 | Per namespace with access policies |
| Polaris Service Connection | 2 | 4 | Per engine connection, credential vending |
| Auto-Refresh Configuration | 1 | 3 | Per table/notification integration |
| Cross-Engine Interop Validation | 4 | 8 | Per engine (Spark, Trino, Databricks) |
| Table Maintenance Automation | 2 | 4 | Compaction, snapshot expiry, cleanup |

## Migration-Specific

| Object Type | MSA Hours | MSC Hours | Notes |
|-------------|-----------|-----------|-------|
| Source Table Assessment | 1 | 2 | Per table |
| Schema Conversion (simple) | 1 | 2 | Direct mapping |
| Schema Conversion (complex) | 3 | 6 | Type changes |
| Stored Proc Conversion | 4 | 12 | Per procedure |
| ETL Job Conversion | 4 | 8 | Per job |
