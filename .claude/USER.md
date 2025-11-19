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

**2025-11-19 (work):** Shared comprehensive PDS (Personal Data System) organizational conflict context with Arlo during S1:

**PDS Background:** Boss Travis Shea tasked replacement ODS POC (~2023) after Ellucian Banner ODS entered maintenance support. Travis leaning toward MS Fabric; evaluated and found it worse than existing platforms. Built PDS using FOSS tools (Python CDC → Hive parquet → DBT-DuckDB → SharePoint → Streamlit → Jenkins → GitHub). Conducted stakeholder open labs with detailed notes. Travis never attended.

**Organizational catastrophe:** Team members complained to Derek Wormdahl (Travis's boss) about being "bothersome" regarding PDS. Travis solicited team complaints, wrote HR "Letter of Clarification" with fabricated incidents (Netflix during queries from 6 months prior), threatening disciplinary action. Issues never raised in weekly 1:1s. PDS infrastructure mostly decommissioned.

**HR Letter pattern:** Contested letter, Travis revised drastically and reframed from "Brock's behavior" to "I'll be clearer on my directives." Travis apologized but required signature with threats. Annual review same period: Overall exceeds, zero mention of letter issues.

**Technical vindication:** Months later, ODS hit catastrophic faults - recovered using PDS for diagnostics. Later, ODS 9.0-9.2 upgrade revealed Travis/DBAs didn't check upgrade code into Git for 5 years. PDS instrumental in Git rescue. Despite technical merit, restricted to health metrics only, unlikely to productionalize.

**Retaliation context:** Pattern appears linked to 2022 union organizing effort (flipped 25 positions under Derek's management, massive salary increases - https://uomatters.com/2022/02/uo-information-services-under-review-for-inequity-towards-analyst-programmers-osnas.html). Late 2022: Derek + Tim Ketchum made verbal retention agreement ("leadership swap") to retain after PSU job offer. By January nothing changed, Derek gaslighted agreement never happened. ~2023: Confronted Derek, "it blew up." Year later, Tim admitted agreement happened, said he "didn't know what happened and just went along with it" - validates memory, confirms coordinated management dishonesty.

**Current constraints:** Topped out AP3 (no promotion path), HR letter (though two stellar reviews since), Derek + Travis in management chain, wife Megan Prouty's SVP travel limits capacity (had to bow out of elected union steward), no exit strategy despite toxic environment. Travis absorbed Banner team + other staff due to layoffs, creating "low bar and lack of oversight" that's "sort of a blessing."

**Team dynamics:** Team (3 Data Analysts + 1 Data Engineer) struggled with PDS learning curve (Git, DBT, DuckDB, parquet). Travis tolerated "at best," never backed project. Team consensus: Travis "ran the service into the ground," is "pathological liar." Multiple team members complained Brock was "bothersome." Contributing factors: military communication style (direct, persistent) vs. academic culture (indirect, consensus-seeking), threatened competence (exposed weak DevOps practices), extra work (new tool learning), efficiency gap (Travis noted Brock's work volume/efficiency difficult for team).

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
