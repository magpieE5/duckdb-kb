---
id: user-pattern-banner-ods-daily-work
category: pattern
title: Banner ODS/Cognos Daily Work Patterns
tags:
- banner
- ods
- cognos
- daily-work
- troubleshooting
- uo-is
created: '2025-11-21T13:01:44.431948'
updated: '2025-11-21T13:01:44.431948'
metadata: {}
---

# Banner ODS/Cognos Daily Work Patterns

Day-to-day varies by initiative but common patterns:

**Operations/Support:**
- ODS refreshes overnight, occasional hangs requiring remedial steps
- Verification before notifying users they can resume data consumption
- Large backlog of tickets to work through

**Ticket types:**
- Data additions (new fields, tables, reports)
- Data discrepancies (may be ODS issue or upstream Banner issue)
- Example: Students registered for courses that don't exist in schedule offering (exists in ODS, not in Banner source)

**Investigation workflow:**
- Uses PDS (~/PDS) to investigate discrepancies
- MCP can query PDS database directly (code at ~/PDS/src/ods_manager)
- Can prescribe data extractions, view data directly

**Technical environment:**
- Banner ERP (Ellucian) with 30 years of modifications
- On-premise ODS (operational data store)
- Cognos reporting layer
- Data flows: Banner → ODS (overnight refresh) → Cognos reports

**Key pain points:**
- Upstream vs downstream responsibility unclear (Banner data quality vs ODS processing)
- Large modification backlog makes troubleshooting complex
- Limited documentation of why modifications exist


---

*KB Entry: `user-pattern-banner-ods-daily-work` | Category: pattern | Updated: 2025-11-21*
