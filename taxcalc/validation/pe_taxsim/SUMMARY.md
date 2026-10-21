# Test Results Summary

```
(taxcalc-dev) pe_taxsim> date
Wed Oct 21 14:52:41 EDT 2026

(taxcalc-dev) pe_taxsim> head -12 test_results.expect
===== PE_PIN =====
policyengine_taxsim_repo: https://github.com/PolicyEngine/policyengine-taxsim
policyengine_taxsim_sha: 3e2a7589c8acda0edd2aa9e748d726c9ca9262d0
policyengine_taxsim_sha_date: 2026-09-30
policyengine_taxsim_version: 3.0.1
policyengine_us_version: 2.30.1
policyengine_core_version: 3.32.21
python_version: 3.13
python_version_resolved: 3.13.16
uv_version: 0.12.23
pinned_on: 2026-10-07
pe_cli_options: --scorp-treatment active

(taxcalc-dev) pe_taxsim> grep -E 'diff|fiitax|v27' test_results.expect
a21: 2617 differences (|tc - pe| > 1) in 2 variables
a22: 1193 differences (|tc - pe| > 1) in 1 variables
a23: 1257 differences (|tc - pe| > 1) in 1 variables
a24: 1377 differences (|tc - pe| > 1) in 1 variables
a25: 2259 differences (|tc - pe| > 1) in 1 variables
b21: 1018 differences (|tc - pe| > 1) in 4 variables
  fiitax     10000      4   4888.0   4125.62
     v27     10000      4   4888.0   4217.38
b22: 14 differences (|tc - pe| > 1) in 4 variables
  fiitax     10000      6   5044.0   3543.08
     v27     10000      6   5044.0   3543.08
b23: 15 differences (|tc - pe| > 1) in 4 variables
  fiitax     10000      6  5408.01   3823.92
     v27     10000      6  5408.00   4257.58
b24: 13 differences (|tc - pe| > 1) in 3 variables
  fiitax     10000      6   4526.0   3469.05
     v27     10000      6   4526.0   3469.05
b25: 912 differences (|tc - pe| > 1) in 5 variables
  fiitax     10000     12  6142.50   4148.46
     v27     10000     12  6142.50   4467.34
c21: 1108 differences (|tc - pe| > 1) in 7 variables
  fiitax     10000      8  2834.62   2002.45
     v27     10000      7  2618.05   2127.29
c22: 22 differences (|tc - pe| > 1) in 6 variables
  fiitax     10000      8   2600.0   1329.62
     v27     10000      6   2600.0   1639.50
c23: 23 differences (|tc - pe| > 1) in 6 variables
  fiitax     10000      7   2340.0   1331.50
     v27     10000      6   2600.0   1658.83
c24: 23 differences (|tc - pe| > 1) in 7 variables
  fiitax     10000      7   2600.0   1587.14
     v27     10000      4   2600.0   2407.25
c25: 957 differences (|tc - pe| > 1) in 7 variables
  fiitax     10000      5   2529.0   1368.80
     v27     10000      5   2529.0   1368.80
```

# b25 Diffs Analysis

## Agent:

Claude Code 2.1.306 running Opus 5.5 with medium effort

## Prompt:

Analyze the twelve tax units with an income tax difference in the b25
validation sample described in the taxcalc/validation/pe_taxsim/
directory tree by comparing the tax logic in Tax-Calculator with the
tax logic in PolicyEngine-US, highlighting any between-model logic
differences, and noting any differences between model logic and the
logic described in the 2025 IRS tax forms and instructions.

## Results:

### Overview

All twelve `fiitax` differences are AMT (`v27`) differences, and all
twelve units are single heads of household aged 17 or 18.  One PE
rule explains every difference: for filers it treats as subject to
the kiddie tax, PE computes Form 6251 line 6 from regular taxable
income instead of from AMTI.  Tax-Calculator follows the IRS form;
PE does not.

### Between-model logic difference

PE's `amt_income_less_exemptions` (policyengine-us 2.30.1) contains:

```python
# For filers subject to the kiddie tax, the deductions are not added back
applied_income = where(kiddie_tax_applies, taxable_income, amt_income)
return max_(0, applied_income - amt_exemption)
```

so for these filers PE's line 6 is taxable income minus the
exemption.  Tax-Calculator's `AMT` function uses
`line6 = c62100 - line5` (AMTI minus the exemption) for everyone.

Everything else agrees:

- AMTI (`v26`) is identical in both models for all twelve units.
- Both cap the exemption at earned income plus $9,550 (IRC 59(j))
  for a non-joint filer under age 19.
- Both reduce earned income for self-employment tax (unit 9479, the
  only one with self-employment income, matches).

So PE's line 6 is too low by the standard deduction (or by any
itemized deductions not added back).

Worked example, unit 773:

| | TC | PE |
|---|---|---|
| Exemption ($26,000 wages + $9,550) | $35,550 | $35,550 |
| Line 6 | $111,950 - $35,550 = $76,400 | $88,325 - $35,550 = $52,775 |
| Regular tax (`v28`, same in both) | $12,536.50 | $12,536.50 |
| Tentative minimum tax | $19,754.00 | $13,611.50 |
| AMT | $7,217.50 | $1,075.00 |

The $23,625 line-6 gap is the 2025 head-of-household standard
deduction, and 26% of it is $6,142.50, the largest difference, which
occurs in five of the twelve units.  The other seven differ by less
because, under PE's line 6, their tentative minimum tax is at or near
their regular tax; four of them have no AMT at all in PE.

Verification: a scratch copy of Tax-Calculator's `AMT` function,
changed so that line 6 uses `c04800` for young non-joint heads, was
run on b25 with exact calculations.  It reproduced PE's `fiitax`,
`v27`, `v22`, and `actc` to the cent for all twelve units, and kept
`fiitax` within $0.04 of PE's for the other 125 young non-joint heads
in the sample, none of whom has AMT in either model.  No repository
file was changed.

Unit 5233's `v22` and `actc` differences are a consequence.  TC's
higher AMT means a larger tax liability, so the entire $7,600 child
tax credit plus credit for other dependents is nonrefundable and TC's
refundable CTC is $0.  PE's lower liability allows only $3,620.50 of
nonrefundable credit, and PE pays $153 refundable using the
three-or-more-children method (7.65% payroll tax on $2,000 of wages).
Both models limit the nonrefundable credit by tax including AMT,
which is correct.

### Comparison with the 2025 IRS forms and instructions

- Line 6: the 2025 Form 6251 instructions compute line 6 as line 4
  minus line 5, and line 2a adds back the standard deduction for
  anyone who does not itemize, with no exception for children; IRC
  55(b)(1)(A)(ii) says the same.  PE's rule is a PE bug;
  Tax-Calculator's logic is correct.

- Who counts as a child: the 2025 Form 8615 conditions are age under
  18; or age 18 with earned income not more than half of the child's
  support; or a full-time student aged 19-23 meeting the same support
  test; plus at least one living parent and no joint return.  Both
  models apply the rule to every non-joint head under 19, with no
  support or parent-alive test, because TAXSIM inputs carry no such
  information.  Several of these 18-year-olds (unit 7486 has $55,000
  of wages and five dependents) would probably fail the support test
  in reality, in which case their AMT would be zero in both models.
  This is a shared modeling simplification, not a between-model
  difference.  A 17- or 18-year-old head of household with up to five
  dependents is also an artifact of the synthetic sample.  All twelve
  units meet the unearned-income condition.

- The $9,550 amount: the HTML 2025 Form 6251 instructions that could
  be read do not state the child exemption limit.  Both models take
  $9,550 from Rev. Proc. 2024-40 under IRC 59(j).

### Separate difference with no b25 tax effect

The 886 `v26` differences (mostly exactly $12,000 or $6,000) come
from the 2025 senior deduction.  The 2025 Form 6251 line 1a starts
from Form 1040 line 14 minus Schedule 1-A line 37, which adds the
senior deduction back for AMT.  Tax-Calculator does this; PE's
`amt_income` does not.  None of those units owes AMT in either model,
so no b25 tax amount changes, but this is a second PE departure from
the 2025 form.
