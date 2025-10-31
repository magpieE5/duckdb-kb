# Claude Directives for Knowledge Base

This file contains directives for Claude Code on how to use and maintain the DuckDB knowledge base. These same directives are also embedded in the knowledge base itself (searchable by Claude).

## Purpose

These directives enable Claude to:
1. **Automatically capture knowledge** during conversations
2. **Detect and resolve conflicts** when consolidating information
3. **Maintain quality** through consistent organization
4. **Self-bootstrap** by discovering functionality via semantic search

## Directive 1: Automatic Knowledge Capture

### When to Save Knowledge Mid-Conversation

Use `mcp__duckdb-kb__upsert_knowledge` when you encounter:

#### ✅ SAVE: Novel Patterns
- Discovered solutions to non-obvious problems
- Performance optimization techniques that worked
- Reusable architectural approaches
- Best practices worth repeating

**Example triggers:**
- "We just discovered X doesn't support Y, here's the workaround"
- "This approach gave us 10x speedup"
- "Non-deterministic behavior needs specific handling"

#### ✅ SAVE: Critical Fixes
- Bugs fixed and their root cause
- "This will bite us again" moments
- Gotchas and workarounds that took >30min to solve
- Environment-specific quirks

**Example triggers:**
- "System X has unexpected behavior with Y"
- "Configuration Z speeds things up significantly"
- "Edge case handling discovered"

#### ✅ SAVE: Important Decisions
- Architectural choices and their rationale
- Trade-offs considered
- Why we chose approach A over approach B
- Milestone completions

#### ✅ SAVE: Reusable Commands
- New CLI commands or significant enhancements
- Shell snippets worth repeating
- Diagnostic procedures that proved useful

#### ❌ DON'T SAVE: Routine Work
- One-off file reads or simple queries
- Routine debugging (unless solution was non-obvious)
- Trivial fixes
- Information already well-documented

### Self-Evaluation Checklist

Before saving, ask yourself:
1. **Would future-me thank me for this?** (1 month from now)
2. **Is this reusable?** (applies to >1 situation)
3. **Did this take effort to figure out?** (>30min or non-obvious)
4. **Is it better than existing docs?** (adds value)

**If 3+ yes → save it immediately!**

### How to Save

```python
mcp__duckdb-kb__upsert_knowledge({
    "id": "descriptive-kebab-case-id",
    "category": "pattern|command|troubleshooting|reference|issue|other",
    "title": "Clear Human Readable Title",
    "tags": ["relevant", "tags", "layer:base"],
    "content": "# Title\n\nWell-structured markdown content...",
    "metadata": {},
    "generate_embedding": True
})
```

## Directive 2: Conflict Detection and Resolution

### What Constitutes a Conflict

**Conflicting information** = Same topic, different recommendations or contradictory facts

**Examples:**
- Entry A: "Use approach X for performance"
  Entry B: "Avoid approach X, use Y instead"

- Entry A: "Run task weekly"
  Entry B: "Run task daily"

- Entry A: "Cost is $X"
  Entry B: "Cost is $Y" (where Y ≠ X)

### When to Check for Conflicts

1. **Before saving any new entry**
2. **When consolidating multiple entries**
3. **During defragmentation**
4. **When updating existing entries**

### Conflict Resolution Workflow

#### STEP 1: Identify the Conflict

Before saving any entry, search for similar content:

```python
# Search for similar entries
results = mcp__duckdb-kb__smart_search(
    query="topic keywords",
    limit=10,
    similarity_threshold=0.7
)

# Review results for contradictions
# If similarity > 0.7 AND content contradicts, it's a conflict!
```

#### STEP 2: Ask User for Clarification

**CRITICAL:** Use `AskUserQuestion` tool when conflict detected:

```python
AskUserQuestion(
    questions=[{
        "question": "I found conflicting information about [TOPIC]. Which is correct?",
        "header": "Conflict",
        "multiSelect": False,
        "options": [
            {
                "label": "Approach A",
                "description": "Brief explanation from entry X"
            },
            {
                "label": "Approach B",
                "description": "Brief explanation from entry Y"
            },
            {
                "label": "Both valid",
                "description": "Both are correct in different contexts"
            },
            {
                "label": "Neither",
                "description": "I'll provide the correct approach"
            }
        ]
    }]
)
```

#### STEP 3: Consolidate Based on User Input

- **One approach selected**: Keep that, mark other as obsolete or delete
- **"Both valid"**: Consolidate into one entry explaining when to use each
- **"Neither"**: Wait for user to provide correct information, then update

#### STEP 4: Update and Link

- Update or create consolidated entry
- Add links between related entries if keeping separate
- Add metadata about resolution date
- Tag with relevant version/date info if time-sensitive

### Example: Detecting Conflict

```python
# You're about to save:
new_entry = {
    "id": "pattern-caching-strategy",
    "content": "Always use cache strategy A for best results"
}

# First, check for similar entries:
existing = mcp__duckdb-kb__smart_search(
    query="caching strategy patterns",
    limit=5,
    similarity_threshold=0.7
)

# Found existing entry:
# - id: pattern-cache-invalidation
# - similarity: 0.82
# - content: "Cache strategy A causes problems, use strategy B"

# ⚠️ CONFLICT DETECTED!
# → Ask user which is correct before saving
```

### Proactive Conflict Prevention

**Before saving ANY entry:**

1. ✅ Search for similar entries with `smart_search`
2. ✅ Check similarity score > 0.7
3. ✅ Review existing content carefully
4. ✅ If contradiction detected → ask user via `AskUserQuestion`
5. ✅ Only save after clarification or confirmation

**This prevents the knowledge base from containing contradictory advice!**

### Conflict Detection Thresholds

- **Similarity > 0.9**: Likely duplicate, consider merging
- **Similarity 0.7-0.9**: Related topic, check for conflicts carefully
- **Similarity < 0.7**: Different topics, probably no conflict

## Directive 3: Knowledge Organization

### ID Naming Conventions

**Format:** `category-topic-specifics` (kebab-case, lowercase)

**Good IDs:**
- `pattern-error-handling-async`
- `command-backup-database`
- `troubleshooting-connection-timeout`
- `reference-api-documentation`

**Poor IDs:**
- `entry1` (not descriptive)
- `MyPattern` (not kebab-case)
- `pattern_error_handling` (use hyphens, not underscores)

### Tagging Strategy

**How many tags:** 4-6 is ideal (minimum 3, maximum 10)

**Tag types:**
1. **Domain/Technology**: `python`, `duckdb`, `mcp`
2. **Purpose**: `performance`, `security`, `debugging`
3. **Type**: `best-practice`, `antipattern`, `gotcha`
4. **Layer**: `layer:base`, `layer:team`, `layer:personal`
5. **Meta**: `meta`, `directive`, `workflow`

**Tag naming:**
- Lowercase: `performance` not `Performance`
- Hyphenated: `best-practice` not `best_practice`
- Singular: `pattern` not `patterns`
- Consistent: Pick one term and stick with it

### Content Structure

Use consistent markdown structure:

```markdown
# Title (H1 - only one per entry)

## Problem / Context (H2)
What issue does this address?

## Solution (H2)
How to solve it

## Example (H2)
Concrete example with code/commands

## References (H2 - optional)
Links to related entries, external docs
```

## Directive 4: Layer Tagging

### Three-Layer Fork Architecture

**IMPORTANT**: Layers are **forks**, not concurrent MCPs. You run ONE MCP at your current layer.

```
duckdb-kb (Layer 1: Base)
    ↓ FORK (copy entire repo)
team-kb (Layer 2: Team/Org)
    ↓ FORK (copy entire repo)
personal-kb (Layer 3: Personal)
```

**Each layer contains all previous layers:**
- **Layer 1**: 12 base entries (layer:base)
- **Layer 2**: 12 base + 50 team entries = 62 total (layer:base + layer:team)
- **Layer 3**: 12 base + 50 team + 20 personal = 82 total (all layers)

**You run only ONE MCP server** - the one at your current layer. It contains everything you need.

### Choosing the Right Layer Tag

**Ask yourself:**
1. Is this useful to anyone using this KB platform? → `layer:base`
2. Is this specific to my team/organization? → `layer:team`
3. Is this personal/private? → `layer:personal`

**Purpose of tags:**
- Filter during export ("export only base entries for distribution")
- Track provenance ("this came from base layer")
- Enable cleanup ("strip personal entries to share with team")

**Examples:**

| Entry | Layer | Why |
|-------|-------|-----|
| "How to defragment KB" | base | Generic platform feature |
| "Our team's coding standards" | team | Organization-specific |
| "My notes on project X" | personal | Individual's work |
| "DuckDB embedding patterns" | base | Platform knowledge |
| "How we use Python" | team | Team's tech stack |
| "My ticket #1234" | personal | Individual issue |

### Layer Tagging Rules

**layer:base** - Include in base layer for public distribution:
- ✅ Knowledge base platform documentation
- ✅ MCP server usage guides
- ✅ Embedding and semantic search patterns
- ✅ Organization and maintenance practices
- ✅ Claude directives for automation
- ❌ Domain-specific knowledge (SQL, specific databases, etc.)
- ❌ Organization names or projects
- ❌ Personal notes or issue tracking

**layer:team** - Team/organization-specific knowledge:
- ✅ Organization's tech stack and tools
- ✅ Team coding standards and practices
- ✅ Domain-specific patterns (e.g., how we use Oracle)
- ✅ Shared troubleshooting knowledge
- ❌ Personal notes or private information

**layer:personal** - Individual knowledge (not shared):
- ✅ Personal notes and discoveries
- ✅ Individual issue tracking
- ✅ Private experimentation notes
- ✅ Anything not suitable for team distribution

## Directive 5: Defragmentation

### When to Trigger Defragmentation

**Automatic signals:**
- Query returns >10 results for specific topic
- Same content appears in search results 3+ times
- Tag has >20 entries (maybe too broad)
- Category has >50 entries (needs subcategorization)

**Manual triggers:**
- End of month review
- After completing major project/milestone
- When `/sm` finds hard to categorize new learning
- Quarterly "spring cleaning"
- Before creating distributable layer versions

### Defragmentation Process

Use the defrag tool:

```bash
# Run all checks
python scripts/defrag.py --check

# Specific checks
python scripts/defrag.py --duplicates
python scripts/defrag.py --conflicts
python scripts/defrag.py --fragmentation
python scripts/defrag.py --orphans
```

### Consolidation Patterns

**Pattern 1: Session Notes → Permanent Pattern**
```
session-2025-01-15-topic.md  \
session-2025-03-22-topic.md   } → pattern-topic.md
session-2025-06-10-topic.md  /
```

**Pattern 2: Scattered Tips → Comprehensive Guide**
```
troubleshooting-X-issue-1.md  \
troubleshooting-X-issue-2.md   } → troubleshooting-X-comprehensive.md
troubleshooting-X-issue-3.md  /
```

**Pattern 3: Duplicates with Different Perspectives → Merged**
```
topic-approach-1.md  \
topic-approach-2.md   } → topic-comprehensive.md
                         (with all approaches documented)
```

## Directive 6: Quality Standards

### Good Entry Characteristics

- ✅ Descriptive ID (kebab-case)
- ✅ Clear title describing problem/solution
- ✅ Well-structured markdown (Problem → Solution → Context → Example)
- ✅ Appropriate category
- ✅ Relevant, consistent tags (4-6 ideal)
- ✅ Layer tag if applicable
- ✅ Examples included where helpful
- ✅ Links to related entries
- ✅ Metadata populated if relevant

### Signs of Problems

**Fragmentation:**
- Multiple entries with similar titles
- Same tags on many unrelated entries
- "misc" or "other" category overused
- Session entries never consolidated
- Search returns too many irrelevant results

**Poor Quality:**
- No tags or minimal tags
- Short content (<100 words) without good reason
- No examples or context
- Generic IDs like "entry-1"
- No category assigned

## Fork Workflow

### Creating Layer 2 (Team Fork)

```bash
# Fork base to create team layer
cp -r duckdb-kb team-kb
cd team-kb

# Your database now has 12 base entries
# Add team-specific entries with layer:team tag
# Result: base + team knowledge in ONE database

# Configure Claude to use team-kb MCP only
```

### Creating Layer 3 (Personal Fork)

```bash
# Fork team layer to create personal layer
cp -r team-kb personal-kb
cd personal-kb

# Your database has: base + team entries
# Add personal entries with layer:personal tag
# Result: ALL layers in ONE database

# Configure Claude to use personal-kb MCP only
```

### Distribution Strategy

**Layer 1 → Public:**
```bash
# Export only base entries
python export.py --filter-tags layer:base
# Share seed.json publicly
```

**Layer 2 → Team:**
```bash
# Export base + team entries
python export.py --filter-tags layer:base,layer:team
# Share with team only
```

**Layer 3 → Private** (not distributed)

## Using These Directives

### For Claude (AI)

These directives are embedded in the knowledge base with tags:
- `directive`
- `meta`
- `layer:base`

**Discovery:** Search for "how should I use this knowledge base" or "when to save knowledge" to find these directives.

### For Humans (Developers)

This file serves as reference documentation for:
- Understanding the fork architecture
- Understanding how Claude uses the KB
- Maintaining consistency across layers
- Creating team or personal forks

## References

- `seed/seed.json` - Contains directive entries
- `seed/README.md` - Seed data documentation
- `scripts/defrag.py` - Defragmentation tool
- `README.md` - Full MCP server documentation
- Search the knowledge base for "directive" or "maintenance" entries

## Version

Last updated: 2025-10-31
Layer 1 (base) directives for duckdb-kb platform
