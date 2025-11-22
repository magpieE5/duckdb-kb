---
id: user-issue-field-explosion-problem
category: issue
title: Cognos Field Explosion - Massive Overhead from Unused Fields
tags:
- cognos
- data-quality
- field-explosion
- consolidation
- shift-left
- cfm
created: '2025-11-22T00:09:50.036870'
updated: '2025-11-22T00:09:50.036870'
metadata: {}
---

# Cognos Field Explosion - Massive Overhead from Unused Fields

Cognos Framework Manager query subjects expose far more fields than Enterprise reports actually consume. Example: Employee Position exposes 172 fields but only 8 are high-usage (used in 10+ reports) = 95% waste. This creates maintenance burden, query complexity, and confusion for report authors.

## Problem

**Symptoms:**
- Query subjects with 100+ fields but only 5-10 heavily used
- Report authors overwhelmed by field selection options
- Difficult to identify which fields are safe to deprecate
- Query performance impacted by unnecessary field availability

**Scale of problem:**
- Employee Position: 172 defined → 8 high-usage (95% waste)
- Identification targets exist across multiple query subjects
- Pattern repeats: many fields exposed "just in case" but never used

**Root cause:**
- CFM authors expose comprehensive field sets to avoid future schema changes
- No usage-based governance or field lifecycle management
- "Better to have it and not need it" mentality
- No visibility into actual field consumption until PDS analysis

## Solution

**Three-tier consolidation strategy:**

1. **Quantify waste per query subject:**
```sql
SELECT query_subject,
       COUNT(DISTINCT query_item) as total_fields,
       COUNT(DISTINCT CASE WHEN report_count >= 10 THEN query_item END) as high_usage,
       COUNT(DISTINCT CASE WHEN report_count BETWEEN 3 AND 9 THEN query_item END) as medium_usage,
       COUNT(DISTINCT CASE WHEN report_count < 3 THEN query_item END) as low_usage
FROM (
  SELECT query_subject, query_item, COUNT(DISTINCT report_path) as report_count
  FROM main.cognos_obt WHERE is_enterprise = 'Y'
  GROUP BY query_subject, query_item
)
GROUP BY query_subject
HAVING total_fields > 20
ORDER BY total_fields DESC
```

2. **Build "shift left" bridge views:**
- Create DuckDB views mirroring CFM joins
- Include only high-usage + medium-usage fields
- Example: `pds.employee_position_bridge` with 25 fields (8 high + 17 medium) vs 172 in CFM

3. **Measure consolidation impact:**
- Target: 85% field reduction (172 → 25) for Employee Position
- Benefit: Simplified field selection, faster queries, clearer data model

## Context

**Discovered in S1 via:**
- Query of cognos_obt showing field usage distribution
- Analysis of Employee Position query subject
- Comparison of total_fields vs high_usage_fields

**Related hot paths:**
- organization_hierarchy (47 reports) - check for field explosion
- operating_ledger (40 reports) - check for field explosion
- person_detail (27 reports) - check for field explosion

**Consolidation philosophy:**
- "Shift left" = consolidate BEFORE CFM fragmentation
- Build bridge views with curated field subsets
- Maintain CFM as source of truth, bridge as consumption layer

## Example

**Employee Position consolidation:**

**Before (CFM):**
- 172 fields exposed
- Report authors confused by options
- 164 fields used in <10 reports (95% waste)

**After (Bridge View):**
```sql
CREATE VIEW pds.employee_position_bridge AS
SELECT
  -- 8 high-usage fields (10+ reports)
  person_uid,
  position_number,
  job_title,
  ... (5 more)
  
  -- 17 medium-usage fields (3-9 reports)
  department_code,
  position_status,
  ... (15 more)
  
FROM odsmgr.employee_position
-- Total: 25 fields, 85% reduction
```

**Impact:**
- Report authors see 25 relevant fields instead of 172
- 95% of report needs covered by 15% of fields
- Performance improved (fewer fields = faster queries)
- Maintenance simplified (deprecated fields don't appear in bridge)

**Next steps:**
1. Run consolidation analysis on all query subjects with >20 fields
2. Identify top 5 candidates by (waste_percentage × report_penetration)
3. Build bridge views for top candidates
4. Measure adoption and field usage shift


---

*KB Entry: `user-issue-field-explosion-problem` | Category: issue | Updated: 2025-11-22*
