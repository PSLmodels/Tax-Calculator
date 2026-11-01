# Test Results Summary

**Draft (Phase 5 of the tbly_ts plan).**  Differences are triaged one
assumption-set letter at a time; letter `a` is done, letters `b` and
`c` are still to be done.  The `test_results.expect` file is written
when the triage is finished.

In the comparisons below, `diff = tc - ts`, Tax-Calculator (TC) runs
current-law policy plus [`ts_emulation.json`](ts_emulation.json), and
Tax-Simulator (TS) is the pinned version in [`ts_pin.json`](ts_pin.json)
with the law adjustments described in [`VARIABLES.md`](VARIABLES.md).
The samples contain single, joint, head-of-household, and married
filing separately (MFS, `mstat=6`) units; MFS units never have
dependents.


Emulation conventions
---------------------

`ts_emulation.json` makes TC adopt three TS conventions, none of which
is an error in either model:

| # | TC parameter | Why |
|---|---|---|
| 1 | `eitc_claim_prob_scale = 9e99` | TS computes EITC entitlement (full take-up) |
| 2 | `actc_claim_prob_scale = 9e99` | TS computes ACTC entitlement (full take-up) |
| 3 | `CR_SchR_hc = 1` | TS does not compute the Schedule R credit for the elderly: it is the exogenous input `old_cred`, which `run_ts.R` zero-fills |

Without (1) and (2), TC's random credit non-claiming zeroes the EITC
or ACTC of a few hundred units in each set-`a` sample.  Without (3),
about twenty 2023-2024 set-`a` single filers aged 65 or older with
$16,000-$17,000 of wages have TC tax $30-$38 lower than TS tax.


Letter a (2023-2025)
--------------------

```
===== a23 =====
a23: 1452 differences (|tc - ts| > 1) in 7 variables
variable  compared  count  max_abs  mean_abs
  fiitax     10000    416   1000.0    299.21
     v13     10000    308    350.0    350.00
     v18     10000    156    350.0    350.00
     v19     10000    156     42.0     36.79
     v28     10000    156     42.0     36.79
     v22     10000    222   1000.0    469.82
     v25     10000     38    600.0    379.75
===== a24 =====
a24: 1408 differences (|tc - ts| > 1) in 7 variables
variable  compared  count  max_abs  mean_abs
  fiitax     10000    401   1000.0    308.25
     v13     10000    304    400.0    400.00
     v18     10000    151    400.0    400.00
     v19     10000    151     48.0     41.58
     v28     10000    151     48.0     41.58
     v22     10000    218   1000.0    481.65
     v25     10000     32    632.0    385.31
===== a25 =====
a25: 45227 differences (|tc - ts| > 1) in 9 variables
variable  compared  count  max_abs  mean_abs
  fiitax     10000   8067   1480.0    354.46
     v13     10000  10000   1500.0   1145.62
     v18     10000   8146   5650.0   1224.15
     v19     10000   8146    579.5    336.04
     v28     10000   8146    579.5    336.04
     v26     10000   2105  24000.0  15597.26
     v22     10000    467   1000.0    321.38
    actc     10000    111    180.0    129.25
     v25     10000     39    649.0    385.42
```

There are no payroll tax differences.  Every `fiitax` difference
comes with a difference in at least one of the compared components,
and every component difference is explained by one of seven causes:

| # | Years | Variable(s) | Units (a23/a24/a25) | Cause | Wrong model |
|---|---|---|---|---|---|
| 1 | all | `v25` | 37 / 30 / 37 | Childless MFS filers get the EITC in TC | **TC** |
| 2 | all | `v25` | 1 / 2 / 2 | Childless joint EITC counts only age-eligible spouse's earnings | TS |
| 3 | all | `v22` | 222 / 218 / 242 | Credit for other dependents phased out separately from the CTC | TS |
| 4 | all | `v13`, `v18`, `v19`, `v28` | 308 / 304 / 318 | MFS aged standard deduction add-on uses the unmarried amount | TS |
| 5 | 2025 | `v13`, `v18`, `v19`, `v28`, `v22`, `actc` | - / - / all | 2025 standard deduction is the pre-OBBBA amount | TS |
| 6 | 2025 | `v18`, `v19`, `v28` | - / - / 149 | MFS filers aged 65+ get the senior deduction | TS |
| 7 | 2025 | `v26` | - / - / 2105 | Senior deduction subtracted (twice) from AMT income | TS |

Causes 4-7 are TS parameter or logic errors; cause 1 is a TC error.
Causes 2-7 should be reported to the Budget Lab.

### 1. EITC for childless MFS filers (TC error)

**Nature.**  In each year, 30-37 MFS units with low wages and no
dependents get an EITC from TC (e.g., a23-187: $7,000 of wages,
TC `v25` = 7.65% x 7,000 = $535.50) but none from TS.

**Cause.**  TC's `EITC` function allows the credit to every MFS filer
from 2021 on (`EITC_sep_filers_elig` is true from 2021).  ARPA 2021
section 9621 amended IRC 32(d) so that a married individual filing
separately is treated as not married only if the individual *resides
with a qualifying child for more than one-half of the year* and lived
apart from the spouse for the last six months of the year (or is
legally separated).  An MFS filer with no qualifying child therefore
cannot claim the EITC (Pub 596, Rule 3).  TS denies the EITC to all
MFS filers (`eitc.mfs_eligible = 0`), which is right for childless
filers but would be wrong for an MFS filer with a qualifying child who
lived apart from the spouse; the samples have no such units.  (PE
allows the credit to childless MFS filers as TC does, which is why
the `pe_taxsim` comparison does not show this error.)  This TC error
is to be fixed on a separate branch; it is not changed here.

### 2. Childless EITC for joint filers with one spouse outside ages 25-64 (TS error)

**Nature.**  A few joint units without EITC-qualifying children, one
spouse aged 65 or older and the other aged 25-64, get a smaller EITC
from TS.  For example, a23-8826 (ages 66 and 60, $18,000 of wages
earned by the 66-year-old) gets $475.30 from TC (the $600 maximum less
7.65% of the $1,630 by which AGI exceeds the $16,370 joint phase-out
threshold) and $0 from TS.

**Cause.**  TS's `eitc.R` computes the earned income used for the
credit as `ei1 * qual1 + ei2 * qual2`, where `qual` is the age test of
each spouse, so the earnings of a spouse outside ages 25-64 are
dropped.  Under IRC 32(c)(1)(A)(ii)(II) a married couple without a
qualifying child is eligible if *either* spouse is 25-64, and the
credit is based on the couple's combined earned income (IRC
32(c)(2)), which is what TC does.

### 3. Credit for other dependents phase-out (TS error)

**Nature.**  Every `v22` difference in 2023 and 2024, and the positive
ones in 2025, are units with at least one CTC child, at least one
other dependent (age 17 or older), and AGI above the $200,000
($400,000 joint) phase-out threshold.  TS's credit is smaller, by up
to $500 per other dependent.  For example, a23-95 (joint, AGI
$433,000, one child and one other dependent): the combined maximum
credit is $2,500 and the phase-out is 33 x $50 = $1,650, so the credit
is $850 (TC); TS gives $350.

**Cause.**  With the baseline `ctc.po_sequential = 0`, TS's `ctc.R`
phases out the child credit (`max_value1 - excess1 * po_rate1`) and
the other-dependent credit (`max_value_other - excess1 *
po_rate_other`) separately, so the $50 per $1,000 reduction is applied
twice.  IRC 24(b)(1) reduces the total credit allowable (CTC plus the
24(h)(4) credit for other dependents) by $50 for each $1,000 of excess
AGI, which is what TC (and Schedule 8812) does.

### 4. MFS additional standard deduction for the aged (TS error)

**Nature.**  Every 2023-2024 `v13` difference is an MFS unit aged 65
or older; TS's standard deduction is $350 (2023) or $400 (2024)
larger.  `v18`, `v19`, and `v28` differ for the half of those units
that have positive taxable income.

**Cause.**  TS maps MFS filers to the unmarried additional amount
(`std.bonus_single`: $1,850 in 2023, $1,950 in 2024) rather than the
married amount ($1,500 and $1,550; IRC 63(f)).  This is not corrected
by `ts_law_overrides.csv` (see `VARIABLES.md`).

### 5. 2025 standard deduction (TS error)

**Nature.**  Every a25 unit has a `v13` difference of $750 (single
and MFS), $1,125 (head of household), $1,500 (joint), or $350 (MFS
units aged 65 or older, see below), with TC larger, and most units
have `v18`/`v19`/`v28` and `fiitax` differences as a result.  The 2025 `actc` differences and the negative 2025 `v22`
differences are also caused by this: TS's higher tax before credits
lets more of the CTC be nonrefundable (e.g., a25-31: TS `v22` $1,650,
`actc` $2,750; TC $1,537.50 and $2,862.50).

**Cause.**  TS's baseline `std.yaml` gives the pre-OBBBA 2025 amounts
($15,000 / $30,000 / $22,500) and starts the OBBBA amounts ($15,750 /
$31,500 / $23,625) in 2026.  OBBBA section 70102 applies to tax years
beginning after December 31, 2024.  For aged MFS units the `v13`
difference is $350 = $750 (base amount) - $400 (cause 4: $2,000 TS
add-on versus $1,600 in 2025).

### 6. 2025 senior deduction for MFS filers (TS error)

**Nature.**  In a25, the MFS units aged 65 or older with taxable
income have `v18` up to $5,650 higher in TC: $6,000 senior deduction
in TS less the $350 standard deduction difference (causes 4 and 5).
For example, a25-443 (age 67, $27,000 of wages): TS taxable income
$4,000, TC $9,650.

**Cause.**  TS's `below_ded.R` allows the senior deduction to every
filing status.  IRC 151(d)(5)(C), as added by OBBBA section 70103,
requires a married individual to file a joint return to claim the
deduction; TC's `MiscDed` function gives MFS filers no senior
deduction.

### 7. 2025 AMT income and the senior deduction (TS error)

**Nature.**  Every a25 `v26` difference is a unit with at least one
person aged 65 or older; TS's AMT income is smaller by $12,000 per
aged person (less where the senior deduction phases out).  For
example, a25-154 (joint, ages 63 and 67, AGI $59,000,
standard deduction): TC `v26` $59,000, TS $47,000.  This does not
change `fiitax` in a25, because no unit's AMT income exceeds its
exemption.

**Cause.**  TS's `txbl_inc.R` adds the senior deduction of a
nonitemizer to `ded`, and `amt.R` then computes `amt_gross_inc = agi -
ded - ... - senior_ded + std_ded`, where `std_ded` excludes the senior
deduction: the senior deduction is subtracted twice.  (For itemizers
it is subtracted once.)  Form 6251 for 2025 (line 1a: Form 1040 line
14 less Schedule 1-A line 37) does not allow the senior deduction for
the AMT at all, so AMT income of a nonitemizer is AGI, as in TC.

### Below-tolerance differences

TS computes the EITC maximum credit as the phase-in rate times the
earned income amount (e.g., 0.34 x 11,760 = $3,998.40) instead of the
IRS-published rounded amount ($3,995); the resulting differences
are smaller than the $1 tolerance in the set-a samples (e.g.,
a25-2308: TS $389.13, TC $388.93).


Letter b (2023-2025)
--------------------

To be done.


Letter c (2023-2025)
--------------------

To be done.
