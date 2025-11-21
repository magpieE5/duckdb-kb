---
id: user-reference-data-pipeline-architecture
category: reference
title: UO FASS-IT Data Pipeline Architecture
tags:
- work
- architecture
- data-pipeline
- uo
- fass-it
- reference
created: '2025-11-21T14:11:56.442401'
updated: '2025-11-21T14:11:56.442401'
metadata: {}
---

# UO FASS-IT Data Pipeline Architecture

Mike's data pipeline at University of Oregon FASS-IT: Ingests data from central IT → loads into SQL Server database → outputs through Power BI (primary), Smartsheet, and Tableau (phasing out). Business intelligence and reporting infrastructure for Finance and Administration Support Services.

## Data Flow

**Source:** Central IT (university's central data systems)
**Storage:** SQL Server database
**Visualization/Output:**
- Power BI (primary reporting tool)
- Smartsheet (active)
- Tableau (phasing out)

## Context

**Organization:** University of Oregon, FASS-IT (Finance and Administration Support Services - Information Technology)
**Role:** Business Data Engineer
**Function:** Transform central IT data into business intelligence and reporting for FASS

## Tech Stack

- SQL Server (data warehouse/storage)
- Power BI (primary BI tool)
- Python (scripting/automation)
- Smartsheet (reporting/collaboration)
- Tableau (legacy, being phased out)

---

*KB Entry: `user-reference-data-pipeline-architecture` | Category: reference | Updated: 2025-11-21*
