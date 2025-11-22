---
id: user-reference-pds-architecture
category: reference
title: PDS Architecture - Vendor-Agnostic Data Delivery Layer
tags:
- pds
- architecture
- duckdb
- parquet
- vendor-agnostic
- uo
created: '2025-11-21T23:05:16.927724'
updated: '2025-11-22T07:54:03.192113'
metadata: {}
---

# PDS Architecture - Vendor-Agnostic Data Delivery Layer

Personal Data System (PDS) at ~/pds is a vendor-agnostic data delivery layer for University of Oregon, built on DuckDB, Parquet, and dbt. Extracts from Oracle/MSSQL, transforms locally, distributes across platforms. Sole developer: Brock Lampman.

## Architecture

**Core components:**
- **DuckDB** - Local query engine and SQL IDE
- **Parquet** - Storage format (massive compression: Oracle 157GB → Parquet 1.31GB for same data)
- **dbt** - Centralized metadata and transformations
- **Python** - CLI framework (typer), data manipulation (pandas/polars)
- **rclone** - Transfer engine for distribution

**Storage structure:**
```
utils/data/
├── ioep/ - Parquet from Oracle 'IOEP' instance
├── icrp/ - Parquet from Oracle 'ICRP' instance  
├── main/ - Transformed parquet in PDS
└── _pds.duckdb - DuckDB file/engine
```

## Strategic Tenets

**Technical foundation:**
- Platform agnostic (Windows/Mac/Linux, laptops/servers/cloud)
- Low-Code-First approach
- FOSS swappable components
- Versioned & readable configurations (CSV seed files)
- Long vendor-agnostic shelf life

**Usability:**
- 2-argument max CLI commands
- CSV, SQL, and optionally Python
- Fast/Small/Offline data capabilities
- Embedded SQL IDEs (DuckDB GUI, harlequin TUI)
- Embedded reporting (Streamlit apps)

**Philosophy:**
- Build for portability, not platforms
- Open formats outlast vendor tools
- Small data deserves small infrastructure
- Composability beats monoliths
- Vendors change, your data shouldn't

## Key Directories

- **~/pds** - Main codebase
- **~/pds/utils/_pds.duckdb** - DuckDB database (query access granted to Arlo)
- **~/pds/utils/idr** - ODS/Cognos work (ODSMGR views, Report XMLs)
- **~/pds/models/** - SQL/Python transformation models
- **~/pds/seeds/** - Configuration CSVs
- **~/pds/personal/index.html** - Full presentation on architecture

## Use Cases

**Perfect for:**
- IR analytics (batch, read-heavy)
- Small to medium data (1GB - 100GB)
- Cost-conscious institutions
- Migration-uncertain environments

**Not suitable for:**
- Real-time data requirements (batch-oriented: minutes to hours)
- Multi-user concurrent writes (read-optimized)
- True "big data" billions of rows (consider Spark/Snowflake/BigQuery)

## Related Resources

- See user-biographical for career context
- See user-reference-cognos-lineage for Cognos metadata work
- Presentation: ~/pds/personal/index.html

---

*KB Entry: `user-reference-pds-architecture` | Category: reference | Updated: 2025-11-22*
