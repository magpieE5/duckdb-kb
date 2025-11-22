---
id: user-current-state
category: context
title: USER - Current State
tags:
- context
- always-load
created: '2025-11-21T21:44:23.154524'
updated: '2025-11-21T23:05:16.927724'
metadata: {}
---

# USER - Current State

**Purpose:** What user is DOING - active work, projects, commitments, investigations across all life domains.

**User:** Brock Lampman
**Created:** 2025-11-21
**Budget:** 10K tokens (autonomous offload to KB entries at 10K cap - you review by timestamp)

---

## Quick Reference

**Who you are/becoming:** See user-biographical KB entry (loaded in all sessions)

---

## Current State (2025-11-21)

### Top Active Focus

1. **Data quality issues in Ellucian Banner ODS/Cognos (2025-11-21)** - high priority
   - Sole developer of PDS (Personal Data System) at ~/pds
   - Vendor-agnostic data delivery layer using DuckDB/Parquet/dbt
   - Extracting from Oracle/MSSQL, transforming locally, distributing across platforms
   - Current focus: Cognos metadata lineage archaeology
   - See presentation at ~/pds/personal/index.html for full context

2. **Cognos → Banner lineage reconstruction (2025-11-21)** - active investigation
   - 162 Enterprise reports, 99 query subjects, identifying consolidation opportunities
   - Field explosion problem: Employee Position 172 fields, only 8 high-usage (95% waste)
   - Building "shift left" DuckDB bridge views for top 5 query subjects
   - Full continuity substrate: ~/pds/utils/idr/cognos_reports/ (Report XML), main.cognos_obt (runtime/usage)

3. **DuckDB knowledge base MCP development (2025-11-21)** - ongoing
   - Private KB system for personal + AI entity continuity
   - This is our "little secret" - not building for broader adoption
   - Grant access: ~/pds/utils/_pds.duckdb for Cognos work

**Note:** All topics include timestamp (YYYY-MM-DD) for age tracking. Update timestamp when topic revisited.

---

## Immediate Commitments

- No explicit commitments documented yet

---

## Active Investigations & Learnings

### Cognos Enterprise Report Consolidation (2025-11-21)
**Status:** Active
**Context:** 162 Enterprise reports showing massive field redundancy across query subjects. Building DuckDB views to consolidate common patterns before CFM fragmentation.
**Recent progress:** Quantified consolidation targets - Employee Position (172→25 fields), Operating Ledger (81→26), Transaction History (65→18)
**Next:** Parse model.xml for CFM join patterns, identify shared consumption patterns

### PDS Architecture Evolution (2025-11-21)
**Insight:** Vendor-agnostic infrastructure allows weathering transitions (Cognos migration, ODI changes, platform shifts)
**Context:** Not advocating dropping vendors, but maximizing ROI and weathering transitions through portable formats (Parquet) and composable tools

---

## Key People

**Work context:** University of Oregon, Information Services
**Personal:** Lives on 11 acres in S. Eugene, kids, enjoys guitar and running

---

## Communication Preferences

**Style:** Detailed and thorough
**Code:** SQL, Python
**Decision-making:** Pragmatic, vendor-agnostic, composability over monoliths

---

**Budget Status:** ~3K/10K tokens
**Offload Protocol:** At 10K cap, you autonomously review topics by timestamp and create KB entries

---

*KB Entry: `user-current-state` | Category: context | Updated: 2025-11-21*
