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
    Calculate total government cost and consumption value of benefits
    delivered by non-repealed benefit programs.

    Parameters
    ----------
    calc: Calculator object
        calc represents the reform while self represents the baseline

    Returns
    -------
    None:
        The function modifies calc
    """
    # zero out benefits delivered by repealed programs
    zero = np.zeros(calc.array_len)
    if calc.policy_param('BEN_housing_repeal'):
        calc.array('housing_ben', zero)
    if calc.policy_param('BEN_ssi_repeal'):
        calc.array('ssi_ben', zero)
    if calc.policy_param('BEN_snap_repeal'):
        calc.array('snap_ben', zero)
    if calc.policy_param('BEN_tanf_repeal'):
        calc.array('tanf_ben', zero)
    if calc.policy_param('BEN_vet_repeal'):
        calc.array('vet_ben', zero)
    if calc.policy_param('BEN_wic_repeal'):
        calc.array('wic_ben', zero)
    if calc.policy_param('BEN_mcare_repeal'):
        calc.array('mcare_ben', zero)
    if calc.policy_param('BEN_mcaid_repeal'):
        calc.array('mcaid_ben', zero)
    if calc.policy_param('BEN_oasdi_repeal'):
        calc.array('e02400', zero)
    if calc.policy_param('BEN_ui_repeal'):
        calc.array('e02300', zero)
    if calc.policy_param('BEN_other_repeal'):
        calc.array('other_ben', zero)
    # calculate government cost of all benefits
    cost = np.array(
        calc.array('housing_ben') +
        calc.array('ssi_ben') +
        calc.array('snap_ben') +
        calc.array('tanf_ben') +
        calc.array('vet_ben') +
        calc.array('wic_ben') +
        calc.array('mcare_ben') +
        calc.array('mcaid_ben') +
        calc.array('e02400') +
        calc.array('e02300') +
        calc.array('ubi') +
        calc.array('other_ben')
    )
    calc.array('benefit_cost_total', cost)
    # calculate consumption value of all benefits
    # (assuming that cash benefits have full value)
    value = np.array(
        calc.array('housing_ben') * calc.consump_param('BEN_housing_value') +
        calc.array('ssi_ben') +
        calc.array('snap_ben') * calc.consump_param('BEN_snap_value') +
        calc.array('tanf_ben') * calc.consump_param('BEN_tanf_value') +
        calc.array('vet_ben') * calc.consump_param('BEN_vet_value') +
        calc.array('wic_ben') * calc.consump_param('BEN_wic_value') +
        calc.array('mcare_ben') * calc.consump_param('BEN_mcare_value') +
        calc.array('mcaid_ben') * calc.consump_param('BEN_mcaid_value') +
        calc.array('e02400') +
        calc.array('e02300') +
        calc.array('ubi') +
        calc.array('other_ben') * calc.consump_param('BEN_other_value')
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
        Wages, salaries, and tips for taxpayer net of pension contributions
    e00200s: float
        Wages, salaries, and tips for spouse net of pension contributions
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
    # compute sey and its individual components
    sey_p = e00900p + e02100p + k1bx14p
    sey_s = e00900s + e02100s + k1bx14s
    sey = sey_p + sey_s  # total self-employment income for filing unit

    # compute gross wage and salary income ('was' denotes 'wage and salary')
    gross_ws_p = e00200p + pencon_p
    gross_ws_s = e00200s + pencon_s

    # compute taxable gross earnings for OASDI FICA
    txearn_was_p = min(SS_Earnings_c, gross_ws_p)
    txearn_was_s = min(SS_Earnings_c, gross_ws_s)

    # compute OASDI and HI payroll taxes on wage-and-salary income, FICA
    ptax_ss_ws_p = (FICA_ss_trt_employer + FICA_ss_trt_employee) * txearn_was_p
    ptax_ss_ws_s = (FICA_ss_trt_employer + FICA_ss_trt_employee) * txearn_was_s
    ptax_mc_ws_p = (FICA_mc_trt_employer + FICA_mc_trt_employee) * gross_ws_p
    ptax_mc_ws_s = (FICA_mc_trt_employer + FICA_mc_trt_employee) * gross_ws_s
    ptax_was = ptax_ss_ws_p + ptax_ss_ws_s + ptax_mc_ws_p + ptax_mc_ws_s

    # compute taxable self-employment income for OASDI SECA
    sey_frac = (
        1.0 - 0.5 *
        (FICA_ss_trt_employer + FICA_ss_trt_employee +
         FICA_mc_trt_employer + FICA_mc_trt_employee)
    )
    txearn_sey_p = min(max(0., sey_p * sey_frac), SS_Earnings_c - txearn_was_p)
    txearn_sey_s = min(max(0., sey_s * sey_frac), SS_Earnings_c - txearn_was_s)

    # compute self-employment tax on taxable self-employment income, SECA
    setax_ss_p = (FICA_ss_trt_employer + FICA_ss_trt_employee) * txearn_sey_p
    setax_ss_s = (FICA_ss_trt_employer + FICA_ss_trt_employee) * txearn_sey_s
    setax_mc_p = (
        (FICA_mc_trt_employer + FICA_mc_trt_employee) *
        max(0., sey_p * sey_frac)
    )
    setax_mc_s = (
        (FICA_mc_trt_employer + FICA_mc_trt_employee) *
        max(0., sey_s * sey_frac)
    )
    setax_p = setax_ss_p + setax_mc_p
    setax_s = setax_ss_s + setax_mc_s
    setax = setax_p + setax_s
    # no setax if self-employment income is low
    if sey * sey_frac > SECA_Earnings_thd:
        setax = setax_p + setax_s
    else:
        setax = 0.0

    # compute extra OASDI payroll taxes on the portion of the sum
    # of wage-and-salary income and taxable self employment income
    # that exceeds SS_Earnings_thd
    sey_frac = 1.0 - 0.5 * (FICA_ss_trt_employer + FICA_ss_trt_employee)
    was_plus_sey_p = gross_ws_p + max(0., sey_p * sey_frac)
    was_plus_sey_s = gross_ws_s + max(0., sey_s * sey_frac)
    extra_ss_income_p = max(0., was_plus_sey_p - SS_Earnings_thd)
    extra_ss_income_s = max(0., was_plus_sey_s - SS_Earnings_thd)
    extra_payrolltax = (
        extra_ss_income_p * (FICA_ss_trt_employer + FICA_ss_trt_employee) +
        extra_ss_income_s * (FICA_ss_trt_employer + FICA_ss_trt_employee)
    )

    # compute part of total payroll taxes for filing unit
    payrolltax = ptax_was + extra_payrolltax

    # compute OASDI part of payroll taxes
    ptax_oasdi = (ptax_ss_ws_p + ptax_ss_ws_s +
                  setax_ss_p + setax_ss_s +
                  extra_payrolltax)

    # compute earned* variables and AGI deduction for
    # "employer share" of self-employment tax, c03260
    # Note: c03260 is the amount on 2015 Form 1040, line 27
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
    Computes dependent-care above-the-line deduction.

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

    if earned <= ALD_Dependents_thd[MARS - 1]:
        care_deduction = (((1. - ALD_Dependents_hc) * nu13 *
                           ALD_Dependents_Child_c) +
                          ((1. - ALD_Dependents_hc) * elderly_dependents *
                           ALD_Dependents_Elder_c))
    else:
        care_deduction = 0.
    return care_deduction


@iterate_jit(nopython=True)
def Adj(e03150, e03210, c03260,
        e03270, e03300, e03400, e03500, e00800,
        e03220, e03230, e03240, e03290, care_deduction,
        ALD_StudentLoan_hc, ALD_SelfEmp_HealthIns_hc, ALD_KEOGH_SEP_hc,
        ALD_EarlyWithdraw_hc, ALD_AlimonyPaid_hc, ALD_AlimonyReceived_hc,
        ALD_EducatorExpenses_hc, ALD_HSADeduction_hc, ALD_IRAContributions_hc,
        ALD_DomesticProduction_hc, ALD_Tuition_hc,
        MARS, earned,
        overtime_income, ALD_OvertimeIncome_hc, ALD_OvertimeIncome_c,
        ALD_OvertimeIncome_ps, ALD_OvertimeIncome_prt,
        tip_income, ALD_TipIncome_hc, ALD_TipIncome_c,
        ALD_TipIncome_ps, ALD_TipIncome_prt,
        c02900, ALD_OvertimeIncome, ALD_TipIncome):
    """
    Adj calculates Form 1040 AGI adjustments (i.e., Above-the-Line Deductions).

    Parameters
    -----
    e03210: float
        Student loan interest paid
    e03220: float
        Educator expenses
    e03150: float
        Total deductible IRA plan contributions
    e03230: float
        Tuition and fees (Form 8917)
    e03240: float
        Domestic production activity deduction (Form 8903)
    c03260: float
        Self-employment tax deduction (after haircut)
    e03270: float
        Self-employed health insurance premiums
    e03290: float
        HSA deduction (Form 8889)
    e03300: float
        Total deductible KEOGH/SEP/SIMPLE/etc. plan contributions
    e03400: float
        Penalty on early withdrawal of savings deduction
    e03500: float
        Alimony paid
    e00800: float
        Alimony received
    care_deduction: float
        Dependent care expense deduction
    ALD_StudentLoan_hc: float
        Student loan interest deduction haircut
    ALD_SelfEmp_HealthIns_hc: float
        Self-employed h.i. deduction haircut
    ALD_KEOGH_SEP_hc: float
        KEOGH/etc. plan contribution deduction haircut
    ALD_EarlyWithdraw_hc: float
        Penalty on early withdrawal deduction haricut
    ALD_AlimonyPaid_hc: float
        Alimony paid deduction haircut
    ALD_AlimonyReceived_hc: float
        Alimony received deduction haircut
    ALD_EducatorExpenses_hc: float
        Eductor expenses haircut
    ALD_HSADeduction_hc: float
        HSA Deduction haircut
    ALD_IRAContributions_hc: float
        IRA Contribution haircut
    ALD_DomesticProduction_hc: float
        Domestic production haircut
    ALD_Tuition_hc: float
        Tuition and fees haircut
    MARS: int
        Filing marital status (1=single, 2=joint, 3=separate,
                               4=household-head, 5=widow(er))
    earned: float
        Earned income used to phase-out ALD_OvertimeIncome and ALD_TipIncome
    overtime_income: float
        Overtime income qualified for an above-the-line deduction
    ALD_OvertimeIncome_hc: float
        ALD_OvertimeIncome haircut
    ALD_OvertimeIncome_c: list[float]
        ALD_OvertimeIncome cap
    ALD_OvertimeIncome_ps: list[float]
        ALD_OvertimeIncome phase-out earned income start
    ALD_OvertimeIncome_prt: float
        ALD_OvertimeIncome phase-out rate
    tip_income: float
        Tip income qualified for an above-the-line deduction
    ALD_TipIncome_hc: float
        ALD_TipIncome haircut
    ALD_TipIncome_c: list[float]
        ALD_TipIncome cap
    ALD_TipIncome_ps: list[float]
        ALD_TipIncome phase-out earned income start
    ALD_TipIncome_prt: float
        ALD_TipIncome phase-out rate

    Returns
    -------
    c02900: float
        Total of all "above the line" income adjustments to get AGI
    ALD_OvertimeIncome: float
        Overtime ALD amount included in c02900
    ALD_TipIncome: float
        Tip ALD amount included in c02900
    """
    # Form 2555 foreign earned income exclusion is assumed to be zero
    # Form 1040 adjustments that are included in expanded income:
    c02900 = ((1. - ALD_StudentLoan_hc) * e03210 +
              c03260 +
              (1. - ALD_EarlyWithdraw_hc) * e03400 +
              (1. - ALD_AlimonyPaid_hc) * e03500 +
              (1. - ALD_AlimonyReceived_hc) * e00800 +
              (1. - ALD_EducatorExpenses_hc) * e03220 +
              (1. - ALD_Tuition_hc) * e03230 +
              (1. - ALD_DomesticProduction_hc) * e03240 +
              (1. - ALD_HSADeduction_hc) * e03290 +
              (1. - ALD_SelfEmp_HealthIns_hc) * e03270 +
              (1. - ALD_IRAContributions_hc) * e03150 +
              (1. - ALD_KEOGH_SEP_hc) * e03300 +
              care_deduction)
    # calculate ALD_OvertimeIncome
    ALD_OvertimeIncome = 0.
    if overtime_income > 0. and ALD_OvertimeIncome_hc < 1.0:
        ded = min(overtime_income, ALD_OvertimeIncome_c[MARS - 1])
        po_start = ALD_OvertimeIncome_ps[MARS - 1]
        if earned > po_start:
            excess = earned - po_start
            po_amount = excess * ALD_OvertimeIncome_prt
            ded = max(0., ded - po_amount)
        ALD_OvertimeIncome = ded
    # calculate ALD_TipIncome
    ALD_TipIncome = 0.
    if tip_income > 0. and ALD_TipIncome_hc < 1.0:
        ded = min(tip_income, ALD_TipIncome_c[MARS - 1])
        po_start = ALD_TipIncome_ps[MARS - 1]
        if earned > po_start:
            excess = earned - po_start
            po_amount = excess * ALD_TipIncome_prt
            ded = max(0., ded - po_amount)
        ALD_TipIncome = ded
    # return results
    c02900 += ALD_OvertimeIncome + ALD_TipIncome
    return (c02900, ALD_OvertimeIncome, ALD_TipIncome)


@iterate_jit(nopython=True)
def ALD_InvInc_ec_base(p22250, p23250, sep,
                       e00300, e00600, e01100, e01200, MARS,
                       invinc_ec_base, Capital_loss_limitation):
    """
    Computes invinc_ec_base.

    Parameters
    ----------
    p22250: float
        Net short-term capital gails/losses (Schedule D)
    p23250: float
        Net long-term capital gains/losses (Schedule D)
    sep: int
        2 when MARS is 3 (married filing separately); otherwise 1
    e00300: float
        Taxable interest income
    e00600: float
        Ordinary dividends included in AGI
    e01100: float
        Capital gains distributions not reported on Schedule D
    e01200: float
        Other net gain/loss from Form 4797
    MARS: int
        Filing marital status (1=single, 2=joint, 3=separate,
                               4=household-head, 5=widow(er))
    invinc_ec_base: float
        Exclusion of investment income from AGI
    Capital_loss_limitation: float
        Limitation on capital losses that are deductible

    Returns
    -------
    invinc_ec_base: float
        Exclusion of investment income from AGI
    """
    # limitation on net short-term and long-term capital losses
    cgain = max(
        (-1 * Capital_loss_limitation[MARS - 1] / sep), p22250 + p23250
    )
    # compute exclusion of investment income from AGI
    invinc_ec_base = e00300 + e00600 + cgain + e01100 + e01200
    return invinc_ec_base


@iterate_jit(nopython=True)
def CapGains(p23250, p22250, sep, ALD_StudentLoan_hc,
             ALD_InvInc_ec_rt, invinc_ec_base,
             e00200, e00300, e00600, e00650, e00700, e00800,
             CG_nodiff, CG_ec, CG_reinvest_ec_rt, Capital_loss_limitation,
             ALD_BusinessLosses_c, MARS,
             e00900, e01100, e01200, e01400, e01700, e02000, e02100,
             e02300, e00400, e02400, c02900, e03210, e03230, e03240,
             c01000, c23650, ymod, ymod1, invinc_agi_ec):
    """
    CapGains function: ...

    Parameters
    ----------
    p23250: float
        Net long-term capital gains/losses (Schedule D)
    p22250: float
        Net short-term capital gails/losses (Schedule D)
    sep: int
        2 when MARS is 3 (married filing separately); otherwise 1
    ALD_StudentLoan_hc: float
        Student loan interest deduction haircut
    ALD_InvInc_ec_rt: float
        Investment income exclusion rate haircut
    invinc_ec_base: float
        Exclusion of investment income from AGI
    e00200: float
        Wages, salaries, tips for filing unit net of pension contributions
    e00300: float
        Taxable interest income
    e00600: float
        Ordinary dividends included in AGI
    e00650: float
        Qualified dividends included in ordinary dividends
    e00700: float
        Taxable refunds of state and local income taxes
    e00800: float
        Alimony received
    CG_nodiff: bool
        Long term capital gains and qualified dividends taxed no
        differently than regular taxable income
    CG_ec: float
        Dollar amount of all capital gains and qualified dividends that are
        excluded from AGI
    CG_reinvest_ec_rt: float
        Fraction of all capital gains and qualified dividends in excess
        of the dollar exclusion that are excluded from AGI
    Capital_loss_limitation: float
        Limitation on capital losses that are deductible
    ALD_BusinessLosses_c: list
        Maximm amount of business losses deductible
    MARS: int
        Filing marital status (1=single, 2=joint, 3=separate,
                               4=household-head, 5=widow(er))
    e00900: float
        Schedule C business net profit/loss for filing unit
    e01100: float
        Capital gain distributions not reported on Schedule D
    e01200: float
        Other net gain/loss from Form 4797
    e01400: float
        Taxable IRA distributions
    e01700: float
        Taxable pensions and annunities
    e02000: float
        Schedule E total rental, royalty, partnership, S-corporation,
        etc, income/loss (includes e26270 and e27200)
    e02100: float
        Farm net income/loss for filing unit from Schedule F
    e02300: float
        Unemployment insurance benefits
    e00400: float
        Tax-exempt interest income
    e02400: float
        Total social security (OASDI) benefits
    c02900: float
        Total of all "above the line" income adjustments to get AGI
    e03210: float
        Student loan interest
    e03230: float
        Tuition and fees from Form 8917
    e03240: float
        Domestic production activities from Form 8903
    c01000: float
        Limitation on capital losses
    c23650: float
        Net capital gains (long and short term) before exclusion
    ymod: float
        Variable that is used in OASDI benefit taxation logic
    ymod1: float
        Variable that is included in AGI
    invinc_agi_ec: float
        Exclusion of investment income from AGI

    Returns
    -------
    c01000: float
        Limitation on capital losses
    c23650: float
        Net capital gains (long and short term) before exclusion
    ymod: float
        Variable that is used in OASDI benefit taxation logic
    ymod1: float
        Variable that is included in AGI
    invinc_agi_ec: float
        Exclusion of investment income from AGI
    """
    # net capital gain (long term + short term) before exclusion
    c23650 = p23250 + p22250
    # limitation on capital losses
    c01000 = max((-1 * Capital_loss_limitation[MARS - 1] / sep), c23650)
    # compute total investment income
    invinc = e00300 + e00600 + c01000 + e01100 + e01200
    # compute exclusion of investment income from AGI
    invinc_agi_ec = ALD_InvInc_ec_rt * max(0., invinc_ec_base)
    # compute ymod1 variable that is included in AGI
    ymod1 = (e00200 + e00700 + e00800 + e01400 + e01700 +
             invinc - invinc_agi_ec + e02100 + e02300 +
             max(e00900 + e02000, -ALD_BusinessLosses_c[MARS - 1]))
    if CG_nodiff:
        # apply QDIV+CG exclusion if QDIV+LTCG receive no special tax treatment
        qdcg_pos = max(0., e00650 + c01000)
        qdcg_exclusion = (min(CG_ec, qdcg_pos) +
                          CG_reinvest_ec_rt * max(0., qdcg_pos - CG_ec))
        ymod1 = max(0., ymod1 - qdcg_exclusion)
        invinc_agi_ec += qdcg_exclusion
    # compute ymod variable that is used in OASDI benefit taxation logic
    ymod2 = e00400 + (0.50 * e02400) - c02900
    ymod3 = (1. - ALD_StudentLoan_hc) * e03210 + e03230 + e03240
    ymod = ymod1 + ymod2 + ymod3
    return (c01000, c23650, ymod, ymod1, invinc_agi_ec)


@iterate_jit(nopython=True)
def SSBenefits(MARS, ymod, e02400, SS_all_in_agi, SS_thd1, SS_thd2,
               SS_percentage1, SS_percentage2, c02500):
    """
    Calculates OASDI benefits included in AGI, c02500.

    Parameters
    ----------
    MARS: int
        Filing marital status (1=single, 2=joint, 3=separate,
                               4=household-head, 5=widow(er))
    ymod: float
        Variable that is used in OASDI benefit taxation logic
    e02400: float
        Total social security (OASDI) benefits
    SS_all_in_agi: bool
        Whether all social security benefits are included in AGI
    SS_thd1: list
        Threshold for social security benefit taxability (1)
    SS_thd2: list
        Threshold for social security benefit taxability (2)
    SS_percentage1: float
        Social security taxable income decimal fraction (1)
    SS_percentage2: float
        Social security taxable income decimal fraction (2)
    c02500: float
        Social security (OASDI) benefits included in AGI

    Returns
    -------
    c02500: float
        Social security (OASDI) benefits included in AGI
    """
    if ymod < SS_thd1[MARS - 1]:
        c02500 = 0.
    elif ymod < SS_thd2[MARS - 1]:
        c02500 = SS_percentage1 * min(ymod - SS_thd1[MARS - 1], e02400)
    else:
        c02500 = min(SS_percentage2 * (ymod - SS_thd2[MARS - 1]) +
                     SS_percentage1 *
                     min(e02400, SS_thd2[MARS - 1] -
                         SS_thd1[MARS - 1]), SS_percentage2 * e02400)
    if SS_all_in_agi:
        c02500 = e02400
    return c02500


@iterate_jit(nopython=True)
def UBI(nu18, n1820, n21, UBI_u18, UBI_1820, UBI_21, UBI_ecrt,
        ubi, taxable_ubi, nontaxable_ubi):
    """
    Calculates total and taxable Universal Basic Income (UBI) amount.

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
        Fraction of UBI benefits that are not included in AGI
    ubi: float
        Total UBI received by the tax unit (is included in expanded_income)
    taxable_ubi: float
        Amount of UBI that is taxable (is added to AGI)
    nontaxable_ubi: float
        Amount of UBI that is nontaxable

    Returns
    -------
    ubi: float
        Total UBI received by the tax unit (is included in expanded_income)
    taxable_ubi: float
        Amount of UBI that is taxable (is added to AGI)
    nontaxable_ubi: float
        Amount of UBI that is nontaxable
    """
    ubi = nu18 * UBI_u18 + n1820 * UBI_1820 + n21 * UBI_21
    taxable_ubi = ubi * (1. - UBI_ecrt)
    nontaxable_ubi = ubi - taxable_ubi
    return ubi, taxable_ubi, nontaxable_ubi


@iterate_jit(nopython=True)
def AGI(ymod1, c02500, c02900, XTOT, MARS, sep, DSI, exact, nu18, taxable_ubi,
        II_em, II_em_ps, II_em_prt, II_no_em_nu18,
        e02300, UI_thd, UI_em, c00100, pre_c04600, c04600):
    """
    Computes Adjusted Gross Income (AGI), c00100, and
    compute personal exemption amount, c04600.

    Parameters
    ----------
    ymod1: float
        Variable that is included in AGI
    c02500: float
        Social security (OASDI) benefits included in AGI
    c02900: float
        Total of all "above the line" income adjustments to get AGI
    XTOT: int
        Total number of exemptions for filing unit
    MARS: int
        Filing marital status (1=single, 2=joint, 3=separate,
                               4=household-head, 5=widow(er))
    sep: int
        2 when MARS is 3 (married filing separately); otherwise 1
    DSI: int
        1 if claimed as dependent on another return; otherwise 0
    exact: int
        Whether or not to do rounding of phaseout fraction
    nu18: int
        Number of people in the tax unit under 18
    taxable_ubi: float
        Amount of UBI that is taxable (is added to AGI)
    II_em: float
        Personal and dependent exemption amount
    II_em_ps: list
        Personal exemption phaseout starting income
    II_em_prt: float
        Personal exemption phaseout rate
    II_no_em_nu18: float
        Repeal personal exemptions for dependents under age 18
    e02300: float
        Unemployment compensation
    UI_thd: list
        AGI threshold for unemployment compensation exclusion
    UI_em: float
        Amount of unemployment compensation excluded from AGI
    c00100: float
        Adjusted Gross Income (AGI)
    pre_c04600: float
        Personal exemption before phase-out
    c04600: float
        Personal exemptions after phase-out

    Returns
    -------
    c00100: float
        Adjusted Gross Income (AGI)
    pre_c04600: float
        Personal exemption before phase-out
    c04600: float
        Personal exemptions after phase-out
    """
    # calculate AGI assuming no foreign earned income exclusion
    c00100 = ymod1 + c02500 - c02900 + taxable_ubi
    # calculate UI exclusion (e.g., from 2020 AGI due to ARPA)
    if (c00100 - e02300) <= UI_thd[MARS - 1]:
        ui_excluded = min(e02300, UI_em)
    else:
        ui_excluded = 0.
    c00100 -= ui_excluded
    # calculate personal exemption amount
    if II_no_em_nu18:  # repeal of personal exemptions for deps. under 18
        pre_c04600 = max(0, XTOT - nu18) * II_em
    else:
        pre_c04600 = XTOT * II_em
    if DSI:
        pre_c04600 = 0.
    # phase-out personal exemption amount
    if exact == 1:  # exact calculation as on tax forms
        line5 = max(0., c00100 - II_em_ps[MARS - 1])
        line6 = math.ceil(line5 / (2500. / sep))
        line7 = II_em_prt * line6
        c04600 = max(0., pre_c04600 * (1. - line7))
    else:  # smoothed calculation needed for sensible mtr calculation
        dispc_numer = II_em_prt * (c00100 - II_em_ps[MARS - 1])
        dispc_denom = 2500. / sep
        dispc = min(1., max(0., dispc_numer / dispc_denom))
        c04600 = pre_c04600 * (1. - dispc)
    return (c00100, pre_c04600, c04600)


@iterate_jit(nopython=True)
def MiscDed(age_head, age_spouse, MARS, c00100, exact,
            SeniorDed_c, SeniorDed_ps, SeniorDed_prt,
            auto_loan_interest,
            AutoLoanInterestDed_c,
            AutoLoanInterestDed_ps,
            AutoLoanInterestDed_po_step_size,
            AutoLoanInterestDed_po_rate_per_step,
            senior_deduction, auto_loan_interest_deduction):
    """
    Calculates below-the-line deduction for elderly head/spouse and
    deduction on qualified auto loan interest paid.

    Parameters
    ----------
    age_head: int
        Age of tax unit head
    age_head: int
        Age of tax unit spouse
    MARS: int
        Filing marital status (1=single, 2=joint, 3=separate,
                               4=household-head, 5=widow(er))
    c00100: float
        Adjusted gross income
    exact: int
        Whether or not to smooth deduction phase out
    SeniorDed_c: float
        Maximum amount of senior deduction per head/spouse aged 65+
    SeniorDed_ps: list[float]
        Senior deduction AGI phase-out start level
    SeniorDed_prt: float
        Senior deduction phase-out rate
    auto_loan_interest: float
        Qualified auto loan interest paid
    AutoLoanInterestDed_c: float
        Deduction cap
    AutoLoanInterestDed_ps: float
        Deduction phase-out starts above this AGI
    AutoLoanInterestDed_po_step_size: float
        Deduction phase-out AGI step size
    AutoLoanInterestDed_po_rate_per_step: float
        Deduction phase-out rate per AGI step
    auto_loan_interest_deduction: float
        Deduction available to both itemizers and nonitemizers

    Returns
    -------
    senior_deduction: float
        Deduction available to both itemizers and nonitemizers
    auto_loan_interest_deduction: float
        Deduction available to both itemizers and nonitemizers
    """
    # calculate senior deduction
    senior_deduction = 0.
    if SeniorDed_c > 0.:
        seniors = 0
        if age_head >= 65:
            seniors += 1
        if MARS == 2 and age_spouse >= 65:
            seniors += 1
        if seniors > 0:
            ded = seniors * SeniorDed_c
            po_start = SeniorDed_ps[MARS - 1]
            if c00100 > po_start:
                excess_agi = c00100 - po_start
                po_amount = excess_agi * SeniorDed_prt
                ded = max(0., ded - po_amount)
            senior_deduction = ded
    # calculate auto loan interest deduction
    auto_loan_interest_deduction = 0.
    if AutoLoanInterestDed_c > 0. and auto_loan_interest > 0.:
        # cap deduction
        ded = min(auto_loan_interest, AutoLoanInterestDed_c)
        po_start = AutoLoanInterestDed_ps[MARS - 1]
        if c00100 > po_start:
            # phase out deduction
            excess_agi = c00100 - po_start
            po_rate = AutoLoanInterestDed_po_rate_per_step
            if exact == 1:  # exact calculation as on tax forms
                step_size = AutoLoanInterestDed_po_step_size
                steps = math.ceil(excess_agi / step_size)
                po_amount = steps * step_size * po_rate
            else:  # smoothed calculation needed for sensible mtr calculation
                po_amount = excess_agi * po_rate
            ded = max(0., ded - po_amount)
        auto_loan_interest_deduction = ded
    return (senior_deduction, auto_loan_interest_deduction)


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
            ID_StateLocalTax_crt, ID_RealEstate_crt, ID_Charity_f,
            ID_reduction_salt_rate, ID_reduction_other_rate):
    """
    Calculates itemized deductions, Form 1040, Schedule A.

    Parameters
    ----------
    e17500: float
        Schedule A: medical expenses
    e18400: float
        Schedule A: state and local income taxes deductlbe
    e18500: float
        Schedule A: state and local real estate taxes deductible
    e19200: float
        Schedule A: interest deduction deductible
    e19800: float
        Schedule A: charity cash contributions deductible
    e20100: float
        Schedule A: charity noncash contributions deductible
    e20400: float
        Schedule A: gross miscellaneous deductions deductible
    g20500: float
        Schedule A: gross casualty or theft loss deductible
    MARS: int
        Filing marital status (1=single, 2=joint, 3=separate,
                               4=household-head, 5=widow(er))
    age_head: int
        Age in years of taxpayer
    age_spouse: int
        Age in years of spouse
    c00100: float
        Adjusted gross income (AGI)
    c04600: float
        Personal exemptions after phase out
    c04470: float
        Itemized deductions after all limitations (0 for non-itemizers)
    c21040: float
        Itemized deductions that are limited under the Pease limitations
    c21060: float
        Itemized deductions before limitation (0 for non-itemizers)
    c17000: float
        Schedule A: medical expenses deducted
    c18300: float
        Schedule A: state and local taxes plus real estate taxes deducted
    c19200: float
        Schedule A: interest deducted
    c19700: float
        Schedule A: charity contributions deducted
    c20500: float
        Schedule A: net casualty or theft loss deducted
    c20800: float
        Schedule A: net limited miscellaneous deductions deducted
    II_brk6: list
        Bottom of top income tax rate bracket
    ID_ps: list
        Itemized deduction phaseout AGI start (Pease)
    ID_Medical_frt: float
        Floor (as decimal fraction of AGI) for deductible medical expenses
    ID_Medical_frt_add4aged: float
        Add on floor (as decimal fraction of AGI) for deductible
        medical expenses for elderly filing units
    ID_Medical_hc: float
        Medical expense deduction haircut
    ID_Casualty_frt: float
        Floor (as decimal fraction of AGI) for deductible casualty loss
    ID_Casualty_hc: float
        Casualty expense deduction haircut
    ID_Miscellaneous_frt: float
        Floor (as decimal fraction of AGI) for deductible
        miscellaneous expenses
    ID_Miscellaneous_hc: float
        Miscellaneous expense deduction haircut
    ID_Charity_crt_all: float
        Ceiling (as decimal fraction of AGI) for all charitable
        contribution deductions
    ID_Charity_crt_noncash: float
        Ceiling (as decimal fraction of AGI) for noncash charitable
        contribution deductions
    ID_prt: float
        Itemized deduction phaseout rate (Pease)
    ID_crt: float
        Itemized deduction maximum phaseout as a decimal fraction of total
        itemized deductions (Pease)
    ID_c: list
        Ceiling on the amount of itemized deductions allowed (dollars)
    ID_StateLocalTax_hc: float
        State and local income and sales taxes deduction haircut
    ID_Charity_frt: float
        Floor (as decimal fraction of AGI) for deductible charitable
        contributions
    ID_Charity_hc: float
        Charity expense deduction haircut
    ID_InterestPaid_hc: float
        Interest paid deduction haircut
    ID_RealEstate_hc: float
        State, local, and foreign real estate taxes deductions haircut
    ID_Medical_c: list
        Ceiling on the amount of medical expense deduction allowed (dollars)
    ID_StateLocalTax_c: list
        Ceiling on the amount of state and local income and sales taxes
        deduction allowed (dollars)
    ID_RealEstate_c: list
        Ceiling on the amount of state, local, and foreign real estate taxes
        deduction allowed (dollars)
    ID_InterestPaid_c: list
        Ceiling on the amount of interest paid deduction allowed (dollars)
    ID_Charity_c: list
        Ceiling on the amount of charity expense deduction allowed (dollars)
    ID_Casualty_c: list
        Ceiling on the amount of casualty expense deduction allowed (dollars)
    ID_Miscellaneous_c: list
        Ceiling on the amount of miscellaneous expense deduction
        allowed (dollars)
    ID_AllTaxes_c: list
        Ceiling on the amount of state and local income, stales, and
        real estate deductions allowed (dollars)
    ID_AllTaxes_hc: float
        State and local income, sales, and real estate tax deduciton haircut
    ID_StateLocalTax_crt: float
        Ceiling (as decimal fraction of AGI) for the combination of all
        state and local income and sales tax deductions
    ID_RealEstate_crt: float
        Ceiling (as decimal fraction of AGI) for the combination of all
        state, local, and foreign real estate tax deductions
    ID_Charity_f: list
        Floor on the amount of charity expense deduction allowed (dollars)
    ID_reduction_salt_rate: float
        OBBBA reduction rate for SALT deductions
    ID_reduction_other_rate: float
        OBBBA reduction rate for other deductions

    Returns
    -------
    c17000: float
        Schedule A: medical expenses deducted
    c18300: float
        Schedule A: state and local taxes plus real estate taxes deducted
    c19200: float
        Schedule A: interest deducted
    c19700: float
        Schedule A: charity contributions deducted
    c20500: float
        Schedule A: net casualty or theft loss deducted
    c20800: float
        Schedule A: net limited miscellaneous deductions deducted
    c21040: float
        Itemized deductions that are phased out under Pease limitation
    c21060: float
        Itemized deductions before any limitation (0 for non-itemizers)
    c04470: float
        Itemized deductions after all limitations (0 for non-itemizers)
    """
    # pylint: disable=too-many-statements
    posagi = max(c00100, 0.)
    # Medical
    medical_frt = ID_Medical_frt
    if age_head >= 65 or (MARS == 2 and age_spouse >= 65):
        medical_frt += ID_Medical_frt_add4aged
    c17750 = medical_frt * posagi
    c17000 = max(0., e17500 - c17750) * (1. - ID_Medical_hc)
    c17000 = min(c17000, ID_Medical_c[MARS - 1])
    # State and local taxes
    c18400 = min((1. - ID_StateLocalTax_hc) * max(e18400, 0.),
                 ID_StateLocalTax_c[MARS - 1])
    c18500 = min((1. - ID_RealEstate_hc) * e18500,
                 ID_RealEstate_c[MARS - 1])
    # following two statements implement a cap on c18400 and c18500 in a way
    # that those with negative AGI, c00100, are not capped under current law,
    # hence the 0.0001 rather than zero
    c18400 = min(c18400, ID_StateLocalTax_crt * max(c00100, 0.0001))
    c18500 = min(c18500, ID_RealEstate_crt * max(c00100, 0.0001))
    c18300 = (c18400 + c18500) * (1. - ID_AllTaxes_hc)
    c18300 = min(c18300, ID_AllTaxes_c[MARS - 1])
    # Interest paid
    c19200 = e19200 * (1. - ID_InterestPaid_hc)
    c19200 = min(c19200, ID_InterestPaid_c[MARS - 1])
    # Charity
    floor = max(ID_Charity_frt * posagi, ID_Charity_f[MARS - 1])
    noncash_ded = max(0., e20100 - floor)
    charity_ded_noncash = min(ID_Charity_crt_noncash * posagi, noncash_ded)
    remaining_floor = max(0., floor - e20100)
    charity_ded_cash = max(0., e19800 - remaining_floor)
    c19700 = charity_ded_noncash + charity_ded_cash
    c19700 = min(c19700, ID_Charity_crt_all * posagi) * (1. - ID_Charity_hc)
    c19700 = min(c19700, ID_Charity_c[MARS - 1])
    # Casualty
    c20500 = (max(0., g20500 - ID_Casualty_frt * posagi) *
              (1. - ID_Casualty_hc))
    c20500 = min(c20500, ID_Casualty_c[MARS - 1])
    # Miscellaneous
    c20400 = e20400
    c20750 = ID_Miscellaneous_frt * posagi
    c20800 = max(0., c20400 - c20750) * (1. - ID_Miscellaneous_hc)
    c20800 = min(c20800, ID_Miscellaneous_c[MARS - 1])
    # Gross total itemized deductions
    c21060 = c17000 + c18300 + c19200 + c19700 + c20500 + c20800
    # Pease limitation on total itemized deductions
    # (no attempt to adjust c04470 components for limitation)
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
    # OBBBA limitation on total itemized deductions
    # (no attempt to adjust c04470 components for limitation)
    reduction = 0.
    if ID_reduction_salt_rate > 0. or ID_reduction_other_rate > 0.:
        assert c21040 <= 0.0, "Pease and OBBBA cannot both be in effect"
        tincome = max(0., c00100 - c04600)
        texcess = max(0., tincome - II_brk6[MARS - 1])
        smaller_salt = min(c18300, texcess)
        salt_reduction = ID_reduction_salt_rate * smaller_salt
        other_deds = max(0, c04470 - c18300)
        smaller_other = min(other_deds, texcess)
        other_reduction = ID_reduction_other_rate * smaller_other
        reduction = salt_reduction + other_reduction
    c04470 = max(0., c04470 - reduction)
    # Cap total itemized deductions
    # (no attempt to adjust c04470 components for limitation)
    c04470 = min(c04470, ID_c[MARS - 1])
    # Return total itemized deduction amounts and pre-limitation components
    return (c17000, c18300, c19200, c19700, c20500, c20800,
            c21040, c21060, c04470)


@iterate_jit(nopython=True)
def AdditionalMedicareTax(e00200, MARS,
                          AMEDT_ec, sey, AMEDT_rt,
                          FICA_mc_trt_employer, FICA_mc_trt_employee,
                          FICA_ss_trt_employer, FICA_ss_trt_employee,
                          ptax_amc):
    """
    Computes Additional Medicare Tax (Form 8959) included in othertaxes.

    Parameters
    -----
    MARS: int
        Filing marital status (1=single, 2=joint, 3=separate,
                               4=household-head, 5=widow(er))
    AMEDT_ec: list
        Additional Medicare Tax earnings exclusion
    AMEDT_rt: float
        Additional Medicare Tax rate
    FICA_ss_trt_employer: float
        Employer side FICA Social Security tax rate
    FICA_ss_trt_employee: float
        Employee side FICA Social Security tax rate
    FICA_mc_trt_employer: float
        Employer side FICA Medicare tax rate
    FICA_mc_trt_employee: float
        Employee side FICA Medicare tax rate
    e00200: float
        Wages and salaries
    sey: float
        Self-employment income
    ptax_amc: float
        Additional Medicare Tax (included in othertaxes and iitax)

    Returns
    -------
    ptax_amc: float
        Additional Medicare Tax (included in othertaxes and iitax)
    """
    line8 = max(0., sey) * (
        1. - 0.5 * (FICA_mc_trt_employer + FICA_mc_trt_employee +
                    FICA_ss_trt_employer + FICA_ss_trt_employee)
    )
    line11 = max(0., AMEDT_ec[MARS - 1] - e00200)
    ptax_amc = AMEDT_rt * (max(0., e00200 - AMEDT_ec[MARS - 1]) +
                           max(0., line8 - line11))
    return ptax_amc


@iterate_jit(nopython=True)
def StdDed(DSI, earned, STD, age_head, age_spouse, STD_Aged, STD_Dep,
           MARS, MIDR, blind_head, blind_spouse, standard,
           STD_allow_charity_ded_nonitemizers, e19800, ID_Charity_crt_all,
           c00100, STD_charity_ded_nonitemizers_max):
    """
    Calculates standard deduction, including standard deduction for
    dependents, aged and bind.

    Parameters
    -----
    DSI: int
        1 if claimed as dependent on another return; otherwise 0
    earned: float
        Earned income for filing unit
    STD: list
        Standard deduction amount
    age_head: int
        Age in years of taxpayer
    age_spouse: int
        Age in years of spouse
    STD_Aged: list
        Additional standard deduction for blind and aged
    STD_Dep: float
        Standard deduction for dependents
    MARS: int
        Filing (marital) status. (1=single, 2=joint, 3=separate,
                                  4=household-head, 5=widow(er))
    MIDR: int
        1 if separately filing spouse itemizes, 0 otherwise
    blind_head: int
        1 if taxpayer is blind, 0 otherwise
    blind_spouse: int
        1 if spouse is blind, 0 otherwise
    standard: float
        Standard deduction (zero for itemizers)
    STD_allow_charity_ded_nonitemizers: bool
        Allow standard deduction filers to take the charitable contributions
        deduction
    e19800: float
        Schedule A: cash charitable contributions
    ID_Charity_crt_all: float
        Fraction of AGI cap on all charitable deductions
    c00100: float
        Federal AGI
    STD_charity_ded_nonitemizers_max: float
        Ceiling amount (in dollars) for charitable deductions for nonitemizers

    Returns
    -------
    standard: float
        Standard deduction (zero for itemizers)
    """
    # calculate deduction for dependents
    if DSI == 1:
        c15100 = max(350. + earned, STD_Dep)
        basic_stded = min(STD[MARS - 1], c15100)
    else:
        c15100 = 0.
        if MIDR == 1:
            basic_stded = 0.
        else:
            basic_stded = STD[MARS - 1]
    # calculate extra standard deduction for aged and blind
    num_extra_stded = blind_head + blind_spouse
    if age_head >= 65:
        num_extra_stded += 1
    if MARS == 2 and age_spouse >= 65:
        num_extra_stded += 1
    extra_stded = num_extra_stded * STD_Aged[MARS - 1]
    # calculate the total standard deduction
    standard = basic_stded + extra_stded
    if MARS == 3 and MIDR == 1:
        standard = 0.
    # calculate CARES cash charity deduction for nonitemizers
    if STD_allow_charity_ded_nonitemizers:
        capped_ded = min(e19800, ID_Charity_crt_all * c00100)
        standard += min(capped_ded, STD_charity_ded_nonitemizers_max[MARS - 1])
    return standard


@iterate_jit(nopython=True)
def TaxInc(c00100, standard, c04470, c04600, MARS, e00900, c03260, e26270,
           e02100, e27200, e00650, c01000,
           senior_deduction, auto_loan_interest_deduction,
           PT_SSTB_income, PT_binc_w2_wages, PT_ubia_property,
           PT_qbid_rt, PT_qbid_limited,
           PT_qbid_taxinc_thd, PT_qbid_taxinc_gap, PT_qbid_w2_wages_rt,
           PT_qbid_alt_w2_wages_rt, PT_qbid_alt_property_rt,
           PT_qbid_ps, PT_qbid_prt, PT_qbid_min_ded, PT_qbid_min_qbi,
           c04800, qbided):
    """
    Calculates taxable income, c04800, and
    qualified business income deduction, qbided.

    Parameters
    ----------
    c00100: float
        Adjusted Gross Income (AGI)
    standard: float
        Standard deduction (zero for itemizers)
    c04470: float
        Itemized deductions after phase-out (zero for non-itemizers)
    c04600: float
        Personal exemptions after phase-out
    MARS: int
        Filing (marital) status. (1=single, 2=joint, 3=separate,
                                  4=household-head, 5=widow(er))
    e00900: float
        Schedule C business net profit/loss for filing unit
    c03260: float
        Self-employment (SECA) tax above-the-line deduction
    e26270: float
        Schedule E: combined partnership and S-corporation net income/loss
    e02100: float
        Farm net income/loss for filing unit from Schedule F
    e27200: float
        Schedule E: farm rent net income or loss
    e00650: float
        Qualified dividends included in ordinary dividends
    c01000: float
        Limitation on capital losses
    senior_deduction: float
        Deduction for elderly head/spouse
    auto_loan_interest_deduction: float
        Deduction for qualified auto loan interest paid
    PT_SSTB_income: int
        Value of one implies business income is from a specified service
          trade or business (SSTB)
        Value of zero implies business income is from a qualified trade or
          business
    PT_binc_w2_wages: float
        Filing unit's share of total W-2 wages paid by the
        pass-through business
    PT_ubia_property: float
        Filing unit's share of total business property owned by the
        pass-through business
    PT_qbid_rt: float
        Pass-through qualified business income deduction rate
    PT_qbid_limited: bool
        Whether or not TCJA QBID limits are active
    PT_qbid_taxinc_thd: list
        Lower threshold of pre-QBID taxable income
    PT_qbid_taxinc_gap: list
        Dollar gap between upper and lower threshold of pre-QBID taxable income
    PT_qbid_w2_wages_rt: float
        QBID cap rate on pass-through business W-2 wages paid
    PT_qbid_alt_w2_wages_rt: float
        Alternative QBID cap rate on pass-through business W-2 wages paid
    PT_qbid_alt_property_rt: float
        Alternative QBID cap rate on pass-through business property owned
    PT_qbid_ps: list
        QBID phaseout taxable income start
    PT_qbid_prt: float
        QBID phaseout rate
    PT_qbid_min_ded: float
        Minimum QBID amount
    PT_qbid_min_qbi: float
        Minimum QBI necessary to get QBID no less than PT_qbid_min_ded
    c04800: float
        Regular taxable income
    qbided: float
        Qualified Business Income (QBI) deduction

    Returns
    -------
    c04800: float
        Regular taxable income
    qbided: float
        Qualified Business Income (QBI) deduction
    """
    # calculate taxable income before qualified business income deduction,
    # which is assumed to be stacked last in the list of deductions
    odeds = senior_deduction + auto_loan_interest_deduction
    pre_qbid_taxinc = max(0., c00100 - max(c04470, standard) - c04600 - odeds)
    # calculate qualified business income deduction
    qbinc = max(0., e00900 - c03260 + e26270 + e02100 + e27200)
    qbid_before_limits = qbinc * PT_qbid_rt
    if PT_qbid_limited:
        lower_thd = PT_qbid_taxinc_thd[MARS - 1]
        if pre_qbid_taxinc <= lower_thd:
            qbided = qbid_before_limits
        else:
            pre_qbid_taxinc_gap = PT_qbid_taxinc_gap[MARS - 1]
            upper_thd = lower_thd + pre_qbid_taxinc_gap
            if PT_SSTB_income == 1 and pre_qbid_taxinc >= upper_thd:
                qbided = 0.
            else:
                wage_cap = PT_binc_w2_wages * PT_qbid_w2_wages_rt
                alt_cap = (PT_binc_w2_wages * PT_qbid_alt_w2_wages_rt +
                           PT_ubia_property * PT_qbid_alt_property_rt)
                full_cap = max(wage_cap, alt_cap)
                if PT_SSTB_income == 0 and pre_qbid_taxinc >= upper_thd:
                    # apply full cap
                    qbided = min(full_cap, qbid_before_limits)
                elif PT_SSTB_income == 0 and pre_qbid_taxinc < upper_thd:
                    # apply adjusted cap as in Part III of Worksheet 12-A
                    # in 2018 IRS Publication 535 (Chapter 12)
                    prt = (pre_qbid_taxinc - lower_thd) / pre_qbid_taxinc_gap
                    adj = prt * (qbid_before_limits - full_cap)
                    qbided = qbid_before_limits - adj
                else:  # PT_SSTB_income == 1 and pre_qbid_taxinc < upper_thd
                    prti = (upper_thd - pre_qbid_taxinc) / pre_qbid_taxinc_gap
                    qbid_adjusted = prti * qbid_before_limits
                    cap_adjusted = prti * full_cap
                    prt = (pre_qbid_taxinc - lower_thd) / pre_qbid_taxinc_gap
                    adj = prt * (qbid_adjusted - cap_adjusted)
                    qbided = qbid_adjusted - adj
        # apply taxinc cap (assuming cap rate is equal to PT_qbid_rt)
        #   net_cg is defined on line 34 of 2018 Pub 535 Worksheet 12-A
        net_cg = e00650 + c01000
        taxinc_cap = PT_qbid_rt * max(0., pre_qbid_taxinc - net_cg)
        qbided = min(qbided, taxinc_cap)
        # apply qbid phaseout
        if qbided > 0. and pre_qbid_taxinc > PT_qbid_ps[MARS - 1]:
            excess = pre_qbid_taxinc - PT_qbid_ps[MARS - 1]
            qbided = max(0., qbided - PT_qbid_prt * excess)
    else:  # if PT_qbid_limited is false
        qbided = qbid_before_limits
    # apply minimum QBID logic
    if qbinc >= PT_qbid_min_qbi and qbided < PT_qbid_min_ded:
        qbided = PT_qbid_min_ded

    # calculate taxable income after qbided
    c04800 = max(0., pre_qbid_taxinc - qbided)
    return (c04800, qbided)


@JIT(nopython=True)
def SchXYZ(taxable_income, MARS,
           II_rt1, II_rt2, II_rt3, II_rt4, II_rt5,
           II_rt6, II_rt7, II_rt8,
           II_brk1, II_brk2, II_brk3, II_brk4, II_brk5,
           II_brk6, II_brk7):
    """
    Taxes function returns tax amount given the progressive tax rate
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
    if taxable_income <= 0.:
        return 0.
    tax = 0.
    brk0 = 0.
    brk1 = II_brk1[MARS - 1]
    if taxable_income <= brk1:
        return tax + II_rt1 * (taxable_income - brk0)
    tax = tax + II_rt1 * (brk1 - brk0)
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
    SchXYZTax calls SchXYZ function and sets c05200 to returned amount.

    Parameters
    ----------
    c04800: float
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
    c05200: float
        Tax amount from Schedule X,Y,Z tables

    Returns
    -------
    c05200: float
        Tax amount from Schedule X, Y, Z tables
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
             dwks10, dwks13, dwks14, dwks19, dwks43, c05700, taxbc):
    """
    GainsTax function implements (2015) Schedule D Tax Worksheet logic for
    the special taxation of long-term capital gains and qualified dividends
    if CG_nodiff is false.

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
    dwks19: float
        Maximum of dwks17 and dwks16
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
    dwks19: float
        Maximum of dwks17 and dwks16
    dwks43: float
        separate tax on long-term capital gains and qualified dividends
    c05700: float
        Lump sum distributions
    taxbc: float
        Regular tax on regular taxable income before credits
    """
    # pylint: disable=too-many-statements
    if c01000 > 0. or c23650 > 0. or p23250 > 0. or e01100 > 0. or e00650 > 0.:
        hasqdivltcg = 1  # has qualified dividends or long-term capital gains
    else:
        hasqdivltcg = 0  # no qualified dividends or long-term capital gains

    if CG_nodiff:
        hasqdivltcg = 0  # no special taxation of qual divids and l-t cap gains

    if hasqdivltcg == 1:

        dwks1 = c04800
        dwks2 = e00650
        dwks3 = e58990
        dwks4 = 0.  # always assumed to be zero
        dwks5 = max(0., dwks3 - dwks4)
        dwks6 = max(0., dwks2 - dwks5)
        dwks7 = min(p23250, c23650)  # SchD lines 15 and 16, respectively
        # dwks8 = min(dwks3, dwks4)
        # dwks9 = max(0., dwks7 - dwks8)
        # BELOW TWO STATEMENTS ARE UNCLEAR IN LIGHT OF dwks9=... COMMENT
        if e01100 > 0.:
            c24510 = e01100
        else:
            c24510 = max(0., dwks7) + e01100
        dwks9 = max(0., c24510 - min(0., e58990))
        # ABOVE TWO STATEMENTS ARE UNCLEAR IN LIGHT OF dwks9=... COMMENT
        dwks10 = dwks6 + dwks9
        dwks11 = e24515 + e24518  # SchD lines 18 and 19, respectively
        dwks12 = min(dwks9, dwks11)
        dwks13 = dwks10 - dwks12
        dwks14 = max(0., dwks1 - dwks13)
        dwks16 = min(CG_brk1[MARS - 1], dwks1)
        dwks17 = min(dwks14, dwks16)
        dwks18 = max(0., dwks1 - dwks10)
        dwks19 = max(dwks17, dwks18)
        dwks20 = dwks16 - dwks17
        lowest_rate_tax = CG_rt1 * dwks20
        # break in worksheet lines
        dwks21 = min(dwks1, dwks13)
        dwks22 = dwks20
        dwks23 = max(0., dwks21 - dwks22)
        dwks25 = min(CG_brk2[MARS - 1], dwks1)
        dwks26 = dwks19 + dwks20
        dwks27 = max(0., dwks25 - dwks26)
        dwks28 = min(dwks23, dwks27)
        dwks29 = CG_rt2 * dwks28
        dwks30 = dwks22 + dwks28
        dwks31 = dwks21 - dwks30
        dwks32 = CG_rt3 * dwks31
        # compute total taxable CG for additional top bracket
        cg_all = dwks20 + dwks28 + dwks31
        hi_base = max(0., cg_all - CG_brk3[MARS - 1])
        hi_incremental_rate = CG_rt4 - CG_rt3
        highest_rate_incremental_tax = hi_incremental_rate * hi_base
        # break in worksheet lines
        dwks33 = min(dwks9, e24515)
        dwks34 = dwks10 + dwks19
        dwks36 = max(0., dwks34 - dwks1)
        dwks37 = max(0., dwks33 - dwks36)
        dwks38 = 0.25 * dwks37
        # break in worksheet lines
        dwks39 = dwks19 + dwks20 + dwks28 + dwks31 + dwks37
        dwks40 = dwks1 - dwks39
        dwks41 = 0.28 * dwks40
        dwks42 = SchXYZ(dwks19, MARS,
                        II_rt1, II_rt2, II_rt3, II_rt4, II_rt5,
                        II_rt6, II_rt7, II_rt8,
                        II_brk1, II_brk2, II_brk3, II_brk4, II_brk5,
                        II_brk6, II_brk7)
        dwks43 = (dwks29 + dwks32 + dwks38 + dwks41 + dwks42 +
                  lowest_rate_tax + highest_rate_incremental_tax)
        dwks44 = c05200
        dwks45 = min(dwks43, dwks44)
        c24580 = dwks45

    else:  # if hasqdivltcg is zero

        c24580 = c05200
        dwks10 = max(0., min(p23250, c23650)) + e01100
        dwks13 = 0.
        dwks14 = 0.
        dwks19 = 0.
        dwks43 = 0.

    # final calculations done no matter what the value of hasqdivltcg
    c05100 = c24580  # because foreign earned income exclusion is assumed zero
    c05700 = 0.  # no Form 4972, Lump Sum Distributions
    taxbc = c05700 + c05100
    return (dwks10, dwks13, dwks14, dwks19, dwks43, c05700, taxbc)


@iterate_jit(nopython=True)
def AGIsurtax(c00100, MARS, AGI_surtax_trt, AGI_surtax_thd, taxbc, surtax):
    """
    Computes surtax on AGI above some threshold.

    Parameters
    ----------
    c00100: float
        Adjusted Gross Income (AGI)
    MARS: int
        Filing (marital) status. (1=single, 2=joint, 3=separate,
                                  4=household-head, 5=widow(er))
    AGI_surtax_trt: float
        New AGI surtax rate
    AGI_surtax_thd: list
        Threshold for the new AGI surtax
    taxbc: float
        Regular tax on regular taxable income before credits
    surtax: float
        Surtax on AGI above some threshold

    Returns
    -------
    taxbc: float
        Regular tax on regular taxable income before credits
    surtax: float
        Surtax on AGI above some threshold
    """
    if AGI_surtax_trt > 0.:
        hiAGItax = AGI_surtax_trt * max(c00100 - AGI_surtax_thd[MARS - 1], 0.)
        taxbc += hiAGItax
        surtax += hiAGItax
    return (taxbc, surtax)


@iterate_jit(nopython=True)
def AMT(e07300, dwks13, standard, f6251, c00100, c18300, taxbc,
        c04470, c17000, c20800, c21040, e24515, MARS, sep, dwks19,
        dwks14, c05700, e62900, e00700, dwks10, age_head, age_spouse,
        earned, cmbtp, qbided,
        AMT_child_em_c_age, AMT_brk1,
        AMT_em, AMT_prt, AMT_rt1, AMT_rt2,
        AMT_child_em, AMT_em_ps, AMT_em_pe,
        AMT_CG_brk1, AMT_CG_brk2, AMT_CG_brk3, AMT_CG_rt1, AMT_CG_rt2,
        AMT_CG_rt3, AMT_CG_rt4, c05800, c09600, c62100):
    """
    Computes Alternative Minimum Tax (AMT) taxable income and liability, where
    c62100 is AMT taxable income,
    c09600 is AMT tax liability, and
    c05800 is total (regular + AMT) income tax liability before credits.

    Note that line-number variable names refer to 2015 Form 6251.

    Parameters
    -----------
    e07300: float
        Foreign tax credit from Form 1116
    dwks13: float
        Difference of dwks10 - dwks12
    standard: float
        Standard deduction (zero for itemizers)
    f6251: int
        1 if Form 6251 (AMT) attached to return, otherwise 0
    c00100: float
        Adjusted Gross Income (AGI)
    c18300: float
        Schedule A: state and local taxes plus real estate taxes deducted
    taxbc: float
        Regular tax on regular taxable income before credits
    c04470: float
        Itemized deductions after phase-out (zero for non-itemizers)
    c17000: float
        Schedule A: Medical expenses deducted
    c20800: float
        Schedule A: net limited miscellaneous deductions deducted
    c21040: float
        Itemized deductions that are phased out
    e24515: float
        Schedule D: Un-Recaptured Section 1250 Gain
    MARS: int
        Filing (marital) status. (1=single, 2=joint, 3=separate,
                                  4=household-head, 5=widow(er))
    sep: int
        2 when MARS is 3 (married filing separately), otherwise 1
    dwks19: float
        Maximum of 0 and dwks1 - dwks13
    dwks14: float
        Maximum of 0 and dwks1 - dwks13
    c05700: float
        Lump sum distributions
    e62900: float
        Alternative Minimum Tax foreign tax credit from Form 6251
    e00700: float
        Taxable refunds of state and local income taxes
    dwks10: float
        Sum of dwks6 + dwks9
    age_head: int
        Age in years of taxpayer (i.e. primary adult)
    age_spouse: int
        Age in years of spouse (i.e. secondary adult if present)
    earned: float
        Earned income for filing unit
    cmbtp: float
        Estimate of income on (AMT) Form 6251 but not in AGI
    qbided: float
        Qualified business income deduction
    AMT_child_em_c_age: float
        Age ceiling for special AMT exemption
    AMT_brk1: float
        AMT bracket 1 (upper threshold)
    AMT_em: list
        AMT exemption amount
    AMT_prt: float
        AMT exemption phaseout rate
    AMT_rt1: float
        AMT rate 1
    AMT_rt2: float
        Additional AMT rate for AMT taxable income about AMT bracket 1
    AMT_child_em: float
        Child AMT exemption additional income base
    AMT_em_ps: list
        AMT exemption phaseout start
    AMT_em_pe: float
        AMT exemption phaseout ending AMT taxable income for
        married filing separately
    AMT_CG_brk1: list
        Top of long-term capital gains and qualified dividends (AMT) tax
        bracket 1
    AMT_CG_brk2: list
        Top of long-term capital gains and qualified dividends (AMT) tax
        bracket 2
    AMT_CG_brk3: list
        Top of long-term capital gains and qualified dividends (AMT) tax
        bracket 3
    AMT_CG_rt1: float
        Long term capital gain and qualified dividends (AMT) rate 1
    AMT_CG_rt2: float
        Long term capital gain and qualified dividends (AMT) rate 2
    AMT_CG_rt3: float
        Long term capital gain and qualified dividends (AMT) rate 3
    AMT_CG_rt4: float
        Long term capital gain and qualified dividends (AMT) rate 4
    c05800: float
        Total (regular + AMT) income tax liability before credits
    c09600: float
        Alternative Minimum Tax (AMT) liability
    c62100: float
        Alternative Minimum Tax (AMT)

    Returns
    -------
    c62100: float
        Alternative Minimum Tax (AMT)
    c09600: float
        Alternative Minimum Tax (AMT) liability
    c05800: float
        Total (regular + AMT) income tax liability before credits
    """
    # pylint: disable=too-many-statements,too-many-branches
    # Form 6251, Part I
    if standard == 0.0:
        c62100 = (c00100 - e00700 - qbided - c04470 +
                  max(0., min(c17000, 0.025 * c00100)) +
                  c18300 + c20800 - c21040)
    if standard > 0.0:
        c62100 = c00100 - e00700 - qbided
    c62100 += cmbtp  # add income not in AGI but considered income for AMT
    if MARS == 3:
        amtsepadd = max(0.,
                        min(AMT_em[MARS - 1], AMT_prt * (c62100 - AMT_em_pe)))
    else:
        amtsepadd = 0.
    c62100 = c62100 + amtsepadd  # AMT taxable income, which is line28
    # Form 6251, Part II top
    line29 = max(0., AMT_em[MARS - 1] - AMT_prt *
                 max(0., c62100 - AMT_em_ps[MARS - 1]))
    young_head = age_head != 0 and age_head < AMT_child_em_c_age
    no_or_young_spouse = age_spouse < AMT_child_em_c_age
    if young_head and no_or_young_spouse:
        line29 = min(line29, earned + AMT_child_em)
    line30 = max(0., c62100 - line29)
    line3163 = (AMT_rt1 * line30 +
                AMT_rt2 * max(0., (line30 - (AMT_brk1 / sep))))
    if dwks10 > 0. or dwks13 > 0. or dwks14 > 0. or dwks19 > 0. or e24515 > 0.:
        # complete Form 6251, Part III (line36 is equal to line30)
        line37 = dwks13
        line38 = e24515
        line39 = min(line37 + line38, dwks10)
        line40 = min(line30, line39)
        line41 = max(0., line30 - line40)
        line42 = (AMT_rt1 * line41 +
                  AMT_rt2 * max(0., (line41 - (AMT_brk1 / sep))))
        line44 = dwks14
        line45 = max(0., AMT_CG_brk1[MARS - 1] - line44)
        line46 = min(line30, line37)
        line47 = min(line45, line46)  # line47 is amount taxed at AMT_CG_rt1
        cgtax1 = line47 * AMT_CG_rt1
        line48 = line46 - line47
        line51 = dwks19
        line52 = line45 + line51
        line53 = max(0., AMT_CG_brk2[MARS - 1] - line52)
        line54 = min(line48, line53)  # line54 is amount taxed at AMT_CG_rt2
        cgtax2 = line54 * AMT_CG_rt2
        line56 = line47 + line54  # total amount in lower two brackets
        if line41 == line56:
            line57 = 0.  # line57 is amount taxed at AMT_CG_rt3
            linex2 = 0.  # linex2 is amount taxed at AMT_CG_rt4
        else:
            line57 = line46 - line56
            linex1 = min(line48,
                         max(0., AMT_CG_brk3[MARS - 1] - line44 - line45))
            linex2 = max(0., line54 - linex1)
        cgtax3 = line57 * AMT_CG_rt3
        cgtax4 = linex2 * AMT_CG_rt4
        if line38 == 0.:
            line61 = 0.
        else:
            line61 = 0.25 * max(0., line30 - line41 - line56 - line57 - linex2)
        line62 = line42 + cgtax1 + cgtax2 + cgtax3 + cgtax4 + line61
        line64 = min(line3163, line62)
        line31 = line64
    else:  # if not completing Form 6251, Part III
        line31 = line3163
    # Form 6251, Part II bottom
    if f6251 == 1:
        line32 = e62900
    else:
        line32 = e07300
    line33 = line31 - line32
    c09600 = max(0., line33 - max(0., taxbc - e07300 - c05700))
    c05800 = taxbc + c09600
    return (c62100, c09600, c05800)


@iterate_jit(nopython=True)
def NetInvIncTax(e00300, e00600, e02000, e26270, c01000,
                 c00100, NIIT_thd, MARS, NIIT_PT_taxed, NIIT_rt, niit):
    """
    Computes Net Investment Income Tax (NIIT) amount assuming that
    all annuity income is excluded from net investment income.

    Parameters
    ----------
    e00300: float
        Tax-exempt interest income
    e00600: float
        Ordinary dividends included in AGI
    e02000: float
        Schedule E total rental, royalty, parternship, S-corporation,
        etc, income/loss
    e26270: float
        Schedule E: combined partnership and S-corporation net income/loss
    c01000: float
        Limitation on capital losses
    c00100: float
        Adjusted Gross Income (AGI)
    NIIT_thd: list
        Net Investment Income Tax modified AGI threshold
    MARS: int
        Filing (marital) status. (1=single, 2=joint, 3=separate,
                                  4=household-head, 5=widow(er))
    NIIT_PT_taxed: bool
        Whether or not partnership and S-corp income is NIIT based
    NIIT_rt: float
        Net Investment Income Tax rate
    niit: float
        Net investment income tax from Form 8960

    Returns
    -------
    niit: float
        Net investment income tax from Form 8960
    """
    modAGI = c00100  # no foreign earned income exclusion to add
    if not NIIT_PT_taxed:
        NII = max(0., e00300 + e00600 + c01000 + e02000 - e26270)
    else:  # do not subtract e26270 from e02000
        NII = max(0., e00300 + e00600 + c01000 + e02000)
    niit = NIIT_rt * min(NII, max(0., modAGI - NIIT_thd[MARS - 1]))
    return niit


@iterate_jit(nopython=True)
def F2441(MARS, earned_p, earned_s, f2441, CDCC_c, e32800, exact, c00100,
          CDCC_ps1, CDCC_ps2, CDCC_po1_rate_max, CDCC_po1_rate_min,
          CDCC_po2_rate_min, CDCC_po1_step_size, CDCC_po2_step_size,
          CDCC_po_rate_per_step, CDCC_refundable,
          c05800, e07300, c32800, c07180, CDCC_refund):
    """
    Calculates Form 2441 child and dependent care expense credit, c07180.

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
    # credit for at most two cared-for individuals and for actual expenses
    max_credit = min(f2441, 2) * CDCC_c
    c32800 = max(0., min(e32800, max_credit))
    # credit is limited to minimum of individuals' earned income
    c32880 = earned_p  # earned income of taxpayer
    if MARS == 2:
        c32890 = earned_s  # earned income of spouse when present
    else:
        c32890 = earned_p
    c33000 = max(0., min(c32800, c32880, c32890))
    # credit rate is limited at high AGI
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
        assert ps2 >= ps1, "CDCC_ps2 must be no less than CDCC_ps1"
        if c00100 > ps2:
            steps_fractional = (c00100 - ps2) / CDCC_po2_step_size[MARS - 1]
            if exact == 1:  # exact calculation as on tax forms
                steps = math.ceil(steps_fractional)
            else:
                steps = steps_fractional
            crate = max(
                CDCC_po2_rate_min,
                CDCC_po1_rate_min - steps * CDCC_po_rate_per_step
            )
    c33200 = c33000 * crate
    # credit is limited by tax liability if not refundable
    if CDCC_refundable:
        c07180 = 0.
        CDCC_refund = c33200
    else:
        c07180 = min(max(0., c05800 - e07300), c33200)
        CDCC_refund = 0.
    return (c32800, c07180, CDCC_refund)


@JIT(nopython=True)
def EITCamount(basic_frac, phasein_rate, earnings, max_amount,
               phaseout_start, agi, phaseout_rate):
    """
    Returns EITC amount given specified parameters.
    English parameter names are used in this function because the
    EITC formula is not available on IRS forms or in IRS instructions;
    the extensive IRS EITC look-up table does not reveal the formula.

    Parameters
    ----------
    basic_frac: float
        Fraction of maximum earned income credit paid at zero earnings
    phasein_rate: float
        Earned income credit phasein rate
    earnings: float
        Earned income for filing unit
    max_amount: float
        Maximum earned income credit
    phaseout_start: float
        Earned income credit phaseout start AGI
    agi: float
        Adjusted Gross Income (AGI)
    phaseout_rate: float
        Earned income credit phaseout rate

    Returns
    -------
    eitc: float
        Earned Income Credit
    """
    # calculate qualified business income de
    eitc = min((basic_frac * max_amount +
                (1.0 - basic_frac) * phasein_rate * earnings), max_amount)
    if earnings > phaseout_start or agi > phaseout_start:
        eitcx = max(0., (max_amount - phaseout_rate *
                         max(0., max(earnings, agi) - phaseout_start)))
        eitc = min(eitc, eitcx)
    return eitc


@iterate_jit(nopython=True)
def EITC(MARS, DSI, EIC, c00100, e00300, e00400, e00600, c01000,
         e02000, e26270, age_head, age_spouse, earned, earned_p, earned_s,
         EITC_ps, EITC_MinEligAge, EITC_MaxEligAge, EITC_ps_MarriedJ,
         EITC_rt, EITC_c, EITC_prt, EITC_basic_frac,
         EITC_InvestIncome_c, EITC_excess_InvestIncome_rt,
         EITC_indiv, EITC_sep_filers_elig, c59660):
    """
    Computes EITC amount, c59660.

    Parameters
    ----------
    MARS: int
        Filing (marital) status. (1=single, 2=joint, 3=separate,
                                  4=household-head, 5=widow(er))
    DSI: int
        1 if claimed as dependent on another return, otherwise 0
    EIC: int
        Number of EIC qualifying children
    c00100: float
        Adjusted Gross Income (AGI)
    e00300: float
        Taxable interest income
    e00400: float
        Tax exempt interest income
    e00600: float
        Ordinary dividends included in AGI
    c01000: float
        Limitation on capital losses
    e02000: float
        Schedule E total rental, royalty, partnership, S-corporation,
        etc, income/loss
    e26270: float
        Schedule E combined partnership and S-corporation net income/loss
    age_head: int
        Age in years of taxpayer (primary adult)
    age_spouse: int
        Age in years of spouse (secondary adult, if present)
    earned: float
        Earned income for filing unit
    earned_p: float
        Earned income for taxpayer
    earned_s: float
        Earned income for spouse
    EITC_ps: list
        Earned income credit phaseout start AGI
    EITC_MinEligAge: int
        Minimum age for childless EITC eligibility
    EITC_MaxEligAge: int
        Maximum age for childless EITC eligibility
    EITC_ps_MarriedJ: list
        Extra earned income credit phaseout start AGI for
        married filling jointly
    EITC_rt: list
        Earned income credit phasein rate
    EITC_c: list
        Maximum earned income credit
    EITC_prt: list
        Earned income credit phaseout rate
    EITC_basic_frac: float
        Fraction of maximum earned income credit paid at zero earnings
    EITC_InvestIncome_c: float
        Maximum investment income before EITC reduction
    EITC_excess_InvestIncome_rt: float
        Rate of EITC reduction when investemtn income exceeds ceiling
    EITC_indiv: bool
        EITC is computed for each spouse based in individual earnings
    EITC_sep_filers_elig: bool
        Separate filers are eligible for the EITC
    c59660: float
        EITC amount

    Returns
    -------
    c59660: float
        EITC amount
    """
    # pylint: disable=too-many-branches
    if MARS != 2:
        eitc = EITCamount(EITC_basic_frac,
                          EITC_rt[EIC], earned, EITC_c[EIC],
                          EITC_ps[EIC], c00100, EITC_prt[EIC])
        if EIC == 0:
            # enforce age eligibility rule for those with no EITC-eligible
            # kids assuming that an unknown age_* value implies EITC age
            # eligibility
            h_age_elig = EITC_MinEligAge <= age_head <= EITC_MaxEligAge
            if (age_head == 0 or h_age_elig):
                c59660 = eitc
            else:
                c59660 = 0.
        else:  # if EIC != 0
            c59660 = eitc

    if MARS == 2:
        po_start = EITC_ps[EIC] + EITC_ps_MarriedJ[EIC]
        if not EITC_indiv:
            # filing unit EITC rather than individual EITC
            eitc = EITCamount(EITC_basic_frac,
                              EITC_rt[EIC], earned, EITC_c[EIC],
                              po_start, c00100, EITC_prt[EIC])
        if EITC_indiv:
            # individual EITC rather than a filing-unit EITC
            eitc_p = EITCamount(EITC_basic_frac,
                                EITC_rt[EIC], earned_p, EITC_c[EIC],
                                po_start, earned_p, EITC_prt[EIC])
            eitc_s = EITCamount(EITC_basic_frac,
                                EITC_rt[EIC], earned_s, EITC_c[EIC],
                                po_start, earned_s, EITC_prt[EIC])
            eitc = eitc_p + eitc_s

        if EIC == 0:
            h_age_elig = EITC_MinEligAge <= age_head <= EITC_MaxEligAge
            s_age_elig = EITC_MinEligAge <= age_spouse <= EITC_MaxEligAge
            if (age_head == 0 or age_spouse == 0 or h_age_elig or s_age_elig):
                c59660 = eitc
            else:
                c59660 = 0.
        else:
            c59660 = eitc

    if (MARS == 3 and not EITC_sep_filers_elig) or DSI == 1:
        c59660 = 0.

    # reduce positive EITC if investment income exceeds ceiling
    if c59660 > 0.:
        invinc = (e00400 + e00300 + e00600 +
                  max(0., c01000) + max(0., (e02000 - e26270)))
        if invinc > EITC_InvestIncome_c:
            eitc = (c59660 - EITC_excess_InvestIncome_rt *
                    (invinc - EITC_InvestIncome_c))
            c59660 = max(0., eitc)
    return c59660


@iterate_jit(nopython=True)
def RefundablePayrollTaxCredit(was_plus_sey_p, was_plus_sey_s,
                               RPTC_c, RPTC_rt,
                               rptc_p, rptc_s, rptc):
    """
    Computes refundable payroll tax credit amounts.

    Parameters
    ----------
    was_plus_sey_p: float
        Wage and salary income plus taxable self employment income for taxpayer
    was_plus_sey_s: float
        Wage and salary income plus taxable self employment income for spouse
    RPTC_c: float
        Maximum refundable payroll tax credit
    RPTC_rt: float
        Refundable payroll tax credit phasein rate
    rptc_p: float
        Refundable Payroll Tax Credit for taxpayer
    rptc_s: float
        Refundable Payroll Tax Credit for spouse
    rptc: float
        Refundable Payroll Tax Credit for filing unit

    Returns
    -------
    rptc_p: float
        Refundable Payroll Tax Credit for taxpayer
    rptc_s: float
        Refundable Payroll Tax Credit for spouse
    rptc: float
        Refundable Payroll Tax Credit for filing unit
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
    Computes amounts on "Child Tax Credit and Credit for Other Dependents
    Worksheet" in 2018 Publication 972, which pertain to these two
    nonrefundable tax credits.

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
        Maximum of 0 and line 10 minus line 16

    Returns
    -------
    c07220: float
        Child tax credit (adjusted) from Form 8812
    odc: float
        Other Dependent Credit
    codtc_limited: float
        Maximum of 0 and line 10 minus line 16
    """
    # Worksheet Part 1
    if CTC_include17:
        tu18 = int(age_head < 18)   # taxpayer is under age 18
        su18 = int(MARS == 2 and age_spouse < 18)  # spouse is under age 18
        childnum = n24 + max(0, nu18 - tu18 - su18 - n24)
    else:
        childnum = n24
    line1 = CTC_c * childnum + CTC_c_under6_bonus * nu06
    line2 = ODC_c * max(0, XTOT - childnum - num)
    line3 = line1 + line2
    modAGI = c00100  # no foreign earned income exclusion to add to AGI (line6)
    if line3 > 0. and modAGI > CTC_ps[MARS - 1]:
        excess = modAGI - CTC_ps[MARS - 1]
        if exact == 1:  # exact calculation as on tax forms
            excess = 1000. * math.ceil(excess / 1000.)
        line10 = max(0., line3 - CTC_prt * excess)
    else:
        line10 = line3
    if line10 > 0.:
        # Worksheet Part 2
        line11 = c05800
        line12 = (e07260 * (1. - CR_ResidentialEnergy_hc) +
                  e07300 * (1. - CR_ForeignTax_hc) +
                  c07180 +  # child & dependent care expense credit
                  c07230 +  # education credit
                  e07240 * (1. - CR_RetirementSavings_hc) +
                  c07200)  # Schedule R credit
        line13 = line11 - line12
        line14 = 0.
        line15 = max(0., line13 - line14)
        if CTC_is_refundable:
            c07220 = line10 * line1 / line3
            odc = max(0., line10 - c07220)
            codtc_limited = max(0., line10 - c07220 - odc)
        else:
            line16 = min(line10, line15)  # credit is capped by tax liability
            # separate the CTC and ODTC amounts
            c07220 = line16 * line1 / line3
            odc = max(0., line16 - c07220)
            # compute codtc_limited for use in AdditionalCTC function
            codtc_limited = max(0., line10 - line16)
    else:
        line16 = 0.
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
    Computes personal_refundable_credit and personal_nonrefundable_credit,
    neither of which are part of current-law policy.

    Parameters
    ----------
    MARS: int
        Filing (marital) status. (1=single, 2=joint, 3=separate,
                                  4=household-head, 5=widow(er))
    c00100: float
        Adjusted Gross Income (AGI)
    XTOT: int
        Total number of exemptions for filing unit
    nu18: int
        Number of people under 18 years old in the filing unit
    II_credit: list
        Personal refundable credit maximum amount
    II_credit_ps: list
        Personal refundable credit phaseout start
    II_credit_prt: float
        Personal refundable credit phaseout rate
    II_credit_nr: list
        Personal nonrefundable credit maximum amount
    II_credit_nr_ps: list
        Personal nonrefundable credit phaseout start
    II_credit_nr_prt: float
        Personal nonrefundable credit phaseout rate
    RRC_c: float
        Maximum amount of Recovery Rebate Credit
    RRC_ps: list
        Recovery Rebate Credit phase out start
    RRC_pe: list
        Recovery Rebate Credit phase out end
    RRC_prt: float
        Recovery Rebate Credit phase out rate
    RRC_c_kids: float
        Credit amount per child as part of the Recovery Rebate Credit
    RRC_c_unit: list
        Maximum credit for filing unit as part of the Recovery Rebate Credit
    personal_refundable_credit: float
        Personal refundable credit
    personal_nonrefundable_credit: float
        Personal nonrefundable credit

    Returns
    -------
    personal_refundable_credit: float
        Personal refundable credit
    personal_nonrefundable_credit: float
        Personal nonrefundable credit
    personal_rebate_credit: float
        Personal rebate credit
    """
    # calculate personal refundable credit amount with phase-out
    personal_refundable_credit = II_credit[MARS - 1]
    if II_credit_prt > 0. and c00100 > II_credit_ps[MARS - 1]:
        pout = II_credit_prt * (c00100 - II_credit_ps[MARS - 1])
        fully_phasedout = personal_refundable_credit - pout
        personal_refundable_credit = max(0., fully_phasedout)
    # calculate personal nonrefundable credit amount with phase-out
    personal_nonrefundable_credit = II_credit_nr[MARS - 1]
    if II_credit_nr_prt > 0. and c00100 > II_credit_nr_ps[MARS - 1]:
        pout = II_credit_nr_prt * (c00100 - II_credit_nr_ps[MARS - 1])
        fully_phasedout = personal_nonrefundable_credit - pout
        personal_nonrefundable_credit = max(0., fully_phasedout)
    # calculate Recovery Rebate Credit from CARES Act 2020 and/or ARPA 2021
    if c00100 < RRC_ps[MARS - 1]:
        recovery_rebate_credit = RRC_c * XTOT
        recovery_rebate_credit += RRC_c_unit[MARS - 1] + RRC_c_kids * nu18
    elif 0 < c00100 < RRC_pe[MARS - 1]:
        prt = (
            (c00100 - RRC_ps[MARS - 1]) /
            (RRC_pe[MARS - 1] - RRC_ps[MARS - 1])
        )
        recovery_rebate_credit = RRC_c * XTOT * (1 - prt)
    else:
        recovery_rebate_credit = max(
            0, RRC_c_unit[MARS - 1] + RRC_c_kids * nu18 - RRC_prt *
            (c00100 - RRC_ps[MARS - 1])
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
    Computes nonrefundable charity credit, charity_credit.
    This credit is not part of current-law policy.

    Parameters
    ----------
    e19800: float
        Itemizable charitable giving for cash and check contributions
    e20100: float
        Itemizable charitable giving other than cash and check contributions
    c00100: float
        Adjusted Gross Income (AGI)
    CR_Charity_rt: float
        Charity credit rate
    CR_Charity_f: list
        Charity credit floor
    CR_Charity_frt: float
        Charity credit floor rate
    MARS: int
        Filing (marital) status. (1=single, 2=joint, 3=separate,
                                  4=household-head, 5=widow(er))
    charity_credit: float
        Credit for charitable giving

    Returns
    -------
    charity_credit: float
        Credit for charitable giving
    """
    total_charity = e19800 + e20100
    floor = max(CR_Charity_frt * c00100, CR_Charity_f[MARS - 1])
    charity_cr_floored = max(total_charity - floor, 0)
    charity_credit = CR_Charity_rt * (charity_cr_floored)
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
def AdditionalCTC(codtc_limited, ACTC_c, n24, earned, ACTC_Income_thd,
                  ACTC_rt, nu06, ACTC_rt_bonus_under6family, ACTC_ChildNum,
                  CTC_is_refundable, CTC_include17, CTC_c,
                  age_head, age_spouse, MARS, nu18,
                  ptax_was, c03260, e09800, c59660, e11200,
                  c11070):
    """
    Calculates refundable Additional Child Tax Credit (ACTC), c11070,
    following 2018 Form 8812 logic.

    Parameters
    ----------
    codtc_limited: float
        Maximum of 0 and line 10 minus line 16
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
        children under 6
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
    # Part I
    line3 = codtc_limited

    if CTC_is_refundable:
        line4 = 0.
    else:
        if CTC_include17:
            tu18 = int(age_head < 18)   # taxpayer is under age 18
            su18 = int(MARS == 2 and age_spouse < 18)  # spouse is under age 18
            childnum = n24 + max(0, nu18 - tu18 - su18 - n24)
        else:
            childnum = n24
        line4 = min(ACTC_c, CTC_c) * childnum
    c11070 = 0.  # line15
    if line3 > 0. and line4 > 0.:
        line5 = min(line3, line4)
        line7 = max(0., earned - ACTC_Income_thd)
        # accommodate ACTC rate bonus for families with children under 5
        if nu06 == 0:
            ACTC_rate = ACTC_rt
        else:
            ACTC_rate = ACTC_rt + ACTC_rt_bonus_under6family
        line8 = ACTC_rate * line7
        if childnum < ACTC_ChildNum:
            if line8 > 0.:
                c11070 = min(line5, line8)
        else:  # if childnum >= ACTC_ChildNum
            if line8 >= line5:
                c11070 = line5
            else:  # complete Part II
                line9 = 0.5 * ptax_was
                line10 = c03260 + e09800
                line11 = line9 + line10
                line12 = c59660 + e11200
                line13 = max(0., line11 - line12)
                line14 = max(line8, line13)
                c11070 = min(line5, line14)
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
        Wages, salaries, and tips for filing unit net of pension contributions
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
