# Migration Engagements

## Additional Phases for Migration
- Source Assessment & Inventory
- Schema Conversion & Mapping
- Data Migration & Loading
- Validation & Reconciliation
- Cutover Planning

## Migration-Specific Baseline Hours

| Object Type | MSA Hours | MSC Hours | Notes |
|-------------|-----------|-----------|-------|
| Source Table Assessment | 1 | 2 | Per table analysis |
| Schema Conversion (simple) | 1 | 2 | Direct mapping |
| Schema Conversion (complex) | 3 | 6 | Data type changes, restructuring |
| Data Migration Script | 2 | 4 | Per table |
| Validation Script | 1 | 3 | Row count, checksum |
| Stored Proc Conversion | 4 | 12 | Per procedure (varies by complexity) |
| View Conversion | 1 | 3 | Per view |
| ETL Job Conversion | 4 | 8 | Per job |

## Migration Complexity Factors

| Factor | Impact |
|--------|--------|
| Source Platform | Oracle/Teradata = +20%, SQL Server = baseline |
| Data Volume | >10TB = +30% for migration phase |
| Transformations | Complex = +50% for conversion |
| Dependencies | Cross-system = +25% |

## Migration Risk Factors

1. Data type incompatibility between source and Snowflake
2. Stored procedure logic complexity and conversion effort
3. Historical data volume and migration window constraints
4. Parallel running requirements during cutover
5. Source system access and extraction limitations
