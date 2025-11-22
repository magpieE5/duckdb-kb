---
id: user-reference-banner-ods-architecture
category: reference
title: Banner ODS Architecture Overview
tags:
- banner
- ods
- oracle
- odi
- etl
- architecture
- uo-work
created: '2025-11-21T21:10:10.054631'
updated: '2025-11-21T21:10:10.054631'
metadata: {}
---

# Banner ODS Architecture Overview

Banner Operational Data Store (ODS) by Ellucian - data warehouse accompanying Banner ERP. Uses Oracle Data Integrator (ODI) for ETL pipelines. Architecture includes Oracle database with Ellucian-defined schemas, Linux folder with code tree of stored procedures, and ODI configured to point to university's Banner database. Key procedure: F_RunODIMap verifies scenarios exist in ODI repository, generates unique numbers, inserts into MGTHOST table. Modern integration uses Data Connect Serverless API pipelines calling Banner Business Process APIs (BP API) through Ethos Integration.

## Components

**Database Layer:**
- Oracle database with Ellucian-defined schemas
- Composite tables for reporting
- Changed objects tracking

**ETL Layer:**
- Oracle Data Integrator (ODI) - primary ETL tool
- F_RunODIMap procedure for scenario management
- ODI repository for transformation logic

**Integration Layer:**
- Data Connect Serverless API pipelines
- Banner Business Process APIs (BP API)
- Ethos Integration for API calls

**Code Layer:**
- Linux folder containing code tree
- Stored procedures for data transformations

## Learning Context

Relevant for UO Information Services ETL development role. Pipeline objects in ODI are data flows, transformations, and mappings defined in graphical designer.

## Sources

- Banner ODS 9.0 Release Guide: https://irda.wayne.edu/educational_resources/banner_ods_9_0_release_guide.pdf
- Katie Kodes - How Banner ODS Works: https://katiekodes.com/pages/blogdrafts/draft-2021-05-25-banner-ods/
- Oracle ODI Licensing: https://support.oracle.com/knowledge/Middleware/2481226_1.html

---

*KB Entry: `user-reference-banner-ods-architecture` | Category: reference | Updated: 2025-11-21*
