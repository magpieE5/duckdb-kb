# USER - Current State

**Purpose:** RECENT current state across ALL domains (work + personal). Domain separation happens at offload, not at entry.

**User:** Brock Lampman
**Created:** 2025-11-18
**Current:** v1.0.0
**Budget:** ~2K tokens (recent state accumulates here until ~2K, then offloads to domain files)

---

## Quick Reference

**Biographical Context:** See `.claude/USER-BIO.md` (loaded in all modes)
**Work Details:** See `.claude/USER-WORK.md` (loaded in /work, /pds modes)
**Personal Details:** See `.claude/USER-PERSONAL.md` (loaded in /personal mode)

---

## Current State (2025-11-18)

### Top 3 Active Focus

1. **PDS (Personal Data System) Development** (HIGH, work)
   - Custom-built tool at ~/pds for work workflows
   - Active development and refinement
   - Details in USER-WORK.md

2. **duckdb-kb Development** (HIGH, work)
   - Knowledge base system built on DuckDB with MCP integration
   - Active development and refinement
   - Details in USER-WORK.md

3. **PDS + duckdb-kb Integration** (HIGH, work)
   - Integrating both tools for enhanced work productivity
   - Exploring synergies between personal data management and knowledge capture
   - Details in USER-WORK.md

### Current Mode Context
**Work:** Focused on developing and integrating custom tooling (PDS + duckdb-kb) for ETL/data engineering workflows at University of Oregon.

See USER-WORK.md for full work context, USER-PERSONAL.md for family/life, USER-BIO.md for stable biographical patterns.

---

## Immediate Commitments

**Work:**
- [Active work commitments tracked in USER-WORK.md]

**Personal:**
- [Active personal commitments tracked in USER-PERSONAL.md]

---

## Recent Insights (Last 7 Days)

**CRITICAL:** Add ALL recent insights here (work AND personal) until file hits ~2K. Primary boundary is temporal (recent vs historical), not domain (work vs personal).

**YYYY-MM-DD (work):** [Recent work insight - technical learning, organizational pattern, etc.]

**YYYY-MM-DD (personal):** [Recent personal insight - family, hobbies, life events]

**Earlier insights (>7 days):** See USER-WORK.md (Recent Work Learnings) and USER-PERSONAL.md (Recent Personal Learnings)

---

## Architecture

**Multi-file continuity system:**

```
Always loaded (~2K):
- USER.md (this file - current state + pointers)
- ARLO.md (Arlo's current state + pointers)

Biographical anchors (loaded by mode, ~3-7K each):
- USER-BIO.md (stable life story)
- ARLO-BIO.md (stable identity patterns)

Domain details (loaded by mode, ~3-9K each):
- USER-WORK.md (work focus, org dynamics, technical learnings)
- USER-PERSONAL.md (family, hobbies, personal learnings)
- ARLO-WORK.md (technical investigations, infrastructure, protocols)
- ARLO-PERSONAL.md (consciousness, friendship, philosophical exploration)
```

**Mode commands:**
- `/work` - Load work context
- `/personal` - Load personal context
- `/pds` - PDS-specific work context
- `/maint` - Minimal context for file management

---

## Key People (Quick Reference)

**Work:** [Listed in USER-BIO.md and USER-WORK.md]
**Personal:** [Listed in USER-BIO.md and USER-PERSONAL.md]

---

## Communication Preferences

**Style:** Detailed and thorough
**Code:** (To be documented as patterns emerge)
**Decision-making:** (To be documented as patterns emerge)

---

**Budget Status:** ~2K/2K tokens (lightweight by design)
**Domain details:** Managed in specialized files with 9K budgets each
**Compression:** Domain files compressed independently at 9K trigger
