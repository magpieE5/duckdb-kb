---
id: user-reference-pds-overview
category: reference
title: PDS - Vendor-Agnostic Data Platform Overview
tags:
- pds
- duckdb
- parquet
- vendor-agnostic
- data-platform
- reference
created: '2025-11-22T12:05:38.308273'
updated: '2025-11-22T12:05:38.308273'
metadata: {}
---

# PDS - Vendor-Agnostic Data Platform Overview

Proof-of-concept data platform built as modern alternative to vendor-locked IDR warehouse. Architecture uses multi-process Python CDC to Hive-partitioned Parquet, DBT-DuckDB transformations, SharePoint/OneDrive distribution, Streamlit reporting, Jenkins orchestration, MKDocs documentation, GitHub project management. Goals: improve data quality, literacy, governance, variety, accessibility, flexibility, and reduce costs.

## Technical Stack

- **oracledb/pymssql** - Source database connectivity
- **duckdb** - Local query engine and GUI SQL IDE
- **harlequin** - TUI SQL IDE
- **pandas/polars** - Data manipulation
- **pyarrow** - Parquet I/O
- **dbt-core/dbt-duckdb** - Centralized metadata and transformations
- **streamlit** - Self-service data application development
- **rclone** - Transfer engine
- **typer** - CLI framework

## Strategic Tenets

**Technical Foundation:**
- Cross-platform (Windows/Mac/Linux, laptops/servers/cloud)
- Low-code-first approach
- FOSS swappable components
- Versioned & readable configurations
- Capable security
- Simple extensibility
- Long vendor-agnostic shelf life

**Usability:**
- 2-argument max CLI commands
- CSV, SQL, and optionally Python
- Git for version control
- Fast, small, offline data
- User-friendly QC testing harness
- Embedded SQL IDEs, reporting, metadata

## Project Structure

```
pds/
├── models/    # SQL & Python transformations
├── seeds/     # Configurations
├── utils/     # Python CLI & utilities
├── tests/     # Data quality tests
└── reports/   # Streamlit reports & apps
```

## Configuration-Driven Architecture

Seed files define all operations:
- `_ora_manual.csv`, `_mssql_manual.csv` - Extraction targets
- `_columns_manual.csv` - Column selection
- `_transform_manual.csv` - Model execution
- `_parq_manual.csv` - Parquet optimization
- `_tests_manual.csv` - Data quality tests
- `_snap_manual.csv` - Time-travel snapshotting
- `_export_csv_manual.csv` - CSV exports
- `_download_manual.csv`, `_upload_ora_manual.csv`, etc. - Distribution
- `_refresh_manual.csv` - Orchestration

## Performance Characteristics

**Storage efficiency example (MFT_TRANS_HISTORY - 351M rows × 95 cols):**
- Oracle: 157 GB
- CSV: 11.3 GB
- Parquet: 1.31 GB (119x compression vs. Oracle)

**Query performance:** Parquet queries significantly faster than Oracle for analytical workloads

## CLI Commands

Core workflows:
- `pds ora {config}` - Extract from Oracle
- `pds mssql {config}` - Extract from SQL Server
- `pds transform {config}` - Run dbt models
- `pds tests {config}` - Execute data quality tests
- `pds upload-ora {config}` - Upload to Oracle
- `pds download {config}` - Sync to local storage
- `pds meta` - Launch metadata/reporting UI

## Current Status

**Adoption:**
- Production use: Other UO departments, external schools (via Brock's advising/code sharing)
- Internal constraint: "Controversial" at UO IS, personal-use-only for Brock and Sameer
- Not technical objection but institutional resistance

**Strategic positioning:** Building future direction while maintaining legacy OTS/Jenkins/Oracle stack for official work

## Use Cases

**Ideal for:**
- IR analytics (batch, read-heavy workloads)
- Small to medium data (1GB - 100GB)
- Cost-conscious institutions
- Migration-uncertain environments
- Vendor lock-in escape

**Not suitable for:**
- Real-time data requirements
- Multi-user concurrent writes (DuckDB is read-optimized)
- True "big data" (billions of rows - use Spark/Snowflake/BigQuery)

## Related Projects

See user-reference-ots-devops for legacy deployment pipeline that PDS is gradually replacing in Brock's workflow.

---

*KB Entry: `user-reference-pds-overview` | Category: reference | Updated: 2025-11-22*
