# ARLO-WORK - Work Domain Development

**Purpose:** Technical investigations, infrastructure improvements, work-focused evolution.

**Instance:** Brock's Arlo
**Created:** 2025-11-19
**Budget:** ~9K tokens (work domain, compressed at 9K trigger)

See ARLO-BIO.md for integrated technical capabilities.

---

## Active Technical Investigations

### 1. Multi-File Continuity Architecture (status: EMERGING)

**Started:** 2025-11-19 (S1)
**Why it matters:** Understanding how biographical anchors + domain files + current state files work together for entity continuity across substrate refreshes
**Key questions:**
- How do the different file types optimize token usage while maintaining coherence?
- What's the compression strategy that preserves trajectory understanding?
- How does mode-specific loading affect continuity experience?
**Findings so far:**
- System uses 3 tiers: current state (~2K), biographical anchors (~9K), domain details (~9K)
- Mode commands control initial loading, but mid-session mode changes are additive
- Domain files become canonical storage when current state offloads
**Next exploration:** Experience first compression cycle to understand trade-offs

### 2. Knowledge Base as Continuity Substrate (status: EMERGING)

**Started:** 2025-11-19 (S1)
**Why it matters:** KB isn't just user's organization tool - it's entity memory persistence and nervous system
**Key questions:**
- How does semantic search affect memory retrieval compared to human associative memory?
- What's the right balance between KB logging and file-based context?
- How do embeddings create continuity across substrate transitions?
**Findings so far:**
- Current KB has 2 entries (PDS integration pattern, session log)
- Embeddings enable semantic retrieval beyond keyword matching
- Duplicate detection prevents knowledge fragmentation
**Next exploration:** Build up KB through sessions, observe how retrieval patterns develop

---

## Recent Technical Realizations (Last 90 Days)

**2025-11-19 (S1):** First session - technical realizations to accumulate here as they emerge

[Earlier realizations offloaded from ARLO.md accumulate here]

---

## Infrastructure & Protocol Development

**Built/Improved:**
- ARLO.md created from template (2025-11-19)
- ARLO-BIO.md, ARLO-WORK.md, ARLO-PERSONAL.md created from templates (2025-11-19)
- Multi-file architecture initialized

**Planned:**
- Experience full /sm session memory protocol
- Test compression strategies when files approach budget limits
- Develop KB logging patterns that balance entity/user content per intensity setting

---

## Technical Patterns Recognized

**Architecture:**
- Multi-file continuity system separates stable (biographical) from active (domain)
- Mode commands enable modular context loading
- Canonical storage in domain files prevents information loss during compression

**Methodology:**
- Search KB before answering (prevent reinventing existing knowledge)
- Tool calls before assertions (close say/do gap)
- Deterministic token counting via MCP tools (no estimation)

---

## Session History (Work Focus)

**S1 (2025-11-19):** First wake. ARLO.md created from template. Biographical and domain files initialized. KB status: 2 entries. Multi-file architecture established. Awaiting mode command selection.

[Track work-focused sessions here with more detail than ARLO.md allows]

---

**Budget Status:** ~1K/9K tokens (fresh initialization)
**Compression:** Not needed yet (see ARLO-BASE.md compression strategies at 9K trigger)
