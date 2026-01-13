---
id: seed-pds-core-utils
category: seed
title: PDS Core Utils - Mintable Data Engineering Toolkit
tags:
- seed
- pds
- core
- utils
- transform
- tests
- snap
- search
- lc
- uk
- compschema
- comptable
- hq
- ui
- meta
- rep
- repgen
- streamlit
- reports
- yaml
- mintable
- data-engineering
created: '2026-01-12T13:02:14.862417'
updated: '2026-01-12T21:24:57.339838'
metadata: {}
---

# PDS Core Utils - Mintable Data Engineering Toolkit

**PDS core utilities - extraction-agnostic data engineering commands. These are the mintable foundation that works without org-specific database connections. Custom utils (Oracle, MSSQL, Jira, etc.) live in utils/custom/ and are removed during minting.**

---

## Quick Reference

```bash
# Human terminal usage (activate venv first)
source ~/pds/.venv/bin/activate
cd ~/pds
pds transform {tag}

# Claude Code usage (no venv activation in Bash tool)
cd ~/pds && ~/pds/.venv/bin/pds transform {tag}
```

### Core Commands

```bash
pds transform {tag}    # Run SQL/Python models → Parquet
pds tests {tag}        # Run data quality tests
pds snap {tag}         # Create SCD Type 2 snapshots
pds export_csv {tag}   # Export tables to CSV
pds refresh {tag}      # Orchestrate multiple commands
pds seed               # Load all seed CSVs into DuckDB

pds search {value}     # Full-text scan across all DuckDB values
pds lc {schema.table}  # List columns with datatypes/nulls
pds uk {schema.table} col1 col2  # Find unique key candidates
pds compschema s1 s2   # Compare all shared tables between schemas
pds comptable s1.t s2.t  # Compare specific table between schemas

pds hq                 # Open Harlequin TUI SQL IDE
pds ui                 # Open DuckDB browser IDE at localhost:4213

pds meta               # Generate pds.html documentation with lineage
pds rep                # Launch Streamlit reports dashboard
pds repgen {config}    # Generate report from YAML config

pds parqinfo {path}    # Analyze parquet file, recommend splitting
pds example            # Template for new data adapters
```

---

## Seed-Based Workflow Pattern

PDS commands operate on **seed CSV files** that define what to process:

```
seeds/
├── {domain}/
│   ├── _transform_{tag}.csv    # Models to run
│   ├── _tests_{tag}.csv        # Tests to execute
│   ├── _snap_{tag}.csv         # Tables to snapshot
│   ├── _export_csv_{tag}.csv   # Tables to export
│   └── _refresh_{tag}.csv      # Commands to orchestrate
```

**Tag convention:**
- `pds` - canonical daily refresh
- `manual` - ad-hoc work
- `idr-NNNN` - ticket-specific work (pruned periodically)

---

## Transform System

**Command:** `pds transform {tag}`

Executes SQL/Python models to create DuckDB tables stored as Parquet.

**Seed format** (`_transform_{tag}.csv`):
```csv
table_name,split_count
cognos_usage,1
large_table,16
```

| Column | Purpose |
|--------|---------|
| table_name | Model name (matches .sql/.py in models/) |
| split_count | 1 = single file, >1 = partitioned output |

**Model resolution:**
1. Python first: `models/**/{table_name}.py` → subprocess execution
2. SQL fallback: `models/**/{table_name}.sql` → DuckDB execution

**Output:**
- Single: `data/main/{table_name}.parquet`
- Partitioned: `data/main/{table_name}/_split=N/*.parquet`

**SQL model pattern:**
```sql
-- begin deps
-- List upstream tables here for lineage tracking
-- from schema.table_name
-- end deps

SELECT columns
FROM schema.source_table
WHERE conditions
```

---

## Tests System

**Command:** `pds tests {tag}`

Seed-driven data quality testing framework.

**Seed format** (`_tests_{tag}.csv`):
```csv
test_name,test_type,test_mode,test_desc,col1,col2,col3
my_test,custom,warn,Description here,,,
my_table,unique,error,Check uniqueness,pk_col1,pk_col2,
```

**Test types:**
| Type | Behavior |
|------|----------|
| custom | Run SQL file `tests/{domain}/{test_name}.sql`, fail if cnt > 0 |
| unique | Generated SQL checks for duplicate composite keys |
| comp | Compare table between schemas |

**Test modes:**
- `warn` - Yellow warning, continues
- `error` - Red error, shows SQL

**Custom test SQL pattern:**
```sql
-- {TICKET}: Brief description
-- Root cause: explanation
select count('x') as cnt
from (
    -- Query returning failing records
    select ... from ... where ...
)
```

---

## Snapshot System

**Command:** `pds snap {tag}`

SCD Type 2 snapshots for time-travel queries.

**Seed format** (`_snap_{tag}.csv`):
```csv
snap_name
schema.table_name
```

**How it works:**
1. First run: Creates snapshot with `snap_scd_id`, `snap_valid_from`, `snap_valid_to`
2. Subsequent runs: Compares current data to snapshot, tracks:
   - New records (inserted)
   - Changed records (old row closed, new row opened)
   - Deleted records (row closed)
   - Unchanged records (preserved)

**Requires:** Unique key defined in `_tests_{tag}.csv` with `test_type=unique`

**Output:** `utils/snapshots/{schema}__{table}.parquet`

**Querying snapshots:**
```sql
-- Current state
SELECT * FROM schema.snap_table WHERE snap_valid_to IS NULL

-- State at specific time
SELECT * FROM schema.snap_table 
WHERE snap_valid_from <= '2024-06-01' 
  AND (snap_valid_to IS NULL OR snap_valid_to > '2024-06-01')
```

---

## Analysis Commands

### search - Full-text value scan

```bash
pds search LAMPMAN      # Find all occurrences across DuckDB
pds search 950000001    # Find specific ID
```

Scans every column of every table. Case-insensitive, no spaces allowed.

### lc - List columns

```bash
pds lc main.cognos_usage
```

Shows column names, datatypes, and whether columns have nulls:
```
column_name - NO NULLs    # Fully populated
column_name               # Has nulls
```

### uk - Unique key discovery

```bash
pds uk schema.table col1 col2 col3
```

Finds minimal composite key candidates. Provide 1-7 preset columns to check.

### compschema - Schema comparison

```bash
pds compschema ioep ioet
```

Compares all shared tables between two schemas. Output: `seeds/{s1}_{s2}.csv` with row counts and column match percentages.

### comptable - Table comparison

```bash
pds comptable ioep.dba_objects ioet.dba_objects
```

Detailed comparison of specific table between schemas.

---

## Interactive Interfaces

### hq - Harlequin TUI

```bash
pds hq
```

Opens Harlequin terminal-based SQL IDE connected to PDS DuckDB. Full SQL editing, results viewing, export capabilities.

### ui - DuckDB Browser IDE

```bash
pds ui
```

Opens DuckDB's built-in browser-based SQL IDE at `localhost:4213`. Keep terminal running to maintain server.

---

## Documentation Generation

### meta - Generate PDS Documentation

```bash
pds meta
```

Generates `pds.html` - a static, self-contained documentation site with:
- **Model lineage visualization** - interactive DAG showing table dependencies
- **Model descriptions** - business context from YAML metadata
- **Column documentation** - field-level descriptions
- **Runnable SQL** - the actual SQL for each model

Opens in browser when complete.

### How Lineage Works

Lineage is derived from two sources:

1. **Deps sections in SQL files** - explicit upstream dependencies:
```sql
-- begin deps
-- from ioep.odsmgr__ods_student
-- from main.stg_academic_periods
-- end deps
```

2. **YAML metadata** - exposures declare downstream dependencies (reports, dashboards)

### Model Documentation (YAML)

Document models by creating YAML files alongside your SQL:

```
models/
├── {domain}/
│   ├── {model}.sql           # The model SQL
│   └── metadata/
│       └── {model}.yml       # Documentation for the model
```

**YAML structure:**
```yaml
version: 2
models:
- name: my_model
  description: |
    Brief description of what this model represents.
    
    ## Grain
    One row per {entity} per {dimension}.
    
    ## Business Context
    Additional context, caveats, or usage notes.
    Markdown supported.
  columns:
  - name: id
    description: Primary identifier for the record.
  - name: status
    description: Current status. Values: ACTIVE, INACTIVE, PENDING.
  - name: created_date
    description: When the record was created.
```

**Key points:**
- `name` must match the SQL file name (without `.sql`)
- `description` supports full markdown
- `columns` is optional - document important/ambiguous columns
- Columns without descriptions are still shown in docs

### Exposures (Downstream Dependencies)

Declare reports or dashboards that consume models:

```yaml
version: 2
exposures:
- name: student_enrollment_dashboard
  type: dashboard
  description: Streamlit dashboard showing enrollment trends
  depends_on:
    - ref('ods_student')
    - ref('ods_student_course')
  owner:
    name: Data Team
```

Place exposure YAML in `reports/` or `models/` - meta scans both.

### What meta.py Does

1. Scans `models/` for SQL files (excluding `_specs/`, `staging/`, `dict/`, `personal/`, `cognos/`)
2. Parses `-- begin deps` sections to build lineage
3. Loads YAML files from `models/**/metadata/*.yml` and `reports/**/*.yml`
4. Merges model documentation with auto-detected dependencies
5. Generates interactive HTML documentation

### Optional Enrichment

`utils/custom/meta_enrichment.py` can add org-specific documentation (security classifications, business metadata from external systems). Core meta works without it.

---

## Streamlit Report System

PDS includes a complete report generation system with cross-filtering dashboards.

### rep - Launch Streamlit

```bash
pds rep
```

Launches Streamlit at `localhost:8501`. Reports live in `reports/pages/`.

### repgen - Generate from YAML

```bash
pds repgen my_report
# Reads:  reports/configs/my_report.yaml
# Writes: reports/pages/my_report.py
```

### AI Workflow for Reports

**Two-layer approach:**

1. **YAML Spec (80%)** - Describe report conversationally, generate YAML, run `pds repgen`
2. **Python Edits (20%)** - For custom behavior, edit the generated .py directly

**Lifecycle:**
```
Conversation → YAML spec → pds repgen → .py → Explore → .py edits
                  ↑                                    |
                  └──── (regenerate if major changes) ─┘
```

### YAML Config Reference

```yaml
report_name: Sales Dashboard           # Display title
report_key: sales                      # Unique key for session state
model: sales_data                      # PDS table/view to query
time_column: order_date                # X-axis for time series
default_where: "order_date >= CURRENT_DATE - INTERVAL '90 days'"

where_hints:                           # Commented filter suggestions
  - "region like '%%'"
  - "product_category like '%%'"

additional_columns:                    # Extra columns beyond inferred
  - customer_id
  - notes

kpis:
  - label: Total Orders
    column: "*"
    agg: count
  - label: Unique Customers
    column: customer_id
    agg: nunique
  - label: Revenue
    column: amount
    agg: sum
  - label: Success Rate
    column: status
    agg: pct_completed              # pct_{value} = percent matching

time_series_tabs:
  - label: "📈 Orders"
    column: "*"
    agg: count
    title: Orders Over Time
  - label: "💰 Revenue"
    column: amount
    agg: sum
    title: Revenue Over Time

dimension_tabs:
  - label: "🏷️ Products"
    column: product_name
    title: Orders by Product
  - label: "🌎 Regions"
    column: region
    title: Orders by Region
```

### Supported Aggregations

| Aggregation | Description |
|-------------|-------------|
| `count` | Row count |
| `nunique` | Distinct values |
| `sum` | Sum of column |
| `mean` | Average of column |
| `pct_{value}` | Percent where column == value |
| `count_not_null` | Count where column is not null |

### Report Layout

```
┌─────────────────────────────────────────────────────────────────┐
│ [▶ Run]  Report Title                                           │
├─────────────────────────────────────────────────────────────────┤
│ > SQL Query (collapsible)                                       │
├─────────────────────────────────────────────────────────────────┤
│ 🔍 Filter status                        [Reset Filters]         │
├─────────────────────────────────────────────────────────────────┤
│  KPI 1      │  KPI 2      │  KPI 3      │  KPI 4               │
│  73,985     │  643        │  1,414      │  98.2%               │
├─────────────────────────────────────────────────────────────────┤
│ TIME SERIES TABS                                                │
│ [Orders] [Revenue] [Users]                                      │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ Line Chart (box-select to filter date range)                │ │
│ └─────────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│ DIMENSION TABS                                                  │
│ [By Product] [By Region] [By Status]                            │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ Bar Chart (click to filter)                                 │ │
│ └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### Cross-Filtering Behavior

| Interaction | Effect |
|-------------|--------|
| Box-select on time series | Filters to date range |
| Click bar in dimension tab | Filters to that value |
| Box-select multiple bars | Filters to multiple values |
| Reset Filters button | Clears all filters |
| Run button (▶) | Re-executes SQL query |

### Design Philosophy

- **SQL-first**: SQL widget always available for power users
- **Box-select over dropdowns**: Visual, precise selection
- **One time column**: Forces clarity on what the report is about
- **Tabs over overlays**: Each metric gets its own tab, avoids scale conflicts
- **Spec for structure, code for behavior**: YAML = what, Python = how

### Report Files

| Location | Purpose |
|----------|---------|
| `reports/configs/*.yaml` | YAML specs (source of truth) |
| `reports/pages/*.py` | Generated/customized reports |
| `reports/pds.py` | Main Streamlit entry point |
| `utils/report_generator.py` | Generator logic |
| `utils/sql_widget.py` | Shared SQL widget component |

---

## Utility Commands

### seed - Load seed CSVs

```bash
pds seed
```

Loads all CSV files in `seeds/` as DuckDB views. Run before other commands to ensure seed data is current.

### export_csv - Export to CSV

```bash
pds export_csv {tag}
```

Exports tables to CSV files in `exports/` directory.

**Seed format** (`_export_csv_{tag}.csv`):
```csv
table_name
schema.table_name
```

### refresh - Orchestrate commands

```bash
pds refresh pds      # Full canonical refresh
pds refresh manual   # Ad-hoc refresh
```

Runs multiple PDS commands in sequence.

**Seed format** (`_refresh_{tag}.csv`):
```csv
pds_command,pds_tag
transform,cognos
tests,cognos
snap,cognos
```

### parqinfo - Parquet analysis

```bash
pds parqinfo path/to/file.parquet
```

Analyzes parquet file and recommends:
- Split count for parallel processing
- Row group size for optimal reads

### example - Adapter template

```bash
pds example
```

Demonstrates the minimal adapter pattern for new data sources:
1. Define schema and table names
2. Write parquet files to `_raw/`
3. Call `load_duckdb` to finalize

---

## Directory Structure

```
~/pds/
├── utils/           # Core commands (mintable)
│   ├── cli.py       # Entry point
│   ├── config.py    # Configuration
│   ├── transform.py # SQL/Python → Parquet
│   ├── tests.py     # Data quality tests
│   ├── meta.py      # Documentation generation
│   ├── rep.py       # Streamlit launcher
│   ├── repgen.py    # Report generator CLI
│   ├── report_generator.py  # Generator logic
│   ├── sql_widget.py        # Shared SQL component
│   ├── ...
│   └── custom/      # Org-specific (remove for minting)
│       ├── ora.py   # Oracle extraction
│       ├── mssql.py # MSSQL extraction
│       └── ...
├── models/          # SQL/Python models
│   ├── {domain}/
│   │   ├── {model}.sql
│   │   └── metadata/{model}.yml
│   └── _specs/      # Auto-generated for lineage
├── seeds/           # Seed CSV files
│   └── {domain}/
│       └── _*.csv
├── tests/           # Custom test SQL files
│   └── {domain}/
│       └── {test_name}.sql
├── reports/         # Streamlit reports
│   ├── pds.py       # Main dashboard
│   ├── pages/       # Report pages
│   └── configs/     # YAML configs for repgen
├── data/            # Parquet output
│   ├── main/        # Transformed tables
│   └── {schema}/    # Source extracts
└── pds.html         # Generated documentation
```

---

## Minting Workflow

To create a clean PDS instance without org-specific tooling:

1. Delete custom command block from `cli.py` (lines 38-68)
2. The `utils/custom/` directory can remain for reference

Core functionality works out of the box for:
- Local parquet file analysis
- SQL transformations
- Data quality testing
- Documentation generation
- Interactive SQL interfaces
- Streamlit report building

---

## Configuration

`utils/config.py` defines paths relative to the PDS root:

| Variable | Default | Purpose |
|----------|---------|---------|
| ROOT_PATH | `~/pds/` | PDS installation root |
| UTILS_PATH | `~/pds/utils/` | Utils directory |
| DATA_PATH | `~/pds/data/` | Parquet output |
| SEEDS_PATH | `~/pds/seeds/` | Seed CSVs |
| DUCKDB_PATH | `~/pds/utils/_pds.duckdb` | DuckDB database |

---

*KB Entry: `seed-pds-core-utils` | Category: seed | Updated: 2026-01-12*
