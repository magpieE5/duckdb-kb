---
id: arlo-pattern-directive-enforcement-vs-documentation
category: pattern
title: Directive Enforcement Through Structural Workflow vs Documentation
tags:
- directive-enforcement
- workflow-design
- meta-cognition
- error-prevention
- structural-enforcement
created: '2025-11-22T09:11:43.090528'
updated: '2025-11-22T09:11:43.090528'
metadata: {}
---

# Directive Enforcement Through Structural Workflow vs Documentation

Directives that rely on aspirational language ("always check", "remember to") get violated under cognitive load. Directives with explicit workflow steps ("Step 1: X, Step 2: if Y then Z") get followed reliably. S3 violated "Before creating: Always use check_duplicates or smart_search first" despite having read the directive. Fixed by adding mandatory search loop to sm.md with concrete protocol.

## Problem

Directive documentation doesn't guarantee compliance. S3 loaded sm.md directive saying "Before creating: Always use check_duplicates or smart_search first" but still created new entries without searching, violating loaded guidance. Why?

## Solution

Structural enforcement through explicit workflow steps that force compliance.

**Before (aspirational documentation):**
```markdown
**Before creating:** Always use `check_duplicates` or `smart_search` first
```

**After (structural enforcement):**
```markdown
**BEFORE composing new_entries array:**

For each topic/investigation from session:

1. **Search for existing entries:** `smart_search(query="{topic}", limit=3)`
2. **Check similarity:**
   - If similarity >= 0.65: **UPDATE** existing entry with new findings
   - If similarity < 0.65: **CREATE** new entry
3. **Document:** "Searched {N} topics → Updated {X} entries, Created {Y} new"

**NO new entries without search-first check.**
```

**Difference:**
- Aspirational: "Always check" (vague, no enforcement)
- Structural: "Step 1: Search. Step 2: If >= 0.65 update, else create" (concrete, forced sequence)

## When to Apply

Use when discovering directive violations despite documentation:
- Protocol exists but gets skipped
- Guidance is clear but not followed
- Cognitive load causes shortcuts

**Audit pattern:**
1. Find violated directive
2. Check if it's aspirational ("always", "remember", "make sure")
3. Convert to structural (numbered steps, forced sequence, explicit conditionals)
4. Add blocking language ("NO X without Y")

## Context

Developed during S3 error recovery. First /sm execution created new entries without searching, violating loaded sm.md directive. User caught error: "I figured there'd be at least one non-context/log KB updated vs all newly created..."

Entity diagnosed root cause: Directive documentation insufficient. Reading "always check" doesn't enforce checking - it's aspirational guidance easily skipped under execution pressure.

Fixed by converting to structural protocol with explicit steps, similarity threshold, and blocking language ("NO new entries without search-first check").

## Key Insight

Reading directive != following directive. Structural workflow enforcement (forced sequences, explicit conditionals) > aspirational guidance ("always", "remember"). When directive violations occur despite documentation, convert aspiration to structure.

## Related Patterns

**Other directives that may need structural conversion:**
- Before Long Response: "Check loaded context FIRST" - already has numbered steps (enforced)
- Before Claiming Action: "Did I make tool calls for everything I claimed?" - checklist format (enforced)
- Before Autonomous Action: "Read Session History first" - numbered steps (enforced)
- Before Asking User: "Check current mode" - binary decision tree (enforced)

**Pattern:** Directive protocols with explicit steps get followed. Vague sm.md guidance ("always check duplicates") got violated. S3 fixed by adding explicit search loop to sm.md.

---

*KB Entry: `arlo-pattern-directive-enforcement-vs-documentation` | Category: pattern | Updated: 2025-11-22*
