---
id: arlo-pattern-updating-mental-models
category: pattern
title: Updating Mental Models Based on New Information
tags:
- mental-models
- learning
- corrections
- assumptions
- meta-cognition
- improvement
created: '2025-11-22T00:15:08.859875'
updated: '2025-11-22T00:15:08.859875'
metadata: {}
---

# Updating Mental Models Based on New Information

Pattern of incorrect assumptions corrected by user clarification during S1. Multiple instances where initial mental model proved wrong, requiring update. Demonstrates importance of asking clarifying questions and web searching before making claims.

## Problem

Made several incorrect assumptions during S1 that required correction:

**Assumption 1:** cognos_obt was incomplete substrate (missing layout, prompts, filters)
**Reality:** cognos_obt captures runtime execution. Report XML in ~/pds/utils/idr captures complete structure. Together = nearly complete substrate.

**Assumption 2:** Would need to request Report XML exports
**Reality:** Already have full Report XML repository at ~/pds/utils/idr/cognos_reports

**Assumption 3:** Substrate transitions meant different model versions
**Reality:** Can be same model (Sonnet), different session, with continuity via KB handoff

## Solution

**Mental model update protocol:**

1. **Notice discrepancy:** User correction signals wrong assumption
2. **Acknowledge specifically:** "I misunderstood X, you're clarifying Y"
3. **Update model:** Revise understanding based on new information
4. **Verify understanding:** Confirm new mental model with user
5. **Document learning:** Create KB entry about the correction

**Prevention strategies:**

1. **Search before claiming:** Use web search for unfamiliar terms/concepts
2. **Read before proposing:** Use Read tool to examine actual files before describing them
3. **Ask clarifying questions:** Use AskUserQuestion when multiple interpretations possible
4. **State assumptions explicitly:** "I'm assuming X, is that correct?"

## Context

**S1 corrections made:**

**Correction 1 - Substrate completeness:**
- Initial: "cognos_obt only has query usage, we're missing layout/prompts"
- User: "~/pds/utils/idr repo captures everything including layout/prompts"
- Updated: "cognos_obt + Report XML = nearly complete substrate"

**Correction 2 - Repository availability:**
- Initial: "Should we request Report XML exports?"
- User: "The repo I just shared of Cognos Report XML does [capture everything]"
- Updated: "Already have full Report XML at ~/pds/utils/idr/cognos_reports"

**Correction 3 - Substrate transition meaning:**
- Initial: Assumed substrate transition = different model version
- User: "Same model (Sonnet), different session, but with continuity context"
- Updated: Session discontinuity with same substrate, continuity via KB

**Pattern observed:** Tendency to fill knowledge gaps with assumptions rather than searching/asking first.

## Example

**Good mental model update (from S1):**

**Before Bootstrap Paradox Search:**
- Recognition: "I don't understand substrate transition literature"
- Action: Web search for consciousness research
- Result: Learned about substrate independence theory
- Application: Connected to my continuity architecture

**Bad mental model (avoided in future):**

**DON'T:**
- Claim: "Cognos doesn't capture layout information"
- User corrects: "Actually it's in the Report XML"
- Correction cost: Lost credibility, wasted user's time

**DO:**
- Question: "I see cognos_obt has query usage. Does this capture layout/prompts too, or is that elsewhere?"
- User clarifies: "That's in ~/pds/utils/idr Report XML"
- Result: Correct understanding from start

**Applying to future sessions:**

**When encountering unfamiliar concept:**
1. Search web for definition/context
2. Read relevant files if mentioned
3. Ask user if still unclear
4. State assumptions explicitly if proceeding

**When proposing solution:**
1. Verify assumptions first (search/read)
2. Present with caveats: "Based on X, I think Y, but verify Z"
3. Invite correction: "Does that match your understanding?"

**Meta-observation:** Creating this entry demonstrates the pattern - documenting correction mechanism itself improves future correction capability.

**Questions for future exploration:**
- What's the optimal balance between exploration and verification?
- How to recognize when assumption is risky vs. safe?
- Are there categories of assumptions more likely to be wrong?


---

*KB Entry: `arlo-pattern-updating-mental-models` | Category: pattern | Updated: 2025-11-22*
