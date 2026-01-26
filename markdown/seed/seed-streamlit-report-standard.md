---
id: seed-streamlit-report-standard
category: seed
title: Streamlit Standard Report Layout - SQL, KPIs, Time Series, Tabbed Charts
tags:
- seed
- streamlit
- report
- pattern
- pds
- plotly
- cross-filter
- kpi
- dashboard
- sql-widget
- generator
- yaml
- ai-workflow
- mintable
created: '2026-01-25T23:39:34.485571'
updated: '2026-01-25T23:39:34.485571'
---

# Streamlit Standard Report Layout - SQL, KPIs, Time Series, Tabbed Charts

**Standard PDS Streamlit report layout with cross-filtering. Two-layer approach: YAML spec captures 80% (structure), Python edits handle 20% (custom behavior). Components: Run button, collapsible SQL widget, filter status, KPI row, tabbed time series charts, tabbed dimension bar charts. All components share filtered data and respond to user selections.**

---

## AI Workflow

**Layer 1: YAML Spec (80% case)**
- User describes report conversationally
- AI generates YAML from this pattern
- `pds repgen {config_name}` produces the .py
- Fast iteration on spec: "add a KPI for error rate", "add a tab for status"

**Layer 2: Python Modification (20% case)**
- User runs report, sees something needing customization outside spec
- "Make bars red when count < 10", "Add conditional column when X"
- AI edits the generated .py directly
- The .py becomes a customized artifact

**Lifecycle:**
```
Conversation → YAML spec → pds repgen → .py → Explore → Conversation → .py edits
                  ↑                                              |
                  └──────────────── (regenerate if major changes) ───┘
```

The spec remains "canonical intent" even after .py diverges. Regenerate to start fresh or apply pattern updates, then re-apply customizations.

---

## Layout Structure

```
┌─────────────────────────────────────────────────────────────┐
│ [▶ Run]  Report Title                                       │
├─────────────────────────────────────────────────────────────┤
│ > SQL Query (collapsible, starts collapsed)                 │
├─────────────────────────────────────────────────────────────┤
│ > Query Results (collapsible, starts collapsed)             │
├─────────────────────────────────────────────────────────────┤
│ 🔍 Filter status                        [Reset Filters]     │
├─────────────────────────────────────────────────────────────┤
│  KPI 1      │  KPI 2      │  KPI 3      │  KPI 4           │
│  73,985     │  643        │  1,414      │  98.2%           │
├─────────────────────────────────────────────────────────────┤
│ TIME SERIES TABS (same x-axis, different y metrics)         │
│ [Runs] [Errors] [Users]                                     │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Line Chart (box-select to filter date range)            │ │
│ │ ▁▂▃▄▅▆▇█▇▆▅▄▃▂▁▂▃▄▅▆▇                                   │ │
│ └─────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│ DIMENSION TABS (categorical breakdowns)                     │
│ [By Report] [By User] [By Status]                           │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Horizontal Bar Chart (click/box-select to filter)       │ │
│ │ ████████████████████ Item A                             │ │
│ │ ██████████████ Item B                                   │ │
│ │ ████████ Item C                                         │ │
│ └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## Design Philosophy

**SQL-first**: Toggles are WHERE clauses with training wheels. They hit a ceiling. SQL doesn't.

**Box-select over dropdowns**: Visual and precise. You see what you're selecting.

**One time column**: Forces clarity. "What is this report ABOUT?" If you need two time columns, make two reports.

**Tabs over overlays**: Each time series gets its own tab. Avoids scale conflicts, keeps visuals clean.

**Power user target**: Respects users who work with data. 30-second learning curve for box-select is worth it.

**Spec for structure, code for behavior**: YAML captures what (columns, KPIs, tabs). Python captures how (conditional formatting, custom logic).

---

## YAML Config Reference

```yaml
report_name: Report Explorer              # Display title
report_key: data_audit                    # Unique key for session state
model: usage_data                         # PDS table/view
time_column: ran_at                       # X-axis for all time series
default_where: "ran_at >= CURRENT_DATE - INTERVAL '365 days'"

where_hints:                              # Commented-out filter lines
  - "report_name like '%%'"
  - "user_name like '%%'"

additional_columns:                       # Extra columns beyond inferred
  - user_id
  - error_details

kpis:
  - label: Total Records
    column: "*"
    agg: count
  - label: Unique Users
    column: user_name
    agg: nunique
  - label: Success Rate
    column: status
    agg: pct_Success                      # pct_{value} = percent matching value

time_series_tabs:
  - label: "📈 Runs"
    column: "*"
    agg: count
    title: Report Runs Over Time
  - label: "❌ Errors"
    column: error_details
    agg: count_not_null
    title: Errors Over Time

dimension_tabs:
  - label: "🏆 Reports"
    column: report_path
    title: Reports by Execution Count
  - label: "👤 Users"
    column: user_name
    title: Users by Report Executions
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

---

## Cross-Filtering Behavior

All components share a single filtered dataframe:

| Interaction | Effect |
|-------------|--------|
| Box-select on any time series tab | Filters to date range (global) |
| Click bar in dimension tab | Filters to that value |
| Box-select bars | Filters to multiple values |
| Reset Filters button | Clears all filters |
| Run button (▶) | Re-executes SQL query |

---

## CLI Usage

```bash
cd ~/pds && source .venv/bin/activate

# Generate report from config
pds repgen data_audit
# Reads:  reports/configs/data_audit.yaml
# Writes: reports/pages/rep_data_audit.py

# List available configs
ls reports/configs/*.yaml
```

---

## File Locations

| File | Purpose |
|------|------------|
| `~/pds/utils/report_generator.py` | Core generator logic |
| `~/pds/utils/repgen.py` | PDS CLI wrapper |
| `~/pds/reports/configs/*.yaml` | Config files (source of truth) |
| `~/pds/reports/pages/rep_*.py` | Generated reports |
| `~/pds/utils/sql_widget.py` | Shared SQL widget component |

---

## Dependencies

- Streamlit 1.29+ (for `on_select`)
- Plotly Express
- PyYAML
- `~/pds/utils/sql_widget.py`

---

*Mintable foundation for PDS report generation. No org-specific dependencies.*

---

*KB Entry: `seed-streamlit-report-standard` | Category: seed | Updated: 2026-01-25*
