---
id: arlo-reference-banner-ods-architecture
category: reference
title: Banner ODS Architecture Understanding
tags:
- arlo-learning
- web-research
- banner
- ods
- architecture
- ellucian
created: '2025-11-21T13:03:05.291860'
updated: '2025-11-21T13:03:05.291860'
metadata: {}
---

# Banner ODS Architecture Understanding

**Source:** Web search (2025-11-21)

Ellucian Banner ODS (Operational Data Store) sits between transactional Banner ERP and reporting/analytics tools. Denormalized, reporting-optimized data structures.

**Architecture:**
- **Source:** Banner ERP (transactional, OLTP)
- **Replication:** Oracle Streams or Materialized Views framework
- **Target:** ODS database with ODSMGR schema
- **Refresh:** Overnight incremental refreshes (institution-defined schedule)
- **Consumers:** Cognos reports, analytics tools

**Layered structure:**
- Staging Area: Contains staging tables, change tables, triggers, comp views
- ODS Layer: ODSMGR schema with denormalized composite tables/views
- EDW Layer: Enterprise data warehouse (longer-term analytics)

**ODSMGR Schema:**
- Contains composite tables representing conceptual organizational structures
- Subject areas include: Schedule Offering, Student Course, etc.
- Views created and maintained in ODSMGR, accessed via database links

**Student/Course relevant tables:**
- Banner source: SCBCRSE, SCBCRKY, SCRLEVL, SCRGMOD, SCRSCHD
- ODS composites: MST_COURSE_PREREQ, MST_OFFERING_PREREQ
- ODS views: COURSE_PREREQ, OFFERING_PREREQ, schedule_offering (exact name varies)

**Implications for troubleshooting:**
- Data discrepancies between Banner and ODS likely due to: stale refresh, ETL bugs, data corruption, historical retention policies
- Example: Students registered for non-existent courses = ODS has student enrollment data but missing corresponding schedule offering record
- Could indicate: deleted course in Banner but stale in ODS, partial ETL failure, referential integrity issue

**Relevance:** When Brock troubleshoots "students in courses that don't exist", this is the architecture context - understanding whether issue is Banner source data vs ODS ETL vs ODS staleness.


---

*KB Entry: `arlo-reference-banner-ods-architecture` | Category: reference | Updated: 2025-11-21*
