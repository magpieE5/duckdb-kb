# USER-WORK - Work Domain Context

**Purpose:** Work focus, org dynamics, technical learnings, project details.

**User:** Brock Lampman
**Created:** 2025-11-18
**Budget:** ~9K tokens (work domain, compressed at 9K trigger)

See USER-BIO.md for stable career/org context.

---

## Current Focus (Top 5 minimum)

### 1. PDS (Personal Data System) Development (started: ~2023, priority: HIGH/COMPLEX)

**Status:** Technical success, organizational failure. Restricted to ODS/Cognos health metrics only. Unlikely to ever productionalize.

**Genesis:** Boss Travis Shea tasked Brock to build "replacement ODS POC" after Ellucian Banner ODS (on-premise) entered maintenance support (no EOL stated). Travis leaning toward MS Fabric; Brock evaluated and found it worse than existing platforms in multiple ways. Given tight budget constraints, researched FOSS tools and built PDS with custom wiring for near-full coverage of ODS/Cognos capabilities.

**Technical architecture:** Multi-process Python CDC ingestion → Hive-partitioned parquet → DBT-DuckDB SQL/Python transformations → SharePoint/OneDrive secure storage/distribution → Streamlit custom reporting → Jenkins automation → MKDocs Material documentation → GitHub project management.

**Stakeholder engagement:** Conducted multiple open labs with key stakeholders, prepared solid agendas, distributed detailed notes and follow-ups. Travis never attended.

**Organizational catastrophe:** Team members complained to Derek Wormdahl (Travis's boss) about Brock being "bothersome" regarding PDS. Travis asked entire team to compile instances of Brock "acting out of line, problematic." Travis wrote HR "Letter of Clarification" threatening disciplinary action if behaviors didn't adjust. PDS infrastructure was mostly decommissioned.

**Vindication arc:** Months later, ODS hit near-catastrophic faults. Brock rapidly recovered using PDS for fast diagnostics. Decommissioning suspended, but restricted to ODS/Cognos health and metrics only. Later, ODS 9.0-9.2 upgrade project revealed Travis/DBAs didn't check 9.0 upgrade code into Git 5 years ago - compiled codebase drifted significantly from versioned codebase. PDS proved instrumental in re-establishing functional Git repo and backfitting modifications.

**Current reality:**
- Mandate: PDS not approved to provide data from team
- Organization moving ahead with MS Fabric engaging Institutional Research and Office of the Provost
- Brock personally uses PDS beyond approved scope for task accomplishment
- Other departments have taken code and implemented large portions
- Recently presented PDS at conference
- Discord it brought (or Brock brought) to team makes productionalization highly unlikely

**Next steps:** Continue restricted use for ODS/Cognos health, personal productivity tool, duckdb-kb integration exploration

**Stakeholders:** Travis Shea (boss, wrote HR letter), Derek Wormdahl (Travis's boss), team members (complained), other departments (adopted code), conference attendees

### 2. duckdb-kb Development (started: 2025-11-18, priority: HIGH)

**Status:** Active development - knowledge base system with MCP integration
**Context:** ~/duckdb-kb - DuckDB-based knowledge management system developed by Brock
**Recent progress:** Initial setup, multi-file USER architecture created
**Next steps:** Extensive usage, refinement, integration with PDS
**Stakeholders:** Brock Lampman (primary user/developer)

### 3. PDS + duckdb-kb Integration (started: 2025-11-18, priority: HIGH)

**Status:** Planning phase - exploring integration opportunities
**Context:** Combining personal data management (PDS) with knowledge capture (duckdb-kb) for enhanced productivity
**Recent progress:** Initial conceptualization
**Next steps:** Identify integration points, develop workflows
**Stakeholders:** Brock Lampman

### 4. Ellucian Banner ODS/Cognos Work (started: ongoing, priority: HIGH)

**Status:** Ongoing ETL and reporting responsibilities
**Context:** Core job function at University of Oregon Information Services
**Recent progress:** (To be documented)
**Next steps:** (To be documented)
**Stakeholders:** (To be documented)

### 5. (Additional focus area to be added)

---

## Recent Work Learnings (Last 90 Days)

**2025-11-18:** Multi-file USER architecture setup for duckdb-kb knowledge base system

[Earlier learnings offloaded from USER.md will accumulate here]

---

## Open Commitments (Accountability Tracking)

(No current commitments tracked - will be added as they emerge)

---

## Organizational Context

**Team structure:**
- University of Oregon Information Services (central IT)
- Brock's team: ETL/Banner ODS development
- Boss: Travis Shea
- Travis's boss: Derek Wormdahl

**Key dynamics:**

**PDS friction (2023-present):** Major organizational conflict stemming from PDS development. Team members complained Brock was "bothersome" about PDS. Travis solicited complaints from entire team, wrote HR "Letter of Clarification" threatening disciplinary action. PDS mostly decommissioned despite technical merit. After PDS saved ODS during catastrophic failures and proved critical for ODS upgrade project, decommissioning suspended but use restricted to health metrics. Organization moving forward with MS Fabric despite PDS proving technically superior and cost-effective. Other departments adopting PDS code while Brock's own team prohibits its use for data distribution.

**Leadership communication pattern:**

**Travis (current boss):** Tasked PDS POC development but never attended stakeholder open labs. Told Brock about HR contact but claimed not to know details. Actually wrote the HR letter himself. Didn't maintain Git versioning discipline for ODS 9.0 upgrade 5 years ago, creating technical debt that PDS later helped resolve. Team consensus: "pathological liar." Weekly 1:1s throughout PDS period, never told Brock to stop/slow down, then cited those activities in HR letter months later.

**Derek Wormdahl (Travis's boss, Brock's former boss):** Made verbal retention agreement with Brock (2022) involving "leadership swap" with Tim Ketchum to retain Brock after PSU job offer. Agreement witnessed by Tim. When Brock inquired about agreement, Derek gaslit him that it ever happened. Tim participated in gaslighting initially. A year later, Tim admitted to Brock: "I was remembering everything as he did, and that he didn't know what happened and just went along with it." Derek orchestrated coordinated denial of documented verbal agreement.

**Tim Ketchum (former boss during Banner Developer role):** Participated in retention agreement meeting with Derek. Initially went along with gaslighting about agreement. Year later, admitted to Brock that agreement happened as Brock remembered, said he "didn't know what happened and just went along with it." Shows conscience but insufficient integrity to object in real-time.

**Technical debt culture:** ODS 9.0 upgrade code not checked into Git for 5 years. Compiled codebase drifted from versioned codebase in many directions. Problem not discovered until 9.0-9.2 upgrade project. Suggests weak DevOps practices and version control discipline at team level.

**Budget constraints:** "Money was tight and wouldn't get better any time soon" - context for PDS FOSS approach vs. vendor solutions like MS Fabric.

**Decision-making:** Top-down (Travis → team), with upper management involvement (Derek) when conflicts arise. Vendor solutions (MS Fabric) preferred over homegrown despite cost/capability trade-offs. Political considerations appear to outweigh technical merit in platform decisions.

**Retaliation timeline:**

1. **2022:** Brock leads unionization effort, flips 25 positions under Derek's management (https://uomatters.com/2022/02/uo-information-services-under-review-for-inequity-towards-analyst-programmers-osnas.html), massive salary increases result
2. **Late 2022:** Derek + Tim make verbal retention agreement ("leadership swap") to retain Brock after PSU job offer. By January nothing changed. Three Banner team openings, Brock excluded from hiring searches. Derek gaslights that retention agreement ever happened.
3. **Early 2023:** Brock leaves Banner team, returns to IDR team (Travis as boss), still doing 75% Banner work for over a year
4. **~2023:** Brock confronts Derek 1:1 about gaslighting regarding retention agreement, "it blew up"
5. **~2023:** Year after original gaslighting, Tim Ketchum admits to Brock that retention agreement happened as Brock remembered, said he "didn't know what happened and just went along with it"
6. **2023:** PDS development begins, organizational conflict escalates
7. **2023/2024:** HR "Letter of Clarification" written by Travis, includes fabricated/exaggerated issues (Netflix during queries from 6 months prior), issues never raised in weekly 1:1s. Brock contests, Travis revises drastically and reframes from "Brock's behavior" to "I'll be clearer on my directives." Travis apologizes but requires signature with disciplinary threats.
8. **Annual review (post-letter):** Overall exceeds, zero mention of any letter issues despite letter covering that performance period

**Pattern interpretation:** PDS conflict and HR letter appear to be retaliation for union organizing and confronting management about gaslighting, using Brock's communication style and technical advocacy as justification. Travis's revision of letter and excellent performance review suggest behavior wasn't actually problematic - retaliation theater requiring manufactured justification.

**Current constraints:**
- Topped out AP3 (no promotion path)
- HR letter creates permanent threat (though two stellar evaluations since suggest in the clear)
- Derek and Travis in management chain
- "Not much any of us feel powered to do"
- Wife Megan Prouty is SVP Operations at PenFed with global responsibilities requiring significant travel - limits Brock's bandwidth for union steward role (had to bow out after election), affects capacity for side projects and job searching
- Geographic/family constraints may limit pursuit of external opportunities (e.g., PSU job)

**No exit strategy:** Despite toxic environment, Brock has no exit plan. Travis absorbed Banner team + other staff due to layoffs, creating "low bar and lack of oversight" that's "sort of a blessing."

**Union representation:** Ran for union steward and was elected, but had to bow out when Megan's travel increased. Union was "very involved" in 2022 re-class effort and "very grateful" for Brock's efforts. Could have pursued union representation for retaliation but didn't.

---

## SMEs & Resources

**Management:**
- **Travis Shea** - Brock's boss, wrote HR letter, tasked PDS POC, never attended stakeholder meetings
- **Derek Wormdahl** - Travis's boss, received team complaints about Brock

**Team members:** (Names not yet documented - complained about Brock being "bothersome" regarding PDS)

**Work references (from USER-BIO.md):**
- **Fraser Barron** - Information Services, Banner Developer
- **Clarke Morris** - Information Services, Enterprise Data Asset Manager
- **Eric Shoemaker** - Information Services, Sr Application Infrastructure Engineer
- **Michael Walsh** - Business Affairs, Sys Admin/Banner Analyst

---

## Technical Environment

**Languages/Frameworks:** (To be documented - likely includes SQL, Python, ETL tools)
**Tools:**
- PDS (Personal Data System) - custom-built at ~/pds
- duckdb-kb - knowledge base system at ~/duckdb-kb
- Ellucian Banner ODS
- Cognos
- (Additional tools to be documented)

**Architecture:** (To be documented as patterns emerge)

---

**Budget Status:** ~2K/9K tokens
**Compression:** At 9K trigger (see KB-BASE.md compression strategies)
