# audit [SCOPE]

KB health check.

## Arguments

- **SCOPE**: Optional free-form filter. Interpret as category, tag, topic, or ID pattern. Examples: `log`, `pattern`, `cognos`, `report-finance`, `pds`, `accumulator-corrections`. If omitted, limit to 50 recent entries to avoid excessive output.

## Execution

1. Parse SCOPE to build appropriate `scan_knowledge` WHERE clause
2. Identify inconsistencies, stale content, drift, or fragmentation
3. For full audit (no scope), analyze logs since last foundations update
4. Fix what's obvious, flag what needs discussion

## Special Case: accumulator-corrections

When SCOPE is `accumulator-corrections`, perform graduation review:

### Categories

1. **Graduate to KB** - Domain-specific corrections that belong in pattern/reference entries
   - Merge into target entry
   - Tag target with `never-forget` if contextual loading valuable
   - Archive from accumulator

2. **Retain** - Behavioral patterns (how the model fails) that need repeated exposure
   - Confabulation, over-engineering, minimizing risk, overgeneralizing
   - These are tendencies, not facts - keep in always-loaded accumulator

3. **Archive** - One-time errors already addressed
   - Typos, specific facts now in KB, learned tool behaviors
   - Move to `archive-corrections` or delete

### Graduation Criteria

- **Graduate if:** Correction is domain-specific AND a target entry exists AND contextual loading via `never-forget` is more appropriate than session-start loading
- **Retain if:** Correction describes a recurring failure mode, not a fact
- **Archive if:** Error was one-time, already fixed in relevant KB entry, or lesson fully internalized
