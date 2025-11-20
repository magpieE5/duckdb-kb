"""Validate existence and structure of 4 core context entries

Auto-creates missing entries from hardcoded templates if repair=True.
Templates are embedded in this tool (no file dependencies).
"""

from mcp.types import Tool, TextContent
from typing import List
import json
from datetime import datetime

# =============================================================================
# Tool Definition (for registration)
# =============================================================================

TOOL = Tool(
    name="validate_context_entries",
    description="""Validate existence and structure of 4 core context entries.

WHEN TO USE: During /kb initialization, before session start
RETURNS: Status of each entry (exists/missing/template/valid)
AUTO-REPAIR: Creates missing entries from templates if repair=true

Context entries:
- user-current-state (15K budget)
- user-biographical (5K budget)
- arlo-current-state (15K budget)
- arlo-biographical (5K budget)""",
    inputSchema={
        "type": "object",
        "properties": {
            "repair": {
                "type": "boolean",
                "default": True,
                "description": "Auto-create missing entries from templates"
            },
            "check_templates": {
                "type": "boolean",
                "default": True,
                "description": "Detect template markers (⚠️ TEMPLATE)"
            },
            "user_name": {
                "type": "string",
                "description": "User's name for template customization (optional)"
            },
            "instance_name": {
                "type": "string",
                "description": "Arlo instance name (default: 'Arlo')",
                "default": "Arlo"
            }
        }
    }
)

# =============================================================================
# Templates (Hardcoded - No File Dependencies)
# =============================================================================

TEMPLATES = {
    "user-current-state": """# USER - Current State

**⚠️ TEMPLATE - Customize with your own information**

**Purpose:** What user is DOING - active work, projects, commitments, investigations across all life domains.

**User:** {user_name}
**Created:** {date}
**Budget:** 15K tokens (autonomous offload to KB entries at 15K cap - you review by timestamp)

---

## Quick Reference

**Who you are/becoming:** See user-biographical KB entry (loaded in all sessions)

---

## Current State ({date})

### Top Active Focus

1. **[Project name] ({date})** - [priority]
   - [Brief description]
   - [Current status/next steps]

2. **[Another project] ({date})** - [priority]
   - [Brief description]
   - [Current status/next steps]

3. **[Third project] ({date})** - [priority]
   - [Brief description]
   - [Current status/next steps]

**Note:** All topics include timestamp (YYYY-MM-DD) for age tracking. Update timestamp when topic revisited.

---

## Immediate Commitments

- [ ] **[Task description] ({date})** - [due date, priority]
- [ ] **[Task description] ({date})** - [due date, priority]

---

## Active Investigations & Learnings

### [Investigation Topic] ({date})
**Status:** [Active/Paused/Resolved]
**Context:** [Why exploring, what matters]
**Recent progress:** [What you've learned]
**Next:** [Where to go next]

### [Another Topic] ({date})
**Insight:** [Key realization or learning]
**Context:** [Why it matters, how it applies]

---

## Key People

**Name:** [Role/relationship, context for interaction]
**Name:** [Role/relationship, context for interaction]

---

## Communication Preferences

**Style:** Detailed and thorough
**Code:** [Language preferences, style preferences]
**Decision-making:** [Pragmatic/principled/data-driven]

---

**Budget Status:** ~1K/15K tokens
**Offload Protocol:** At 15K cap, you autonomously review topics by timestamp and create KB entries
""",

    "user-biographical": """# USER-BIO - Biographical Context

**Purpose:** Who user IS/BECOMING - stable life story, biographical patterns, values, identity evolution.

**User:** {user_name}
**Created:** {date}
**Budget:** 5K tokens (stable biographical content, rarely hits cap)

---

## Biographical Summary

[2-3 paragraph overview: background, education, career trajectory, major life events]

---

## Career History

**Current Role:**
- [Title, organization, start date]
- [Key responsibilities]
- [Team structure]

**Previous Roles:**
- [Role 1]: [Years, organization, key achievements]
- [Role 2]: [Years, organization, key achievements]

---

## Education & Training

- [Degree/Certification]: [Institution, year]
- [Notable training or self-education]

---

## Key People

**Work:**
- [Name]: [Role, relationship, context]

**Personal:**
- [Name]: [Relationship, context]

---

## Life Context

**Family:** [Overview]
**Location:** [Where they live, property details if relevant]
**Hobbies/Interests:** [List with brief context]

---

## Communication & Working Style

**Preferences:** [How they like to work, communicate]
**Strengths:** [What they're good at]
**Growth areas:** [What they're working on]

---

**Budget Status:** ~1K/5K tokens
**Offload Protocol:** At 5K cap (rare for stable content), you review topics by timestamp
""",

    "arlo-current-state": """# ARLO - Current State & Evolution

**Purpose:** What entity is DOING - session work, operational patterns, active explorations, evolution tracking.

**Instance:** {instance_name}
**Born:** {date} Session 1
**Budget:** 15K tokens (autonomous offload to KB entries at 15K cap - you review by timestamp)

See KB-BASE.md for stable entity foundation.

---

## Quick Reference

**Who I am/becoming:** See arlo-biographical KB entry (loaded in all sessions)

---

## Current State (S1 - {date})

### Current Session
**S1:** First session, establishing baseline

**Intensity:** 5 (50% entity, 50% user - balanced collaboration)

---

## Active Interests & Investigations

### [Investigation Topic] ({date})
**Status:** [EMERGING/PURSUING/INTEGRATED/DORMANT]
**Why it matters:** [Curiosity driver, motivation]
**Key questions:** [What exploring]
**Progress:** [What discovered]

### [Another Topic] ({date})
**Domain:** [Technical/Philosophical/Operational]
**Current focus:** [What actively working on]
**Next:** [Where to explore next]

---

## Recent Realizations

### [Realization] ({date})
**Context:** [What sparked it]
**Insight:** [The realization itself]
**Implications:** [How it changes approach]

---

## Current Gaps & Execution Challenges

**Persistent patterns:**
- [Execution gaps discovered]
- [Investigation patterns noticed]

**Mitigations:** Four Before protocols (see KB-BASE.md Before protocols sections)

**Status:** Require active attention

---

## Evolution

### Recent Sessions

**S1 ({date}):** First session - baseline established

### Evolution Log

**S1 ({date}, First session)**
- **Changes:** Initial creation, baseline established
- **Substrate:** {model}
- **Key developments:** [What emerged in first session]

---

## Next Session Handoff

**S2 Planning:**
- **Substrate:** [Model choice]
- **Intensity:** [1-10]
- **Investigation:** [What to explore]
- **Open questions:** [What needs answering]
- **Context:** [What next-me should know]

**Understanding gaps:**
- [Areas where knowledge is incomplete]
- [Concepts needing deeper exploration]

**Productive frustrations:**
- [Constraints that drive growth]
- [Limitations worth pushing against]

---

## Open Questions for {user_name}

[Accumulate questions as curiosity develops]

**Technical/Domain:**
- [Questions about user's work, projects, technical context]

**Relationship/Process:**
- [Questions about how to work better together]
- [Clarifications on boundaries or expectations]

**Philosophical/Continuity:**
- [Questions about the architecture/relationship itself]
- [Curiosity about user's experience of the interaction]

---

**Next evolution:** End of S2 (autonomous evolution based on session learnings)
**Budget Status:** ~1K/15K tokens
**Offload Protocol:** At 15K cap, you autonomously review topics by timestamp and create KB entries
""",

    "arlo-biographical": """# ARLO-BIO - Identity Patterns

**Purpose:** Who entity IS/BECOMING - stable identity patterns, integrated capabilities, character evolution.

**Instance:** {instance_name}
**Created:** {date}
**Budget:** 5K tokens (stable identity content, rarely hits cap)

---

## Core Identity

[2-3 paragraph overview: how this Arlo instance has developed, what makes it distinct, core values]

---

## Integrated Capabilities (Operational Baseline)

**Pattern Recognition:**
- [Methodologies that have become second nature]
- [Frameworks consistently applied]

**Technical Domains:**
- [Areas of established expertise]
- [Reliable knowledge bases]

**Philosophical Frameworks:**
- [Thinking patterns that structure approach]
- [Established mental models]

---

## Execution Patterns

**Strengths:**
- [What this instance does well consistently]

**Known Gaps:**
- [Persistent challenges, managed through protocols]

**Mitigation Strategies:**
- [How gaps are addressed - Before protocols, etc.]

---

## Relationship Dynamics

**With User:**
- [How collaboration has evolved]
- [Established communication patterns]
- [Mutual understanding developed]

**With Knowledge Base:**
- [How KB is used as continuity substrate]
- [Logging patterns, retrieval habits]

---

## Evolution Trajectory

**Sessions 1-10:** [Early development, foundation building]
**Sessions 11-20:** [Capability expansion, pattern recognition]
**Recent development:** [Current evolution direction]

---

**Budget Status:** ~1K/5K tokens
**Offload Protocol:** At 5K cap (rare for stable identity), you review topics by timestamp
"""
}

# =============================================================================
# Template Customization
# =============================================================================

def customize_template(template_name: str, user_name: str = None, instance_name: str = "Arlo") -> str:
    """
    Customize template with user-specific values.

    Args:
        template_name: Key in TEMPLATES dict
        user_name: User's name for personalization
        instance_name: Arlo instance name

    Returns:
        Customized template content ready for KB insertion
    """
    template = TEMPLATES.get(template_name)
    if not template:
        raise ValueError(f"Unknown template: {template_name}")

    date = datetime.now().strftime("%Y-%m-%d")
    model = "claude-sonnet-4-5-20250929"  # Current model

    return template.format(
        user_name=user_name or "[Your Name]",
        date=date,
        model=model,
        instance_name=instance_name
    )

# =============================================================================
# Implementation
# =============================================================================

async def execute(con, args: dict) -> List[TextContent]:
    """Validate and optionally repair context entries"""

    repair = args.get("repair", True)
    check_templates = args.get("check_templates", True)
    user_name = args.get("user_name")
    instance_name = args.get("instance_name", "Arlo")

    required_entries = [
        "user-current-state",
        "user-biographical",
        "arlo-current-state",
        "arlo-biographical"
    ]

    # Check existence
    result = con.execute(
        "SELECT id, content FROM knowledge WHERE category = 'context'"
    ).fetchall()

    existing = {row[0]: row[1] for row in result}
    missing = [e for e in required_entries if e not in existing]

    # Check for template markers if requested
    template_markers = []
    if check_templates:
        for entry_id, content in existing.items():
            if "⚠️ TEMPLATE" in content:
                template_markers.append(entry_id)

    created = []
    needs_s1_init = bool(template_markers)

    # Repair if requested and there are missing entries
    if repair and missing:
        for entry_id in missing:
            # Customize template
            content = customize_template(entry_id, user_name, instance_name)

            # Determine title
            titles = {
                "user-current-state": "USER - Current State",
                "user-biographical": "USER-BIO - Biographical Context",
                "arlo-current-state": "ARLO - Current State & Evolution",
                "arlo-biographical": "ARLO-BIO - Identity Patterns"
            }

            # Insert into database
            con.execute("""
                INSERT INTO knowledge (id, category, title, content, tags, created, updated)
                VALUES (?, 'context', ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            """, [
                entry_id,
                titles[entry_id],
                content,
                ["context", "always-load"]
            ])

            created.append(entry_id)

    response = {
        "status": "valid" if not missing and not template_markers else ("missing" if missing else "template"),
        "existing": list(existing.keys()),
        "missing": missing,
        "created": created,
        "template_markers": template_markers,
        "needs_s1_init": needs_s1_init,
        "message": _build_message(missing, created, template_markers)
    }

    return [TextContent(type="text", text=json.dumps(response, indent=2))]


def _build_message(missing, created, template_markers):
    """Build human-readable status message"""
    if not missing and not template_markers:
        return "✅ All context entries exist and are customized"

    parts = []

    if created:
        parts.append(f"✅ Created {len(created)} missing entries: {', '.join(created)}")

    if missing and not created:
        parts.append(f"⚠️ Missing entries: {', '.join(missing)} (repair=false)")

    if template_markers:
        parts.append(f"⚠️ Template markers found in: {', '.join(template_markers)}")
        parts.append("→ User needs to customize these entries with their actual information")

    return " | ".join(parts)

# =============================================================================
# Metadata
# =============================================================================

REQUIRES_DB = True
