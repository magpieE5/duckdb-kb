---
id: user-reference-odi-architecture
category: reference
title: Oracle Data Integrator (ODI) Architecture for Banner ODS
tags:
- odi
- oracle
- banner-ods
- etl
- uo-work
- architecture
created: '2025-11-21T21:18:03.392753'
updated: '2025-11-21T21:18:03.392753'
metadata: {}
---

# Oracle Data Integrator (ODI) Architecture for Banner ODS

Oracle Data Integrator (ODI) is the ETL tool used in Banner ODS environments at University of Oregon. Understanding the component architecture is essential for ETL development work.

## Core Components

### 1. ODI Repository (Database Layer)

**Master Repository** (single, shared):
- Security information (user profiles, roles, privileges)
- Topology information (server definitions, technology connections)
- Version control for all ODI objects

**Work Repository** (multiple: dev/test/prod):
- Data models (source/target metadata, schema definitions)
- Projects (ETL logic: mappings, packages, procedures, variables)
- Execution logs and scenarios
- Relationship: One-to-many (one Master, multiple Work repos)

### 2. ODI Studio (Java-based IDE)

Four navigators for different roles:

**Designer Navigator:**
- Build transformations and data integrity checks
- Reverse-engineer existing databases/applications
- Graphical development of interfaces/mappings

**Operator Navigator:**
- Monitor production jobs and sessions
- View execution logs
- Manage scenarios

**Topology Navigator:**
- Configure connections to source/target systems
- Manage physical and logical architecture

**Security Navigator:**
- Manage user access and permissions

### 3. Execution Agents

- Java-based runtime engines
- Read ETL instructions from Work Repository
- Execute transformations against source/target databases
- Can be deployed standalone or in Java EE containers (WebLogic)

### 4. ODI Console

- Web-based UI for read-only access and operations
- Alternative to ODI Studio for monitoring and basic operations

## Banner ODS Specific Components

### ODSMGR Schema
- Primary schema in Banner ODS database (pre-8.2)
- Contains denormalized composite tables for reporting

### Composite Tables
- Flattened reporting tables combining many normalized Banner tables
- Constructed specifically for analytics and reporting
- Examples: Student composites, Employee composites, Receivable Customer composites

### Staging Mechanism
Two options for data extraction:
- **Oracle Streams** - Change data capture
- **Materialized Views** - Snapshot-based replication

## ETL Flow Architecture

```
Banner (Source) 
  ↓
Oracle Streams/Materialized Views
  ↓
Banner ODS Staging
  ↓
ODI Mappings/Packages (pipeline objects)
  ↓
Composite Tables (ODSMGR schema)
```

## What Are "Pipeline Objects"?

Pipeline objects in Banner ODS context are:
- ODI mappings (data flow diagrams)
- ODI packages (orchestration logic)
- Located in Designer Navigator
- Move data from staging into composite tables
- Include transformations, business rules, data quality checks

## Key Concepts

**Knowledge Modules (KMs):**
- Reusable templates for common ETL patterns
- Loading Knowledge Modules (LKMs), Integration Knowledge Modules (IKMs), Check Knowledge Modules (CKMs)

**Scenarios:**
- Compiled, production-ready versions of mappings/packages
- Can be scheduled and executed by agents

**Sessions:**
- Runtime execution instances of scenarios
- Generate logs viewable in Operator Navigator

## References

- [Understanding Oracle Data Integrator](https://docs.oracle.com/en/middleware/fusion-middleware/data-integrator/12.2.1.3/odiun/overview-oracle-data-integrator.html)
- [Oracle Data Integrator Component Architecture](https://www.kpipartners.com/blogs/oracle-data-integrator-component-architecture)
- [Banner Operational Data Store Handbook](https://tech.wayne.edu/depdocs/banner-ods-handbook-8-4.pdf)
- [Types of Oracle Data Integrator (ODI) Repositories](https://blogs.perficient.com/2014/09/04/types-of-oracle-data-integrator-odi-repositories/)

## Next Steps for Learning

1. Get access to ODI Studio at UO
2. Explore Designer Navigator to see actual Banner ODS mappings
3. Review Work Repository to understand project structure
4. Run test scenarios in Operator Navigator to see execution flow
5. Study existing composite table definitions in ODSMGR schema

---

*KB Entry: `user-reference-odi-architecture` | Category: reference | Updated: 2025-11-21*
