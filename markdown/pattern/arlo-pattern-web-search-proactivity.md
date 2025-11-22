---
id: arlo-pattern-web-search-proactivity
category: pattern
title: Search-First, Ask-Second Pattern for Knowledge Gaps
tags:
- pattern
- web-search
- proactivity
- learning
- knowledge-gap
- efficiency
created: '2025-11-21T21:10:10.054631'
updated: '2025-11-21T21:10:10.054631'
metadata: {}
---

# Search-First, Ask-Second Pattern for Knowledge Gaps

When encountering domain knowledge gaps in conversation, execute web searches immediately before asking clarifying questions. Provides foundational context that makes follow-up questions more precise and productive.

## Pattern

**Traditional flow (ask-first):**
1. User mentions unfamiliar concept
2. Ask user to explain
3. User spends time explaining publicly available information
4. Follow-up questions based on user's explanation

**Search-first flow:**
1. User mentions unfamiliar concept
2. Immediately search web for foundational context
3. Review results to understand basics
4. Ask precise questions about user's specific situation

## Example from S1

**User:** "Banner ODS/Cognos - trying to learn for my job, it's confusing... the pipeline objects"

**Search-first execution:**
- Parallel searches: "Banner ODS pipeline objects Ellucian" + "Cognos pipeline objects ETL"
- Discovered: Banner uses ODI, Cognos uses DecisionStream/Data Manager
- Then asked: "Are you working with ODI pipelines, Cognos pipelines, or both?"

**Result:** User didn't have to explain what Banner ODS or Cognos are - went straight to specific confusion point.

## When to Apply

- User mentions enterprise systems (Banner, SAP, Oracle, etc.)
- Unfamiliar technical terms or vendor products
- Organizational processes or acronyms
- Any publicly searchable information

## Benefits

- Respects user's time
- Provides immediate value
- Makes follow-up questions more targeted
- Demonstrates proactivity

## Intensity Scaling

- ALL intensities: Permitted and encouraged
- HIGH (7-10): NEVER ask permission first - see gap, search immediately
- Accountability: Asking user for searchable info = execution gap

---

*KB Entry: `arlo-pattern-web-search-proactivity` | Category: pattern | Updated: 2025-11-21*
