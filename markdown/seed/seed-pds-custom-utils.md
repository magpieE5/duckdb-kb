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
- chat
- email
- calendar
- gmail
- ad
- ldap
- checkdet
- slice
- extraction
- api
created: '2026-01-12T13:04:30.916766'
updated: '2026-01-12T21:26:18.083151'
metadata: {}
---

# PDS Custom Utils - Organization-Specific Data Extraction

**PDS custom utilities - organization-specific data extraction and analysis commands. These require external database connections, API credentials, or platform-specific access (macOS). Located in utils/custom/ and removed from cli.py during minting. Kept as reference for building your own adapters.**

---

## Quick Reference

```bash
# Human terminal usage (activate venv first)
source ~/pds/.venv/bin/activate
cd ~/pds
pds ora {tag}

# Claude Code usage (no venv activation in Bash tool)
cd ~/pds && ~/pds/.venv/bin/pds ora {tag}
```

### Database Extraction

```bash
pds ora {tag}           # Oracle → Parquet (parallel sliced extraction)
pds mssql {tag}         # MS SQL Server → Parquet
pds upload_ora {tag}    # Parquet → Oracle tables
pds upload_mssql {tag}  # Parquet → MS SQL Server tables
pds download {tag}      # Sync pre-extracted canonical data
pds distro {tag}        # Create distribution directories with symlinks

# Oracle Profiling & Analysis
pds checkdet {schema.table} {runs}  # Detect non-determinism
pds slice {schema.table} {col} {n}  # Generate partition boundaries
pds rc_ora {tag}        # Oracle row counts
pds rc_mssql {tag}      # MSSQL row counts
pds sql {schema} {file} # Execute SQL file against Oracle

# Personal Data (macOS)
pds chat                # iMessage → Parquet
pds email               # macOS Mail → Parquet
pds calendar            # macOS Calendar → Parquet
pds gmail               # Gmail API → Parquet

# Enterprise APIs
pds jira                # Atlassian Jira REST API → Parquet
pds canvasrest {tag}    # Canvas LMS REST API → Parquet
pds canvasdap           # Canvas Data Access Platform → Parquet
pds ad                  # Active Directory/LDAP → Parquet

# Cognos
pds cogxml              # Parse Cognos report XML specifications
```

---

## Configuration

Custom utils require credentials in `locations.ini`:

**Location:**
- macOS/Linux: `~/.config/pds/locations.ini`
- Windows: `%APPDATA%/pds/locations.ini`
- Override: Set `PDS_CONFIG` environment variable to custom path

```ini
# Database connections
[ioep]
host = oracle-prod.example.com
port = 1521
service_name = PROD
user = readonly_user
pass = secret

[ioet]
host = oracle-test.example.com
port = 1521
service_name = TEST
user = readonly_user
pass = secret

[mssql_schema]
host = sqlserver.example.com
port = 1433
database = MyDB
user = readonly_user
pass = secret

# API credentials
[jira]
url = https://jira.example.com
pat = your_personal_access_token

[canvas]
url = https://canvas.example.com
token = your_api_token

[canvasdap]
client_id = your_client_id
client_secret = your_client_secret

[gmail]
credentials_path = /path/to/credentials.json
token_path = /path/to/token.json
```

**Security:** `locations.ini` contains credentials - stored outside the repo by design.

---

## Database Extraction

### ora - Oracle to Parquet

**Command:** `pds ora {tag}`

Parallel extraction from Oracle databases with automatic slicing for large tables.

**Seed format** (`_ora_{tag}.csv`):
```csv
table_name,where
ioep.odsmgr__student,none
ioep.odsmgr__person,1=1
ioep.saturn__spriden,spriden_change_ind is null
```

| Value | Meaning |
|-------|---------|
| `none` | Use slices from `_ora_profiles.csv` |
| `1=1` | Extract all rows (no partitioning) |
| `{condition}` | Custom WHERE clause |

**Profiles** (`_ora_profiles.csv`):
```csv
table_name,where
ioep.odsmgr__student,person_uid is null
ioep.odsmgr__student,person_uid <= 123456
ioep.odsmgr__student,person_uid > 123456 AND person_uid <= 234567
ioep.odsmgr__student,person_uid > 999999
```

**Column filtering** (`_columns_{tag}.csv`):
```csv
table_name,column_name
ioep.odsmgr__student,person_uid
ioep.odsmgr__student,name_prefix
```

Limits extraction to specified columns. Omit table from this file for `SELECT *`.

**Features:**
- Parallel extraction using ProcessPoolExecutor
- Automatic schema inference from Oracle
- Batch writing to Parquet with snappy compression
- Progress reporting per table

### mssql - MS SQL Server to Parquet

**Command:** `pds mssql {tag}`

Same pattern as Oracle extraction but for MS SQL Server.

**Seed format** (`_mssql_{tag}.csv`):
```csv
table_name,where
schema.dbo__table_name,none
schema.dbo__other_table,1=1
```

Uses pymssql for connectivity (FreeTDS bundled in wheels).

### upload_ora / upload_mssql - Parquet to Database

**Commands:**
```bash
pds upload_ora {tag}
pds upload_mssql {tag}
```

Uploads Parquet tables back to Oracle or MS SQL Server.

**Seed format** (`_upload_ora_{tag}.csv`):
```csv
source_table,target_table,mode
main.my_table,SCHEMA.TARGET_TABLE,truncate
main.other,SCHEMA.OTHER,append
```

| Mode | Behavior |
|------|----------|
| `truncate` | Delete all rows, then insert |
| `append` | Insert without deleting |

---

## Oracle Profiling & Analysis

### checkdet - Non-determinism Detection

**Command:** `pds checkdet {schema.table} {runs}`

Detects non-deterministic Oracle views by extracting N times and comparing results.

```bash
pds checkdet ioep.odsmgr__supervisor 10
```

**What it does:**
1. Extracts the view N times using parallel slices
2. Compares row counts across runs
3. Compares each non-PK column for value differences
4. Reports affected rows and columns

**Requires:** Unique key defined in `_tests_{tag}.csv` with `test_type=unique`

**Output:**
```
✓ Row counts consistent across all runs
  All runs: 45,000 rows

⚠ NON-DETERMINISM DETECTED in 3 columns

Affected rows: 19,800 (44.00%)

Non-deterministic columns:
  - supervisor_name
  - position_number
  - effective_date
```

**Use case:** Before creating a unique key test, verify the view is deterministic. Non-deterministic views cannot have reliable unique keys.

### slice - Generate Partition Boundaries

**Command:** `pds slice {schema.table} {column} {num_slices}`

Generates evenly distributed partition boundaries for large table extraction.

```bash
pds slice ioep.odsmgr__student person_uid 16
```

**Output:**
```
ioep.odsmgr__student,person_uid is null
ioep.odsmgr__student,person_uid <= 123456
ioep.odsmgr__student,person_uid > 123456 AND person_uid <= 234567
...
ioep.odsmgr__student,person_uid > 999999
```

**Workflow:**
1. Run `pds slice` to generate boundaries
2. Paste output into `_ora_profiles.csv`
3. Update `_ora_{tag}.csv` to use `none` for the table
4. Extract with `pds ora {tag}` (now uses parallel slices)

**Slice count guidance:**
- 16 slices for most tables
- 32 slices if extraction takes >5 minutes
- Based on Oracle/network latency and local CPU cores

### rc_ora / rc_mssql - Row Counts

**Commands:**
```bash
pds rc_ora {tag}
pds rc_mssql {tag}
```

Quick row count verification against source databases.

### sql - Execute SQL File

**Command:** `pds sql {schema} {file.sql}`

Executes a SQL file against the specified Oracle schema.

```bash
pds sql ioep scripts/update_status.sql
```

---

## Personal Data Extraction (macOS)

These utilities extract data from macOS system databases and APIs.

### chat - iMessage

**Command:** `pds chat`

Extracts iMessage history from macOS `chat.db`.

**Source:** `~/Library/Messages/chat.db`

**Output:** `personal.chat` view with:
- message_id, handle_id, text, date
- is_from_me, chat_identifier
- Decoded NSAttributedString blobs

**Requires:** Full Disk Access for Terminal/iTerm

### email - macOS Mail

**Command:** `pds email`

Extracts email metadata from macOS Mail app.

**Source:** `~/Library/Mail/V*/MailData/Envelope Index`

**Output:** `personal.email` view with sender, subject, date, mailbox

### calendar - macOS Calendar

**Command:** `pds calendar`

Extracts calendar events from macOS Calendar app.

**Source:** `~/Library/Calendars/Calendar.sqlitedb`

**Output:** `personal.calendar` view with title, start_date, end_date, location

### gmail - Gmail API

**Command:** `pds gmail`

Extracts Gmail messages via Google API.

**Requires:**
- OAuth credentials in `locations.ini`
- First run opens browser for authorization

**Output:** `personal.gmail` view with full message metadata

---

## Enterprise API Extraction

### jira - Atlassian Jira

**Command:** `pds jira`

Extracts Jira issues and comments via REST API.

**Configuration:**
```ini
[jira]
url = https://jira.example.com
pat = your_personal_access_token
```

**Output:**
- `personal.jira__issues` - All issues with fields
- `personal.jira__comments` - Comments with author, body, created

**Features:**
- Pagination handling
- Flattens nested JSON structures
- Extracts custom fields

### canvasrest - Canvas LMS REST API

**Command:** `pds canvasrest {tag}`

Extracts Canvas LMS data via REST API.

**Seed format** (`_canvasrest_{tag}.csv`):
```csv
endpoint,table_name
/api/v1/courses,courses
/api/v1/users,users
```

**Configuration:**
```ini
[canvas]
url = https://canvas.example.com
token = your_api_token
```

### canvasdap - Canvas Data Access Platform

**Command:** `pds canvasdap`

Extracts Canvas analytics data via DAP (Data Access Platform).

**Configuration:**
```ini
[canvasdap]
client_id = your_client_id
client_secret = your_client_secret
```

**Output:** Large-scale analytics tables (submissions, enrollments, etc.)

**Features:**
- Handles massive datasets (94M+ rows)
- DuckDB parallel flattening for nested JSON
- Auto-creates `canvas.dap_*` views

### ad - Active Directory / LDAP

**Command:** `pds ad`

Extracts user/group data from Active Directory via LDAP.

**Configuration:**
```ini
[ad]
server = ldap://ad.example.com
user = CN=service,OU=Users,DC=example,DC=com
pass = secret
base_dn = DC=example,DC=com
```

**Output:** `personal.ad__users`, `personal.ad__groups`

---

## Cognos Utilities

### cogxml - Parse Cognos Report XML

**Command:** `pds cogxml`

Parses Cognos report XML specifications to extract:
- Query subjects and relationships
- Filter definitions
- Column mappings
- Report structure

**Output:** Used by transform models to create `cognos_*` analytics tables

---

## Distribution & Sync

### download - Sync Pre-extracted Data

**Command:** `pds download {tag}`

Downloads pre-extracted canonical data from a shared location.

**Seed format** (`_download_{tag}.csv`):
```csv
source_path,target_schema
/shared/pds/ioep,ioep
/shared/pds/cognos,main
```

**Use case:** Team members without database access can sync from shared extracts.

### distro - Create Distribution Directories

**Command:** `pds distro {tag}`

Creates distribution directories with symlinked Parquet files.

**Use case:** Prepare data for sharing without copying files.

---

## Extending Custom Utils

To add a new custom data source:

1. **Create the extractor** (`utils/custom/myapi.py`):
```python
from pathlib import Path
import pyarrow as pa
import pyarrow.parquet as pq
from utils.config import DATA_PATH, config
from utils.load_duckdb import load_duckdb

MYAPI_COMMAND_HELP = """
Extract data from MyAPI to Parquet.
"""

def myapi():
    # Get credentials
    api_key = config['myapi']['key']
    
    # Extract data
    data = fetch_from_api(api_key)
    
    # Write to Parquet
    schema = "myapi"
    table = "records"
    raw_path = DATA_PATH / schema / "_raw" / table
    raw_path.mkdir(parents=True, exist_ok=True)
    
    pa_table = pa.Table.from_pydict(data)
    pq.write_table(pa_table, raw_path / "data.parquet")
    
    # Finalize
    load_duckdb('parq', schema, silent=True)
    load_duckdb('views', schema, silent=False)
```

2. **Register in cli.py** (in CUSTOM COMMANDS block):
```python
('myapi', 'utils.custom.myapi', 'MYAPI_COMMAND_HELP', 'Personal Data Sources'),
```

3. **Add credentials to `locations.ini`**:
```ini
[myapi]
key = your_api_key
```

---

## Output Patterns

All custom extractors write to:
```
data/{schema}/_raw/{table}/*.parquet   # Raw extraction batches
data/{schema}/{table}.parquet          # Consolidated output
```

Views are created in DuckDB:
```sql
{schema}.{table}  -- e.g., ioep.odsmgr__student, personal.chat
```

---

## Security Notes

- `locations.ini` stored at `~/.config/pds/` (outside repo) - credentials never committed
- Personal data extractions (chat, email, calendar) require macOS Full Disk Access
- API tokens should have minimal required permissions

---

*KB Entry: `seed-pds-custom-utils` | Category: seed | Updated: 2026-01-12*
