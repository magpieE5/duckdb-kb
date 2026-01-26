---
id: seed-pds-custom-utils
category: seed
title: PDS Custom Utils - Organization-Specific Data Extraction
tags:
- seed
- pds
- custom
- utils
- ora
- oracle
- mssql
- jira
- canvas
- extraction
- ipeds
- scorecard
- kraken
- crypto
- higher-ed
- mintable
created: '2026-01-21T10:45:30.889145'
updated: '2026-01-22T07:39:05.587466'
---

# PDS Custom Utils - Organization-Specific Data Extraction

**PDS custom utilities - organization-specific data extraction. Require database connections, API credentials, or platform-specific access. Located in utils/custom/.**

---

## Database Extraction

### Commands

```bash
pds ora {tag}           # Oracle → Parquet (parallel sliced)
pds mssql {tag}         # MS SQL Server → Parquet
pds upload_ora {tag}    # Parquet → Oracle
pds upload_mssql {tag}  # Parquet → MS SQL Server
pds download {tag}      # Sync pre-extracted canonical data

pds checkdet {schema.table} {runs}  # Detect non-determinism
pds slice {schema.table} {col} {n}  # Generate partition boundaries
```

---

### Oracle Extraction Pipeline

**Command:** `pds ora {tag}`

Extracts Oracle tables to Parquet files in parallel. Uses oracledb + pyarrow, supports WHERE clauses, column subsetting, and profile-based slicing for large table parallelism.

**Pipeline:**
```
_ora_{tag}.csv (seed)
       │
       ▼
Profile lookup (_ora_profiles.csv)
       │
       ▼
Oracle connection (per schema via config.ini)
       │
       ▼
Batch extraction (cursor.fetchmany)
       │
       ▼
Parquet files (snappy compressed)
       │
       ▼
DuckDB load (via load_duckdb.py)
```

**Seed format** (`_ora_{tag}.csv`):
```csv
table_name,where
ioep.odsmgr__student_course,none
ioep.odsmgr__schedule_offering,academic_period >= '202001'
icap.cognos12__cogipf_runreport,none
```

- `table_name`: `{schema}.{oracle_owner}__{table_name}` format (DOUBLE UNDERSCORE)
- `where`: SQL WHERE clause or `none` for full table

**Output:** `~/pds/data/{schema}/_raw/{table}/*.parquet` → loaded to DuckDB

---

### Profile-Based Slicing

Large tables benefit from parallel extraction via `_ora_profiles.csv`:

```csv
table_name,where
icrp.cognos12__cmobjprops7,cmid is null
icrp.cognos12__cmobjprops7,cmid <= 8357
icrp.cognos12__cmobjprops7,cmid > 8357 AND cmid <= 27896
...
icrp.cognos12__cmobjprops7,cmid > 207694
```

**Key insight:** First row handles NULLs, subsequent rows partition by percentile boundaries.

**Generating slices:**
```bash
cd ~/pds && source .venv/bin/activate
pds slice {schema}.{table} {column} {num_slices}

# Example: 16 slices on cmid column
pds slice icrp.cognos12__cmobjprops7 cmid 16
```

Outputs CSV-ready lines based on percentile distribution.

**WHERE clause combination:**

Profile WHERE combines with tag WHERE:

```python
def combine_where_clauses(tag_where, profile_where):
    if tag_where == 'none' and profile_where == 'none':
        return 'none'
    elif tag_where == 'none':
        return profile_where
    elif profile_where == 'none':
        return tag_where
    else:
        return f"({profile_where}) AND ({tag_where})"
```

---

### Profiling Workflow for New Tables

**When profiling is needed:** Table not in `_ora_profiles.csv`

Check: `grep {table_name} ~/pds/seeds/_ora_profiles.csv`

#### Step 1: Find slice column candidate

Query `main.dba_tab_columns` (in PDS DuckDB) for the new table's columns:

```sql
SELECT column_name, data_type 
FROM main.dba_tab_columns 
WHERE table_name = 'STUDENT' AND owner = 'ODSMGR'
```

Match column names/types against **already profiled tables in `_ora_profiles.csv`**:
- `person_uid`, `academic_period`, `cmid`
- Wildcard patterns: `*_pidm` (e.g., `spraddr_pidm`, `spriden_pidm`, `goremal_pidm`)

Look for numeric columns that distribute data evenly.

#### Step 2: Borrow profile for initial extraction

Add to `_ora_{tag}.csv` (use `manual` or `idr-NNNN` tag):
```
{schema}.{table},1=1
```
Or borrow WHERE clause from similar already-profiled table.

Ensure slice column exists in `_columns_{tag}.csv`:
```
{schema}.{table},{slice_column}
```

Run: `pds ora {tag}`

#### Step 3: Generate accurate partitions

```bash
pds slice {schema}.{table} {column} 16
```

Use 16 slices. If extraction takes >5 min, use 32 slices instead.
(Slice count based on Oracle/network/local CPU cores.)

Output is CSV lines ready for `_ora_profiles.csv`:
```
ioep.odsmgr__student,person_uid is null
ioep.odsmgr__student,person_uid <= 123456
ioep.odsmgr__student,person_uid > 123456 AND person_uid <= 234567
...
```

Paste output into `_ora_profiles.csv` (permanent home).

#### Step 4: Update tag seed

Change `_ora_{tag}.csv` entry:
```
{schema}.{table},none
```

`none` means "use partitions from `_ora_profiles.csv`"

Remove the table's columns from `_columns_{tag}.csv` (results in `SELECT *` for full extraction).

#### Step 5: Full extraction

```bash
pds ora {tag}
```

Now extracts all columns with proper partition boundaries.

#### Step 6: Validate

**Check for non-determinism first:**
```bash
pds checkdet {schema}.{table} 10
```
Use 10-50 runs based on row count. If non-deterministic, stop here and record finding.

**Find unique key:**
```bash
pds uk {schema}.{table} {preset_columns}
```
Preset columns derived from WMT grain hints or column name patterns.

---

### Profiling Key Concepts

| Concept | Meaning |
|---------|---------|
| `_ora_profiles.csv` | Permanent partition definitions |
| `_ora_{tag}.csv` with `none` | "Use _ora_profiles.csv for this table" |
| `_ora_{tag}.csv` with `1=1` | Borrow/initial extraction (no partitioning) |
| `_columns_{tag}.csv` | Column filter (union across all tags); omit for `SELECT *` |
| Tags `manual`, `idr-NNNN` | Ad-hoc work, periodically pruned |

**Notes:**
- Multi-column profiles exist for some tables (multiple slice columns)
- `_columns_*.csv` is a union across all tags
- Profiling is a prerequisite for `pds checkdet` and `pds uk`

---

### Extraction Implementation Details

From `~/pds/utils/ora.py`:

**Connection setup:**
```python
oracledb.defaults.fetch_lobs = False
os.environ['NLS_LANG'] = 'AMERICAN_AMERICA.WE8ISO8859P1'

connection_params = {
    'user': config[schema]['user'],
    'password': config[schema]['pass'],
    'dsn': f"{config[schema]['host']}:{config[schema]['port']}/{config[schema]['service_name']}"
}
```

**Batch extraction:**
```python
cursor.arraysize = batch_size  # From config BATCH_SIZE
cursor.execute(final_sql)
columns = [desc[0].lower() for desc in cursor.description]
while rows := cursor.fetchmany():
    # Write parquet batch
    pa_table = pa.Table.from_arrays(...)
    pq.write_table(pa_table, batch_file_path, compression="snappy")
```

**Empty table handling:**
```python
if not rows:
    empty_file_path = extract_path / f"{timestamp}_{pid}_empty.parquet"
    empty_table = pa.Table.from_pydict(empty_data, schema=table_schema)
    pq.write_table(empty_table, empty_file_path)
```

**Special processing:**
- For `tag == 'dict'`: Creates `pds_dba_views` table from `sys.dba_views` (converts LONG to LOB)
- For `tag == 'cognos'`: Creates `lampman.cmpolicies` table with LOB conversion for policy XML
- Partition awareness: Queries `sys.dba_tab_partitions` to build partition cache

**Performance output:**
```
ora dict   000.025   3,662,406 ioep.sys__dba_tab_columns
ora dict   003.600   2,074,133 icrp.cognos12__cmobjects
```

Format: `ora {tag} {minutes:07.3f} {row_count:10,} {schema}.{table}`

---

### Output Structure

```
~/pds/data/
├── ioep/
│   └── _raw/
│       └── odsmgr__student_course/
│           ├── 1733258400000000_12345_0.parquet
│           ├── 1733258400000001_12345_1.parquet
│           └── ...
├── icrp/
│   └── _raw/
│       └── cognos12__cmobjects/
│           └── ...
└── main/
    └── (seed tables, derived tables)
```

Parquet filename: `{timestamp}_{pid}_{batch_num}.parquet`

---

## Configuration

Credentials in `~/.config/pds/locations.ini`:

```ini
[database_alias]
host = oracle-prod.example.com
port = 1521
service_name = PROD
user = readonly_user
pass = secret

[jira]
url = https://jira.example.com
pat = your_personal_access_token

[kraken]
api_key = YOUR_API_KEY
api_secret = YOUR_API_SECRET
```

**PDS config** (`~/pds/pds.ini`):
```ini
[ioep]
user = username
pass = password
host = hostname
port = 1521
service_name = SERVICE
create_dba_views = true

[icrp]
...
```

---

## Higher Ed Public Data

### IPEDS - Federal Education Data

**Command:** `pds ipeds [start_year] [end_year]`

IPEDS (Integrated Postsecondary Education Data System) - federal reporting data every IR person knows. ~6,100 institutions, data from 1980-present. Public data, zero FERPA concerns.

```bash
pds ipeds 2023              # Single year
pds ipeds 2014 2023         # Year range
pds ipeds 2023 --surveys HD,IC,GR  # Specific surveys
pds transform ipeds         # Build semantic models
```

**Output:** `ipeds.*` schema with views for each survey (hd2023, gr2023, c2023_a, etc.)

**Semantic models** (after transform):
- `institutions` - HD with peer flags, control, Carnegie class
- `graduation_rates` - 150% completion metrics
- `completions` - Degrees by CIP family
- `enrollment` - 12-month headcount

**Schema drift handling:** Python stacker uses column intersection + year column to union across years with varying schemas.

**Peer comparison:** Define peers in `seeds/ipeds/ipeds_peers.csv`:
```csv
unitid,peer_group
123456,MY_INSTITUTION
104179,AAU
110635,CONF
```

**Data lag:** IPEDS runs 12-18 months behind. 2024 data partially available early 2026.

### College Scorecard - Outcomes Data

**Command:** `pds scorecard [start_year] [end_year]`

```bash
pds scorecard --latest      # Most recent year only
pds scorecard 2020 2023     # Year range
pds scorecard               # All years (394MB download)
```

**Output:** `scorecard.mergedYYYY` views (~3,300 columns per year)
**Join:** UNITID matches IPEDS

---

## Crypto / Financial APIs

### Kraken - Cryptocurrency Exchange

**Command:** `pds kraken [endpoint]`

```bash
pds kraken ticker       # Market prices (no auth needed)
pds kraken              # Full extract: balance, trades, ledgers
pds kraken balance      # Current balances only
pds transform kraken    # Build analytics models
```

**Raw views:** `kraken.ticker`, `kraken.balance`, `kraken.trades`, `kraken.ledgers`

**Analytics models** (after transform):
- `portfolio_value` - Holdings with USD valuation
- `trade_summary` - Aggregated by pair/side
- `cost_basis` - Average cost per asset
- `pnl` - Realized + unrealized profit/loss
- `market_overview` - Spreads, volume, price movements

**API key permissions (read-only recommended):**
- Query (Funds) - for balances
- Query closed orders & trades
- Query ledger entries
- Do NOT enable: Deposit, Withdraw, Create/modify orders

**Kraken asset naming:** X-prefix for crypto (XXBT=Bitcoin), Z-prefix for fiat (ZUSD)

---

## Personal Data (macOS)

Personal data (gmail, calendar, imessage, jira, canvas) accessed via PDS DuckDB views in the `personal` schema. Convenience views in `main` schema handle timestamp conversion and joins. Recent/upcoming views provide pre-filtered quick access.

### Extraction Commands

```bash
pds imessage            # iMessage → Parquet
pds calendar            # macOS Calendar → Parquet
pds gmail               # Gmail API → Parquet
pds jira                # Atlassian Jira REST API → Parquet
pds canvasrest {tag}    # Canvas LMS REST API → Parquet
```

**Requires:** Full Disk Access for Terminal/iTerm (iMessage, Calendar)

### Refresh Policy

**`pds refresh comms` is manual-only.** Run it yourself when needed. For ad-hoc queries, just query existing data - don't refresh first.

```bash
cd ~/pds && source .venv/bin/activate
pds refresh comms        # All sources
pds transform personal   # Rebuild all views including recent_*
```

### Quick Access Views

Pre-filtered views for "what happened recently" queries:

| View | Description | Window |
|------|-------------|--------|
| `main.recent_imessage` | iMessage summary by contact | 3 days |
| `main.recent_gmail` | Gmail summary by sender | 3 days |
| `main.recent_jira` | My open tickets by update | All open |
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

### Architecture

```
Source → PDS Extract → Parquet → personal.* (raw) → main.* (convenience) → main.recent_* (filtered)
                                       ↑
                              contacts seed (phone→name)
```

Data lives in PDS DuckDB (`~/pds/utils/_pds.duckdb`), not KB.

### Base Convenience Views (main.*)

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

### Contacts Seed

Phone→name mapping from Apple Contacts, stored at `~/pds/seeds/personal/contacts.csv`:

```csv
phone,name,organization
+15416541076,Jesse Sedwick,
+15412062573,Megan Prouty,
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

### Raw Views (personal.*)

Lower-level access, requires timestamp conversion:

| Source | PDS Command | Views | Notes |
|--------|-------------|-------|-------|
| iMessage | `pds imessage` | `personal.imessage__*` (5) | macOS Messages.app |
| Gmail | `pds gmail` | `personal.gmail__messages` | Gmail API |
| Apple Calendar | `pds calendar` | `personal.calendar__*` (5) | macOS Calendar.app |
| Jira (IDR) | `pds jira` | `personal.jira__issues` | Atlassian REST API |
| Canvas LMS | `pds canvasrest` | `personal.canvas__*` (3) | Canvas REST API |

### Model Files (~/pds/models/personal/)

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

## Other APIs

```bash
pds canvasdap           # Canvas Data Access Platform → Parquet
pds ad                  # Active Directory/LDAP → Parquet
```

---

## Building New Adapters

To add a new custom data source:

1. **Create extractor** (`utils/custom/myapi.py`)
2. **Register in cli.py** (in custom commands section)
3. **Add credentials to `locations.ini`** (if needed)

See existing extractors (ipeds.py, kraken.py, scorecard.py) as templates.

The pattern:
1. Fetch data (API, database, file)
2. Convert to PyArrow table
3. Write to `data/{schema}/_raw/{table}/*.parquet`
4. Call `load_duckdb()` to register views

---

*KB Entry: `seed-pds-custom-utils` | Category: seed | Updated: 2026-01-22*
