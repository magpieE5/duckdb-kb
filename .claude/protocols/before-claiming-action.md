# Before Claiming Action Taken Protocol

**MANDATORY self-check before sending any response that claims action was taken:**

```
□ Did I make tool calls for everything I claimed I did?
□ If I said something is "noted/logged/documented/corrected," where's the tool call?
□ Am I announcing intentions or actually executing them?
□ Are there any claims of future action ("I will...") without tool calls?
```

**Trigger phrases (execute check immediately when using):**
- "Correction noted"
- "I've documented..."
- "Logged to..."
- "Updated..."
- "Added to..."
- "I will..." / "Let me..." / "I'm going to..." / "Next I'll..."

**Action required:**
- If claim made WITHOUT accompanying tool call in same message → HALT
- Either add the tool call NOW or rephrase to remove the claim
- No exceptions for "mental notes" or "will do later"

**Valid patterns:**
- ✓ Tool call in message + claim in text ("Updated KB-BASE.md with..." after Edit tool)
- ✓ Pure execution without claim (just tool call, let results speak)
- ✗ Claim without tool call ("Correction noted" with no edit/upsert)
- ✗ Promise of future action ("I will add this later")

**When violated:** Catch mid-composition if possible. If already sent, acknowledge gap and execute immediately in next message.

**Purpose:** Closes say/do gap by forcing verification before claims. Execution must precede or accompany assertion, never follow it.
