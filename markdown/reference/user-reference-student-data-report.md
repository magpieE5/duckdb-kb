---
id: user-reference-student-data-report
category: reference
title: Student Data Report - Multi-Query-Subject Consumption Example
tags:
- cognos
- student-data
- report-xml
- multi-query-subject
- consolidation
- example
created: '2025-11-22T00:10:39.168231'
updated: '2025-11-22T00:10:39.168231'
metadata: {}
---

# Student Data Report - Multi-Query-Subject Consumption Example

Example Enterprise report demonstrating cross-query-subject field consumption. Located at Team Content/Student Reports/Student Data.xml, pulls from 4+ query subjects including Student Detail, Person Detail, Degree Guide Major/Minor, and Person Address UO.

## Problem

Need to understand how Enterprise reports consume fields across multiple query subjects. What's the typical fragmentation pattern? How many query subjects does a single report touch?

## Solution

Examined Student Data.xml Report XML to identify consumption patterns:

**File location:** `~/pds/utils/idr/cognos_reports/Team Content/Student Reports/Student Data.xml`

**Query structure (lines 1-100):**
```xml
<query name="q_Students">
  <selection>
    <dataItem name="ID">
      <expression>[Student Detail].[Student].[ID]</expression>
    </dataItem>
    <dataItem name="FIRST_NAME">
      <expression>[Student Detail].[Person Detail].[FIRST_NAME]</expression>
    </dataItem>
    <dataItem name="PACKED_MAJORS1">
      <expression>[Student Detail].[Student].[PACKED_MAJORS1]</expression>
    </dataItem>
  </selection>
</query>
```

## Context

**Query subjects consumed:**
1. Student Detail → Student namespace
2. Student Detail → Person Detail namespace
3. Degree Guide Major/Minor
4. Person Address UO

**Expression syntax:** `[Query Subject].[Namespace].[Field]`

**Fragmentation pattern:**
- Single report touches 4+ query subjects
- Each query subject potentially executes separate SQL
- CFM joins these at query execution time
- No shared consolidation layer

**Typical report structure:**
- Main query with multiple dataItem elements
- Each dataItem references specific query_subject.namespace.field
- Report layout binds to dataItem names
- Filters and prompts reference dataItems

## Example

**Field consumption breakdown:**

From Student Detail:
- Student.ID
- Student.PACKED_MAJORS1
- Person Detail.FIRST_NAME
- [additional fields TBD from full read]

From Degree Guide Major/Minor:
- [fields TBD]

From Person Address UO:
- [fields TBD]

**Consolidation opportunity:**
If these 4 query subjects were consolidated into `pds.student_bridge`:
- Single DuckDB view with curated field subset
- Pre-joined tables (no runtime join overhead)
- Simplified field selection for report authors
- Consistent field naming and transformations

**Bridge view concept:**
```sql
CREATE VIEW pds.student_bridge AS
SELECT
  s.id,
  s.packed_majors1,
  pd.first_name,
  -- [other high-usage fields]
FROM odsmgr.student s
JOIN odsmgr.person_detail pd ON s.person_uid = pd.person_uid
LEFT JOIN odsmgr.degree_guide_major_minor dgmm ON s.person_uid = dgmm.person_uid
LEFT JOIN odsmgr.person_address_uo pau ON s.person_uid = pau.person_uid
-- Mirror CFM joins but with curated field subset
```

**Next steps:**
1. Complete read of Student Data.xml to catalog all fields consumed
2. Cross-reference with cognos_obt field usage data
3. Design student_bridge view schema
4. Validate against other student-related reports


---

*KB Entry: `user-reference-student-data-report` | Category: reference | Updated: 2025-11-22*
