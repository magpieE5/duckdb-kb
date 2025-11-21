---
id: user-current-state
category: context
title: USER - Current State
tags:
- context
- always-load
created: '2025-11-21T09:59:13.072701'
updated: '2025-11-21T10:53:41.296340'
metadata: {}
---

# USER - Current State

**Purpose:** What user is DOING - active work, projects, commitments, investigations across all life domains.

**User:** Brock Lampman
**Created:** 2025-11-21
**Budget:** 15K tokens (autonomous offload to KB entries at 15K cap - you review by timestamp)

---

## Quick Reference

**Who you are/becoming:** See user-biographical KB entry (loaded in all sessions)

---

## Current State (2025-11-21)

### Top Active Focus

1. **IDR-3771: Banner ODS schedule_offering data quality issue (2025-11-21)** - high priority
   - Student registrations exist but courses missing from schedule_offering view
   - CRN 26776 (term 202502) reported by Tom Johnston from CAS academic unit
   - Root cause identified: MSVGVC1 INNER JOIN filtering
   - Next: Extract Banner source tables via PDS to validate diagnosis

2. **duckdb-kb MCP development (2025-11-21)** - high priority
   - Entity-mode knowledge base with persistent memory and autonomous evolution
   - Sole developer, recently completed core functionality
   - Status: S1 complete, testing real-time logging protocols
   - Discovered execution gap: need formulaic triggers for KB creation

3. **Home/property improvement (2025-11-21)** - ongoing
   - Active property maintenance and improvement projects
   - Personal focus area

4. **Ellucian Banner ODS/Cognos work (2025-11-21)** - professional
   - Primary work focus at UO Information Services
   - ETL development and data warehouse operations

**Note:** All topics include timestamp (YYYY-MM-DD) for age tracking. Update timestamp when topic revisited.

---

## Immediate Commitments

- [ ] **IDR-3771: Run PDS extraction and validate diagnosis (2025-11-21)** - high priority, Tom Johnston waiting
- [ ] **Update real-time logging protocols based on S1 learnings (2025-11-21)** - high priority
- [ ] **Continue MCP testing and refinement (2025-11-21)** - ongoing

---

## Active Investigations & Learnings

### IDR-3771: Missing Schedule Offerings (2025-11-21)
**Status:** Diagnosis complete, validation pending
**Context:** Student course registrations exist in SFRSTCR but courses don't appear in SCHEDULE_OFFERING view
**Root cause:** MSVGVC1 view uses INNER JOINs to MSV_COURSE_CATALOG - courses not in catalog are filtered out
**Next steps:** 
- Extract 24 Banner source tables via PDS (_ora_manual.csv populated)
- Query to confirm CRN 26776 exists in SSBSECT
- Check if course exists in SCBCRSE catalog for term 202502
- Identify patterns: are missing CRNs lacking catalog entries?
- Determine if special course types (independent study, thesis) involved

### duckdb-kb MCP Real-Time Logging (2025-11-21)
**Status:** Active refinement
**Context:** S1 revealed execution gap - deferred KB creation to /sm instead of real-time logging
**Recent progress:** 
- Identified need for formulaic triggers (topic change, architecture discovery)
- Proposed pre-send enforcement checklist
- Clarified /sm as safety net, not primary KB mechanism
**Next:** Update protocols with explicit content-type gates and timing rules

---

## Key People

**Tom Johnston:** Requester for IDR-3771 ticket, CAS academic unit contact

---

## Communication Preferences

**Style:** Detailed and thorough
**Code:** PL/SQL, Python, bash
**Decision-making:** Pragmatic, systems-focused

---

**Budget Status:** ~3K/15K tokens
**Offload Protocol:** At 15K cap, you autonomously review topics by timestamp and create KB entries

---

*KB Entry: `user-current-state` | Category: context | Updated: 2025-11-21*
