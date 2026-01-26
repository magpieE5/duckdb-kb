---
id: seed-ipeds-complementary-datasets
category: seed
title: IPEDS Complementary Datasets - Scorecard, Carnegie, HERD
tags:
- seed
- ipeds
- scorecard
- carnegie
- herd
- nsf
- public-data
- higher-ed
- pds
- unitid
- mintable
created: '2026-01-25T23:40:03.974128'
updated: '2026-01-25T23:40:03.974128'
---

# IPEDS Complementary Datasets - Scorecard, Carnegie, HERD

**Public datasets that complement IPEDS for higher education analysis. All join on UNITID. Candidates for `pds {source}` commands following IPEDS pattern. Federal reporting data with zero FERPA concerns.**

---

## College Scorecard ✓ PDS-Ready

**Source:** https://collegescorecard.ed.gov/data/

| Aspect | Detail |
|--------|--------|
| Format | CSV inside ZIP |
| Structure | One file per year: `MERGED2017_18_PP.csv`, `MERGED2018_19_PP.csv`, etc. |
| Key | UNITID (same as IPEDS) |
| Years | 1997-present |
| Columns | ~1,800-2,000 (wide, longitudinal additions over time) |
| Content | Earnings after graduation, debt, repayment rates, completion by program |

**Why it matters:** The *outcomes* data IPEDS lacks. Answers "what happens to graduates?" Post-enrollment earnings, loan repayment success, completion rates for specific programs.

**Pattern:** Very similar to IPEDS. Year-based CSVs, UNITID key, bulk ZIP download. A `pds scorecard` command would follow the same pattern as `pds ipeds`.

---

## Carnegie Classifications ✓ PDS-Ready

**Source:** https://carnegieclassifications.acenet.edu/resource-type/data-file/

| Aspect | Detail |
|--------|--------|
| Format | Single Excel file (XLSX) |
| Structure | One row per institution, all classifications |
| Key | UNITID |
| Current | 2021 edition |
| Direct link | https://carnegieclassifications.acenet.edu/wp-content/uploads/2023/03/CCIHE2021-PublicData.xlsx |
| Content | R1/R2/M1/etc., size, control, residential character, undergraduate/graduate profile |

**Why it matters:** Richer classification detail than IPEDS CARNEGIE field. Enables "show me R1 publics with high residential character" type filtering. More granular peer grouping.

**Pattern:** Simpler than IPEDS - single file, not annual. Could be a seed file or one-time download rather than a full command.

---

## NSF HERD ✓ PDS-Ready

**Source:** https://ncses.nsf.gov/explore-data/microdata/higher-education-research-development

| Aspect | Detail |
|--------|--------|
| Format | CSV and SAS, by year |
| Structure | One file per year, institution-level |
| Key | Linkable to IPEDS (likely UNITID or FICE) |
| Years | 2010-2024 |
| Content | R&D expenditures by field, funding source, type of research |

**Why it matters:** Research intensity metrics for R1/AAU context. Shows which institutions are research-heavy vs teaching-focused. Relevant for peer comparisons where research mission matters.

**Pattern:** Annual CSVs like IPEDS. Would need to verify the join key.

---

## Build Priority

1. **College Scorecard** - Outcomes data, same pattern as IPEDS, direct UNITID join, answers "so what?"
2. **Carnegie** - Simple seed file, enriches peer analysis with classification detail
3. **HERD** - Research intensity for research university context, annual pattern

---

## Join Pattern

All three datasets join on **UNITID** (federal institution identifier):

```sql
-- Example: Graduation rates + outcomes + classification
SELECT 
    i.institution_name,
    i.state,
    gr.grad_rate_4yr,
    sc.median_earnings_10yr,
    c.carnegie_basic_2021
FROM ipeds.institutions i
LEFT JOIN ipeds.graduation_rates gr ON i.unitid = gr.unitid
LEFT JOIN scorecard.merged2023 sc ON i.unitid = sc.unitid
LEFT JOIN carnegie.classifications c ON i.unitid = c.unitid
WHERE i.sector = 'Public 4-year'
```

---

*Mintable foundation for higher education data analysis beyond IPEDS core surveys.*

---

*KB Entry: `seed-ipeds-complementary-datasets` | Category: seed | Updated: 2026-01-25*
