# Test Results Summary

The differences recorded in [`test_results.expect`](test_results.expect)
are explained below.  The differences found when this workflow
compared Tax-Calculator with the R Tax-Simulator, which
tax-simulator-gpu replaces, are listed at the end.

In the comparisons below, `diff = tc - ts`, Tax-Calculator (TC) runs
current-law policy plus [`ts_emulation.json`](ts_emulation.json), and
tax-simulator-gpu (TS) is the pinned version in
[`ts_pin.json`](ts_pin.json) run with its default tax law, unchanged
(see [`VARIABLES.md`](VARIABLES.md)).  So a TS tax law parameter value
that differs from the IRS or SSA published value that TC uses shows up
as a difference.  The samples contain single, joint,
head-of-household, and married filing separately (MFS, `mstat=6`)
units; MFS units never have dependents.


Emulation conventions
---------------------

`ts_emulation.json` makes TC adopt three TS conventions, none of which
is an error in either model:

| # | TC parameter | Why |
|---|---|---|
| 1 | `eitc_claim_prob_scale = 9e99` | TS computes EITC entitlement (full take-up) |
| 2 | `actc_claim_prob_scale = 9e99` | TS computes ACTC entitlement (full take-up) |
| 3 | `CR_SchR_hc = 1` | TS does not compute the Schedule R credit for the elderly: it is the exogenous input `old_cred`, which `run_ts.py` zero-fills |

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
a24: 12098 differences (|tc - ts| > 1) in 2 variables
variable  compared  count  max_abs  mean_abs
    fica     10000   6049    297.6    180.48
   tfica     10000   6049    148.8     90.24
===== a25 =====
a25: 11848 differences (|tc - ts| > 1) in 2 variables
variable  compared  count  max_abs  mean_abs
    fica     10000   5924    148.8     89.66
   tfica     10000   5924     74.4     44.83
===== b23 =====
b23: 17322 differences (|tc - ts| > 1) in 4 variables
variable  compared  count  max_abs  mean_abs
  fiitax     10000   8504   969.00    419.65
     v28     10000     18     1.25      1.25
    niit     10000   8413   969.00    423.01
     v22     10000    387    49.92     25.58
===== b24 =====
b24: 39743 differences (|tc - ts| > 1) in 11 variables
variable  compared  count  max_abs  mean_abs
  fiitax     10000   8435   912.00    412.57
    fica     10000   7366   297.61    187.85
   tfica     10000   7366   297.61    113.55
     v10     10000   1861   148.80     77.69
    qbid     10000    318   110.50     23.06
     v18     10000   1861   259.30     79.11
     v19       304     59    52.08     26.34
     v28     10000   1877    82.98     26.80
     v26     10000   1861   259.30     79.17
    niit     10000   8334   912.00    422.30
     v22     10000    405    48.66     26.30
===== b25 =====
b25: 39940 differences (|tc - ts| > 1) in 11 variables
variable  compared  count  max_abs  mean_abs
  fiitax     10000   8466   923.40    414.24
    fica     10000   7234   148.81     93.05
   tfica     10000   7234   148.81     56.96
     v10     10000   1950    74.40     38.72
    qbid     10000    320    57.95     11.82
     v18     10000   1950   132.36     39.41
     v19       332     64    27.53     14.05
     v28     10000   1965    42.35     13.39
     v26     10000   1950   132.36     39.42
    niit     10000   8385   923.40    420.14
     v22     10000    422    48.74     24.45
===== c23 =====
c23: 17192 differences (|tc - ts| > 1) in 4 variables
variable  compared  count  max_abs  mean_abs
  fiitax     10000   8429   957.60    419.88
     v28     10000     21     1.25      1.25
    niit     10000   8342   957.60    423.01
     v22     10000    400    49.92     25.94
===== c24 =====
c24: 40445 differences (|tc - ts| > 1) in 13 variables
variable  compared  count  max_abs  mean_abs
  fiitax     10000   8488   991.80    412.75
    fica     10000   7432   297.61    188.06
   tfica     10000   7432   297.61    114.68
     v10     10000   1973   148.80     77.80
     v13      2682      1 16550.00  16550.00
    qbid     10000    350   115.08     25.87
     v18     10000   1974  1375.00     80.66
     v19       338     71    84.44     27.86
     v28     10000   1985    84.44     27.11
     v26     10000   1974 24000.00     92.13
    niit     10000   8403   991.80    422.27
     v22     10000    360    49.93     24.08
     v24     10000      2     8.00      6.44
===== c25 =====
c25: 40165 differences (|tc - ts| > 1) in 13 variables
variable  compared  count  max_abs  mean_abs
  fiitax     10000   8466   980.40    413.96
    fica     10000   7309   148.81     93.20
   tfica     10000   7309   148.80     56.81
     v10     10000   1933    74.40     38.60
     v13      2479      1 25625.00  25625.00
     v17      7521     79    22.32      9.54
    qbid     10000    366    50.14     12.81
     v18     10000   1934  1875.00     40.82
     v19       302     55    39.84     14.07
     v28     10000   1951    39.84     13.42
     v26     10000   1934 39000.00     59.63
    niit     10000   8386   980.40    419.68
     v22     10000    442    49.86     25.52
```

Every difference is explained by one of the six causes below.  This
was checked by rerunning TC with a scratch copy of
`ts_emulation.json` that also sets the TC parameters of causes 2 and 3
to the TS values: then the only differences left are those of causes
1, 4, 5, and 6, and in every unit the `fiitax` difference equals the
`niit` difference less the `v22` and `v24` differences (to within
$0.50, the size of a few EITC rounding differences that are within
the $1 tolerance).

| # | Years | Variable(s) | Cause | Wrong model |
|---|---|---|---|---|
| 1 | all | `niit`, `fiitax` | Net investment income scaled by 0.7 | TS (calibration) |
| 2 | 2024-2025 | `fica`, `tfica`, and through the SECA deduction `v10`, `v17`, `qbid`, `v18`, `v19`, `v28`, `v26`, `fiitax` | OASDI maximum taxable earnings | TS (parameter) |
| 3 | all | `v28`, `fiitax` | MFS 20% capital gains bracket | TS (parameter) |
| 4 | all | `v22`, `fiitax` | Smoothed child tax credit phase-out | TS (law specification) |
| 5 | all | `v24`, `v22`, `fiitax` | Smoothed child care credit rate phase-down | TS (law specification) |
| 6 | all | `v13`, `v18`, `v26` | Itemize-or-not tie broken differently | neither |

### 1. NIIT net investment income scaled by 0.7 (TS calibration)

**Nature.**  In about 84% of the set-`b` and set-`c` units (8,334 to
8,413 units per sample) TS's net investment income tax is 70% of TC's.
For example, b23-4 (MFS, AGI $279,800, net investment income of
$46,000: $16,000 of interest, $1,000 of dividends, $3,000 of net
capital gain, and $26,000 of rent): TC `niit` 3.8% x 46,000 = $1,748,
TS $1,223.60.  In the other differing units TC's NIIT is limited by
the excess of AGI over the threshold, and TS's is not, or less so, so
TS's NIIT is between 70% and 100% of TC's.

**Cause.**  TS's `niit.py` multiplies net investment income by 0.7
("Assumed: 70% of the computed base, to allow for Form 8960 components
the PUF does not report"), a calibration for gaps in the PUF-based tax
base rather than a statement of law (IRC 1411 has no such factor).  It
is a TS modeling choice that cannot be emulated exactly in TC (scaling
`NIIT_rt` would also scale the tax of units limited by AGI), so it is
documented here.

### 2. OASDI maximum taxable earnings in 2024 and 2025 (TS parameter)

**Nature.**  TS's OASDI maximum taxable earnings are $167,400 in 2024
and $175,500 in 2025, while the SSA-announced values used by TC are
$168,600 and $176,100.  So every earner with wages or self-employment
earnings above the TS maximum pays more OASDI tax in TC: up to 12.4%
(employee plus employer) of $1,200 = $148.80 per earner in 2024 and
of $600 = $74.40 in 2025, which is $297.60 and $148.80 for a couple
with two such earners.  This accounts for every `fica` and `tfica`
difference (5,924 to 7,432 units in the 2024 and 2025 samples).  For
self-employed units the larger TC SECA tax means a larger deduction
for one-half of SECA tax, so TC's AGI (`v10`) is lower by up to $74.40
(2024) or $37.20 (2025) per earner, which changes taxable income
(`v18`), the QBI deduction (`qbid`), the 2025 SALT limitation and so
itemized deductions (`v17`), AMT income (`v26`), the regular tax
(`v19`, `v28`), and `fiitax` in about 1,900 units of each 2024 and
2025 set-`b` and set-`c` sample.  The larger `v18` and `v26`
differences in c24 and c25 are those of cause 6.

**Cause.**  TS's `pr.yaml` gives the OASDI maximum only through 2023
(when its value, $160,200, is the SSA value) and indexes later values
with its average wage index series (from the pinned Macro-Projections
publication), rather than using the values SSA announced.

### 3. MFS 20% capital gains bracket (TS parameter)

**Nature.**  TS's MFS taxable income threshold of the 20% capital
gains rate is $276,925 in 2023, $291,875 in 2024, and $300,025 in
2025, $25 more than the IRS-published values used by TC ($276,900,
$291,850, and $300,000).  So the regular tax (`v28`) and `fiitax` of
MFS units with preferential income taxed above the IRS threshold are
5% x $25 = $1.25 more in TC (12 to 21 units per set-`b` and set-`c`
sample).

**Cause.**  TS's `pref.yaml` sets the MFS threshold to exactly
one-half of the joint threshold ($553,850 / 2 = $276,925 in 2023),
but the IRS-published MFS thresholds are one-half of the joint
threshold rounded down to a multiple of $50.

### 4. Child tax credit phase-out not rounded (TS law specification)

**Nature.**  In 360 to 442 units per set-`b` and set-`c` sample, TS's
nonrefundable child tax credit (`v22`) is up to $50 larger than TC's.
For example, b23-13: TC `v22` $1,150, TS $1,197.50.

**Cause.**  IRC 24(b)(1) reduces the credit by $50 for each $1,000,
or fraction thereof, by which modified AGI exceeds the threshold.  TC
rounds the excess up to a multiple of $1,000; TS's default law
(`ctc.yaml`, `po_discrete: 0`) reduces the credit by 5% of the excess
itself.  tax-simulator-gpu's `ARCHITECTURE.md` says that such a
smoothed version of a statutory step is a deliberate change in policy
specification, made so that marginal tax rates, which TS computes as
derivatives, are well defined.  So TS's phase-out is $0-$50 smaller.

### 5. Child care credit rate not rounded (TS law specification)

**Nature.**  In two c24 units the child and dependent care credit
(`v24`) is larger in TS: c24-3793 (AGI $44,675) TC $600, TS $604.88;
c24-7808 (AGI $43,400) TC $200, TS $208.  In each the larger TS
credit leaves less tax for the nonrefundable child tax credit, so TS's
`v22` is smaller by about the same amount and `fiitax` is the same.

**Cause.**  IRC 21(a)(2) reduces the 35% credit rate by one
percentage point for each $2,000, or fraction thereof, by which AGI
exceeds $15,000, to no less than 20%.  TC rounds the excess up to a
multiple of $2,000; TS's default law phases the rate down by 0.0005%
per dollar of excess (a smoothed version of the statutory step, as in
cause 4), so for c24-7808 TS's rate is 35% - 14.2% = 20.8% rather
than 20%.

### 6. Itemizing when it does not change tax (convention)

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


Differences found with the R Tax-Simulator
------------------------------------------

Before tax-simulator-gpu replaced it, this workflow compared TC with
the R Tax-Simulator, whose indexed parameter values that differed
from the IRS and SSA published values were replaced by the published
values.  That comparison found one TC error and fifteen R
Tax-Simulator errors, all of which were fixed before the R
Tax-Simulator was replaced, and none of which occurs with the pinned
tax-simulator-gpu.

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
