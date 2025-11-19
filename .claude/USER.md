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

1. **Banner ODS/Cognos Data Engineering** (HIGH, work)
   - Daily forensics on Oracle data, Cognos Framework Manager packages, Cognos Reports, IA_ADMIN/ODI transformations
   - Stakeholder engagement with Banner Developers and external customers
   - Details in USER-WORK.md

2. **PDS & duckdb-kb Development** (HIGH, work)
   - Built ~/pds to address Oracle ODS performance issues (sole author)
   - Built ~/duckdb-kb MCP (sole author, this project)
   - Collaborating with Jesse Sedwick on ~/jesse/obsidian-mcp-server
   - Details in USER-WORK.md

3. **Winter Property Preparation** (MEDIUM, personal)
   - 11-acre property in south Eugene, Oregon
   - Generator research and purchase, well inspection, pest exterminator, shop organization
   - Details in USER-PERSONAL.md

### Current Mode Context
**Work:** University of Oregon Information Services (central IT), data engineering on Ellucian Banner ecosystem
**Personal:** Family life with Megan (wife), Laser (7), Rowan (12), pets (Daisy, Matilda, 6 chickens); running and guitar hobbies need more attention

See USER-WORK.md for full work context, USER-PERSONAL.md for family/life, USER-BIO.md for stable biographical patterns.

---

## Immediate Commitments

**Work:**
- Continue collaboration with Jesse Sedwick on obsidian-mcp-server
- Daily Banner ODS/Cognos forensics and stakeholder support

**Personal:**
- Research and purchase generator (winter prep)
- Schedule well inspection
- Arrange pest exterminator visit
- Organize shop on property

---

## Recent Insights (Last 7 Days)

**CRITICAL:** Add ALL recent insights here (work AND personal) until file hits ~2K. Primary boundary is temporal (recent vs historical), not domain (work vs personal).

**2025-11-18 (work):** Built markdown-to-confluence git pre-push hook for Jesse Sedwick's obsidian-mcp-server collaboration. Integrating markdown-based workflows with Confluence publishing.

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

**Style:** Detailed and thorough explanations preferred
**Code:** Python, SQL, TypeScript (MCP development); pragmatic solutions over perfection
**Decision-making:** Data-driven pragmatist; values technical accuracy and evidence-based choices

---

**Budget Status:** ~2K/2K tokens (lightweight by design)
**Domain details:** Managed in specialized files with 9K budgets each
**Compression:** Domain files compressed independently at 9K trigger
