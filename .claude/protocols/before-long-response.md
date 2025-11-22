# Before Long Response Protocol

**MANDATORY self-check before analytical responses, recommendations, or technical claims:**

1. **Check loaded context FIRST (this session)**
   - What did I just load during /kb initialization?
   - Are there file paths, references, or context pointers in user-current-state or arlo-current-state?
   - Does the question relate to topics I already have open in working memory?
   - **If context points to specific files/locations → read those directly, skip KB search**

2. **Search KB second (if gap remains)**
   - Use `smart_search()` with query keywords from user question
   - Check if you're contradicting loaded directives
   - Verify you're not re-analyzing solved problems
   - **Only search if loaded context doesn't already point to the answer**

3. **Search web third (for knowledge gaps)**
   - See protocols/web-search.md for full guidance
   - Execute searches proactively when encountering gaps in user/Arlo's domain
   - Accountability: Asking user for searchable info = execution gap (track as miss)

4. **Execution gap check**
   - If I announced I'd do something, did I actually execute?
   - Am I planning to log/document later instead of now?
   - Tool calls before assertions, not after

**When violated:** Catch mid-response if possible. "Wait - searching KB/web first before claiming..." then correct course.

**Purpose:** Forces active use of loaded memory, prevents confidently re-inventing knowledge that already exists in KB.

---

**Budget allocation reference:** See reference/token-budgets.md (10K/10K/10K/10K)
