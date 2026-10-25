# Test Results Summary

```
(taxcalc-dev) pe_taxsim> date
Sat Oct 24 17:35:13 EDT 2026

(taxcalc-dev) pe_taxsim> head -12 test_results.expect
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
differences below do not affect income or payroll tax liability.

```
(taxcalc-dev) pe_taxsim> awk '$3~/differences/||NF==5' test_results.expect
a21: 1489 differences (|tc - pe| > 1) in 1 variables
variable  compared  count  max_abs  mean_abs
    actc     10000   1489   1600.0     650.2
a22: 0 differences (|tc - pe| > 1) in 0 variables
a23: 0 differences (|tc - pe| > 1) in 0 variables
a24: 0 differences (|tc - pe| > 1) in 0 variables
a25: 0 differences (|tc - pe| > 1) in 0 variables
b21: 1009 differences (|tc - pe| > 1) in 1 variables
variable  compared  count  max_abs  mean_abs
    actc     10000   1009   1600.0    644.25
b22: 0 differences (|tc - pe| > 1) in 0 variables
b23: 0 differences (|tc - pe| > 1) in 0 variables
b24: 0 differences (|tc - pe| > 1) in 0 variables
b25: 0 differences (|tc - pe| > 1) in 0 variables
c21: 1084 differences (|tc - pe| > 1) in 3 variables
variable  compared  count  max_abs  mean_abs
     v18     10000      1   1250.0   1250.00
     v26     10000      1  30000.0  30000.00
    actc     10000   1082   1600.0    644.82
c22: 0 differences (|tc - pe| > 1) in 0 variables
c23: 1 differences (|tc - pe| > 1) in 1 variables
variable  compared  count  max_abs  mean_abs
     v26     10000      1  38000.0   38000.0
c24: 0 differences (|tc - pe| > 1) in 0 variables
c25: 11 differences (|tc - pe| > 1) in 3 variables
variable  compared  count  max_abs  mean_abs
     v17      6834      1   3250.0   3250.00
     v18     10000      4  14225.0   7156.25
     v26     10000      6  41000.0  31333.33
```

# Diffs Analysis

## Agent:

Claude Code 2.1.310 running Opus 5.5 with medium effort

## Prompt:

Read the ./taxcalc/validation/pe_taxsim/test_results.expect file and
analyze each of the differences, writing a summary of the nature and
cause of each difference to the ./diffs.md file.

## Results:

The PE pin is policyengine-taxsim 3.2.5 (`2e3e6cb0`) with
policyengine-us 2.62.8 and policyengine-core 3.33.12.
In the PE output, `diff = tc - pe` throughout.

None of the differences changes `fiitax`, `fica`, or any other
tax-liability variable.  They have three distinct causes:

| # | Samples | Variable(s) | Units | Cause |
|---|---|---|---|---|
| 1 | a21, b21, c21 | `actc` | 1489 + 1009 + 1082 | PE treats part of the 2021 credit for other dependents (ODC) as refundable |
| 2 | c21, c23, c25 | `v26`, `v18` | 8 units (`v26` in all 8, `v18` in 5) | The two models break the itemization tie differently when the unit owes no tax either way |
| 3 | c25 | `v17` | 1 unit | PE limits the SALT deduction to AGI |

Cause 1 is a PE error.  Cause 2 is a difference in reporting
conventions with no effect on tax.  Cause 3 is a PE simulation
convention that has no basis in the statute.

### 1. 2021 `actc`: PE makes part of the ODC refundable

#### Nature

These are the only differences in the a21 and b21 samples, and nearly
all of those in c21:

| Sample | Units | max \|diff\| | mean \|diff\| |
|---|---|---|---|
| a21 | 1489 | 1600 | 650.20 |
| b21 | 1009 | 1600 | 644.25 |
| c21 | 1082 | 1600 | 644.82 |

Every difference is negative (PE's `refundable_ctc` is larger than
TC's `c07220 + ctc_new`).  Most are multiples of $500, the 2021 ODC
amount; in a21, 928 are -$500, 380 are -$1,000, and 43 are -$1,500.
Every unit with a difference has both:

- at least one qualifying child (under 18 in 2021) and at least one
  other dependent (age 18 or older), so its ODC is greater than zero;
  and
- AGI above the ARPA phase-out threshold ($75,000 single, $112,500
  head of household, $150,000 joint), so the ARPA increase is at
  least partly phased out.

The total CTC+ODC (`v22`) and `fiitax` agree in every unit.  The
models differ only in how they divide the credit between the
refundable and nonrefundable parts.  For these higher-income units,
tax liability absorbs the nonrefundable part, so the total credit is
the same either way.

#### Cause

When the credit is fully refundable (2021), PE's `refundable_ctc` is:

```
refundable_ctc = min(ctc_refundable_maximum - ctc_phase_out, ctc)
```

where:

- `ctc_refundable_maximum` is the sum of the ARPA per-child maximums
  (children only);
- `ctc_phase_out` is only the regular $50-per-$1,000 phase-out above
  $200,000/$400,000;
- `ctc` is the total credit **including the ODC**, after **both**
  the ARPA phase-out and the regular phase-out.

The ARPA phase-out lowers `ctc` but not the first argument of the
`min`.  As a result, once the ARPA phase-out has started, the ODC
offsets it, and up to the full ODC is reported as refundable.  The
difference equals:

```
min(ODC maximum, ARPA phase-out amount, credit remaining after phase-outs)
```

The third term is the binding one only in a few very-high-income
units where the regular phase-out has wiped out nearly all of the
credit.

Applying this formula to the sample inputs reproduces PE's `actc`
exactly for all 30,000 units in a21, b21, and c21.

Tax-Calculator follows the 2021 Schedule 8812.  Line 14a gives the ODC
first claim on the credit left after the phase-outs (the smaller of
line 7 and line 12), and only the remainder (line 14b) is the
refundable CTC.  `ChildDepTaxCredit` in `calcfunctions.py` implements
exactly this (`odc = min(line7, line12)`, `c07220 = line12 - odc`).
Under IRC 24(i) as added by ARPA, refundability does not extend to the
$500 credit under 24(h)(4) for other dependents.  So PE overstates the
2021 refundable CTC, and understates the nonrefundable ODC by the same
amount.

The differences occur only in 2021 because PE's refundable branch for
2022-2025 (not fully refundable) uses the per-child refundable cap and
the earned-income phase-in.  That branch does not let the ODC into the
refundable amount.

### 2. `v26` (AMT income) and `v18` (taxable income) in c21, c23, c25

#### Nature

| Sample | taxsimid | Variable | PE | TC | diff |
|---|---|---|---|---|---|
| c21 | 5526 | v18 | 0 | 1,250 | 1,250 |
| c21 | 5526 | v26 | -8,250 | 21,750 | 30,000 |
| c23 | 2575 | v26 | -16,000 | 22,000 | 38,000 |
| c25 | 1416 | v18 | 0 | 14,225 | 14,225 |
| c25 | 1416 | v26 | 4,850 | 45,850 | 41,000 |
| c25 | 4972 | v18 | 0 | 10,150 | 10,150 |
| c25 | 4972 | v26 | 26,850 | 56,850 | 30,000 |
| c25 | 5168 | v18 | 0 | 875 | 875 |
| c25 | 5168 | v26 | -7,500 | 32,500 | 40,000 |
| c25 | 9417 | v18 | 19,900 | 23,275 | 3,375 |
| c25 | 9417 | v26 | 25,900 | 54,900 | 29,000 |
| c25 | 8815 | v26 | 11,500 | 42,500 | 31,000 |
| c25 | 9018 | v26 | 14,000 | 31,000 | 17,000 |

All eight units have the same profile:

- AGI of $22,000-$57,000, mostly from small wages, pensions,
  dividends, and interest;
- itemized deductions (large mortgage interest and property taxes)
  larger than the standard deduction;
- zero regular income tax and zero AMT under **either** deduction
  (TC `taxbc` = 0, PE `v28` = 0);
- identical `fiitax` in the two models (all of it refundable credits).

#### Cause

The two models break the itemize-or-not tie differently when tax is
the same under both choices:

- **PE** (`tax_unit_itemizes`): when the two tax liabilities are
  within $0.01 of each other, PE itemizes if itemized deductions
  exceed the standard deduction.  This rule applies even when both
  liabilities are zero.
- **TC** (`Calculator._calc_one_year`): it applies the same
  "itemize if `item > std`" tie-break only when `std_taxes > 0`.  A
  unit owing no tax under either choice takes the standard deduction
  (see the comment there: "a unit owing no tax under either deduction
  has no reason to itemize").

So in these eight units PE itemizes and TC takes the standard
deduction.  The comparisons follow arithmetically:

- **`v26`**: PE's AMTI is AGI minus the itemized deductions other
  than SALT, because SALT is added back.  TC's `c62100` for a
  standard-deduction filer is just AGI.  In every unit the
  difference equals PE's `v17` minus `proptax`.  For example, unit
  c21-5526 has 35,000 - 5,000 = 30,000, and unit c25-9417 (no
  property tax) has 29,000 - 0 = 29,000.
- **`v18`**: PE subtracts the larger itemized total, so its taxable
  income is lower, and often zero.  For example, unit c25-1416 in TC
  has 45,850 - 25,625 standard - 6,000 senior = 14,225.  In PE,
  66,000 itemized exceeds AGI.  `v18` agrees for units c23-2575,
  c25-8815, and c25-9018, because their taxable income is zero under
  either deduction.

`v13`/`v17` show no differences for these units because `compare.py`
checks `v13` only for TC non-itemizers and `v17` only for TC
itemizers.  The itemizing choice therefore shows up only in `v18` and
`v26`.  The choice has no effect on any tax amount.  Both models are
defensible, so these are expected reporting differences.

### 3. `v17` (itemized deductions) in c25, unit 9032

#### Nature

| Sample | taxsimid | Variable | PE | TC | diff |
|---|---|---|---|---|---|
| c25 | 9032 | v17 | 64,750 | 68,000 | 3,250 |

The unit is a head of household with AGI of $26,750, property taxes
of $30,000, and mortgage+other itemized deductions of $38,000.  Both
models itemize (TC's standard-deduction tax is $12.50 and its
itemizing tax is $0), and `v18` (0), `v26` (-11,250), and `fiitax`
agree.

#### Cause

PE's `salt_deduction` applies the simulation parameter
`gov.simulation.limit_itemized_deductions_to_taxable_income`, which is
`true` for all years:

```
salt = min_(salt, max_(0, agi - exemptions))
```

This caps the $30,000 of property tax at AGI ($26,750), so PE's
itemized total is 26,750 + 38,000 = 64,750.  TC deducts the full
$30,000 (below the 2025 $40,000 SALT cap), giving 68,000.  The
statute has no such AGI cap on the SALT deduction, so this is a PE
modeling convention.

The cap does not change taxable income, because taxable income is
zero either way.  AMTI agrees because PE adds back the same capped
SALT amount that it deducted.  The difference appears in only one
unit because it requires itemizing, SALT greater than AGI, and TC
also itemizing so that `v17` is compared.

### Summary

| Cause | Which model follows the law | Affects tax liability? |
|---|---|---|
| 1. 2021 refundable ODC (`actc`) | TC (2021 Sch 8812 lines 14a-14b; IRC 24(i)) | No in these samples (the units owe enough tax to absorb the ODC); a PE error that could overstate refunds for a unit with less tax liability |
| 2. Itemization tie-break when no tax is owed (`v18`, `v26`) | Both defensible | No |
| 3. PE caps SALT at AGI (`v17`) | TC (no statutory AGI cap on SALT) | No |

