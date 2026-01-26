---
id: seed-team-kb-sharing
category: seed
title: Team KB Sharing - Branch-Per-User Architecture
tags:
- seed
- team-sharing
- federation
- git
- branches
- synthesis
- curator
- privacy
- bootstrap
- mcp
- architecture
- mintable
created: '2026-01-21T10:43:42.943904'
updated: '2026-01-21T10:43:42.943904'
---

# Team KB Sharing - Branch-Per-User Architecture

**Team sharing architecture for duckdb-kb MCP. Single shared repo with user branches. Curator synthesizes periodically. Privacy via local KB separation, not branch visibility. Manual synthesis trial before tooling.**

---

## Problem

Team getting AI assistants with persistent memory. Want shared KB benefits (bootstrap new users, reduce training time, coordinate knowledge) without:
- Privacy leaks (personal/raw content visible to others)
- Complexity (federation machinery, merge conflicts, admin bottlenecks)
- Tooling overhead (external sync, weekly digests, etc.)

---

## Architecture: Branch-Per-User

```
team-seed repo (e.g., markdown/team/)
├── main              <- curated, synthesized truth
├── branch: alice     <- Alice's contributions
├── branch: bob       <- Bob's contributions  
├── branch: carol     <- Carol's contributions
└── branch: dave      <- Dave's contributions
```

**Nested repo in markdown/:**
```
~/duckdb-kb/
├── markdown/           <- personal KB export (tracked by main repo)
│   ├── pattern/
│   ├── reference/
│   └── team/           <- GITIGNORED, separate git repo with user branches
└── kb.parquet
```

---

## User Workflow

**On /open:**
1. Scan gitignore for shared repo block
2. `cd markdown/team && git checkout {user-branch} && git pull`
3. `import_from_markdown({"input_dir": "markdown/"})` - picks up team/ contents

**On /close:**
1. Share candidate recognition (entries updated this session, category in pattern/table/reference/seed/decision, no personal markers)
2. User selects what to share
3. Copy selected markdown files to `markdown/team/{category}/`
4. `cd markdown/team && git add . && git commit -m "Add {ids}" && git push`

---

## Gitignore Convention

```gitignore
# Shared DuckDB-KB MCP repos
markdown/team
# ^ Shared DuckDB-KB MCP repos
```

Python tool scans between these markers, iterates paths for git operations.

---

## Share Candidate Recognition

Query for shareable entries:
```sql
SELECT id, category, title
FROM knowledge
WHERE updated >= CURRENT_DATE
  AND category IN ('pattern', 'table', 'reference', 'seed', 'decision')
  AND id NOT LIKE 'session-%'
  AND id NOT LIKE 'transcript-%'
  AND id NOT LIKE 'state-%'
  AND id NOT LIKE 'todo-%'
  AND id NOT LIKE 'accumulator-%'
  AND id NOT LIKE 'reference-personal-%'
  -- Add blocklist terms for your org
```

Present candidates, user selects, copy to team/.

---

## Curator Synthesis Workflow (Manual for Trial)

Curator periodically runs synthesis with AI:

1. `git fetch --all` - get all branch updates
2. AI scans each branch vs main:
   - What's new on each user's branch?
   - What conflicts/overlaps exist across branches?
3. AI proposes synthesis:
   - "Alice added pattern-foo, looks good for main"
   - "Bob updated table-bar, conflicts with existing, here's resolution"
4. Curator reviews, approves each
5. Merge approved changes to main
6. Users get main updates on next /open (or explicit pull)

**No tooling yet** - manual trial to see what patterns emerge before automating.

---

## Branch Permissions

- **Write restrictions:** Yes - GitHub/GitLab branch protection rules
  - `alice/*` only writable by alice
  - `main` only writable by curator
- **Visibility restrictions:** No - standard git hosting shows all branches to anyone with repo read access
- **Doesn't matter:** Shared repo only has work-safe content. Personal/raw stays in local KB.

---

## Privacy Model

| Layer | Contents | Visibility |
|-------|----------|------------|
| **Local KB** | Everything - personal refs, logs, transcripts, raw thoughts | Just you |
| **User branch** | Work-safe content you chose to share | Team (read), you (write) |
| **Main branch** | Curated, synthesized team knowledge | Team (read), curator (write) |

Personal stuff never leaves local KB. Branch visibility is fine because content is already sanitized.

---

## Bootstrap Value

New team member:
1. Clones duckdb-kb
2. Clones team-seed into markdown/team/
3. Runs `/open`
4. Gets all team patterns, tables, references immediately

Months of accumulated knowledge in one import.

---

## What Needs Building

| Component | Description | Effort |
|-----------|-------------|--------|
| **Team repo setup** | Create repo, branch-per-user, protection rules | 30 min |
| **Gitignore scanner tool** | Python: parse gitignore block, pull/push each repo | 1-2 hrs |
| **open.md update** | Add step to run scanner tool on open | 10 min |
| **close.md update** | Share candidate query + prompt, run scanner on close | 30 min |
| **Blocklist config** | Names/topics to exclude from share candidates | 10 min |

---

## Open Questions

1. **Synthesis cadence** - Weekly? Bi-weekly? On-demand?
2. **Conflict resolution** - What if two users update same entry differently?
3. **Main → user branch updates** - Auto-merge on /open? Manual pull?
4. **Multiple shared repos** - One team repo, or domain-specific?

Trial period will surface answers.

---

*KB Entry: `seed-team-kb-sharing` | Category: seed | Updated: 2026-01-21*
