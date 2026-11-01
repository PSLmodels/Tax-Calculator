# Test Results Summary

The differences recorded in [`test_results.expect`](test_results.expect)
are being explained one assumption-set letter at a time: letters `a`
and `b` are done; the differences for letter `c` are recorded in
`test_results.expect` but are not yet explained here.

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

Set `b` adds self-employment, business, S-corporation, investment,
rental, pension, Social Security, and unemployment income to the
set-`a` units.

```
===== b23 =====
b23: 21913 differences (|tc - ts| > 1) in 10 variables
variable  compared  count  max_abs  mean_abs
  fiitax     10000   8864  4663.80    467.81
     v13     10000    323   350.00    350.00
    qbid     10000    809  3730.20   1096.06
     v18     10000   1067  3730.21    936.86
     v19       304     40   605.45    187.76
     v28     10000   1349  3900.00    448.76
     v26     10000    890 63250.00   3428.71
    niit     10000   8413   969.00    423.01
     v22     10000    156  1000.00    464.42
    actc     10000      2   128.00     67.75
===== b24 =====
b24: 22364 differences (|tc - ts| > 1) in 10 variables
variable  compared  count  max_abs  mean_abs
  fiitax     10000   8834  4300.20    467.64
     v13     10000    355   400.00    400.00
    qbid     10000    932  4563.84   1158.67
     v18     10000   1227  4563.84    995.83
     v19       304     43   920.68    260.51
     v28     10000   1498  3525.00    419.79
     v26     10000    986 66650.00   2463.70
    niit     10000   8328   912.00    422.60
     v22     10000    158  1000.00    467.72
    actc     10000      3   154.50     79.50
===== b25 =====
b25: 51805 differences (|tc - ts| > 1) in 11 variables
variable  compared  count  max_abs  mean_abs
  fiitax     10000   9931  4251.90    227.13
     v13     10000  10000  1500.00   1151.33
    qbid     10000   1037  3956.27   1009.72
     v18     10000  10000  5701.73   1163.87
     v19       332    332   862.18    366.49
     v28     10000   9998  3442.50    388.91
     v26     10000   1858 68500.00   6590.45
    niit     10000   8384   923.40    420.19
     v22     10000    235  1000.00    399.20
    actc     10000     29   303.75    134.96
     v25     10000      1    88.51     88.51
```

There are no payroll tax differences.  Every `fiitax` difference
equals the sum of the differences in `v28`, `niit`, `v22`, `actc`, and
`v25`, and every component difference is explained by one or more of
twelve causes: five set-`a` causes (3-7) and seven new ones (8-14).
Set-`a` causes 1 and 2 (the EITC of childless MFS and of joint filers
with one spouse aged 65 or older) do not occur in set `b`, because
nearly all such units have too much unearned income to get the EITC.

| # | Years | Variable(s) | Units (b23/b24/b25) | Cause | Wrong model |
|---|---|---|---|---|---|
| 3 | all | `v22` | 156 / 158 / 184 | Credit for other dependents phased out separately from the CTC | TS |
| 4 | all | `v13`, `v18`, `v19`, `v28` | 323 / 355 / 342 | MFS aged standard deduction add-on uses the unmarried amount | TS |
| 5 | 2025 | `v13`, `v18`, `v19`, `v28`, `v22`, `actc` | - / - / all | 2025 standard deduction is the pre-OBBBA amount | TS |
| 6 | 2025 | `v18`, `v19`, `v28` | - / - / 176 | MFS filers aged 65+ get the senior deduction | TS |
| 7 | 2025 | `v26` | - / - / 969 | Senior deduction subtracted (twice) from AMT income | TS |
| 8 | all | `niit` | 8413 / 8328 / 8384 | Net investment income scaled by 0.7 | TS (calibration) |
| 9 | all | `qbid`, `v18`, `v19`, `v28`, `v26` | 802 / 922 / 934 | QBI not reduced by the deduction for half of SE tax | TS |
| 10 | all | `v28` | 294 / 288 / 297 | Preferential income stacked above taxable income | TS |
| 11 | all | `actc` | 2 / 3 / 3 | No payroll-tax alternative ACTC for three or more children | TS |
| 12 | all | `actc` | 0 / 0 / 1 | Earned income not reduced by the deduction for half of SE tax | TS |
| 13 | all | `v25` | 0 / 0 / 1 | EITC phase-out applied to the phase-in amount | TS |
| 14 | all | `v26` | 81 / 54 / 44 | No MFS AMT income add-on | TS |

The other `qbid` differences (7 / 10 / 103) and the `v26` differences
that follow from them are caused by the standard deduction errors
(causes 4 and 5), which change the taxable income that limits the
deduction.  The remaining 2025 `v22` and `actc` differences (51 and
25 units) are cause 5 moving credit between the nonrefundable and the
refundable parts of the CTC.  All the new causes are TS errors except
cause 8, a deliberate TS calibration; causes 9-14 should be reported
to the Budget Lab.  None of them can be emulated by a Tax-Calculator
reform, so `ts_emulation.json` is unchanged.

### 8. NIIT net investment income scaled by 0.7 (TS calibration)

**Nature.**  In about 84% of the units TS's net investment income tax
is 70% of TC's.  For example, b23-4 (MFS, AGI $279,800, net
investment income of $46,000: $16,000 of interest, $1,000 of
dividends, $3,000 of net capital gain, and $26,000 of rent): TC `niit`
3.8% x 46,000 = $1,748, TS $1,223.60.  In the other differing units
(about 110 per sample) TC's NIIT is limited by the excess of AGI over
the threshold, and TS's is not, or less so.

**Cause.**  TS's `niit.R` multiplies net investment income by 0.7
("TEMP: scale down by a factor to match actuals"), a calibration for
gaps in the PUF-based tax base rather than a statement of law (IRC
1411 has no such factor).  It is a TS modeling choice that cannot be
emulated exactly in TC (scaling `NIIT_rt` would also scale the tax of
units limited by AGI), so it is documented here.

### 9. QBI deduction and self-employment tax (TS error)

**Nature.**  Most units with self-employment or business income below
the QBI phase-in range get a larger QBI deduction from TS.  For
example, b23-33 (single, $75,000 of wages, $34,000 of business
income): TS `qbid` 20% x 34,000 = $6,800; TC 20% x (34,000 - 2,402.02)
= $6,319.60, where $2,402.02 is the deduction for one-half of the
self-employment tax.  The smaller TS taxable income changes `v18`,
`v19`, `v28`, and `v26` too.  Within the phase-in range the difference
is reduced in proportion.

**Cause.**  TS's `qbi_ded.R` uses gross `sole_prop` income as
qualified business income.  Treas. Reg. 1.199A-3(b)(1)(vi) requires
QBI to be reduced by the deductions attributable to the business,
including the deductible part of self-employment tax (IRC 164(f)).
Applying TS's own QBI formula to QBI net of that deduction (and to
TC's taxable income) reproduces TC's `qbid` in every unit of all three
samples.

### 10. Tax on preferential income (TS error)

**Nature.**  High-income units whose qualified dividends and net
capital gain cross a 0%/15%/20% threshold have smaller TS tax before
credits, with identical taxable income.  For example, b23-2 (head of
household, taxable income $511,000 including $15,000 of qualified
dividends, net capital loss): all $15,000 is in the 15% band, because
$511,000 is below the $523,050 20% threshold, so the tax on it is
$2,250 (TC); TS taxes $12,050 at 15% ($1,807.50) and the other $2,950
not at all, so its `v28` is $442.50 lower.

**Cause.**  TS's `tax.R` computes the preferential-rate tax with
`integrate_conditional_rates_brackets(y = txbl_inc, x =
txbl_adj_pref_inc, inclusive = T)`, which places the preferential
income in the range from taxable income to taxable income plus
preferential income and then limits each bracket's amount to the part
of taxable income in that bracket.  The part of the preferential
income that falls in a band the taxable income does not reach is
dropped.  The Qualified Dividends and Capital Gain Tax Worksheet (IRC
1(h)) stacks preferential income on top of ordinary income, in the
range from taxable income less preferential income to taxable income.
With that stacking, TS's own brackets and ordinary-rate tax reproduce
TC's `v28` in every affected unit whose taxable income is the same in
both models.

### 11. ACTC for three or more children (TS error)

**Nature.**  A few heads of household with three qualifying children
and low earnings get a smaller ACTC from TS.  For example, b23-8528
($5,000 of wages): TS 15% x (5,000 - 2,500) = $375; TC $382.50, the
employee's 7.65% Social Security and Medicare tax.

**Cause.**  TS's `ctc.R` computes the refundable credit only as the
phase-in rate times earned income above $2,500.  IRC 24(d)(1)(B)(ii)
allows a taxpayer with three or more qualifying children the larger
of that amount and the Social Security taxes paid less the EITC, which
TC (and Schedule 8812, Part II-B) does.

### 12. Earned income and self-employment tax (TS error)

**Nature.**  In b25-6462 (joint, $14,000 of wages, $4,000 of business
income, two qualifying children), TS's ACTC is 15% x (18,000 - 2,500)
= $2,325; TC's is 15% x (17,717.39 - 2,500) = $2,282.61.

**Cause.**  TS's `pr.R` computes the earned income used by the CTC
and EITC as wages plus self-employment income.  Under IRC
32(c)(2)(A)(ii), which IRC 24(d)(1)(B)(i) uses, earned income includes
net earnings from self-employment determined with regard to the
deduction for one-half of self-employment tax (IRC 164(f)), as in TC.
The samples have no EITC difference from this cause only because few
units with self-employment income get the EITC.

### 13. EITC phase-out (TS error)

**Nature.**  In b25-3156 (joint, ages 77 and 72, one qualifying child,
$12,000 of wages, AGI $57,000) TC's EITC is $88.51: the $4,328 maximum
credit less 15.98% of the $26,530 by which AGI exceeds $30,470.  TS
gives $0.

**Cause.**  TS's `eitc.R` subtracts the phase-out amount from the
phase-in amount (`pmin(ei, pi_end) * pi_rate`, here 34% x 12,000 =
$4,080) instead of from the maximum credit.  Under IRC 32(a)(2) the
credit is the smaller of the phase-in amount and the maximum credit
less the phase-out amount.  The two agree unless earned income is
below the end of the phase-in range while AGI is in the phase-out
range, which takes unearned income, so this does not occur in set `a`.

### 14. AMT income of high-income MFS filers (TS error)

**Nature.**  MFS units with AMT income above the end of the
exemption phase-out range have larger AMT income in TC, by up to the
MFS exemption amount.  For example, b23-443 (AGI $1,087,600): TC `v26`
$1,150,850 = AGI + $63,250; TS $1,087,600.  No unit in the samples
owes AMT, so `v27` and `fiitax` do not differ.

**Cause.**  IRC 55(d)(2) increases the AMT income of a married
individual filing separately by the lesser of 25% of the excess of AMT
income over the amount at which the exemption is fully phased out and
the MFS exemption amount (Form 6251, line 4 instructions).  TS's
`amt.R` has no such adjustment; TC's `AMT` function has it.


Letter c (2023-2025)
--------------------

To be done.
