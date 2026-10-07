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
**TC bug** (reported to the TC developers), or
**PE output definition** (the two models compute the same tax but
report an intermediate amount differently).

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

### 2021: `fiitax`, `v22` (child tax credit and credit for other dependents) — TC bugs

All 2021 `v22` differences, and therefore all 2021 `fiitax`
differences, come from two TC errors.  An independent statutory
calculation of the 2021 Schedule 8812 credit reproduces PE's `v22` for
all 10,000 a21 units and reproduces TC's `v22` when both errors are
introduced.

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

### 2021: `actc` (refundable child tax credit) — PE output definition (and TC bugs above)

PE's 2021 `refundable_ctc` is
`min(ctc, ctc_refundable_maximum - ctc_phase_out)`, where `ctc`
includes the credit for other dependents, `ctc_refundable_maximum` is
the ARPA child maximum ($3,000 or $3,600 per child), and
`ctc_phase_out` is only the regular $200,000/$400,000 phase-out.  So
PE's refundable amount ignores the first-stage ARPA reduction and
can include credit-for-other-dependents dollars.  On the 2021 Schedule
8812 the refundable amount is the child part of the credit after both
reductions, which is what TC reports (`c07220 + ctc_new`, apart from
the cap bug above).  PE's `v22` and `fiitax` are nevertheless correct
in every a21 unit, because PE limits `ctc_value` correctly, so this
affects only the reported `actc` split.  The formula above reproduces
PE's `actc` for all 10,000 a21 units.
