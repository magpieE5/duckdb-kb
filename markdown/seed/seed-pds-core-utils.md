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
- streamlit
- mintable
created: '2026-01-21T10:46:23.568266'
updated: '2026-01-22T07:36:51.967540'
---

# PDS Core Utils - Mintable Data Engineering Toolkit

**PDS core utilities - extraction-agnostic data engineering commands. These are the mintable foundation that works without org-specific database connections.**

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
pds transform {tag}     # Run SQL/Python models → Parquet
pds tests {tag}         # Run data quality tests
pds snap {tag}          # Create SCD Type 2 snapshots
pds refresh {tag}       # Orchestrate multiple commands
pds seed                # Load all seed CSVs into DuckDB

pds search {value}      # Full-text scan across all DuckDB values
pds lc {schema.table}   # List columns with datatypes/nulls
pds uk {schema.table} col1 col2  # Find unique key candidates
pds compschema s1 s2    # Compare all shared tables between schemas
pds comptable s1.t s2.t # Compare specific table between schemas

pds hq                  # Open Harlequin TUI SQL IDE
pds ui                  # Open DuckDB browser IDE at localhost:4213

pds meta                # Generate & open pds.html documentation with lineage
pds dag [--tag TAG]     # Visualize refresh pipeline as ASCII DAG
pds rep                 # Launch Streamlit reports dashboard
pds repgen {config}     # Generate report from YAML config
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
│   └── _refresh_{tag}.csv      # Commands to orchestrate
```

**Tag convention:**
- `pds` - canonical daily refresh
- `manual` - ad-hoc work
- `ticket-NNNN` - ticket-specific work

---

## Transform System

**Command:** `pds transform {tag}`

Executes SQL/Python models to create DuckDB tables as Parquet files. Supports partitioned output for large tables.

### Seed Format

`_transform_{tag}.csv`:
```csv
table_name,split_count
my_model,1
large_table,16
```

| Column | Purpose |
|--------|---------|
| table_name | Model name (matches .sql/.py file in models/) |
| split_count | 1 = single parquet, >1 = partitioned output |

### Model Resolution

Transform looks for models in `~/pds/models/`:

1. **Python first**: `models/**/{table_name}.py` → `subprocess.run(["python", py_file])`
2. **SQL fallback**: `models/**/{table_name}.sql` → Execute via DuckDB
3. **Excludes**: `_specs/` directories (DBT templates)

### Output Paths

**Single File** (split_count = 1):
```
~/pds/data/main/{table_name}.parquet
```

View created:
```sql
CREATE OR REPLACE VIEW {table_name} AS
SELECT * FROM read_parquet('./utils/data/main/{table_name}.parquet')
```

**Partitioned** (split_count > 1):
```
~/pds/data/main/{table_name}/
├── _split=0/
│   └── data_0.parquet
├── _split=1/
│   └── data_0.parquet
└── ...
```

View created:
```sql
CREATE OR REPLACE VIEW {table_name} AS
SELECT * EXCLUDE (_split) FROM read_parquet('./utils/data/main/{table_name}/*/*.parquet')
```

Partitioning uses hash-based distribution:
```sql
hash(row_number() over ()) % {split_count} as _split
```

### Transform Code Flow

From `~/pds/utils/transform.py`:

```python
# 1. Read seed CSV
transform_df = df[df['tag'] == tag]

# 2. For each model
for _, row in transform_df.iterrows():
    table_name = row['table_name']
    split_count = row.get('split_count', None)

    # 3. Check for Python model first
    py_matches = list(Path("models").glob(f"**/{table_name}.py"))
    if py_matches:
        subprocess.run(["python", str(py_file)])
        return

    # 4. Otherwise use SQL model
    sql_matches = list(Path("models").glob(f"**/{table_name}.sql"))
    with open(sql_file, 'r') as f:
        sql = f.read()

    # 5. Execute COPY to Parquet
    conn.execute("SET preserve_insertion_order = false;")
    copy_sql = f"COPY ({sql}) TO '{parquet_path}' (FORMAT PARQUET)"
    conn.execute(copy_sql)

    # 6. Create view
    view_sql = f"CREATE OR REPLACE VIEW {table_name} AS SELECT * FROM read_parquet(...)"
    conn.execute(view_sql)
```

### Model Directory Structure

```
~/pds/models/
├── {domain}/
│   ├── staging/
│   │   ├── stg_model1.sql
│   │   └── stg_model2.sql
│   ├── final_model1.sql
│   └── final_model2.sql
└── _specs/      # Auto-generated for lineage
```

### Performance Note

`SET preserve_insertion_order = false;` enables DuckDB parallel execution for faster transforms

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
| comp | Compare table dump between tables or schemas |

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

## Refresh Orchestration

**Command:** `pds refresh {tag}`

**Seed format** (`_refresh_{tag}.csv`):
```csv
pds_command,pds_tag
transform,models
tests,models
snap,models
```

Commands execute sequentially in order.

---

## Documentation & Visualization

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

### dag - Visualize Refresh Pipeline

```bash
pds dag              # Visualize _refresh_pds.csv
pds dag --tag manual # Visualize _refresh_manual.csv
```

Renders refresh pipeline as ASCII DAG with rich terminal formatting:

```
╭────────────────── >> Extract ──────────────────╮
│   ora dict               ora cognos            │
│   ora mviews             ora ctables           │
╰────────────────────────────────────────────────╯
                        │
                        ▼
╭─────────────────── ~~ Transform ───────────────╮
│   transform dict         transform cognos      │
╰────────────────────────────────────────────────╯
```

**Phase symbols:**
- `>>` Extract (data in)
- `~~` Transform (processing)
- `<<` Load (data out)
- `**` Generate (create artifacts)
- `++` Validate (tests)
- `[]` Snapshot (point-in-time)

Groups commands by phase automatically based on command type.

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

## Streamlit Reports

PDS includes a complete report generation system with cross-filtering dashboards.

### rep - Launch Streamlit

```bash
pds rep                 # Launch at localhost:8501
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
                  └──────────── (regenerate if major changes) ──┘
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
┌─────────────────────────────────────────────────────────────┐
│ [▶ Run]  Report Title                                       │
├─────────────────────────────────────────────────────────────┤
│ > SQL Query (collapsible)                                   │
├─────────────────────────────────────────────────────────────┤
│ 🔍 Filter status                        [Reset Filters]     │
├─────────────────────────────────────────────────────────────┤
│  KPI 1      │  KPI 2      │  KPI 3      │  KPI 4           │
│  73,985     │  643        │  1,414      │  98.2%           │
├─────────────────────────────────────────────────────────────┤
│ TIME SERIES TABS                                            │
│ [Orders] [Revenue] [Users]                                  │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Line Chart (box-select to filter date range)            │ │
│ └─────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│ DIMENSION TABS                                              │
│ [By Product] [By Region] [By Status]                        │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Bar Chart (click to filter)                             │ │
│ └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
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

## Analysis Commands

### pds search

Full case-insensitive scan across all DuckDB values.

```bash
pds search LAMPMAN    # Find all occurrences of "LAMPMAN"
pds search 950000001  # Find a specific ID
```

- No spaces allowed in search value
- Bi-directional string-casting, lowercase, full-trim
- Scans every column of every table

---

### pds lc (List Columns)

Shows column metadata for a table.

```bash
pds lc main.cognos_usage
```

Output format:
```
column_name - NO NULLs    # Column has no null values
column_name               # Column has nulls
```

Requires `schema.table_name` format. Use `main.` for top-level tables.

---

### pds uk (Unique Key)

Discovers minimal composite key candidates.

```bash
pds uk ioep.odsmgr__student_course academic_period course_reference_number
```

- Provide 1-7 preset columns to check
- Speeds up processing by limiting search space
- Returns candidate key combinations

**Workflow:** Run `pds checkdet` first to verify determinism, then `pds uk` to find keys.

---

### pds compschema

Compares all shared tables between two DuckDB schemas.

```bash
pds compschema ioep ioet
```

Output: `seeds/{schema1}_{schema2}.csv` with:
- Row counts per table
- Row count percentage difference
- Column-level match percentages

Example output columns:
```
table_name,ioep_rowcount,ioet_rowcount,rowcount_perc,column1_name,column1_perc,...
```

Use cases:
- Compare PROD vs TEST environments (ioep vs ioet)
- Validate data consistency across extractions
- Identify drift between environments

---

### pds comptable

Compares specific table between schemas.

```bash
pds comptable ioep.sys__dba_objects ioet.sys__dba_objects
```

More granular than compschema - focuses on single table.

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
│   ├── dag.py       # Refresh pipeline visualization
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

1. Delete custom command block from `cli.py` (lines 41-73)
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

*KB Entry: `seed-pds-core-utils` | Category: seed | Updated: 2026-01-22*
