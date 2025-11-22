---
id: user-reference-banner-ods-cognos-architecture
category: reference
title: Banner/ODS/Cognos Three-Layer Architecture
tags:
- banner
- ods
- cognos
- ellucian
- higher-ed
- architecture
- uo
created: '2025-11-21T20:47:41.546204'
updated: '2025-11-21T20:47:41.546204'
metadata: {}
---

# Banner/ODS/Cognos Three-Layer Architecture

Ellucian's Banner ecosystem uses three-layer architecture for higher education data: Banner (transactional Oracle database), ODS (Operational Data Store with denormalized composite tables), and Cognos (IBM BI reporting tool). Understanding this vendor stack required for UO work despite having built superior portable alternative (PDS).

## Three-Layer Architecture

### Layer 1: Banner (Transactional Database)
- Oracle database storing normalized operational data
- Source of truth for student records, finance, HR, payroll
- Optimized for writes/updates (OLTP)
- Complex normalized schema (dozens of tables for simple queries)
- Can't allow report queries to impact transactional performance

### Layer 2: ODS (Operational Data Store)
- Denormalized Oracle database with 'composite tables'
- Reorganizes Banner's complex schema into simpler reporting structures
- Refreshed overnight via ETL using Oracle Streams or Materialized Views
- Optimized for reads/queries during business hours (OLAP)
- Contains frozen data snapshots at key dates (CENSUS, TERM_END)
- Typical pattern: minimal DML during business hours, heavy refresh overnight
- ODSMGR schema commonly used

### Layer 3: Cognos
- IBM BI tool querying ODS (not Banner directly)
- Web-based interface for non-technical users
- Ellucian is preferred Cognos reseller for higher ed
- Widely adopted: UCR, FGCU, STLCC, and other institutions
- Reports query ODS composite tables instead of Banner normalized tables

## Why This Architecture

1. **Performance separation** - Report queries don't slow Banner transactions
2. **Schema simplification** - Composite tables hide Banner complexity from end users
3. **Higher ed specificity** - ODS structures designed for institutional reporting patterns
4. **Consistent reporting periods** - Frozen snapshots enable historical comparisons

## PDS Parallel

Brock's Personal Data System (PDS) implements same pattern with portable stack:
- **Banner → Parquet** (instead of Banner → ODS Oracle tables)
- **DuckDB/Streamlit** (instead of Cognos)
- Same architecture, vendor-agnostic implementation
- 157GB Oracle → 1.31GB Parquet compression
- CLI-driven workflows, dbt metadata management

## Key Differences: Vendor vs Portable

| Aspect | Ellucian Stack | PDS Stack |
|--------|---------------|----------|
| Extraction target | Oracle ODS tables | Parquet files |
| Query engine | Oracle SQL | DuckDB SQL |
| BI tool | Cognos (proprietary) | Streamlit (open source) |
| Storage format | Oracle proprietary | Parquet (open standard) |
| Portability | Vendor lock-in | Swappable components |
| Cost | Licensing fees | FOSS |

## Sources

- [Banner ODS Architecture - Ellucian](https://www.ellucian.com/assets/emea-ap/solution-sheet/emea-banner-operational-data-store.pdf)
- [How Banner ODS Works - Katie Kodes](https://katiekodes.com/pages/blogdrafts/draft-2021-05-25-banner-ods/)
- [Banner ODS Handbook 8.4 - Wayne State](https://tech.wayne.edu/docs/banner_ods_handbook_8_4.pdf)
- [Banner ODS Cognos Integration - STLCC](https://stlcc.edu/departments/information-technology/banner-analytics/cognos.aspx)
- [UCR Banner Data and Reports](https://ucrbanner.ucr.edu/banner-data-and-reports)

## Learning Context

Required learning at UO despite having built PDS. Organizational constraint unclear - integration requirement, political navigation, or institutional knowledge documentation?

---

*KB Entry: `user-reference-banner-ods-cognos-architecture` | Category: reference | Updated: 2025-11-21*
