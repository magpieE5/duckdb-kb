---
id: seed-pds-personal-data
category: seed
title: Personal Data Access via PDS
tags:
- pds
- personal
- gmail
- calendar
- imessage
- jira
- canvas
- duckdb
- convenience-views
- recent-views
- comms
- mode-work-load
- mode-personal
created: '2025-12-22T10:36:11.635118'
updated: '2026-01-18T00:24:34.447172'
---

# Personal Data Access via PDS

**Personal data (gmail, calendar, imessage, jira, canvas) accessed via PDS DuckDB views in the `personal` schema. Convenience views in `main` schema handle timestamp conversion and joins. Recent/upcoming views provide pre-filtered quick access. Data refreshed via `pds refresh comms`.**

---

## Refresh Policy

**`pds refresh comms` is manual-only.** User runs it himself; Arlo should NOT run it proactively.

For ad-hoc queries (e.g., "check recent emails from X"), just query existing data - don't refresh first.

**Exception:** Only if user explicitly asks for a refresh.

---

## Before Querying: Get Schema

**Run this before querying comms views** to see available columns and avoid schema assumption errors:

```bash
duckdb ~/pds/utils/_pds.duckdb -c "
SELECT table_name, column_name, data_type
FROM information_schema.columns
WHERE table_schema = 'main'
  AND table_name IN ('imessage', 'calendar', 'jira', 'jira_comments', 'canvas',
                     'recent_imessage', 'recent_gmail', 'recent_jira', 'upcoming_calendar', 'recent_canvas')
ORDER BY table_name, ordinal_position;
"
```

**Key gotcha:** `main.jira` uses `ticket` column, but `main.jira_comments` uses `issue_key`. Join: `jira.ticket = jira_comments.issue_key`

---

## Quick Access (Recent/Upcoming Views)

Pre-filtered views for "what happened recently" queries:

| View | Description | Window |
|------|-------------|--------|
| `main.recent_imessage` | iMessage summary by contact | 3 days |
| `main.recent_gmail` | Gmail summary by sender | 3 days |
| `main.recent_jira` | **My** open tickets by update | All open, assignee=Brock |
| `main.upcoming_calendar` | Calendar events | -1 to +7 days |
| `main.recent_canvas` | Missing assignments | 14 days |

**Quick queries:**
```sql
SELECT * FROM main.recent_imessage;       -- Who's been texting
SELECT * FROM main.recent_gmail;          -- Recent emails by sender
SELECT * FROM main.recent_jira;           -- My open Jira tickets + staleness
SELECT * FROM main.upcoming_calendar;     -- Week ahead
SELECT * FROM main.recent_canvas;         -- Kids' missing work
```

---

## Architecture

```
Source → PDS Extract → Parquet → personal.* (raw) → main.* (convenience) → main.recent_* (filtered)
                                       ↑
                              contacts seed (phone→name)
```

Data lives in PDS DuckDB (`~/pds/utils/_pds.duckdb`), not KB.

---

## Base Convenience Views (main.*)

Full data with timestamps converted and joins done:

| View | Key Columns | Notes |
|------|-------------|-------|
| `main.imessage` | msg_time, contact, phone, direction, message | iMessage with decoded text + contact names |
| `main.calendar` | title, start_time, end_time, calendar | Apple Calendar with names |
| `main.jira` | ticket, title, status, assignee, updated | IDR project issues (all) |
| `main.jira_comments` | issue_key, author, body, created | Comments - joins via issue_key = jira.ticket |
| `main.canvas` | student_name, assignment_name, due_at | Missing assignments |

**Gmail raw view:** `personal.gmail__messages` (message_id, thread_id, date, from_addr, from_name, to_addr, subject, body, labels, snippet)

**Timestamp handling:** All timestamps are plain `TIMESTAMP` (not `TIMESTAMPTZ`). This allows `::TIME` and `::DATE` casts to work directly:
```sql
SELECT msg_time::TIME as time FROM main.imessage;
SELECT date::TIMESTAMP::DATE as dt FROM personal.gmail__messages;
```

---

## Contacts Seed

Phone→name mapping from Apple Contacts, stored at `~/pds/seeds/personal/contacts.csv`:

```csv
phone,name,organization
+15416541234,Jesse Burnside,
+15412063344,Megan Smith,
```

**Phone format:** E.164 (+1XXXXXXXXXX) to match iMessage handle IDs.

**Reload after edits:**
```bash
pds seed && pds transform personal
```

**Edge cases:**
- Group chat outbound messages show `contact = NULL` (no single recipient)
- Short codes (872265) won't match contacts
- Unknown numbers fall back to raw phone

---

## Raw Views (personal.*)

Lower-level access, requires timestamp conversion:

| Source | PDS Command | Views | Notes |
|--------|-------------|-------|-------|
| iMessage | `pds imessage` | `personal.imessage__*` (5) | macOS Messages.app |
| Gmail | `pds gmail` | `personal.gmail__messages` | Gmail API |
| Apple Calendar | `pds calendar` | `personal.calendar__*` (5) | macOS Calendar.app |
| Jira (IDR) | `pds jira` | `personal.jira__issues` | Atlassian REST API |
| Canvas LMS | `pds canvasrest` | `personal.canvas__*` (3) | Canvas REST API |

---

## Refresh Commands

```bash
cd ~/pds && source .venv/bin/activate
pds refresh comms        # All sources
pds transform personal   # Rebuild all views including recent_*
```

---

## Model Files (~/pds/models/personal/)

| File | Output View | Notes |
|------|-------------|-------|
| imessage.sql | main.imessage | |
| calendar.sql | main.calendar | |
| jira.sql | main.jira | All tickets |
| jira_comments.sql | main.jira_comments | |
| canvas.sql | main.canvas | |
| recent_imessage.sql | main.recent_imessage | 3-day summary by contact |
| recent_gmail.sql | main.recent_gmail | 3-day summary by sender |
| recent_jira.sql | main.recent_jira | My open tickets only |
| upcoming_calendar.sql | main.upcoming_calendar | -1 to +7 days |
| recent_canvas.sql | main.recent_canvas | 14-day missing assignments |

Transform config: `~/pds/seeds/personal/_transform_personal.csv`

---

*KB Entry: `seed-pds-personal-data` | Category: seed | Updated: 2026-01-18*
