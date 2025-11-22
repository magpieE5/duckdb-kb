---
id: user-reference-cognos-lineage
category: reference
title: Cognos Enterprise Reports - Lineage & Consolidation Targets
tags:
- cognos
- metadata
- lineage
- enterprise-reports
- consolidation
- uo
created: '2025-11-21T23:05:16.927724'
updated: '2025-11-21T23:05:16.927724'
metadata: {}
---

# Cognos Enterprise Reports - Lineage & Consolidation Targets

University of Oregon Cognos metadata showing consumption patterns across 162 Enterprise reports. Data stored in main.cognos_obt table in ~/pds/utils/_pds.duckdb, derived from parsing Cognos Report XML and Framework Manager model.

## Metadata Sources

**Full continuity substrate:**
1. **~/pds/utils/idr/cognos_reports/** - Complete Report XML files (layout, prompts, logic, filters)
2. **main.cognos_obt table** - Parsed consumption patterns (query_subject, query_item, report_path, runtime execution)
3. **~/OTS/ods/cognos/sghe_ods_bv/sghe_ods_bv/model.xml** - Cognos Framework Manager model (525K lines, 1646 query subjects, embedded SQL joins)
4. **~/pds/models/cognos** - Shows how cognos_obt was created
5. **Git history** - Version control for all Report XML changes

**Runtime execution tracking in main.cognos_obt:**
- duck_id, user_name - who ran the report
- ran_at - when executed
- report_status, error_details - success/failure tracking

## Enterprise Reports Overview

**Scope:** 162 Enterprise reports (is_enterprise='Y')
**Query subjects consumed:** 99 (perfect 1:1 mapping to rview_names)
**Total query subjects defined in model.xml:** 1646 (massive unused metadata)

## Hot Paths (High-Usage Query Subjects)

**Top 5 by report count:**
1. **Organization Hierarchy** - 47 reports, 30 distinct fields
2. **Operating Ledger** - 40 reports, 81 distinct fields
3. **Person Detail** - 27 reports, 12 distinct fields
4. **Student** - 26 reports, 57 distinct fields
5. **Index to FOAPAL** - 24 reports, 10 distinct fields

## Field Explosion Problem

Query subjects exposing far more fields than actually consumed:

**Employee Position:**
- Total fields defined: 172
- High-usage (10+ reports): 8 fields (POSITION, ID, JOB_SUFFIX, TIMESHEET_ORGANIZATION, TIMESHEET_ORGANIZATION_DESC, POSITION_TITLE, NAME, POSITION_END_DATE)
- Waste: 95%
- Consolidation target: ~20-25 fields (core 8 + next tier)

**Operating Ledger:**
- Total: 81 fields
- High-usage (10+ reports): 26 fields
- Waste: 68%

**Transaction History:**
- Total: 65 fields
- High-usage (10+ reports): 18 fields  
- Waste: 72%

## Most Complex Reports

**By field count:**
1. Employee Roster - 242 fields (where CFM join proliferation happens)
2. OA ATB Eligibility Roster - 128 fields
3. Instructional Pro Tem Positions w Budget - 94 fields
4. Student Data with GPA - 84 fields
5. Student Data - 80 fields

## Student Query Subject Top Fields

**High-usage (10+ reports):**
- ACADEMIC_PERIOD (20 reports)
- STUDENT_LEVEL (17)
- ID (15)
- PERSON_UID (12)
- REGISTERED_IND (12)
- PACKED_MAJORS1-4 (10 each)

## Person Detail Query Subject Top Fields

**High-usage:**
- FIRST_NAME (24 reports)
- LAST_NAME (24)
- PREFERRED_FIRST_NAME (19)
- UO_EMAIL_ADDRESS (17)
- CONFIDENTIALITY_IND (16)
- MIDDLE_NAME (11)

## "Shift Left" Consolidation Strategy

Build DuckDB bridge views for top 5 query subjects containing only high-usage field subsets. Consolidate common CFM joins before fragmentation across 100+ reports.

**Targets:**
- Employee Position: 172→25 fields (85% reduction)
- Operating Ledger: 81→26 fields (68% reduction)
- Transaction History: 65→18 fields (72% reduction)

**Next steps:**
- Parse model.xml to extract CFM join patterns
- Identify common joins across query_subjects
- Build consolidated DuckDB views
- Map back to ODSSRC views (~/pds/utils/idr/ioep/**/*.sql)

## Querying cognos_obt

```sql
-- Top query subjects by Enterprise report usage
SELECT query_subject, 
       COUNT(DISTINCT report_path) as report_count,
       COUNT(DISTINCT query_item) as distinct_fields
FROM main.cognos_obt 
WHERE is_enterprise = 'Y'
GROUP BY query_subject
ORDER BY report_count DESC;

-- High-usage fields for specific query subject
SELECT query_item, COUNT(DISTINCT report_path) as report_count
FROM main.cognos_obt
WHERE is_enterprise = 'Y' AND query_subject = 'Employee Position'
GROUP BY query_item
HAVING report_count >= 10
ORDER BY report_count DESC;
```

---

*KB Entry: `user-reference-cognos-lineage` | Category: reference | Updated: 2025-11-21*
