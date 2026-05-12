"""
Tax-Calculator functions that calculate payroll and individual income taxes.

These functions are imported into the Calculator class.

Note: the parameter_indexing_CPI_offset parameter is no longer used.
"""
# CODING-STYLE CHECKS:
# pycodestyle calcfunctions.py
# pylint --disable=locally-disabled calcfunctions.py
#
# pylint: disable=too-many-lines
# pylint: disable=invalid-name
# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments
# pylint: disable=too-many-locals

import math
import numpy as np
from taxcalc.decorators import iterate_jit, JIT


def BenefitPrograms(calc):
    """
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
    """
    # programs aggregated below, in a fixed order:
    #   (record_array_name, repeal_param_or_None, value_param_or_None)
    # repeal_param=None ==> program has no repeal flag (UBI only).
    # value_param=None  ==> cash benefit, valued at full dollar cost.
    programs = (
        ('housing_ben', 'BEN_housing_repeal', 'BEN_housing_value'),
        ('ssi_ben', 'BEN_ssi_repeal', None),
        ('snap_ben', 'BEN_snap_repeal', 'BEN_snap_value'),
        ('tanf_ben', 'BEN_tanf_repeal', 'BEN_tanf_value'),
        ('vet_ben', 'BEN_vet_repeal', 'BEN_vet_value'),
        ('wic_ben', 'BEN_wic_repeal', 'BEN_wic_value'),
        ('mcare_ben', 'BEN_mcare_repeal', 'BEN_mcare_value'),
        ('mcaid_ben', 'BEN_mcaid_repeal', 'BEN_mcaid_value'),
        ('e02400', 'BEN_oasdi_repeal', None),  # OASDI Social Security
        ('e02300', 'BEN_ui_repeal', None),  # Unemployment Insurance
        ('ubi', None, None),  # UBI reform construct
        ('other_ben', 'BEN_other_repeal', 'BEN_other_value'),
    )
    # zero out benefits delivered by repealed programs
    zero = np.zeros(calc.array_len)
    for name, repeal_param, _ in programs:
        if repeal_param is not None and calc.policy_param(repeal_param):
            calc.array(name, zero)
    # calculate government cost of all benefits
    cost = sum(calc.array(name) for name, _, _ in programs)
    calc.array('benefit_cost_total', cost)
    # calculate consumption value of all benefits
    # (cash benefits are valued at full dollar cost)
    value = sum(
        calc.array(name) if vparam is None
        else calc.array(name) * calc.consump_param(vparam)
        for name, _, vparam in programs
    )
    calc.array('benefit_value_total', value)


@iterate_jit(nopython=True)
def EI_PayrollTax(SS_Earnings_c, e00200p, e00200s, pencon_p, pencon_s,
                  FICA_ss_trt_employer, FICA_ss_trt_employee,
                  FICA_mc_trt_employer, FICA_mc_trt_employee,
                  ALD_SelfEmploymentTax_hc, SS_Earnings_thd, SECA_Earnings_thd,
                  e00900p, e00900s, e02100p, e02100s, k1bx14p,
                  k1bx14s, payrolltax, ptax_was, setax, c03260, ptax_oasdi,
                  sey, earned, earned_p, earned_s,
                  was_plus_sey_p, was_plus_sey_s):
    """
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
        Individual earnings above this threshold are subjected to
        OASDI payroll tax, in addtion to earnings below the
        maximum taxable earnings threshold.
    SECA_Earnings_thd: float
        Threshold value for self-employment income below which there is
        no SECA tax liability
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
    was_plus_sey_p: float
        Wage and salary income plus taxable self employment income for taxpayer
    was_plus_sey_s: float
        Wage and salary income plus taxable self employment income for spouse

    Returns
    -------
    sey: float
        Total self-employment income for filing unit
    payrolltax: float
        Total (employee and employer) payroll tax liability
        payrolltax = ptax_was
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
    was_plus_sey_p: float
        Wage and salary income plus taxable self employment income for taxpayer
    was_plus_sey_s: float
        Wage and salary income plus taxable self employment income for spouse
    """
    # combined OASDI and HI FICA rates (employer + employee shares)
    ss_rate = FICA_ss_trt_employer + FICA_ss_trt_employee
    mc_rate = FICA_mc_trt_employer + FICA_mc_trt_employee

    # compute sey and its individual components
    sey_p = e00900p + e02100p + k1bx14p
    sey_s = e00900s + e02100s + k1bx14s
    sey = sey_p + sey_s  # total self-employment income for filing unit

    # ---------- FICA on wages and salaries ----------
    # compute gross wage and salary income ('was' denotes 'wage and salary')
    gross_ws_p = e00200p + pencon_p
    gross_ws_s = e00200s + pencon_s

    # compute taxable gross earnings for OASDI FICA
    txearn_was_p = min(SS_Earnings_c, gross_ws_p)
    txearn_was_s = min(SS_Earnings_c, gross_ws_s)

    # compute OASDI and HI payroll taxes on wage-and-salary income
    ptax_ss_ws_p = ss_rate * txearn_was_p
    ptax_ss_ws_s = ss_rate * txearn_was_s
    ptax_mc_ws_p = mc_rate * gross_ws_p
    ptax_mc_ws_s = mc_rate * gross_ws_s
    ptax_was = ptax_ss_ws_p + ptax_ss_ws_s + ptax_mc_ws_p + ptax_mc_ws_s

    # ---------- SECA on self-employment income (Sch SE Part I) ----------
    # Sch SE line 4a multiplier 0.9235, generalized to current FICA rates
    seca_frac = 1.0 - 0.5 * (ss_rate + mc_rate)
    # Sch SE line 4c (taxable net SE earnings, per spouse)
    net_sey_p = max(0., sey_p * seca_frac)
    net_sey_s = max(0., sey_s * seca_frac)
    # Sch SE line 9: remaining OASDI base = SS_Earnings_c - W-2 SS wages
    txearn_sey_p = min(net_sey_p, SS_Earnings_c - txearn_was_p)
    txearn_sey_s = min(net_sey_s, SS_Earnings_c - txearn_was_s)
    # Sch SE line 10 (OASDI portion) and line 11 (HI portion), per spouse
    setax_ss_p = ss_rate * txearn_sey_p
    setax_ss_s = ss_rate * txearn_sey_s
    setax_mc_p = mc_rate * net_sey_p
    setax_mc_s = mc_rate * net_sey_s
    setax_p = setax_ss_p + setax_mc_p
    setax_s = setax_ss_s + setax_mc_s
    # Sch SE line 12: zero out if filing-unit SE earnings are below the
    # $400 floor (Sch SE line 4: "stop; you do not owe SE tax")
    if sey * seca_frac > SECA_Earnings_thd:
        setax = setax_p + setax_s
    else:
        setax = 0.0

    # ---------- Reform-only extra OASDI bracket (not on Sch SE) ----------
    # extra OASDI on the portion of (wages + taxable SE) above SS_Earnings_thd
    extra_frac = 1.0 - 0.5 * ss_rate
    was_plus_sey_p = gross_ws_p + max(0., sey_p * extra_frac)
    was_plus_sey_s = gross_ws_s + max(0., sey_s * extra_frac)
    extra_ss_income_p = max(0., was_plus_sey_p - SS_Earnings_thd)
    extra_ss_income_s = max(0., was_plus_sey_s - SS_Earnings_thd)
    extra_payrolltax = ss_rate * (extra_ss_income_p + extra_ss_income_s)

    # filing-unit payroll tax and OASDI-only part (HI excluded from ptax_oasdi)
    payrolltax = ptax_was + extra_payrolltax
    ptax_oasdi = (ptax_ss_ws_p + ptax_ss_ws_s +
                  setax_ss_p + setax_ss_s +
                  extra_payrolltax)

    # ---------- earned-income outputs and Sch SE line 13 deduction ----------
    # c03260: deductible half of SE tax (Sch SE line 13 / Sch 1 line 15),
    # optionally reduced by the ALD_SelfEmploymentTax_hc reform haircut
    c03260 = (1. - ALD_SelfEmploymentTax_hc) * 0.5 * setax
    earned = max(0., e00200p + e00200s + sey - c03260)
    earned_p = max(0., (e00200p + sey_p -
                        (1. - ALD_SelfEmploymentTax_hc) * 0.5 * setax_p))
    earned_s = max(0., (e00200s + sey_s -
                        (1. - ALD_SelfEmploymentTax_hc) * 0.5 * setax_s))
    return (sey, payrolltax, ptax_was, setax, c03260, ptax_oasdi,
            earned, earned_p, earned_s, was_plus_sey_p, was_plus_sey_s)


@iterate_jit(nopython=True)
def DependentCare(nu13, elderly_dependents, earned,
                  MARS, ALD_Dependents_thd, ALD_Dependents_hc,
                  ALD_Dependents_Child_c, ALD_Dependents_Elder_c,
                  care_deduction):
    """
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
    """
    earned_thd = ALD_Dependents_thd[MARS - 1]
    if earned <= earned_thd:
        hc_frac = 1. - ALD_Dependents_hc
        child_ded = hc_frac * nu13 * ALD_Dependents_Child_c
        elder_ded = hc_frac * elderly_dependents * ALD_Dependents_Elder_c
        care_deduction = child_ded + elder_ded
    else:
        care_deduction = 0.
    return care_deduction


@iterate_jit(nopython=True)
def Adj(e03220, e03290, c03260, e03300, e03270,
        e03400, e03500, e03150, e03210,
        e03230, e03240, care_deduction,
        ALD_EducatorExpenses_hc, ALD_HSADeduction_hc,
        ALD_KEOGH_SEP_hc, ALD_SelfEmp_HealthIns_hc,
        ALD_EarlyWithdraw_hc, ALD_AlimonyPaid_hc,
        ALD_IRAContributions_hc, ALD_StudentLoan_hc,
        ALD_Tuition_hc, ALD_DomesticProduction_hc,
        c02900):
    """
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
    """
    # Sch 1 Part II lines not modeled: line 12 (reservist/artist/fee-basis
    # gov-official biz expenses, Form 2106), line 14 (moving expenses for
    # Armed Forces, Form 3903), line 23 (Archer MSA), and lines 24a-24z /
    # 25 (other adjustments).
    c02900 = (
        (1. - ALD_EducatorExpenses_hc) * e03220 +    # Sch 1 line 11
        (1. - ALD_HSADeduction_hc) * e03290 +        # Sch 1 line 13
        c03260 +                                     # Sch 1 line 15
        (1. - ALD_KEOGH_SEP_hc) * e03300 +           # Sch 1 line 16
        (1. - ALD_SelfEmp_HealthIns_hc) * e03270 +   # Sch 1 line 17
        (1. - ALD_EarlyWithdraw_hc) * e03400 +       # Sch 1 line 18
        (1. - ALD_AlimonyPaid_hc) * e03500 +         # Sch 1 line 19a
        (1. - ALD_IRAContributions_hc) * e03150 +    # Sch 1 line 20
        (1. - ALD_StudentLoan_hc) * e03210 +         # Sch 1 line 21
        # legacy / reform-only items (zero under current law):
        (1. - ALD_Tuition_hc) * e03230 +             # ALD repealed post-2020
        (1. - ALD_DomesticProduction_hc) * e03240 +  # ALD expired post-2017
        care_deduction                               # ALD reform construct
    )
    return c02900


@iterate_jit(nopython=True)
def ALD_InvInc_ec_base(p22250, p23250,
                       e00300, e00600, e01100, e01200, MARS,
                       invinc_ec_base, Capital_loss_limitation):
    """
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
    """
    # Schedule D line 21 / IRC §1211(b): cap any net capital loss at the
    # MARS-indexed limit. Re-derived here (rather than reusing c01000)
    # because CapGainsLoss has not yet run; result equals c01000.
    cgain = max(
        (-1 * Capital_loss_limitation[MARS - 1]), p22250 + p23250
    )
    invinc_ec_base = e00300 + e00600 + cgain + e01100 + e01200
    return invinc_ec_base


@iterate_jit(nopython=True)
def CapGainsLoss(p22250, p23250, Capital_loss_limitation, MARS,
                 c23650, c01000):
    """
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
    """
    # Schedule D line 16: combine net short-term and net long-term
    c23650 = p23250 + p22250
    # Schedule D line 21: cap any net loss at MARS-indexed limit
    c01000 = max((-1 * Capital_loss_limitation[MARS - 1]), c23650)
    return (c23650, c01000)


@iterate_jit(nopython=True)
def AGIIncome(e00200, e00300, e00400, e00600, e00650, e00700, e00800,
              e00900, e01100, e01200, e01400, e01700, e02000, e02100,
              e02300, e02400, c01000, c02900, e03210, e03230, e03240,
              ALD_StudentLoan_hc, ALD_Tuition_hc, ALD_DomesticProduction_hc,
              ALD_InvInc_ec_rt, invinc_ec_base,
              CG_nodiff, CG_ec, CG_reinvest_ec_rt,
              ALD_BusinessLosses_c, AlimonyReceived_frac_in_AGI, MARS,
              ymod, ymod1, invinc_agi_ec):
    """
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
    """
    # investment income (1040 lines 2b, 3b, 7 + Sch 1 line 4 + capgain distrib)
    invinc = e00300 + e00600 + c01000 + e01100 + e01200
    # reform: exclude a fraction of investment income from AGI
    invinc_agi_ec = ALD_InvInc_ec_rt * max(0., invinc_ec_base)
    # ymod1 = Form 1040 income lines + Schedule 1 Part I
    # (e00800 = alimony received, Sch 1 line 2a, included only to the
    # extent of AlimonyReceived_frac_in_AGI -- TCJA excludes alimony
    # received from income for post-2018 divorces.)
    ymod1 = (e00200 + e00700 +
             AlimonyReceived_frac_in_AGI * e00800 +
             e01400 + e01700 +
             invinc - invinc_agi_ec + e02100 + e02300 +
             max(e00900 + e02000, -ALD_BusinessLosses_c[MARS - 1]))
    if CG_nodiff:
        # reform: when QDCG receive no preferential rates, partially
        # exclude (qualified dividends + net capital gain) from AGI
        qdcg_pos = max(0., e00650 + c01000)
        qdcg_exclusion = (min(CG_ec, qdcg_pos) +
                          CG_reinvest_ec_rt * max(0., qdcg_pos - CG_ec))
        ymod1 = max(0., ymod1 - qdcg_exclusion)
        invinc_agi_ec += qdcg_exclusion
    # ymod = modAGI used by the SS-benefits worksheet (Pub. 915).
    # Worksheet line 6 = "Schedule 1, lines 11 through 20, and 23 and
    # 25" — it excludes Sch 1 line 21 (student loan interest) and the
    # legacy tuition / domestic-production lines. ymod3 adds back the
    # exact amount Adj subtracted into c02900 for those three items so
    # the worksheet line 6 omission is undone symmetrically.
    ymod2 = e00400 + (0.50 * e02400) - c02900
    ymod3 = ((1. - ALD_StudentLoan_hc) * e03210 +
             (1. - ALD_Tuition_hc) * e03230 +
             (1. - ALD_DomesticProduction_hc) * e03240)
    ymod = ymod1 + ymod2 + ymod3
    return (ymod, ymod1, invinc_agi_ec)


@iterate_jit(nopython=True)
def SSBenefits(MARS, ymod, e02400, SS_all_in_agi, SS_thd1, SS_thd2,
               SS_percentage1, SS_percentage2, c02500):
    """
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
    Note: MARS=3 thresholds correspond to "MFS lived apart all year";
    Tax-Calculator does not model the MFS-lived-together case (base = 0).

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
    """
    # reform: include all OASDI in AGI (override worksheet)
    if SS_all_in_agi:
        c02500 = e02400
        return c02500
    thd1 = SS_thd1[MARS - 1]  # worksheet line 8
    thd2 = SS_thd2[MARS - 1]  # worksheet line 8 + line 10
    if ymod < thd1:
        # worksheet line 9 <= 0
        c02500 = 0.
    elif ymod < thd2:
        # worksheet line 11 = 0; c02500 = line 14 = min(line 2, line 13)
        c02500 = SS_percentage1 * min(ymod - thd1, e02400)
    else:
        # c02500 = line 18 = min(line 16, line 17)
        # line 16 = line 14 + line 15
        #         = p1 * min(e02400, thd2 - thd1) + p2 * (ymod - thd2)
        # line 17 = p2 * e02400
        c02500 = min(SS_percentage2 * (ymod - thd2) +
                     SS_percentage1 * min(e02400, thd2 - thd1),
                     SS_percentage2 * e02400)
    return c02500


@iterate_jit(nopython=True)
def UBI(nu18, n1820, n21, UBI_u18, UBI_1820, UBI_21, UBI_ecrt,
        ubi, taxable_ubi, nontaxable_ubi):
    """
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
    """
    ubi = nu18 * UBI_u18 + n1820 * UBI_1820 + n21 * UBI_21
    taxable_ubi = ubi * (1. - UBI_ecrt)
    nontaxable_ubi = ubi - taxable_ubi
    return ubi, taxable_ubi, nontaxable_ubi


@iterate_jit(nopython=True)
def AGI(ymod1, c02500, c02900, XTOT, MARS, DSI, exact, nu18, taxable_ubi,
        II_em, II_em_ps, II_em_po_step_size, II_em_prt, II_no_em_nu18,
        e02300, UI_thd, UI_em, c00100, pre_c04600, c04600):
    """
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
    """
    # ----------------------------------------------------------------
    # Form 1040 line 11: Adjusted Gross Income
    # ----------------------------------------------------------------
    # line 9 (total income) - line 10 (Sch 1 line 26 adjustments)
    # = line 11 (AGI); reform-only taxable_ubi is added in.
    c00100 = ymod1 + c02500 - c02900 + taxable_ubi
    # UI exclusion (2020 ARPA-style; reform parameters UI_em / UI_thd)
    if (c00100 - e02300) <= UI_thd[MARS - 1]:
        ui_excluded = min(e02300, UI_em)
    else:
        ui_excluded = 0.
    c00100 -= ui_excluded
    # ----------------------------------------------------------------
    # Personal exemption pre-phaseout (reform / pre-TCJA only;
    # no line on the 2025 Form 1040)
    # ----------------------------------------------------------------
    # pre_c04600 = XTOT * II_em, with optional under-18-dep repeal
    # (II_no_em_nu18) and dependent-filer override (DSI).
    if II_no_em_nu18:  # repeal of personal exemptions for deps. under 18
        pre_c04600 = max(0, XTOT - nu18) * II_em
    else:
        pre_c04600 = XTOT * II_em
    if DSI:
        pre_c04600 = 0.
    # ----------------------------------------------------------------
    # Personal exemption phase-out (PEP)
    # Pre-TCJA "Deduction for Exemptions Worksheet" (lines 5-7);
    # reform-only.
    # ----------------------------------------------------------------
    if exact == 1:  # exact calculation as on tax forms
        pep_line5 = max(0., c00100 - II_em_ps[MARS - 1])
        pep_line6 = math.ceil(pep_line5 / II_em_po_step_size[MARS - 1])
        pep_line7 = II_em_prt * pep_line6
        c04600 = max(0., pre_c04600 * (1. - pep_line7))
    else:  # smoothed calculation needed for sensible mtr calculation
        dispc_numer = II_em_prt * (c00100 - II_em_ps[MARS - 1])
        dispc_denom = II_em_po_step_size[MARS - 1]
        dispc = min(1., max(0., dispc_numer / dispc_denom))
        c04600 = pre_c04600 * (1. - dispc)
    return (c00100, pre_c04600, c04600)


@iterate_jit(nopython=True)
def MiscDed(age_head, age_spouse, MARS, c00100, exact,
            SeniorDed_c, SeniorDed_ps, SeniorDed_prt,
            overtime_income,
            OvertimeIncomeDed_c, OvertimeIncomeDed_ps,
            OvertimeIncomeDed_po_step_size,
            OvertimeIncomeDed_po_rate_per_step,
            tip_income,
            TipIncomeDed_c, TipIncomeDed_ps,
            TipIncomeDed_po_step_size,
            TipIncomeDed_po_rate_per_step,
            auto_loan_interest,
            AutoLoanInterestDed_c, AutoLoanInterestDed_ps,
            AutoLoanInterestDed_po_step_size,
            AutoLoanInterestDed_po_rate_per_step,
            senior_deduction,
            overtime_income_deduction,
            tip_income_deduction,
            auto_loan_interest_deduction):
    """
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
    """
    # pylint: disable=too-many-statements,too-many-branches
    # ----------------------------------------------------------------
    # Sch 1-A Part I (lines 1-3): Modified AGI
    # Foreign-income add-backs (lines 2a-2d) are not modeled in
    # Tax-Calculator records, so AGI (Form 1040 line 11 = c00100)
    # is the MAGI proxy used by all four parts below.
    # ----------------------------------------------------------------
    magi = c00100
    # ----------------------------------------------------------------
    # Sch 1-A Part II (lines 4-13): No Tax on Tips
    # MFJ-only if married (MARS=3 disallowed).
    # ----------------------------------------------------------------
    tip_income_deduction = 0.
    if tip_income > 0. and MARS != 3:
        ded = min(tip_income, TipIncomeDed_c)  # line 7 (cap)
        po_start = TipIncomeDed_ps[MARS - 1]  # line 9
        if magi > po_start:  # line 10 (excess)
            excess_agi = magi - po_start
            po_rate = TipIncomeDed_po_rate_per_step
            if exact == 1:  # exact calculation as on tax forms
                step_size = TipIncomeDed_po_step_size
                steps = math.floor(excess_agi / step_size)  # line 11
                po_amount = steps * step_size * po_rate  # line 12
            else:  # smoothed calculation needed for sensible mtr calculation
                po_amount = excess_agi * po_rate
            ded = max(0., ded - po_amount)  # line 13
        tip_income_deduction = ded
    # ----------------------------------------------------------------
    # Sch 1-A Part III (lines 14-21): No Tax on Overtime
    # MFJ-only if married (MARS=3 disallowed).
    # ----------------------------------------------------------------
    overtime_income_deduction = 0.
    if overtime_income > 0. and MARS != 3:
        ded = min(overtime_income,
                  OvertimeIncomeDed_c[MARS - 1])  # line 15 (cap)
        po_start = OvertimeIncomeDed_ps[MARS - 1]  # line 17
        if magi > po_start:  # line 18 (excess)
            excess_agi = magi - po_start
            po_rate = OvertimeIncomeDed_po_rate_per_step
            if exact == 1:  # exact calculation as on tax forms
                step_size = OvertimeIncomeDed_po_step_size
                steps = math.floor(excess_agi / step_size)  # line 19
                po_amount = steps * step_size * po_rate  # line 20
            else:  # smoothed calculation needed for sensible mtr calculation
                po_amount = excess_agi * po_rate
            ded = max(0., ded - po_amount)  # line 21
        overtime_income_deduction = ded
    # ----------------------------------------------------------------
    # Sch 1-A Part IV (lines 22-30): No Tax on Car Loan Interest
    # No MFS restriction on the form; allowed for all MARS values.
    # Step rounding is CEIL (line 28 "increase to next higher whole
    # number"), unlike Parts II/III which FLOOR.
    # ----------------------------------------------------------------
    auto_loan_interest_deduction = 0.
    if AutoLoanInterestDed_c > 0. and auto_loan_interest > 0.:
        ded = min(auto_loan_interest, AutoLoanInterestDed_c)  # line 24
        po_start = AutoLoanInterestDed_ps[MARS - 1]  # line 26
        if magi > po_start:  # line 27 (excess)
            excess_agi = magi - po_start
            po_rate = AutoLoanInterestDed_po_rate_per_step
            if exact == 1:  # exact calculation as on tax forms
                step_size = AutoLoanInterestDed_po_step_size
                steps = math.ceil(excess_agi / step_size)  # line 28
                po_amount = steps * step_size * po_rate  # line 29
            else:  # smoothed calculation needed for sensible mtr calculation
                po_amount = excess_agi * po_rate
            ded = max(0., ded - po_amount)  # line 30
        auto_loan_interest_deduction = ded
    # ----------------------------------------------------------------
    # Sch 1-A Part V (lines 31-37): Enhanced Deduction for Seniors
    # MFJ-only if married (MARS=3 disallowed); per eligible
    # head/spouse aged 65+. Phaseout is smooth 6% (no exact branch).
    # ----------------------------------------------------------------
    senior_deduction = 0.
    if SeniorDed_c > 0. and MARS != 3:
        seniors = 0
        if age_head >= 65:
            seniors += 1
        if MARS == 2 and age_spouse >= 65:
            seniors += 1
        if seniors > 0:
            po_start = SeniorDed_ps[MARS - 1]  # line 32
            if magi > po_start:  # line 33 (excess)
                excess_agi = magi - po_start
                po_amount = excess_agi * SeniorDed_prt  # line 34
                per_person_ded = max(0., SeniorDed_c - po_amount)  # line 35
            else:
                per_person_ded = SeniorDed_c  # line 33: use $6,000 base
            senior_deduction = seniors * per_person_ded  # lines 36a/36b/37
    return (senior_deduction, overtime_income_deduction,
            tip_income_deduction, auto_loan_interest_deduction)


@iterate_jit(nopython=True)
def ItemDed(e17500, e18400, e18500, e19200,
            e19800, e20100, e20400, g20500,
            MARS, age_head, age_spouse, c00100, c04600, c04470, c21040, c21060,
            c17000, c18300, c19200, c19700, c20500, c20800, II_brk6,
            ID_ps, ID_Medical_frt, ID_Medical_frt_add4aged, ID_Medical_hc,
            ID_Casualty_frt, ID_Casualty_hc, ID_Miscellaneous_frt,
            ID_Miscellaneous_hc, ID_Charity_crt_all, ID_Charity_crt_noncash,
            ID_prt, ID_crt, ID_c, ID_StateLocalTax_hc, ID_Charity_frt,
            ID_Charity_hc, ID_InterestPaid_hc, ID_RealEstate_hc,
            ID_Medical_c, ID_StateLocalTax_c, ID_RealEstate_c,
            ID_InterestPaid_c, ID_Charity_c, ID_Casualty_c,
            ID_Miscellaneous_c, ID_AllTaxes_c, ID_AllTaxes_hc,
            ID_AllTaxes_c_ps, ID_AllTaxes_c_po_rate, ID_AllTaxes_c_po_floor,
            ID_StateLocalTax_crt, ID_RealEstate_crt, ID_Charity_f,
            ID_reduction_rate):
    """
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
        Reform additional AGI-fraction floor (zero under current law
        because g20500 is already post-Form-4684)
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
    """
    # pylint: disable=too-many-statements
    posagi = max(c00100, 0.)
    # ----------------------------------------------------------------
    # Sch A Medical and Dental Expenses (lines 1-4)
    # Reform plumbing: ID_Medical_frt_add4aged (age 65+ floor add-on,
    # zero post-TCJA), ID_Medical_hc haircut, ID_Medical_c dollar cap.
    # ----------------------------------------------------------------
    medical_frt = ID_Medical_frt  # line 3 floor rate (7.5% of AGI)
    if age_head >= 65 or (MARS == 2 and age_spouse >= 65):
        medical_frt += ID_Medical_frt_add4aged
    c17750 = medical_frt * posagi  # line 3
    c17000 = max(0., e17500 - c17750) * (1. - ID_Medical_hc)  # line 4
    c17000 = min(c17000, ID_Medical_c[MARS - 1])  # reform cap
    # ----------------------------------------------------------------
    # Sch A Taxes You Paid (lines 5-7)
    # Line 5c (personal property tax) and line 6 (other taxes) are
    # unmodeled. Per-component reform plumbing: ID_StateLocalTax_c /
    # ID_RealEstate_c (per-MARS dollar caps); ID_StateLocalTax_crt /
    # ID_RealEstate_crt (AGI-fraction caps); ID_AllTaxes_hc (haircut on
    # combined 5d). The OBBBA 5e SALT cap with $500k/$250k phaseout is
    # implemented via ID_AllTaxes_c + ID_AllTaxes_c_ps +
    # ID_AllTaxes_c_po_rate + ID_AllTaxes_c_po_floor.
    # ----------------------------------------------------------------
    c18400 = min((1. - ID_StateLocalTax_hc) * max(e18400, 0.),
                 ID_StateLocalTax_c[MARS - 1])  # line 5a (state inc/sales)
    c18500 = min((1. - ID_RealEstate_hc) * e18500,
                 ID_RealEstate_c[MARS - 1])  # line 5b (real estate)
    # Per-component AGI-fraction caps. The 0.0001 (rather than zero)
    # leaves filers with negative AGI uncapped under current law.
    c18400 = min(c18400, ID_StateLocalTax_crt * max(c00100, 0.0001))
    c18500 = min(c18500, ID_RealEstate_crt * max(c00100, 0.0001))
    c18300 = (c18400 + c18500) * (1. - ID_AllTaxes_hc)  # line 5d sum + hc
    salt_cap = ID_AllTaxes_c[MARS - 1]  # line 5e base cap
    salt_ps = ID_AllTaxes_c_ps[MARS - 1]  # line 5e phaseout start
    if posagi > salt_ps:
        salt_excess_agi = posagi - salt_ps
        salt_cap = max(0., salt_cap - salt_excess_agi * ID_AllTaxes_c_po_rate)
        salt_cap = max(salt_cap, ID_AllTaxes_c_po_floor[MARS - 1])
    # c18300 is line 5e final (= line 7, since line 6 is unmodeled)
    c18300 = min(c18300, salt_cap)
    # ----------------------------------------------------------------
    # Sch A Interest You Paid (lines 8-10)
    # Mortgage (line 8e) and investment (line 9) interest are
    # pre-aggregated in input variable e19200. Reform plumbing:
    # ID_InterestPaid_hc, ID_InterestPaid_c (no on-form analogue).
    # ----------------------------------------------------------------
    c19200 = e19200 * (1. - ID_InterestPaid_hc)  # line 10 (= 8e + 9)
    c19200 = min(c19200, ID_InterestPaid_c[MARS - 1])  # reform cap
    # ----------------------------------------------------------------
    # Sch A Gifts to Charity (lines 11-14)
    # On-form: e19800 = line 11 (cash), e20100 = line 12 (noncash);
    # line 13 (carryover) not modeled. Reform/OBBBA plumbing:
    # ID_Charity_frt (AGI-fraction floor; OBBBA's 0.5% kicks in 2026+),
    # ID_Charity_f (dollar floor), ID_Charity_crt_noncash (AGI cap on
    # noncash), ID_Charity_crt_all (AGI cap on total per IRC §170(b)),
    # ID_Charity_hc, ID_Charity_c. Floor is applied to noncash first,
    # any unused remainder against cash.
    # ----------------------------------------------------------------
    charity_floor = max(ID_Charity_frt * posagi, ID_Charity_f[MARS - 1])
    noncash_ded = max(0., e20100 - charity_floor)
    charity_ded_noncash = min(ID_Charity_crt_noncash * posagi, noncash_ded)
    remaining_floor = max(0., charity_floor - e20100)
    charity_ded_cash = max(0., e19800 - remaining_floor)
    c19700 = charity_ded_noncash + charity_ded_cash  # line 14
    c19700 = min(c19700, ID_Charity_crt_all * posagi) * (1. - ID_Charity_hc)
    c19700 = min(c19700, ID_Charity_c[MARS - 1])
    # ----------------------------------------------------------------
    # Sch A Casualty and Theft Losses (line 15)
    # g20500 is post-Form-4684 (10% AGI floor already applied), so
    # ID_Casualty_frt defaults to 0 under current law.
    # ----------------------------------------------------------------
    c20500 = (max(0., g20500 - ID_Casualty_frt * posagi) *
              (1. - ID_Casualty_hc))  # line 15
    c20500 = min(c20500, ID_Casualty_c[MARS - 1])  # reform cap
    # ----------------------------------------------------------------
    # Sch A Other Itemized Deductions (line 16, "miscellaneous" in code)
    # The pre-TCJA 2%-of-AGI miscellaneous deductions are repealed for
    # current law (ID_Miscellaneous_hc = 1.0); parameters retained for
    # reform use.
    # ----------------------------------------------------------------
    c20750 = ID_Miscellaneous_frt * posagi  # reform AGI floor
    c20800 = max(0., e20400 - c20750) * (1. - ID_Miscellaneous_hc)  # line 16
    c20800 = min(c20800, ID_Miscellaneous_c[MARS - 1])  # reform cap
    # ----------------------------------------------------------------
    # Sch A Total Itemized Deductions (line 17 = sum of 4+7+10+14+15+16)
    # ----------------------------------------------------------------
    c21060 = c17000 + c18300 + c19200 + c19700 + c20500 + c20800
    # ----------------------------------------------------------------
    # Reform/legacy post-form stack (no Sch A correspondence):
    # (1) §68 Pease overall-limitation — repealed by TCJA for 2018-2025;
    #     parameters retained for reform use. Excludes medical (c17000)
    #     and casualty (c20500) per §68(c).
    # (2) OBBBA top-bracket reduction (ID_reduction_rate). Mutually
    #     exclusive with Pease via the assert.
    # (3) Reform hard cap ID_c on total itemized deductions.
    # No attempt is made to adjust c04470's components for any of these
    # post-total limitations.
    # ----------------------------------------------------------------
    nonlimited = c17000 + c20500
    limitstart = ID_ps[MARS - 1]
    if c21060 > nonlimited and c00100 > limitstart:
        dedmin = ID_crt * (c21060 - nonlimited)
        dedpho = ID_prt * max(0., posagi - limitstart)
        c21040 = min(dedmin, dedpho)
        c04470 = c21060 - c21040
    else:
        c21040 = 0.
        c04470 = c21060
    reduction = 0.
    if ID_reduction_rate > 0.:
        assert c21040 <= 0.0, 'Pease and OBBBA cannot both be in effect'
        tincome = max(0., c00100 - c04600)
        texcess = max(0., tincome - II_brk6[MARS - 1])
        reduction = ID_reduction_rate * texcess
    c04470 = max(0., c04470 - reduction)
    c04470 = min(c04470, ID_c[MARS - 1])
    return (c17000, c18300, c19200, c19700, c20500, c20800,
            c21040, c21060, c04470)


@iterate_jit(nopython=True)
def AdditionalMedicareTax(MARS, e00200,
                          e00900p, e00900s, e02100p, e02100s, k1bx14p, k1bx14s,
                          FICA_ss_trt_employer, FICA_ss_trt_employee,
                          FICA_mc_trt_employer, FICA_mc_trt_employee,
                          AMEDT_ec, AMEDT_rt,
                          ptax_amc):
    """
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

    Tax-Calculator does not separately track Medicare wages (W-2 box 5)
    from Form 4137 unreported tips and Form 8919 wages, so `e00200`
    substitutes for Form 8959 line 4 (the sum of lines 1+2+3).

    Form 8959 line 8 (Sch SE Part I line 6) is reconstructed per-spouse:
    Sch SE is filed separately by each spouse, so each spouse's net SE
    earnings are floored at zero independently before the joint total is
    formed. The records-bound `sey` is the unfloored sum, which would
    over-net a positive-sey spouse against a negative-sey spouse; this
    function therefore re-derives `sey_p`/`sey_s` from the underlying
    per-spouse input components (matching `EI_PayrollTax`) and applies
    the per-spouse 0-floor before summing.

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
        Wages and salaries; substitutes for Form 8959 line 4 (Medicare
        wages from W-2 box 5 + Form 4137 line 6 + Form 8919 line 6)
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
    """
    threshold = AMEDT_ec[MARS - 1]  # line 5 (also line 9; same value)
    seca_frac = 1. - 0.5 * (FICA_ss_trt_employer + FICA_ss_trt_employee +
                            FICA_mc_trt_employer + FICA_mc_trt_employee)
    # Per-spouse Sch SE Part I line 6 (each floored at 0; matches the
    # `sey_p`/`sey_s` and `net_sey_p`/`net_sey_s` construction in
    # `EI_PayrollTax`).
    sey_p = e00900p + e02100p + k1bx14p
    sey_s = e00900s + e02100s + k1bx14s
    net_sey_p = max(0., sey_p * seca_frac)
    net_sey_s = max(0., sey_s * seca_frac)
    # -- Part I: Medicare wages (lines 1-7) --
    line4 = e00200
    line6 = max(0., line4 - threshold)
    line7 = AMEDT_rt * line6
    # -- Part II: Self-employment income (lines 8-13) --
    line8 = net_sey_p + net_sey_s
    line11 = max(0., threshold - line4)  # = max(0, line 9 - line 10)
    line12 = max(0., line8 - line11)
    line13 = AMEDT_rt * line12
    # -- Part IV: Total (line 18); Part III RRTA not modeled --
    ptax_amc = line7 + line13
    return ptax_amc


@iterate_jit(nopython=True)
def StdDed(DSI, earned, STD, age_head, age_spouse, STD_Aged, STD_Dep,
           STD_Dep_earned_add, MARS, MIDR, blind_head, blind_spouse, standard,
           STD_allow_charity_ded_nonitemizers, e19800, ID_Charity_crt_all,
           c00100, STD_charity_ded_nonitemizers_max):
    """
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
    4. Reform/legacy CARES cash-charity add-on for nonitemizers (off
       under current law; STD_allow_charity_ded_nonitemizers defaults
       to False).

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
    -- Reform/legacy CARES nonitemizer charity add-on --
    STD_allow_charity_ded_nonitemizers: bool
        Allow standard deduction filers to take the charitable
        contributions deduction (off under current law)
    e19800: float
        Schedule A line 11 cash charitable contributions
    ID_Charity_crt_all: float
        Fraction-of-AGI cap on all charitable deductions
    c00100: float
        Federal AGI (Form 1040 line 11)
    STD_charity_ded_nonitemizers_max: list
        Per-MARS ceiling amount (in dollars) on the nonitemizer
        charitable contributions deduction

    Returns
    -------
    standard: float
        Standard deduction (zero for itemizers)
    """
    # ----------------------------------------------------------------
    # MFS-and-spouse-itemizes override (Form 1040 line-12 instructions:
    # "Married filing separately and your spouse itemizes deductions").
    # Implementation invariant: MIDR=1 only occurs when MARS=3.
    # ----------------------------------------------------------------
    if MARS == 3 and MIDR == 1:
        standard = 0.
        return standard
    # ----------------------------------------------------------------
    # Basic standard deduction: dependent worksheet if claimed as a
    # dependent, otherwise the Form 1040 line-12 chart value.
    # ----------------------------------------------------------------
    std_basic = STD[MARS - 1]                       # line-12 chart cap
    if DSI == 1:
        # Dependent Std Ded Worksheet:
        # line 3 = earned + STD_Dep_earned_add  (worksheet lines 1+2)
        # line 5 = max(line 3, STD_Dep)         (worksheet lines 4-5)
        # line 7 = min(line 5, STD[MARS-1])     (worksheet line 7)
        basic_stded = min(std_basic,
                          max(earned + STD_Dep_earned_add, STD_Dep))
    else:
        basic_stded = std_basic
    # ----------------------------------------------------------------
    # Aged/blind add-on (line-12 chart): one STD_Aged box per
    # 65+/blind condition on filer; spouse boxes only count for MFJ.
    # ----------------------------------------------------------------
    num_extra_stded = blind_head
    if age_head >= 65:
        num_extra_stded += 1
    if MARS == 2:
        num_extra_stded += blind_spouse
        if age_spouse >= 65:
            num_extra_stded += 1
    extra_stded = num_extra_stded * STD_Aged[MARS - 1]
    standard = basic_stded + extra_stded
    # ----------------------------------------------------------------
    # Reform/legacy CARES cash-charity add-on for nonitemizers
    # (STD_allow_charity_ded_nonitemizers defaults to False under
    # current law; active in 2020-2021 and under reforms).
    # ----------------------------------------------------------------
    if STD_allow_charity_ded_nonitemizers:
        capped_ded = min(e19800, ID_Charity_crt_all * c00100)
        standard += min(capped_ded, STD_charity_ded_nonitemizers_max[MARS - 1])
    return standard


@iterate_jit(nopython=True)
def TaxInc(c00100, standard, c04470, c04600, MARS,
           e00900, c03260, e03270, e03300, e26270, e02100, e27200,
           e00650, p22250, p23250,
           senior_deduction, overtime_income_deduction,
           tip_income_deduction, auto_loan_interest_deduction,
           PT_SSTB_income, PT_binc_w2_wages, PT_ubia_property,
           PT_qbid_rt, PT_qbid_limited,
           PT_qbid_taxinc_thd, PT_qbid_taxinc_gap, PT_qbid_w2_wages_rt,
           PT_qbid_alt_w2_wages_rt, PT_qbid_alt_property_rt,
           PT_qbid_ps, PT_qbid_prt, PT_qbid_min_ded, PT_qbid_min_qbi,
           c04800, qbided):
    """
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
    """
    # ----------------------------------------------------------------
    # Pre-QBID taxable income (Form 8995 line 11 / Form 8995-A line 33)
    # = Form 1040 line 15 with the QBID line removed. QBID is "stacked
    # last" so all other below-AGI deductions are subtracted here:
    # max(itemized, standard) + reform-only personal exemption +
    # Sch 1-A senior/overtime/tip/auto-loan deductions.
    # ----------------------------------------------------------------
    odeds = (
        senior_deduction          # Sch 1-A Part V
        + overtime_income_deduction  # Sch 1-A Part III
        + tip_income_deduction       # Sch 1-A Part II
        + auto_loan_interest_deduction  # Sch 1-A Part IV
    )
    pre_qbid_taxinc = max(0., c00100 - max(c04470, standard) - c04600 - odeds)
    # ----------------------------------------------------------------
    # Qualified Business Income (QBI) build (Form 8995 line 1c /
    # Form 8995-A line 2): Sch C net, Sch E partnership/S-corp, Sch F
    # farm, Sch E farm rent, less the trade-or-business above-the-line
    # items per Form 8995 line 1 instructions: deductible SE tax (Sch 1
    # line 15), SE retirement (Sch 1 line 16), SE health insurance
    # (Sch 1 line 17). Wages and investment income are NOT QBI.
    # ----------------------------------------------------------------
    qbinc = max(0., e00900 - c03260 - e03300 - e03270
                + e26270 + e02100 + e27200)
    qbid_before_limits = qbinc * PT_qbid_rt  # Form 8995 line 5 / 8995-A line 3
    if PT_qbid_limited:
        # ------------------------------------------------------------
        # Form 8995-A Parts II/III: W-2 wage / UBIA cap and SSTB phase-in.
        # Filers with pre_qbid_taxinc <= lower_thd file the simplified
        # Form 8995 (no cap, no SSTB exclusion). Above lower_thd, four
        # sub-cases per Form 8995-A: (a) SSTB above upper_thd: 0; (b)
        # non-SSTB above upper_thd: line 11 = min(line 3, line 10); (c)
        # non-SSTB in phase-in: Part III lines 24-26; (d) SSTB in
        # phase-in: Schedule A scales QBI/W-2/UBIA by applicable %, then
        # Part III applied to scaled values.
        # ------------------------------------------------------------
        lower_thd = PT_qbid_taxinc_thd[MARS - 1]  # 8995-A line 21
        if pre_qbid_taxinc <= lower_thd:
            # Form 8995 path: no W-2/UBIA cap, no SSTB exclusion
            qbided = qbid_before_limits
        else:
            gap = PT_qbid_taxinc_gap[MARS - 1]    # 8995-A line 23
            upper_thd = lower_thd + gap
            if PT_SSTB_income == 1 and pre_qbid_taxinc >= upper_thd:
                # (a) SSTB above phase-in: deduction fully disallowed
                qbided = 0.
            else:
                # W-2 wage / UBIA cap (8995-A lines 4-10):
                #   line 5  = 50% * W-2 wages
                #   line 9  = 25% * W-2 wages + 2.5% * UBIA
                #   line 10 = max(line 5, line 9)
                wage_cap = PT_binc_w2_wages * PT_qbid_w2_wages_rt
                alt_cap = (PT_binc_w2_wages * PT_qbid_alt_w2_wages_rt +
                           PT_ubia_property * PT_qbid_alt_property_rt)
                full_cap = max(wage_cap, alt_cap)
                if PT_SSTB_income == 0 and pre_qbid_taxinc >= upper_thd:
                    # (b) non-SSTB above phase-in: line 11 =
                    # min(line 3, line 10)
                    qbided = min(full_cap, qbid_before_limits)
                elif PT_SSTB_income == 0 and pre_qbid_taxinc < upper_thd:
                    # (c) non-SSTB in phase-in: 8995-A Part III lines
                    # 24-26. line 26 = line 17 - line 25
                    #     = qbid_before_limits
                    #         - prt * max(0, qbid_before_limits - full_cap)
                    # where prt = line 24 = (taxinc - thd) / gap. Part III
                    # is skipped when line 10 (full_cap) >= line 3
                    # (qbid_before_limits), so the cap-vs-QBI excess is
                    # floored at 0 to prevent the formula from inflating
                    # qbided above qbid_before_limits.
                    prt = (pre_qbid_taxinc - lower_thd) / gap
                    adj = prt * max(0., qbid_before_limits - full_cap)
                    qbided = qbid_before_limits - adj
                else:  # PT_SSTB_income == 1 and pre_qbid_taxinc < upper_thd
                    # (d) SSTB in phase-in: Schedule A scales QBI and
                    # W-2/UBIA cap by applicable_pct = (upper_thd -
                    # taxinc) / gap; Part III phase-in is then applied
                    # to the Schedule-A-adjusted line 3 and line 10,
                    # with the same Part-III-skipped floor as case (c).
                    prti = (upper_thd - pre_qbid_taxinc) / gap  # applicable %
                    qbid_adjusted = prti * qbid_before_limits  # Sch A line 3
                    cap_adjusted = prti * full_cap             # Sch A line 10
                    prt = (pre_qbid_taxinc - lower_thd) / gap
                    adj = prt * max(0., qbid_adjusted - cap_adjusted)
                    qbided = qbid_adjusted - adj
        # ------------------------------------------------------------
        # Form 8995-A Part IV: income limitation (lines 33-37; same
        # role as Form 8995 lines 11-15). Form 8995 line 12 / 8995-A
        # line 34 net_cg = §1(h) net capital gain (excess of net LTCG
        # over net STCL) plus qualified dividends per §199A(e)(3) and
        # the form 8995 instructions. Net STCG must NOT enter net_cg,
        # so we use p22250/p23250 directly rather than the post-cap
        # Sch D total c01000 = p22250 + p23250 (capped at -3000).
        # Income cap = PT_qbid_rt * (pre_qbid_taxinc - net_cg) is
        # line 36 / 14; final qbided = min(line 32, line 36) is
        # line 37 / 15.
        # ------------------------------------------------------------
        net_ltcg = max(0., p23250)
        net_stcl = max(0., -p22250)
        net_cg = max(0., net_ltcg - net_stcl) + e00650
        taxinc_cap = PT_qbid_rt * max(0., pre_qbid_taxinc - net_cg)
        qbided = min(qbided, taxinc_cap)
        # ------------------------------------------------------------
        # Reform-only: linear QBID phase-out above PT_qbid_ps (no IRS
        # form analogue).
        # ------------------------------------------------------------
        if qbided > 0. and pre_qbid_taxinc > PT_qbid_ps[MARS - 1]:
            excess = pre_qbid_taxinc - PT_qbid_ps[MARS - 1]
            qbided = max(0., qbided - PT_qbid_prt * excess)
    else:
        # Reform: TCJA W-2/UBIA cap, SSTB exclusion, Part III phase-in,
        # and Part IV income limitation all disabled.
        qbided = qbid_before_limits
    # ----------------------------------------------------------------
    # Reform-only: minimum QBID floor for filers with QBI at or above
    # PT_qbid_min_qbi (no IRS form analogue).
    # ----------------------------------------------------------------
    if qbinc >= PT_qbid_min_qbi and qbided < PT_qbid_min_ded:
        qbided = PT_qbid_min_ded
    # ----------------------------------------------------------------
    # Form 1040 line 15: taxable income = pre_qbid_taxinc - qbided
    # (line 14 = std/itemized + QBID; QBID stacked last as documented
    # in pre_qbid_taxinc construction above).
    # ----------------------------------------------------------------
    c04800 = max(0., pre_qbid_taxinc - qbided)
    return (c04800, qbided)


@JIT(nopython=True)
def SchXYZ(taxable_income, MARS,
           II_rt1, II_rt2, II_rt3, II_rt4, II_rt5,
           II_rt6, II_rt7, II_rt8,
           II_brk1, II_brk2, II_brk3, II_brk4, II_brk5,
           II_brk6, II_brk7):
    """
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
    """
    # pylint: disable=too-many-return-statements
    # IRS 2025 Tax Rate Schedules X (single), Y-1 (MFJ/QW), Y-2 (MFS),
    # Z (HoH): MARS - 1 selects the schedule via II_brk?[MARS - 1].
    if taxable_income <= 0.:
        return 0.
    brk1 = II_brk1[MARS - 1]
    if taxable_income <= brk1:
        return II_rt1 * taxable_income
    tax = II_rt1 * brk1
    brk2 = II_brk2[MARS - 1]
    if taxable_income <= brk2:
        return tax + II_rt2 * (taxable_income - brk1)
    tax = tax + II_rt2 * (brk2 - brk1)
    brk3 = II_brk3[MARS - 1]
    if taxable_income <= brk3:
        return tax + II_rt3 * (taxable_income - brk2)
    tax = tax + II_rt3 * (brk3 - brk2)
    brk4 = II_brk4[MARS - 1]
    if taxable_income <= brk4:
        return tax + II_rt4 * (taxable_income - brk3)
    tax = tax + II_rt4 * (brk4 - brk3)
    brk5 = II_brk5[MARS - 1]
    if taxable_income <= brk5:
        return tax + II_rt5 * (taxable_income - brk4)
    tax = tax + II_rt5 * (brk5 - brk4)
    brk6 = II_brk6[MARS - 1]
    if taxable_income <= brk6:
        return tax + II_rt6 * (taxable_income - brk5)
    tax = tax + II_rt6 * (brk6 - brk5)
    brk7 = II_brk7[MARS - 1]
    if taxable_income <= brk7:
        return tax + II_rt7 * (taxable_income - brk6)
    return tax + II_rt8 * (taxable_income - brk7)


@iterate_jit(nopython=True)
def SchXYZTax(c04800, MARS,
              II_rt1, II_rt2, II_rt3, II_rt4, II_rt5,
              II_rt6, II_rt7, II_rt8,
              II_brk1, II_brk2, II_brk3, II_brk4, II_brk5,
              II_brk6, II_brk7, c05200):
    """
    Function that routes c04800 (regular taxable income) through the
    SchXYZ rate-schedule function and stores the result in c05200 (tax
    amount from Tax Rate Schedules X, Y-1, Y-2, Z). See the SchXYZ function
    for the semantics of MARS, II_rt?, and II_brk?.
    """
    c05200 = SchXYZ(
        c04800, MARS,
        II_rt1, II_rt2, II_rt3, II_rt4, II_rt5, II_rt6, II_rt7, II_rt8,
        II_brk1, II_brk2, II_brk3, II_brk4, II_brk5, II_brk6, II_brk7
    )
    return c05200


@iterate_jit(nopython=True)
def GainsTax(e00650, c01000, c23650, p23250, e01100, e58990,
             e24515, e24518, MARS, c04800, c05200,
             II_rt1, II_rt2, II_rt3, II_rt4, II_rt5, II_rt6, II_rt7, II_rt8,
             II_brk1, II_brk2, II_brk3, II_brk4, II_brk5, II_brk6, II_brk7,
             CG_nodiff,
             CG_rt1, CG_rt2, CG_rt3, CG_rt4, CG_brk1, CG_brk2, CG_brk3,
             dwks10, dwks13, dwks14, dwks18, dwks43, c05700, taxbc):
    """
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
        (regular/non-AMT) tax bracket 3
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
    """
    # pylint: disable=too-many-statements
    has_qdivltcg = (
        not CG_nodiff and
        (c01000 > 0. or c23650 > 0. or p23250 > 0. or
         e01100 > 0. or e00650 > 0.)
    )

    if has_qdivltcg:

        # ---- Sch D TW lines 1-10 (common to QDCGTW) ----------------------
        dwks1 = c04800                    # line 1: taxable income
        dwks2 = e00650                    # line 2: qualified dividends
        dwks3 = e58990                    # line 3: Form 4952 line 4g
        dwks4 = 0.                        # line 4: Form 4952 line 4e (=0)
        dwks5 = max(0., dwks3 - dwks4)    # line 5
        dwks6 = max(0., dwks2 - dwks5)    # line 6
        dwks7 = min(p23250, c23650)       # line 7: min(Sch D ln 15, ln 16)
        dwks8 = min(dwks3, dwks4)         # line 8: min(4952 ln 4g, ln 4e) = 0
        # line 9: max(0, dwks7 - dwks8) is the on-form value when Sch D
        # was filed; when Sch D was not filed, p23250 = c23650 = 0 so
        # dwks7 = 0 and the QDCGTW counterpart of line 9 is e01100
        # (capital gain distributions on Form 1040 line 7).  The two
        # cases are mutually exclusive, so the sum captures both.
        dwks9 = max(0., dwks7 - dwks8) + e01100        # line 9
        dwks10 = dwks6 + dwks9                         # line 10

        # ---- Sch D TW lines 11-13 (Sch D TW only; vanish in QDCGTW) -----
        dwks11 = e24515 + e24518          # line 11: Sch D ln 18 + ln 19
        dwks12 = min(dwks9, dwks11)       # line 12
        dwks13 = dwks10 - dwks12          # line 13

        # ---- Sch D TW lines 14-19 (rate-bracket setup, common) ----------
        dwks14 = max(0., dwks1 - dwks13)          # line 14
        dwks15 = min(CG_brk1[MARS - 1], dwks1)    # line 15
        dwks16 = min(dwks14, dwks15)              # line 16
        dwks17 = max(0., dwks1 - dwks10)          # line 17
        dwks18 = max(dwks16, dwks17)              # line 18
        dwks19 = dwks15 - dwks16                  # line 19: amount @ 0%
        lowest_rate_tax = CG_rt1 * dwks19         # line 20: 0% tax (=0)

        # ---- Sch D TW lines 21-32 (15% and 20% rate buckets, common) ----
        dwks21 = min(dwks1, dwks13)               # line 21
        dwks22 = dwks19                           # line 22
        dwks23 = max(0., dwks21 - dwks22)         # line 23
        dwks25 = min(CG_brk2[MARS - 1], dwks1)    # line 25
        dwks26 = dwks18 + dwks19                  # line 26
        dwks27 = max(0., dwks25 - dwks26)         # line 27
        dwks28 = min(dwks23, dwks27)              # line 28: amount @ 15%
        dwks29 = CG_rt2 * dwks28                  # line 29: 15% tax
        dwks30 = dwks22 + dwks28                  # line 30
        dwks31 = dwks21 - dwks30                  # line 31: amount @ 20%
        dwks32 = CG_rt3 * dwks31                  # line 32: 20% tax

        # ---- Reform-only: 4th capital-gains bracket (not in IRS form) ---
        # Tax-Calculator extension that levies (CG_rt4 - CG_rt3) on the
        # portion of total taxed cap gains above CG_brk3.  Inactive under
        # current law (CG_rt4 = CG_rt3).
        cg_all = dwks19 + dwks28 + dwks31
        hi_base = max(0., cg_all - CG_brk3[MARS - 1])
        hi_incremental_rate = CG_rt4 - CG_rt3
        highest_rate_incremental_tax = hi_incremental_rate * hi_base

        # ---- Sch D TW lines 33-41 (Sch D TW only: 25% and 28% rates) ----
        # These blocks zero out when e24515 = e24518 = 0, recovering QDCGTW.
        dwks33 = min(dwks9, e24515)           # line 33
        dwks34 = dwks10 + dwks18              # line 34
        dwks36 = max(0., dwks34 - dwks1)      # line 36 (line 35 omitted)
        dwks37 = max(0., dwks33 - dwks36)     # line 37: amount @ 25%
        dwks38 = 0.25 * dwks37                # line 38: 25% tax
        dwks39 = dwks18 + dwks19 + dwks28 + dwks31 + dwks37   # line 39
        dwks40 = dwks1 - dwks39               # line 40: amount @ 28%
        dwks41 = 0.28 * dwks40                # line 41: 28% tax

        # ---- Sch D TW lines 42-45 (final assembly, common) --------------
        dwks42 = SchXYZ(dwks18, MARS,         # line 42: ordinary tax
                        II_rt1, II_rt2, II_rt3, II_rt4, II_rt5,
                        II_rt6, II_rt7, II_rt8,
                        II_brk1, II_brk2, II_brk3, II_brk4, II_brk5,
                        II_brk6, II_brk7)
        dwks43 = (dwks29 + dwks32 + dwks38 + dwks41 + dwks42 +
                  lowest_rate_tax + highest_rate_incremental_tax)  # line 43
        dwks44 = c05200                       # line 44: ordinary tax on line 1
        dwks45 = min(dwks43, dwks44)          # line 45: smaller of 43, 44
        c24580 = dwks45

    else:  # no qualified-rate preference

        c24580 = c05200
        dwks10 = max(0., min(p23250, c23650)) + e01100
        dwks13 = 0.
        dwks14 = 0.
        dwks18 = 0.
        dwks43 = 0.

    # final assembly (foreign earned income exclusion assumed zero, so
    # c05100 = c24580; Form 4972 lump-sum distributions not modeled)
    c05700 = 0.
    taxbc = c24580
    return (dwks10, dwks13, dwks14, dwks18, dwks43, c05700, taxbc)


@iterate_jit(nopython=True)
def AGIsurtax(c00100, MARS, AGI_surtax_trt, AGI_surtax_thd, taxbc, surtax):
    """
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
    """
    # Reform construct: inert under current law (AGI_surtax_trt = 0).
    if AGI_surtax_trt > 0.:
        agi_surtax = (
            AGI_surtax_trt * max(c00100 - AGI_surtax_thd[MARS - 1], 0.)
        )
        taxbc += agi_surtax
        surtax += agi_surtax
    return (taxbc, surtax)


@iterate_jit(nopython=True)
def AMT(e07300, dwks13, standard, f6251, c00100, c18300, taxbc,
        c04470, c20800, c21040, e24515, MARS, dwks18,
        dwks14, c05700, e62900, e00700, dwks10, age_head, age_spouse,
        earned, cmbtp, qbided,
        AMT_child_em_c_age, AMT_brk1,
        AMT_em, AMT_prt, AMT_rt1, AMT_rt2_addon,
        AMT_child_em, AMT_em_ps, AMT_em_pe,
        AMT_CG_brk1, AMT_CG_brk2, AMT_CG_brk3, AMT_CG_rt1, AMT_CG_rt2,
        AMT_CG_rt3, AMT_CG_rt4, c05800, c09600, c62100):
    """
    Computes Form 6251 (2025) Alternative Minimum Tax (AMT).

    Builds AMT taxable income c62100 (Form 6251 line 4), tentative
    minimum tax via either the flat-rate computation (line 7) or
    Part III's maximum-capital-gains-rates worksheet (lines 12-40),
    subtracts AMT foreign tax credit (line 8) to yield tentative
    minimum tax (line 9), and subtracts the regular-tax base
    (line 10) to yield AMT liability c09600 (line 11). Total tax
    before credits c05800 = taxbc + c09600.

    Form 6251 structure:
      - Part I (lines 1a-4): AMTI = taxable income (Form 1040 line 15)
        plus AMT-disallowed deductions (SALT line 2a, Sch A misc) and
        the unmodeled prefs/adjustments (lines 2c-2t + 3) captured in
        cmbtp; line 2b refunds (e00700) are subtracted.  Note: 2025
        Form 6251 has no medical add-back (TCJA/OBBBA harmonized
        regular and AMT Sch A medical floors at 7.5% of AGI).
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
      - IRC §59(j) kiddie AMT: for filers under AMT_child_em_c_age
        (no qualifying older spouse), exemption capped at
        earned + AMT_child_em.
      - Reform-only 4th cap-gains bracket above AMT_CG_brk3 taxed
        at AMT_CG_rt4 (no form analogue; AMT_CG_brk3 default 9e+99
        makes this inert under current law).

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
        Qualified business income deduction (Form 1040 line 13)
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
    age_spouse: int
        Age in years of spouse (i.e. secondary adult if present)
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
        Reform-only top of cap-gains bracket 3 (default 9e+99 →
        inert under current law)
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
    """
    # pylint: disable=too-many-statements,too-many-branches
    # ----------------------------------------------------------------
    # Form 6251 Part I (lines 1a-4): Alternative Minimum Taxable Income
    # ----------------------------------------------------------------
    # Form 6251 line 1 = Form 1040 line 15 = AGI - (STD or itemized) - QBID.
    if standard == 0.0:
        c62100 = (c00100 - e00700 - qbided - c04470 +
                  c18300 +    # SALT add-back (Form 6251 line 2a)
                  c20800 -    # Sch A misc add-back (TCJA-suspended 2018-2025)
                  c21040)     # Pease undone for AMT
    if standard > 0.0:
        c62100 = c00100 - e00700 - qbided - standard
    c62100 += cmbtp  # Form 6251 lines 2c-2t + 3: AMT prefs/adjustments
    # c62100 is AMT taxable income = Form 6251 line 4
    # ----------------------------------------------------------------
    # Form 6251 Part II top (lines 5-6): exemption and AMTI less exemption
    # ----------------------------------------------------------------
    # line 5: AMT exemption amount (with phase-out)
    line5 = max(0., AMT_em[MARS - 1] - AMT_prt *
                max(0., c62100 - AMT_em_ps[MARS - 1]))
    if MARS == 3 and c62100 > AMT_em_pe:
        line5 = 0.
    # IRC §59(j) kiddie-AMT cap: exemption limited to earned +
    # AMT_child_em when filer is under AMT_child_em_c_age (and no
    # qualifying older spouse).
    young_head = age_head != 0 and age_head < AMT_child_em_c_age
    no_or_young_spouse = age_spouse < AMT_child_em_c_age
    if young_head and no_or_young_spouse:
        line5 = min(line5, earned + AMT_child_em)
    # line 6: AMT taxable income less AMT exemption amount
    line6 = max(0., c62100 - line5)
    # ----------------------------------------------------------------
    # Form 6251 Part II tax (line 7): flat-rate AMT tax OR Part III
    # ----------------------------------------------------------------
    # Flat-rate tax: 26% below AMT_brk1, 28% above. Also serves as
    # Part III line 39 (AMT-rate on full line 12 = line 6).
    amt_brk1 = AMT_brk1[MARS - 1]
    flat_rate_tax = (AMT_rt1 * line6 +
                     AMT_rt2_addon * max(0., line6 - amt_brk1))
    if dwks10 > 0. or dwks13 > 0. or dwks14 > 0. or dwks18 > 0. or e24515 > 0.:
        # ------------------------------------------------------------
        # Form 6251 Part III (lines 12-40): tax computation using
        # maximum capital gains rates. line 12 == line 6.
        # ------------------------------------------------------------
        line13 = dwks13                        # QDCGTW ln 4 / SchDTW ln 13
        line14 = e24515                        # Sch D line 19 (unrecap §1250)
        line15 = min(line13 + line14, dwks10)  # min(13+14, SchDTW line 10)
        line16 = min(line6, line15)
        line17 = max(0., line6 - line16)       # ordinary-income portion
        line18 = (AMT_rt1 * line17 +           # AMT-rate on line 17
                  AMT_rt2_addon * max(0., line17 - amt_brk1))
        # line 19 = AMT_CG_brk1[MARS-1] (top of 0% bracket)
        cg_brk1 = AMT_CG_brk1[MARS - 1]
        line20 = dwks14                        # QDCGTW ln 5 / SchDTW ln 14
        line21 = max(0., cg_brk1 - line20)     # unused 0% bracket
        line22 = min(line6, line13)            # cap-gains-eligible portion
        line23 = min(line21, line22)           # amount taxed at AMT_CG_rt1:0%
        cgtax1 = line23 * AMT_CG_rt1
        line24 = line22 - line23
        # line 25 = AMT_CG_brk2[MARS-1] (top of 15% bracket)
        # line 26 == line 21
        line27 = dwks18                        # QDCGTW ln 5 / SchDTW ln 21
        line28 = line21 + line27
        line29 = max(0., AMT_CG_brk2[MARS - 1] - line28)
        line30 = min(line24, line29)           # amount taxed at AMT_CG_rt2:15%
        cgtax2 = line30 * AMT_CG_rt2           # line 31 = 15% * line 30
        line32 = line23 + line30               # sum of 0% + 15% amounts
        # Form 6251 line 33 = line 22 - line 32 (residual cap-gains for
        # 20% bracket / reform-only 4th bracket).  Skip when line 22 ==
        # line 32 (no residual).
        if line22 == line32:
            line33 = 0.                        # amount taxed at AMT_CG_rt3:20%
            linex2 = 0.                        # amount taxed at AMT_CG_rt4:ref
        else:
            line33 = line22 - line32
            # Reform-only 4th bracket above AMT_CG_brk3 (default
            # 9e+99 → linex2 collapses to 0 under current law).
            linex1 = min(line24,
                         max(0., AMT_CG_brk3[MARS - 1] - line20 - line21))
            linex2 = max(0., line30 - linex1)
        cgtax3 = line33 * AMT_CG_rt3           # line 34 = 20% * line 33
        cgtax4 = linex2 * AMT_CG_rt4
        if line14 == 0.:                       # line 35-37: §1250 25%
            line37 = 0.
        else:
            line37 = 0.25 * max(0., line6 - line17 - line32 - line33 - linex2)
        line38 = line18 + cgtax1 + cgtax2 + cgtax3 + cgtax4 + line37
        line40 = min(flat_rate_tax, line38)    # min(line 38, line 39)
        line7 = line40
    else:  # if not completing Form 6251 Part III
        line7 = flat_rate_tax
    # ----------------------------------------------------------------
    # Form 6251 Part II bottom (lines 8-11): AMT FTC, TMT, regular-tax
    # base, AMT.
    # ----------------------------------------------------------------
    if f6251 == 1:
        line8 = e62900                         # AMT FTC from filed Form 6251
    else:
        line8 = e07300                         # regular FTC proxy
    line9 = line7 - line8                      # tentative minimum tax
    # line 10 regular-tax base = max(0, taxbc - e07300 - c05700);
    # c05700 corresponds to "minus any tax from Form 4972".
    c09600 = max(0., line9 - max(0., taxbc - e07300 - c05700))
    c05800 = taxbc + c09600
    return (c62100, c09600, c05800)


@iterate_jit(nopython=True)
def NetInvIncTax(e00300, e00600, e02000, e26270, c01000,
                 c00100, NIIT_thd, MARS, NIIT_PT_taxed, NIIT_rt, niit):
    """
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
    """
    # ---- Part I: investment income (Form 8960 lines 1-8) ----
    line1 = e00300                                  # line 1
    line2 = e00600                                  # line 2
    # line 3 (annuities): not modeled
    if NIIT_PT_taxed:
        line4c = e02000                             # line 4b adjustment = 0
    else:
        line4c = e02000 - e26270                    # line 4b = -e26270
    line5d = c01000                                 # lines 5b/5c not modeled
    # lines 6, 7: not modeled
    line8 = line1 + line2 + line4c + line5d         # line 8

    # ---- Part II: investment expenses (lines 9-11) not modeled => 0 ----

    # ---- Part III: tax computation (Form 8960 lines 12-17) ----
    line12 = max(0., line8)                         # line 12 (line 11 = 0)
    modAGI = c00100  # no foreign earned income exclusion to add
    line15 = max(0., modAGI - NIIT_thd[MARS - 1])   # lines 13-15
    line16 = min(line12, line15)                    # line 16
    niit = NIIT_rt * line16                         # line 17
    return niit


@iterate_jit(nopython=True)
def F2441(MARS, earned_p, earned_s, f2441, CDCC_c, e32800, exact, c00100,
          CDCC_ps1, CDCC_ps2, CDCC_po1_rate_max, CDCC_po1_rate_min,
          CDCC_po2_rate_min, CDCC_po1_step_size, CDCC_po2_step_size,
          CDCC_po_rate_per_step, CDCC_refundable,
          c05800, e07300, c32800, c07180, CDCC_refund):
    """
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
    """
    # ---- Form 2441 Part II ------------------------------------------------
    # line 3: qualifying expenses, capped at min(f2441,2) * CDCC_c
    max_credit = min(f2441, 2) * CDCC_c
    c32800 = max(0., min(e32800, max_credit))
    # lines 4, 5, 6: limit to smallest earned income across taxpayer/spouse
    earned_s_eff = earned_s if MARS == 2 else earned_p
    line6 = max(0., min(c32800, earned_p, earned_s_eff))
    # line 8: credit rate (phased down at high AGI via two stepped ramps)
    crate = CDCC_po1_rate_max
    ps1 = CDCC_ps1
    if c00100 > ps1:
        # ... first phase-down from CDCC_po1_rate_max to CDCC_po1_rate_min
        steps_fractional = (c00100 - ps1) / CDCC_po1_step_size
        if exact == 1:  # exact calculation as on tax forms
            steps = math.ceil(steps_fractional)
        else:
            steps = steps_fractional
        crate = max(
            CDCC_po1_rate_min,
            CDCC_po1_rate_max - steps * CDCC_po_rate_per_step
        )
        # ... second phase-down from CDCC_po1_rate_min to CDCC_po2_rate_min
        ps2 = CDCC_ps2[MARS - 1]
        assert ps2 >= ps1, 'CDCC_ps2 must be no less than CDCC_ps1'
        if c00100 > ps2:
            step2 = CDCC_po2_step_size[MARS - 1]
            steps_fractional = (c00100 - ps2) / step2
            if exact == 1:  # exact calculation as on tax forms
                steps = math.ceil(steps_fractional)
            else:
                steps = steps_fractional
            crate = max(
                CDCC_po2_rate_min,
                CDCC_po1_rate_min - steps * CDCC_po_rate_per_step
            )
    # line 9a: preliminary credit (line 6 * line 8)
    # line 9b (2024 expenses paid in 2025 catch-up via Worksheet A) is
    # not modeled, so on-form line 9c = line 9a + line 9b reduces to
    # line 9a here
    line9a = line6 * crate
    # lines 10, 11: nonrefundable credit limited by tax-before-credits
    # less FTC per the 2025 Credit Limit Worksheet (which subtracts only
    # Sch 3 line 1 and the unmodeled Sch 3 line 6l Form 8978 line 14;
    # CDCC itself is Sch 3 line 2 so no other nonrefundable credits
    # precede it).  Under reform CDCC_refundable, the full line-9a
    # amount is routed to CDCC_refund instead.
    if CDCC_refundable:
        c07180 = 0.
        CDCC_refund = line9a
    else:
        c07180 = min(max(0., c05800 - e07300), line9a)
        CDCC_refund = 0.
    return (c32800, c07180, CDCC_refund)


@JIT(nopython=True)
def EITCamount(basic_frac, phasein_rate, earnings, max_amount,
               phaseout_start, agi, phaseout_rate):
    """
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
    """
    eitc = min((basic_frac * max_amount +
                (1.0 - basic_frac) * phasein_rate * earnings), max_amount)
    if earnings > phaseout_start or agi > phaseout_start:
        eitcx = max(0., (max_amount - phaseout_rate *
                         max(0., max(earnings, agi) - phaseout_start)))
        eitc = min(eitc, eitcx)
    return eitc


@iterate_jit(nopython=True)
def EITC(eitc_claim_thd, MARS, DSI, c00100, e00300, e00400, e00600, c01000,
         e02000, e26270, age_head, age_spouse, earned, earned_p, earned_s, EIC,
         EITC_ps, EITC_MinEligAge, EITC_MaxEligAge, EITC_ps_addon_MarriedJ,
         EITC_rt, EITC_c, EITC_prt, EITC_basic_frac,
         EITC_InvestIncome_c, EITC_excess_InvestIncome_rt,
         EITC_indiv, EITC_sep_filers_elig, c59660):
    """
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
      (E) Model-specific claiming approximation: filers with expected
          credit below `eitc_claim_thd` (default 0) are assumed not to
          claim.  No form analogue.

    Downstream: `c59660` is the records-bound EITC amount consumed by
    `IITAX` (Form 1040 line 27a, refundable credit) and reported in
    `taxcalc/cli/input_data_tests/tests.sh` baseline `*.tables`.

    Parameters
    ----------
    eitc_claim_thd: float
        Model-specific behavioral parameter: EITC amount below which
        the credit is assumed unclaimed (no form analogue)
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
    """
    # pylint: disable=too-many-branches

    # ---------------- (A) EIC Worksheet A: credit amount -------------
    phasein_rate = EITC_rt[EIC]
    max_amount = EITC_c[EIC]
    phaseout_rate = EITC_prt[EIC]
    po_start = EITC_ps[EIC]
    if MARS == 2:
        po_start += EITC_ps_addon_MarriedJ[EIC]

    if MARS == 2 and EITC_indiv:
        # reform-only: per-spouse EITC instead of filing-unit EITC
        eitc_p = EITCamount(EITC_basic_frac, phasein_rate, earned_p,
                            max_amount, po_start, earned_p, phaseout_rate)
        eitc_s = EITCamount(EITC_basic_frac, phasein_rate, earned_s,
                            max_amount, po_start, earned_s, phaseout_rate)
        eitc = eitc_p + eitc_s
    else:
        eitc = EITCamount(EITC_basic_frac, phasein_rate, earned,
                          max_amount, po_start, c00100, phaseout_rate)

    # ---------------- (B) Pub 596 Rule 11: childless age test --------
    # Filer (or, for MFJ, either spouse) with no qualifying children
    # must be in [EITC_MinEligAge, EITC_MaxEligAge] (25-64 under
    # current law).  age == 0 in the data is treated as eligible.
    if EIC == 0:
        h_age_elig = EITC_MinEligAge <= age_head <= EITC_MaxEligAge
        h_ok = age_head == 0 or h_age_elig
        if MARS == 2:
            s_age_elig = EITC_MinEligAge <= age_spouse <= EITC_MaxEligAge
            s_ok = age_spouse == 0 or s_age_elig
            if not (h_ok or s_ok):
                eitc = 0.
        else:
            if not h_ok:
                eitc = 0.
    c59660 = eitc

    # ---------------- (C) Pub 596 Rules 3 (MFS) and 10 (dependent) ---
    if (MARS == 3 and not EITC_sep_filers_elig) or DSI == 1:
        c59660 = 0.

    # ---------------- (D) Pub 596 Rule 6: investment-income cliff ----
    # IRC §32(i): no EITC if investment income exceeds the ceiling.
    # Modeled as a smooth phaseout; with EITC_excess_InvestIncome_rt
    # default 9e+99 the reduction immediately drives c59660 to 0.
    if c59660 > 0.:
        invinc = (e00400 + e00300 + e00600 +
                  max(0., c01000) + max(0., (e02000 - e26270)))
        if invinc > EITC_InvestIncome_c:
            red = EITC_excess_InvestIncome_rt * (invinc - EITC_InvestIncome_c)
            c59660 = max(0., c59660 - red)

    # ---------------- (E) Behavioral claiming approximation ----------
    # Not on the form: filers with expected credit < eitc_claim_thd
    # are assumed not to claim (default 0 = no suppression).
    if c59660 < eitc_claim_thd:
        c59660 = 0.

    return c59660


@iterate_jit(nopython=True)
def RefundablePayrollTaxCredit(was_plus_sey_p, was_plus_sey_s,
                               RPTC_c, RPTC_rt,
                               rptc_p, rptc_s, rptc):
    """
    Computes the Refundable Payroll Tax Credit (RPTC).

    Reform construct with no IRS form correspondence: RPTC is a
    Tax-Calculator-only credit designed to emulate a payroll-tax
    exemption via the refundable-credit side of Form 1040.  Per the
    `RPTC_c` policy-parameter description, positive values of `RPTC_c`
    and `RPTC_rt` together emulate a payroll-tax exemption whose
    implied earnings ceiling is `RPTC_c / RPTC_rt` per spouse.

    Inert under current law: `RPTC_c` and `RPTC_rt` both default to
    0.0 for all years (2013+), so `rptc_p = rptc_s = rptc = 0`.

    Body (per spouse): pre-phaseout credit = min(rate * earnings, cap),
    where "earnings" is `was_plus_sey_*` (gross wages-and-salaries plus
    the reform-only extra-OASDI taxable SE component) as produced by
    `EI_PayrollTax`.  The filing-unit total `rptc` is the sum of the
    two per-spouse credits.

    Calling order (calculator.py): invoked after `EITC` and before
    `PersonalTaxCredit` in the refundable-credit sequence.  Downstream
    consumer: `IITAX` subtracts `rptc` from total tax liability as a
    fully-refundable credit (Form 1040 line 31 / Schedule 3 line 13
    territory, modeled here as a standalone refundable item).

    Parameters
    ----------
    was_plus_sey_p: float
        Taxpayer's gross wages-and-salaries plus reform-only extra-OASDI
        taxable self-employment earnings (set by `EI_PayrollTax`).
    was_plus_sey_s: float
        Spouse's gross wages-and-salaries plus reform-only extra-OASDI
        taxable self-employment earnings (set by `EI_PayrollTax`).
    RPTC_c: float
        Per-spouse maximum refundable payroll tax credit (reform-only;
        default 0.0).
    RPTC_rt: float
        Phasein rate applied to per-spouse earnings before the cap
        (reform-only; default 0.0).
    rptc_p: float
        Records-bound output: RPTC for taxpayer.
    rptc_s: float
        Records-bound output: RPTC for spouse.
    rptc: float
        Records-bound output: RPTC for filing unit (`rptc_p + rptc_s`).

    Returns
    -------
    rptc_p: float
        RPTC for taxpayer.
    rptc_s: float
        RPTC for spouse.
    rptc: float
        RPTC for filing unit.
    """
    rptc_p = min(was_plus_sey_p * RPTC_rt, RPTC_c)
    rptc_s = min(was_plus_sey_s * RPTC_rt, RPTC_c)
    rptc = rptc_p + rptc_s
    return (rptc_p, rptc_s, rptc)


@iterate_jit(nopython=True)
def ChildDepTaxCredit(age_head, age_spouse, nu18, n24, MARS, c00100, XTOT, num,
                      c05800, e07260, CR_ResidentialEnergy_hc,
                      e07300, CR_ForeignTax_hc,
                      c07180,
                      c07230,
                      e07240, CR_RetirementSavings_hc,
                      c07200,
                      CTC_c, CTC_ps, CTC_prt, exact, ODC_c,
                      CTC_c_under6_bonus, nu06,
                      CTC_is_refundable, CTC_include17,
                      c07220, odc, codtc_limited):
    """
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
    """
    # Sch 8812 lines 1-3: modified AGI (no foreign earned income exclusion)
    modAGI = c00100
    # reform-only: redefine "qualifying child" as under 18 instead of under 17
    if CTC_include17:
        tu18 = int(age_head < 18)   # taxpayer is under age 18
        su18 = int(MARS == 2 and age_spouse < 18)  # spouse is under age 18
        childnum = n24 + max(0, nu18 - tu18 - su18 - n24)
    else:
        childnum = n24
    # Sch 8812 lines 4-5: tentative CTC (plus reform under-6 bonus)
    line5 = CTC_c * childnum + CTC_c_under6_bonus * nu06
    # Sch 8812 lines 6-7: tentative ODC
    line7 = ODC_c * max(0, XTOT - childnum - num)
    # Sch 8812 line 8: sum of tentative CTC and ODC
    line8 = line5 + line7
    # Sch 8812 lines 9-12: phase out using CTC_ps threshold and CTC_prt rate
    if line8 > 0. and modAGI > CTC_ps[MARS - 1]:
        excess = modAGI - CTC_ps[MARS - 1]
        if exact == 1:  # exact calculation as on tax forms
            excess = 1000. * math.ceil(excess / 1000.)
        line12 = max(0., line8 - CTC_prt * excess)
    else:
        line12 = line8
    if line12 > 0.:
        # Credit Limit Worksheet A: cap by c05800 minus other nonrefundable
        # credits already used (Sch 3 lines 1, 2, 3, 4, 5a, 6d)
        clwA_other = (e07300 * (1. - CR_ForeignTax_hc) +         # foreign tax
                      c07180 +                                   # CDCC
                      c07230 +                                   # education
                      e07240 * (1. - CR_RetirementSavings_hc) +  # ret savings
                      e07260 * (1. - CR_ResidentialEnergy_hc) +  # res energy
                      c07200)                                    # Schedule R
        clwA_limit = max(0., c05800 - clwA_other)
        if CTC_is_refundable:  # reform-only: skip tax-liability cap
            c07220 = line12 * line5 / line8
            odc = max(0., line12 - c07220)
            codtc_limited = max(0., line12 - c07220 - odc)
        else:
            # Sch 8812 line 14: smaller of line 12 or Credit Limit Worksheet A
            line14 = min(line12, clwA_limit)
            # split line 14 into CTC portion and ODC portion
            c07220 = line14 * line5 / line8
            odc = max(0., line14 - c07220)
            # tentative credit not absorbed by tax — passed to AdditionalCTC
            codtc_limited = max(0., line12 - line14)
    else:
        c07220 = 0.
        odc = 0.
        codtc_limited = 0.
    return (c07220, odc, codtc_limited)


@iterate_jit(nopython=True)
def PersonalTaxCredit(MARS, c00100, XTOT, nu18,
                      II_credit, II_credit_ps, II_credit_prt,
                      II_credit_nr, II_credit_nr_ps, II_credit_nr_prt,
                      RRC_c, RRC_ps, RRC_pe, RRC_prt, RRC_c_kids, RRC_c_unit,
                      personal_refundable_credit,
                      personal_nonrefundable_credit,
                      recovery_rebate_credit):
    """
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
    """
    # ---- Personal refundable credit (reform-only) ----
    ii_ps = II_credit_ps[MARS - 1]
    personal_refundable_credit = II_credit[MARS - 1]
    if II_credit_prt > 0. and c00100 > ii_ps:
        pout = II_credit_prt * (c00100 - ii_ps)
        personal_refundable_credit = max(0., personal_refundable_credit - pout)
    # ---- Personal nonrefundable credit (reform-only) ----
    ii_nr_ps = II_credit_nr_ps[MARS - 1]
    personal_nonrefundable_credit = II_credit_nr[MARS - 1]
    if II_credit_nr_prt > 0. and c00100 > ii_nr_ps:
        pout = II_credit_nr_prt * (c00100 - ii_nr_ps)
        personal_nonrefundable_credit = max(
            0., personal_nonrefundable_credit - pout
        )
    # ---- Recovery Rebate Credit (CARES Act 2020 EIP + ARPA 2021 RRC) ----
    # Historically Form 1040 line 30 (2020 + 2021); parameters are zeroed
    # for 2022+, so the three branches all return 0 under current law.
    rrc_ps = RRC_ps[MARS - 1]
    rrc_pe = RRC_pe[MARS - 1]
    rrc_unit_kids = RRC_c_unit[MARS - 1] + RRC_c_kids * nu18
    if c00100 < rrc_ps:
        # below phaseout start: full per-person (ARPA) + unit+kids (CARES)
        recovery_rebate_credit = RRC_c * XTOT + rrc_unit_kids
    elif 0 < c00100 < rrc_pe:
        # ARPA-only per-person linear ramp between rrc_ps and rrc_pe
        prt = (c00100 - rrc_ps) / (rrc_pe - rrc_ps)
        recovery_rebate_credit = RRC_c * XTOT * (1 - prt)
    else:
        # CARES-only linear phaseout of unit+kids above rrc_ps
        recovery_rebate_credit = max(
            0., rrc_unit_kids - RRC_prt * (c00100 - rrc_ps)
        )
    return (personal_refundable_credit, personal_nonrefundable_credit,
            recovery_rebate_credit)


@iterate_jit(nopython=True)
def AmOppCreditParts(exact, e87521, num, c00100, CR_AmOppRefundable_hc,
                     CR_AmOppNonRefundable_hc, c10960, c87668):
    """
    Applies a phaseout to the Form 8863, line 1, American Opportunity Credit
    amount, e87521, and then applies the 0.4 refundable rate.
    Logic corresponds to Form 8863, Part I.

    Parameters
    ----------
    exact: int
        Whether or not to do rounding of phaseout fraction
    e87521: float
        Total tentative AmOppCredit amount for all students.
        From Form 8863, line 1.
    num: int
        2 when MARS is 2 (married filing jointly), otherwise 1
    c00100: float
        Adjusted Gross Income (AGI)
    CR_AmOppRefundable_hc: float
        Refundable portion of the American Opportunity Credit haircut
    CR_AmOppNonRefundable_hc: float
        Nonrefundable portion of the American Opportunity Credit haircut
    c10960: float
        American Opportunity Credit refundable amount from Form 8863
    c87668: float
        American Opportunity Credit non-refundable amount from Form 8863

    Returns
    -------
    c10960: float
        American Opportunity Credit refundable amount from Form 8863
    c87668: float
        American Opportunity Credit non-refundable amount from Form 8863

    Notes
    -----
    Tax Law Paramters that are not parameterized:
        90000: American Opportunity phaseout income base
        10000: American Opportunity Credit phaseout income range length
        1/1000: American Opportunity Credit phaseout rate
        0.3: American Opportunity Credit refundable rate
    """
    if e87521 > 0.:
        c87658 = max(0., 90000. * num - c00100)
        c87660 = 10000. * num
        if exact == 1:  # exact calculation as on tax forms
            c87662 = 1000. * min(1., round(c87658 / c87660, 3))
        else:
            c87662 = 1000. * min(1., c87658 / c87660)
        c87664 = c87662 * e87521 / 1000.
        c10960 = 0.4 * c87664 * (1. - CR_AmOppRefundable_hc)
        c87668 = c87664 - c10960 * (1. - CR_AmOppNonRefundable_hc)
    else:
        c10960 = 0.
        c87668 = 0.
    return (c10960, c87668)


@iterate_jit(nopython=True)
def SchR(age_head, age_spouse, MARS, c00100,
         c05800, e07300, c07180, e02400, c02500, e01500, e01700, CR_SchR_hc,
         c07200):
    """
    Calculates Schedule R credit for the elderly and the disabled, c07200.

    Note that no Schedule R policy parameters are inflation indexed.

    Note that all Schedule R policy parameters are hard-coded, and therefore,
    are not able to be changed using Policy class parameters.

    Note that the CR_SchR_hc policy parameter allows the user to eliminate
    or reduce total Schedule R credits.

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
        Adjusted Gross Income (AGI)
    c05800: float
        Total (regular + AMT) income tax liability before credit
    e07300: float
        Foreign tax credit from Form 1116
    c07180: float
        Credit for child and dependent care expenses from Form 2441
    e02400: float
        Total social security (OASDI) benefits
    c02500: float
        Social security (OASDI) benefits included in AGI
    e01500: float
        Total pensions and annuities
    e01700: float
        Taxable pensions and annuities
    CR_SchR_hc: float
        Schedule R credit haircut
    c07200: float
        Schedule R credit for the elderly and the disabled

    Returns
    -------
    c07200: float
        Schedule R credit for the elderly and the disabled
    """
    if age_head >= 65 or (MARS == 2 and age_spouse >= 65):
        # calculate credit assuming nobody is disabled (so line12 = line10)
        if MARS == 2:
            if age_head >= 65 and age_spouse >= 65:
                schr12 = 7500.
            else:
                schr12 = 5000.
            schr15 = 10000.
        elif MARS == 3:
            schr12 = 3750.
            schr15 = 5000.
        elif MARS in (1, 4):
            schr12 = 5000.
            schr15 = 7500.
        else:
            schr12 = 0.
            schr15 = 0.
        # nontaxable portion of OASDI benefits, line 13a
        schr13a = max(0., e02400 - c02500)
        # nontaxable portion of pension benefits, line 13b
        # NOTE: the following approximation (required because of inadequate IRS
        #       data) will be accurate if all pensions are partially taxable
        #       or if all pensions are fully taxable.  But if a filing unit
        #       receives at least one partially taxable pension and at least
        #       one fully taxable pension, then the approximation in the
        #       following line is not exactly correct.
        schr13b = max(0., e01500 - e01700)
        schr13c = schr13a + schr13b
        schr16 = max(0., c00100 - schr15)
        schr17 = 0.5 * schr16
        schr18 = schr13c + schr17
        schr19 = max(0., schr12 - schr18)
        schr20 = 0.15 * schr19
        schr21 = max(0., (c05800 - e07300 - c07180))
        c07200 = min(schr20, schr21) * (1. - CR_SchR_hc)
    else:  # if not calculating Schedule R credit
        c07200 = 0.
    return c07200


@iterate_jit(nopython=True)
def EducationTaxCredit(exact, e87530, MARS, c00100, c05800,
                       e07300, c07180, c07200, c87668,
                       LLC_Expense_c, ETC_pe_Single, ETC_pe_Married,
                       CR_Education_hc,
                       c07230):
    """
    Computes Education Tax Credits (Form 8863) nonrefundable amount, c07230.
    Logic corresponds to Form 8863, Part II.

    Parameters
    ----------
    exact: int
        Whether or not to do rounding of phaseout fraction
    e87530: float
        Adjusted qualified lifetime learning expenses for all students
    MARS: int
        Filing (marital) status. (1=single, 2=joint, 3=separate,
                                  4=household-head, 5=widow(er))
    c00100: float
        Adjusted Gross Income (AGI)
    c05800: float
        Total (regular + AMT) income tax liability before credits
    e07300: float
        Foreign tax credit from Form 1116
    c07180: float
        Credit for child and dependent care expenses from Form 2441
    c07200: float
        Schedule R credit for the elderly and the disabled
    c87668: float
        American Opportunity Credit non-refundalbe amount from Form 8863
    LLC_Expense_c: float
        Lifetime learning credit expense limit
    ETC_pe_Single: float
        Education tax credit phaseout ends (single)
    ETC_pe_Married: float
        Education tax credit phaseout ends (married)
    CR_Education_hc: float
        Education Credits haircut
    c07230: float
        Education tax credits non-refundable amount from Form 8863

    Returns
    -------
    c07230: float
        Education tax credits non-refundable amount from Form 8863

    Notes
    -----
    Tax Law Parameters that are not parameterized:
        0.2: Lifetime Learning Credit ratio against expense
        10000.0: AGI range bewteen ETC_pe_Single and single phase-out start;
                 twice this amount for ETC_pe_Married
    """
    c87560 = 0.2 * min(e87530, LLC_Expense_c)
    # on the following credit phase-out law see:
    # https://www.law.cornell.edu/uscode/text/26/25A#d_1
    if MARS == 2:
        c87570 = ETC_pe_Married * 1000.
        c87600 = 20000.
    else:
        c87570 = ETC_pe_Single * 1000.
        c87600 = 10000.
    c87590 = max(0., c87570 - c00100)
    if exact == 1:  # exact calculation as on tax forms
        c87610 = min(1., round(c87590 / c87600, 3))
    else:
        c87610 = min(1., c87590 / c87600)
    c87620 = c87560 * c87610
    xline4 = max(0., c05800 - (e07300 + c07180 + c07200))
    xline5 = min(c87620, xline4)
    xline9 = max(0., c05800 - (e07300 + c07180 + c07200 + xline5))
    xline10 = min(c87668, xline9)
    c87680 = xline5 + xline10
    c07230 = c87680 * (1. - CR_Education_hc)
    return c07230


@iterate_jit(nopython=True)
def CharityCredit(e19800, e20100, c00100, CR_Charity_rt, CR_Charity_f,
                  CR_Charity_frt, MARS, charity_credit):
    """
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
    """
    total_charity = e19800 + e20100
    dollar_floor = CR_Charity_f[MARS - 1]
    floor = max(CR_Charity_frt * c00100, dollar_floor)
    eligible_giving = max(total_charity - floor, 0.)
    charity_credit = CR_Charity_rt * eligible_giving
    return charity_credit


@iterate_jit(nopython=True)
def NonrefundableCredits(c05800, e07240, e07260, e07300, e07400,
                         e07600, p08000, odc,
                         personal_nonrefundable_credit,
                         CTC_is_refundable,
                         CR_RetirementSavings_hc, CR_ForeignTax_hc,
                         CR_ResidentialEnergy_hc, CR_GeneralBusiness_hc,
                         CR_MinimumTax_hc, CR_OtherCredits_hc, charity_credit,
                         c07180, c07200, c07220, c07230, c07240,
                         c07260, c07300, c07400, c07600, c08000):
    """
    NonRefundableCredits function sequentially limits credits to tax liability.

    Parameters
    ----------
    c05800: float
        Total (regular + AMT) income tax liability before credits
    e07240: float
        Retirement savings contributions credit from Form 8880
    e07260: float
        Residential energy credit from Form 5695
    e07300: float
        Foreign tax credit from Form 1116
    e07400: float
        General business credit from Form 3800
    e07600: float
        Prior year minimum tax credit from Form 8801
    p08000: float
        Other tax credits
    odc: float
        Other Dependent Credit
    personal_nonrefundable_credit: float
        Personal nonrefundable credit
    CTC_is_refundable: bool
        Whether the child tax credit is fully refundable
    CR_RetirementSavings_hc: float
        Credit for retirement savings haircut
    CR_ForeignTax_hc: float
        Credit for foreign tax credit
    CR_ResidentialEnergy_hc: float
        Credit for residential energy haircut
    CR_GeneralBusiness_hc: float
        Credit for general business haircut
    CR_MinimumTax_hc: float
        Credit for previous year minimum tax credit haircut
    CR_OtherCredits_hc: float
        Other Credit haircut
    charity_credit: float
        Credit for charitable giving
    c07180: float
        Credit for child and dependent care expenses from Form 2441
    c07200: float
        Schedule R credit for the elderly and the disabled
    c07220: float
        Child tax credit (adjusted) from From 8812
    c07230: float
        Education tax credits non-refundable amount from Form 8863
    c07240: float
        Retirement savings credit - Form 8880
    c07260: float
        Residential energy credit - Form 5695
    c07300: float
        Foreign tax credit - Form 1116
    c07400: float
        General business credit - Form 3800
    c07600: float
        Prior year minimum tax credit - Form 8801
    c08000: float
        Other credits
    Returns
    -------
    c07180: float
        Credit for child and dependent care expenses from Form 2441
    c07200: float
        Schedule R credit for the elderly and the disabled
    c07220: float
        Child tax credit (adjusted) from From 8812
    c07230: float
        Education tax credits non-refundable amount from Form 8863
    c07240: float
        Retirement savings credit - Form 8880
    odc: float
        Other Dependent Credit
    c07260: float
        Residential energy credit - Form 5695
    c07300: float
        Foreign tax credit - Form 1116
    c07400: float
        General business credit - Form 3800
    c07600: float
        Prior year minimum tax credit - Form 8801
    c08000: float
        Other credits
    charity_credit: float
        Credit for charitable giving
    personal_nonrefundable_credit: float
        Personal nonrefundable credit
    """
    # limit tax credits to tax liability in order they are on 2015 1040 form
    avail = c05800
    # Foreign tax credit - Form 1116
    c07300 = min(e07300 * (1. - CR_ForeignTax_hc), avail)
    avail = avail - c07300
    # Child & dependent care expense credit
    c07180 = min(c07180, avail)
    avail = avail - c07180
    # Education tax credit
    c07230 = min(c07230, avail)
    avail = avail - c07230
    # Retirement savings credit - Form 8880
    c07240 = min(e07240 * (1. - CR_RetirementSavings_hc), avail)
    avail = avail - c07240
    # Child tax credit
    if not CTC_is_refundable:
        c07220 = min(c07220, avail)
        avail = avail - c07220
        # Other dependent credit
        odc = min(odc, avail)
        avail = avail - odc
    # Residential energy credit - Form 5695
    c07260 = min(e07260 * (1. - CR_ResidentialEnergy_hc), avail)
    avail = avail - c07260
    # General business credit - Form 3800
    c07400 = min(e07400 * (1. - CR_GeneralBusiness_hc), avail)
    avail = avail - c07400
    # Prior year minimum tax credit - Form 8801
    c07600 = min(e07600 * (1. - CR_MinimumTax_hc), avail)
    avail = avail - c07600
    # Schedule R credit
    c07200 = min(c07200, avail)
    avail = avail - c07200
    # Other credits
    c08000 = min(p08000 * (1. - CR_OtherCredits_hc), avail)
    avail = avail - c08000
    charity_credit = min(charity_credit, avail)
    avail = avail - charity_credit
    # Personal nonrefundable credit
    personal_nonrefundable_credit = min(personal_nonrefundable_credit, avail)
    avail = avail - personal_nonrefundable_credit
    return (c07180, c07200, c07220, c07230, c07240, odc,
            c07260, c07300, c07400, c07600, c08000, charity_credit,
            personal_nonrefundable_credit)


@iterate_jit(nopython=True)
def AdditionalCTC(actc_claim_thd, codtc_limited,
                  ACTC_c, n24, earned, ACTC_Income_thd,
                  ACTC_rt, nu06, ACTC_rt_bonus_under6family, ACTC_ChildNum,
                  CTC_is_refundable, CTC_include17, CTC_c,
                  age_head, age_spouse, MARS, nu18,
                  ptax_was, c03260, e09800, c59660, e11200,
                  c11070):
    """
    Calculates refundable Additional Child Tax Credit (ACTC), c11070,
    following Schedule 8812 Part II (Parts II-A, II-B, II-C).

    Parameters
    ----------
    actc_claim_thd: float
        ACTC amount below which ACTC is unclaimed
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
    """
    # Sch 8812 line 16a: leftover Part I tentative credit
    line16a = codtc_limited
    # Sch 8812 line 16b: max refundable amount = ACTC_c per qualifying child
    if CTC_is_refundable:  # reform-only: refundable portion handled in Part I
        line16b = 0.
    else:
        # reform-only: redefine "qualifying child" as under 18 instead
        #              of under 17
        if CTC_include17:
            tu18 = int(age_head < 18)   # taxpayer is under age 18
            su18 = int(MARS == 2 and age_spouse < 18)  # spouse is under age 18
            childnum = n24 + max(0, nu18 - tu18 - su18 - n24)
        else:
            childnum = n24
        line16b = min(ACTC_c, CTC_c) * childnum
    c11070 = 0.  # default if no refundable amount
    if line16a > 0. and line16b > 0.:
        # Sch 8812 line 17: smaller of line 16a or line 16b
        line17 = min(line16a, line16b)
        # Part II-A
        # Sch 8812 line 18a / line 20: earned income excess over threshold
        earned_excess = max(0., earned - ACTC_Income_thd)
        # reform-only: ACTC rate bonus for families with children under 6
        if nu06 == 0:
            ACTC_rate = ACTC_rt
        else:
            ACTC_rate = ACTC_rt + ACTC_rt_bonus_under6family
        # Sch 8812 line 20: ACTC_rt times earned-income excess
        line20 = ACTC_rate * earned_excess
        if childnum < ACTC_ChildNum:
            # Sch 8812 line 27 (Part II-C): smaller of line 17 or line 20
            if line20 > 0.:
                c11070 = min(line17, line20)
        else:  # childnum >= ACTC_ChildNum: consider Part II-B alternative
            if line20 >= line17:
                c11070 = line17
            else:  # Part II-B
                # Sch 8812 line 22: SS+Medicare+Add'l Medicare withheld
                line22 = 0.5 * ptax_was
                # Sch 8812 line 23: deductible SE tax + unreported FICA
                line23 = c03260 + e09800
                # Sch 8812 line 24: sum of lines 22 and 23
                line24 = line22 + line23
                # Sch 8812 line 25: EITC + excess SS/RRTA withheld
                line25 = c59660 + e11200
                # Sch 8812 line 26: line 24 minus line 25 (not less than 0)
                line26 = max(0., line24 - line25)
                # Sch 8812 line 27 (Part II-b3157
                #   min(line 17, max(line 20, line 26))
                line27 = max(line20, line26)
                c11070 = min(line17, line27)

    # approximate ACTC claiming behavior
    if c11070 < actc_claim_thd:
        c11070 = 0.

    return c11070


@iterate_jit(nopython=True)
def C1040(c05800, c07180, c07200, c07220, c07230, c07240, c07260, c07300,
          c07400, c07600, c08000, e09700, e09800, e09900, niit, setax,
          ptax_amc, othertaxes, c07100, c09200, odc, charity_credit,
          personal_nonrefundable_credit,
          CTC_is_refundable, ODC_is_refundable):
    """
    Computes total used nonrefundable credits, c07100, othertaxes, and
    income tax before refundable credits, c09200.

    Parameters
    ----------
    c05800: float
        Total (regular + AMT) income tax liability before credits
    c07180: float
        Credit for child and dependent care expenses from Form 2441
    c07200: float
        Schedule R credit for the elderly and the disabled
    c07220: float
        Child tax credit (adjusted) from Form 8812
    c07230: float
        Education tax credit non-refundable amount from Form 8863
    c07240: float
        Retirement savings credit - Form 8880
    c07260: float
        Residential energy credit - Form 5695
    c07300: float
        Foreign tax credit - Form 1116
    c07400: float
        General business credit - Form 3800
    c07600: float
        Prior year minimum tax credit - Form 8801
    c08000: float
        Other credits
    e09700: float
        Recapture of Investment Credit
    e09800: float
        Unreported payroll taxes from Form 4137 or 8919
    e09900: float
        Penalty tax on qualified retirement plans
    niit: float
        Net Investment Income Tax from Form 8960
    setax: float
        Self-employment tax
    ptax_amc: float
        Additional Medicare tax
    othertaxes: float
        Sum of niit, setax, ptax_amc, e09700, e09800, and e09900
    c07100: float
        Total non-refundable credits used to reduce positive tax liability
    c09200: float
        Income tax liabilities (including othertaxes) after non-refundable
        credits are used, but before refundable credits are applied
    odc: float
        Other Dependent Credit
    charity_credit: float
        Credit for charitable giving
    personal_nonrefundable_credit: float
        Personal nonrefundable credit

    Returns
    -------
    c07100: float
        Total non-refundable credits used to reduce positive tax liability
    othertaxes: float
        Sum of niit, e09700, e09800, and e09900
    c09200: float
        Income tax liabilities (including othertaxes) after non-refundable
        credits are used, but before refundable credits are applied
    """
    # total used nonrefundable credits (as computed in NonrefundableCredits)
    c07100 = (c07180 + c07200 + c07600 + c07300 + c07400 +
              c07220 * (1. - CTC_is_refundable) + c08000 +
              c07230 + c07240 + c07260 +
              odc * (1. - ODC_is_refundable) + charity_credit +
              personal_nonrefundable_credit)
    # tax after credits (2016 Form 1040, line 56)
    tax_net_nonrefundable_credits = max(0., c05800 - c07100)
    # tax (including othertaxes) before refundable credits
    othertaxes = e09700 + e09800 + e09900 + niit + setax + ptax_amc
    c09200 = othertaxes + tax_net_nonrefundable_credits
    return (c07100, othertaxes, c09200)


@iterate_jit(nopython=True)
def CTC_new(CTC_new_c, CTC_new_rt, CTC_new_c_under6_bonus,
            CTC_new_ps, CTC_new_prt, CTC_new_for_all, CTC_include17,
            CTC_new_refund_limited, CTC_new_refund_limit_payroll_rt,
            CTC_new_refund_limited_all_payroll, payrolltax, exact,
            n24, nu06, age_head, age_spouse, nu18, c00100, MARS, ptax_oasdi,
            c09200, ctc_new):
    """
    Computes new refundable child tax credit using specified parameters.

    Parameters
    ----------
    CTC_new_c: float
        New refundable child tax credit maximum amount per child
    CTC_new_rt: float
        New refundalbe child tax credit amount phasein rate
    CTC_new_c_under6_bonus: float
        Bonus new refundable child tax credit maximum for qualifying
        children under six
    CTC_new_ps: list
        New refundable child tax credit phaseout starting AGI
    CTC_new_prt: float
        New refundable child tax credit amount phaseout rate
    CTC_new_for_all: bool
        Whether or not maximum amount of the new refundable child tax credit
        is available to all
    CTC_new_refund_limited: bool
        New child tax credit refund limited to a decimal fraction of
        payroll taxes
    CTC_new_refund_limit_payroll_rt: float
        New child tax credit refund limit rate (decimal fraction of
        payroll taxes)
    CTC_new_refund_limited_all_payroll: bool
        New child tax credit refund limit applies to all FICA taxes, not
        just OASDI
    payrolltax: float
        Total (employee + employer) payroll tax liability
    exact: int
        Whether or not exact phase-out calculation is being done
    n24: int
        Number of children who are Child-Tax-Credit eligible, one
        condition for which is being under age 17
    nu06: int
        Number of dependents under 6 years old
    c00100: float
        Adjusted Gross Income (AGI)
    MARS: int
        Filing (marital) status. (1=single, 2=joint, 3=separate,
                                  4=household-head, 5=widow(er))
    ptax_oasdi: float
        Employee and employer OASDI FICA tax plus self employment tax
        Excludes HI FICA so positive ptax_oasdi is less than ptax_was + setax
    c09200: float
        Income tax liabilities (including othertaxes) after non-refundable
        credits are used, but before refundable credits are applied
    ctc_new: float
        New refundable child tax credit

    Returns
    -------
    ctc_new: float
        New refundable child tax credit
    """
    if CTC_include17:
        tu18 = int(age_head < 18)   # taxpayer is under age 18
        su18 = int(MARS == 2 and age_spouse < 18)  # spouse is under age 18
        childnum = n24 + max(0, nu18 - tu18 - su18 - n24)
    else:
        childnum = n24
    if childnum > 0:
        posagi = max(c00100, 0.)
        ctc_new = CTC_new_c * childnum + CTC_new_c_under6_bonus * nu06
        if not CTC_new_for_all:
            ctc_new = min(CTC_new_rt * posagi, ctc_new)
        ymax = CTC_new_ps[MARS - 1]
        if posagi > ymax:
            over = posagi - ymax
            if exact == 1:  # exact calculation as on tax form
                excess = math.ceil(over / 1000.) * 1000.
            else:  # smoothed calculation
                excess = over
            ctc_new_reduced = max(0., ctc_new - CTC_new_prt * excess)
            ctc_new = min(ctc_new, ctc_new_reduced)
        if ctc_new > 0. and CTC_new_refund_limited:
            refund_new = max(0., ctc_new - c09200)
            limit_new = CTC_new_refund_limit_payroll_rt * ptax_oasdi
            if CTC_new_refund_limited_all_payroll:
                limit_new = CTC_new_refund_limit_payroll_rt * payrolltax
            limited_new = max(0., refund_new - limit_new)
            ctc_new = max(0., ctc_new - limited_new)
    else:
        ctc_new = 0.
    return ctc_new


@iterate_jit(nopython=True)
def IITAX(c59660, c11070, c10960, personal_refundable_credit, ctc_new, rptc,
          c09200, payrolltax, CDCC_refund, recovery_rebate_credit,
          eitc, c07220, odc, CTC_is_refundable, ODC_is_refundable, refund,
          ctc_total, ctc_refundable, ctc_nonrefundable, iitax, combined):
    """
    Computes final taxes.

    Parameters
    ----------
    c59660: float
        EITC amount
    c11070: float
        Child tax credit (refunded) from Form 8812
    c10960: float
        American Opportunity Credit refundable amount from Form 8863
    personal_refundable_credit: float
        Personal refundable credit
    ctc_new: float
        New refundable child tax credit
    rptc: float
        Refundable Payroll Tax Credit for filing unit
    c09200: float
        Income tax liabilities (including othertaxes) after non-refundable
        credits are used, but before refundable credits are applied
    payrolltax: float
        Total (employee + employer) payroll tax liability
    eitc: float
        Earned Income Credit
    refund: float
        Total refundable income tax credits
    ctc_total: float
        Total CTC amount (c07220 + c11070 + odc + ctc_new)
    ctc_refundable: float
        Portion of total CTC amount that is refundable
    iitax: float
        Total federal individual income tax liability
    combined: float
        Sum of iitax and payrolltax and lumpsum_tax

    Returns
    -------
    eitc: float
        Earned Income Credit
    refund: float
        Total refundable income tax credits
    ctc_total: float
        Total CTC amount (c07220 + c11070 + odc + ctc_new)
    ctc_refundable: float
        Portion of total CTC amount that is refundable
    ctc_nonrefundable: float
        Portion of total CTC amount that is nonrefundable
    iitax: float
        Total federal individual income tax liability
    combined: float
        Sum of iitax and payrolltax and lumpsum_tax
    """
    eitc = c59660
    if CTC_is_refundable:
        ctc_refund = c07220
    else:
        ctc_refund = 0.
    if ODC_is_refundable:
        odc_refund = odc
    else:
        odc_refund = 0.
    refund = (eitc + c11070 + c10960 + CDCC_refund + recovery_rebate_credit +
              personal_refundable_credit + ctc_new + rptc + ctc_refund +
              odc_refund)
    ctc_total = c07220 + c11070 + odc + ctc_new
    ctc_refundable = ctc_refund + c11070 + odc_refund + ctc_new
    ctc_nonrefundable = max(0., ctc_total - ctc_refundable)
    iitax = c09200 - refund
    combined = iitax + payrolltax
    return (eitc, refund, ctc_total, ctc_refundable, ctc_nonrefundable,
            iitax, combined)


@iterate_jit(nopython=True)
def FairShareTax(c00100, MARS, ptax_was, setax, ptax_amc,
                 FST_AGI_trt, FST_AGI_thd_lo, FST_AGI_thd_hi,
                 fstax, iitax, combined, surtax):
    """
    Computes Fair Share Tax, or "Buffet Rule", types of reforms.

    Parameters
    ----------
    c00100: float
        Adjusted Gross Income (AGI)
    MARS: int
        Filing (marital) status. (1=single, 2=joint, 3=separate,
                                  4=household-head, 5=widow(er))
    ptax_was: float
        Employee and employer OASDI plus HI FICA tax
    setax: float
        Self-employment tax
    ptax_amc: float
        Additional Medicare Tax
    FST_AGI_trt: float
        New minimum tax; rate as a decimal fraction of AGI
    FST_AGI_thd_lo: list
        Minimum AGI needed to be subject to the new minimum tax
    FST_AGI_thd_hi: list
        AGI level at which the New Minimum Tax is fully phased in
    fstax: float
        Fair Share Tax amount
    iitax: float
        Total federal individual income tax liability
    combined: float
        Sum of iitax and payrolltax and lumpsum_tax
    surtax: float
        Individual income tax subtotal augmented by fstax

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
    """
    if FST_AGI_trt > 0. and c00100 >= FST_AGI_thd_lo[MARS - 1]:
        employee_share = 0.5 * ptax_was + 0.5 * setax + ptax_amc
        fstax = max(c00100 * FST_AGI_trt - iitax - employee_share, 0.)
        thd_gap = max(FST_AGI_thd_hi[MARS - 1] - FST_AGI_thd_lo[MARS - 1], 0.)
        if thd_gap > 0. and c00100 < FST_AGI_thd_hi[MARS - 1]:
            fstax *= (c00100 - FST_AGI_thd_lo[MARS - 1]) / thd_gap
        iitax += fstax
        combined += fstax
        surtax += fstax
    else:
        fstax = 0.
    return (fstax, iitax, combined, surtax)


@iterate_jit(nopython=True)
def LumpSumTax(DSI, num, XTOT,
               LST,
               lumpsum_tax, combined):
    """
    Computes lump-sum tax and add it to combined taxes.

    Parameters
    ----------
    DSI: int
        1 if claimed as dependent on another return, otherwise 0
    num: int
        2 when MARS is 2 (married filing jointly); otherwise 1
    XTOT: int
        Total number of exemptions for filing unit
    LST: float
        Dollar amount of lump-sum tax
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
    """
    if LST == 0.0 or DSI == 1:
        lumpsum_tax = 0.
    else:
        lumpsum_tax = LST * max(num, XTOT)
    combined += lumpsum_tax
    return (lumpsum_tax, combined)


@iterate_jit(nopython=True)
def ExpandIncome(e00200, pencon_p, pencon_s, e00300, e00400, e00600,
                 e00700, e00800, e00900, e01100, e01200, e01400, e01500,
                 e02000, e02100, p22250, p23250, cmbtp, ptax_was,
                 benefit_value_total, expanded_income):
    """
    Calculates expanded_income from component income types.

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
      Tax-exempt interest income
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
    p23250:float
      Schedule D net long term capital gains/losses
    cmbtp: float
      Estimate of inome on (AMT) Form 6251 but not in AGI
    ptax_was: float
      Employee and employer OASDI and HI FICA tax
    benefit_value_total: float
      Consumption value of all benefits received by tax unit, which
      is included in expanded income
    expanded_income: float
      Broad income measure that includes benefit_value_total

    Returns
    -------
    expanded_income: float
      Broad income measure that includes benefit_value_total
    """
    expanded_income = (
        e00200 +  # wage and salary income net of DC pension contributions
        pencon_p +  # tax-advantaged DC pension contributions for taxpayer
        pencon_s +  # tax-advantaged DC pension contributions for spouse
        e00300 +  # taxable interest income
        e00400 +  # non-taxable interest income
        e00600 +  # dividends
        e00700 +  # state and local income tax refunds
        e00800 +  # alimony received
        e00900 +  # Sch C business net income/loss
        e01100 +  # capital gain distributions not reported on Sch D
        e01200 +  # Form 4797 other net gain/loss
        e01400 +  # taxable IRA distributions
        e01500 +  # total pension & annuity income (including DB-plan benefits)
        e02000 +  # Sch E total rental, ..., partnership, S-corp income/loss
        e02100 +  # Sch F farm net income/loss
        p22250 +  # Sch D: net short-term capital gain/loss
        p23250 +  # Sch D: net long-term capital gain/loss
        cmbtp +  # other AMT taxable income items from Form 6251
        0.5 * ptax_was +  # employer share of FICA taxes on wages/salaries
        benefit_value_total  # consumption value of all benefits received;
        # see the BenefitPrograms function in this file for details on
        # exactly how the benefit_value_total variable is computed
    )
    return expanded_income


@iterate_jit(nopython=True)
def AfterTaxIncome(combined, expanded_income, aftertax_income):
    """
    Calculates after-tax expanded income.

    Parameters
    ----------
    combined: float
        Sum of iitax and payrolltax and lumpsum_tax
    expanded_income: float
        Broad income measure that includes benefit_value_total
    aftertax_income: float
        After tax income is equal to expanded_income minus combined

    Returns
    -------
    aftertax_income: float
        After tax income is equal to expanded_income minus combined
    """
    aftertax_income = expanded_income - combined
    return aftertax_income
