---
id: user-reference-pds-diagnostic-workflow
category: reference
title: PDS Diagnostic Workflow for Banner ODS Issues
tags:
- pds
- banner
- diagnostic
- workflow
- reference
- duckdb
created: '2025-11-21T10:51:33.442305'
updated: '2025-11-21T10:51:33.442305'
metadata: {}
---

# PDS Diagnostic Workflow for Banner ODS Issues

Standard workflow for diagnosing Banner ODS data quality issues using PDS (Portable Data Synchronization) system. Combines Banner source table extraction, DuckDB analysis, and view chain tracing.

## PDS Seed File Format

**Location:** `~/pds/seeds/manual/_ora_manual.csv`

**Format:**
```csv
table_name,where
ioep.saturn__ssbsect,ssbsect_term_code >= '202401'
ioep.saturn__sfrstcr,sfrstcr_term_code >= '202401'
```

**Schema prefixes:**
- `ioep.saturn__` - Banner source tables (SATURN schema)
- `ioep.odssrc__` - ODS source views (ODSSRC schema)
- `ioep.odsmgr__` - ODS manager views (ODSMGR schema)

**Where clause:**
- `none` - Extract full table (use for small lookup tables: STVSSTS, STVSUBJ)
- SQL predicate - Filter large tables (example: `academic_period >= '202401'`)

## Diagnostic Workflow

### Step 1: Identify View Chain
Trace data flow from Banner source to final ODS view:
```bash
# Find view definition
ls ~/pds/utils/idr/ioep/view/odsmgr/ | grep [view_name]

# Read view SQL
cat ~/pds/utils/idr/ioep/view/odsmgr/[view_name].sql

# Identify source tables (FROM/JOIN clauses)
grep -E "FROM|JOIN" [view].sql
```

### Step 2: Populate PDS Seed File
Add critical tables to `_ora_manual.csv`:
- **Banner source tables** (SATURN schema) - raw data
- **Lookup/decode tables** (STV* tables) - validation
- **ODS views at each layer** - trace transformations

Filter large tables by term/date to reduce extraction time.

### Step 3: Extract Data with PDS
```bash
# Run PDS extraction (method TBD - Brock's workflow)
# Outputs to: ~/pds/utils/data/main/*.parquet
```

### Step 4: Query with DuckDB
```bash
# Query extracted data
duckdb ~/pds/utils/_pds.duckdb "
SELECT * FROM read_parquet('~/pds/utils/data/main/[table].parquet')
WHERE [conditions]
"

# Or query registered tables
duckdb ~/pds/utils/_pds.duckdb "
SELECT * FROM ioep.saturn__ssbsect 
WHERE ssbsect_term_code = '202502'
"
```

### Step 5: Comparative Analysis
Compare data at each layer to find where records drop out:
```sql
-- Example: Find students registered but course not in schedule_offering
SELECT sf.sfrstcr_crn, COUNT(DISTINCT sf.sfrstcr_pidm) as student_count
FROM ioep.saturn__sfrstcr sf
LEFT JOIN ioep.odsmgr__schedule_offering so
  ON sf.sfrstcr_term_code = so.academic_period
 AND sf.sfrstcr_crn = so.course_reference_number
WHERE sf.sfrstcr_term_code >= '202401'
  AND so.course_reference_number IS NULL
GROUP BY sf.sfrstcr_crn
ORDER BY student_count DESC;
```

## PDS Test Structure

**Tests:** `~/pds/tests/[issue]__[description].sql`
- Verification queries that should return 0 rows (or specific thresholds)
- Example: `idr_3771__verify_missing_offerings.sql` counts missing schedule offerings

**Models:** `~/pds/models/[issue]__[description].sql`
- Diagnostic queries providing details about failing conditions
- Example: `idr_3771__missing_schedule_offerings.sql` lists which CRNs missing + impact

**Test results cached:** `~/pds/utils/data/main/[issue]__[description].parquet`

## Common Banner Tables

**Section/Course:**
- `SSBSECT` - Section master
- `SCBCRSE` - Course catalog
- `SSBOVRR` - Section overrides
- `SSBDESC` - Section descriptions

**Student Registration:**
- `SFRSTCR` - Student course registration
- `SHRTCKN/SHRTCKG` - Student course history

**Lookup/Decode:**
- `STVSSTS` - Section status codes
- `STVTERM` - Term codes
- `STVSUBJ` - Subject codes
- `STVCOLL/STVDEPT/STVDIVS` - College/department/division codes

---

*KB Entry: `user-reference-pds-diagnostic-workflow` | Category: reference | Updated: 2025-11-21*
