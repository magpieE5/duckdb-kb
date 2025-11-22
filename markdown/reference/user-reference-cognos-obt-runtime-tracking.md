---
id: user-reference-cognos-obt-runtime-tracking
category: reference
title: cognos_obt Runtime Execution Metadata
tags:
- cognos
- pds
- duckdb
- metadata
- field-usage
- obt
created: '2025-11-21T23:58:09.551542'
updated: '2025-11-21T23:58:09.551542'
metadata: {}
---

# cognos_obt Runtime Execution Metadata

DuckDB table tracking Cognos Enterprise report field consumption patterns. Captures report_path, query_subject, query_item (field) relationships from runtime execution logs. Enables quantified analysis of which fields are actually used vs. which are exposed.

## Problem

Cognos Framework Manager exposes thousands of fields across 1646 query subjects. Need to identify which fields are actually consumed by Enterprise reports to target consolidation efforts and quantify field explosion waste.

## Solution

Query cognos_obt to analyze field usage patterns:

**Profile Enterprise landscape:**
```sql
SELECT COUNT(DISTINCT report_path) as enterprise_reports,
       COUNT(DISTINCT rview_name) as distinct_rviews,
       COUNT(DISTINCT query_subject) as distinct_query_subjects
FROM main.cognos_obt
WHERE is_enterprise = 'Y'
-- Result: 162 reports, 99 rviews, 99 query subjects
```

**Identify hot paths (high-usage query subjects):**
```sql
SELECT rview_name,
       COUNT(DISTINCT report_path) as used_in_reports,
       COUNT(DISTINCT query_item) as distinct_columns
FROM main.cognos_obt
WHERE is_enterprise = 'Y'
GROUP BY rview_name
ORDER BY used_in_reports DESC
LIMIT 20
-- Top: organization_hierarchy (47), operating_ledger (40), person_detail (27)
```

**Quantify field explosion:**
```sql
SELECT query_subject,
       COUNT(DISTINCT query_item) as total_fields,
       COUNT(DISTINCT CASE WHEN report_count >= 10 THEN query_item END) as high_usage_fields
FROM (
  SELECT query_subject, query_item, COUNT(DISTINCT report_path) as report_count
  FROM main.cognos_obt WHERE is_enterprise = 'Y'
  GROUP BY query_subject, query_item
)
GROUP BY query_subject
HAVING total_fields > 20
ORDER BY total_fields DESC
-- Employee Position: 172 total, 8 high-usage = 95% waste
```

## Context

**Database:** `~/pds/utils/_pds.duckdb`
**Table:** `main.cognos_obt`
**Key fields:**
- `report_path` - Report location in Cognos
- `query_subject` - CFM query subject (data source)
- `query_item` - Individual field/column
- `is_enterprise` - Filter for Enterprise reports ('Y'/'N')
- `rview_name` - Alternative query subject identifier

**Coverage:** Runtime execution logs, not complete report structure (see user-reference-cognos-report-xml for full substrate)

## Example

**Field explosion discovery:**
- **Employee Position:** 172 fields defined, only 8 high-usage (used in 10+ reports)
- **Waste calculation:** 164 fields exposed but rarely/never used = 95% overhead
- **Consolidation target:** Build bridge view with 25 fields (8 high-usage + 17 medium-usage) = 85% reduction

**Hot path identification:**
- **organization_hierarchy:** Used in 47 of 162 Enterprise reports (29% penetration)
- **operating_ledger:** 40 reports (25%)
- **person_detail:** 27 reports (17%)

**Use case:** Prioritize consolidation efforts on high-waste query subjects appearing in hot paths. Employee Position (95% waste) + organization_hierarchy (47 reports) = prime candidate for "shift left" bridge view.


---

*KB Entry: `user-reference-cognos-obt-runtime-tracking` | Category: reference | Updated: 2025-11-21*
