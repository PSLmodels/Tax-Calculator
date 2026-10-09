# Explanations of known differences between Tax-Calculator and PolicyEngine-TAXSIM

This document explains the differences larger than $1 between
Tax-Calculator (TC) and the pinned policyengine-taxsim (PE) version in
[`pe_pin.json`](pe_pin.json) that remain after the translation in
[`VARIABLES.md`](VARIABLES.md) and the `pe_emulation.json` reform.
The differences themselves are listed in
`expected_differences/LYY-taxdiffs-expect.csv`; `compare.py` writes
the actual ones to `work/actual_differences/LYY-taxdiffs-actual.csv`.
Variable names are TAXSIM output names; `diff` means TC minus PE.

Each explanation is classified as one of:
**PE bug** (PE departs from the statute or tax forms; candidate for an
upstream issue),
**TC bug** (reported to the TC developers),
**PE output definition** (the two models compute the same tax but
report an intermediate amount differently), or
**convention** (both models are defensible given the TAXSIM input,
but TC has no parameter that could emulate PE's choice).

Differences removed by the translation itself are not listed here.
One example: `run_tc.py` runs the TC CLI with `--exact`, so TC rounds
phase-out excesses up to the next $1,000 (or other step) as the statute
and PE do; without it TC phased the 2021 child tax credit out smoothly
above the $112,500 head-of-household threshold, giving many $25
differences in `v22` and `fiitax`.


## `a` files (wages, ages, dependents)

### All years: `v26` (AMT income) — PE bug, no tax effect

Every unit whose taxable income is zero has a `v26` difference: TC
reports AMT income equal to AGI, whereas PE reports the standard
deduction.  PE computes `amt_income` as taxable income plus the
standard (or itemized) deduction, and its `taxable_income` is floored
at zero, so the part of the deduction that exceeds AGI is wrongly added
to AMT income.  Form 6251 line 1 instructions say that when taxable
income is zero the filer enters AGI minus the deductions, *as a
negative amount if less than zero*, so AMT income is AGI.  (Example:
a22 id 1, joint, AGI $7,000: TC $7,000, PE $28,700.)  The AMT itself
(`v27`) is zero in both models for all such units, because AMT
income is far below the AMT exemption.

### 2025: `v26` (AMT income) — PE bug, no tax effect

In addition, every 2025 unit with positive taxable income that gets
the OBBBA senior deduction has `diff` equal to that deduction (up to
$6,000 per person aged 65+).  The senior deduction is a section 151
deduction (section 151(d)(5)(C)), which section 56(b)(1)(E) disallows
in computing AMT income, so TC adds it back (Form 6251 line 1a); PE's
`amt_income` adds back only the standard deduction.  `v27` is zero in
both models for these units.

### 2021: `fiitax`, `v22` (child tax credit and credit for other dependents) — TC bugs, now fixed

Before the two TC errors below were fixed on `master` (B1 and B2 in
`PLAN.md`), all 2021 `v22` differences, and therefore all 2021
`fiitax` differences, came from them.  An independent statutory
calculation of the 2021 Schedule 8812 credit reproduces PE's `v22` for
all 10,000 a21 units and reproduced TC's former `v22` when both errors
were introduced.  With the fixes there are no 2021 `v22` or `fiitax`
differences, so none appear in the a21 expect file.

1. **Refundable credit for other dependents (`diff` = -$500 per
   dependent aged 18+, or less when tax is between $0 and the credit).**
   TC's `ODC_is_refundable` is true in 2021, but ARPA made only the
   child credit refundable (section 24(i)); on the 2021 Schedule 8812
   the $500 credit stays limited by tax liability.  TC's `fiitax` is
   too low for units whose tax is less than their credit for other
   dependents.  (Example: a21 id 3, head of household, AGI $17,000,
   dependents aged 5 and 19: TC `v22` $4,100, PE $3,600.)

2. **Uncapped ARPA phase-out (`diff` = +$225, +$825, +$1,225, ...).**
   Section 24(i)(4)(B) limits the first-stage reduction of the ARPA
   credit increase to 5% of the difference between the $200,000
   ($400,000 joint) and the $75,000/$112,500/$150,000 thresholds,
   i.e., $6,250 single, $4,375 head of household, $12,500 joint.  Any
   increase above that cap survives and is reduced only by the regular
   phase-out.  TC's `CTC_new` reduces the increase without this cap,
   so units with a large increase (several children, some under 6)
   and AGI above $200,000 ($400,000 joint) get too little credit.
   (Example: a21 id 33, head of household, AGI $344,000, five children
   aged 5-17: increase $5,600, capped reduction $4,375, so TC `v22`
   $2,800, PE $4,025.)

### 2021: `actc` (refundable child tax credit) — PE output definition

PE's 2021 `refundable_ctc` is
`min(ctc, ctc_refundable_maximum - ctc_phase_out)`, where `ctc`
includes the credit for other dependents, `ctc_refundable_maximum` is
the ARPA child maximum ($3,000 or $3,600 per child), and
`ctc_phase_out` is only the regular $200,000/$400,000 phase-out.  So
PE's refundable amount ignores the first-stage ARPA reduction and
can include credit-for-other-dependents dollars.  On the 2021 Schedule
8812 the refundable amount is the child part of the credit after both
reductions, which is what TC reports (`c07220 + ctc_new`).  PE's `v22` and `fiitax` are nevertheless correct
in every a21 unit, because PE limits `ctc_value` correctly, so this
affects only the reported `actc` split.  The formula above reproduces
PE's `actc` for all 10,000 a21 units.


## `b` files (adds non-labor and business income)

The set-`a` explanations above for `v26` (all years and 2025) and for
2021 `actc` also explain every set-`b` difference in those variables:
the zero-taxable-income `v26` pattern occurs in a few units each year,
the 2025 senior-deduction `v26` pattern in about 900 aged units (`diff`
equals TC's `senior_deduction` to within a few cents), and the formula
for PE's 2021 `refundable_ctc` reproduces PE's `actc` for all 10,000
b21 units.  Since the 2021 TC fixes (B1, B2) the 2021 `v22` and
`fiitax` differences are gone.  The only new pattern is the following.

### All years: `v27` (AMT), `fiitax`, and sometimes `v22`/`actc` — PE bug

Every remaining `v27` difference is a unit to which both models apply
the section 59(j) kiddie-tax AMT exemption cap (head under age 19 and
spouse, if any, under 19; these samples have no full-time-student
input, so the student age limit never applies).  `diff` is 26% of the
standard deduction (e.g., $4,888 = 26% x $18,800 for 2021 head of
household; $5,408 for 2023 head of household; $6,142.50 for 2025 head
of household), or less when PE's AMT is not positive.  PE's
`amt_income_less_exemptions` uses taxable income instead of AMT income
for these filers ("the deductions are not added back"), so PE's AMT
base omits the standard-deduction add-back on Form 6251 line 2a.
Section 59(j) changes only the exemption (limited to earned income
plus the child amount); it does not change AMT income, and the Form
6251 instructions make no exception to line 2a for children.  PE
reports the correct `v26` (AMT income) for these units, but does not
use it.  A scratch TC run with PE's convention removes every set-`b`
`v27` and `fiitax` difference, and the few `v22`/`actc` differences,
which occur in units whose larger TC AMT leaves less tax for the
nonrefundable credits.  (Example: b23 id 3287, head of household aged
17, one child aged 12, wages $1,000, AGI $59,400, taxable income
$38,600: both models give `v26` $59,400, but PE's AMT base is $38,600,
so TC `v27` $7,598, PE $2,190.)

Both models also apply the cap to joint filers aged under 19, although
section 1(g)(2)(C) excludes a child who files a joint return (and so
does section 59(j), which applies only to a child to whom section 1(g)
applies).  This shared error causes no difference here.


## `c` files (adds itemized deductions and child care)

The set-`a` and set-`b` explanations also explain most set-`c`
differences: the zero-taxable-income `v26` pattern (3-7 units per
year, plus the units below), the 2025 senior-deduction `v26` pattern
(about 935 c25 units), PE's 2021 `actc` definition (about 1,080 c21
units; the formula reproduces PE's `actc` for all 10,000 c21 units),
and the kiddie-tax AMT pattern (5-8 units per year).  In set `c` the
kiddie-tax AMT pattern can also change the itemizing choice: each
model picks the deduction giving the lower tax under its own AMT, so
some of these units also differ in `v18`, `v28`, `v26`, and `qbid`
(whose taxable-income limit depends on the deduction).  (Example: c21
id 5788, single, aged 17, itemized deductions $15,000: with TC's AMT,
itemizing gives less tax than the $18,800 standard deduction, so TC
taxable income is $141,750, PE $137,950.)  A scratch TC run with PE's
kiddie-tax AMT convention removes every set-`c` `v27`, `v28`, `qbid`,
`v22`, and kiddie-unit `v18` difference, and every `fiitax` and 2022-2025
`actc` difference except the CDCC units below.  The new patterns
follow.

### 2022-2024: `v24` (child and dependent care credit), `fiitax` — convention

Every `v24` difference is a married couple whose spouse is aged 17
and earns less than $3,000 (one qualifying child under 13) or $6,000
(two or more).  Section 21(d)(2) deems a spouse who is a full-time
student (or incapable of self-care) to earn at least those amounts.
TAXSIM input has no student flag, and TC assumes no one is a student,
so TC limits the creditable expenses to the spouse's actual earnings.
PE imputes every person aged 5-17 to be a K-12 full-time student
(`is_in_k12_school`), so its `min_head_spouse_earned` uses the deemed
amount.  `diff` is the credit rate (20% at these incomes) times the
shortfall of the spouse's earnings below $3,000 or $6,000.  Neither
model is wrong given the input, and TC has no input or parameter that
could emulate PE's imputation.  (Example: c22 id 7928, joint, head
aged 25, spouse aged 17 with wages $3,000, three children under 13,
child care $7,000: TC `v24` $600, PE $1,200.)  The 2021 sample has
no such unit with a nonzero credit.

### 2021, 2023, 2025: `v18` (taxable income), `v26` — convention, no tax effect

When itemizing and the standard deduction give the same tax, PE
itemizes whenever itemized deductions exceed the standard deduction,
whereas TC does so only if the unit owes tax (before credits) under
either deduction (see the comment in `Calculator._calc_one_year`).
So a unit that owes no regular tax under either deduction (here,
because its taxable income is zero or consists only of qualified
dividends and capital gains taxed at 0%)
takes the standard deduction in TC and itemizes in PE.  Tax and
credits are the same; only taxable income and AMT income differ.
(Example: c25 id 1416, single, aged 72, AGI $45,850, itemized
deductions $66,000: TC takes the $25,625 standard deduction and
reports taxable income $14,225, PE reports $0; both give `fiitax`
-$1,700.)  A scratch TC run with PE's tie-breaking rule removes these
`v18` differences and leaves only `v26` differences of the
zero-taxable-income kind.

### 2025: `v17` (itemized deductions), `v26` — PE output definition, no tax effect

PE's `salt_deduction` limits the SALT deduction to AGI (less
exemptions), under the default-on simulation option
`gov.simulation.limit_itemized_deductions_to_taxable_income`; the
statute has no such limit.  It matters only when SALT exceeds AGI,
when taxable income is zero either way.  No 2021-2024 unit in these
samples is affected; with the 2025 $40,000 SALT cap, one c25 unit is.  (c25 id 9032: AGI $26,750,
property tax $30,000, other itemized deductions $38,000: TC `v17`
$68,000, PE $64,750.  Its `v26` difference is the zero-taxable-income
pattern with PE's SALT add-back also limited to $26,750.)
