---
id: user-issue-pds-origin-vendor-tension
category: issue
title: 'PDS Origin Story: Vendor vs Open Source Tension at UO'
tags:
- pds
- vendor-tension
- open-source
- microsoft-fabric
- uo-politics
- organizational-dynamics
- banner
created: '2025-11-21T13:01:45.800903'
updated: '2025-11-21T13:01:45.800903'
metadata: {}
---

# PDS Origin Story: Vendor vs Open Source Tension at UO

PDS born from organizational crisis and philosophical disagreement about vendor-first stance at UO.

**Trigger event:** Ellucian announced on-premise ODS entering maintenance support (precursor to end-of-life). Boss asked Brock to build ODS replacement proof-of-concept - "ridiculous task for one person" but led to deep research into data engineering landscape.

**Discovery process:**
- Read books: data governance, data integration, data applications
- Found robust open source ecosystem: Parquet, DuckDB, Streamlit, Harley Quinn, motherduck, DBT, Elementary Data, MkDocs Material
- Realized: "pains we have from vendor solutions are very well handled by open source solutions"

**Vendor frustration:**
- Boss implied proof-of-concept should use Microsoft Fabric exclusively
- Brock's assessment: "Fabric is a big piece of shit" - only utility maybe Power BI, data engineering parts "fucking garbage"
- Historical pattern: Oracle Warehouse Builder → Oracle Data Integrator (worse, not better) - newer/paid ≠ better
- UO stance: "vendor first" - bothers Brock that "we're choosing to have these problems"

**Open source performance advantage:**
- "Bloody fast" compared to vendor tools
- Most schools don't have big data, why pay for big data tools that underperform compared to laptop specs?
- Presentation at regional institutional research conference: ~/PDS/personal/index.HTML

**Common counterarguments Brock hears:**
1. "Don't want to build anything" - Born from decades of Banner modifications creating technical debt and vendor lock-in
2. "Skilling up burden" - Brock: 15 years experience says learning open source ≈ learning proprietary tool clicks
3. "Nobody gets fired for buying Microsoft" - Risk aversion post-layoffs driving vendor-first despite better alternatives

**Banner modification problem:**
- Modify Banner inside Ellucian's framework = two-way vendor lock-in
- Prevents lift-and-shift to other tools
- Prevents Ellucian from making architectural improvements
- Every upgrade: massive back-fitting effort

**Organizational dynamics:**
- Layoffs created risk-averse culture
- Management flattened (boss now manages 18 people)
- Limited bandwidth to explain technical details
- Default to "safe" vendor choices even when suboptimal

**PDS result:** Proof-of-concept became personal toolkit demonstrating open source viability, but organizational inertia points toward Fabric despite technical inferiority.


---

*KB Entry: `user-issue-pds-origin-vendor-tension` | Category: issue | Updated: 2025-11-21*
