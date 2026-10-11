# Tax-Calculator CalcFunctions

Documentation of the `taxcalc.calcfunctions` module.

## BenefitPrograms

```python
def BenefitPrograms(calc)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/calcfunctions.py#L23)

```text
Aggregate per-record government cost and consumption value of the
non-tax benefit programs tracked by Tax-Calculator and write them
to the Records arrays `benefit_cost_total` and `benefit_value_total`.

This function does not implement any IRS form; it is a model-internal
aggregator. For each program a `BEN_*_repeal` policy parameter, when
set, zeroes the program's per-record array before the sums are
formed (UBI has no repeal flag because UBI is itself a reform
construct that is zero under current law). In-kind programs are
weighted by a `BEN_*_value` consumption parameter; cash programs
(SSI, OASDI = e02400, UI = e02300, UBI) are valued at full dollar
cost. `benefit_value_total` is consumed downstream by ExpandIncome
via `expanded_income`.

Parameters
----------
calc: Calculator object
    calc represents the reform while self represents the baseline

Returns
-------
None:
    The function modifies calc
```

## EI_PayrollTax

```python
def EI_PayrollTax(SS_Earnings_c, e00200p, e00200s, pencon_p, pencon_s, FICA_ss_trt_employer, FICA_ss_trt_employee, FICA_mc_trt_employer, FICA_mc_trt_employee, ALD_SelfEmploymentTax_hc, SS_Earnings_thd, SECA_Earnings_deminimus, e00900p, e00900s, e02100p, e02100s, k1bx14p, k1bx14s, payrolltax, ptax_er_p, ptax_er_s, ptax_was, setax, c03260, ptax_oasdi, sey, earned, earned_p, earned_s)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/calcfunctions.py#L86)

```text
Compute part of total OASDI+HI payroll taxes and earned income variables.

Parameters
----------
SS_Earnings_c: float
    Maximum taxable earnings for Social Security.
    Individual earnings below this amount are subjected to
      OASDI payroll tax.
    This parameter is indexed by rate of growth in average wages not by
      the price inflation rate.
e00200p: float
    Wages, salaries,tips/otime for taxpayer net of pension contributions
e00200s: float
    Wages, salaries, tips/otime for spouse net of pension contributions
pencon_p: float
    Contributions to defined-contribution pension plans for taxpayer
pencon_s: float
    Contributions to defined-contribution pension plans for spouse
FICA_ss_trt_employer: float
    Employer side social security payroll tax rate
FICA_ss_trt_employee: float
    Employee side social security payroll tax rate
FICA_mc_trt_employer: float
    Employer side medicare payroll tax rate
FICA_mc_trt_employee: float
    Employee side medicare payroll tax rate
ALD_SelfEmploymentTax_hc: float
    Adjustment for self-employment tax haircut
    If greater than zero, reduces the employer equivalent portion
      of self-employment adjustment
    Final adjustment amount = (1-Haircut)*SelfEmploymentTaxAdjustment
SS_Earnings_thd: float
    Additional taxable earnings threshold for Social Security
    Individual wage-and-salary earnings above this threshold are subjected
    to OASDI payroll tax, in addition to earnings below the
    maximum taxable earnings threshold.
SECA_Earnings_deminimus: float
    Threshold value for an individual's net self-employment earnings
    (Sch SE line 4c) below which that individual has no SECA tax
    liability; applied to taxpayer and spouse separately
e00900p: float
    Schedule C business net profit/loss for taxpayer
e00900s: float
    Schedule C business net profit/loss for spouse
e02100p: float
    Farm net income/loss for taxpayer
e02100s: float
    Farm net income/loss for spouse
k1bx14p: float
    Partner self-employment earnings/loss for taxpayer
    (included in e26270 total)
k1bx14s: float
    Partner self-employment earnings/loss for spouse
    (included in e26270 total)
payrolltax: float
    Total (employee and employer) payroll tax liability
    payrolltax = ptax_was
ptax_er_p: float
    Taxpayer's employer share of payrolltax on wages and salaries
ptax_er_s: float
    Spouse's employer share of payrolltax on wages and salaries
ptax_was: float
    Employee and employer OASDI plus HI FICA tax
setax: float
    Self-employment tax (included in othertaxes and iitax)
c03260: float
    Deductible part of self-employment tax
    c03260 = (1 - ALD_SelfEmploymentTax_hc) * 0.5 * setax
ptax_oasdi: float
    Employee and employer OASDI FICA tax plus self employment tax
    Excludes HI FICA so positive ptax_oasdi is less than ptax_was + setax
sey: float
    Total self-employment income for filing unit
earned: float
    Earned income for filing unit
earned_p: float
    Earned income for taxpayer
earned_s: float
    Earned income for spouse

Returns
-------
sey: float
    Total self-employment income for filing unit
payrolltax: float
    Total (employee and employer) payroll tax liability
    payrolltax = ptax_was
ptax_er_p: float
    Taxpayer's employer share of payrolltax on wages and salaries
ptax_er_s: float
    Spouse's employer share of payrolltax on wages and salaries
ptax_was: float
    Employee and employer OASDI plus HI FICA tax
setax: float
    Self-employment tax (included in othertaxes and iitax)
c03260: float
    Deductible part of self-employment tax
    c03260 = (1 - ALD_SelfEmploymentTax_hc) * 0.5 * setax
ptax_oasdi: float
    Employee and employer OASDI FICA tax plus self employment tax
    Excludes HI FICA so positive ptax_oasdi is less than ptax_was + setax
earned: float
    Earned income for filing unit
earned_p: float
    Earned income for taxpayer
earned_s: float
    Earned income for spouse
```

## DependentCare

```python
def DependentCare(nu13, elderly_dependents, earned, MARS, ALD_Dependents_thd, ALD_Dependents_hc, ALD_Dependents_Child_c, ALD_Dependents_Elder_c, care_deduction)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/calcfunctions.py#L299)

```text
Computes the dependent-care above-the-line deduction.

Reform-only construct (originally specified for the 2016 Trump campaign
tax plan); no IRS form correspondence. Inert under current law because
all four ALD_Dependents_* parameters default to 0.0, which forces
care_deduction = 0. for every record.

The income test is a cliff, not a phaseout: filing units with earned
income above ALD_Dependents_thd[MARS-1] receive zero deduction.

care_deduction is summed into c02900 (Sch 1 line 26) by Adj under the
legacy/reform-only banner.

Parameters
----------
nu13: int
    Number of dependents under 13 years old
elderly_dependents: int
    Number of elderly dependents age 65+ in filing unit other than
    taxpayer and spouse
earned: float
    Earned income for filing unit
MARS: int
    Filing marital status (1=single, 2=joint, 3=separate,
                           4=household-head, 5=widow(er))
ALD_Dependents_thd: list
    Maximum income to qualify for dependent care deduction
ALD_Dependents_hc: float
    Deduction for childcare costs haircut
ALD_Dependents_Child_c: float
    National weighted average cost of childcare, ceiling for
    available childcare deduction
ALD_Dependents_Elder_c: float
    Eldercare deduction ceiling

Returns
-------
care_deduction: float
    Total above the line deductions for dependent care.
```

## Adj

```python
def Adj(e03220, e03290, c03260, e03300, e03270, e03400, e03500, e03150, e03210, e03230, e03240, care_deduction, ALD_EducatorExpenses_hc, ALD_HSADeduction_hc, ALD_KEOGH_SEP_hc, ALD_SelfEmp_HealthIns_hc, ALD_EarlyWithdraw_hc, ALD_AlimonyPaid_hc, ALD_IRAContributions_hc, ALD_StudentLoan_hc, ALD_Tuition_hc, ALD_DomesticProduction_hc, c02900)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/calcfunctions.py#L356)

```text
Adj calculates Form 1040 AGI adjustments (i.e., Above-the-Line Deductions).
Summands are ordered to match 2025 Schedule 1, Part II.

Parameters
-----
e03220: float
    Educator expenses (Sch 1 line 11)
e03290: float
    HSA deduction, Form 8889 (Sch 1 line 13)
c03260: float
    Deductible part of self-employment tax, after haircut (Sch 1 line 15)
e03300: float
    Total deductible KEOGH/SEP/SIMPLE/etc. plan contributions
    (Sch 1 line 16)
e03270: float
    Self-employed health insurance premiums (Sch 1 line 17)
e03400: float
    Penalty on early withdrawal of savings (Sch 1 line 18)
e03500: float
    Alimony paid (Sch 1 line 19a)
e03150: float
    Total deductible IRA plan contributions (Sch 1 line 20)
e03210: float
    Student loan interest paid (Sch 1 line 21)
e03230: float
    Tuition and fees, Form 8917
    (legacy; permanently repealed for tax years after 2020)
e03240: float
    Domestic production activity deduction, Form 8903
    (legacy; expired after 2017)
care_deduction: float
    Dependent care expense deduction (reform construct)
ALD_EducatorExpenses_hc: float
    Educator expenses haircut
ALD_HSADeduction_hc: float
    HSA deduction haircut
ALD_KEOGH_SEP_hc: float
    KEOGH/etc. plan contribution deduction haircut
ALD_SelfEmp_HealthIns_hc: float
    Self-employed h.i. deduction haircut
ALD_EarlyWithdraw_hc: float
    Penalty on early withdrawal deduction haircut
ALD_AlimonyPaid_hc: float
    Alimony paid deduction haircut
ALD_IRAContributions_hc: float
    IRA contribution haircut
ALD_StudentLoan_hc: float
    Student loan interest deduction haircut
ALD_Tuition_hc: float
    Tuition and fees haircut
ALD_DomesticProduction_hc: float
    Domestic production haircut

Returns
-------
c02900: float
    Total above-the-line income adjustments (Sch 1 line 26;
    flows to Form 1040 line 10)
```

## ALD_InvInc_ec_base

```python
def ALD_InvInc_ec_base(p22250, p23250, e00300, e00600, e01100, e01200, MARS, invinc_ec_base, Capital_loss_limitation)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/calcfunctions.py#L448)

```text
Computes invinc_ec_base, the base amount of investment income that
the reform parameter ALD_InvInc_ec_rt multiplies in AGIIncome to
produce invinc_agi_ec, the dollar amount of investment income
excluded from AGI. No IRS form correspondence (reform plumbing);
inert under current law because ALD_InvInc_ec_rt defaults to 0.

The base is the sum of five investment-income components: taxable
interest, ordinary dividends, net capital gain/(loss) after the
Sch D §1211(b) per-MARS loss cap, capital-gain distributions not
reported on Schedule D, and other gain/(loss) from Form 4797.

Note: this function runs before CapGainsLoss in calc_all (so c01000
is not yet available) and therefore re-derives the loss-capped
capital gain locally as `cgain`. By construction `cgain` equals the
`c01000` that CapGainsLoss will produce one call later.

Parameters
----------
p22250: float
    Net short-term capital gain/(loss) (Schedule D line 7)
p23250: float
    Net long-term capital gain/(loss) (Schedule D line 15)
e00300: float
    Taxable interest (Form 1040 line 2b)
e00600: float
    Ordinary dividends (Form 1040 line 3b)
e01100: float
    Capital gain distributions not reported on Schedule D
e01200: float
    Other gain/(loss) from Form 4797 (Schedule 1 line 4)
MARS: int
    Filing marital status (1=single, 2=joint, 3=separate,
                           4=household-head, 5=widow(er))
invinc_ec_base: float
    Base investment income subject to the reform exclusion
    (consumed by AGIIncome via ALD_InvInc_ec_rt)
Capital_loss_limitation: list
    MARS-indexed dollar limit on net capital loss deductible
    against ordinary income (Schedule D line 21 cap)

Returns
-------
invinc_ec_base: float
    Base investment income subject to the reform exclusion
```

## CapGainsLoss

```python
def CapGainsLoss(p22250, p23250, Capital_loss_limitation, MARS, c23650, c01000)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/calcfunctions.py#L508)

```text
Schedule D Part III netting of short-term and long-term capital
gains and losses, capped by the per-MARS net-capital-loss
deduction limit.

Parameters
----------
p22250: float
  Net short-term capital gain/(loss) (Schedule D line 7)
p23250: float
  Net long-term capital gain/(loss) (Schedule D line 15)
Capital_loss_limitation: list
  MARS-indexed dollar limit on net capital loss deductible
  against ordinary income (Schedule D line 21 cap)
MARS: int
  Filing marital status (1=single, 2=joint, 3=separate,
                         4=household-head, 5=widow(er))
c23650: float
  Net capital gain/(loss) before loss limitation
  (Schedule D line 16)
c01000: float
  Net capital gain/(loss) after loss limitation
  (Schedule D line 21 / Form 1040 line 7)

Returns
-------
c23650: float
  Net capital gain/(loss) before loss limitation
c01000: float
  Net capital gain/(loss) after loss limitation
```

## AGIIncome

```python
def AGIIncome(e00200, e00300, e00400, e00600, e00650, e00700, e00800, e00900, e01100, e01200, e01400, e01700, e02000, e02100, e02300, e02400, c01000, c02900, e03210, e03230, e03240, ALD_StudentLoan_hc, ALD_Tuition_hc, ALD_DomesticProduction_hc, ALD_InvInc_ec_rt, invinc_ec_base, CG_nodiff, CG_ec, CG_reinvest_ec_rt, ALD_BusinessLosses_c, AlimonyReceived_frac_in_AGI, MARS, ymod, ymod1, invinc_agi_ec)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/calcfunctions.py#L549)

```text
Builds ymod1 (Form 1040 income lines + Schedule 1 Part I, the
AGI building-block consumed by AGI()) and ymod (the modified-AGI
used by SSBenefits to determine the taxable portion of OASDI
benefits). Reform-only investment-income and QDCG exclusions
are applied here.

Parameters
----------
e00200: float
  Wages, salaries, tips (Form 1040 line 1)
e00300: float
  Taxable interest (Form 1040 line 2b)
e00400: float
  Tax-exempt interest (Form 1040 line 2a; not in AGI but used
  in the SS-benefits modAGI)
e00600: float
  Ordinary dividends (Form 1040 line 3b)
e00650: float
  Qualified dividends (Form 1040 line 3a; subset of e00600)
e00700: float
  Taxable refunds of state and local income taxes
  (Schedule 1 line 1)
e00800: float
  Alimony received, before TCJA inclusion gating (Schedule 1
  line 2a; included in ymod1 only to the extent of
  AlimonyReceived_frac_in_AGI)
e00900: float
  Schedule C business net profit/(loss) (Schedule 1 line 3)
e01100: float
  Capital gain distributions not reported on Schedule D
e01200: float
  Other gain/(loss) from Form 4797 (Schedule 1 line 4)
e01400: float
  Taxable IRA distributions (Form 1040 line 4b)
e01700: float
  Taxable pensions and annuities (Form 1040 line 5b)
e02000: float
  Schedule E rental, royalty, partnership, S-corp, etc.
  income/(loss); includes e26270 and e27200 (Schedule 1 line 5)
e02100: float
  Schedule F farm net income/(loss) (Schedule 1 line 6)
e02300: float
  Unemployment compensation (Schedule 1 line 7)
e02400: float
  Total social security (OASDI) benefits (Form 1040 line 6a)
c01000: float
  Net capital gain/(loss) after loss limitation
  (Form 1040 line 7); set by CapGainsLoss
c02900: float
  Total above-the-line adjustments (Schedule 1 line 26)
e03210: float
  Student loan interest deduction (pre-haircut)
e03230: float
  Tuition and fees deduction (legacy)
e03240: float
  Domestic production activities deduction (legacy)
ALD_StudentLoan_hc: float
  Reform haircut on the student loan interest deduction
ALD_Tuition_hc: float
  Haircut on the tuition-and-fees deduction (1.0 from 2021,
  after IRC §222 was repealed by the Taxpayer Certainty and
  Disaster Tax Relief Act of 2020 §104)
ALD_DomesticProduction_hc: float
  Haircut on the domestic-production-activities deduction
  (1.0 from 2018, after TCJA §13305(a) repealed IRC §199)
ALD_InvInc_ec_rt: float
  Reform exclusion rate for investment income
invinc_ec_base: float
  Base investment income subject to the reform exclusion
  (set by ALD_InvInc_ec_base)
CG_nodiff: bool
  Reform: long-term capital gains and qualified dividends taxed
  at ordinary rates (no preferential treatment)
CG_ec: float
  Reform: dollar amount of QDCG excluded from AGI when CG_nodiff
CG_reinvest_ec_rt: float
  Reform: fraction of QDCG above CG_ec excluded from AGI when
  CG_nodiff
ALD_BusinessLosses_c: list
  Reform: MARS-indexed cap on combined Sch C + Sch E losses
AlimonyReceived_frac_in_AGI: float
  Fraction of e00800 (alimony received) included in AGI.
  1.0 pre-TCJA (alimony was income to the recipient); 0.0 under
  TCJA (alimony received excluded from income for divorce or
  separation agreements executed after 2018-12-31)
MARS: int
  Filing marital status
ymod: float
  Modified-AGI used by SSBenefits to determine taxable portion
  of OASDI benefits
ymod1: float
  AGI build-up: Form 1040 income lines + Schedule 1 Part I,
  net of reform investment-income and QDCG exclusions
invinc_agi_ec: float
  Reform exclusion of investment income from AGI

Returns
-------
ymod: float
ymod1: float
invinc_agi_ec: float
```

## SSBenefits

```python
def SSBenefits(MARS, ymod, e02400, SS_all_in_agi, SS_thd1, SS_thd2, SS_percentage1, SS_percentage2, c02500)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/calcfunctions.py#L696)

```text
Calculates the taxable portion of OASDI benefits, c02500
(Form 1040 line 6b), per the Social Security Benefits Worksheet
in the Form 1040 instructions (also published as Pub. 915).

The three-branch form below is algebraically equivalent to the
worksheet's all-min/max formulation:
  * ymod < thd1                : worksheet line 9 <= 0
                                 -> c02500 = 0
  * thd1 <= ymod < thd2        : worksheet line 11 = 0
                                 -> c02500 = p1 * min(ymod - thd1,
                                                      e02400)
  * ymod >= thd2               : full worksheet
                                 -> c02500 = min(p2 * (ymod - thd2)
                                                 + p1 * min(e02400,
                                                            thd2 - thd1),
                                                 p2 * e02400)
where ymod is the worksheet line 7 amount built in AGIIncome.

MARS=3 (MFS) sub-case modeling gap: worksheet line 8 gives a base
of $0 for MFS filers who "lived with [their] spouse at any time
during the year" (instructions further direct such filers to skip
lines 8-15 and enter 0.85 * line 1 directly on line 16, i.e. 85%
of OASDI is taxable). `SS_thd1[2]`/`SS_thd2[2]` ($25,000/$34,000)
encode only the "MFS lived apart all year" case. Tax-Calculator
records do not carry a lived-apart-all-year flag (same data-gap
pattern as Schedule R row 26 in CODE_REVIEW_2025.md), so the code
unconditionally treats every MARS=3 filer as lived-apart and
under-taxes MFS-lived-with-spouse filers. Not fixable code-side.

The reform flag SS_all_in_agi (default False under current law)
overrides the worksheet and includes 100% of OASDI in AGI.

Downstream: c02500 is added to c00100 (AGI) by AGI().

Parameters
----------
MARS: int
    Filing marital status (1=single, 2=joint, 3=separate,
                           4=household-head, 5=widow(er))
ymod: float
    Worksheet line 7 (provisional income) built in AGIIncome
e02400: float
    Total OASDI benefits (worksheet line 1; SSA-1099 box 5 sum)
SS_all_in_agi: bool
    Reform: include 100% of OASDI in AGI (override worksheet)
SS_thd1: list
    MARS-indexed worksheet line 8 base amount
SS_thd2: list
    MARS-indexed (line 8 + line 10) second-tier threshold
SS_percentage1: float
    First-tier inclusion rate (worksheet line 13; 0.50 current law)
SS_percentage2: float
    Second-tier inclusion rate (worksheet lines 15/17; 0.85 current law)
c02500: float
    Taxable OASDI benefits (Form 1040 line 6b)

Returns
-------
c02500: float
    Taxable OASDI benefits (Form 1040 line 6b)
```

## UBI

```python
def UBI(nu18, n1820, n21, UBI_u18, UBI_1820, UBI_21, UBI_ecrt, ubi, taxable_ubi, nontaxable_ubi)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/calcfunctions.py#L784)

```text
Calculates total and taxable Universal Basic Income (UBI) amount.

Reform construct with no IRS-form correspondence. The per-person UBI
parameters (UBI_u18, UBI_1820, UBI_21) default to 0 in current law,
so this function is inert unless a reform activates UBI.

Outputs flow as follows:
  ubi            -> BenefitPrograms (benefit_cost_total and, via
                    BEN_*_value, benefit_value_total which feeds
                    expanded_income)
  taxable_ubi    -> AGI (added to c00100)
  nontaxable_ubi -> Records-bound output only; not consumed downstream

Parameters
----------
nu18: int
    Number of people in the tax unit under 18
n1820: int
    Number of people in the tax unit age 18-20
n21: int
    Number of people in the tax unit age 21+
UBI_u18: float
    UBI benefit for those under 18
UBI_1820: float
    UBI benefit for those between 18 to 20
UBI_21: float
    UBI benefit for those 21 or more
UBI_ecrt: float
    Fraction of UBI benefits excluded from AGI; the complementary
    fraction (1 - UBI_ecrt) is the taxable share added to AGI
ubi: float
    Total UBI received by the tax unit
taxable_ubi: float
    Amount of UBI that is taxable (is added to AGI)
nontaxable_ubi: float
    Amount of UBI that is excluded from AGI

Returns
-------
ubi: float
    Total UBI received by the tax unit
taxable_ubi: float
    Amount of UBI that is taxable (is added to AGI)
nontaxable_ubi: float
    Amount of UBI that is excluded from AGI
```

## AGI

```python
def AGI(ymod1, c02500, c02900, XTOT, MARS, DSI, exact, nu18, taxable_ubi, II_em, II_em_ps, II_em_po_step_size, II_em_prt, II_no_em_nu18, e02300, UI_thd, UI_em, c00100, pre_c04600, c04600)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/calcfunctions.py#L840)

```text
Computes Adjusted Gross Income (c00100, Form 1040 line 11) and
the reform-only personal exemption amount (pre_c04600 and c04600;
no current-law form correspondence — TCJA repealed exemptions).

Parameters
----------
-- AGI inputs (Form 1040 lines 9-11) --
ymod1: float
    Form 1040 lines 1z+2b+3b+4b+5b+7a+8 (total income excluding
    taxable Social Security benefits)
c02500: float
    Form 1040 line 6b: taxable Social Security (OASDI) benefits
c02900: float
    Form 1040 line 10: total above-the-line adjustments
    (Schedule 1, Part II, line 26)
taxable_ubi: float
    Reform-only: amount of UBI that is added to AGI
-- UI exclusion inputs (reform parameter; 2020 ARPA-style) --
MARS: int
    Filing marital status (1=single, 2=joint, 3=separate,
                           4=household-head, 5=widow(er))
e02300: float
    Unemployment compensation
UI_thd: list
    AGI threshold for unemployment compensation exclusion
UI_em: float
    Amount of unemployment compensation excluded from AGI
-- Personal exemption inputs (reform / pre-TCJA only) --
XTOT: int
    Total number of exemptions for filing unit
DSI: int
    1 if claimed as dependent on another return; otherwise 0
exact: int
    Whether or not to do rounding of phaseout fraction
nu18: int
    Number of people in the tax unit under 18
II_em: float
    Personal and dependent exemption amount
II_em_ps: list
    Personal exemption phaseout starting income
II_em_po_step_size: list
    Personal exemption phaseout step size
II_em_prt: float
    Personal exemption phaseout rate
II_no_em_nu18: float
    Repeal personal exemptions for dependents under age 18
-- Outputs (also accepted as inputs by iterate_jit) --
c00100: float
    Adjusted Gross Income (AGI), Form 1040 line 11
pre_c04600: float
    Personal exemption before phase-out (reform-only)
c04600: float
    Personal exemptions after phase-out (reform-only)

Returns
-------
c00100: float
    Adjusted Gross Income (AGI), Form 1040 line 11
pre_c04600: float
    Personal exemption before phase-out (reform-only)
c04600: float
    Personal exemptions after phase-out (reform-only)
```

## MiscDed

```python
def MiscDed(age_head, age_spouse, MARS, c00100, exact, SeniorDed_c, SeniorDed_ps, SeniorDed_prt, overtime_income, OvertimeIncomeDed_c, OvertimeIncomeDed_ps, OvertimeIncomeDed_po_step_size, OvertimeIncomeDed_po_rate_per_step, tip_income, TipIncomeDed_c, TipIncomeDed_ps, TipIncomeDed_po_step_size, TipIncomeDed_po_rate_per_step, auto_loan_interest, AutoLoanInterestDed_c, AutoLoanInterestDed_ps, AutoLoanInterestDed_po_step_size, AutoLoanInterestDed_po_rate_per_step, senior_deduction, overtime_income_deduction, tip_income_deduction, auto_loan_interest_deduction)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/calcfunctions.py#L950)

```text
Computes the four below-the-line additional deductions on
Schedule 1-A (new for 2025): qualified tips (Part II), qualified
overtime compensation (Part III), qualified passenger-vehicle
loan interest (Part IV), and the enhanced deduction for seniors
(Part V). The four amounts are summed into Schedule 1-A line 38
(Form 1040 line 13b) and consumed downstream by `StdDed`/`TaxInc`.

Each part caps the qualified input, then phases the cap out as
MAGI exceeds a MARS-indexed start. Tips, overtime, and auto-loan
use an `exact==1` stepped phaseout (floor or ceil of
`excess / step_size`, scaled by `rate_per_step`) and a smooth
linear fallback that gives sensible marginal-tax-rate behavior.
The senior phaseout is always smooth (form Part V line 34
multiplies by 6%, no step rounding).

MAGI: Schedule 1-A line 3 adds foreign-income exclusions (Puerto
Rico, Form 2555 lines 45/50, Form 4563 line 15) to AGI; those
inputs are not modeled in Tax-Calculator records, so `c00100`
(Form 1040 line 11 AGI) is used directly as the MAGI proxy.

MFS (`MARS=3`): Parts II/III/V state "If married, you must file
jointly to claim this deduction"; the function therefore zeroes
the tip, overtime, and senior deductions when `MARS=3`. Part IV
(auto loan) carries no MFS restriction and is allowed for MFS.

Senior deduction is per eligible head/spouse (born before
1961-01-02 ≈ age 65+); each gets the line-35 amount.

Eligibility conditions documented on the form but not modeled
here include: valid SSN for taxpayer (and spouse if MFJ);
qualified-occupation listing for tips; qualified-overtime
classification; and the per-vehicle VIN/QPVLI definition for
auto-loan interest. The `tip_income`, `overtime_income`, and
`auto_loan_interest` inputs are assumed to already represent
the form-qualified amounts.

Parameters
----------
age_head: int
    Age of tax unit head
age_spouse: int
    Age of tax unit spouse
MARS: int
    Filing marital status (1=single, 2=joint, 3=separate,
                           4=household-head, 5=widow(er))
c00100: float
    Adjusted gross income (Form 1040 line 11); used as the
    MAGI proxy for Schedule 1-A line 3
exact: int
    Whether or not to smooth deduction phase out
-- Part II (Tips, Sch 1-A lines 4-13) --
tip_income: float
    Qualified tips received (Sch 1-A line 6)
TipIncomeDed_c: float
    Cap on qualified tips deduction (Sch 1-A line 7)
TipIncomeDed_ps: list[float]
    Phase-out start MAGI (Sch 1-A line 9)
TipIncomeDed_po_step_size: float
    Phase-out MAGI step size (Sch 1-A line 11 denominator)
TipIncomeDed_po_rate_per_step: float
    Phase-out rate per MAGI step (Sch 1-A line 12 multiplier
    divided by line 11 step size)
-- Part III (Overtime, Sch 1-A lines 14-21) --
overtime_income: float
    Qualified overtime compensation (Sch 1-A line 14c)
OvertimeIncomeDed_c: list[float]
    Cap on overtime deduction (Sch 1-A line 15)
OvertimeIncomeDed_ps: list[float]
    Phase-out start MAGI (Sch 1-A line 17)
OvertimeIncomeDed_po_step_size: float
    Phase-out MAGI step size (Sch 1-A line 19 denominator)
OvertimeIncomeDed_po_rate_per_step: float
    Phase-out rate per MAGI step (Sch 1-A line 20)
-- Part IV (Auto loan interest, Sch 1-A lines 22-30) --
auto_loan_interest: float
    Qualified passenger-vehicle loan interest paid
    (Sch 1-A line 23)
AutoLoanInterestDed_c: float
    Cap on auto loan interest deduction (Sch 1-A line 24)
AutoLoanInterestDed_ps: list[float]
    Phase-out start MAGI (Sch 1-A line 26)
AutoLoanInterestDed_po_step_size: float
    Phase-out MAGI step size (Sch 1-A line 28 denominator)
AutoLoanInterestDed_po_rate_per_step: float
    Phase-out rate per MAGI step (Sch 1-A line 29)
-- Part V (Seniors, Sch 1-A lines 31-37) --
SeniorDed_c: float
    Maximum amount of senior deduction per elderly head/spouse
    (Sch 1-A line 35 base, $6,000 for 2025)
SeniorDed_ps: list[float]
    Phase-out start MAGI (Sch 1-A line 32)
SeniorDed_prt: float
    Phase-out rate (Sch 1-A line 34, 6% for 2025)

Returns
-------
senior_deduction: float
    Sch 1-A line 37 (enhanced deduction for seniors)
overtime_income_deduction: float
    Sch 1-A line 21 (qualified overtime compensation deduction)
tip_income_deduction: float
    Sch 1-A line 13 (qualified tips deduction)
auto_loan_interest_deduction: float
    Sch 1-A line 30 (qualified passenger vehicle loan interest
    deduction)
```

## ItemDed

```python
def ItemDed(e17500, e18400, e18500, e19200, e19800, e20100, e20400, g20500, MARS, age_head, age_spouse, c00100, c04600, c04470, c21040, c21060, c17000, c18300, c19200, c19700, c20500, c20800, II_brk6, ID_ps, ID_Medical_frt, ID_Medical_frt_add4aged, ID_Medical_hc, ID_Casualty_frt, ID_Casualty_hc, ID_Miscellaneous_frt, ID_Miscellaneous_hc, ID_Charity_crt_all, ID_Charity_crt_noncash, ID_prt, ID_crt, ID_c, ID_StateLocalTax_hc, ID_Charity_frt, ID_Charity_hc, ID_InterestPaid_hc, ID_RealEstate_hc, ID_Medical_c, ID_StateLocalTax_c, ID_RealEstate_c, ID_InterestPaid_c, ID_Charity_c, ID_Casualty_c, ID_Miscellaneous_c, ID_AllTaxes_c, ID_AllTaxes_hc, ID_AllTaxes_c_ps, ID_AllTaxes_c_po_rate, ID_AllTaxes_c_po_floor, ID_StateLocalTax_crt, ID_RealEstate_crt, ID_Charity_f, ID_reduction_rate)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/calcfunctions.py#L1169)

```text
Calculates itemized deductions, Schedule A (Form 1040).

Body sections mirror Schedule A's six-section structure:
  Medical (lines 1-4) → Taxes (5-7) → Interest (8-10) →
  Charity (11-14) → Casualty (15) → Other (16) → Total (17).

Schedule A inputs and form-arithmetic come first within each
section; reform/legacy plumbing (per-section haircuts ``_hc``,
per-section MARS-indexed dollar caps ``_c``, and AGI-fraction
caps/floors absent from the form) is interleaved.

Three post-Sch-A reform/legacy operations apply to the line-17
total ``c21060``: (1) the §68 Pease limitation (repealed by TCJA
for 2018-2025; parameters retained for reform use); (2) the OBBBA
top-bracket reduction (``ID_reduction_rate``, mutually exclusive
with Pease via assert); (3) a reform hard cap ``ID_c`` on total
itemized deductions. No attempt is made to adjust the per-section
components for these post-total limitations; only ``c04470``
reflects them.

Unmodeled Schedule A items: line 5c (state and local personal
property taxes), line 6 (other taxes), line 13 (charity carryover
from prior year). Mortgage interest (line 8) and investment
interest (line 9) are pre-aggregated in input variable ``e19200``.
The OBBBA SALT-cap phaseout (line 5e text: "If Form 1040 line 11b
is more than $500,000 ($250,000 MFS), see instructions") is
implemented via ``ID_AllTaxes_c`` + ``ID_AllTaxes_c_ps`` +
``ID_AllTaxes_c_po_rate`` + ``ID_AllTaxes_c_po_floor``.

Parameters
----------
-- Filer attributes --
MARS: int
    Filing marital status (1=single, 2=joint, 3=separate,
                           4=household-head, 5=widow(er))
age_head: int
    Age in years of taxpayer
age_spouse: int
    Age in years of spouse
c00100: float
    Adjusted gross income (Form 1040 line 11)
c04600: float
    Personal exemptions after phase out (used by OBBBA reduction
    block to derive a taxable-income proxy)
II_brk6: list
    Bottom of top income tax rate bracket (used by OBBBA reduction)
-- Sch A Medical and Dental Expenses (lines 1-4) --
e17500: float
    Medical and dental expenses paid (Sch A line 1)
ID_Medical_frt: float
    AGI floor rate for medical-expense deduction (Sch A line 3,
    7.5% under current law)
ID_Medical_frt_add4aged: float
    Add-on AGI floor rate for filers age 65+ (zero post-TCJA)
ID_Medical_hc: float
    Reform haircut on medical-expense deduction
ID_Medical_c: list
    Reform per-MARS dollar cap on medical-expense deduction
-- Sch A Taxes You Paid (lines 5-7) --
e18400: float
    State and local income or sales taxes (Sch A line 5a)
e18500: float
    State and local real estate taxes (Sch A line 5b)
ID_StateLocalTax_hc: float
    Reform haircut on Sch A line 5a
ID_RealEstate_hc: float
    Reform haircut on Sch A line 5b
ID_StateLocalTax_c: list
    Reform per-MARS dollar cap on Sch A line 5a
ID_RealEstate_c: list
    Reform per-MARS dollar cap on Sch A line 5b
ID_StateLocalTax_crt: float
    Reform AGI-fraction cap on Sch A line 5a
ID_RealEstate_crt: float
    Reform AGI-fraction cap on Sch A line 5b
ID_AllTaxes_hc: float
    Reform haircut on combined Sch A line 5d (state+local+RE)
ID_AllTaxes_c: list
    SALT cap base amount on Sch A line 5e ($40k / $20k MFS for 2025)
ID_AllTaxes_c_ps: list
    AGI level above which the line 5e SALT cap phases out
    ($500k / $250k MFS for 2025 per OBBBA)
ID_AllTaxes_c_po_rate: float
    Phaseout rate per dollar of AGI above ID_AllTaxes_c_ps
ID_AllTaxes_c_po_floor: list
    Floor below which the SALT cap cannot be reduced by the phaseout
-- Sch A Interest You Paid (lines 8-10) --
e19200: float
    Total deductible interest (mortgage line 8e + investment line 9,
    pre-aggregated in input data)
ID_InterestPaid_hc: float
    Reform haircut on interest deduction
ID_InterestPaid_c: list
    Reform per-MARS dollar cap on interest deduction
-- Sch A Gifts to Charity (lines 11-14) --
e19800: float
    Cash charitable contributions (Sch A line 11)
e20100: float
    Non-cash charitable contributions (Sch A line 12)
ID_Charity_frt: float
    AGI-fraction floor on total charitable contributions (OBBBA
    introduces 0.5% for tax years 2026+; not on form face)
ID_Charity_f: list
    Per-MARS dollar floor on charitable contributions
ID_Charity_crt_all: float
    AGI-fraction ceiling on total charitable contributions
    (~50% / 60% per IRC §170(b))
ID_Charity_crt_noncash: float
    AGI-fraction ceiling on noncash charitable contributions
ID_Charity_hc: float
    Reform haircut on charitable deduction
ID_Charity_c: list
    Reform per-MARS dollar cap on charitable deduction
-- Sch A Casualty and Theft Losses (line 15) --
g20500: float
    Casualty / theft loss after Form 4684 10% AGI floor
ID_Casualty_frt: float
    Reform additional AGI-fraction floor
ID_Casualty_hc: float
    Reform haircut on casualty deduction
ID_Casualty_c: list
    Reform per-MARS dollar cap on casualty deduction
-- Sch A Other Itemized Deductions (line 16, "miscellaneous") --
e20400: float
    Gross miscellaneous deductions
ID_Miscellaneous_frt: float
    AGI-fraction floor (pre-TCJA 2% rule retained for reform use)
ID_Miscellaneous_hc: float
    Reform haircut (1.0 under current law — TCJA repealed line-16
    miscellaneous deductions for 2018-2025)
ID_Miscellaneous_c: list
    Reform per-MARS dollar cap on miscellaneous deduction
-- Post-form reform/legacy on Sch A line 17 total --
ID_ps: list
    Pease phaseout AGI start (per MARS)
ID_prt: float
    Pease phaseout rate
ID_crt: float
    Pease maximum-phaseout fraction of total itemizable amount
ID_reduction_rate: float
    OBBBA top-bracket reduction rate on itemized deductions
ID_c: list
    Reform hard cap on total itemized deductions (per MARS)
-- iterate_jit Records-bound outputs (also appear as inputs) --
c17000: float
    Sch A line 4 (medical expenses deducted)
c18300: float
    Sch A line 7 (state and local taxes deducted)
c19200: float
    Sch A line 10 (interest deducted)
c19700: float
    Sch A line 14 (charity deducted)
c20500: float
    Sch A line 15 (casualty / theft loss deducted)
c20800: float
    Sch A line 16 (other / miscellaneous deducted)
c21040: float
    Pease phaseout amount applied to itemized deductions
c21060: float
    Sch A line 17 (gross total before Pease / OBBBA / reform cap)
c04470: float
    Final itemized deductions after Pease / OBBBA / reform cap
    (zero for non-itemizers)

Returns
-------
c17000, c18300, c19200, c19700, c20500, c20800, c21040, c21060, c04470
(see Records-bound section above for line correspondences)
```

## AdditionalMedicareTax

```python
def AdditionalMedicareTax(MARS, e00200, pencon_p, pencon_s, e00900p, e00900s, e02100p, e02100s, k1bx14p, k1bx14s, FICA_ss_trt_employer, FICA_ss_trt_employee, FICA_mc_trt_employer, FICA_mc_trt_employee, SECA_Earnings_deminimus, AMEDT_ec, AMEDT_rt, ptax_amc)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/calcfunctions.py#L1481)

```text
Form 8959 Additional Medicare Tax. Liability flows into Schedule 2
line 11 via `othertaxes` in `C1040` and ultimately into `iitax`.

Form 8959 has five Parts:
  Part I  (lines 1-7)  Additional Medicare Tax on Medicare wages
  Part II (lines 8-13) Additional Medicare Tax on SE income
  Part III(lines 14-17)Additional Medicare Tax on RRTA compensation
                       — *not modeled* (no RRTA variables in records)
  Part IV (line 18)    Total = line 7 + line 13 (+ line 17)
  Part V  (lines 19-24)Withholding reconciliation — refundable side,
                       not part of liability.

Medicare wages (W-2 box 5) include elective deferrals to
defined-contribution pension plans, which W-2 box 1 wages exclude,
so Form 8959 line 1 is `e00200` plus `pencon_p` and `pencon_s`
(the same gross wages on which `EI_PayrollTax` levies HI FICA tax).
Tax-Calculator does not separately track Form 4137 unreported tips
and Form 8919 wages, so line 1 also serves as Form 8959 line 4 (the
sum of lines 1+2+3).

Form 8959 line 8 (Sch SE Part I line 6) is reconstructed per-spouse:
Sch SE is filed separately by each spouse, so each spouse's net SE
earnings are floored at zero independently before the joint total is
formed, and a spouse whose net SE earnings are less than the
`SECA_Earnings_deminimus` ($400) floor has no SE income. The records-bound
`sey` is the unfloored sum, which would over-net a positive-sey
spouse against a negative-sey spouse; this function therefore
re-derives `sey_p`/`sey_s` from the underlying per-spouse input
components and applies the per-spouse floors before summing
(matching `EI_PayrollTax`).

The line-5 / line-9 / line-15 thresholds are identical on the form
($250k MFJ / $125k MFS / $200k Single/HoH/QSS for 2025) and are
parameterized by `AMEDT_ec[MARS-1]`. The 0.9% rate is parameterized
by `AMEDT_rt`.

Parameters
----------
MARS: int
    Filing status (1=single, 2=joint, 3=separate,
                   4=household-head, 5=widow(er))
-- Part I: Medicare wages (lines 1-7) --
e00200: float
    Wages and salaries net of pension contributions (W-2 box 1);
    component of Form 8959 line 1 (Medicare wages, W-2 box 5)
pencon_p: float
    Contributions to defined-contribution pension plans for
    taxpayer; component of Form 8959 line 1
pencon_s: float
    Contributions to defined-contribution pension plans for
    spouse; component of Form 8959 line 1
-- Part II: Self-employment income (lines 8-13) --
e00900p: float
    Sch C (taxpayer) net profit/loss; component of `sey_p`
e00900s: float
    Sch C (spouse) net profit/loss; component of `sey_s`
e02100p: float
    Sch F (taxpayer) net profit/loss; component of `sey_p`
e02100s: float
    Sch F (spouse) net profit/loss; component of `sey_s`
k1bx14p: float
    Sch K-1 box 14 SE earnings (taxpayer); component of `sey_p`
k1bx14s: float
    Sch K-1 box 14 SE earnings (spouse); component of `sey_s`
FICA_ss_trt_employer: float
    Employer-side FICA OASDI tax rate (Sch SE line 4c reduction)
FICA_ss_trt_employee: float
    Employee-side FICA OASDI tax rate (Sch SE line 4c reduction)
FICA_mc_trt_employer: float
    Employer-side FICA HI tax rate (Sch SE line 4c reduction)
FICA_mc_trt_employee: float
    Employee-side FICA HI tax rate (Sch SE line 4c reduction)
SECA_Earnings_deminimus: float
    Per-spouse Sch SE line 4c floor below which that spouse has no
    SE income (Sch SE line 4c: "If less than $400, stop")
-- Common to Parts I and II --
AMEDT_ec: list
    Form 8959 line 5 / line 9 threshold by MARS
AMEDT_rt: float
    Form 8959 line 7 / line 13 rate (0.9% under current law)
-- iterate_jit Records-bound output --
ptax_amc: float
    Additional Medicare Tax (Form 8959 line 18)

Returns
-------
ptax_amc: float
    Additional Medicare Tax (Form 8959 line 18)
```

## StdDed

```python
def StdDed(DSI, earned, STD, age_head, age_spouse, STD_Aged, STD_Dep, STD_Dep_earned_add, MARS, MIDR, blind_head, blind_spouse, standard, e19800, STD_charity_ded_nonitemizers_max)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/calcfunctions.py#L1606)

```text
Computes standard deduction (Form 1040 line 12).

Mirrors the "Standard Deduction for—" chart on Form 1040 line 12 and
the "Standard Deduction Worksheet for Dependents" in the 2025 Form
1040 instructions. The body is split into four sections:

1. MFS-and-spouse-itemizes override (line-12 chart bullet 3): if the
   filer files married-separately and the spouse itemizes, the
   standard deduction is zero (filer must itemize).
2. Basic standard deduction: either the dependent-worksheet amount
   (if claimed as a dependent) or the line-12 chart's STD[MARS-1].
   The dependent worksheet caps the deduction at STD[MARS-1] but
   floors it at max(earned + STD_Dep_earned_add, STD_Dep).
3. Aged/blind add-on: STD_Aged[MARS-1] per checked box (filer 65+,
   filer blind, spouse 65+, spouse blind). Spouse boxes only count
   for MFJ filers.
4. Cash-charity-deduction add-on for nonitemizers active under
   CARES (2020-21) and OBBBA (2026-).

The Records-bound output is `standard` (Form 1040 line 12);
downstream `TaxInc` consumes it into Form 1040 line 14.

Parameters
-----
DSI: int
    1 if claimed as dependent on another return; otherwise 0
    (selects the dependent worksheet branch)
earned: float
    Earned income for filing unit (dependent worksheet line 1)
STD: list
    Per-MARS basic standard deduction (Form 1040 line-12 chart;
    dependent worksheet line 6 / line-12 chart cap)
age_head: int
    Age in years of taxpayer (≥65 → check filer aged box)
age_spouse: int
    Age in years of spouse (≥65 → check spouse aged box; MFJ only)
STD_Aged: list
    Per-MARS additional standard deduction per checked box
    (per-box amount on the line-12 chart for aged/blind)
STD_Dep: float
    Minimum dependent standard deduction (worksheet line 4)
STD_Dep_earned_add: float
    Earned-income additional amount in the dependent worksheet
    (worksheet line 2)
MARS: int
    Filing (marital) status. (1=single, 2=joint, 3=separate,
                              4=household-head, 5=widow(er))
MIDR: int
    1 if separately filing spouse itemizes, 0 otherwise
    (only meaningful when MARS=3)
blind_head: int
    1 if taxpayer is blind, 0 otherwise (filer blind box)
blind_spouse: int
    1 if spouse is blind, 0 otherwise (spouse blind box; MFJ only)
standard: float
    Records-bound output: standard deduction (zero for itemizers)
e19800: float
    Schedule A line 11 cash charitable contributions
STD_charity_ded_nonitemizers_max: list
    Per-MARS ceiling amount (in dollars) on the nonitemizer
    cash charitable contributions deduction

Returns
-------
standard: float
    Standard deduction (zero for itemizers)
```

## TaxInc

```python
def TaxInc(c00100, standard, c04470, c04600, MARS, e00900, c03260, e03270, e03300, e26270, e02100, e27200, e00650, p22250, p23250, senior_deduction, overtime_income_deduction, tip_income_deduction, auto_loan_interest_deduction, PT_SSTB_income, PT_binc_w2_wages, PT_ubia_property, PT_qbid_rt, PT_qbid_limited, PT_qbid_taxinc_thd, PT_qbid_taxinc_gap, PT_qbid_w2_wages_rt, PT_qbid_alt_w2_wages_rt, PT_qbid_alt_property_rt, PT_qbid_ps, PT_qbid_prt, PT_qbid_min_ded, PT_qbid_min_qbi, c04800, qbided)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/calcfunctions.py#L1720)

```text
Form 1040 lines 13-15 (2025): the §199A pass-through Qualified
Business Income deduction (line 13, from Form 8995 or Form 8995-A)
and regular taxable income (line 15 = AGI - line 14).

QBI deduction structure (TCJA §199A):
  - Filers with pre-QBID taxable income at or below
    PT_qbid_taxinc_thd[MARS-1] ($197,300 / $394,600 MFJ for 2025)
    file the simplified Form 8995: deduction = PT_qbid_rt * QBI,
    capped only by the income limitation.
  - Filers above the threshold file Form 8995-A. In the phase-in
    window of width PT_qbid_taxinc_gap[MARS-1] ($50,000 /
    $100,000 MFJ) above the threshold:
      * Specified Service Trade or Business (SSTB) filers have QBI
        and W-2 wages / UBIA scaled by Schedule A's "applicable
        percentage" = (upper_thd - taxinc) / gap, with full
        disallowance once taxinc >= upper_thd.
      * Non-SSTB filers face the W-2/UBIA cap with a Part III
        phase-in reduction; above the window the cap binds in full.
  - All filers face the Part IV income limitation: deduction may
    not exceed PT_qbid_rt * (pre-QBID taxinc - net_cg), where
    net_cg = qualified dividends + net long-term capital gain.

QBI components (Form 8995 line 1c instructions): Sch C net profit
`e00900`, Sch E partnership/S-corp `e26270`, Sch F `e02100`, Sch E
farm rent `e27200`. Wages (`e00200`) and investment income are NOT
QBI. QBI is reduced by the trade-or-business above-the-line items:
deductible part of SECA tax `c03260` (Sch 1 line 15), self-employed
retirement contributions `e03300` (Sch 1 line 16), and self-employed
health insurance `e03270` (Sch 1 line 17). REIT dividends and PTP
income (Form 8995 lines 6-9 / Form 8995-A Part IV lines 28-31) are
not modeled.

Pre-QBID taxable income (Form 8995 line 11 / Form 8995-A line 33)
subtracts from AGI: max(itemized, standard) + personal exemption
(reform-only `c04600`) + Sch 1-A senior/overtime/tip/auto-loan
deductions. The QBID is "stacked last" so that c04800 = max(0,
pre_qbid_taxinc - qbided).

Reform-only constructs (no IRS form analogue):
  - PT_qbid_limited=False disables the W-2/UBIA cap, SSTB exclusion,
    and phase-in entirely (deduction = PT_qbid_rt * QBI subject only
    to the income cap).
  - PT_qbid_ps / PT_qbid_prt: linear phase-out of the deduction
    above PT_qbid_ps[MARS-1].
  - PT_qbid_min_qbi / PT_qbid_min_ded: minimum-deduction floor for
    filers with QBI at or above PT_qbid_min_qbi.

Downstream consumer: `c04800` is the input to `SchXYZ` /
`SchXYZTax` / `GainsTax` (regular tax) and to `AMT` (Form 6251).

Parameters
----------
c00100: float
    Adjusted Gross Income (Form 1040 line 11)
standard: float
    Standard deduction (Form 1040 line 12; zero for itemizers)
c04470: float
    Itemized deductions after phase-out (Form 1040 line 12; zero
    for non-itemizers)
c04600: float
    Personal exemptions after phase-out (reform-only; zero under
    current law for 2018-2025 per TCJA suspension)
MARS: int
    Filing (marital) status. (1=single, 2=joint, 3=separate,
                              4=household-head, 5=widow(er))
e00900: float
    Schedule C business net profit/loss (QBI component)
c03260: float
    Self-employment (SECA) tax above-the-line deduction (Sch 1
    line 15); subtracted from QBI per §199A
e03270: float
    Self-employed health insurance deduction (Sch 1 line 17);
    subtracted from QBI per Form 8995 line 1 instructions
e03300: float
    Self-employed retirement contributions to SEP/SIMPLE/qualified
    plans (Sch 1 line 16); subtracted from QBI per Form 8995 line 1
    instructions
e26270: float
    Schedule E partnership / S-corporation net income/loss (QBI
    component)
e02100: float
    Schedule F farm net income/loss (QBI component)
e27200: float
    Schedule E farm rent net income/loss (QBI component)
e00650: float
    Qualified dividends (Form 8995 line 12 / 8995-A line 34 input)
p22250: float
    Sch D Part I line 7 (net short-term capital gain/loss); used
    to compute §1(h) net capital gain for Form 8995 line 12 /
    8995-A line 34
p23250: float
    Sch D Part II line 15 (net long-term capital gain/loss); used
    to compute §1(h) net capital gain for Form 8995 line 12 /
    8995-A line 34
senior_deduction: float
    Sch 1-A Part V senior deduction (reduces pre-QBID taxinc)
overtime_income_deduction: float
    Sch 1-A Part III overtime deduction (reduces pre-QBID taxinc)
tip_income_deduction: float
    Sch 1-A Part II tip deduction (reduces pre-QBID taxinc)
auto_loan_interest_deduction: float
    Sch 1-A Part IV auto-loan-interest deduction (reduces pre-QBID
    taxinc)
PT_SSTB_income: int
    1 = QBI is from a Specified Service Trade or Business; 0 = QBI
    is from a qualified (non-SSTB) trade or business
PT_binc_w2_wages: float
    Filing unit's allocable share of W-2 wages paid by the
    pass-through business (Form 8995-A line 4)
PT_ubia_property: float
    Filing unit's allocable share of unadjusted basis immediately
    after acquisition of qualified property (Form 8995-A line 7)
PT_qbid_rt: float
    QBID rate (Form 8995 line 5 / 8995-A line 3 multiplier; 20% in
    2025)
PT_qbid_limited: bool
    Reform switch; False disables the W-2/UBIA cap, SSTB exclusion,
    and Part III phase-in
PT_qbid_taxinc_thd: list
    MARS-indexed lower threshold of pre-QBID taxable income (Form
    8995-A line 21; $197,300 / $394,600 MFJ for 2025)
PT_qbid_taxinc_gap: list
    MARS-indexed phase-in window width (Form 8995-A line 23;
    $50,000 / $100,000 MFJ for 2025)
PT_qbid_w2_wages_rt: float
    Primary W-2-wages cap rate (Form 8995-A line 5; 50%)
PT_qbid_alt_w2_wages_rt: float
    Alternative W-2-wages cap rate (Form 8995-A line 6; 25%)
PT_qbid_alt_property_rt: float
    Alternative UBIA cap rate (Form 8995-A line 8; 2.5%)
PT_qbid_ps: list
    Reform-only QBID phase-out start (no form analogue)
PT_qbid_prt: float
    Reform-only QBID phase-out rate (no form analogue)
PT_qbid_min_ded: float
    Reform-only minimum QBID amount (no form analogue)
PT_qbid_min_qbi: float
    Reform-only minimum QBI to qualify for PT_qbid_min_ded floor
c04800: float
    Regular taxable income (Form 1040 line 15; iterate_jit
    Records-bound output)
qbided: float
    Qualified Business Income deduction (Form 1040 line 13;
    iterate_jit Records-bound output)

Returns
-------
c04800: float
    Regular taxable income (Form 1040 line 15)
qbided: float
    Qualified Business Income deduction (Form 1040 line 13)
```

## SchXYZ

```python
def SchXYZ(taxable_income, MARS, II_rt1, II_rt2, II_rt3, II_rt4, II_rt5, II_rt6, II_rt7, II_rt8, II_brk1, II_brk2, II_brk3, II_brk4, II_brk5, II_brk6, II_brk7)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/calcfunctions.py#L2012)

```text
Function that returns tax amount given the progressive tax rate
schedule specified by the II_rt? and (upper) II_brk? parameters and
given taxable income and filing status (MARS).

Parameters
----------
taxable_income: float
    Regular taxable income
MARS: int
    Filing (marital) status. (1=single, 2=joint, 3=separate,
                              4=household-head, 5=widow(er))
II_rt1: float
    Personal income (regular/non-AMT) tax rate 1
II_rt2: float
    Personal income (regular/non-AMT) tax rate 2
II_rt3: float
    Personal income (regular/non-AMT) tax rate 3
II_rt4: float
    Personal income (regular/non-AMT) tax rate 4
II_rt5: float
    Personal income (regular/non-AMT) tax rate 5
II_rt6: float
    Personal income (regular/non-AMT) tax rate 6
II_rt7: float
    Personal income (regular/non-AMT) tax rate 7
II_rt8: float
    Personal income (regular/non-AMT) tax rate 8
II_brk1: list
    Personal income (regular/non-AMT) tax bracket (upper threshold) 1
II_brk2: list
    Personal income (regular/non-AMT) tax bracket (upper threshold) 2
II_brk3: list
    Personal income (regular/non-AMT) tax bracket (upper threshold) 3
II_brk4: list
    Personal income (regular/non-AMT) tax bracket (upper threshold) 4
II_brk5: list
    Personal income (regular/non-AMT) tax bracket (upper threshold) 5
II_brk6: list
    Personal income (regular/non-AMT) tax bracket (upper threshold) 6
II_brk7: list
    Personal income (regular/non-AMT) tax bracket (upper threshold) 7

Returns
-------
Regular individual income tax liability on all taxable income
```

## SchXYZTax

```python
def SchXYZTax(c04800, MARS, II_rt1, II_rt2, II_rt3, II_rt4, II_rt5, II_rt6, II_rt7, II_rt8, II_brk1, II_brk2, II_brk3, II_brk4, II_brk5, II_brk6, II_brk7, c05200)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/calcfunctions.py#L2101)

```text
Function that routes c04800 (regular taxable income) through the
SchXYZ rate-schedule function and stores the result in c05200 (tax
amount from Tax Rate Schedules X, Y-1, Y-2, Z). See the SchXYZ function
for the semantics of MARS, II_rt?, and II_brk?.
```

## GainsTax

```python
def GainsTax(e00650, c01000, c23650, p23250, e01100, e58990, e24515, e24518, MARS, c04800, c05200, II_rt1, II_rt2, II_rt3, II_rt4, II_rt5, II_rt6, II_rt7, II_rt8, II_brk1, II_brk2, II_brk3, II_brk4, II_brk5, II_brk6, II_brk7, CG_nodiff, CG_rt1, CG_rt2, CG_rt3, CG_rt4, CG_brk1, CG_brk2, CG_brk3, dwks10, dwks13, dwks14, dwks18, dwks43, c05700, taxbc)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/calcfunctions.py#L2121)

```text
Computes the regular-tax preference for long-term capital gains and
qualified dividends.  Implements both IRS worksheets in a single body:

  * Qualified Dividends and Capital Gain Tax Worksheet (QDCGTW)
    from the 2025 Form 1040 instructions; and
  * Schedule D Tax Worksheet (Sch D TW) from the 2025 Schedule D
    instructions, which is QDCGTW plus extra rate buckets for
    un-recaptured section 1250 gain (25%) and collectibles 28%-rate
    gain (lines 11-12 and 33-41).

Sch D TW reduces algebraically to QDCGTW when both e24515 and e24518
are zero, so the code runs the Sch D TW computation unconditionally
and lets the Sch D-only blocks vanish when not applicable.  Section
banners below mark which IRS-worksheet lines are common to both
worksheets and which belong to Sch D TW only.

If CG_nodiff is true, qualified dividends and long-term capital gains
are taxed at ordinary rates and the worksheet is skipped.

Parameters
----------
e00650: float
    Qualified dividends included in ordinary dividends
c01000: float
    Limitation on capital losses
c23650: float
    Net capital gain (long term + short term) before exclusion
p23250: float
    Schedule D: net long-term capital gains/losses
e01100: float
    Capital gains distributions not reported on Schedule D
e58990: float
    Investment income elected amount from Form 4952
e24515: float
    Schedule D: un-recaptured section 1250 Gain
e24518: float
    Schedule D: 28% rate gain or loss
MARS: int
    Filing (marital) status. (1=single, 2=joint, 3=separate,
                              4=household-head, 5=widow(er))
c04800: float
    Regular taxable income
c05200: float
    Tax amount from Schedule X,Y,Z tables
II_rt1: float
    Personal income (regular/non-AMT) tax rate 1
II_rt2: float
    Personal income (regular/non-AMT) tax rate 2
II_rt3: float
    Personal income (regular/non-AMT) tax rate 3
II_rt4: float
    Personal income (regular/non-AMT) tax rate 4
II_rt5: float
    Personal income (regular/non-AMT) tax rate 5
II_rt6: float
    Personal income (regular/non-AMT) tax rate 6
II_rt7: float
    Personal income (regular/non-AMT) tax rate 7
II_rt8: float
    Personal income (regular/non-AMT) tax rate 8
II_brk1: list
    Personal income (regular/non-AMT)
    tax bracket (upper threshold) 1
II_brk2: list
    Personal income (regular/non-AMT)
    tax bracket (upper threshold) 2
II_brk3: list
    Personal income (regular/non-AMT)
    tax bracket (upper threshold) 3
II_brk4: list
    Personal income (regular/non-AMT)
    tax bracket (upper threshold) 4
II_brk5: list
    Personal income (regular/non-AMT)
    tax bracket (upper threshold) 5
II_brk6: list
    Personal income (regular/non-AMT)
    tax bracket (upper threshold) 6
II_brk7: list
    Personal income (regular/non-AMT)
    tax bracket (upper threshold) 7
CG_nodiff: bool
    Long term capital gains and qualified dividends taxed no differently
    than regular taxable income
CG_rt1: float
    Long term capital gain and qualified dividends (regular/non-AMT) rate 1
CG_rt2: float
    Long term capital gain and qualified dividends (regular/non-AMT) rate 2
CG_rt3: float
    Long term capital gain and qualified dividends (regular/non-AMT) rate 3
CG_rt4: float
    Long term capital gain and qualified dividends (regular/non-AMT) rate 4
CG_brk1: list
    Top of long-term capital gains and qualified dividends
    (regular/non-AMT) tax bracket 1
CG_brk2: list
    Top of long-term capital gains and qualified dividends
    (regular/non-AMT) tax bracket 2
CG_brk3: list
    Top of long-term capital gains and qualified dividends
    (regular/non-AMT) tax bracket 3 (reform-only taxable-income
    threshold with gains stacked on top of ordinary income; default
    9e+99 makes the fourth bracket inert under current law)
dwks10: float
    Sum of dwks6 + dwks9
dwks13: float
    Difference of dwks10 - dwks12
dwks14: float
    Maximum of 0 and dwks1 - dwks13
dwks18: float
    Maximum of dwks16 and dwks17
dwks43: float
    separate tax on long-term capital gains and qualified dividends
c05700: float
    Lump sum distributions
taxbc: float
    Regular tax on regular taxable income before credits

Returns
-------
dwks10: float
    Sum of dwks6 + dwks9
dwks13: float
    Difference of dwks10 - dwks12
dwks14: float
    Maximum of 0 and dwks1 - dwks13
dwks18: float
    Maximum of dwks16 and dwks17
dwks43: float
    separate tax on long-term capital gains and qualified dividends
c05700: float
    Lump sum distributions
taxbc: float
    Regular tax on regular taxable income before credits
```

## AGIsurtax

```python
def AGIsurtax(c00100, MARS, AGI_surtax_trt, AGI_surtax_thd, taxbc, surtax)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/calcfunctions.py#L2371)

```text
Computes a flat surtax on the portion of Adjusted Gross Income (AGI)
above a MARS-indexed threshold.

Reform construct: there is no IRS form correspondence (the Internal
Revenue Code has no general AGI surtax line). Inert under current
law because `AGI_surtax_trt` defaults to 0.0 for all years and
`AGI_surtax_thd` defaults to 9e+99 for every MARS value.

When the rate is positive the same amount (`rate * max(0, AGI - thd)`)
is added to two accumulators:
  - `taxbc` (regular tax on regular taxable income before credits)
    so the surtax flows through `c05800` into `iitax` downstream;
  - `surtax` (records-bound diagnostic accumulator, also incremented
    by `FairShareTax` for the "Buffett Rule" reform construct).

Called in `Calculator.calc_all` after `GainsTax` (so `taxbc` already
reflects the rate-schedule + qualified-div/LTCG tax) and before
`NetInvIncTax` and `AMT`.

Parameters
----------
c00100: float
    Adjusted Gross Income (Form 1040 line 11)
MARS: int
    Filing (marital) status (1=single, 2=joint, 3=separate,
                             4=household-head, 5=widow(er))
AGI_surtax_trt: float
    Reform-only flat surtax rate applied to AGI above
    `AGI_surtax_thd[MARS-1]`. Default 0.0 (inert).
AGI_surtax_thd: list
    Reform-only MARS-indexed AGI threshold above which the surtax
    applies. Default 9e+99 (inert).
taxbc: float
    Regular tax on regular taxable income before credits (input;
    already includes rate-schedule + qualified-div/LTCG tax)
surtax: float
    Records-bound surtax accumulator (input)

Returns
-------
taxbc: float
    Input `taxbc` augmented by the AGI surtax
surtax: float
    Input `surtax` augmented by the AGI surtax
```

## AMT

```python
def AMT(e07300, dwks13, standard, f6251, c00100, c17000, c18300, taxbc, c04470, c20800, c21040, e24515, MARS, dwks18, dwks14, c05700, e62900, e00700, dwks10, age_head, earned, cmbtp, qbided, tip_income_deduction, overtime_income_deduction, auto_loan_interest_deduction, AMT_child_em_c_age, AMT_brk1, AMT_em, AMT_prt, AMT_rt1, AMT_rt2_addon, AMT_child_em, AMT_em_ps, AMT_em_pe, AMT_Medical_frt, AMT_CG_brk1, AMT_CG_brk2, AMT_CG_brk3, AMT_CG_rt1, AMT_CG_rt2, AMT_CG_rt3, AMT_CG_rt4, AMT_CG_rt1250, c05800, c09600, c62100)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/calcfunctions.py#L2429)

```text
Computes Form 6251 (2025) Alternative Minimum Tax (AMT).

Builds AMT taxable income c62100 (Form 6251 line 4), tentative
minimum tax via either the flat-rate computation (line 7) or
Part III's maximum-capital-gains-rates worksheet (lines 12-40),
subtracts AMT foreign tax credit (line 8) to yield tentative
minimum tax (line 9), and subtracts the regular-tax base
(line 10) to yield AMT liability c09600 (line 11). Total tax
before credits c05800 = taxbc + c09600.

Form 6251 structure:
  - Part I (lines 1a-4): line 1a = Form 1040 line 14 less Sch 1-A
    line 37 and line 1b = Form 1040 line 11b less line 1a, which
    together are AGI less the standard-or-itemized deduction, less
    QBID, and less the Sch 1-A tip/overtime/auto-loan deductions.
    The Sch 1-A senior deduction (line 37) is not allowed for the
    AMT and so is never subtracted here.  Line 2a then adds back
    the AMT-disallowed deduction: SALT (Sch A line 7) for
    itemizers, the standard deduction (IRC 56(b)(1)(E)) for
    nonitemizers.  Sch A misc is added back, line 2b refunds
    (e00700) are subtracted, and the unmodeled prefs/adjustments
    (lines 2c-2t + 3) are captured in cmbtp.  Pre-2017 law
    also added back the medical expenses deducted under the
    regular tax's lower floor but disallowed under the AMT's
    higher floor: max(0, min(c17000, AMT_Medical_frt * c00100)).
    AMT_Medical_frt is zero beginning in 2017, when TCJA (and now
    OBBBA) harmonized the regular and AMT Sch A medical floors at
    7.5% of AGI, making this add-back inert under current law.
  - Part II top (lines 5-6): exemption schedule with phaseout
    (line 5 = AMT_em - AMT_prt * max(0, AMTI - AMT_em_ps));
    line 6 = AMTI - exemption.
  - Part II tax (line 7): flat-rate AMT tax (26% below AMT_brk1,
    28% above) OR Part III's cap-gains-aware tax (line 40).
  - Part III (lines 12-40): tax computation using maximum
    capital gains rates (0% / 15% / 20% / 25% unrecap §1250)
    paralleling QDCGTW / Sch D Tax Worksheet.
  - Part II bottom (lines 8-11): AMT FTC, tentative minimum
    tax, regular-tax base, AMT.

Special rules:
  - MARS == 3 (MFS): exemption fully phased out when
    c62100 > AMT_em_pe (IRC §55(d)(3) "$900,350 see instructions"
    cliff).
  - IRC §59(j) kiddie AMT: for non-joint filers under
    AMT_child_em_c_age, exemption capped at earned + AMT_child_em
    (IRC §1(g)(2)(C): kiddie tax never applies to a joint return).
  - Reform-only 4th cap-gains bracket: cap gains that, when
    stacked on top of ordinary income, are above the AMT_CG_brk3
    taxable-income threshold are taxed at AMT_CG_rt4 instead of
    AMT_CG_rt3 (no form analogue; AMT_CG_brk3 default 9e+99 makes
    this inert under current law).

Downstream: c05800 → C1040 (Form 1040 line 16 + Sch 2 line 1) →
                     NonrefundableCredits → IITAX.

Parameters
-----------
standard: float
    Standard deduction (zero for itemizers); branches AMTI
    construction (form line 1b itemizer vs non-itemizer path)
c00100: float
    Adjusted Gross Income (Form 1040 line 11)
e00700: float
    Taxable refunds of state and local income taxes
    (Form 6251 line 2b subtraction)
qbided: float
    Qualified business income deduction (Form 1040 line 13a)
tip_income_deduction: float
    Sch 1-A Part II tip deduction (line 13); allowed for the AMT
overtime_income_deduction: float
    Sch 1-A Part III overtime deduction (line 21); allowed for AMT
auto_loan_interest_deduction: float
    Sch 1-A Part IV auto-loan-interest deduction (line 30);
    allowed for the AMT
c04470: float
    Itemized deductions after Pease phase-out (zero for non-
    itemizers); Form 1040 line 12 itemized portion
c18300: float
    Schedule A SALT post-cap deduction (Form 6251 line 2a
    add-back for itemizers)
c20800: float
    Schedule A miscellaneous deductions post-2% floor (TCJA-
    suspended 2018-2025; add-back)
c21040: float
    Itemized deductions that are phased out by Pease
    (subtracted to undo Pease for AMT)
c17000: float
    Schedule A medical expense deduction under the regular tax's
    floor (used in the pre-2017 AMT medical add-back)
AMT_Medical_frt: float
    Floor (as a decimal fraction of AGI) for the AMT medical
    deduction add-back; 0.025 before 2017, zero in 2017+ (TCJA/
    OBBBA harmonized regular and AMT medical deduction floors)
cmbtp: float
    Estimate of income on AMT Form 6251 but not in AGI; captures
    Form 6251 lines 2c through 2t and line 3 (depreciation,
    depletion, ISO, PAB interest, etc.) not separately modeled
MARS: int
    Filing (marital) status. (1=single, 2=joint, 3=separate,
                              4=household-head, 5=widow(er))
AMT_em: list
    AMT exemption amount by MARS (Form 6251 line 5)
AMT_prt: float
    AMT exemption phaseout rate (line 5 phaseout)
AMT_em_ps: list
    AMT exemption phaseout start by MARS
AMT_em_pe: float
    AMT exemption phaseout ending AMT taxable income for
    married filing separately (MARS == 3 cliff)
AMT_child_em_c_age: float
    Age ceiling for IRC §59(j) kiddie-AMT exemption cap
AMT_child_em: float
    Kiddie-AMT exemption increment: earned + this amount
age_head: int
    Age in years of taxpayer (i.e. primary adult); 0 = unset
earned: float
    Earned income for filing unit
AMT_brk1: list
    AMT bracket 1 upper threshold by MARS (Form 6251 line 7:
    $239,100 / $119,550 MFS)
AMT_rt1: float
    AMT rate 1 (26%)
AMT_rt2_addon: float
    Additional AMT rate above AMT_brk1 (combined top = 28%)
e24515: float
    Schedule D unrecaptured §1250 gain (Form 6251 line 14)
dwks13: float
    QDCGTW line 4 / Sch D TW line 13 (Form 6251 line 13)
dwks14: float
    QDCGTW line 5 / Sch D TW line 14 (Form 6251 line 20)
dwks18: float
    QDCGTW line 5 / Sch D TW line 21 (Form 6251 line 27)
dwks10: float
    Schedule D Tax Worksheet line 10 (cap on Form 6251 line 15)
AMT_CG_brk1: list
    Top of long-term capital gains and qualified dividends (AMT)
    tax bracket 1 (Form 6251 line 19: top of 0% bracket)
AMT_CG_brk2: list
    Top of long-term capital gains and qualified dividends (AMT)
    tax bracket 2 (Form 6251 line 25: top of 15% bracket)
AMT_CG_brk3: list
    Reform-only top of cap-gains bracket 3 (taxable-income
    threshold with gains stacked on top of ordinary income;
    default 9e+99 → inert under current law)
AMT_CG_rt1: float
    Long term capital gain and qualified dividends (AMT) rate 1
    (0%)
AMT_CG_rt2: float
    Long term capital gain and qualified dividends (AMT) rate 2
    (15%)
AMT_CG_rt3: float
    Long term capital gain and qualified dividends (AMT) rate 3
    (20%)
AMT_CG_rt4: float
    Reform-only long term capital gain and qualified dividends
    (AMT) rate 4
AMT_CG_rt1250: float
    Unrecaptured Section 1250 gain (AMT) rate
f6251: int
    1 if Form 6251 (AMT) attached to return, otherwise 0
e62900: float
    Alternative Minimum Tax foreign tax credit from Form 6251
    (used when f6251 == 1)
e07300: float
    Foreign tax credit from Form 1116 (used when f6251 == 0)
taxbc: float
    Regular tax on regular taxable income before credits (used
    in the Form 6251 line 10 regular-tax base)
c05700: float
    Lump sum distributions (Form 4972) subtracted from taxbc in
    the Form 6251 line 10 regular-tax base
c05800: float
    Total (regular + AMT) income tax liability before credits
c09600: float
    Alternative Minimum Tax (AMT) liability
c62100: float
    Alternative Minimum Tax (AMT) taxable income

Returns
-------
c62100: float
    Alternative Minimum Tax (AMT) taxable income (Form 6251 line 4)
c09600: float
    Alternative Minimum Tax (AMT) tax liability (Form 6251 line 11)
c05800: float
    Total (regular + AMT) income tax liability before credits
```

## NetInvIncTax

```python
def NetInvIncTax(e00300, e00600, e02000, e26270, c01000, c00100, NIIT_thd, MARS, NIIT_PT_taxed, NIIT_rt, niit)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/calcfunctions.py#L2747)

```text
Computes the Net Investment Income Tax (NIIT) per Form 8960 (2025),
Parts I and III for individuals.  Output `niit` flows downstream
through `C1040` to Schedule 2 line 12 ("Other Taxes") and thence to
Form 1040 line 23 / `iitax`.

Form structure:
  * Part I  (lines 1-8)   Investment income.
  * Part II (lines 9-11)  Investment expenses — NOT MODELED;
                          effectively treated as zero (Tax-Calculator
                          records do not separate the investment-
                          interest, allocable state-tax, and misc-
                          investment expense items from total Sch A).
  * Part III (lines 12-17) Tax computation for individuals
                          (estate/trust lines 18-21 not applicable).

Mapping of Form 8960 lines to inputs:
  * line 1  Taxable interest         <- e00300
  * line 2  Ordinary dividends       <- e00600
  * line 3  Annuities                NOT MODELED (excluded from NII)
  * line 4a Sch E rents/royalties/
            PT/S-corp/trust/business <- e02000
  * line 4b Adjustment for non-
            section-1411 t-or-b      <- -e26270 when NIIT_PT_taxed is
                                        False (default); 0 otherwise
  * line 4c Combine 4a + 4b          <- e02000 [- e26270]
  * line 5a Property-disposition gain<- c01000 (Sch D §1211(b)-capped
                                        net cap gain/loss, Form 1040
                                        line 7)
  * line 5b/5c Exclusions/adjustment NOT MODELED
  * line 5d Combine 5a+5b+5c         <- c01000
  * line 6  CFC/PFIC adjustments     NOT MODELED
  * line 7  Other modifications      NOT MODELED
  * line 8  Total investment income  <- sum of above
  * line 12 NII = line 8 - line 11   <- max(0., line 8); line 11 = 0
  * line 13 MAGI                     <- c00100 (no foreign earned
                                        income exclusion add-back
                                        because Form 2555 not modeled)
  * line 14 Threshold by filing      <- NIIT_thd[MARS-1]; current-law
            status                      defaults match the form
                                        ($200k single/HoH; $250k MFJ/QW;
                                        $125k MFS)
  * line 15 max(0, line 13 - line 14)
  * line 16 min(line 12, line 15)
  * line 17 NIIT_rt * line 16        <- niit; current-law NIIT_rt
                                        default 0.038 matches the form

`NIIT_PT_taxed` is a reform construct: setting it True zeroes out the
Form 8960 line 4b adjustment so that active partnership / S-corp
income (`e26270`) remains in the NIIT base.

Parameters
----------
e00300: float
    Taxable interest income (Form 8960 line 1)
e00600: float
    Ordinary dividends included in AGI (Form 8960 line 2)
e02000: float
    Schedule E total rental, royalty, partnership, S-corporation,
    trust, and trade-or-business income/loss (Form 8960 line 4a)
e26270: float
    Schedule E: combined partnership and S-corporation net
    income/loss; the portion of e02000 treated as non-section-1411
    trade-or-business income for the Form 8960 line 4b adjustment
c01000: float
    Net capital gain/loss after the Sch D §1211(b) cap
    (Form 8960 line 5a; lines 5b/5c not modeled)
c00100: float
    Adjusted Gross Income (Form 8960 line 13 MAGI proxy;
    foreign earned income exclusion not modeled)
NIIT_thd: list
    Net Investment Income Tax MAGI threshold by filing status
    (Form 8960 line 14)
MARS: int
    Filing (marital) status. (1=single, 2=joint, 3=separate,
                              4=household-head, 5=widow(er))
NIIT_PT_taxed: bool
    Reform switch: false (current law) excludes active partnership
    and S-corp income from the NIIT base via the Form 8960 line 4b
    adjustment; true keeps it in the base.
NIIT_rt: float
    Net Investment Income Tax rate (Form 8960 line 17; 3.8% under
    current law)
niit: float
    Net investment income tax from Form 8960 (workspace, overwritten)

Returns
-------
niit: float
    Net investment income tax from Form 8960 line 17
```

## F2441

```python
def F2441(MARS, earned_p, earned_s, f2441, CDCC_c, e32800, exact, c00100, CDCC_ps1, CDCC_ps2, CDCC_po1_rate_max, CDCC_po1_rate_min, CDCC_po2_rate_min, CDCC_po1_step_size, CDCC_po2_step_size, CDCC_po_rate_per_step, CDCC_refundable, c05800, e07300, c32800, c07180, CDCC_refund)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/calcfunctions.py#L2864)

```text
Calculates Form 2441 (2025) Child and Dependent Care Expenses credit.

Maps to Form 2441 Part II lines 2-11:
  line 2  (qualifying persons) ......... f2441 (capped at 2)
  line 3  (expenses, capped $3k/$6k) ... c32800 = min(e32800, line2*CDCC_c)
  line 4  (taxpayer earned income) ..... earned_p
  line 5  (spouse earned income, MFJ) .. earned_s (else line 4)
  line 6  (smallest of 3, 4, 5) ........ line6
  line 7  (AGI) ........................ c00100
  line 8  (decimal from AGI table) ..... crate
  line 9a (line 6 * line 8) ............ line9a
  line 9b (2024 expenses paid in 2025) . not modeled (records data gap)
  line 9c (line 9a + line 9b) .......... = line9a here
  line 10 (tax-liability limit) ........ max(0, c05800 - e07300)
  line 11 (nonrefundable credit) ....... c07180 = min(line 9c, line 10)

The line-8 rate is computed via two stepped phase-downs:
  - From CDCC_po1_rate_max (35%) down to CDCC_po1_rate_min (20%)
    starting at AGI > CDCC_ps1, in CDCC_po1_step_size AGI steps of
    size CDCC_po_rate_per_step.
  - From CDCC_po1_rate_min down to CDCC_po2_rate_min starting at
    AGI > CDCC_ps2[MARS-1], in CDCC_po2_step_size[MARS-1] AGI steps
    of size CDCC_po_rate_per_step (OBBBA upper phase-down).

Form 2441 line 9b (Worksheet A line 13 = qualified 2024 dependent-care
expenses paid in 2025 in excess of the 2024 cap) is not modeled
because Tax-Calculator records do not separate prior-year-unpaid
expenses from current-year expenses; for filers with a 2024 catch-up
amount the modeled credit is biased downward by `line9b * crate`.
The 2025 credit remains entirely non-refundable on-form; the
reform-only CDCC_refundable switch instead routes the full line-9a
amount to CDCC_refund (all-or-nothing, not the on-form line-9b
catch-up provision).

The line-10 Credit Limit Worksheet (2025) subtracts only Schedule 3
line 1 (foreign tax credit, modeled as e07300) and Schedule 3 line 6l
(Form 8978 line 14, BBA partner imputed-underpayment push-out — not
modeled). CDCC is itself Schedule 3 line 2, so no other nonrefundable
credits precede it in the Sch 3 ordering, and `c05800 - e07300`
faithfully implements the worksheet (modulo the unmodeled Form 8978
line). F2441 is correspondingly called first in calculator.py among
the Schedule 3 credit functions, before PersonalTaxCredit,
AmOppCreditParts, SchR, EducationTaxCredit, CharityCredit, and
ChildDepTaxCredit.

Parameters
----------
MARS: int
    Filing (marital) status. (1=single, 2=joint, 3=separate,
                              4=household-head, 5=widow(er))
earned_p: float
    Earned income for taxpayer
earned_s: float
    Earned income for spouse
f2441: int
    Number of child/dependent care qualifying persons
CDCC_c: float
    Maximum child/dependent care credit per dependent
e32800: float
    Child/dependent care expenses for qualifying persons from Form 2441
exact: int
    Whether or not to do rounding of phaseout fraction
c00100: float
    Adjusted Gross Income (AGI)
CDCC_ps1: float
    Child/dependent care credit first phaseout start
CDCC_ps2: list[float]
    Child/dependent care credit second phaseout start
CDCC_po1_rate_max: float
    Child/dependent care credit first phaseout rate maximum
CDCC_po1_rate_min: float
    Child/dependent care credit first phaseout rate minimum
CDCC_po2_rate_min: float
    Child/dependent care credit second phaseout rate minimum
CDCC_po1_step_size: float
    Child/dependent care credit first phaseout AGI step size
CDCC_po2_step_size: float
    Child/dependent care credit second phaseout AGI step size
CDCC_po_rate_per_step: float
    Child/dependent care credit phaseout rate per step size
CDCC_refundable: bool
    Indicator for whether CDCC is refundable
c05800: float
    Total (regular + AMT) income tax liability before credits
e07300: float
    Foreign tax credit from Form 1116
c32800: float
    Child and dependent care expenses capped by policy (not by earnings)
c07180: float
    Credit for child and dependent care expenses from Form 2441

Returns
-------
c32800: float
    Child and dependent care expenses capped by policy (not by earnings)
c07180: float
    Credit for child and dependent care expenses from Form 2441
CDCC_refund: float
    Refundable amount of c07180 amount
```

## EITCamount

```python
def EITCamount(basic_frac, phasein_rate, earnings, max_amount, phaseout_start, agi, phaseout_rate)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/calcfunctions.py#L3026)

```text
Returns the EIC Worksheet A (or B) line 6 amount: the smaller of
the earned-income-based credit (line 2, an EIC-Table lookup keyed
on earnings) and the AGI-based credit (line 5, the same lookup
keyed on AGI when AGI exceeds the phaseout start).

The trapezoidal credit schedule is:
  - phase-in:  phasein_rate * earnings
  - plateau:   max_amount
  - phase-out: max_amount - phaseout_rate * (max(earnings, AGI) - ps)

English parameter names are used because the EIC Table is published
rather than the algebraic formula; `basic_frac` is a reform-only
knob (0 under current law) that shifts the schedule so a fraction
of `max_amount` is paid at zero earnings.

Parameters
----------
basic_frac: float
    Fraction of maximum earned income credit paid at zero earnings
    (reform-only; 0 under current law)
phasein_rate: float
    Earned income credit phasein rate (EIC Table phase-in slope)
earnings: float
    Earned income for filing unit (EIC Worksheet A line 1)
max_amount: float
    Maximum earned income credit (EIC Table plateau)
phaseout_start: float
    Earned income credit phaseout start (EIC Worksheet A line 3
    threshold; AGI/earnings at which line 5 begins to bite)
agi: float
    Adjusted Gross Income (Form 1040 line 11; EIC Worksheet A
    line 3) — the worksheet uses AGI rather than earnings to
    compute line 5 when AGI exceeds line 4
phaseout_rate: float
    Earned income credit phaseout rate (EIC Table phase-out slope)

Returns
-------
eitc: float
    Earned Income Credit (EIC Worksheet A line 6)
```

## EITC

```python
def EITC(eitc_claim_prob_min, eitc_claim_prob_scale, credit_claim_urn, MARS, DSI, c00100, e00300, e00400, e00600, c01000, e02000, e26270, age_head, age_spouse, earned, earned_p, earned_s, EIC, EITC_ps, EITC_MinEligAge, EITC_MaxEligAge, EITC_ps_addon_MarriedJ, EITC_rt, EITC_c, EITC_prt, EITC_basic_frac, EITC_InvestIncome_c, EITC_excess_InvestIncome_rt, EITC_indiv, EITC_sep_filers_elig, c59660)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/calcfunctions.py#L3080)

```text
Computes Earned Income Tax Credit (Form 1040 line 27a).

Implements EIC Worksheet A (Form 1040 instructions) and the Pub 596
"Rules If You Have a Qualifying Child" / "Rules If You Do Not Have
a Qualifying Child" eligibility tests.  Schedule EIC supplies the
qualifying-child count (the `EIC` Records variable); per-child
EITC parameters (`EITC_rt`/`EITC_c`/`EITC_prt`/`EITC_ps`) are
length-5 lists indexed by `EIC` ∈ {0, 1, 2, 3, 4} with index 4
cloned from 3 to encode the "3 or more" plateau.

EIC Worksheet B (for filers with self-employment income) is not
represented separately because Tax-Calculator's `earned` input
(built by `EI_PayrollTax`) already includes net SE earnings, so
Worksheets A and B collapse to a single `EITCamount` call.

Body sections (mirroring the worksheet + Pub 596):
  (A) EIC Worksheet A credit amount (filing-unit, or reform-only
      per-spouse under `EITC_indiv`).  MFJ adds
      `EITC_ps_addon_MarriedJ[EIC]` to the phaseout start.
  (B) Pub 596 Rule 11: childless filer must be age
      `EITC_MinEligAge`-`EITC_MaxEligAge` (current law 25-64;
      age == 0 in the data is treated as eligible).  Applies only
      when EIC == 0; for MFJ either spouse meeting the age test
      qualifies.
  (C) Pub 596 Rule 3 (MFS) and Rule 10 (claimed as dependent).
      MFS eligibility tracks IRC §32(d) as amended by ARPA 2021
      §9621 via `EITC_sep_filers_elig` (false 2013-2020, true
      2021+); DSI==1 always disqualifies.
  (D) Pub 596 Rule 6: investment-income cliff (IRC §32(i)).
      Investment income = taxable interest (`e00300`) + tax-exempt
      interest (`e00400`) + ordinary dividends (`e00600`) + net
      capital gain (`max(0, c01000)`) + net non-passive rents and
      royalties (`max(0, e02000 - e26270)`, removing Sch E
      partnership/S-corp).  The form's hard cliff at
      `EITC_InvestIncome_c` ($11,950 for 2025) is modeled as a
      smooth phaseout at `EITC_excess_InvestIncome_rt` (default
      9e+99 → behaviorally identical to the cliff).
  (E) Model-specific claiming approximation: see details below.
      No form analogue.

Downstream: `c59660` is the records-bound EITC amount consumed by
`IITAX` (Form 1040 line 27a, refundable credit) and reported in
`taxcalc/cli/input_data_tests/tests.sh` baseline `*.tables`.

Parameters
----------
eitc_claim_prob_min: float
    See Section E logic and comments (no form analogue)
eitc_claim_prob_scale: float
    See Section E logic and comments (no form analogue)
credit_claim_urn: float
    See Section E logic and comments (no form analogue)
MARS: int
    Filing (marital) status (1=single, 2=joint, 3=separate,
                             4=household-head, 5=widow(er))
DSI: int
    1 if claimed as dependent on another return, otherwise 0
    (Pub 596 Rule 10)
EIC: int
    Number of EIC qualifying children (from Schedule EIC,
    capped at 3 for parameter-lookup purposes; values up to 4
    are accepted but mapped to the index-4 entry which clones
    index 3)
c00100: float
    Adjusted Gross Income (Form 1040 line 11; EIC Worksheet A
    line 3)
e00300: float
    Taxable interest income (investment-income component)
e00400: float
    Tax-exempt interest income (investment-income component;
    IRC §32(i)(2)(B))
e00600: float
    Ordinary dividends included in AGI (investment-income
    component)
c01000: float
    Capital-loss-limited Schedule D total (Sch D line 21;
    investment income uses `max(0, c01000)` — only net gain
    per IRC §32(i)(2)(D))
e02000: float
    Schedule E total rental, royalty, partnership, S-corp,
    etc., income/loss
e26270: float
    Schedule E combined partnership and S-corp net income/loss
    (subtracted from `e02000` to leave net rents and royalties)
age_head: int
    Age in years of taxpayer (primary adult); 0 in the data
    means unknown and is treated as eligible
age_spouse: int
    Age in years of spouse (secondary adult, if present); 0 means
    unknown / no spouse
earned: float
    Earned income for filing unit (EIC Worksheet A/B line 1;
    already includes net SE earnings via `EI_PayrollTax`)
earned_p: float
    Earned income for taxpayer (used only for reform-only
    `EITC_indiv` per-spouse EITC)
earned_s: float
    Earned income for spouse (used only for reform-only
    `EITC_indiv` per-spouse EITC)
EITC_ps: list
    EIC-indexed phaseout start (EIC Worksheet A line 3 threshold)
EITC_MinEligAge: int
    Minimum age for childless EITC eligibility (Pub 596 Rule 11;
    25 under current law)
EITC_MaxEligAge: int
    Maximum age for childless EITC eligibility (Pub 596 Rule 11;
    64 under current law)
EITC_ps_addon_MarriedJ: list
    EIC-indexed addition to the phaseout start for MFJ filers
    (= EIC-Table MFJ threshold − single threshold)
EITC_rt: list
    EIC-indexed phasein rate
EITC_c: list
    EIC-indexed maximum credit (EIC Table plateau)
EITC_prt: list
    EIC-indexed phaseout rate
EITC_basic_frac: float
    Reform-only fraction of `EITC_c` paid at zero earnings;
    default 0 (inert under current law)
EITC_InvestIncome_c: float
    Investment-income ceiling (IRC §32(i); $11,950 for 2025)
EITC_excess_InvestIncome_rt: float
    Rate at which the EITC is reduced per dollar of investment
    income above `EITC_InvestIncome_c`; default 9e+99 makes the
    smooth phaseout behaviorally equivalent to the form's hard
    cliff
EITC_indiv: bool
    Reform-only: if true, MFJ EITC is computed per spouse on
    individual earnings and summed; default false (filing-unit
    EITC per the form)
EITC_sep_filers_elig: bool
    MFS eligibility (Pub 596 Rule 3 / IRC §32(d) as amended by
    ARPA 2021 §9621); false 2013-2020, true 2021+
c59660: float
    Records-bound EITC amount (input, overwritten)

Returns
-------
c59660: float
    Earned Income Tax Credit (Form 1040 line 27a)
```

## ChildDepTaxCredit

```python
def ChildDepTaxCredit(age_head, age_spouse, nu18, n24, MARS, c00100, XTOT, num, c05800, e07260, CR_ResidentialEnergy_hc, e07300, CR_ForeignTax_hc, c07180, c07230, e07240, CR_RetirementSavings_hc, c07200, CTC_c, CTC_ps, CTC_prt, exact, ODC_c, CTC_c_under6_bonus, nu06, CTC_is_refundable, CTC_include17, c07220, odc, codtc_limited)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/calcfunctions.py#L3295)

```text
Computes nonrefundable Child Tax Credit and Credit for Other Dependents
on Schedule 8812 Part I (and Credit Limit Worksheet A).
https://www.irs.gov/pub/irs-pdf/f1040s8.pdf

Parameters
----------
n24: int
    Number of children who are Child-Tax-Credit eligible, one condition
    for which is being under age 17
MARS: int
    Filing (marital) status. (1=single, 2=joint, 3=separate,
                              4=household-head, 5=widow(er))
c00100: float
    Adjusted Gross Income (AGI)
XTOT: int
    Total number of exemptions for filing unit
num: int
    2 when MARS is 2 (married filing jointly), otherwise 1
c05800: float
    Total (regular + AMT) income tax liability before credits
e07260: float
    Residential energy credit from Form 5695
CR_ResidentialEnergy_hc: float
    Credit for residential energy haircut
e07300: float
    Foreign tax credit from Form 1116
CR_ForeignTax_hc: float
    Credit for foreign tax credit
c07180: float
    Credit for child and dependent care expenses from Form 2441
c07230: float
    Education tax credits non-refundable amount from Form 8863
e07240: float
    Retirement savings contributions credit from Form 8880
CR_RetirementSavings_hc: float
    Credit for retirement savings haircut
c07200: float
    Schedule R credit for the elderly and the disabled
CTC_c: float
    Maximum nonrefundable child tax credit per child
CTC_ps: list
    Child tax credit phaseout MAGI start
CTC_prt: float
    Child and dependent tax credit phaseout rate
exact: int
    Whether or not to do rounding of phaseout fraction
ODC_c: float
    Maximum nonrefundable other-dependent credit
CTC_c_under6_bonus: float
    Bonus child tax credit maximum for qualifying children under six
nu06: int
    Number of dependents under 6 years old
c07220: float
    Child tax credit (adjusted) from Form 8812
odc: float
    Other Dependent Credit
codtc_limited: float
    Tentative credit not yet absorbed by tax liability (Sch 8812 line 12
    minus the nonrefundable amount); used by AdditionalCTC.

Returns
-------
c07220: float
    Child tax credit (adjusted) from Form 8812
odc: float
    Other Dependent Credit
codtc_limited: float
    Tentative credit not yet absorbed by tax liability (Sch 8812 line 12
    minus the nonrefundable amount); used by AdditionalCTC.
```

## PersonalTaxCredit

```python
def PersonalTaxCredit(MARS, c00100, XTOT, nu18, II_credit, II_credit_ps, II_credit_prt, II_credit_nr, II_credit_nr_ps, II_credit_nr_prt, RRC_c, RRC_ps, RRC_pe, RRC_prt, RRC_c_kids, RRC_c_unit, personal_refundable_credit, personal_nonrefundable_credit, recovery_rebate_credit)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/calcfunctions.py#L3433)

```text
Computes three reform-construct credits. None corresponds to a 2025
current-law IRS form line:

- `personal_refundable_credit` and `personal_nonrefundable_credit` are
  generic AGI-phased reform knobs (`II_credit*` parameters). Both
  default to zero under current law.
- `recovery_rebate_credit` emulates the 2020 CARES Act Economic Impact
  Payments and the 2021 ARPA Recovery Rebate Credit, both reconciled
  historically on Form 1040 line 30 via a published worksheet. For 2022+
  all RRC parameters default to zero, so the credit is 0 under current
  law.

The two `II_credit*` blocks are identical-shaped: start with the
MARS-indexed maximum; if the rate is positive and AGI exceeds the
MARS-indexed phaseout start, subtract `rate * (AGI - start)` and floor
at 0.

The RRC block encodes an either/or parameter regime:
- 2020 CARES (`RRC_c=0`, `RRC_c_unit`/`RRC_c_kids` > 0, `RRC_prt=0.05`,
  `RRC_pe=0`): branches 1 + 3 implement the CARES linear phaseout
  from `RRC_ps`; branch 2 cannot fire because `c00100 < RRC_pe = 0`
  is never true.
- 2021 ARPA (`RRC_c=1400`, `RRC_c_unit=RRC_c_kids=0`, `RRC_prt=0`):
  branches 1 + 2 implement the ARPA per-person linear ramp from
  `RRC_ps` to `RRC_pe`; branch 3 returns 0.

Downstream: `personal_refundable_credit` and `recovery_rebate_credit`
are added by `IITAX` on the refundable side (Form 1040 line 32-style
additions); `personal_nonrefundable_credit` is sequentially limited
against remaining tax in `NonrefundableCredits`.

Parameters
----------
MARS: int
    Filing (marital) status. (1=single, 2=joint, 3=separate,
                              4=household-head, 5=widow(er))
c00100: float
    Adjusted Gross Income (AGI) (Form 1040 line 11)
XTOT: int
    Total number of exemptions for filing unit (RRC per-person count)
nu18: int
    Number of people under 18 years old in the filing unit (RRC kids
    count)
II_credit: list
    Personal refundable credit maximum amount by MARS (reform-only;
    default 0)
II_credit_ps: list
    Personal refundable credit phaseout start by MARS (reform-only;
    default 0)
II_credit_prt: float
    Personal refundable credit phaseout rate (reform-only; default 0)
II_credit_nr: list
    Personal nonrefundable credit maximum amount by MARS (reform-only;
    default 0)
II_credit_nr_ps: list
    Personal nonrefundable credit phaseout start by MARS (reform-only;
    default 0)
II_credit_nr_prt: float
    Personal nonrefundable credit phaseout rate (reform-only; default 0)
RRC_c: float
    Per-person Recovery Rebate Credit maximum (ARPA 2021 = 1400; 0
    otherwise)
RRC_ps: list
    Recovery Rebate Credit phaseout start by MARS
RRC_pe: list
    Recovery Rebate Credit phaseout end by MARS (used only by the ARPA
    per-person ramp; 0 outside 2021)
RRC_prt: float
    Recovery Rebate Credit phaseout rate (CARES 2020 = 0.05; 0
    otherwise)
RRC_c_kids: float
    Per-child amount for the Recovery Rebate Credit (CARES 2020;
    0 otherwise)
RRC_c_unit: list
    Per-filing-unit base amount for the Recovery Rebate Credit by MARS
    (CARES 2020; 0 otherwise)
personal_refundable_credit: float
    Records-bound output: personal refundable credit
personal_nonrefundable_credit: float
    Records-bound output: personal nonrefundable credit
recovery_rebate_credit: float
    Records-bound output: recovery rebate credit

Returns
-------
personal_refundable_credit: float
    Personal refundable credit
personal_nonrefundable_credit: float
    Personal nonrefundable credit
recovery_rebate_credit: float
    Recovery rebate credit
```

## AmOppCreditParts

```python
def AmOppCreditParts(exact, e87521, num, c00100, CR_AmOppRefundable_hc, CR_AmOppNonRefundable_hc, c10960, c87668)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/calcfunctions.py#L3570)

```text
Computes the American Opportunity Credit (AOTC) refundable and
nonrefundable amounts from Form 8863 Part I (2025).

Form 8863 Part I line map:
  * line 1  Tentative AOTC across students <- e87521 (Form 8863
                                             Part III line 30 sum;
                                             capped at $2,500/student)
  * line 2  Phaseout base by filing status <- 90000*num
                                             ($180k MFJ / $90k other)
  * line 3  MAGI                           <- c00100 (no Form 2555 /
                                             Form 4563 / Puerto Rico
                                             exclusion add-back because
                                             these are not modeled)
  * line 4  max(0, line 2 - line 3)
  * line 5  Phaseout range length          <- 10000*num
                                             ($20k MFJ / $10k other)
  * line 6  min(1.000, line 4 / line 5)    <- rounded to 3 decimals
                                             per IRS instructions when
                                             exact == 1
  * line 7  line 1 * line 6                <- post-phaseout AOTC
  * line 8  0.4 * line 7                   <- refundable AOTC; goes to
                                             Form 1040 line 29 via
                                             c10960
  * Part II line 9 = line 7 - line 8       <- nonrefundable portion
                                             feeding the Part II Credit
                                             Limit Worksheet via c87668

The reform haircuts `CR_AmOppRefundable_hc` and
`CR_AmOppNonRefundable_hc` both default to 0.0 from 2013 onward, so
under current law c10960 = 0.4*line7 and c87668 = 0.6*line7 exactly as
on the form. `num` doubles the single thresholds for MARS=2 (MFJ
thresholds on this form are exactly twice the single thresholds).
The Form 8863 line-7 under-24 dependency-eligibility checkbox
(IRC §25A(i)(6)(B)) is not modeled; Tax-Calculator records do not
encode the parental/dependent status required to determine whether a
filer is barred from the refundable portion.

Calling order: `calculator.py` invokes `AmOppCreditParts` between
`SchR` and `EducationTaxCredit`. `c10960` flows to `IITAX` refundable
side (Form 1040 line 29); `c87668` flows to `EducationTaxCredit`
Part II Credit Limit Worksheet line 10.

Parameters
----------
exact: int
    If 1, round the line-6 phaseout fraction to 3 decimals per IRS
    instructions; if 0, use the unrounded fraction.
e87521: float
    Tentative AOTC across all students (Form 8863 line 1 = sum of
    Part III line 30).
num: int
    2 when MARS is 2 (MFJ), otherwise 1; doubles the single thresholds
    on Form 8863 lines 2 and 5.
c00100: float
    Adjusted Gross Income (Form 8863 line 3 MAGI proxy; Form 2555 /
    Form 4563 / Puerto Rico add-backs not modeled).
CR_AmOppRefundable_hc: float
    Reform haircut on the refundable portion (Form 8863 line 8);
    current-law default 0.0 means no haircut.
CR_AmOppNonRefundable_hc: float
    Reform haircut on the nonrefundable portion (Form 8863 Part II
    line 9); current-law default 0.0 means no haircut.
c10960: float
    Records-bound output, computed below (refundable AOTC).
c87668: float
    Records-bound output, computed below (nonrefundable AOTC fed to
    EducationTaxCredit Part II).

Returns
-------
c10960: float
    Refundable AOTC after the reform haircut (Form 8863 line 8).
c87668: float
    Nonrefundable AOTC after the reform haircut (Form 8863 Part II
    line 9 input).
```

## SchR

```python
def SchR(age_head, age_spouse, MARS, c00100, c05800, e07300, c07180, e02400, c02500, e01500, e01700, CR_SchR_hc, c07200)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/calcfunctions.py#L3671)

```text
Calculates Schedule R (2025) Credit for the Elderly or the Disabled,
c07200 (Schedule 3 line 6d, nonrefundable).

Maps to Schedule R Part III lines 10-22 (Part I checkbox selects the
line-10 base and line-15 AGI threshold; Part II physician statement
not modeled). Schedule R policy amounts are hardcoded on the form
(not inflation-indexed and not exposed as Policy parameters); only
the reform haircut CR_SchR_hc is in policy_current_law.json.

Part I box mapping (Tax-Calculator-reachable boxes only):
  Box 1  Single/HoH/QSS 65+ ......... MARS in (1, 4, 5) and age_head>=65
  Box 3  MFJ both 65+ ............... MARS==2, both ages>=65
  Box 7  MFJ one 65+ + other not disabled MARS==2, one age>=65
  Box 8  MFS 65+ lived apart all year MARS==3 and age_head>=65
Boxes 2/4/5/6/9 (disability) are unreachable — Tax-Calculator records
do not encode disability or taxable disability income, so the Part I
"disabled under 65" paths are not modeled and line 12 reduces to
line 10 (no smaller-of-line-10-or-line-11 step).

Box 8 over-credit (model-input-data gap): the 2025 Schedule R
instructions disallow the credit for MFS filers who "lived with
[their] spouse at any time during 2025"; Box 8 applies only to
MFS filers who lived apart from their spouse for all of 2025.
Tax-Calculator records do not encode whether MFS filers lived
apart all year, so this code treats every MARS==3 filer with
age_head>=65 as Box 8 and over-credits the lived-with-spouse
sub-population. Same record-data limitation pattern as in
SSBenefits (lived-apart-all-year not encoded).

Part III line-by-line mapping:
  line 10 (base) ............ 5000/7500/3750 per box (above)
  line 11 (disability inc) .. not modeled
  line 12 = line 10 (no disability claimed)
  line 13a (nontaxable OASDI). max(0, e02400 - c02500)
  line 13b (nontaxable pens). max(0, e01500 - e01700) — approximation
  line 13c (sum) ............ line13a + line13b
  line 14 (AGI) ............. c00100
  line 15 (AGI threshold) ... 7500/10000/5000 per box
  line 16 ................... max(0, line14 - line15)
  line 17 ................... 0.5 * line16
  line 18 ................... line13c + line17
  line 19 ................... max(0, line12 - line18)
  line 20 ................... 0.15 * line19
  line 21 (tax limit) ....... Credit Limit Worksheet output
  line 22 ................... min(line20, line21), with haircut applied

The line-13b approximation (max(0, e01500 - e01700)) treats every
dollar of gross pension above taxable pension as "nontaxable" under
line-13b. It is exact when all of a filer's pensions are uniformly
fully taxable or uniformly partially taxable; for filers receiving
both a fully-taxable pension and a partially-taxable pension it
over-states the line-13b add-back and biases the credit downward.

The line-21 Credit Limit Worksheet (2025) for Schedule 3 line 6d
per the IRS Schedule R 2025 instructions subtracts Sch 3 line 1
(foreign tax credit, e07300) + Sch 3 line 2 (CDCC, c07180) +
Sch 3 line 6l (Form 8978). Form 8978 is not modeled in
Tax-Calculator records (model-input-data gap). The on-form
worksheet does NOT subtract Sch 3 line 3 Education credits, but
EducationTaxCredit is called AFTER SchR in calc_all so c07230
would not be available here in any case; the final sequential
nonrefundable-credit limit is enforced downstream by
NonrefundableCredits.

Calling-order context (calculator.py): F2441 -> PersonalTaxCredit ->
AmOppCreditParts -> SchR -> EducationTaxCredit -> CharityCredit ->
ChildDepTaxCredit -> NonrefundableCredits. Downstream: c07200 is
consumed by NonrefundableCredits as a nonrefundable Sch 3 credit
summed into the Form 1040 line 22 credit total.

Parameters
----------
age_head: int
    Age in years of taxpayer (primary adult)
age_spouse: int
    Age in years of spouse (secondary adult, if present)
MARS: int
    Filing (marital) status. (1=single, 2=joint, 3=separate,
                              4=household-head, 5=widow(er))
c00100: float
    Adjusted Gross Income (AGI); used for Schedule R line 14
c05800: float
    Total (regular + AMT) income tax liability before credits; input
    to the line-21 Credit Limit Worksheet
e07300: float
    Foreign tax credit from Form 1116 (Sch 3 line 1); subtracted on
    line 21
c07180: float
    Credit for child and dependent care expenses from Form 2441
    (Sch 3 line 2); subtracted on line 21
e02400: float
    Total social security (OASDI) benefits; line 13a gross
c02500: float
    Social security (OASDI) benefits included in AGI; line 13a
    nontaxable = e02400 - c02500
e01500: float
    Total pensions and annuities; line 13b gross
e01700: float
    Taxable pensions and annuities; line 13b nontaxable approximation
    = e01500 - e01700
CR_SchR_hc: float
    Schedule R credit haircut (reform parameter); default 0.0 under
    current law

Returns
-------
c07200: float
    Schedule R credit for the elderly and the disabled (Sch 3 line 6d)
```

## EducationTaxCredit

```python
def EducationTaxCredit(exact, e87530, MARS, c00100, c05800, e07300, c07180, c07200, c87668, LLC_Expense_c, ETC_pe_Single, ETC_pe_Married, CR_Education_hc, c07230)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/calcfunctions.py#L3831)

```text
Computes Education Tax Credits (`c07230`, Schedule 3 line 3) from
Form 8863 (2025) Part II "Nonrefundable Education Credits" and the
Credit Limit Worksheet (CLW) in the Form 8863 instructions.

Part II line-by-line mapping:
    line 9  = `c87668`        (nonref AOTC, computed by `AmOppCreditParts`)
    line 10 = `e87530`        (LLC adjusted qualified expenses,
                               summed over students)
    line 11 = min(`e87530`, `LLC_Expense_c`)         (cap; $10,000 on form)
    line 12 = line 11 * 0.20                         (LLC tentative)
    line 13 = $180,000 MFJ / $90,000 other (`ETC_pe_*` stored in
                                            thousands of dollars)
    line 14 = AGI (`c00100`)
    line 15 = max(0., line 13 - line 14)
    line 16 = $20,000 MFJ / $10,000 other            (phaseout spread)
    line 17 = min(1., line 15 / line 16) rounded to 3 decimals when
              `exact==1` per the form instruction
    line 18 = line 12 * line 17                      (LLC after phaseout)
    line 19 = CLW line 7                             -> Sch 3 line 3

Credit Limit Worksheet (from Form 8863 instructions):
    CLW line 1  = Form 8863 line 18                  (LLC after phaseout)
    CLW line 2  = Form 8863 line 9                   (nonref AOTC)
    CLW line 3  = CLW line 1 + CLW line 2
    CLW line 4  = Form 1040 line 18 = `c05800`
    CLW line 5  = Sch 3 line 1 (`e07300` FTC) + line 2 (`c07180` CDCC)
                + line 6d (`c07200` SchR) + 6f + 6l + 6m
                  (6f / 6l / 6m unmodeled in Tax-Calculator records)
    CLW line 6  = CLW line 4 - CLW line 5
    CLW line 7  = min(CLW line 3, CLW line 6)        (nonref ed credits)
The code applies CLW lines 5-7 sequentially (LLC first, then nonref
AOTC, subtracting LLC from remaining tax-availability before AOTC);
this is algebraically equivalent to the form's single combined
`min(line 3, line 6)` because both portions are bounded above by
the same tax-availability quantity (line 6).

`ETC_pe_Single` / `ETC_pe_Married` are stored in thousands of
dollars per `policy_current_law.json` (descriptions say "in
thousands"), so the `* 1000.` factors convert them to the dollar
thresholds the form prints on line 13.

`CR_Education_hc` is a reform construct (haircut) with no IRS-form
counterpart; under current law it defaults to 0.0 for all years,
so `c07230` equals the on-form line 19 unmodified.

Downstream consumer: `c07230` flows to `NonrefundableCredits` as
Sch 3 line 3 in the credit-ordering and is sequentially re-limited
against remaining tax-before-credits there before being summed into
the nonrefundable-credit total subtracted in `IITAX`.

Parameters
----------
exact: int
    Whether or not to do rounding of phaseout fraction (Form 8863
    line 17 form-instruction rounding when `exact==1`).
e87530: float
    Adjusted qualified lifetime learning expenses for all students
    (Form 8863 Part III line 31 summed across students; Part II
    line 10).
MARS: int
    Filing (marital) status. (1=single, 2=joint, 3=separate,
                              4=household-head, 5=widow(er))
c00100: float
    Adjusted Gross Income (Form 1040 line 11; Form 8863 line 14).
c05800: float
    Total (regular + AMT) income tax liability before credits
    (CLW line 4).
e07300: float
    Foreign tax credit from Form 1116 (Sch 3 line 1; CLW line 5).
c07180: float
    Credit for child and dependent care expenses from Form 2441
    (Sch 3 line 2; CLW line 5).
c07200: float
    Schedule R credit for the elderly and the disabled (Sch 3
    line 6d; CLW line 5).  Sch 3 lines 6f / 6l / 6m also belong
    to CLW line 5 but are not modeled in Tax-Calculator records.
c87668: float
    American Opportunity Credit nonrefundable amount from Form 8863
    line 9 (= 0.6 * line 7), computed by `AmOppCreditParts`.
LLC_Expense_c: float
    Lifetime learning credit expense limit (Form 8863 line 11 cap;
    $10,000 on the form).
ETC_pe_Single: float
    Education tax credit phaseout end for non-joint filers, in
    thousands of dollars (Form 8863 line 13 = $90,000 for non-MFJ).
ETC_pe_Married: float
    Education tax credit phaseout end for joint filers, in thousands
    of dollars (Form 8863 line 13 = $180,000 for MFJ).
CR_Education_hc: float
    Education credits haircut.  Reform construct; default 0.0 under
    current law (function emits on-form line 19 unmodified).
c07230: float
    Records-bound output, computed below.

Returns
-------
c07230: float
    Education tax credits nonrefundable amount (Form 8863 line 19;
    Sch 3 line 3) with reform haircut applied.
```

## CharityCredit

```python
def CharityCredit(e19800, e20100, c00100, CR_Charity_rt, CR_Charity_f, CR_Charity_frt, MARS, charity_credit)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/calcfunctions.py#L3973)

```text
Computes nonrefundable credit for charitable giving (a reform
construct with no IRS form correspondence; not part of current-law
policy).  Under current law `CR_Charity_rt`, `CR_Charity_f`, and
`CR_Charity_frt` all default to 0.0, so `charity_credit` is
identically 0 and the function is inert.

Under reform the credit equals
    CR_Charity_rt * max(0, (e19800 + e20100) - floor)
where the floor is the larger of a MARS-indexed dollar amount
(`CR_Charity_f[MARS-1]`) and an AGI-share (`CR_Charity_frt *
c00100`); only giving in excess of the floor earns the credit.

Downstream consumers: `charity_credit` is fed to
`NonrefundableCredits`, where it is sequentially limited against
the remaining tax-before-credits (`avail`), and the limited amount
is then summed into the nonrefundable-credit total subtracted from
tax in `IITAX`.

Parameters
----------
e19800: float
    Itemizable charitable giving for cash and check contributions
    (Sch A line 11)
e20100: float
    Itemizable charitable giving other than cash and check
    contributions (Sch A line 12)
c00100: float
    Adjusted Gross Income (AGI; Form 1040 line 11)
CR_Charity_rt: float
    Charity credit rate (reform-only; 0 under current law)
CR_Charity_f: list
    MARS-indexed dollar floor: only giving above this amount is
    eligible (reform-only; 0 under current law)
CR_Charity_frt: float
    AGI-share floor: only giving above this fraction of AGI is
    eligible (reform-only; 0 under current law)
MARS: int
    Filing (marital) status. (1=single, 2=joint, 3=separate,
                              4=household-head, 5=widow(er))
charity_credit: float
    Records-bound output, computed below.

Returns
-------
charity_credit: float
    Credit for charitable giving
```

## NonrefundableCredits

```python
def NonrefundableCredits(c05800, e07240, e07260, e07300, e07400, e07600, p08000, odc, personal_nonrefundable_credit, CTC_is_refundable, ODC_is_refundable, CR_RetirementSavings_hc, CR_ForeignTax_hc, CR_ResidentialEnergy_hc, CR_GeneralBusiness_hc, CR_MinimumTax_hc, CR_OtherCredits_hc, charity_credit, c07180, c07200, c07220, c07230, c07240, c07260, c07300, c07400, c07600, c08000)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/calcfunctions.py#L4032)

```text
Sequentially limits nonrefundable credits against remaining income
tax liability and returns the limited per-credit amounts.  The
limited amounts are summed by `C1040` into Form 1040 line 22 via
Form 1040 line 19 (CTC + Credit for Other Dependents) and line 20
(Schedule 3 Part I total).

Application order mirrors Schedule 3 (2025) Part I line numbering
plus Form 1040 line 19, with reform-construct credits appended:

  (A) Sch 3 Part I lines 1-4 (FTC -> CDCC -> Education -> RetSav)
  (B) Form 1040 line 19 (CTC -> ODC); CTC capping is skipped
      under reform-only `CTC_is_refundable` and ODC capping is
      skipped under reform-only `ODC_is_refundable`, with each
      credit independently routed to the refundable side in
      `IITAX` / `CTC_new`
  (C) Sch 3 Part I lines 5a, 6a, 6b, 6d, 6z (ResEnergy -> GenBus
      -> PrYrMin -> SchR -> Other); unmodeled on-form items are
      5b, 6c, 6e-6m
  (D) Reform-only nonrefundable credits (charity_credit,
      personal_nonrefundable_credit); inert under current law

CTC/ODC placement between Sch 3 line 4 and line 5a is consistent
with Sch 8812 Credit Limit Worksheet A, which subtracts only Sch 3
lines 1, 2, 3, 4 (plus a set of unmodeled credits) from tax before
applying CTC.  Credits with statutory carryforwards (ResEnergy,
GenBus, PrYrMin) come after CTC/ODC, which have no carryforward.

Two flavors of inputs:
  * **Raw record values** `e07240`, `e07260`, `e07300`, `e07400`,
    `e07600`, `p08000`: the per-credit haircut `(1 - CR_*_hc)` is
    applied here, then `min` against remaining tax.  All `CR_*_hc`
    parameters default to 0.0 (current-law inert).
  * **Pre-computed credits** `c07180`, `c07200`, `c07220`,
    `c07230`, `odc`, `charity_credit`,
    `personal_nonrefundable_credit`: the source function already
    applied any haircut and its own Credit Limit Worksheet; this
    function re-caps against remaining tax (belt-and-braces, and
    correcting any source-side worksheet that omitted a Sch 3
    line ahead of itself -- e.g., `SchR` line-21 worksheet omits
    Sch 3 line 3 Education).

Calling-order context: invoked by `Calculator.calc_all` after
`ChildDepTaxCredit` (which produces `c07220` and `odc`) and the
other per-credit source functions (`F2441` -> `c07180`,
`EducationTaxCredit` -> `c07230`, `SchR` -> `c07200`,
`CharityCredit` -> `charity_credit`, `PersonalTaxCredit` ->
`personal_nonrefundable_credit`), and before `AdditionalCTC` /
`C1040`.

Parameters
----------
c05800: float
    Total (regular + AMT) income tax liability before credits
    (Form 1040 line 18)
e07240: float
    Retirement savings contributions credit input from Form 8880
    (Sch 3 line 4); haircut `(1 - CR_RetirementSavings_hc)`
    applied here
e07260: float
    Residential clean energy credit input from Form 5695 line 15
    (Sch 3 line 5a); haircut `(1 - CR_ResidentialEnergy_hc)`
    applied here
e07300: float
    Foreign tax credit input from Form 1116 (Sch 3 line 1);
    haircut `(1 - CR_ForeignTax_hc)` applied here
e07400: float
    General business credit input from Form 3800 (Sch 3 line 6a);
    haircut `(1 - CR_GeneralBusiness_hc)` applied here
e07600: float
    Prior-year minimum tax credit input from Form 8801
    (Sch 3 line 6b); haircut `(1 - CR_MinimumTax_hc)` applied
    here
p08000: float
    Other nonrefundable credits input (Sch 3 line 6z); haircut
    `(1 - CR_OtherCredits_hc)` applied here
odc: float
    Credit for Other Dependents from Sch 8812 (Form 1040 line 19
    ODC component); pre-computed with `CTC_hc` already applied
personal_nonrefundable_credit: float
    Reform-only personal nonrefundable credit from
    `PersonalTaxCredit`; current-law inert
CTC_is_refundable: bool
    Reform-only switch (default false): when true, CTC is not
    limited here and is routed to the refundable side in
    `IITAX` / `CTC_new`
ODC_is_refundable: bool
    Reform-only switch (default false): when true, ODC is not
    limited here and is routed to the refundable side in `IITAX`
CR_RetirementSavings_hc: float
    Retirement savings credit haircut (default 0.0; current-law
    inert)
CR_ForeignTax_hc: float
    Foreign tax credit haircut (default 0.0)
CR_ResidentialEnergy_hc: float
    Residential clean energy credit haircut (default 0.0)
CR_GeneralBusiness_hc: float
    General business credit haircut (default 0.0)
CR_MinimumTax_hc: float
    Prior-year minimum tax credit haircut (default 0.0)
CR_OtherCredits_hc: float
    Other nonrefundable credits haircut (default 0.0)
charity_credit: float
    Reform-only nonrefundable charity credit from `CharityCredit`;
    current-law inert
c07180: float
    Credit for child and dependent care expenses from Form 2441
    (Sch 3 line 2); pre-computed by `F2441`
c07200: float
    Schedule R credit for the elderly and the disabled
    (Sch 3 line 6d); pre-computed by `SchR`
c07220: float
    Child tax credit from Sch 8812 (Form 1040 line 19 CTC
    component); pre-computed by `ChildDepTaxCredit`
c07230: float
    Nonrefundable education credit from Form 8863
    (Sch 3 line 3); pre-computed by `EducationTaxCredit`
c07240: float
    Retirement savings credit limited output (overwritten here)
c07260: float
    Residential clean energy credit limited output (overwritten
    here)
c07300: float
    Foreign tax credit limited output (overwritten here)
c07400: float
    General business credit limited output (overwritten here)
c07600: float
    Prior-year minimum tax credit limited output (overwritten
    here)
c08000: float
    Other nonrefundable credits limited output (overwritten here)

Returns
-------
c07180: float
    Limited credit for child and dependent care expenses
    (Sch 3 line 2)
c07200: float
    Limited Schedule R credit (Sch 3 line 6d)
c07220: float
    Limited child tax credit (Form 1040 line 19 CTC component);
    unchanged when `CTC_is_refundable`
c07230: float
    Limited nonrefundable education credit (Sch 3 line 3)
c07240: float
    Limited retirement savings credit (Sch 3 line 4)
odc: float
    Limited Credit for Other Dependents (Form 1040 line 19 ODC
    component); unchanged when `ODC_is_refundable`
c07260: float
    Limited residential clean energy credit (Sch 3 line 5a)
c07300: float
    Limited foreign tax credit (Sch 3 line 1)
c07400: float
    Limited general business credit (Sch 3 line 6a)
c07600: float
    Limited prior-year minimum tax credit (Sch 3 line 6b)
c08000: float
    Limited other nonrefundable credits (Sch 3 line 6z)
charity_credit: float
    Limited reform-only nonrefundable charity credit
personal_nonrefundable_credit: float
    Limited reform-only personal nonrefundable credit
```

## AdditionalCTC

```python
def AdditionalCTC(actc_claim_prob_min, actc_claim_prob_scale, credit_claim_urn, codtc_limited, ACTC_c, n24, earned, ACTC_Income_thd, ACTC_rt, nu06, ACTC_rt_bonus_under6family, ACTC_ChildNum, CTC_is_refundable, CTC_include17, CTC_c, age_head, age_spouse, MARS, nu18, ptax_was, c03260, e09800, c59660, e11200, c11070)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/calcfunctions.py#L4275)

```text
Calculates refundable Additional Child Tax Credit (ACTC), c11070,
following Schedule 8812 Part II (Parts II-A, II-B, II-C).

Parameters
----------
actc_claim_prob_min: float
    See logic and comments at bottom of function (no form analogue)
actc_claim_prob_scale: float
    See logic and comments at bottom of function (no form analogue)
credit_claim_urn: float
    See logic and comments at bottom of function (no form analogue)
codtc_limited: float
    Sch 8812 line 16a: Part I tentative credit minus the nonrefundable
    portion absorbed (line 12 minus line 14); set in ChildDepTaxCredit
ACTC_c: float
    Maximum refundable additional child tax credit
n24: int
    Number of children who are Child-Tax-Credit eligible, one condition
    for which is being under age 17
earned: float
    Earned income for filing unit
ACTC_Income_thd: float
    Additional Child Tax Credit income threshold
ACTC_rt: float
    Additional Child Tax Credit rate
nu06: int
    Number of dependents under 6 years old
ACTC_rt_bonus_under6family: float
    Bonus additional child tax credit rate for families with qualifying
    children under 6 (reform-only; no form correspondence)
ACTC_ChildNum: float
    Additional Child Tax Credit minimum number of qualified children for
    different formula
ptax_was: float
    Employee and employer OASDI plus HI FICA tax
c03260: float
    Self-employment tax deduction (after haircut)
e09800: float
    Unreported payroll taxes from Form 4137 or 8919
c59660: float
    EITC amount
e11200: float
    Excess payroll (FICA/RRTA) tax withheld
c11070: float
    Child tax credit (refunded) from Form 8812

Returns
-------
c11070: float
    Child tax credit (refunded) from Form 8812
```

## C1040

```python
def C1040(c05800, c07180, c07200, c07220, c07230, c07240, c07260, c07300, c07400, c07600, c08000, e09700, e09800, e09900, niit, setax, ptax_amc, othertaxes, c07100, c09200, odc, charity_credit, personal_nonrefundable_credit, CTC_is_refundable, ODC_is_refundable)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/calcfunctions.py#L4401)

```text
Assembles Form 1040 (2025) lines 22-24 + Schedule 2 (2025) Part II
line 21:
  * `c07100` = Form 1040 line 21 = total nonrefundable credits used
    (Sch 3 line 8 + Form 1040 line 19 CTC + ODC components),
    re-summed here from the per-credit limited amounts produced by
    `NonrefundableCredits` and `ChildDepTaxCredit`.
  * `othertaxes` = Sch 2 line 21 = Form 1040 line 23, the sum of
    the six modeled "Other Taxes" items.
  * `c09200` = Form 1040 line 24 = line 22 + line 23, total tax
    before refundable credits and withholding (which are payments,
    not taxes, and are applied later by `IITAX`).
https://www.irs.gov/pub/irs-pdf/f1040s2.pdf

Schedule 2 Part II line 21 = line 4 + (lines 7-16) + line 18 +
line 19.  Modeled items:
  * line 4  -- Self-employment tax (Schedule SE)               <- setax
  * line 7  -- Total addl SS/Medicare tax (Forms 4137 + 8919)  <- e09800
  * line 8  -- Addl tax on IRAs/other tax-favored accts        <- e09900
  * line 11 -- Additional Medicare Tax (Form 8959)             <- ptax_amc
  * line 12 -- Net Investment Income Tax (Form 8960)           <- niit
  * line 18 -- Total addl taxes (only line 17a recapture of
               investment credit modeled)                       <- e09700
Unmodeled Sch 2 Part II items: line 9 (household employment
taxes, Sch H); lines 13-16 (uncollected SS/Medicare on tips,
interest on installment-sale deferred tax, low-income housing
recapture); the rest of line 17 (HSA/MSA, NQDC, golden parachute,
Form 4255 EPE, etc.); line 19 (recapture of net EPE); line 20
(sec 965 installment).

Schedule 2 Part I (line 1z additions to tax + line 2 AMT) is
folded into the input `c05800` only via line 2 (AMT, produced by
`AMT`); Part I additions (premium-tax-credit repayment, clean
vehicle credit repayments, Form 4255 EPE additions) are
unmodeled, so c05800 ~= Form 1040 line 16 + Sch 2 line 2 ~= Form
1040 line 18.

Reform-only knobs:
  * `CTC_is_refundable` -- when true, CTC (`c07220`) is excluded
    from `c07100` here and `NonrefundableCredits` skips CTC
    capping; CTC is routed to the refundable side via `CTC_new`
    / `IITAX`.
  * `ODC_is_refundable` -- when true, ODC (`odc`) is excluded
    from `c07100` here and `NonrefundableCredits` skips ODC
    capping; ODC is routed to the refundable side via `IITAX`.

Calling order (calculator.py): invoked after `NonrefundableCredits`
and `AdditionalCTC` (so each per-credit input has had its final
Sch 3 / Sch 8812 cap applied) and before `CTC_new` / `IITAX`
(which subtract refundable credits from `c09200`).

Parameters
----------
c05800: float
    Total (regular + AMT) income tax liability before credits
    (Form 1040 line 16 + Sch 2 line 2; approximates Form 1040
    line 18 since Sch 2 line 1z additions are unmodeled)
c07180: float
    Limited credit for child and dependent care expenses from
    Form 2441 (Sch 3 line 2)
c07200: float
    Limited Schedule R credit for the elderly and the disabled
    (Sch 3 line 6d)
c07220: float
    Limited child tax credit from Sch 8812 (Form 1040 line 19
    CTC component); excluded from `c07100` when
    `CTC_is_refundable`
c07230: float
    Limited nonrefundable education credit from Form 8863
    (Sch 3 line 3)
c07240: float
    Limited retirement savings credit from Form 8880
    (Sch 3 line 4)
c07260: float
    Limited residential clean energy credit from Form 5695
    (Sch 3 line 5a)
c07300: float
    Limited foreign tax credit from Form 1116 (Sch 3 line 1)
c07400: float
    Limited general business credit from Form 3800
    (Sch 3 line 6a)
c07600: float
    Limited prior-year minimum tax credit from Form 8801
    (Sch 3 line 6b)
c08000: float
    Limited other nonrefundable credits (Sch 3 line 6z)
e09700: float
    Recapture of Investment Credit (Sch 2 line 17a, the only
    modeled component of Sch 2 line 18)
e09800: float
    Unreported payroll taxes from Form 4137 + Form 8919
    (Sch 2 lines 5 + 6 -> Sch 2 line 7)
e09900: float
    Additional tax on IRAs / other tax-favored accounts from
    Form 5329 (Sch 2 line 8)
niit: float
    Net Investment Income Tax from Form 8960 (Sch 2 line 12)
setax: float
    Self-employment tax from Schedule SE (Sch 2 line 4)
ptax_amc: float
    Additional Medicare Tax from Form 8959 (Sch 2 line 11)
othertaxes: float
    Records-bound output: Schedule 2 line 21 / Form 1040 line 23
    (overwritten here)
c07100: float
    Records-bound output: total nonrefundable credits used,
    Form 1040 line 21 (overwritten here)
c09200: float
    Records-bound output: total tax before refundable credits,
    Form 1040 line 24 (overwritten here)
odc: float
    Limited Credit for Other Dependents from Sch 8812 (Form 1040
    line 19 ODC component); excluded from `c07100` when
    `ODC_is_refundable`
charity_credit: float
    Reform-only nonrefundable charity credit (current-law inert)
personal_nonrefundable_credit: float
    Reform-only personal nonrefundable credit (current-law inert)
CTC_is_refundable: bool
    Reform-only switch (default false): when true, CTC is routed
    to the refundable side rather than included in `c07100`
ODC_is_refundable: bool
    Reform-only switch (default false): when true, ODC is routed
    to the refundable side rather than included in `c07100`

Returns
-------
c07100: float
    Total nonrefundable credits used (Form 1040 line 21)
othertaxes: float
    Sum of the six modeled Sch 2 Part II line 21 components
    (setax, e09800, e09900, ptax_amc, niit, e09700) = Form 1040
    line 23
c09200: float
    Total tax before refundable credits = Form 1040 line 24
    = line 22 + line 23
```

## CTC_new

```python
def CTC_new(CTC_new_c, CTC_new_rt, CTC_new_c_under6_bonus, CTC_new_ps, CTC_new_prt, CTC_new_for_all, CTC_include17, CTC_new_refund_limited, CTC_new_refund_limit_payroll_rt, CTC_new_refund_limited_all_payroll, payrolltax, exact, CTC_c, CTC_c_under6_bonus, CTC_ps, CTC_prt, ODC_c, n24, nu06, age_head, age_spouse, nu18, XTOT, num, c00100, MARS, ptax_oasdi, c09200, ctc_new)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/calcfunctions.py#L4579)

```text
Computes a reform-construct refundable Child Tax Credit (`ctc_new`)
that is added on top of, not in place of, the current-law CTC/ODC
machinery in `ChildDepTaxCredit` and `AdditionalCTC`.

No IRS form: this credit does not correspond to any current-law
Form 1040 / Schedule 8812 line. All `CTC_new_*` policy parameters
default to 0 / false for all years except 2021, where defaults emulate
the ARPA-2021 expanded CTC (`CTC_new_c=1000`, `CTC_new_c_under6_bonus=600`,
`CTC_new_for_all=true`, `CTC_new_ps={75k single / 150k MFJ / 75k MFS /
112.5k HoH / 150k widow}`, `CTC_new_prt=0.05`). Under 2025 current law
every parameter is 0/false, so `ctc_new` is identically zero.

Body sections:
  (A) qualifying-child count: `n24`, optionally widened via
      `CTC_include17` to count under-18 non-`n24` dependents (same
      block as in `ChildDepTaxCredit` row 29).
  (B) tentative credit: `CTC_new_c·childnum + CTC_new_c_under6_bonus·nu06`,
      optionally capped at `CTC_new_rt·posagi` when `CTC_new_for_all=false`
      (an AGI-based phase-in).
  (C) AGI phase-out: reduction of `CTC_new_prt` per dollar of AGI above
      `CTC_new_ps[MARS-1]`, with `exact==1` rounding excess up to the
      next $1000 (mirrors the Sch 8812 line-9 step).  When
      `CTC_new_prt > 0` and `CTC_new_ps[MARS-1] < CTC_ps[MARS-1]` (the
      ARPA-style structure), the reduction is capped at
      `CTC_new_prt·(CTC_ps[MARS-1] - CTC_new_ps[MARS-1])`, as in IRC
      section 24(i)(4)(B) (2021 Sch 8812 Line 5 Worksheet).
  (C2) combined-credit phase-out, only under the ARPA-style structure
      defined in (C): above `CTC_ps[MARS-1]` the `CTC_prt`
      reduction applies to the sum of the tentative CTC, ODC, and
      `ctc_new` (2021 Sch 8812 lines 8-12); the part of that reduction
      not absorbed by the tentative CTC and ODC in `ChildDepTaxCredit`
      reduces `ctc_new`.
  (D) reform-only payroll-tax refundability cap: when
      `CTC_new_refund_limited=true`, the portion of `ctc_new` exceeding
      pre-refundable-credits liability `c09200` is capped at
      `CTC_new_refund_limit_payroll_rt` times either OASDI-only
      (`ptax_oasdi`) or all-FICA (`payrolltax`) payroll tax depending
      on `CTC_new_refund_limited_all_payroll`.

Calling order: runs after `C1040` (so `c09200`, `ptax_oasdi`, and
`payrolltax` are final) and immediately before `IITAX`, which
subtracts `ctc_new` on the refundable side and rolls it into the
`ctc_total` / `ctc_refundable` records-bound aggregates.

Parameters
----------
CTC_new_c: float
    Reform: maximum new refundable CTC per qualifying child.
CTC_new_rt: float
    Reform: AGI phase-in rate when `CTC_new_for_all=false`.
CTC_new_c_under6_bonus: float
    Reform: bonus added to `CTC_new_c` for each under-6 dependent.
CTC_new_ps: list
    Reform: MARS-indexed AGI threshold at which the phase-out begins.
CTC_new_prt: float
    Reform: phase-out reduction rate per dollar of AGI above
    `CTC_new_ps[MARS-1]`.
CTC_new_for_all: bool
    Reform: when true, full `CTC_new_c·childnum + ...` is available
    regardless of AGI (no `CTC_new_rt` phase-in); when false the
    tentative credit is capped at `CTC_new_rt·posagi`.
CTC_include17: bool
    Reform: when true, dependents with `age < 18` not already in `n24`
    are added to `childnum` (same widening used in `ChildDepTaxCredit`).
CTC_new_refund_limited: bool
    Reform: when true, the refund portion (excess of `ctc_new` over
    `c09200`) is capped via the payroll-tax limit below.
CTC_new_refund_limit_payroll_rt: float
    Reform: payroll-tax-share cap on the refund portion of `ctc_new`.
CTC_new_refund_limited_all_payroll: bool
    Reform: when true, the payroll cap applies to total FICA
    (`payrolltax`); when false it applies to OASDI only (`ptax_oasdi`).
payrolltax: float
    Total (employee + employer) FICA payroll tax liability.
exact: int
    When 1, round the phase-out excess up to the next $1000 (Sch 8812
    line-9 step); when 0, use the smooth excess.
CTC_c: float
    Maximum nonrefundable CTC per qualifying child; used to compute the
    tentative CTC in section (C2).
CTC_c_under6_bonus: float
    Bonus CTC amount for each under-6 dependent; used in section (C2).
CTC_ps: list
    MARS-indexed AGI threshold of the `ChildDepTaxCredit` phase-out;
    caps the section (C) reduction and starts section (C2).
CTC_prt: float
    `ChildDepTaxCredit` phase-out rate; used in section (C2).
ODC_c: float
    Maximum credit per other dependent; used in section (C2).
n24: int
    Number of CTC-eligible children (a condition for which is being
    under age 17).
nu06: int
    Number of dependents under 6 years old.
age_head: int
    Age of taxpayer (filer); used by the `CTC_include17` widening.
age_spouse: int
    Age of spouse (or 0 if not MFJ); used by the `CTC_include17` widening.
nu18: int
    Number of dependents under 18 years old; used by the
    `CTC_include17` widening.
XTOT: int
    Total number of exemptions for filing unit; used to count other
    dependents in section (C2).
num: int
    2 when MARS is 2 (married filing jointly), otherwise 1.
c00100: float
    Adjusted Gross Income (AGI); floored at 0 as `posagi`.
MARS: int
    Filing status (1=single, 2=MFJ, 3=MFS, 4=HoH, 5=widow(er)).
ptax_oasdi: float
    Employee + employer OASDI FICA plus SE tax (excludes HI FICA).
c09200: float
    Total income tax (including other taxes) after nonrefundable
    credits, before refundable credits.
ctc_new: float
    Records-bound output, computed below.

Returns
-------
ctc_new: float
    Reform-only new refundable child tax credit; fed into `IITAX` on
    the refundable side.
```

## IITAX

```python
def IITAX(c59660, c11070, c10960, personal_refundable_credit, ctc_new, c09200, CDCC_refund, recovery_rebate_credit, eitc, c07220, odc, CTC_is_refundable, ODC_is_refundable, soi_iitax, setax, e09800, ptax_amc, refund, ctc_total, ctc_refundable, ctc_nonrefundable, iitax, payrolltax, combined)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/calcfunctions.py#L4767)

```text
Final assembly: sums refundable credits and computes total income-tax
liability net of those credits. Maps to Form 1040 (2025) lines 22-37
with two model-specific simplifications:

  (1) `refund` here is the analogue of Form 1040 line 32 (refundable-
      credit sum) ONLY. Lines 25d (federal income tax withheld) and 26
      (estimated tax payments) are not modeled by Tax-Calculator, so
      line 33 = 25d + 26 + 32 reduces to line 32 in the model.
  (2) `iitax` = c09200 - refund = Form 1040 line 24 - line 32. The
      model does not split this into line 34 (refund when 33 > 24) vs.
      line 37 (owed when 24 > 33); `iitax` is sign-permissive (positive
      = amount owed, negative = refund position).

Body sections:

  (A) Reform-only refundable conversions. When `CTC_is_refundable` or
      `ODC_is_refundable` are true (both default false under current
      law), the CTC (c07220) and ODC (odc) amounts that were applied
      as nonrefundable credits in `NonrefundableCredits` / `C1040` are
      added on the refundable side here.
  (B) Form 1040 line 32 build. Each addend is annotated with its 1040
      line (27a EIC / 28 ACTC / 29 AOC / 30 historical RRC / 31 Sch 3
      line 13 refundable CDCC) or reform-only label (no form line).
  (C) Records-bound CTC diagnostic. `ctc_total` / `ctc_refundable` /
      `ctc_nonrefundable` summarize the union of `ChildDepTaxCredit`
      (c07220 nonref + odc), `AdditionalCTC` (c11070 refundable), and
      `CTC_new` (reform-only) — partitioned by whether each piece is
      refundable under the current parameter regime. Not on the form.
  (D) Form 1040 line 24 − line 32 net + combined-tax accumulator.
      `combined` = iitax + payrolltax; `lumpsum_tax` is added later
      by `LumpSumTax` (also a reform construct, inert under current
      law).  The `soi_iitax` switch determines whether the three
      employment-related "other taxes" already folded into `c09200`
      by `C1040` (`setax`, `e09800`, `ptax_amc`) stay in `iitax`
      (true, SOI/IRS concept) or are shifted from `iitax` to
      `payrolltax` (false, tax-analysis concept).  `c09200` itself
      is not changed; only the final bucketing between the two tax
      totals is.

Reform constructs (no Form 1040 (2025) line):
  `personal_refundable_credit` (II_credit* knobs from
  `PersonalTaxCredit`), `ctc_new` (from `CTC_new`), and the
  `recovery_rebate_credit` (historically Form 1040 line 30
  for 2020 CARES / 2021 ARPA RRC; inert for 2022+).

Calling order: invoked by `Calculator._calc_one_year` after `CTC_new`
(so c09200, c07220, odc, c10960, c11070, c59660, CDCC_refund are all
final) and before `FairShareTax` / `LumpSumTax` / `BenefitPrograms`.

Parameters
----------
c59660: float
    EITC amount from EITC function (Form 1040 line 27a)
c11070: float
    Refundable Additional CTC from AdditionalCTC / Schedule 8812
    Part II (Form 1040 line 28)
c10960: float
    American Opportunity Credit refundable portion from
    EducationTaxCredit / Form 8863 line 8 (Form 1040 line 29)
personal_refundable_credit: float
    Reform-only refundable personal credit from `PersonalTaxCredit`
    (no Form 1040 line; default 0 under current law)
ctc_new: float
    Reform-only new refundable child tax credit from `CTC_new`
    (no Form 1040 line; default 0 under current law)
c09200: float
    Total income tax (including other taxes, after nonrefundable
    credits) from `C1040` (Form 1040 line 24)
CDCC_refund: float
    Refundable portion of Child and Dependent Care Credit from
    `CDCC_refundable` (Schedule 3 line 13 → Form 1040 line 31)
recovery_rebate_credit: float
    Recovery Rebate Credit from `PersonalTaxCredit` (historical
    Form 1040 line 30 for 2020/2021; inert for 2022+ under
    current law)
eitc: float
    Records-bound output; rebound to `c59660` here
c07220: float
    Nonrefundable CTC (post-NonrefundableCredits cap) from
    `ChildDepTaxCredit` / Schedule 8812 Credit Limit Worksheet A
odc: float
    Nonrefundable Credit for Other Dependents (post-cap) from
    `ChildDepTaxCredit` / Schedule 8812
CTC_is_refundable: bool
    Reform-only switch (default false): when true, the entire CTC is
    treated as refundable (Schedule 8812 nonref portion `c07220` is
    added to `refund` here)
ODC_is_refundable: bool
    Reform-only switch (default false): when true, ODC is treated as
    refundable (`odc` is added to `refund` here)
soi_iitax: bool
    Bucketing switch: when true, `setax`, `e09800`, and `ptax_amc`
    remain in `iitax` via `c09200` (SOI/IRS concept, matching the
    Form 1040 / Schedule 2 layout); when false, they are shifted
    from `iitax` to `payrolltax` (tax-analysis concept).  Does not
    change `c09200` or `othertaxes`.
setax: float
    Self-employment tax (Sch 2 line 4) from `EI_PayrollTax`; shifted
    out of `iitax` and into `payrolltax` when `soi_iitax` is false
e09800: float
    Unreported payroll taxes (Sch 2 line 7) from Forms 4137 + 8919;
    shifted out of `iitax` and into `payrolltax` when `soi_iitax`
    is false
ptax_amc: float
    Additional Medicare Tax (Sch 2 line 11) from Form 8959; shifted
    out of `iitax` and into `payrolltax` when `soi_iitax` is false
refund: float
    Records-bound output (re-computed)
ctc_total: float
    Records-bound output (re-computed)
ctc_refundable: float
    Records-bound output (re-computed)
ctc_nonrefundable: float
    Records-bound output (re-computed)
iitax: float
    Records-bound output (re-computed)
payrolltax: float
    Total (employee + employer) payroll tax liability from
    `EI_PayrollTax`; re-computed here when `soi_iitax` is false to
    absorb `setax + e09800 + ptax_amc` from `iitax`
combined: float
    Records-bound output (re-computed)

Returns
-------
eitc: float
    Earned Income Credit (= c59660; Form 1040 line 27a)
refund: float
    Sum of refundable credits (model-specific Form 1040 line 32
    analogue; lines 25d and 26 not modeled)
ctc_total: float
    Diagnostic: c07220 + c11070 + odc + ctc_new
ctc_refundable: float
    Diagnostic: portion of ctc_total that is refundable
ctc_nonrefundable: float
    Diagnostic: max(0, ctc_total - ctc_refundable)
iitax: float
    Total federal individual income tax liability.  Equals
    c09200 − refund when `soi_iitax` is true (SOI/IRS concept);
    equals (c09200 − setax − e09800 − ptax_amc) − refund when
    false (fiscal-analysis concept).  Sign-permissive: positive
    = amount owed, negative = refund position; model does not
    split into Form 1040 lines 34 vs 37.
payrolltax: float
    Final payroll tax: unchanged from input when `soi_iitax` is
    true; equals input + (setax + e09800 + ptax_amc) when false
combined: float
    iitax + payrolltax (lumpsum_tax added later by `LumpSumTax`);
    invariant under `soi_iitax` by construction
```

## FairShareTax

```python
def FairShareTax(c00100, MARS, ptax_was, ptax_er_p, ptax_er_s, setax, ptax_amc, FST_AGI_trt, FST_AGI_thd_lo, FST_AGI_thd_hi, fstax, iitax, combined, surtax)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/calcfunctions.py#L4967)

```text
Computes Fair Share Tax (aka "Buffett Rule") — a reform-only minimum
tax on high-AGI filers. No IRS form correspondence: the construct
models the 2012 Paying a Fair Share Act / Buffett Rule proposal,
which was never enacted. Inert under current law because the rate
parameter `FST_AGI_trt` defaults to 0.0 for all years 2013+.

Mechanics (when active under reform):
  tentative = c00100 * FST_AGI_trt - iitax - employee_share
  where employee_share = (ptax_was - ptax_er_p - ptax_er_s)
                          + 0.5*setax + ptax_amc
  and `ptax_er_p`/`ptax_er_s` are the taxpayer and spouse employer
  shares of OASDI+HI FICA on wages, so the first term uses the
  actual employee/employer rate split rather than assuming a
  50/50 split.  Adding back half of
  SECA and the employee-paid Additional Medicare Tax gives the full
  worker-borne share, credited against the minimum to avoid
  double-counting payroll already paid.
The tentative amount is floored at 0, then linearly phased in
between `FST_AGI_thd_lo` and `FST_AGI_thd_hi` (MARS-indexed),
fully imposed at or above the high threshold.

The resulting `fstax` is added to three running accumulators:
`iitax` (income-tax total flowing to Form 1040 line 24),
`combined` (iitax + payrolltax + lumpsum_tax), and `surtax`
(records-bound diagnostic also incremented by `AGIsurtax`; see
row 18). Called by `Calculator.calc_all` after `_calc_one_year`
finishes, so `iitax`, `ptax_was`, `ptax_er_p`, `ptax_er_s`, `setax`,
and `ptax_amc` are already final. Because the employer-share
variables cover wages only — matching `ptax_was` — the employee-share
arithmetic here is invariant under the `soi_iitax` bucketing switch.

Parameters
----------
c00100: float
    Adjusted Gross Income (AGI)
MARS: int
    Filing (marital) status. (1=single, 2=joint, 3=separate,
                              4=household-head, 5=widow(er))
ptax_was: float
    Employee and employer OASDI plus HI FICA tax on wages and
    salaries (`EI_PayrollTax` output; never mutated afterward)
ptax_er_p: float
    Taxpayer's employer share of payrolltax on wages and salaries
    (`EI_PayrollTax` output; never mutated afterward)
ptax_er_s: float
    Spouse's employer share of payrolltax on wages and salaries
    (`EI_PayrollTax` output; never mutated afterward)
setax: float
    Self-employment tax (`EI_PayrollTax` output)
ptax_amc: float
    Additional Medicare Tax (`AdditionalMedicareTax` output)
FST_AGI_trt: float
    Reform-only minimum-tax rate applied to AGI (default 0.0 →
    function inert)
FST_AGI_thd_lo: list
    MARS-indexed AGI floor below which no minimum tax is imposed
FST_AGI_thd_hi: list
    MARS-indexed AGI level at which the minimum tax is fully
    phased in; equal to `FST_AGI_thd_lo` disables the phase-in
fstax: float
    Records-bound output: Fair Share Tax amount
iitax: float
    Records-bound accumulator: total federal income tax liability
combined: float
    Records-bound accumulator: iitax + payrolltax + lumpsum_tax
surtax: float
    Records-bound accumulator: diagnostic surtax total (also
    incremented by `AGIsurtax`)

Returns
-------
fstax: float
    Fair Share Tax amount
iitax: float
    Total federal individual income tax liability
combined: float
    Sum of iitax and payrolltax and lumpsum_tax
surtax: float
    Individual income tax subtotal augmented by fstax
```

## LumpSumTax

```python
def LumpSumTax(DSI, num, XTOT, LST, lumpsum_tax, combined)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/calcfunctions.py#L5074)

```text
Computes a per-capita lump-sum ("head") tax and adds it to combined taxes.

No IRS form correspondence: ``LST`` is a reform construct (section
"Surtaxes / Lump-Sum Tax" in ``policy_current_law.json``) and defaults
to 0.0 from 2013 onward, so this function is inert under current law.

When active, every member of a non-dependent filing unit pays ``LST``
dollars; filing units claimed as dependents elsewhere (``DSI == 1``)
are exempt. The head count is ``max(num, XTOT)``: ``num`` is 2 for MFJ
and 1 otherwise, which floors the count at the number of filers when
``XTOT`` is unusually low. The resulting tax is added only to
``combined`` (not to ``iitax`` or ``payrolltax``).

Parameters
----------
DSI: int
    1 if claimed as dependent on another return, otherwise 0
num: int
    2 when MARS is 2 (married filing jointly); otherwise 1
XTOT: int
    Total number of exemptions for filing unit
LST: float
    Dollar amount of lump-sum tax (reform parameter; 0.0 under current law)
lumpsum_tax: float
    Lumpsum (or head) tax
combined: float
    Sum of iitax and payrolltax and lumpsum_tax

Returns
-------
lumpsum_tax: float
    Lumpsum (or head) tax
combined: float
    Sum of iitax and payrolltax and lumpsum_tax
```

## ExpandIncome

```python
def ExpandIncome(e00200, pencon_p, pencon_s, e00300, e00400, e00600, e00700, e00800, e00900, e01100, e01200, e01400, e01500, e02000, e02100, p22250, p23250, cmbtp, ptax_er_p, ptax_er_s, benefit_value_total, expanded_income)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/calcfunctions.py#L5122)

```text
Computes the records-bound `expanded_income` aggregate — a broad
pre-tax income measure used for distributional analysis. This is a
model-internal concept with no IRS form/schedule counterpart: it is
not part of the tax-liability path and feeds only `AfterTaxIncome`
(and downstream distributional tables).

Relative to AGI (`c00100`), `expanded_income` differs by:
  + adding tax-exempt interest (`e00400`),
  + adding back DC pension contributions (`pencon_p`, `pencon_s`),
    so wage compensation enters gross rather than net of pension
    deferrals already removed from `e00200`,
  + adding the employer share of FICA on wages (`ptax_er_p` plus
    `ptax_er_s`),
  + adding non-AGI AMT preference items (`cmbtp`, from Form 6251),
  + adding the consumption value of transfer benefits
    (`benefit_value_total`, from `BenefitPrograms`),
  − but NOT subtracting Sch 1 Part II above-the-line adjustments
    (`c02900`); Sch C / Sch E / Sch F enter gross of those.
Sch C / Sch E / Sch F / Sch D / Form 4797 items enter at their
statutory net (income net of losses), so capital losses and
business losses reduce `expanded_income`.

Body is organized into seven groups (A)-(G), summed in this order
to preserve floating-point bit-exactness with the prior
implementation. The categories are commentary only; no
parenthesized subtotals are introduced.

Calling order: `calculator.calc_all` invokes `ExpandIncome` after
`BenefitPrograms` (which produces `benefit_value_total`) and after
`_calc_one_year` / `FairShareTax` / `LumpSumTax`; it precedes
`AfterTaxIncome`, which subtracts the `combined` total tax to
produce `aftertax_income`. The employer-share add-on covers wages
only, not self-employment income (which enters `expanded_income`
gross, via `e00900`/`e02000`, with no employer-side gross-up), and
is therefore invariant under the `soi_iitax` bucketing switch.

Parameters
----------
e00200: float
  Wages, salaries, tips/otime for filing unit net of pension contributions
pencon_p: float
  Contributions to defined-contribution pension plans for taxpayer
pencon_s: float
  Contributions to defined-contribution pension plans for spouse
e00300: float
  Taxable interest income
e00400: float
  Tax-exempt interest income (not in AGI; expanded-income add-on)
e00600: float
  Ordinary dividends included in AGI
e00700: float
  Taxable refunds of state and local income taxes
e00800: float
  Alimony received
e00900: float
  Schedule C business net profit/loss for filing unit
e01100: float
  Capital gain distributions not reported on Schedule D
e01200: float
  Other net gain/loss from Form 4797
e01400: float
  Taxable IRA distributions
e01500: float
  Total pensions and annuities
e02000: float
  Schedule E total rental, royalty, partnership, S-corporation,
  etc, income/loss
e02100: float
  Farm net income/loss for filing unit from Schedule F
p22250: float
  Schedule D net short term capital gains/losses
p23250: float
  Schedule D net long term capital gains/losses
cmbtp: float
  Estimate of income on (AMT) Form 6251 but not in AGI
ptax_er_p: float
  Taxpayer's employer share of payrolltax on wages and salaries
  (from `EI_PayrollTax`), added here as employer-side compensation
  not present in `e00200`.
ptax_er_s: float
  Spouse's employer share of payrolltax on wages and salaries
  (from `EI_PayrollTax`), added here as employer-side compensation
  not present in `e00200`.
benefit_value_total: float
  Consumption value of all benefits received by tax unit
  (from `BenefitPrograms`); included in expanded income.
expanded_income: float
  Records-bound output, computed below.

Returns
-------
expanded_income: float
  Broad pre-tax income measure (see body docstring above).
```

## AfterTaxIncome

```python
def AfterTaxIncome(combined, expanded_income, aftertax_income)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/calcfunctions.py#L5257)

```text
Computes the records-bound `aftertax_income` = `expanded_income`
− `combined`. This is a model-internal distributional-analysis
aggregate with no IRS form/schedule counterpart: it is not part
of the tax-liability path. The output can be negative (no floor
at zero) — e.g., when `combined` exceeds `expanded_income` for a
unit with large business/capital losses. Note that any refundable
credits have already been netted into `iitax` (and therefore into
`combined`) upstream.

Calling order: `Calculator.calc_all` invokes `AfterTaxIncome`
last, immediately after `ExpandIncome` (which produces
`expanded_income`) and after `LumpSumTax` (which finalizes
`combined` = `iitax` + `payrolltax` + `lumpsum_tax`). Downstream
consumers are distributional tables (`Calculator.decile_graph`,
`mtr_graph`) and the consumer-equivalent welfare calculation
`Calculator.ce_aftertax_income`.

Parameters
----------
combined: float
  Sum of `iitax` + `payrolltax` + `lumpsum_tax` for the filing
  unit (finalized in `LumpSumTax`).
expanded_income: float
  Broad pre-tax income measure including `benefit_value_total`
  (from `ExpandIncome`); see that function's docstring for the
  AGI-vs-expanded-income deltas.
aftertax_income: float
  Records-bound output, computed below.

Returns
-------
aftertax_income: float
  `expanded_income` − `combined`; can be negative.
```
