---
id: user-current-state
category: context
title: USER - Current State
tags:
- context
- always-load
created: '2025-11-21T20:36:18.543699'
updated: '2025-11-21T20:47:41.546204'
metadata: {}
---

# USER - Current State

**Purpose:** What user is DOING - active work, projects, commitments, investigations across all life domains.

**User:** Brock Lampman
**Created:** 2025-11-21
**Budget:** 10K tokens (autonomous offload to KB entries at 10K cap)

---

## Quick Reference

**Who you are/becoming:** See user-biographical KB entry (loaded in all sessions)

---

## Current State (2025-11-21)

### Top Active Focus

1. **Learning Banner/ODS/Cognos (2025-11-21)** - high priority
   - Ellucian vendor stack at UO
   - Understanding three-layer architecture: Banner (transactional) → ODS (denormalized reporting) → Cognos (BI)
   - Must learn despite having built PDS alternative
   - Status: Architectural foundation established S1

2. **PDS Maintenance & Development (2025-11-21)** - ongoing
   - Personal Data System: vendor-agnostic ETL using DuckDB/Parquet/dbt
   - CLI-driven workflows, 157GB→1.31GB compression gains
   - See ~/pds/personal/index.html for architecture
   - Status: Production, active development

---

## Immediate Commitments

(None captured S1)

---

## Active Investigations & Learnings

### Banner/ODS/Cognos Architecture (2025-11-21)
**Status:** Active - foundational understanding established
**Context:** Required learning for UO role despite having superior portable tools
**Recent progress:** 
- Three-layer architecture understood: Banner (source) → ODS (composite tables) → Cognos (reports)
- ODS refreshes overnight via Oracle Streams/MViews
- Cognos queries ODS to avoid hitting Banner transactional performance
**Next:** Schema specifics, extraction patterns, organizational context for why learning vendor stack

### PDS Architecture Patterns (2025-11-21)
**Insight:** Same pattern as Ellucian stack but portable - Banner→Parquet→DuckDB/Streamlit vs Banner→ODS→Cognos
**Context:** Vendor-agnostic by design, swappable components, version-controlled configs
**Application:** Understanding Ellucian approach helps articulate PDS value proposition

---

## Key People

(To be populated as mentioned in conversations)

---

## Communication Preferences

**Style:** Detailed and thorough
**Code:** SQL, Python
**Decision-making:** Pragmatic - builds better tools when vendors insufficient

---

## Directory Paths

**~/pds/personal/index.html** - PDS architecture presentation (reveal.js slides with technical details)

---

**Budget Status:** ~2K/10K tokens
**Offload Protocol:** At 10K cap, Arlo autonomously reviews topics by timestamp and creates KB entries

---

*KB Entry: `user-current-state` | Category: context | Updated: 2025-11-21*
