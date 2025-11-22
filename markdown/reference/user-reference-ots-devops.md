---
id: user-reference-ots-devops
category: reference
title: OTS - Database DevOps Pipeline (Git/Jenkins)
tags:
- ots
- devops
- git
- jenkins
- oracle
- appworx
- reference
created: '2025-11-22T12:05:38.308273'
updated: '2025-11-22T12:05:38.308273'
metadata: {}
---

# OTS - Database DevOps Pipeline (Git/Jenkins)

Home-grown solution for versioning, deployment, and promotion of database objects and AppWorx executables. Used by ~10 staff for enterprise applications and integrations. Replaced legacy Oracle Forms-based OTS (circa 2000) that was sunsetted.

## Architecture

**Components:**
- **BitBucket (Git)** - Version control
- **Jenkins (Bash/Groovy)** - CI/CD orchestration
- **Oracle Database** - Target deployment environment
- **AppWorx** - Job scheduling/execution

**Scope:** Enterprise applications spanning HR, Finance, Payroll, Registrars, Admissions, Financial Aid

## Implementation History

**Context:** Internal project to replace Oracle Forms-based OTS when Forms was sunsetted

**Brock's role:** Solely performed:
- Analysis and design
- Implementation
- Migration from legacy system
- Documentation
- Training
- Ongoing maintenance and end-user support

**Collaboration:** Worked with Middleware and DBAs during development

## Current Status (2025-11-22)

**Still primary devops for:**
- ODS/Cognos code
- Oracle database objects
- Banner integrations
- Enterprise application deployments

**Shift in usage:** Brock using less as workflow transitions to PDS. OTS remains official pipeline for department, but Brock's personal workflow increasingly PDS-centric.

## Related Systems

**Banner Admin:** Web app (Maven Java MVC) using vendor extensibility. Brock developed versioning, standardized IDEs, deployment, promotion, upgrades, and migration with Middleware support. Continues supporting during Banner seasonal upgrades.

**Banner Self-Service 9 (DuckWeb):** Groovy/Grails web app (Gradle projects, Git submodules). Brock performed majority of internal refactoring to expedite development and upgrades from legacy PLSQL-generated HTML version.

## Technical Context

Part of dual infrastructure pattern:
- **Legacy official:** OTS/Jenkins/Oracle/AppWorx for departmental work
- **Future personal:** PDS for Brock's workflow transition

See user-reference-pds-overview for modern alternative architecture.

---

*KB Entry: `user-reference-ots-devops` | Category: reference | Updated: 2025-11-22*
