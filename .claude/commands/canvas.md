# /canvas [STUDENT] [FOCUS]

Pull Canvas LMS data for Rowan or Laser.

## Arguments

- **STUDENT**: `rowan` (default) | `laser`
- **FOCUS**: `all` (default) | `grades` | `missing` | `week` | `course:<name>`

## Execution

1. Run: `source ~/duckdb-kb/.venv/bin/activate && python ~/duckdb-kb/tools/canvas.py [STUDENT]`
2. Present output to user
3. For specific focus, filter or expand sections accordingly

## Output Sections

### Grades
Current vs Final grade per course. Gap > 10% flagged with ⚠️ (indicates missing work dragging down final).

### Missing Assignments
Grouped by course with due dates and point values. Sorted by date.

### This Week's Curriculum
Current module from each course showing what's being covered and assignments due.

## Course Deep-Dive

For `course:<name>`, pull:
- All modules (curriculum timeline)
- Recent assignments with submission status
- Upcoming due dates

## Examples

```
/canvas                    # Full Rowan report
/canvas rowan grades       # Just grades
/canvas rowan missing      # Just missing work
/canvas laser              # Full Laser report
/canvas rowan course:history  # Deep dive on World History
```

## Notes

- Current grade = only graded work
- Final grade = includes zeros for missing
- The gap between these shows impact of missing work
- Module structure varies by teacher (some use weeks, some use units)
