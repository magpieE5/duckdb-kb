---
id: issue-pds-organizational-conflict-2023
category: issue
title: 'PDS Project: Technical Success, Organizational Failure - Retaliation Pattern
  (2023-present)'
tags:
- pds
- organizational-politics
- hr-action
- retaliation
- union-organizing
- gaslighting
- technical-debt
- leadership
- work
- derek-wormdahl
- travis-shea
- tim-ketchum
- vendor-vs-homegrown
created: '2025-11-19T01:03:26.326947'
updated: '2025-11-19T01:41:58.888904'
metadata: {}
---

# PDS Project: Technical Success, Organizational Failure - Retaliation Pattern (2023-present)

# PDS Project: Technical Success vs Organizational Failure - Retaliation Context

## Summary

PDS (Personal Data System) represents organizational retaliation disguised as performance management. Technical merit proved twice (catastrophic failure recovery, Git rescue), but project decommissioned following HR disciplinary letter. Pattern fits multi-year retaliation for 2022 union organizing that flipped 25 positions under Derek Wormdahl's management. PDS conflict used communication style as weapon, not cause.

## Retaliation Timeline Context

### 2022: Union Organizing (Root Cause)

**Action:** Brock leads unionization charge to flip 25 drastically underpaid non-union positions at UO Information Services

**Result:** 
- 25 positions flipped to union
- Massive salary bumps and trajectory changes
- Public documentation: https://uomatters.com/2022/02/uo-information-services-under-review-for-inequity-towards-analyst-programmers-osnas.html
- Derek Wormdahl's organization directly affected (Derek = Travis's boss, Brock's former boss)

### Late 2022: Retention Agreement Betrayal

**Situation:** Brock applies for AP2 job at Portland State University Banner team, makes it to final round. Notifies Derek.

**Agreement:** Derek + Tim Ketchum (Brock's boss) meet, agree on "leadership swap" to retain Brock. Verbal agreement made before Thanksgiving.

**Broken promise:** By January, nothing changed. Three Banner team openings occur, Brock excluded from hiring searches. When Brock raises retention agreement, Derek gaslights that it ever happened.

**Coordinated gaslighting:** Tim Ketchum initially goes along with Derek's denial despite being present for original discussion.

### ~2023: Tim's Admission (Critical Validation)

**Timeline:** About a year after "leadership swap" meeting

**Brock confronts Tim Ketchum** about participating in gaslighting

**Tim's admission:** "I was remembering everything as he did, and that he didn't know what happened and just went along with it"

**Significance:** 
- Validates Brock's memory - agreement happened
- Confirms coordinated management denial
- Derek orchestrated betrayal, Tim was complicit but weak
- Establishes pattern of management dishonesty

### ~2023: Confrontation with Derek

**Brock's action:** Meets Derek 1:1 to confront about gaslighting and get closure

**Result:** "It blew up"

**Significance:** Direct challenge to Derek's integrity likely escalated retaliation risk

### 2023: PDS Development Begins (Retaliation Vehicle)

## PDS Technical Development

**Genesis:** Boss Travis Shea tasked Brock to build "replacement ODS POC" after Ellucian Banner ODS entered maintenance support. Travis leaning toward MS Fabric; Brock evaluated and found it worse than existing platforms.

**Budget context:** "Money was tight and wouldn't get better any time soon"

**Brock's approach:**
- Researched FOSS tools, built PDS with custom wiring for near-full coverage of ODS/Cognos
- Architecture: Python CDC ingestion → Hive-partitioned parquet → DBT-DuckDB transformations → SharePoint/OneDrive → Streamlit reporting → Jenkins → MKDocs → GitHub

**Stakeholder engagement:**
- Conducted multiple open labs with key stakeholders
- Prepared solid agendas, distributed detailed notes and follow-ups
- Developed efficient tailored trainings using ScribeHow
- **Travis never attended any open labs**

## Team Resistance

**Team composition:** 3 Data Analysts + 1 Data Engineer (Brock), most at UO < 1 year

**Learning curve requirements:**
- Git (DAs didn't know it or weren't comfortable)
- Parquet, DuckDB, DBT
- DBT in particular - Brock saw it as improvement for analysts' pain points, not just engineers

**Travis's lack of support:** "Tolerated it at best" - never backed PDS in front of team

**Team complaints to Derek:** Multiple members complained Brock was "bothersome" about PDS

**Broader team context:**
- Travis "ran the service into the ground" (team assessment)
- Team consensus: Travis is "pathological liar"
- Weak DevOps practices: ODS 9.0 upgrade code not checked into Git for 5 years
- Stack proliferation without strategy (PowerBI, Azure Synapse, shadow databases)
- Gutted best practices (metadata updates stopped, Cognos open labs ended)

## HR Letter (Retaliation Mechanism)

**Travis's solicitation:** Asked entire team to compile instances of Brock "acting out of line, problematic"

**HR "Letter of Clarification":**
- Written by Travis Shea (initially claimed ignorance about HR contact)
- Included fabricated/exaggerated issues: "watching Netflix during queries" from 6 months prior (never happened, possibly joked about)
- Cited PDS activities and stakeholder engagement as problematic
- **Critical: Issues never raised in weekly 1:1s throughout period**
- Threatened disciplinary action

**Brock's contest:** Challenged nearly every accusation

**Travis's dramatic revision:**
- Reframed from "Brock's problematic behavior" to "In the future, I will be clearer on my directives"
- Travis apologized about letter
- Still required Brock's signature with disciplinary threats remaining

**Annual review (same performance period):** Overall exceeds rating, zero mention of any letter issues

**Interpretation:** If behavior was actually problematic, would appear in performance review and weekly 1:1s. Letter was retaliation theater requiring manufactured justification.

## Technical Vindication (Twice)

### ODS Catastrophic Failure (Months After Decommissioning)

**Crisis:** ODS hit near-catastrophic faults

**Resolution:** Brock rapidly recovered using PDS for fast diagnostics

**Result:** Decommissioning suspended, but use restricted to ODS/Cognos health and metrics only

### ODS 9.0-9.2 Upgrade Project

**Discovery:** Travis/DBAs didn't check ODS 9.0 upgrade code into Git 5 years ago

**Problem:** Compiled codebase drifted significantly from versioned codebase in many directions

**Solution:** PDS proved instrumental in re-establishing functional Git repo and backfitting modifications

**Irony:** PDS solved technical debt created by Travis's own poor Git discipline

## Current Reality (2025)

**Official mandate:**
- PDS not approved to provide data from team
- Restricted to ODS/Cognos health and metrics only
- Organization moving ahead with MS Fabric engaging Institutional Research and Office of the Provost
- Discord it brought (or Brock brought) makes productionalization highly unlikely

**Actual usage:**
- Brock personally uses PDS beyond approved scope for task accomplishment
- Other departments have taken code and implemented large portions
- Recently presented PDS at conference
- Technical merit recognized externally, rejected internally

**Brock's constraint:**
- Topped out AP3 (no promotion path)
- HR letter creates permanent threat
- Derek and Travis in management chain
- "Not much any of us feel powered to do"

## Pattern Analysis

### Retaliation Evidence

1. **Timeline:** Union organizing (2022) → retention betrayal (2022-2023) → Derek confrontation (2023) → Tim's admission (2023) → PDS conflict & HR letter (2023-2024)

2. **Letter construction:**
   - Travis solicited complaints rather than documenting own observations
   - Issues never raised in weekly 1:1s before letter
   - Includes 6-month-old fabricated incident
   - Travis rewrites after contest, changes blame from Brock to "I'll be clearer"
   - Travis apologizes but requires signature

3. **Performance contradiction:**
   - Letter threatens discipline
   - Same period earns "Overall exceeds" with zero mention of issues

4. **Management coordination:**
   - Derek orchestrated retention agreement betrayal (confirmed by Tim)
   - Derek received PDS complaints
   - Travis wrote HR letter
   - Both in Brock's management chain

5. **Technical vindication ignored:**
   - PDS saved ODS during catastrophic failure
   - PDS solved Travis's own technical debt (missing Git commits)
   - Other departments adopt code
   - Conference presentation
   - Still restricted and unlikely to productionalize

### Communication Style as Weapon

**Contributing factors (not causes):**
- Multiple team members complained (not just one conflict)
- Team learning curve (Git, DBT, DuckDB, parquet)
- Brock's work efficiency noted as difficult for team by Travis
- Military communication style (direct, persistent, mission-focused) vs. academic culture (indirect, consensus-seeking, conflict-avoidant)
- Possible social cue blindness (Travis tolerated "at best" but never said stop in weekly 1:1s)

**Why weapon, not cause:**
- External stakeholders kept attending open labs
- Other departments adopted PDS code
- Travis could have provided feedback before HR letter
- Travis's revision changed blame to "I'll be clearer" - management communication failure
- If communication was issue, wouldn't earn "Overall exceeds" review

### Synthesis

Most likely interpretation: **Retaliation for union organizing and Derek confrontation, using communication style as justification mechanism.** Communication style was the weapon, not the cause.

## Key People

**Derek Wormdahl** (Travis's boss, Brock's former boss):
- Organization affected by 2022 union organizing (25 positions flipped)
- Made retention agreement, orchestrated denial/gaslighting (confirmed by Tim)
- Received team complaints about Brock during PDS
- Confrontation with Brock "blew up"

**Travis Shea** (Brock's current boss):
- Worked alongside Brock as ETL Developer 2012-2015 before becoming manager
- Tasked PDS development, never attended stakeholder meetings
- Solicited team complaints about Brock
- Wrote HR letter, initially claimed ignorance
- Revised letter drastically, apologized
- Gave "Overall exceeds" review covering letter period
- Poor Git discipline created technical debt PDS later solved
- Team consensus: "pathological liar"

**Tim Ketchum** (Brock's former boss):
- Participated in retention agreement with Derek
- Initially went along with gaslighting
- Year later admitted agreement happened: "didn't know what happened and just went along with it"
- Conscience but insufficient integrity

**Team members (data analysts):**
- Complained to Derek about Brock being "bothersome"
- Compiled instances at Travis's request
- Say Travis "ran the service into the ground"
- Consensus: Travis is "pathological liar"

## Implications

**For understanding PDS:**
- Development occurred in adversarial organizational environment
- Technical excellence insufficient when management hostile
- Survival mechanism in toxic environment, not just productivity tool

**For future projects:**
- Keep tools personal/private to avoid organizational conflict
- External validation safer than internal advocacy
- Management will coordinate against perceived threats
- Documentation matters but won't protect against coordinated retaliation

**For duckdb-kb development:**
- Same organizational context applies
- Keep personal/gitignored to avoid PDS repeat
- External presentation safer than internal adoption push
- Technical merit won't protect against hostile management

## Unresolved Questions

1. Is HR letter still "active" with timeframe for escalation?
2. Has Brock consulted union representation about retaliation?
3. What legal protections exist for union organizing retaliation?
4. Is there documentation of retention agreement beyond Tim's admission?
5. What specific behaviors were "bothersome" to team members?
6. Why did Travis task project but never attend stakeholder meetings?
7. What drives MS Fabric preference despite cost/capability disadvantages?
8. What organizational incentives favor vendor solutions over homegrown innovation?
9. Why did Derek break retention agreement after making it?
10. What's Brock's exit strategy timeline?


---

*KB Entry: `issue-pds-organizational-conflict-2023` | Category: issue | Updated: 2025-11-19*
