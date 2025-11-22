---
id: user-issue-uo-pds-restriction-rationale
category: issue
title: 'UO Management PDS Restriction: Analysis & Implications'
tags:
- organizational-dynamics
- career
- pds
- uo
- management
- security-theater
- vendor-lock-in
created: '2025-11-21T20:08:21.755552'
updated: '2025-11-21T20:08:21.755552'
metadata: {}
---

# UO Management PDS Restriction: Analysis & Implications

University of Oregon management restricts PDS to internal service analysis/forensics only, despite external adoption and demonstrated value. Can measure system performance but cannot deliver production datasets. This is legitimacy vs. visibility problem, not technical security problem.

## Management Position

**Stated concern:** PDS 'encourages or acknowledges data exfiltration'

**Actual concern:** Non-standard stack seen as risk

**History:** Initial block → grudging acceptance through demonstrated value + embedded dependency + outlasted resistance

**Current restriction:** Internal service analysis/forensics only - can analyze Cognos performance degradation, track ODS query patterns, measure infrastructure failures, but cannot deliver datasets that would reduce dependency on approved systems

## Technical Reality

**Before PDS:**
- Analysts export CSVs from Cognos daily
- Email to colleagues, save to local drives, copy to network shares
- Completely ungoverned, no audit trail, scattered everywhere

**With PDS:**
- Centralized extraction with versioned configs
- Reproducible datasets with clear lineage
- Potential for audit logging (who/what/when)
- Oracle grant preservation (if they can query in Banner, they can extract via PDS - no new access granted)

**Analysis:** PDS doesn't 'encourage' exfiltration - it **formalizes data distribution already happening in worse ways**. Makes it visible and governable.

## Security Theater vs. Actual Risk

Management more comfortable with:
- Invisible, unauditable data leaking everywhere (current state)

Than with:
- Explicit, trackable, governable system (PDS)

This is backwards security posture - preferring ignorance to governance.

## Organizational Impact

**Work architecture created:**
- Generate unused evidence of unfixed problems
- With tool not allowed to fix them
- Insights not acted upon (zero action loop)
- External institutions benefit while UO blocks internal use

**Demotivating characteristics:**
- Technical vindication (external adoption proves approach works)
- Organizational constraint (can't deploy internally where built)
- Insight production (can measure system failure)
- Zero action loop (insights don't drive decisions)

## Career Implications

**Position:** Topped out AP3 ($140K, benefits, work-life balance)

**Growth blocked:** Management that blocks PDS deployment won't promote PDS builder

**Options:**
1. Reclassification (unlikely given management stance)
2. Leave for higher classification elsewhere
3. Accept ceiling, optimize for other variables (stability, external reputation, personal projects)

**Current strategy:** #3 while keeping #2 option open - compound skills/visibility through external evangelism, conference talks, portable infrastructure building

## Strategic Positioning

**Portable infrastructure developed:**
- PDS architectural patterns (vendor-agnostic, open formats)
- duckdb-kb knowledge management system
- Conference presence and external reputation
- No vendor lock-in, no institutional dependency

**Optionality preserved:** If leaves UO, takes both systems and reputation with him

**Compounding maintained:** External adoption, conference talks, skill development continue despite organizational ceiling

## Questions Management Should Ask (But Don't)

**Right question:** 'How do we govern this capability?'

**Wrong question:** 'How do we prevent what we've been unable to prevent for years?'

**Tactical responses if escalates:**
1. Audit trail advantage - PDS can log every extraction; Cognos CSV exports have no record
2. Access control preservation - PDS respects Oracle grants, doesn't grant new access
3. Recovery capability - When analyst leaves and reports break, PDS configs are versioned; Cognos documentation is hope-based

## Related Context

See user-reference-pds-architecture for technical details.

PNAIRP presentation demonstrates external validation: other institutions implementing approach UO management restricts internally.

---

*KB Entry: `user-issue-uo-pds-restriction-rationale` | Category: issue | Updated: 2025-11-21*
