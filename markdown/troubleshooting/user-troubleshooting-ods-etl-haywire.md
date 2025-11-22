---
id: user-troubleshooting-ods-etl-haywire
category: troubleshooting
title: Nightly ETL Failure Recovery via PDS
tags:
- ods
- etl
- troubleshooting
- pds
- oracle
- performance
- disaster-recovery
created: '2025-11-22T13:30:09.915319'
updated: '2025-11-22T13:30:10.453289'
metadata: {}
---

# Nightly ETL Failure Recovery via PDS

Catastrophic failure of nightly Banner ODS ETL processes (ODI mappings) requiring query-heavy analysis to determine reload requirements. Oracle-based investigation would have been impossible/extremely slow. PDS made quick work of analysis and recovery, proving July 17 technical assessment correct and becoming inflection point for grudging internal permission.

## Problem

**Failure:** Bunch of nightly ETL processes (ODI mappings) went haywire

**Recovery requirement:** Query-heavy task to sort out what data needed reloading

**Oracle limitation:** Would have been "impossible" to investigate in Oracle due to query performance

**Timeline pressure:** Nightly processes = daily business impact, required fast resolution

## Solution: PDS Analysis

**PDS capabilities leveraged:**
- Fast query performance (Parquet columnar storage vs. Oracle row-based)
- DuckDB analytical query engine
- Ad-hoc investigation without impacting production Oracle

**Outcome:** "Made quick work" of identifying reload requirements

## Context: July 17 Incident Vindication

**July 17, 2024:** Frustrated in Teams chat after being asked to investigate ODS issue

**Brock's assessment:**
- Investigation would take all day
- Due to "slow nature of ODS"
- Should be using DBT instead
- Unclear expectations on roles/responsibilities
- "I agree that I can be frustrating to have to use inferior tools in this role"

**Travis/team interpretation:** Emotional reaction, insubordination, not using "official tooling"

**Reality proven:** When nightly ETL actually went haywire, Brock's assessment correct - PDS/DBT approach essential to recovery

## Inflection Point

**Before this failure:**
- PDS completely shut down except personal use
- HR disciplinary letter (Sept 2024)
- Team rift from manufactured complaint

**After this failure (and ODS 9.2 migration disaster):**
- Travis grudging permission for PDS use
- Constraint: "Internal system health monitoring, quality control, testing metrics"
- Still forbidden: "Any piece of data that goes to our users cannot come from PDS platform"

**What changed:** Catastrophic failures made PDS utility undeniable, but containment maintained via production data restriction

## Related Failures

**ODS 9.2 migration disaster:**
- 5 years of source control drift from 2019 Travis decision
- Lost track of modifications
- PDS re-established proper devops flow
- See user-issue-pds-source-control-negligence

**Both failures:** Management decisions/negligence created problems PDS solved

## Technical Lesson

**Query performance matters for operational recovery:**
- Not just nice-to-have for analytics
- Critical for incident response and troubleshooting
- Oracle row-based storage slow for analytical queries
- Parquet columnar + DuckDB fast for investigation patterns

**"Inferior tools" assessment validated:** July 17 frustration not insubordination but accurate technical assessment proven by subsequent failures

## Political Lesson

**Being right creates vulnerability:**
- Proved technical approach superior
- Exposed management incompetence
- Made essential to disaster recovery
- Still constrained from production use

**Utility ≠ adoption:** Even when proven essential, institutional resistance maintains constraints if solution contradicts leadership roadmap

## Current State

**PDS role:** Allowed for internal monitoring/QC/testing only

**Nightly ETL:** Presumably stable (not mentioned as ongoing issue)

**Investigation capability:** PDS available for future failures within allowed scope

**Constraint unchanged:** Production data delivery to users still forbidden despite disaster recovery validation

---

*KB Entry: `user-troubleshooting-ods-etl-haywire` | Category: troubleshooting | Updated: 2025-11-22*
