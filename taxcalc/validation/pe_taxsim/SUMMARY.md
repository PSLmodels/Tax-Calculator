# Test Results Summary

The differences recorded in [`test_results.expect`](test_results.expect)
are explained below one assumption-set letter at a time.  Causes are
numbered consecutively across the letters, and a cause first explained
for one letter is not explained again for a later one.  A summary of
the causes that are errors in either model is at the end.

In the comparisons below, `diff = tc - pe`, Tax-Calculator (TC) runs
current-law policy plus [`pe_emulation.json`](pe_emulation.json), and
PolicyEngine (PE) is the pinned version of `policyengine-taxsim` in
[`pe_pin.json`](pe_pin.json) (run with `--scorp-treatment active`),
whose variables are described in [`VARIABLES.md`](VARIABLES.md).
The samples contain single, joint, head-of-household, and married
filing separately (MFS, `mstat=6`) units; MFS units never have
dependents.

There are no payroll tax differences in any sample.  The only
federal income tax (`fiitax`) differences are in seven a21 MFS units
and are caused by a PE error (cause 1).  The other differences do not
affect income or payroll tax liability in these samples.


Emulation conventions
---------------------

`pe_emulation.json` makes TC adopt three PE conventions, none of which
is an error in either model:

| # | TC parameter | Why |
|---|---|---|
| 1 | `eitc_claim_prob_scale = 9e99` | PE computes EITC entitlement (full take-up) |
| 2 | `actc_claim_prob_scale = 9e99` | PE computes ACTC entitlement (full take-up) |
| 3 | `SS_thd1 = SS_thd2 = 0` for MFS | PE treats every MFS filer as having lived with the spouse, so the taxable Social Security base amounts are zero |

Without (1) and (2), TC's random credit non-claiming zeroes the EITC
or ACTC of some units in each sample.  Without (3), TC treats every
MFS unit as having lived apart from the spouse all year (TC has no
lived-apart flag) and so applies the single filer's base amounts in
the taxable Social Security benefits worksheet.


Letter a (2021-2025)
--------------------

```
===== a21 =====
a21: 1118 differences (|tc - pe| > 1) in 2 variables
variable  compared  count  max_abs  mean_abs
  fiitax     10000      7     10.0     10.00
    actc     10000   1111   1600.0    650.81
===== a22 =====
a22: 0 differences (|tc - pe| > 1) in 0 variables
===== a23 =====
a23: 0 differences (|tc - pe| > 1) in 0 variables
===== a24 =====
a24: 0 differences (|tc - pe| > 1) in 0 variables
===== a25 =====
a25: 0 differences (|tc - pe| > 1) in 0 variables
```

There are no payroll tax differences, and there are no differences at
all in 2022-2025.  Every 2021 difference is explained by one of two
causes:

| # | Years | Variable(s) | Units (a21) | Cause | Wrong model |
|---|---|---|---|---|---|
| 1 | 2021 | `fiitax` | 7 | MFS Schedule R credit uses the wrong initial amount | PE |
| 2 | 2021 | `actc` | 1111 | Part of the credit for other dependents (ODC) counted as refundable CTC | PE |

Cause 1 changes tax liability (PE's tax is too low); cause 2 does not
in these samples.

### 1. 2021 MFS Schedule R credit (PE error)

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
$15,000 of wages show no difference.  The credit is so small for MFS
filers that it shows up only when the unit's tax is also small, which
in these samples (wages in $1,000 steps) happens only in 2021.

Under the statute, an MFS filer who lived with the spouse at any time
during the year gets no Schedule R credit at all (IRC 22(e)(1)).
`pe_emulation.json` already assumes that every MFS unit lived with the
spouse, as PE does when it computes taxable Social Security benefits,
but both models allow the credit to every MFS filer aged 65 or older.

### 2. 2021 refundable CTC and the ODC (PE error)

**Nature.**  These are all the remaining 2021 differences.  Every
`diff` is negative (PE's refundable CTC is larger).  Most are
multiples of the $500 ODC: in a21, 684 are -$500, 273 are -$1,000, and
42 are -$1,500; the rest are smaller amounts.  Every unit with a
difference is a joint or head-of-household unit with at least one
qualifying child (under 18) and at least one other dependent (18 or
older), and has AGI above the ARPA phase-out threshold ($112,500 head
of household, $150,000 joint).  The total credit (`v22`) agrees in
every one of these units, so the two models differ only in how they
split the same credit between its refundable CTC and nonrefundable
ODC parts.

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
dependents, so PE overstates the 2021 refundable CTC and understates
the nonrefundable ODC by the same amount.  It leaves tax unchanged in
these samples only because each unit's tax liability is large enough
to absorb the nonrefundable ODC; a unit with less tax liability would
get too large a refund from PE.  The error is limited to 2021 because
PE's 2022-2025 branch caps the refundable amount per child and phases
it in with earnings, which keeps the ODC out.


Letter b (2021-2025)
--------------------

Set `b` adds self-employment, business, S-corporation, investment,
rental, pension, Social Security, and unemployment income to the
set-`a` units.

```
===== b21 =====
b21: 802 differences (|tc - pe| > 1) in 1 variables
variable  compared  count  max_abs  mean_abs
    actc     10000    802   1600.0     616.9
===== b22 =====
b22: 0 differences (|tc - pe| > 1) in 0 variables
===== b23 =====
b23: 0 differences (|tc - pe| > 1) in 0 variables
===== b24 =====
b24: 0 differences (|tc - pe| > 1) in 0 variables
===== b25 =====
b25: 0 differences (|tc - pe| > 1) in 0 variables
```

There are no payroll tax or `fiitax` differences, and there are no
differences at all in 2022-2025.  Every b21 difference is explained by
set-`a` cause 2; there are no new causes, and set-`a` cause 1 does
not occur in set `b`.

| # | Years | Variable(s) | Units (b21) | Cause | Wrong model |
|---|---|---|---|---|---|
| 2 | 2021 | `actc` | 802 | Part of the ODC counted as refundable CTC | PE |


Letter c (2021-2025)
--------------------

Set `c` adds child-care expenses, property taxes, other itemized
deductions, and mortgage interest to the set-`b` units.

```
===== c21 =====
c21: 873 differences (|tc - pe| > 1) in 1 variables
variable  compared  count  max_abs  mean_abs
    actc     10000    873   1600.0     639.0
===== c22 =====
c22: 0 differences (|tc - pe| > 1) in 0 variables
===== c23 =====
c23: 0 differences (|tc - pe| > 1) in 0 variables
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

There are no payroll tax or `fiitax` differences.  Every difference is
explained by one earlier cause and one new one (3):

| # | Years | Variable(s) | Units (c21/c22/c23/c24/c25) | Cause | Wrong model |
|---|---|---|---|---|---|
| 2 | 2021 | `actc` | 873 / - / - / - / - | Part of the ODC counted as refundable CTC | PE |
| 3 | all | `v18`, `v26` | 0 / 0 / 0 / 1 / 1 | Itemize-or-not tie broken differently when no tax is owed | neither |

### 3. Itemizing when it does not change tax (convention)

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

The choice has no effect on any tax amount, so neither is an error
and these are reporting differences only.


Errors found
------------

The comparison found no TC errors and two PE errors:

- **PE**: cause 1 (2021 MFS Schedule R initial amount: $5,000 instead
  of the $3,750 in IRC 22(c)(2)(A)(iii)), which makes PE's tax too low.
- **PE**: cause 2 (2021 refundable CTC includes part of the ODC,
  contrary to the 2021 Schedule 8812 lines 14a-14b and IRC 24(i)),
  which leaves tax unchanged in these samples but would overstate the
  refund of a unit with less tax liability.
- **Neither**: cause 3 (itemization tie-break when no tax is owed).
