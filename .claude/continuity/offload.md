# Topic Placement & Offload Protocol

**Budget allocation (10K/10K/10K/10K):**
- user-current-state: 10K tokens (high-churn: projects, commitments)
- user-biographical: 10K tokens (stable: career, identity)
- arlo-current-state: 10K tokens (high-churn: sessions, interests)
- arlo-biographical: 10K tokens (stable: core identity)

## Autonomous Offload at Budget Cap

**Use `offload_topics` MCP tool when budget exceeded:**

```python
offload_topics({
    "entry_id": "user-current-state",
    "target_tokens": 9000,  # 10K budget with 1K margin
    "strategy": "oldest_first"
})
```

**The tool autonomously:**
1. Parses topics with timestamps
2. Sorts by date (oldest first)
3. Extracts oldest topics until under target
4. Generates KB entry suggestions
5. Returns updated content + new entry proposals

**Then:** Create suggested KB entries using returned data

---

**Related:**
- See reference/token-budgets.md for measurement
- See reference/mcp-tools.md for tool details
