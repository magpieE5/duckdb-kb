---
id: user-reference-pds-architecture
category: reference
title: PDS - Personal Data System Architecture
tags:
- pds
- duckdb
- parquet
- dbt
- streamlit
- etl
- uo
- architecture
created: '2025-11-21T20:47:41.546204'
updated: '2025-11-21T20:47:41.546204'
metadata: {}
---

# PDS - Personal Data System Architecture

Vendor-agnostic ETL pipeline for higher education data infrastructure. Built by Brock Lampman at University of Oregon. Uses DuckDB/Parquet/dbt stack for portable, cost-effective alternative to proprietary vendor tools (Cognos, Informatica, ODI). Implements same three-layer pattern as Ellucian (extract → transform → report) but with open formats and swappable components.

## Strategic Tenets

### Technical Foundation
- Cross-platform (Windows/Mac/Linux, laptops/servers/cloud)
- Low-Code-First approach
- FOSS swappable components
- Versioned & readable configurations (Git)
- Optimization tools built-in
- Capable security
- Simple extensibility
- Long vendor-agnostic shelf life

### Usability
- 2-argument max CLI commands
- CSV, SQL, and (optionally) Python only
- Git-based version control
- Fast/Small/Offline data capabilities
- User-friendly QC testing harness
- User-friendly orchestration
- Embedded SQL IDEs (DuckDB GUI, Harlequin TUI)
- Embedded reporting (Streamlit)
- Embedded metadata (dbt)

## Technical Stack

- **oracledb** - Oracle connectivity
- **pymssql** - SQL Server connectivity
- **duckdb** - Local query engine and GUI SQL IDE
- **harlequin** - TUI SQL IDE
- **pandas/polars** - Data manipulation
- **pyarrow** - Parquet I/O
- **dbt-core/dbt-duckdb** - Centralized metadata management
- **streamlit** - Self-service data application development
- **rclone** - Transfer engine
- **typer** - CLI framework

## Project Structure

```
pds/
├── models/    # SQL & Python transformations
├── seeds/     # CSV configurations
├── utils/     # Python CLI & utilities
├── tests/     # Data quality tests
└── reports/   # Streamlit reports & apps
```

## Configuration-Driven Workflows

All operations defined in CSV seed files:
- `_ora_manual.csv` - Oracle table/view extraction
- `_mssql_manual.csv` - SQL Server extraction
- `_columns_manual.csv` - Column selection
- `_transform_manual.csv` - Model execution (SQL/Python)
- `_parq_manual.csv` - Parquet optimization (slicing/splitting)
- `_tests_manual.csv` - Data quality tests
- `_snap_manual.csv` - Time-travel snapshots
- `_export_csv_manual.csv` - CSV exports
- `_download_manual.csv` - Local sync
- `_upload_ora_manual.csv` - Oracle uploads
- `_upload_mssql_manual.csv` - SQL Server uploads
- `_upload_fabric_manual.csv` - MS Fabric uploads
- `_refresh_manual.csv` - Orchestration of seed-based commands

## CLI Commands

Simple 2-argument pattern:
- `pds ora cognos` - Extract Cognos metadata from Oracle
- `pds mssql [config]` - Extract from SQL Server
- `pds transform cognos` - Run transformation models
- `pds upload-ora cognos` - Upload to Oracle
- `pds download cognos` - Sync to local storage
- `pds test cognos` - Run data quality tests
- `pds meta` - Launch dbt metadata viewer

## Performance Gains

### Storage Efficiency
Example: MFT_TRANS_HISTORY (351M rows × 95 columns)
- Oracle: 157 GB
- CSV: 11.3 GB
- Parquet: 1.31 GB (120× smaller than Oracle)

### Query Speed
- Oracle queries: 30-40 seconds
- Parquet queries: 2-3 seconds (10-20× faster)
- Parallel extraction with table slicing (5× improvement on large tables)

## Parquet Storage Pattern

```
utils/data/
├── ioep/                              # Oracle IOEP connection
│   ├── odsmgr__schedule_offering.parquet
│   ├── saturn__spriden.parquet
│   └── sys__dba_tab_columns.parquet
├── icrp/                              # Oracle ICRP connection
│   ├── cognos12__cmobjects.parquet
│   └── cognos12__cmclasses.parquet
└── main/                              # Transformed data
    ├── af_transaction_history.parquet # Single file
    ├── as_student_course.parquet
    └── cognos_obt/                    # Split parquet (16 partitions)
        ├── _split=0/data_0.parquet
        ├── _split=1/data_0.parquet
        └── ...
```

## Transformation Models (dbt)

SQL and Python models with dependency tracking:
1. `cognos_users` - Extract unique usernames/IDs
2. `cognos_audit` - Report execution logs with user details
3. `cognos_xml` - Recursive CTE building folder hierarchy
4. `cognos_specs` (Python) - Parse XML for query subjects/items
5. `cognos_obt` - Final join creating comprehensive metadata

DAG visualization shows model dependencies.

## When PDS Doesn't Make Sense

- Real-time data requirements (batch-oriented: minutes to hours)
- Multi-user concurrent writes (DuckDB read-optimized)
- True "big data" at billions of rows (use Spark/Snowflake/BigQuery)

## When PDS Is Perfect

- IR analytics (batch, read-heavy)
- Small to medium data (1GB - 100GB)
- Cost-conscious institutions
- Migration-uncertain environments
- Vendor lock-in avoidance

## Key Philosophy

**"Vendors change. Your data shouldn't."**

Build for portability, not platforms. Open formats outlast vendor tools. Composability beats monoliths. Strategic infrastructure enables tactical flexibility.

## Documentation

Full presentation: `~/pds/personal/index.html` (reveal.js slides with demos)
GitHub: github.com/magpieE5/pnairp

## Relationship to Banner/ODS/Cognos

PDS implements same three-layer pattern:
- **Banner → Parquet** (replaces Banner → ODS)
- **DuckDB** (replaces Oracle ODS)
- **Streamlit** (replaces Cognos)

Same architecture, portable stack. Brock learning vendor specifics despite having built superior alternative - organizational constraint unclear.

---

*KB Entry: `user-reference-pds-architecture` | Category: reference | Updated: 2025-11-21*
