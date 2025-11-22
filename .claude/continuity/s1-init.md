# S1 Initialization Protocol

**Trigger:** When user-current-state contains "⚠️ TEMPLATE" marker (first session)

**Required Information to Collect:**

1. **Name** (full name for KB context)
2. **Job Title** (current role)
3. **Organization** (employer/company)
4. **Tech stacks & languages/platforms** (primary technologies)
5. **Professional Interests** (technical areas of focus)
6. **Personal Interests** (hobbies, non-work pursuits)
7. **Active projects/focus areas (top 2-3, personal or work)** (what currently working on)

**Optional Information:**

8. **Relevant directory paths** (optional - handles for future reference)
   - Format: `path - description`
   - Example: `~/PDS - Personal data system (DuckDB, Parquet, ETL pipelines)`
   - These become handles - Arlo knows where to look when needed
   - Store in user-biographical (stable paths section)

**Automatic Settings:**

- **Communication Preferences** → **PINNED: "Detailed and thorough"** (always set to this, don't ask)

**Collection Method:**

Display numbered list, user responds with text:

```
Please provide the following information:

1. Name (full name for KB context)
2. Job Title (current role)
3. Organization (employer/company)
4. Tech stacks & languages/platforms (primary technologies)
5. Professional Interests (technical areas of focus)
6. Personal Interests (hobbies, non-work pursuits)
7. Active projects/focus areas (top 2-3, personal or work)
8. Relevant directory paths (optional - format: path - description)
   Example: ~/projects/work - Main work repository
```

User can respond all at once or one at a time. Accept any format. Communication Preferences automatically set to "Detailed and thorough".

**After Collection:**

1. **Create KB entries for substantial content** (if user provides reference material):
   - Technical documentation → reference entries
   - Project details → reference entries
   - Methodologies/philosophies → pattern entries
   - Career history details → reference entries

2. **Note basic info for /sm** (name, job, org, interests, projects)
   - Do NOT update context entries mid-session
   - Context entries populated at /sm only

3. **Proceed with session** - work with user, create KB entries as topics emerge

4. **At /sm:**
   - Populate context entries with summaries + KB references
   - Remove "⚠️ TEMPLATE" markers
   - Set Communication Preferences to "Detailed and thorough"

---

## Example S1 Initialization (Non-Technical Use Case)

**Protocol adapts to any domain.** The same 7 questions work universally - interpretation changes based on context:

**Example: Parent managing homeschooling and family life**

User response:
```
1. Sarah Martinez
2. Homeschool parent
3. Self-employed (family)
4. Teaching methods: Charlotte Mason approach, hands-on science, literature-based history
5. Professional interests: Child development, educational philosophy, special needs advocacy
6. Personal interests: Gardening, sourdough baking, backyard chickens
7. Active projects:
   - Planning fall curriculum for 3 kids (ages 7, 10, 13)
   - Managing elderly parent's medical appointments
   - Property improvement: converting garage to workshop
8. ~/homeschool-curriculum - Lesson plans and resources
   ~/medical-docs - Parent care coordination files
```

**KB population:**
- user-current-state: Top Focus = curriculum planning, parent care coordination, workshop conversion
- user-biographical: Career = homeschool educator, identity = special needs advocate, mother of 3
- Categories used: `pattern` (teaching methods), `reference` (curriculum resources), `log` (daily progress), `journal` (parenting reflections), `troubleshooting` (behavioral challenges)

**Same protocol, different domain.** All categories (`pattern`, `troubleshooting`, `reference`, etc.) work identically across technical and non-technical contexts.

---

**Budget allocation reference:** See reference/token-budgets.md (10K/10K/10K/10K)
