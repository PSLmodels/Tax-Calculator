# Test Results Summary

```
(taxcalc-dev) pe_taxsim> awk 'NR<=12' test_results.expect
===== PE_PIN =====
policyengine_taxsim_repo: https://github.com/PolicyEngine/policyengine-taxsim
policyengine_taxsim_sha: 2e3e6cb003aefc977ee4a6f9b2a8a701595dec2f
policyengine_taxsim_sha_date: 2026-10-23
policyengine_taxsim_version: 3.2.5
policyengine_us_version: 2.62.8
policyengine_core_version: 3.33.12
python_version: 3.13
python_version_resolved: 3.13.16
uv_version: 0.12.23
pinned_on: 2026-10-24
pe_cli_options: --scorp-treatment active
```

The remainder of the `test_results.expect` file shows no differences
in either federal income tax or payroll taxes.  The intermediate variable
differences below do not affect income or payroll tax liability in the
validation samples used here.

```
(taxcalc-dev) pe_taxsim> awk 'NR>12' test_results.expect
===== a21 =====
a21: 1489 differences (|tc - pe| > 1) in 1 variables
variable  compared  count  max_abs  mean_abs
    actc     10000   1489   1600.0     650.2
===== a22 =====
a22: 0 differences (|tc - pe| > 1) in 0 variables
===== a23 =====
a23: 0 differences (|tc - pe| > 1) in 0 variables
===== a24 =====
a24: 0 differences (|tc - pe| > 1) in 0 variables
===== a25 =====
a25: 0 differences (|tc - pe| > 1) in 0 variables
===== b21 =====
b21: 1009 differences (|tc - pe| > 1) in 1 variables
variable  compared  count  max_abs  mean_abs
    actc     10000   1009   1600.0    644.25
===== b22 =====
b22: 0 differences (|tc - pe| > 1) in 0 variables
===== b23 =====
b23: 0 differences (|tc - pe| > 1) in 0 variables
===== b24 =====
b24: 0 differences (|tc - pe| > 1) in 0 variables
===== b25 =====
b25: 0 differences (|tc - pe| > 1) in 0 variables
===== c21 =====
c21: 1084 differences (|tc - pe| > 1) in 3 variables
variable  compared  count  max_abs  mean_abs
     v18     10000      1   1250.0   1250.00
     v26     10000      1  30000.0  30000.00
    actc     10000   1082   1600.0    644.82
===== c22 =====
c22: 0 differences (|tc - pe| > 1) in 0 variables
===== c23 =====
c23: 1 differences (|tc - pe| > 1) in 1 variables
variable  compared  count  max_abs  mean_abs
     v26     10000      1  38000.0   38000.0
===== c24 =====
c24: 0 differences (|tc - pe| > 1) in 0 variables
===== c25 =====
c25: 11 differences (|tc - pe| > 1) in 3 variables
variable  compared  count  max_abs  mean_abs
     v17      6834      1   3250.0   3250.00
     v18     10000      4  14225.0   7156.25
     v26     10000      6  41000.0  31333.33
```

# Diffs Analysis

## Agent:

Claude Code 2.1.310 running Opus 5.5 with medium effort
on Tax-Calculator master branch at Sun Oct 25 11:15:24 EDT 2026.

## Prompt:

Read the taxcalc/validation/pe_taxsim/test_results.expect file and
analyze each of the differences, writing a summary of the nature and
cause of each difference at the bottom of the
taxcalc/validation/pe_taxsim/SUMMARY.md file just below the Results:
line.

## Results:

In the comparisons below, `diff = tc - pe`.  None of the differences
changes `fiitax`, `fica`, or any other tax-liability variable.  There
are three distinct causes:

| # | Samples | Variable(s) | Units | Cause |
|---|---|---|---|---|
| 1 | a21, b21, c21 | `actc` | 1489 + 1009 + 1082 | PE counts part of the 2021 other-dependent credit (ODC) as refundable CTC |
| 2 | c21, c23, c25 | `v26`, `v18` | 8 (`v26` in all 8, `v18` in 5) | Different itemization tie-break when a unit owes no tax either way |
| 3 | c25 | `v17` | 1 | PE limits the SALT deduction to AGI |

### 1. 2021 `actc` (a21, b21, c21)

**Nature.**  These are all the a21 and b21 differences and 1082 of the
1084 c21 differences.  Every `diff` is negative (PE's refundable CTC
is larger).  Most are multiples of the $500 ODC: in a21, 928 are
-$500, 380 are -$1,000, and 43 are -$1,500; the rest are smaller
amounts.  Every unit with a difference has at least one qualifying
child (under 18) and at least one other dependent (18 or older), and
has AGI above the ARPA phase-out threshold ($75,000 single, $112,500
head of household, $150,000 joint).  The total credit (`v22`) and
`fiitax` agree in every one of these units, so the two models differ
only in how they split the same credit between its refundable CTC and
nonrefundable ODC parts.  Units above the ARPA threshold that have
both kinds of dependents but show no difference are, with a handful
of exceptions, units whose credit is fully phased out (AGI above
about $250,000).

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
threshold, or units whose remaining credit is small).  Applying the
PE formula to the sample inputs reproduces PE's `actc` exactly (within
$1) for all 30,000 units in a21, b21, and c21.

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

### 2. `v26` and `v18` (c21, c23, c25)

**Nature.**

| Sample-id | `v18` PE | `v18` TC | `v26` PE | `v26` TC | `v26` diff |
|---|---|---|---|---|---|
| c21-5526 | 0 | 1,250 | -8,250 | 21,750 | 30,000 |
| c23-2575 | 0 | 0 | -16,000 | 22,000 | 38,000 |
| c25-1416 | 0 | 14,225 | 4,850 | 45,850 | 41,000 |
| c25-4972 | 0 | 10,150 | 26,850 | 56,850 | 30,000 |
| c25-5168 | 0 | 875 | -7,500 | 32,500 | 40,000 |
| c25-8815 | 0 | 0 | 11,500 | 42,500 | 31,000 |
| c25-9018 | 0 | 0 | 14,000 | 31,000 | 17,000 |
| c25-9417 | 19,900 | 23,275 | 25,900 | 54,900 | 29,000 |

All eight units have modest AGI ($21,750-$56,850), itemized deductions
(mostly mortgage interest and property tax) larger than the standard
deduction, and zero income tax before credits under either deduction:
any taxable income they have is preferential income (qualified
dividends and long-term gains, `dwks10` > 0) taxed at 0%, so TC
`taxbc` and `c09600` are zero and PE `v28` is zero.  `fiitax` agrees
in all eight (it consists entirely of refundable credits).

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
  standard-deduction filer is AGI.  In every unit the `v26` diff
  equals PE's `v17` minus property tax.
- `v18`: PE subtracts the larger itemized total, so its taxable income
  is lower (zero in all but c25-9417).  In c23-2575, c25-8815, and
  c25-9018 taxable income is zero either way, so only `v26` differs.
- `v13` and `v17` show no differences here because `compare.py`
  compares `v13` only for TC non-itemizers (and PE reports the same
  standard deduction) and `v17` only for TC itemizers.

The choice has no effect on any tax amount, so both conventions are
defensible and these are reporting differences only.

### 3. `v17` (c25, unit 9032)

**Nature.**  PE `v17` is $64,750 and TC `v17` is $68,000 (diff
$3,250).  The unit is a head of household with AGI of $26,750,
property tax of $30,000, and $38,000 of mortgage interest and other
itemized deductions.  Both models itemize: TC's standard-deduction
tax is $12.50 (on $125 of ordinary taxable income), versus zero when
itemizing, so TC's tie-break does not apply.  `v18` (0), `v26`
(-11,250), and `fiitax` agree.

**Cause.**  PE's `salt_deduction` applies the simulation parameter
`gov.simulation.limit_itemized_deductions_to_taxable_income`, which is
`true` for all years:

```
salt = min_(salt, max_(0, agi - exemptions))
```

This caps the $30,000 of property tax at AGI ($26,750), so PE's
itemized total is 26,750 + 38,000 = 64,750.  TC deducts the full
$30,000 (under the 2025 $40,000 SALT cap), giving 68,000.  The statute
has no AGI limit on the SALT deduction, so this is a PE modeling
convention.  It can never change taxable income, because it binds only
when SALT alone exceeds AGI, in which case taxable income is zero
either way; and it leaves AMT income unchanged because PE adds back
the same capped SALT amount it deducted (26,750 - 38,000 = -11,250 in
both models).  It appears in only one unit because it requires SALT
greater than AGI and TC also itemizing, so that `v17` is compared.

### Summary

| Cause | Which model follows the law | Affects tax liability? |
|---|---|---|
| 1. 2021 refundable ODC (`actc`) | TC (2021 Sch 8812 lines 14a-14b; IRC 24(i)) | Not in these samples; a PE error that would overstate refunds for units with less tax liability |
| 2. Itemization tie-break at zero tax (`v18`, `v26`) | Both defensible | No |
| 3. PE caps SALT at AGI (`v17`) | TC (no statutory AGI limit on SALT) | No |
