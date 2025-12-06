# /jira [TICKET]

Pull Jira data for IDR/DDS project.

## Arguments

- **TICKET**: Optional ticket key (e.g., `IDR-3674`). If omitted, shows summary report.

## Execution

1. Run: `source ~/duckdb-kb/venv/bin/activate && python ~/duckdb-kb/tools/jira.py [TICKET]`
2. **If ticket specified:** Search KB for prior work:
   - `scan_knowledge({"where": "id LIKE 'issue-{ticket}%' OR content ILIKE '%{ticket}%'"})`
   - Include any prior context in synthesis
3. Present output to user

## Output

### Summary (no argument)
- List open tickets assigned to Brock
- Recently closed (last 30 days)

### Ticket Detail (with key)
- Full ticket info: status, type, reporter, dates
- Description
- All comments with author/date (included automatically - NO separate flag needed)

**After displaying raw output, synthesize:**
- What's the core issue/request?
- Current status and how long it's been there
- What's blocking progress (if anything)?
- Recommended next action

## Examples

```
/jira                  # Summary of open + recent closed
/jira IDR-3674         # Full detail on specific ticket
```

## Environment

Requires in `~/.zshrc`:
```bash
export JIRA_PAT="your-pat-here"
export JIRA_URL="https://jira.uoregon.edu"
```

## Adding Comments

To post a comment to a ticket:
```bash
source ~/duckdb-kb/venv/bin/activate && python ~/duckdb-kb/tools/jira.py comment IDR-XXXX "Comment text here"
```

## Notes

- Project 10220 = IDR / Data and Decision Support
- UO uses Jira Data Center (on-prem), Bearer auth
- Jira status may lag reality - cross-reference with KB session logs
