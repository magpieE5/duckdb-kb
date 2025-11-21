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
8. **Communication Preferences** → **PINNED: "Detailed and thorough"** (always set to this, don't ask)

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
```

User can respond all at once or one at a time. Accept any format. Communication Preferences automatically set to "Detailed and thorough".

**After Collection:**

1. **Update user-current-state:**
   - Replace template placeholders with actual information
   - Populate "Top Active Focus" with provided projects
   - Set Communication Preferences to "Detailed and thorough"
   - Remove "⚠️ TEMPLATE" marker

2. **Update user-biographical:**
   - Add name, career information
   - Fill in biographical summary with collected context
   - Add key people if provided
   - Remove template markers

3. **Update arlo-current-state:**
   - Replace "[Your Name]" placeholder with actual user name in "Open Questions" section
   - Update "Current Session" with S1 details
   - Remove template markers

4. **Proceed to normal session status display**

---

**Budget allocation reference:** See KB-BASE.md Architecture & Scoping (15K/5K/15K/5K)
