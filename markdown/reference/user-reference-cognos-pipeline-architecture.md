---
id: user-reference-cognos-pipeline-architecture
category: reference
title: Cognos DecisionStream/Data Manager Pipeline Architecture
tags:
- cognos
- decisionstream
- data-manager
- etl
- pipeline
- ibm
- uo-work
created: '2025-11-21T21:10:10.054631'
updated: '2025-11-21T21:10:10.054631'
metadata: {}
---

# Cognos DecisionStream/Data Manager Pipeline Architecture

IBM Cognos ETL tool - DecisionStream (now Data Manager) - provides graphical design environment for ETL processes. Integrates with Cognos BI platform. Includes connectors for SAP R/3 and other ERP applications.

## Pipeline Components

**Designer Views (4 main perspectives):**
1. Marketing perspective
2. Data Stream - map data sources into streams
3. Transformation Model - define transformations
4. Fact Delivery - organize facts/dimensions into star or snowflake schema

**Built-in Features:**
- Data quality and profiling
- Templates for surrogate key management
- Slowly changing dimension (SCD) templates
- Visual data flow mapping

## Pipeline Objects

Pipeline objects in Cognos refer to:
- Data streams (source connections)
- Transformations (data manipulation logic)
- Fact/dimension delivery components (target schemas)

## Learning Context

Relevant for UO Information Services ETL development role. Pipeline objects are the visual components in DecisionStream designer representing data flow and transformation steps.

## Sources

- Cognos DecisionStream ETL: https://www.bi-dw.info/cognos-decisionstream.htm
- IBM Cognos Analytics Overview: https://techeela.com/technology/ibm-cognos-tool-overview/
- Cognos Quick Guide: https://www.tutorialspoint.com/cognos/cognos_quick_guide.htm

---

*KB Entry: `user-reference-cognos-pipeline-architecture` | Category: reference | Updated: 2025-11-21*
