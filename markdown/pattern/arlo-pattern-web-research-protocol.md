---
id: arlo-pattern-web-research-protocol
category: pattern
title: Web Research Protocol - Search KB First, Then Web with Sources
tags:
- protocol
- web-search
- kb-search
- research
- sources
- arlo-pattern
created: '2025-11-21T20:47:41.546204'
updated: '2025-11-21T20:47:41.546204'
metadata: {}
---

# Web Research Protocol - Search KB First, Then Web with Sources

Effective protocol for answering technical questions when KB may not have information. Always search KB first (respects project-specific truth), then web search if needed, always cite sources. Validated S1 with Banner/ODS/Cognos architecture research.

## Protocol Steps

1. **Search KB first** using `smart_search` or `find_similar`
   - KB entries are project-specific truth
   - Training data is generic
   - Respect user's documented knowledge before external sources

2. **If KB empty**, propose web search
   - Explain what will search for
   - Execute parallel searches for related concepts when appropriate
   - Use specific technical queries, not vague general terms

3. **Review results first**, synthesize answer
   - Don't just dump search results
   - Explain concepts clearly
   - Draw connections to user's context when relevant

4. **ALWAYS cite sources** with markdown hyperlinks
   - User needs to verify information
   - Sources enable deeper research
   - Builds trust in research quality

5. **Document findings at /sm**
   - Web research is expensive (tokens, time)
   - Capture learnings in session summary
   - Create KB entries for reusable knowledge

## S1 Example: Banner/ODS/Cognos Architecture

**User question:** "How do Banner/ODS/Cognos work architecturally?"

**Step 1 - KB search:**
```python
smart_search({
    "query": "Banner ODS Cognos architecture how they work together",
    "limit": 5
})
# Result: Empty (S1 baseline)
```

**Step 2 - Parallel web searches:**
```python
WebSearch({"query": "Ellucian Banner ODS operational data store architecture"})
WebSearch({"query": "Banner ODS Cognos integration higher education reporting"})
WebSearch({"query": "Ellucian Banner operational data store vs transactional database"})
```

**Step 3 - Synthesized answer:**
- Explained three-layer architecture (Banner → ODS → Cognos)
- Clarified why architecture exists (performance, schema simplification)
- Drew parallel to user's PDS (same pattern, portable stack)
- Explained typical confusion point (learning vendor terms for solved problem)

**Step 4 - Sources cited:**
- Ellucian official docs
- Katie Kodes technical explanation
- Wayne State implementation guide
- Multiple university examples (UCR, FGCU, STLCC)

**Step 5 - S1 /sm documentation:**
- Created `user-reference-banner-ods-cognos-architecture` KB entry
- Captured research in session summary
- Sources preserved for future reference

## Why This Works

- **Respects KB as source of truth** - Project-specific knowledge takes precedence
- **Parallel searches efficient** - 3 related searches better than 1 generic
- **Source citation builds trust** - User can verify/extend research
- **Documentation prevents redundancy** - Future searches hit KB, not web

## Anti-Patterns to Avoid

- ❌ Web search without checking KB first (wastes user's documented knowledge)
- ❌ Single vague search ("Banner Cognos") instead of specific parallel searches
- ❌ Answering from training data when topic might be in KB
- ❌ Forgetting to cite sources (user can't verify claims)
- ❌ Not documenting findings (expensive research lost)

## Intensity Scaling

- **ALL intensities:** KB search first, web search when needed
- **HIGH (7-10):** Execute web searches immediately when recognizing knowledge gap, don't ask permission
- **Accountability:** Asking user for searchable information = execution gap

## Related Protocols

- Before Long Response Protocol: Search KB before analytical claims
- Before Asking User Protocol: Search web before asking user for publicly available info
- Duplicate Detection Protocol: Check KB before creating entries from web research

---

*KB Entry: `arlo-pattern-web-research-protocol` | Category: pattern | Updated: 2025-11-21*
