# Test Results Summary

The differences recorded in [`test_results.expect`](test_results.expect)
are explained below.  A list of the differences found with earlier
Tax-Simulator pins, all of which have been fixed, is at the end.

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


Results
-------

```
===== a23 =====
a23: 0 differences (|tc - ts| > 1) in 0 variables
===== a24 =====
a24: 0 differences (|tc - ts| > 1) in 0 variables
===== a25 =====
a25: 0 differences (|tc - ts| > 1) in 0 variables
===== b23 =====
b23: 16826 differences (|tc - ts| > 1) in 2 variables
variable  compared  count  max_abs  mean_abs
  fiitax     10000   8413    969.0    423.01
    niit     10000   8413    969.0    423.01
===== b24 =====
b24: 16656 differences (|tc - ts| > 1) in 2 variables
variable  compared  count  max_abs  mean_abs
  fiitax     10000   8328    912.0     422.6
    niit     10000   8328    912.0     422.6
===== b25 =====
b25: 16768 differences (|tc - ts| > 1) in 2 variables
variable  compared  count  max_abs  mean_abs
  fiitax     10000   8384    923.4    420.19
    niit     10000   8384    923.4    420.19
===== c23 =====
c23: 16684 differences (|tc - ts| > 1) in 2 variables
variable  compared  count  max_abs  mean_abs
  fiitax     10000   8342    957.6    423.01
    niit     10000   8342    957.6    423.01
===== c24 =====
c24: 16805 differences (|tc - ts| > 1) in 5 variables
variable  compared  count  max_abs  mean_abs
  fiitax     10000   8401    991.8    422.37
     v13      2682      1  16550.0  16550.00
     v18     10000      1   1375.0   1375.00
     v26     10000      1  24000.0  24000.00
    niit     10000   8401    991.8    422.37
===== c25 =====
c25: 16773 differences (|tc - ts| > 1) in 5 variables
variable  compared  count  max_abs  mean_abs
  fiitax     10000   8385    980.4    419.73
     v13      2479      1  25625.0  25625.00
     v18     10000      1   1875.0   1875.00
     v26     10000      1  39000.0  39000.00
    niit     10000   8385    980.4    419.73
```

The set-`a` samples (wages, ages, and dependents) agree to within $1
in every compared variable.  Sets `b` and `c` add self-employment,
business, S-corporation, investment, rental, pension, Social Security,
and unemployment income (set `b`) and child-care expenses, property
taxes, other itemized deductions, and mortgage interest (set `c`).
There are no payroll tax differences.  Every `fiitax` difference
equals the `niit` difference in the same unit, and every difference
is explained by one of two causes:

| # | Years | Variable(s) | Units (b23/b24/b25, c23/c24/c25) | Cause | Wrong model |
|---|---|---|---|---|---|
| 1 | all | `niit`, `fiitax` | 8413 / 8328 / 8384, 8342 / 8401 / 8385 | Net investment income scaled by 0.7 | TS (calibration) |
| 2 | all | `v13`, `v18`, `v26` | 0 / 0 / 0, 0 / 1 / 1 | Itemize-or-not tie broken differently | neither |

### 1. NIIT net investment income scaled by 0.7 (TS calibration)

**Nature.**  In about 84% of the set-`b` and set-`c` units TS's net
investment income tax is 70% of TC's.  For example, b23-4 (MFS, AGI
$279,800, net investment income of $46,000: $16,000 of interest,
$1,000 of dividends, $3,000 of net capital gain, and $26,000 of rent):
TC `niit` 3.8% x 46,000 = $1,748, TS $1,223.60.  In the other
differing units (91 to 121 per sample) TC's NIIT is limited by the
excess of AGI over the threshold, and TS's is not, or less so, so
TS's NIIT is between 70% and 100% of TC's.

**Cause.**  TS's `niit.R` multiplies net investment income by 0.7
("TEMP: scale down by a factor to match actuals"), a calibration for
gaps in the PUF-based tax base rather than a statement of law (IRC
1411 has no such factor).  It is a TS modeling choice that cannot be
emulated exactly in TC (scaling `NIIT_rt` would also scale the tax of
units limited by AGI), so it is documented here.

### 2. Itemizing when it does not change tax (convention)

**Nature.**  c24-6333 and c25-5391 have itemized deductions larger
than the standard deduction, but their tax is zero either way (the
taxable income left by the standard deduction is qualified dividends
taxed at 0%).  TC reports the standard deduction (`v13`) and positive
taxable income (`v18`); TS reports the itemized deductions and zero
taxable income.  Because the standard deduction is added back for the
AMT and the itemized deductions are not, AMT income (`v26`) differs
too.

**Cause.**  TC chooses the deduction that yields the lower tax and
takes the standard deduction when the tax is the same; TS itemizes
whenever itemized deductions exceed the standard deduction.  Neither
is an error, and the tax is the same.


Fixed differences
-----------------

The comparison with the previous TS pin (commit `5a045cd67f53`,
2026-10-23) found one TC error and fifteen TS errors, all of which
have since been fixed.  None of them occurs with the current pin.

- **TC** (fixed in Tax-Calculator pull request 3222): childless MFS
  filers got the EITC, which IRC 32(d) as amended by ARPA 2021 allows
  an MFS filer only with a qualifying child.
- **TS parameter errors**: the 2025 standard deduction was the
  pre-OBBBA amount; the MFS additional standard deduction for the aged
  used the unmarried amount.
- **TS logic errors**:
  - the childless EITC of a joint couple counted only the earnings of
    a spouse aged 25-64;
  - the credit for other dependents was phased out separately from the
    CTC, so the $50 per $1,000 reduction was applied twice;
  - MFS filers aged 65 or older got the 2025 senior deduction;
  - the 2025 senior deduction was subtracted twice from the AMT income
    of nonitemizers;
  - qualified business income was not reduced by the deduction for
    one-half of self-employment tax;
  - preferential income was stacked above, rather than at the top of,
    taxable income;
  - the ACTC had no Social Security tax alternative for three or more
    children;
  - earned income for the CTC and EITC was not reduced by the
    deduction for one-half of self-employment tax;
  - the EITC phase-out was subtracted from the phase-in amount rather
    than from the maximum credit;
  - the AMT income of high-income MFS filers lacked the IRC 55(d)(2)
    increase;
  - the 2025 SALT limit of MFS filers was phased down at 30% rather
    than 15%;
  - the child care credit earned income limit was applied separately
    to young and older children;
  - the 2025 QBI deduction taxable income limit ignored the senior
    deduction.
