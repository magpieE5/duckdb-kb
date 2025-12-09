# /kba [SCOPE]

KB health check.

## Arguments

- **SCOPE**: Optional free-form filter. Interpret as category, tag, topic, or ID pattern. Examples: `log`, `pattern`, `cognos`, `report-finance`, `pds`. If omitted, limit to 50 recent entries to avoid excessive output.

## Execution

1. Parse SCOPE to build appropriate `scan_knowledge` WHERE clause
2. Identify inconsistencies, stale content, drift, or fragmentation
3. For full audit (no scope), analyze logs since last foundations update
4. Fix what's obvious, flag what needs discussion
