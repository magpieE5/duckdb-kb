---
id: user-troubleshooting-idr-3771-missing-schedule-offerings
category: troubleshooting
title: 'IDR-3771: Student Registrations Missing from Schedule Offering'
tags:
- idr-3771
- banner
- schedule-offering
- data-quality
- ods
- troubleshooting
created: '2025-11-21T10:51:31.167472'
updated: '2025-11-21T10:51:31.167472'
metadata: {}
---

# IDR-3771: Student Registrations Missing from Schedule Offering

Student course registrations exist in SFRSTCR/MST_STUDENT_COURSE but corresponding courses don't appear in SCHEDULE_OFFERING view. Affects enrollment reports and Duckweb course display. Root cause: MSVGVC1 view uses INNER JOINs that filter out courses not in Banner course catalog (SCBCRSE).

## Root Cause

**View chain architecture:**
- `SATURN.SSBSECT` (Banner section master) → `ODSSRC.AS_COURSE_OFFERING` → `ODSMGR.MST_COURSE_OFFERING_UO` → `ODSMGR.MSVGVC1` → `ODSMGR.SCHEDULE_OFFERING`

**Critical filtering in MSVGVC1** (lines 454-456, 469-472):
```sql
-- Must exist in course catalog
WHERE CC.ACADEMIC_PERIOD = CO.ACADEMIC_PERIOD
  AND CC.SUBJECT = CO.SUBJECT  
  AND CC.COURSE_NUMBER = CO.COURSE_NUMBER
  
-- Must exist in MST_COURSE_OFFERING
AND COF.ACADEMIC_PERIOD = CO.ACADEMIC_PERIOD
AND COF.COURSE_REFERENCE_NUMBER = CO.COURSE_REFERENCE_NUMBER
```

These INNER JOINs to `MSV_COURSE_CATALOG` (CC) and `MST_COURSE_OFFERING` (COF) exclude any sections not properly cataloged.

**Why registrations succeed:** `STUDENT_COURSE` view uses LEFT JOIN to schedule_offering (student_course.sql:418-421), so students can register even when offering missing.

## Diagnostic Approach

**Priority 1 tables to extract (Banner source):**
1. `SATURN.SSBSECT` - Section master (does CRN exist? what's status?)
2. `SATURN.SFRSTCR` - Student registrations (confirm enrollments)
3. `SATURN.SCBCRSE` - Course catalog (is course cataloged for this term?)

**Priority 2 tables:**
4. `SATURN.SSBOVRR` - Section overrides (college/dept/division)
5. `SATURN.SSRXLST + SSBXLST` - Cross-list tables
6. Validation tables: `STVSSTS` (section status codes), `STVTERM`, `STVSUBJ`

**Diagnostic queries:**
```sql
-- Check if CRN exists in section master
SELECT * FROM SATURN.SSBSECT 
WHERE SSBSECT_TERM_CODE = '202502' AND SSBSECT_CRN = '26776';

-- Check student enrollments
SELECT COUNT(*), SFRSTCR_RSTS_CODE
FROM SATURN.SFRSTCR 
WHERE SFRSTCR_TERM_CODE = '202502' AND SFRSTCR_CRN = '26776'
GROUP BY SFRSTCR_RSTS_CODE;

-- Check if course in catalog (key diagnostic)
SELECT * FROM SATURN.SCBCRSE
WHERE SCBCRSE_SUBJ_CODE = '[from SSBSECT]'
  AND SCBCRSE_CRSE_NUMB = '[from SSBSECT]'
  AND SCBCRSE_EFF_TERM <= '202502'
  AND (SCBCRSE_TERM_CODE_END IS NULL OR SCBCRSE_TERM_CODE_END >= '202502');
```

## Potential Causes

1. **Missing catalog entry** - Course never cataloged for this term
2. **Special course types** - Independent study, thesis courses that bypass catalog
3. **Timing issues** - Registrations before catalog entry complete
4. **Cross-list complications** - Issues in cross-list setup
5. **Section status filtering** - Non-active status codes excluded upstream

## Solution Considerations

**Option 1: LEFT JOIN fix**
- Change MSVGVC1 INNER JOINs to LEFT JOIN
- **Pros:** More CRNs visible, matches student reality
- **Cons:** Loses catalog metadata (titles, credits, college/dept), downstream reports get incomplete data, masks root problem

**Option 2: Fix data at source**
- Ensure all sections have proper catalog entries
- **Pros:** Clean data, proper metadata
- **Cons:** May not be possible for special course types

**Recommendation:** Investigate catalog gap patterns first. If systemic for special course types, may need hybrid approach (LEFT JOIN with special handling).

## Related Files

**PDS Test:** `~/pds/tests/idr_3771__verify_missing_offerings.sql`
**Model Query:** `~/pds/models/idr_3771__missing_schedule_offerings.sql`
**View Definitions:**
- `~/pds/utils/idr/ioep/view/odsmgr/student_course.sql` (line 418-421: LEFT JOIN pattern)
- `~/pds/utils/idr/ioet/view/odsmgr/msvgvc1.sql` (line 454-456, 469-472: INNER JOIN filtering)
- `~/pds/utils/idr/ioep/view/odsmgr/schedule_offering.sql` (straight pass-through from MSVGVC1)
- `~/pds/utils/idr/ioep/view/odssrc/as_course_offering.sql` (Banner source view)

---

*KB Entry: `user-troubleshooting-idr-3771-missing-schedule-offerings` | Category: troubleshooting | Updated: 2025-11-21*
