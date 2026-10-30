# Test Results Summary

```
(taxcalc-dev) pe_taxsim> awk 'NR<=12' test_results.expect
===== PE_PIN =====
policyengine_taxsim_repo: https://github.com/PolicyEngine/policyengine-taxsim
policyengine_taxsim_sha: c0d565948af3896e3a6e4d34970f7502d17cdf34
policyengine_taxsim_sha_date: 2026-10-30
policyengine_taxsim_version: 3.3.0
policyengine_us_version: 2.87.0
policyengine_core_version: 3.33.14
python_version: 3.13
python_version_resolved: 3.13.16
uv_version: 0.12.23
pinned_on: 2026-10-30
pe_cli_options: --scorp-treatment active
```

The remainder of the `test_results.expect` file shows no differences
in payroll taxes.  It does show federal income tax (`fiitax`)
differences, all for married filing separately units, in the a21,
b21, c21, a23, b23, and c23 samples: two are caused by errors in
Tax-Calculator 2021 and 2023 policy parameter values and one by a PE
error.  The other differences below do not affect income or payroll
tax liability in the validation samples used here.  See the Diffs
Analysis section below for details.

```
(taxcalc-dev) pe_taxsim> awk 'NR>12' test_results.expect
===== a21 =====
a21: 1118 differences (|tc - pe| > 1) in 2 variables
variable  compared  count  max_abs  mean_abs
  fiitax     10000      7     10.0     10.00
    actc     10000   1111   1600.0    650.81
===== a22 =====
a22: 0 differences (|tc - pe| > 1) in 0 variables
===== a23 =====
a23: 912 differences (|tc - pe| > 1) in 3 variables
variable  compared  count  max_abs  mean_abs
  fiitax     10000    304   2785.5   1345.24
     v19     10000    304   2785.5   1345.24
     v28     10000    304   2785.5   1345.24
===== a24 =====
a24: 0 differences (|tc - pe| > 1) in 0 variables
===== a25 =====
a25: 0 differences (|tc - pe| > 1) in 0 variables
===== b21 =====
b21: 998 differences (|tc - pe| > 1) in 7 variables
variable  compared  count  max_abs  mean_abs
  fiitax     10000     37     5.26      2.22
    qbid     10000     40    16.41      7.56
     v18     10000     40    16.43      7.56
     v19       296      2     2.34      1.82
     v28     10000     37     5.26      2.21
     v26     10000     40    16.43      7.56
    actc     10000    802  1600.00    616.90
===== b22 =====
b22: 0 differences (|tc - pe| > 1) in 0 variables
===== b23 =====
b23: 1754 differences (|tc - pe| > 1) in 3 variables
variable  compared  count  max_abs  mean_abs
  fiitax     10000    862  4625.03   3169.57
     v19       304     30  4625.00   3617.32
     v28     10000    862  4625.04   3169.57
===== b24 =====
b24: 0 differences (|tc - pe| > 1) in 0 variables
===== b25 =====
b25: 0 differences (|tc - pe| > 1) in 0 variables
===== c21 =====
c21: 1081 differences (|tc - pe| > 1) in 7 variables
variable  compared  count  max_abs  mean_abs
  fiitax     10000     39     6.07      2.92
    qbid     10000     43    18.96      9.20
     v18     10000     43    18.97      9.20
     v19       321      1     2.59      2.59
     v28     10000     39     6.07      2.92
     v26     10000     43    18.97      9.20
    actc     10000    873  1600.00    639.00
===== c22 =====
c22: 0 differences (|tc - pe| > 1) in 0 variables
===== c23 =====
c23: 1616 differences (|tc - pe| > 1) in 3 variables
variable  compared  count  max_abs  mean_abs
  fiitax     10000    795  4625.03   3043.34
     v19       326     26  4625.01   2787.37
     v28     10000    795  4625.03   3043.34
===== c24 =====
c24: 2 differences (|tc - pe| > 1) in 2 variables
variable  compared  count  max_abs  mean_abs
     v18     10000      1   1375.0    1375.0
     v26     10000      1  24000.0   24000.0
===== c25 =====
c25: 2 differences (|tc - pe| > 1) in 2 variables
variable  compared  count  max_abs  mean_abs
     v18     10000      1   1875.0    1875.0
     v26     10000      1  39000.0   39000.0
```


# Diffs Analysis

## Agent:

Claude Code 2.1.314 running Opus 5.5 with medium effort
on Tax-Calculator validation-samples branch at Fri Oct 30 12:22:35 EDT 2026.

## Prompt:

Look into the new differences and update the SUMMARY.md analysis
section.

## Results:

In the comparisons below, `diff = tc - pe`.  The samples contain all
four filing statuses, including married filing separately (MFS,
`mstat=6`) units, which never have dependents.  There are five
distinct causes, and every difference is explained by one of them:

| # | Samples | Variable(s) | Units | Cause | Affects `fiitax`? |
|---|---|---|---|---|---|
| 1 | a23, b23, c23 | `fiitax`, `v28`, `v19` | 304 + 862 + 795 MFS | TC 2023 MFS 37% bracket threshold is wrong | Yes (TC too low) |
| 2 | b21, c21 | `qbid`, `v18`, `v26`, `fiitax`, `v28`, `v19` | 40 + 43 MFS | TC 2021 MFS QBID threshold is wrong | Yes (TC too high) |
| 3 | a21 | `fiitax` | 7 MFS | PE gives an MFS filer the wrong Schedule R initial amount | Yes (PE too low) |
| 4 | a21, b21, c21 | `actc` | 1111 + 802 + 873 | PE counts part of the 2021 other-dependent credit (ODC) as refundable CTC | No |
| 5 | c24, c25 | `v18`, `v26` | 1 + 1 | Different itemization tie-break when a unit owes no tax either way | No |

Causes 1 and 2 are Tax-Calculator parameter errors, which should be
fixed in `policy_current_law.json`.  Adding the corrected values to a
scratch copy of `pe_emulation.json` removes every difference in a23,
b23, and c23, and every b21 and c21 difference except the `actc`
differences.

### 1. 2023 MFS top bracket (a23, b23, c23)

**Nature.**  Every difference is in an MFS unit, and every `diff` is
negative (TC tax is lower).  `fiitax`, `v28`, and (where compared)
`v19` differ by the same amount in each unit, by as much as $4,625 =
0.02 x $231,250.  In a23, where all income is wages, every `diff`
equals -0.02 x (taxable income - $346,875).

**Cause.**  TC's 2023 `II_brk6` value for MFS is $578,125, which is the
single-filer value.  Rev. Proc. 2022-38 (Table 3) puts the 2023 MFS
37% bracket above $346,875, half the joint $693,750 threshold, which is
what PE uses.  TC therefore taxes MFS taxable income between $346,875
and $578,125 at 35% rather than 37%.  The 2021, 2022, 2024, and 2025
MFS values are correct, as is the 2023 head-of-household value
($578,100).  This is a TC error.

### 2. 2021 MFS QBID threshold (b21, c21)

**Nature.**  Every difference is in an MFS unit, and every MFS unit
with QBI whose taxable income before the QBID is in the phase-in range
($164,900 to $214,925) has a `qbid` diff of -$2 to -$19, with
matching `v18` and `v26` diffs.  The smaller deduction raises
`fiitax` and `v28` by $1-$6 (fewer units than `qbid`, because some
diffs are below the $1 tolerance after the tax rate is applied).  MFS
units below the phase-in range agree exactly.

**Cause.**  TC's 2021 `PT_qbid_taxinc_thd` value for MFS is $164,900,
the value for single filers.  Rev. Proc. 2020-45 (section 3.27) gives
the 2021 threshold amount as "$329,800 for married filing joint
returns, $164,925 for married filing separate returns, and $164,900
for all other returns", and PE uses $164,925.  With a $50,000
phase-in range and no W-2 wages, the $25 lower threshold reduces TC's
deduction by 25/50,000 of 20% of QBI (for example, $6 for unit b21-13,
which has $60,000 of S-corporation income).  This is a TC error.

### 3. 2021 MFS Schedule R credit (a21)

**Nature.**  Seven a21 MFS units, each aged 65 or older with $14,000
of wages, have `fiitax` $10 higher in TC.  Every compared component
agrees: taxable income is $100 (AGI less the $12,550 standard
deduction and $1,350 additional aged amount) and tax before credits is
$10.  PE's `income_tax` is $10 lower than the sum of the components
because PE allows a $10 credit for the elderly (Schedule R), which is
not one of the compared output variables.

**Cause.**  PE's `section_22_income` chooses the Schedule R initial
amount with

```
select([num_qualifying_individuals == 1,
        num_qualifying_individuals == 2,
        filing_status == SEPARATE],
       [5_000, 7_500, 3_750])
```

Because the one-qualifying-individual test comes first, an MFS filer
aged 65 or older gets $5,000 rather than the statutory $3,750 (IRC
22(c)(2)(A)(iii)).  With PE's $5,000 MFS phase-out threshold, the
credit is 15% x (5,000 - 0.5 x (14,000 - 5,000)) = $75, limited to the
$10 tax.  TC's `SchR` uses $3,750, which gives no credit at that AGI.
Probing PE directly gives `elderly_disabled_credit` = $10 at $14,000
of wages and $0 at $15,000, which matches the samples: MFS units with
$15,000 of wages show no difference.  This is a PE error.  The credit
is so small for MFS filers that it shows up only when the unit's tax
is also small, which in these samples (wages in $1,000 steps) happens
only in 2021.  Under the statute, an MFS filer who lived with the
spouse at any time during the year gets no Schedule R credit at all
(IRC 22(e)(1)).  `pe_emulation.json` already assumes that every MFS
unit lived with the spouse, as PE does when it computes taxable
Social Security benefits, but both models allow the credit to every
MFS filer aged 65 or older.

### 4. 2021 `actc` (a21, b21, c21)

**Nature.**  These are all the remaining a21, b21, and c21
differences.  Every `diff` is negative (PE's refundable CTC is
larger).  Most are multiples of the $500 ODC: in a21, 684 are -$500,
273 are -$1,000, and 42 are -$1,500; the rest are smaller amounts.
Every unit with a difference is a joint or head-of-household unit
with at least one qualifying child (under 18) and at least one other
dependent (18 or older), and has AGI above the ARPA phase-out
threshold ($112,500 head of household, $150,000 joint).  The total
credit (`v22`) agrees in every one of these units, so the two models
differ only in how they split the same credit between its refundable
CTC and nonrefundable ODC parts.

**Cause.**  In a fully refundable year (2021 only), PE's
`refundable_ctc` is

```
min(ctc_refundable_maximum - ctc_phase_out, ctc)
```

where `ctc_refundable_maximum` is the sum of the ARPA per-child
maximums (children only), `ctc_phase_out` is only the regular
$50-per-$1,000 phase-out above $200,000/$400,000, and `ctc` is the
whole credit, including the ODC, after both the ARPA and regular
phase-outs.  Because the ARPA phase-out reduces `ctc` but not the
first argument of the `min`, the ODC offsets the ARPA phase-out and
up to the full ODC ends up in the refundable amount.  The `diff` is

```
-min(ODC maximum, ARPA phase-out amount, credit left after both phase-outs)
```

which explains the non-$500 amounts (units just above the ARPA
threshold, or units whose remaining credit is small).

Tax-Calculator follows the 2021 Schedule 8812: line 14a gives the ODC
first claim on the credit left after the phase-outs (the smaller of
lines 7 and 12), and only the remainder, line 14b, is refundable.
`ChildDepTaxCredit` in `calcfunctions.py` does exactly this
(`odc = min(line7, line12)`, `c07220 = line12 - odc`).  ARPA's IRC
24(i) refundability does not extend to the 24(h)(4) credit for other
dependents, so this is a PE error that overstates the 2021 refundable
CTC and understates the nonrefundable ODC by the same amount.  It
leaves tax unchanged in these samples only because each unit's tax
liability is large enough to absorb the nonrefundable ODC; a unit
with less tax liability would get too large a refund from PE.  The
error is limited to 2021 because PE's 2022-2025 branch caps the
refundable amount per child and phases it in with earnings, which
keeps the ODC out.

### 5. `v26` and `v18` (c24, c25)

**Nature.**

| Sample-id | `v18` PE | `v18` TC | `v26` PE | `v26` TC | `v26` diff |
|---|---|---|---|---|---|
| c24-6333 | 0 | 1,375 | -6,075 | 17,925 | 24,000 |
| c25-5391 | 0 | 1,875 | -5,500 | 33,500 | 39,000 |

Both units are single or head-of-household filers with modest AGI
($17,925 and $33,500), itemized deductions (mostly mortgage interest
and property tax) larger than the standard deduction, and zero income
tax before credits under either deduction: their taxable income under
the standard deduction is preferential income (qualified dividends,
`dwks10` > 0) taxed at 0%, so TC `taxbc` and PE `v28` are zero.
`fiitax` agrees in both (in c25-5391 it consists entirely of
refundable credits).

**Cause.**  PE itemizes and TC takes the standard deduction, because
the two models break a tie in tax liability differently:

- PE (`tax_unit_itemizes`): if the tax liabilities with and without
  itemizing are within $0.01, the unit itemizes when itemized
  deductions exceed the standard deduction, even when both
  liabilities are zero.
- TC (`Calculator._calc_one_year`): the same "itemize if `item >
  std`" tie-break applies only when `std_taxes > 0`; a unit owing no
  tax under either deduction takes the standard deduction.

The reported differences follow from that choice:

- `v26`: PE's AMT income is AGI minus the non-SALT itemized
  deductions (SALT is added back); TC's `c62100` for a
  standard-deduction filer is AGI.  In both units the `v26` diff
  equals PE's `v17` minus property tax.
- `v18`: PE subtracts the larger itemized total, so its taxable income
  is zero.
- `v13` and `v17` show no differences here because `compare.py`
  compares `v13` only for TC non-itemizers (and PE reports the same
  standard deduction) and `v17` only for TC itemizers.

The choice has no effect on any tax amount, so both conventions are
defensible and these are reporting differences only.

### Summary

| Cause | Which model follows the law | Affects tax liability? |
|---|---|---|
| 1. 2023 MFS 37% bracket threshold (`fiitax`) | PE (Rev. Proc. 2022-38: $346,875) | Yes: TC understates MFS tax by up to $4,625 |
| 2. 2021 MFS QBID threshold (`qbid`, `fiitax`) | PE (Rev. Proc. 2020-45: $164,925) | Yes: TC overstates MFS tax by a few dollars |
| 3. Schedule R initial amount for MFS (`fiitax`) | TC (IRC 22(c)(2)(A)(iii): $3,750) | Yes: PE overstates the MFS credit |
| 4. 2021 refundable ODC (`actc`) | TC (2021 Sch 8812 lines 14a-14b; IRC 24(i)) | Not in these samples; a PE error that would overstate refunds for units with less tax liability |
| 5. Itemization tie-break at zero tax (`v18`, `v26`) | Both defensible | No |
