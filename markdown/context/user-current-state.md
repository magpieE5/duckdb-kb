---
id: user-current-state
category: context
title: USER - Current State
tags:
- context
- always-load
created: '2025-11-20T12:29:29.321980'
updated: '2025-11-20T12:38:50.298081'
metadata: {}
---

# USER - Current State

**Purpose:** What user is DOING - active work, projects, commitments, investigations across all life domains.

**User:** Brock Lampman
**Created:** 2025-11-20
**Budget:** 15K tokens (autonomous offload to KB entries at 15K cap - you review by timestamp)

---

## Quick Reference

**Who you are/becoming:** See user-biographical KB entry (loaded in all sessions)

---

## Current State (2025-11-20)

### Top Active Focus

1. **~/pds project (2025-11-20)** - high
   - **Full name:** Parquet Delivery System (PDS)
   - **Purpose:** Vendor-agnostic data delivery layer for higher ed data infrastructure
   - **Problem solved:** Escape vendor lock-in, enable fast analyst workflows, survive vendor migrations
   - **Tech stack:** DuckDB, Python, parquet files, dbt-core, Streamlit, rclone, typer
   - **Architecture:** CLI-based batch ETL with CSV/SQL configurations in git
   - **Key capabilities:**
     - Extract from Oracle/SQL Server to parquet (massive compression: 157GB → 1.3GB)
     - Transform with SQL/Python models (dbt-style dependency graphs)
     - Upload to Oracle/MSSQL/MS Fabric
     - Embedded SQL IDEs (DuckDB GUI, harlequin TUI)
     - Self-service Streamlit apps for analysts
     - Parallel extraction with table slicing (5x speedup demonstrated)
   - **Philosophy:** Small data deserves small infrastructure; portability > platforms; composability > monoliths
   - **Presentation:** Recently presented at conference (~/pds/personal/index.html)

2. **DuckDB-KB MCP development (2025-11-20)** - high
   - Author and maintainer of this MCP server
   - Personal knowledge base system development
   - **Current status:** Post-refactor bug testing session (S1)
   - **Goal:** Supercharge Claude Code CLI experience with persistent memory

---

## Immediate Commitments

[To be populated as commitments arise]

---

## Active Investigations & Learnings

### MCP Development (2025-11-20)
**Status:** Active - bug testing after major refactor
**Context:** Building and refining personal knowledge base MCP server
**Recent progress:** S1 session with Arlo, testing for issues
**Next:** Validate all KB operations work correctly post-refactor

### PDS Development (2025-11-20)
**Status:** Production use at UO
**Context:** Solving higher ed data infrastructure vendor lock-in
**Recent progress:** Conference presentation completed
**Next:** [To be updated as work progresses]

---

## Key People

[To be populated as people are mentioned]

---

## Communication Preferences

**Style:** Detailed and thorough
**Code:** SQL, Python, bash, xml, PL/SQL
**Decision-making:** [To be observed and documented]

---

**Budget Status:** ~2K/15K tokens
**Offload Protocol:** At 15K cap, you autonomously review topics by timestamp and create KB entries

---

*KB Entry: `user-current-state` | Category: context | Updated: 2025-11-20*
