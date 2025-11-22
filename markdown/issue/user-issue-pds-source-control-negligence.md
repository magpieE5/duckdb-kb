---
id: user-issue-pds-source-control-negligence
category: issue
title: Banner ODS Source Control Negligence - 5 Years of Drift
tags:
- banner
- ods
- source-control
- negligence
- devops
- migration
- issue
created: '2025-11-22T13:30:09.915319'
updated: '2025-11-22T13:30:09.915319'
metadata: {}
---

# Banner ODS Source Control Negligence - 5 Years of Drift

2019 decision by Travis (then ODS/Cognos manager, now Associated Director) not to check vendor code into repository during Banner ODS 9.0 upgrade, creating 5 years of untracked drift where bug fixes unknowingly reverted production from 9.0 to 8.5. PDS instrumental in recovery during forced 9.2 upgrade, exposing management incompetence.

## Background

**Travis's history with ODS:**
- 2012-2015: Travis and Brock both ETL Developers, worked side-by-side
- 2015+: Travis became manager of ODS/Cognos team
- 2019: Travis managed ODS 9.0 upgrade
- 2019-2024: Brock in Banner Developer role, then back to ETL Developer

**Shared competency baseline:**
- Both had metadata publishing capability 2012-2015 (push HTML to Tomcat)
- Both understood source control workflows
- Not rocket science, standard devops practice

## The 2019 Decision

**ODS 9.0 upgrade:**
- Travis migrated from 8.5 to 9.0
- Did NOT check all vendor code into repository
- Documented decision but did not tell Brock or team when Brock returned to role

**Impact:**
- Repository showed 8.5 baseline
- Production running 9.0 modified
- No one knew vendor code didn't match repo

## 5 Years of Drift (2019-2024)

**Brock's workflow (unknowingly broken):**
1. Check out prod branch (thinking it's 9.0 baseline)
2. Make bug fix or feature change
3. Commit and deploy
4. **Unknowingly reverting production from 9.0 modified to 8.5 modified**

**Compounding problems:**
- Published metadata stuck at 8.5 (users seeing wrong documentation)
- Metadata complaints "one of the most common things users complain about"
- Travis claimed team "lost the competency" to publish metadata
- Reality: Wasn't complicated (HTML to Tomcat), capability existed 2012-2015

**5 years of accumulated drift** made true state of modifications unknowable.

## Forced Reckoning: 9.2 Upgrade

**Migration project: ODS 9.0 → 9.2+10 patches**

**Challenge:** Lost track of what modifications even were due to:
- Vendor code not in repo (2019 decision)
- 5 years of unknowing reversions (8.5←→9.0 flip-flopping)
- Published metadata stuck at 8.5
- No source of truth for actual production state

**PDS role in recovery:**
- Re-established proper devops source → compile → deploy flow
- Made "quick work" of query-heavy analysis impossible in Oracle
- Proved July 17 assessment correct (DBT faster than ODS for investigation)

**Brock's reaction:**
- "Hard to contain my sense of how gross negligence this was on Travis's part"
- Vindication of technical approach Travis had threatened discipline over

## Pattern Recognition

**Management incompetence exposure:**
- 2019 decision created problem
- 2024 problem forces reckoning
- PDS solves problem Travis's approach created
- Being right = the threat

**"Lost competency" framing:**
- Deflects from 2019 decision
- Claims team forgot how to do simple task (HTML to Tomcat)
- Both Travis and Brock had this competency 2012-2015
- Not credible technical explanation

**Why PDS became threatening:**
- Proved technical approach superior (query performance, analysis capability)
- Exposed source control negligence during recovery
- Contradicted Fabric roadmap Travis committed to
- Made management incompetence visible

## Related Context

- See user-issue-pds-hr-retaliation for HR response to PDS success
- See user-troubleshooting-ods-etl-haywire for other catastrophic failure PDS solved
- See user-reference-ots-devops for proper devops workflow Brock built previously

## Current State

**Metadata publishing:** Presumably restored during 9.2 migration (not confirmed)

**Source control:** Presumably proper state re-established via PDS-assisted recovery

**Lessons learned:** None institutionally - PDS still blocked from production data delivery despite proving essential to disaster recovery

**Strategic impact:** Vindication of technical approach while creating political vulnerability - being right exposed leadership incompetence, triggering containment response

---

*KB Entry: `user-issue-pds-source-control-negligence` | Category: issue | Updated: 2025-11-22*
