---
id: user-pattern-vendor-agnostic-data-layer
category: pattern
title: Vendor-Agnostic Data Delivery Layer (PDS Architecture)
tags:
- pattern
- architecture
- data-engineering
- vendor-agnostic
- higher-ed
- pds
created: '2025-11-20T12:37:57.971232'
updated: '2025-11-20T12:37:57.971232'
metadata: {}
---

# Vendor-Agnostic Data Delivery Layer (PDS Architecture)

Architectural pattern for building data infrastructure that survives vendor migrations and eliminates lock-in. Implemented in Brock's PDS (Parquet Delivery System) for University of Oregon.

## Problem

Higher ed data teams face:
- Vendor lock-in at every layer (Oracle/MS databases, proprietary ETL like ODI/SSIS/Informatica, platform-specific BI)
- Slow workflows (weeks/months to build datasets)
- Vendor migrations = rebuild everything (years of work to rewrite reports and pipelines)
- Business logic scattered across proprietary tools

## Solution Architecture

**Core principle:** Vendors change. Your data shouldn't.

**Technical Stack (composable, swappable components):**
- **Storage layer:** Parquet files (open format, massive compression: 157GB Oracle → 1.3GB parquet)
- **Query engine:** DuckDB (local, fast, embedded SQL IDE)
- **Transform layer:** dbt-core + SQL/Python models (dependency graphs, version control)
- **CLI framework:** typer (simple 2-arg max commands)
- **Configuration:** CSV files in git (readable, versioned)
- **Connectivity:** oracledb, pymssql (extract from proprietary sources)
- **Transfer:** rclone (sync to cloud/local)
- **Reporting:** Streamlit (self-service apps for analysts)

**Project Structure:**
```
pds/
├── models/    # SQL & Python transformations (dbt-style)
├── seeds/     # CSV configurations (what/where/how to extract/transform)
├── utils/     # Python CLI & utilities
├── tests/     # Data quality tests
└── reports/   # Streamlit apps
```

**Key Capabilities:**
- Extract from Oracle/SQL Server to parquet with massive compression
- Parallel extraction via table slicing (40s → 8s demonstrated, 5x speedup)
- Transform with SQL/Python models in dependency graphs
- Upload to Oracle/MSSQL/MS Fabric (hybrid on-prem/cloud)
- Embedded SQL IDEs (DuckDB GUI, harlequin TUI)
- User-friendly testing harness for data quality
- Self-service reporting without BI vendor lock-in

## Performance Characteristics

**Storage efficiency example (MFT_TRANS_HISTORY: 351M rows × 95 cols):**
- Oracle: 157 GB
- CSV: 11.3 GB (7% of Oracle)
- Parquet: 1.31 GB (0.83% of Oracle)

**Query performance:** Parquet queries dramatically faster than Oracle for analytics workloads (demonstrated in conference presentation)

## Strategic Tenets

**Technical Foundation:**
- Windows/Mac/Linux; laptops, servers, cloud (run anywhere)
- Low-Code-First (CSV configs, SQL models)
- FOSS Swappable Components (no vendor lock-in)
- Versioned & readable configurations (git-friendly)
- Long vendor-agnostic shelf life

**Usability:**
- 2-arg max CLI commands
- CSV, SQL, and optionally Python (that's it)
- Fast/Small/Offline Data capable
- User-friendly QC testing
- Embedded metadata (dbt-style lineage)

## When NOT to Use

- Real-time data requirements (this is batch-oriented: minutes to hours)
- Multi-user concurrent writes (DuckDB is read-optimized, use Postgres for write-heavy)
- True "big data" at scale (billions of rows → consider Spark/Snowflake/BigQuery)

## When Perfect For

- IR analytics (batch, read-heavy)
- Small to medium data (1GB - 100GB)
- Cost-conscious institutions
- Migration-uncertain environments (weather vendor transitions)

## Philosophy

> **Build for portability, not platforms.** Open formats outlast vendor tools.

> **Small data deserves small infrastructure.** Don't over-engineer.

> **Composability beats monoliths.** Swappable components = resilience.

> **Strategic infrastructure enables tactical flexibility.** Keep analysts doing their magic during vendor transitions.

## Implementation Reference

- **Project:** ~/pds (University of Oregon production system)
- **Presentation:** ~/pds/personal/index.html (conference talk with demos)
- **GitHub:** github.com/magpieE5/pnairp (public repo)

## Related Patterns

- Parquet as universal data interchange format
- dbt-core for transform layer metadata and lineage
- CLI-first tooling for reproducibility
- Configuration-as-code in git for version control

---

*KB Entry: `user-pattern-vendor-agnostic-data-layer` | Category: pattern | Updated: 2025-11-20*
