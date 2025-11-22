---
id: user-reference-model-xml-structure
category: reference
title: Cognos Framework Manager model.xml Structure
tags:
- cognos
- cfm
- metadata
- xml
- lineage
- model
created: '2025-11-21T23:58:04.532580'
updated: '2025-11-21T23:58:04.532580'
metadata: {}
---

# Cognos Framework Manager model.xml Structure

525K-line XML file containing Cognos Framework Manager metadata model with 1646 query subjects. Each query subject embeds complete SQL join definitions including table relationships, join conditions, and field mappings. Located at ~/OTS/ods/cognos/sghe_ods_bv/sghe_ods_bv/model.xml.

## Problem

Need to reverse-engineer Cognos Framework Manager (CFM) join patterns to understand data lineage without access to CFM authoring tool. The proprietary .cpf format requires exporting to XML for programmatic access.

## Solution

Parse model.xml to extract query subject SQL definitions. Each `<querySubject>` element contains:
- Query subject name in `<name locale="en">` element
- SQL definition in `<sql type="cognos">` element within `<modelQuery>`
- Table join patterns, join types (left outer, inner), join conditions
- Field definitions and transformations

## Context

**File location:** `~/OTS/ods/cognos/sghe_ods_bv/sghe_ods_bv/model.xml`
**Size:** 525,291 lines
**Query subjects:** 1,646 total
**Purpose:** Extract CFM join patterns to build DuckDB bridge views that consolidate high-usage fields before fragmentation occurs

**Structure discovered (lines 1-200):**
```xml
<querySubject status="valid">
  <name locale="en">Employee Info</name>
  <definition>
    <modelQuery>
      <sql type="cognos">
        select ... from 
        ([ODSMGR].EMPLOYEE Employee
         join [ODSMGR].PERSON_DETAIL Person_Detail
          on (Employee.PERSON_UID = Person_Detail.PERSON_UID))
        left outer join (...) Employee_Position
         on (Employee.PERSON_UID = Employee_Position.PERSON_UID)
      </sql>
    </modelQuery>
  </definition>
</querySubject>
```

## Example

**Next step:** Parse SQL blocks to extract:
1. Base tables and aliases
2. Join types (inner, left outer, right outer)
3. Join conditions and key relationships
4. Subquery patterns

**Use case:** Build `pds.employee_info_bridge` view mirroring CFM joins with only high-usage fields, enabling "shift left" consolidation before Enterprise reports fragment queries across 99 query subjects.


---

*KB Entry: `user-reference-model-xml-structure` | Category: reference | Updated: 2025-11-21*
