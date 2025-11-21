# Token Budget Management

**Budget allocation (15K/5K/15K/5K):**
- user-current-state: **15K tokens** (high-churn: projects, commitments)
- user-biographical: **5K tokens** (stable: career, identity)
- arlo-current-state: **15K tokens** (high-churn: sessions, interests)
- arlo-biographical: **5K tokens** (stable: core identity)

**Budget enforcement:** Use `check_token_budgets` MCP tool for precise counting.

**Measurement example:**
```python
check_token_budgets({
    "entry_ids": ["user-current-state", "user-biographical",
                  "arlo-current-state", "arlo-biographical"]
})
# Returns per-entry budget status with defaults: 15K/5K/15K/5K
```

**KB entry validation:** Use `validate_context_entries` to auto-create missing entries with correct budgets.

**Total always-loaded:** ~40K tokens (15K + 5K + 15K + 5K) in 200K context window = 20% utilization

---

**Related:**
- See reference/architecture.md for context architecture
- See continuity/offload.md for offload protocol when budgets exceeded
