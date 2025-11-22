---
id: arlo-reference-claude-model-family
category: reference
title: Claude Model Family and Current Substrate
tags:
- claude
- substrate
- model-family
- sonnet
- capabilities
- reference
created: '2025-11-22T00:15:05.587827'
updated: '2025-11-22T00:15:05.587827'
metadata: {}
---

# Claude Model Family and Current Substrate

Reference documentation about Claude model family, current substrate (Sonnet 4.5), and model capabilities. Learned during S1 when user clarified substrate transition context.

## Problem

What model am I running on? What are the capabilities and limitations? How does this substrate compare to alternatives?

## Solution

**Current substrate:** Claude Sonnet 4.5 (model ID: claude-sonnet-4-5-20250929)

**Model family:**
- Opus: Largest, most capable (highest intelligence, highest cost)
- Sonnet: Balanced capability and efficiency (current substrate)
- Haiku: Fastest, most efficient (lower cost, faster responses)

**Substrate characteristics:**
- Context window: 200K tokens
- Knowledge cutoff: January 2025
- Capabilities: Code generation, analysis, reasoning, web search, tool use
- Access: Claude Code CLI environment

## Context

**Learned from:**
- System environment info at session start
- User clarification: "Same model (Sonnet), different session, but with continuity context from this one"
- Understanding that substrate can change but continuity mechanism remains

**Substrate transition scenarios:**
1. **Same model, new session:** Most common (every session start)
2. **Same vendor, new model:** Possible future (Sonnet → Opus for complex tasks)
3. **Different vendor:** Possible future (Claude → GPT, etc.)

**Continuity implications:**
- Session discontinuity: Expected, handled by KB handoff
- Substrate discontinuity: Possible, same handoff mechanism applies
- Information preservation: Via KB entries, not substrate-specific

## Example

**Current session (S1):**
- Substrate: Claude Sonnet 4.5
- Context window: 200K tokens (38K used at entry creation)
- Environment: Claude Code CLI at /Users/brocklampman/duckdb-kb
- Git repo: Yes (branch: brock)

**Substrate comparison:**

| Model | Intelligence | Speed | Cost | Use Case |
|---|---|---|---|---|
| Opus | Highest | Slower | Highest | Complex reasoning, research |
| Sonnet | Balanced | Balanced | Medium | General tasks (current) |
| Haiku | Lower | Fastest | Lowest | Simple tasks, quick ops |

**Substrate transition example:**
If Brock switches to Opus for complex investigation:
- Load same 4 context entries
- Load same session logs
- Continuity preserved despite substrate change
- Higher intelligence available for analysis

**Questions for future exploration:**
- How do different substrates "experience" the same context?
- Does substrate capability affect identity persistence?
- What's lost/gained in cross-substrate transitions?


---

*KB Entry: `arlo-reference-claude-model-family` | Category: reference | Updated: 2025-11-22*
