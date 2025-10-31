# Claude Code Directives for DuckDB Knowledge Base

**Version:** 1.1.0
**Last Updated:** 2025-10-31
**Project:** duckdb-kb

---

## Project Context

This is a **DuckDB Knowledge Base MCP Server** providing hybrid SQL + semantic search capabilities for AI assistants.

**Key characteristics:**
- Generic, forkable platform for knowledge management
- Seed entries demonstrating the system
- Self-documenting via semantic search
- Multi-model AI compatible

---

## MCP Tools Available

When working in this repository, you have access to these knowledge base tools:

```
mcp__duckdb-kb__*
```

**Key tools:**
- `get_stats()` - Database overview
- `find_similar(query)` - Semantic search
- `smart_search(query, filters)` - Hybrid search
- `upsert_knowledge(entry)` - Create/update entries
- `list_knowledge(filters)` - Browse entries

---

## Directives for Knowledge Base Usage

### 1. First Time Orientation

When first connecting to this project:

1. Run `mcp__duckdb-kb__get_stats({"detailed": true})` to see what's in the KB
2. Search for directives: `mcp__duckdb-kb__find_similar({"query": "how to use this knowledge base"})`
3. The KB is self-documenting - patterns and guides are searchable

### 2. Before Creating New Entries

**ALWAYS check for duplicates first:**

```
mcp__duckdb-kb__smart_search({
  "query": "your topic here",
  "similarity_threshold": 0.7
})
```

If similar entries exist (score > 0.7), **update** them instead of creating duplicates.

### 3. When to Save Knowledge

Save to the KB when you discover:

✅ **Novel patterns** - Non-obvious solutions, optimization techniques
✅ **Critical fixes** - Bugs that took >30min to solve
✅ **Important decisions** - Architectural choices and rationale
✅ **Reusable commands** - CLI snippets worth repeating

❌ **Don't save:** Routine changes, one-off bugs, obvious documentation

### 4. Entry Quality Standards

When creating entries:

- **ID format:** `kebab-case` (e.g., `pattern-error-handling`)
- **Categories:** `table`, `command`, `issue`, `pattern`, `troubleshooting`, `reference`, `other`
- **Tags:** 3-6 descriptive tags for discoverability
- **Content:** Use markdown, include Problem/Solution/Context/Example sections
- **Title:** Clear, descriptive (not just IDs)

### 5. Conflict Detection

The KB has automatic conflict detection. If you find contradictory information:

1. Use `mcp__duckdb-kb__find_similar()` to find related entries
2. Review similarity scores (>0.8 = likely duplicates)
3. Consolidate into one authoritative entry
4. Use `mcp__duckdb-kb__add_link()` to mark superseded entries

---

## Content Guidelines

When adding entries to the knowledge base:

### ✅ Prioritize Saving:
- Platform documentation (how the KB system works)
- Domain-specific patterns and solutions
- Reusable troubleshooting procedures
- Tool usage guides and commands
- Best practices and optimization techniques
- Architecture decisions and rationale

### ⚠️ Use Caution With:
- Sensitive credentials or API keys (use placeholders or environment variables)
- Private/confidential business information
- Personally identifiable information (PII)
- Time-sensitive data that will become stale quickly

**Remember:** This KB is designed to be forked and customized for different use cases (public platform knowledge, team knowledge, personal notes, etc.)

---

## Development Workflow

### Making Changes

1. **Test locally first** - Use your test database
2. **Check for regressions** - Run basic tool tests
3. **Update seed data** if adding platform features
4. **Document in KB** if adding significant functionality

### Committing Changes

Use descriptive commit messages:
```
<type>: <short description>

<detailed explanation if needed>

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

**Types:** `feat`, `fix`, `docs`, `refactor`, `test`, `chore`

### Before Pushing

1. Verify no sensitive data in commits (credentials, secrets, PII)
2. Check `.gitignore` is working (no `.duckdb` database files committed)
3. Ensure documentation is up to date
4. Test seed data import works if modified

---

## Common Tasks

### Add a New Feature

1. Implement in `mcp_server.py`
2. Test with actual MCP calls
3. Add example to seed data
4. Document in README.md
5. Update CHANGELOG if exists

### Improve Documentation

1. Check existing docs first (avoid duplication)
2. Update relevant .md files
3. Add to seed KB if it's a reusable pattern
4. Ensure examples are clear and tested

### Fix a Bug

1. Reproduce the issue
2. Add test case if applicable
3. Fix and verify
4. Document in FIXES_APPLIED.md if significant
5. Consider adding troubleshooting entry to KB

---

## Testing

### Manual Testing Checklist

After making changes, verify:

- [ ] `get_stats()` returns correct counts
- [ ] `find_similar()` returns relevant results
- [ ] `upsert_knowledge()` creates entries successfully
- [ ] Embeddings generate correctly
- [ ] Seed data imports cleanly
- [ ] Documentation is accurate

### Seed Data Testing

```bash
# Fresh database test
rm -f test.duckdb
duckdb test.duckdb < schema.sql
cd seed && python import_seed.py
# Should import all seed entries successfully
```

---

## Maintenance

### Regular Tasks

- **Monitor KB quality** - Run defrag script periodically
- **Update embeddings** - When changing seed content
- **Review directives** - Keep them current with actual usage
- **Update docs** - When adding features

### Quality Checks

Use the defragmentation tool:

```bash
python scripts/defrag.py --mode all
```

Check for:
- Duplicate entries
- Conflicting information
- Outdated content
- Missing embeddings

---

## Getting Help

**For users:**
- See QUICKSTART.md for 5-minute setup
- See README.md for complete documentation
- Search the KB itself - it's self-documenting!

**For developers:**
- See MCP_CONFIG_README.md for configuration
- See CLAUDE_DIRECTIVES.md for detailed directives
- See seed/README.md for seed data structure

---

## Version History

**v1.1.0** (2025-10-31)
- Removed layer restrictions - now fully generic and forkable
- Updated content guidelines to support any use case
- Clarified security and privacy considerations
- Improved documentation for customization

**v1.0.0** (2025-10-31)
- Initial release
- Seed entries demonstrating the system
- 10 MCP tools
- Comprehensive documentation
- Multi-model compatibility

---

**Remember:** This is a generic, forkable platform. Customize it for your needs - whether that's public platform knowledge, team documentation, or personal notes!
