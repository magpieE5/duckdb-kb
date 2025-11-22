---
id: user-reference-cognos-report-xml
category: reference
title: Cognos Enterprise Report XML Structure
tags:
- cognos
- report-xml
- idr
- metadata
- enterprise-reports
- lineage
created: '2025-11-21T23:58:06.709858'
updated: '2025-11-21T23:58:06.709858'
metadata: {}
---

# Cognos Enterprise Report XML Structure

Full Report XML files capturing complete Enterprise report definitions including queries, layout, prompts, filters, and drill-through. Located in ~/pds/utils/idr/cognos_reports/ organized by Team Content folders. Provides complete substrate for report consumption analysis.

## Problem

cognos_obt table in PDS only captures runtime execution metadata (report_path, query_subject, query_item usage). Missing complete report structure: layout, prompts, filters, conditional formatting, drill-through targets. Need full Report XML to understand report intent and dependencies.

## Solution

Repository at ~/pds/utils/idr/cognos_reports contains full Report XML exports from Cognos. Each .xml file includes:
- Query definitions with dataItem expressions
- Selection logic showing which query_subjects and query_items are consumed
- Layout specifications (tables, charts, crosstabs)
- Prompt definitions for user input
- Filter conditions and logic
- Drill-through report targets

## Context

**Repository:** `~/pds/utils/idr/cognos_reports/Team Content/`
**Format:** Cognos Report XML (.xml files)
**Coverage:** All Enterprise reports (is_enterprise = 'Y')
**Completeness:** Full substrate - includes everything cognos_obt lacks

**Example file examined:** `Student Reports/Student Data.xml`

**Structure discovered:**
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

## Example

**Student Data report findings:**
- Pulls from 4+ query subjects: Student Detail, Person Detail, Degree Guide Major/Minor, Person Address UO
- Expression syntax: `[Query Subject].[Namespace].[Field]`
- Can track exactly which fields from which query subjects each report consumes

**Integration with cognos_obt:**
- cognos_obt provides: execution frequency, runtime patterns, field usage counts
- Report XML provides: complete context, why fields are used, conditional logic, dependencies

**Use case:** Combined analysis enables field consolidation decisions based on both usage frequency (cognos_obt) and functional dependencies (Report XML).


---

*KB Entry: `user-reference-cognos-report-xml` | Category: reference | Updated: 2025-11-21*
