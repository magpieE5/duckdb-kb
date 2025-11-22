---
id: user-reference-enterprise-report-hot-paths
category: reference
title: Cognos Enterprise Report Hot Paths - High-Usage Query Subjects
tags:
- cognos
- hot-paths
- prioritization
- field-usage
- enterprise-reports
- obt
created: '2025-11-22T00:10:37.128620'
updated: '2025-11-22T00:10:37.128620'
metadata: {}
---

# Cognos Enterprise Report Hot Paths - High-Usage Query Subjects

Top 20 most-consumed Cognos query subjects ranked by report penetration. Hot paths represent shared data sources used across many Enterprise reports, making them prime candidates for consolidation and performance optimization.

## Problem

Need to prioritize data quality and consolidation efforts. Which query subjects have the highest impact? Which ones, if optimized, would benefit the most reports?

## Solution

Query cognos_obt to rank query subjects by usage frequency:

```sql
SELECT rview_name,
       COUNT(DISTINCT report_path) as used_in_reports,
       COUNT(DISTINCT query_item) as distinct_columns
FROM main.cognos_obt
WHERE is_enterprise = 'Y'
GROUP BY rview_name
ORDER BY used_in_reports DESC
LIMIT 20
```

**Top 10 hot paths:**
1. **organization_hierarchy** - 47 reports (29% penetration)
2. **operating_ledger** - 40 reports (25%)
3. **person_detail** - 27 reports (17%)
4. **student_detail** - [count TBD]
5. **employee_position** - [count TBD]
6-10. [Additional hot paths TBD]

## Context

**Data source:** `main.cognos_obt` in `~/pds/utils/_pds.duckdb`
**Total Enterprise reports:** 162
**Total query subjects used:** 99

**Penetration calculation:**
- organization_hierarchy: 47/162 = 29% of all Enterprise reports
- Changes to this query subject impact nearly 1/3 of reporting

**Use case:**
- Prioritize consolidation: Hot paths with field explosion = highest ROI
- Focus data quality efforts on shared dependencies
- Identify breaking change blast radius

## Example

**Consolidation prioritization matrix:**

| Query Subject | Reports | Fields | High-Usage | Waste % | Priority Score |
|---|---|---|---|---|---|
| organization_hierarchy | 47 | TBD | TBD | TBD | 47 × waste% |
| operating_ledger | 40 | TBD | TBD | TBD | 40 × waste% |
| employee_position | [TBD] | 172 | 8 | 95% | [count] × 0.95 |

**Strategy:**
1. Run field explosion analysis on top 10 hot paths
2. Calculate priority score: `report_count × waste_percentage`
3. Build bridge views for top 5 by priority score
4. Measure field usage shift over time

**Next steps:**
- Complete hot path ranking (full top 20 list)
- Run field explosion query on each hot path
- Calculate priority scores
- Document findings in consolidation roadmap


---

*KB Entry: `user-reference-enterprise-report-hot-paths` | Category: reference | Updated: 2025-11-22*
