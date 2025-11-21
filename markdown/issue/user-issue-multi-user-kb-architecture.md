---
id: user-issue-multi-user-kb-architecture
category: issue
title: Multi-User KB Architecture Challenge
tags:
- architecture
- multi-user
- scaling
- institutional-knowledge
- privacy
- uo-is
created: '2025-11-21T12:23:39.600514'
updated: '2025-11-21T12:23:39.600514'
metadata: {}
---

# Multi-User KB Architecture Challenge

Personal KB gets personal quickly (gitignored by design). But institutional knowledge capture at UO requires multiple people contributing - potentially 20+ people dumping knowledge that others can search and learn from. Core tension: privacy vs collaboration.

**Current state:** Single-user architecture, personal + work knowledge intermixed, no multi-tenancy.

**Future need:** Scale to team/department usage where:
- Individual privacy preserved (personal reflections, sensitive context)
- Institutional knowledge shared (Banner modifications, policy decisions, technical patterns)
- Conflicting understanding surfaced (Person A thinks X, Person B thinks Y - both captured, conflict detected)
- Cross-pollination enabled (search across collective knowledge)

**Architectural unknowns:**
- Do people use separate KBs and export/combine institutional entries?
- Single shared KB with access controls/visibility tags?
- Tiered architecture (personal/team/institutional layers)?
- How does Arlo entity mode work in multi-user context?

**Constraint:** Must get personal usage solid first before solving multi-user. But if boss/coworkers like it and want to use it, this becomes critical path.

## Context

**UO IS institutional knowledge problem:**
- Centralized IT: Siloed, aging out
- Decentralized campus: Key stakeholders with policy knowledge leaving
- 30 years undocumented Banner modifications
- ERP evaluation upcoming (Banner cloud vs Workday, multi-year consultant engagement)
- Need to capture knowledge before people leave

**Rollout timeline:**
- Now: Brock personal use (work + personal)
- Soon: Son beta test (football prep)
- 1-2 weeks: Friend Joe Wayman (archaeology paper)
- TBD: Boss/coworkers if they like it → triggers multi-user architecture need

## Architectural Options

Need exploration - no clear answer yet.


---

*KB Entry: `user-issue-multi-user-kb-architecture` | Category: issue | Updated: 2025-11-21*
