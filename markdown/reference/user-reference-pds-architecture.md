---
id: user-reference-pds-architecture
category: reference
title: PDS (Personal Data System) Architecture & Philosophy
tags:
- pds
- architecture
- data-warehousing
- duckdb
- parquet
- vendor-agnostic
- higher-ed
created: '2025-11-21T20:08:21.755552'
updated: '2025-11-21T20:08:21.755552'
metadata: {}
---

# PDS (Personal Data System) Architecture & Philosophy

Vendor-agnostic data delivery layer for higher education built on DuckDB + Parquet. Core philosophy: 'Vendors change. Your data shouldn't.' Stack: oracledb, pymssql, duckdb, harlequin, pandas/polars, pyarrow, dbt-core, streamlit, rclone, typer. Performance: 157GB Oracle → 1.31GB Parquet (351M rows × 95 cols). Presented at PNAIRP 2024, external adoption by other institutions and UO departments.

## Technical Stack

**Connectivity & Storage:**
- oracledb, pymssql - Database connectivity
- duckdb - Local query engine and GUI SQL IDE
- harlequin - Local TUI SQL IDE
- pyarrow - Parquet I/O

**Processing & Orchestration:**
- pandas/polars - Data manipulation
- dbt-core/dbt-duckdb - Centralized metadata
- streamlit - Self-service data application development
- rclone - Transfer engine
- typer - CLI framework

## Project Structure

```
pds/
├── models/    # SQL & Python transformations
├── seeds/     # Configurations (CSV-driven)
├── utils/     # Python CLI & utilities
├── tests/     # Data quality tests
└── reports/   # Streamlit reports & apps
```

## Configuration Philosophy

All operations driven by CSV config files in seeds/ directory:
- `_ora_manual.csv` - Tables/views to extract from Oracle
- `_mssql_manual.csv` - Tables/views from SQL Server
- `_columns_manual.csv` - Column selection
- `_transform_manual.csv` - Models (SQL/Python) to run
- `_parq_manual.csv` - Parquet optimization
- `_tests_manual.csv` - Data quality tests
- `_snap_manual.csv` - Time-travel snapshotting
- `_refresh_manual.csv` - Orchestration

## Performance Characteristics

**Storage efficiency example (MFT_TRANS_HISTORY):**
- Oracle: 157 GB
- CSV: 11.3 GB
- Parquet: 1.31 GB (351M rows × 95 cols)

**Query performance:** Dramatic speedup vs. Oracle (demo videos show seconds vs. minutes)

**Parallel extraction:** Config-driven slicing enables 5x speedup (40s → 8s for cognos metadata extraction via 16 parallel slices)

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
- CSV, SQL, and (optionally) Python only
- Git-based version control
- Fast, small, offline data capabilities
- User-friendly QC testing harness
- User-friendly orchestration
- Embedded SQL IDEs (duckdb GUI, harlequin TUI)
- Embedded reporting (Streamlit)
- Embedded MVP metadata (dbt)

## Limitations

**When NOT to use:**
- Real-time data requirements (batch-oriented: minutes to hours)
- Multi-user concurrent writes (read-optimized, use Postgres for write-heavy)
- True big data (billions of rows - consider Spark/Snowflake/BigQuery)

**Perfect for:**
- IR analytics (batch, read-heavy)
- Small to medium data (1GB - 100GB)
- Cost-conscious institutions
- Migration-uncertain environments

## Organizational Context at UO

**Status:** Solo-built by Brock Lampman, controversial stack (management sees as risk due to non-standard)

**Restriction:** Internal use limited to service analysis/forensics only - can measure Cognos/ODS performance but cannot deliver production datasets to campus

**External validation:** Other institutions and other UO departments implementing parts of PDS

**Management concern:** Data exfiltration (PDS 'encourages or acknowledges' what already happens via ungoverned Cognos CSV exports)

## Key Takeaways (from PNAIRP presentation)

1. Not selling product/consultancy - steal what you like
2. Not advocating dropping vendors - get more ROI, weather transitions
3. Build for portability, not platforms - open formats outlast vendor tools
4. Small data deserves small infrastructure - don't over-engineer
5. Composability beats monoliths - swappable components = resilience
6. Strategic infrastructure enables tactical flexibility - keep analysts doing their magic

## Related Materials

**Presentation:** ~/pds/personal/index.html (Reveal.js slides with demo videos)
**Conference:** PNAIRP 2024 (https://www.pnairpevents.org/xconference/view/363)
**GitHub:** QR codes in presentation link to public repo

---

*KB Entry: `user-reference-pds-architecture` | Category: reference | Updated: 2025-11-21*
