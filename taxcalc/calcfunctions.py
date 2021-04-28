"""
Tax-Calculator functions that calculate payroll and individual income taxes.

These functions are imported into the Calculator class.

Note: the parameter_indexing_CPI_offset policy parameter is the only
policy parameter that does not appear here; it is used in the policy.py
file to possibly adjust the price inflation rate used to index policy
parameters (as would be done in a reform that introduces chained-CPI
indexing).
"""
# CODING-STYLE CHECKS:
# pycodestyle calcfunctions.py
# pylint --disable=locally-disabled calcfunctions.py
#
# pylint: disable=too-many-lines
# pylint: disable=invalid-name
# pylint: disable=too-many-arguments
# pylint: disable=too-many-locals

import math
import copy
import numpy as np


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


def EI_PayrollTax(e00200p, e00200s, e00900p, e00900s, e02100p, e02100s,
                  k1bx14p, k1bx14s, pencon_p, pencon_s, FICA_ss_trt,
                  FICA_mc_trt, ALD_SelfEmploymentTax_hc, SS_Earnings_c,
                  SS_Earnings_thd):
    """
    Compute part of total OASDI+HI payroll taxes and earned income variables.

    Parameters
    ----------
    SS_Earnings_c: float
        Maximum taxable earnings for Social Security.
        Individual earnings below this amount are subjected to OASDI payroll tax.
        This parameter is indexed by rate of growth in average wages not by the price inflation rate.
    e00200p: float
        Wages, salaries, and tips for taxpayer net of pension contributions
    e00200s: float
        Wages, salaries, and tips for spouse net of pension contributions
    pencon_p: float
        Contributions to defined-contribution pension plans for taxpayer
    pencon_s: float
        Contributions to defined-contribution pension plans for spouse
    FICA_ss_trt: float
        Social security payroll tax rate, including both employer and employee
    FICA_mc_trt: float
        Medicare payroll tax rate, including both employer and employee
    ALD_SelfEmploymentTax_hc: float
        Adjustment for self-employment tax haircut
        If greater than zero, reduces the employer equivalent portion of self-employment adjustment
        Final adjustment amount = (1-Haircut)*SelfEmploymentTaxAdjustment
    SS_Earnings_thd: float
        Additional taxable earnings threshold for Social Security
        Individual earnings above this threshold are subjected to OASDI payroll tax, in addtion to
        earnings below the maximum taxable earnings threshold.
    e00900p: float
        Schedule C business net profit/loss for taxpayer
    e00900s: float
        Schedule C business net profit/loss for spouse
    e02100p: float
        Farm net income/loss for taxpayer
    e02100s: float
        Farm net income/loss for spouse
    k1bx14p: float
        Partner self-employment earnings/loss for taxpayer (included in e26270 total)
    k1bx14s: float
        Partner self-employment earnings/loss for spouse (included in e26270 total)
    payrolltax: float
        Total (employee and employer) payroll tax liability
        payrolltax = ptax_was + setax + ptax_amc
    ptax_was: float
        Employee and employer OASDI plus HI FICA tax
    setax: float
        Self-employment tax
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
        payrolltax = ptax_was + setax + ptax_amc
    ptax_was: float
        Employee and employer OASDI plus HI FICA tax
    setax: float
        Self-employment tax
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
    gross_was_p = e00200p + pencon_p
    gross_was_s = e00200s + pencon_s

    # compute taxable gross earnings for OASDI FICA
    txearn_was_p = np.minimum(SS_Earnings_c, gross_was_p)
    txearn_was_s = np.minimum(SS_Earnings_c, gross_was_s)

    # compute OASDI and HI payroll taxes on wage-and-salary income, FICA
    ptax_ss_was_p = FICA_ss_trt * txearn_was_p
    ptax_ss_was_s = FICA_ss_trt * txearn_was_s
    ptax_mc_was_p = FICA_mc_trt * gross_was_p
    ptax_mc_was_s = FICA_mc_trt * gross_was_s
    ptax_was = ptax_ss_was_p + ptax_ss_was_s + ptax_mc_was_p + ptax_mc_was_s

    # compute taxable self-employment income for OASDI SECA
    sey_frac = 1.0 - 0.5 * (FICA_ss_trt + FICA_mc_trt)
    txearn_sey_p = np.minimum(np.maximum(0., sey_p * sey_frac), SS_Earnings_c - txearn_was_p)
    txearn_sey_s = np.minimum(np.maximum(0., sey_s * sey_frac), SS_Earnings_c - txearn_was_s)

    # compute self-employment tax on taxable self-employment income, SECA
    setax_ss_p = FICA_ss_trt * txearn_sey_p
    setax_ss_s = FICA_ss_trt * txearn_sey_s
    setax_mc_p = FICA_mc_trt * np.maximum(0., sey_p * sey_frac)
    setax_mc_s = FICA_mc_trt * np.maximum(0., sey_s * sey_frac)
    setax_p = setax_ss_p + setax_mc_p
    setax_s = setax_ss_s + setax_mc_s
    setax = setax_p + setax_s

    # compute extra OASDI payroll taxes on the portion of the sum
    # of wage-and-salary income and taxable self employment income
    # that exceeds SS_Earnings_thd
    sey_frac = 1.0 - 0.5 * FICA_ss_trt
    was_plus_sey_p = gross_was_p + np.maximum(0., sey_p * sey_frac)
    was_plus_sey_s = gross_was_s + np.maximum(0., sey_s * sey_frac)
    extra_ss_income_p = np.maximum(0., was_plus_sey_p - SS_Earnings_thd)
    extra_ss_income_s = np.maximum(0., was_plus_sey_s - SS_Earnings_thd)
    extra_payrolltax = (extra_ss_income_p * FICA_ss_trt +
                        extra_ss_income_s * FICA_ss_trt)

    # compute part of total payroll taxes for filing unit
    # (the ptax_amc part of total payroll taxes for the filing unit is
    # computed in the AdditionalMedicareTax function below)
    payrolltax = ptax_was + setax + extra_payrolltax

    # compute OASDI part of payroll taxes
    ptax_oasdi = (ptax_ss_was_p + ptax_ss_was_s +
                  setax_ss_p + setax_ss_s +
                  extra_payrolltax)

    # compute earned* variables and AGI deduction for
    # "employer share" of self-employment tax, c03260
    # Note: c03260 is the amount on 2015 Form 1040, line 27
    c03260 = (1. - ALD_SelfEmploymentTax_hc) * 0.5 * setax
    earned = np.maximum(0., e00200p + e00200s + sey - c03260)
    earned_p = np.maximum(0., (e00200p + sey_p -
                        (1. - ALD_SelfEmploymentTax_hc) * 0.5 * setax_p))
    earned_s = np.maximum(0., (e00200s + sey_s -
                        (1. - ALD_SelfEmploymentTax_hc) * 0.5 * setax_s))
    return (sey, payrolltax, ptax_was, setax, c03260, ptax_oasdi,
            earned, earned_p, earned_s, was_plus_sey_p, was_plus_sey_s)


def DependentCare(nu13, elderly_dependents, earned,
                  MARS, ALD_Dependents_thd, ALD_Dependents_hc,
                  ALD_Dependents_Child_c, ALD_Dependents_Elder_c):
    """
    Computes dependent-care above-the-line deduction.

    Parameters
    ----------
    nu13: int
        Number of dependents under 13 years old
    elderly_dependents: int
        Number of elderly dependents age 65+ in filing unit excluding taxpayer and spouse
    earned: float
        Earned income for filing unit
    MARS: int
        Filing marital status (1=single, 2=joint, 3=separate, 4=household-head, 5=widow(er))
    ALD_Dependents_thd: list
        Maximum income to qualify for dependent care deduction
    ALD_Dependents_hc: float
        Deduction for childcare costs haircut
    ALD_Dependents_Child_c: float
        National weighted average cost of childcare, ceiling for available childcare deduction
    ALD_Dependents_Elder_c: float
        Eldercare deduction ceiling

    Returns
    -------
    care_deduction: float
        Total above the line deductions for dependent care.
    """

    care_deduction = np.where(earned <= ALD_Dependents_thd[MARS - 1],
                               (((1. - ALD_Dependents_hc) * nu13 *
                                    ALD_Dependents_Child_c) +
                               ((1. - ALD_Dependents_hc) * elderly_dependents *
                                    ALD_Dependents_Elder_c)),
                                0.)
    
    return care_deduction



def Adj(e03150, e03210, c03260,
        e03270, e03300, e03400, e03500, e00800,
        e03220, e03230, e03240, e03290, care_deduction,
        ALD_StudentLoan_hc, ALD_SelfEmp_HealthIns_hc, ALD_KEOGH_SEP_hc,
        ALD_EarlyWithdraw_hc, ALD_AlimonyPaid_hc, ALD_AlimonyReceived_hc,
        ALD_EducatorExpenses_hc, ALD_HSADeduction_hc, ALD_IRAContributions_hc,
        ALD_DomesticProduction_hc, ALD_Tuition_hc):
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

    Returns
    -------
    c02900: float
        Total of all "above the line" income adjustments to get AGI
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
    return c02900


def ALD_InvInc_ec_base(p22250, p23250, sep,
                       e00300, e00600, e01100, e01200):
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
    invinc_ec_base: float
        Exclusion of investment income from AGI

    Returns
    -------
    invinc_ec_base: float
        Exclusion of investment income from AGI
    """
    # limitation on net short-term and long-term capital losses
    cgain = np.maximum((-3000. / sep), p22250 + p23250)
    # compute exclusion of investment income from AGI
    invinc_ec_base = e00300 + e00600 + cgain + e01100 + e01200
    return invinc_ec_base


def CapGains(p23250, p22250, sep, invinc_ec_base, MARS,
             e00200, e00300, e00600, e00650, e00700, e00800,
             e00900, e01100, e01200, e01400, e01700, e02000, e02100,
             e02300, e00400, e02400, c02900, e03210, e03230, e03240,
             ALD_InvInc_ec_rt, CG_nodiff, CG_ec,
             CG_reinvest_ec_rt, ALD_StudentLoan_hc, ALD_BusinessLosses_c):
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
        Long term capital gains and qualified dividends taxed no differently than regular taxable income
    CG_ec: float
        Dollar amount of all capital gains and qualified dividends that are excluded from AGI
    CG_reinvest_ec_rt: float
        Fraction of all capital gains and qualified dividends in excess of the dollar exclusion that are excluded from AGI
    ALD_BusinessLosses_c: list
        Maximm amount of business losses deductible
    MARS: int
        Filing marital status (1=single, 2=joint, 3=separate, 4=household-head, 5=widow(er))
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
        Schedule E total rental, royalty, partnership, S-corporation, etc, income/loss (includes e26270 and e27200)
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
    c01000 = np.maximum((-3000. / sep), c23650)
    # compute total investment income
    invinc = e00300 + e00600 + c01000 + e01100 + e01200
    # compute exclusion of investment income from AGI
    invinc_agi_ec = ALD_InvInc_ec_rt * np.maximum(0., invinc_ec_base)
    # compute ymod1 variable that is included in AGI
    ymod1 = (e00200 + e00700 + e00800 + e01400 + e01700 +
             invinc - invinc_agi_ec + e02100 + e02300 +
             np.maximum(e00900 + e02000, (-1)*ALD_BusinessLosses_c[MARS - 1]))
    if CG_nodiff:
        # apply QDIV+CG exclusion if QDIV+LTCG receive no special tax treatment
        qdcg_pos = np.maximum(0., e00650 + c01000)
        qdcg_exclusion = (np.minimum(CG_ec, qdcg_pos) +
                          CG_reinvest_ec_rt * np.maximum(0., qdcg_pos - CG_ec))
        ymod1 = np.maximum(0., ymod1 - qdcg_exclusion)
        invinc_agi_ec += qdcg_exclusion
    # compute ymod variable that is used in OASDI benefit taxation logic
    ymod2 = e00400 + (0.50 * e02400) - c02900
    ymod3 = (1. - ALD_StudentLoan_hc) * e03210 + e03230 + e03240
    ymod = ymod1 + ymod2 + ymod3
    return (c01000, c23650, ymod, ymod1, invinc_agi_ec)


def SSBenefits(MARS, ymod, e02400,
               SS_thd50, SS_thd85, SS_percentage1, SS_percentage2):
    """
    Calculates OASDI benefits included in AGI, c02500.

    Parameters
    ----------
    MARS: int
        Filing marital status (1=single, 2=joint, 3=separate, 4=household-head, 5=widow(er))
    ymod: float
        Variable that is used in OASDI benefit taxation logic
    e02400: float
        Total social security (OASDI) benefits
    SS_thd50: list
        Threshold for social security benefit taxability (1)
    SS_thd85: list
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
    condlist = [ymod < SS_thd50[MARS - 1], ymod < SS_thd85[MARS - 1],
                np.logical_and(ymod >= SS_thd50[MARS - 1], ymod >= SS_thd85[MARS - 1])]

    choicelist = [0.,
                  SS_percentage1 * np.minimum(ymod - SS_thd50[MARS - 1], e02400),
                  np.minimum(SS_percentage2 * (ymod - SS_thd85[MARS - 1]) +
                    SS_percentage1 *
                    np.minimum(e02400, SS_thd85[MARS - 1] -
                        SS_thd50[MARS - 1]), SS_percentage2 * e02400)]

    c02500 = np.select(condlist, choicelist)
    return c02500


def UBI(nu18, n1820, n21, UBI_u18, UBI_1820, UBI_21, UBI_ecrt):
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



@np.vectorize
def AGI(ymod1, c02500, c02900, XTOT, MARS, sep, DSI, exact, nu18, taxable_ubi,
        II_em, II_em_ps, II_prt, II_no_em_nu18):
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
        Filing marital status (1=single, 2=joint, 3=separate, 4=household-head, 5=widow(er))
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
    II_prt: float
        Personal exemption phaseout rate
    II_no_em_nu18: float
        Repeal personal exemptions for dependents under age 18
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
    # calculate personal exemption amount
    if II_no_em_nu18:  # repeal of personal exemptions for deps. under 18
        pre_c04600 = max(0., XTOT - nu18) * II_em
    else:
        pre_c04600 = XTOT * II_em
    if DSI:
        pre_c04600 = 0.
    # phase-out personal exemption amount
    if exact == 1:  # exact calculation as on tax forms
        line5 = max(0., c00100 - II_em_ps)
        line6 = math.ceil(line5 / (2500. / sep))
        line7 = II_prt * line6
        c04600 = max(0., pre_c04600 * (1. - line7))
    else:  # smoothed calculation needed for sensible mtr calculation
        dispc_numer = II_prt * (c00100 - II_em_ps)
        dispc_denom = 2500. / sep
        dispc = min(1., max(0., dispc_numer / dispc_denom))
        c04600 = pre_c04600 * (1. - dispc)
    return (c00100, pre_c04600, c04600)


def ItemDedCap(e17500, e18400, e18500, e19200, e19800, e20100, e20400, g20500,
               c00100, ID_AmountCap_rt, ID_AmountCap_Switch):
    """
    Applies a cap to gross itemized deductions.

    Parameters
    ----------
    e17500: float
        Itemizable medical and dental expenses
    e18400: float
        Itemizable state and local income/sales taxes
    e18500: float
        Itemizable real-estate taxes paid
    e19200: float
        Itemizable interest paid
    e19800: float
        Itemizable charitable giving: cash/check contributions
    e20100: float
        Itemizable charitalb giving: other than cash/check contributions
    e20400: float
        Itemizable gross (before 10% AGI disregard) casualty or theft loss
    g20500: float
        Itemizable gross (before 10% AGI disregard) casualty or theft loss
    c00100: float
        Adjusted gross income (AGI)
    ID_AmountCap_rt: float
        Ceiling on the gross amount of itemized deductions allowed; decimal fraction of AGI
    ID_AmountCap_Switch: list
        Deductions subject to the cap on itemized deduction benefits
    e17500_capped: float
        Schedule A: medical expenses, capped by ItemDedCap as a decimal fraction of AGI
    e18400_capped: float
        Schedule A: state and local income taxes deductlbe, capped by ItemDedCap as a decimal fraction of AGI
    e18500_capped: float
        Schedule A: state and local real estate taxes deductible, capped by ItemDedCap as a decimal fraction of AGI
    e19200_capped: float
        Schedule A: interest deduction deductible, capped by ItemDedCap as decimal fraction of AGI
    e19800_capped: float
        Schedule A: charity cash contributions deductible, capped by ItemDedCap as a decimal fraction of AGI
    e20100_capped: float
        Schedule A: charity noncash contributions deductible, capped aby ItemDedCap s a decimal fraction of AGI
    e20400_capped: float
        Schedule A: gross miscellaneous deductions deductible, capped by ItemDedCap as a decimal fraction of AGI
    g20500_capped: float
        Schedule A: gross casualty or theft loss deductible, capped aby ItemDedCap s a decimal fraction of AGI

    Returns
    -------
    e17500_capped: float
        Schedule A: medical expenses, capped by ItemDedCap as a decimal fraction of AGI
    e18400_capped: float
        Schedule A: state and local income taxes deductlbe, capped by ItemDedCap as a decimal fraction of AGI
    e18500_capped: float
        Schedule A: state and local real estate taxes deductible, capped by ItemDedCap as a decimal fraction of AGI
    e19200_capped: float
        Schedule A: interest deduction deductible, capped by ItemDedCap as decimal fraction of AGI
    e19800_capped: float
        Schedule A: charity cash contributions deductible, capped by ItemDedCap as a decimal fraction of AGI
    e20100_capped: float
        Schedule A: charity noncash contributions deductible, capped by ItemDedCap as a decimal fraction of AGI
    e20400_capped: float
        Schedule A: gross miscellaneous deductions deductible, capped by ItemDedCap as a decimal fraction of AGI
    g20500_capped: float
        Schedule A: gross casualty or theft loss deductible, capped by ItemDedCap as a decimal fraction of AGI
    """
    # pylint: disable=too-many-branches

    cap = np.maximum(0., ID_AmountCap_rt * c00100)

    gross_ded_amt = 0
    if ID_AmountCap_Switch[0]:  # medical
        gross_ded_amt += e17500
    if ID_AmountCap_Switch[1]:  # statelocal
        gross_ded_amt += e18400
    if ID_AmountCap_Switch[2]:  # realestate
        gross_ded_amt += e18500
    if ID_AmountCap_Switch[3]:  # casualty
        gross_ded_amt += g20500
    if ID_AmountCap_Switch[4]:  # misc
        gross_ded_amt += e20400
    if ID_AmountCap_Switch[5]:  # interest
        gross_ded_amt += e19200
    if ID_AmountCap_Switch[6]:  # charity
        gross_ded_amt += e19800 + e20100

    overage = np.maximum(0., gross_ded_amt - cap)

    e17500_capped = e17500
    e18400_capped = e18400
    e18500_capped = e18500
    g20500_capped = g20500
    e20400_capped = e20400
    e19200_capped = e19200
    e19800_capped = e19800
    e20100_capped = e20100


    if ID_AmountCap_Switch[0]:  # medical
        e17500_capped = np.where(np.logical_and(overage > 0., c00100 > 0),
                              e17500_capped - (e17500 / gross_ded_amt) * overage,
                              e17500_capped)
    if ID_AmountCap_Switch[1]:  # statelocal
        e18400_capped = np.where(np.logical_and(overage > 0., c00100 > 0.),
                              e18400_capped - (e18400 / (gross_ded_amt) * overage),
                              e18400_capped)
    if ID_AmountCap_Switch[2]:  # realestate
        e18500_capped = np.where(np.logical_and(overage > 0., c00100 > 0.),
                              e18500_capped - (e18500 / gross_ded_amt) * overage,
                              e18500_capped)
    if ID_AmountCap_Switch[3]:  # casualty
        g20500_capped = np.where(np.logical_and(overage > 0., c00100 > 0.),
                             g20500_capped - (g20500 / gross_ded_amt) * overage,
                             g20500_capped)
    if ID_AmountCap_Switch[4]:  # misc
        e20400_capped = np.where(np.logical_and(overage > 0., c00100 > 0.),
                             e20400_capped - (e20400 / gross_ded_amt) * overage,
                             e20400_capped)
    if ID_AmountCap_Switch[5]:  # interest
        e19200_capped = np.where(np.logical_and(overage > 0., c00100 > 0.),
                             e19200_capped - (e19200 / gross_ded_amt) * overage,
                             e19200_capped)
    if ID_AmountCap_Switch[6]:  # charity
        e19800_capped = np.where(np.logical_and(overage > 0., c00100 > 0.),
                             e19800_capped - (e19800 / gross_ded_amt) * overage,
                             e19800_capped)
        e20100_capped = np.where(np.logical_and(overage > 0., c00100 > 0.),
                             e20100_capped - (e20100 / gross_ded_amt) * overage,
                             e20100_capped)


    return (e17500_capped, e18400_capped, e18500_capped, g20500_capped,
            e20400_capped, e19200_capped, e19800_capped, e20100_capped)



def ItemDed(e17500_capped, e18400_capped, e18500_capped, e19200_capped,
            e19800_capped, e20100_capped, e20400_capped, g20500_capped,
            MARS, age_head, age_spouse, c00100, 
            ID_ps, ID_Medical_frt, ID_Medical_frt_add4aged, ID_Medical_hc,
            ID_Casualty_frt, ID_Casualty_hc, ID_Miscellaneous_frt,
            ID_Miscellaneous_hc, ID_Charity_crt_all, ID_Charity_crt_noncash,
            ID_prt, ID_crt, ID_c, ID_StateLocalTax_hc, ID_Charity_frt,
            ID_Charity_hc, ID_InterestPaid_hc, ID_RealEstate_hc,
            ID_Medical_c, ID_StateLocalTax_c, ID_RealEstate_c,
            ID_InterestPaid_c, ID_Charity_c, ID_Casualty_c,
            ID_Miscellaneous_c, ID_AllTaxes_c, ID_AllTaxes_hc,
            ID_StateLocalTax_crt, ID_RealEstate_crt, ID_Charity_f):
    """
    Calculates itemized deductions, Form 1040, Schedule A.

    Parameters
    ----------
    e17500_capped: float
        Schedule A: medical expenses, capped by ItemDedCap as a decimal fraction of AGI
    e18400_capped: float
        Schedule A: state and local income taxes deductlbe, capped by ItemDedCap as a decimal fraction of AGI
    e18500_capped: float
        Schedule A: state and local real estate taxes deductible, capped by ItemDedCap as a decimal fraction of AGI
    e19200_capped: float
        Schedule A: interest deduction deductible, capped by ItemDedCap as decimal fraction of AGI
    e19800_capped: float
        Schedule A: charity cash contributions deductible, capped by ItemDedCap as a decimal fraction of AGI
    e20100_capped: float
        Schedule A: charity noncash contributions deductible, capped by ItemDedCap as a decimal fraction of AGI
    e20400_capped: float
        Schedule A: gross miscellaneous deductions deductible, capped by ItemDedCap as a decimal fraction of AGI
    g20500_capped: float
        Schedule A: gross casualty or theft loss deductible, capped by ItemDedCap as a decimal fraction of AGI
    MARS: int
        Filing marital status (1=single, 2=joint, 3=separate, 4=household-head, 5=widow(er))
    age_head: int
        Age in years of taxpayer
    age_spouse: int
        Age in years of spouse
    c00100: float
        Adjusted gross income (AGI)
    c04470: float
        Itemized deductions after phase out (0 for non itemizers)
    c21040: float
        Itemized deductions that are phased out
    c21060: float
        Itemized deductions before phase out (0 for non itemizers)
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
    ID_ps: list
        Itemized deduction phaseout AGI start (Pease)
    ID_Medical_frt: float
        Floor (as decimal fraction of AGI) for deductible medical expenses
    ID_Medical_frt_add4aged: float
        Add on floor (as decimal fraction of AGI) for deductible medical expenses for elderly filing units
    ID_Medical_hc: float
        Medical expense deduction haircut
    ID_Casualty_frt: float
        Floor (as decimal fraction of AGI) for deductible casualty loss
    ID_Casualty_hc: float
        Casualty expense deduction haircut
    ID_Miscellaneous_frt: float
        Floor (as decimal fraction of AGI) for deductible miscellaneous expenses
    ID_Miscellaneous_hc: float
        Miscellaneous expense deduction haircut
    ID_Charity_crt_all: float
        Ceiling (as decimal fraction of AGI) for all charitable contribution deductions
    ID_Charity_crt_noncash: float
        Ceiling (as decimal fraction of AGI) for noncash charitable contribution deductions
    ID_prt: float
        Itemized deduction phaseout rate (Pease)
    ID_crt: float
        Itemized deduction maximum phaseout as a decimal fraction of total itemized deductions (Pease)
    ID_c: list
        Ceiling on the amount of itemized deductions allowed (dollars)
    ID_StateLocalTax_hc: float
        State and local income and sales taxes deduction haircut
    ID_Charity_frt: float
        Floor (as decimal fraction of AGI) for deductible charitable contributions
    ID_Charity_hc: float
        Charity expense deduction haircut
    ID_InterestPaid_hc: float
        Interest paid deduction haircut
    ID_RealEstate_hc: float
        State, local, and foreign real estate taxes deductions haircut
    ID_Medical_c: list
        Ceiling on the amount of medical expense deduction allowed (dollars)
    ID_StateLocalTax_c: list
        Ceiling on the amount of state and local income and sales taxes deduction allowed (dollars)
    ID_RealEstate_c: list
        Ceiling on the amount of state, local, and foreign real estate taxes deduction allowed (dollars)
    ID_InterestPaid_c: list
        Ceiling on the amount of interest paid deduction allowed (dollars)
    ID_Charity_c: list
        Ceiling on the amount of charity expense deduction allowed (dollars)
    ID_Casualty_c: list
        Ceiling on the amount of casualty expense deduction allowed (dollars)
    ID_Miscellaneous_c: list
        Ceiling on the amount of miscellaneous expense deduction allowed (dollars)
    ID_AllTaxes_c: list
        Ceiling on the amount of state and local income, stales, and real estate deductions allowed (dollars)
    ID_AllTaxes_hc: float
        State and local income, sales, and real estate tax deduciton haircut
    ID_StateLocalTax_crt: float
        Ceiling (as decimal fraction of AGI) for the combination of all state and local income and sales tax deductions
    ID_RealEstate_crt: float
        Ceiling (as decimal fraction of AGI) for the combination of all state, local, and foreign real estate tax deductions
    ID_Charity_f: list
        Floor on the amount of charity expense deduction allowed (dollars)

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
        Itemized deductions that are phased out
    c21060: float
        Itemized deductions before phase out (0 for non itemizers)
    c04470: float
        Itemized deductions after phase out (0 for non itemizers)
    """
    posagi = np.maximum(c00100, 0.)
    # Medical
    medical_frt = ID_Medical_frt
    medical_frt = np.where(np.logical_or(age_head >= 65, np.logical_and(MARS == 2, age_spouse >= 65)),
                            medical_frt + ID_Medical_frt_add4aged,
                            medical_frt)
    c17750 = medical_frt * posagi
    c17000 = np.maximum(0., e17500_capped - c17750) * (1. - ID_Medical_hc)
    c17000 = np.minimum(c17000, ID_Medical_c[MARS - 1])
    # State and local taxes
    c18400 = np.minimum((1. - ID_StateLocalTax_hc) * np.maximum(e18400_capped, 0.),
                 ID_StateLocalTax_c[MARS - 1])
    c18500 = np.minimum((1. - ID_RealEstate_hc) * e18500_capped,
                 ID_RealEstate_c[MARS - 1])
    # following two statements implement a cap on c18400 and c18500 in a way
    # that those with negative AGI, c00100, are not capped under current law,
    # hence the 0.0001 rather than zero
    c18400 = np.minimum(c18400, ID_StateLocalTax_crt * np.maximum(c00100, 0.0001))
    c18500 = np.minimum(c18500, ID_RealEstate_crt * np.maximum(c00100, 0.0001))
    c18300 = (c18400 + c18500) * (1. - ID_AllTaxes_hc)
    c18300 = np.minimum(c18300, ID_AllTaxes_c[MARS - 1])
    # Interest paid
    c19200 = e19200_capped * (1. - ID_InterestPaid_hc)
    c19200 = np.minimum(c19200, ID_InterestPaid_c[MARS - 1])
    # Charity
    lim30 = np.minimum(ID_Charity_crt_noncash * posagi, e20100_capped)
    c19700 = np.minimum(ID_Charity_crt_all * posagi, lim30 + e19800_capped)
    # charity floor is zero in present law
    charity_floor = np.maximum(ID_Charity_frt * posagi, ID_Charity_f[MARS - 1])
    c19700 = np.maximum(0., c19700 - charity_floor) * (1. - ID_Charity_hc)
    c19700 = np.minimum(c19700, ID_Charity_c[MARS - 1])
    # Casualty
    c20500 = (np.maximum(0., g20500_capped - ID_Casualty_frt * posagi) *
              (1. - ID_Casualty_hc))
    c20500 = np.minimum(c20500, ID_Casualty_c[MARS - 1])
    # Miscellaneous
    c20400 = e20400_capped
    c20750 = ID_Miscellaneous_frt * posagi
    c20800 = np.maximum(0., c20400 - c20750) * (1. - ID_Miscellaneous_hc)
    c20800 = np.minimum(c20800, ID_Miscellaneous_c[MARS - 1])
    # Gross total itemized deductions
    c21060 = c17000 + c18300 + c19200 + c19700 + c20500 + c20800
    # Limitations on total itemized deductions
    # (no attempt to adjust c04470 components for limitations)
    nonlimited = c17000 + c20500
    limitstart = ID_ps[MARS - 1]

    condition = np.logical_and(c21060 > nonlimited, c00100 > limitstart)
    dedmin = np.where(condition, ID_crt * (c21060 - nonlimited), 0.)
    dedpho = np.where(condition, ID_prt * np.maximum(0., posagi - limitstart), 0.)
    c21040 = np.where(condition, np.minimum(dedmin, dedpho), 0.)
    c04470 = np.where(condition, c21060 - c21040, c21060)

    c04470 = np.minimum(c04470, ID_c[MARS - 1])
    # Return total itemized deduction amounts and components
    return (c17000, c18300, c19200, c19700, c20500, c20800,
            c21040, c21060, c04470)


def AdditionalMedicareTax(e00200, MARS, sey, payrolltax,
                          AMEDT_ec, AMEDT_rt,
                          FICA_mc_trt, FICA_ss_trt):
    """
    Computes Additional Medicare Tax (Form 8959) included in payroll taxes.

    Parameters
    -----
    MARS: int
        Filing marital status (1=single, 2=joint, 3=separate, 4=household-head, 5=widow(er))
    AMEDT_ec: list
        Additional Medicare Tax earnings exclusion
    AMEDT_rt: float
        Additional Medicare Tax rate
    FICA_ss_trt: float
        FICA Social Security tax rate
    FICA_mc_trt: float
        FICA Medicare tax rate
    e00200: float
        Wages and salaries
    sey: float
        Self-employment income
    ptax_amc: float
        Additional Medicare Tax
    payrolltax: float
        payroll tax augmented by Additional Medicare Tax

    Returns
    -------
    ptax_amc: float
        Additional Medicare Tax
    payrolltax: float
        payroll tax augmented by Additional Medicare Tax
    """
    line8 = np.maximum(0., sey) * (1. - 0.5 * (FICA_mc_trt + FICA_ss_trt))
    line11 = np.maximum(0., AMEDT_ec[MARS - 1] - e00200)
    ptax_amc = AMEDT_rt * (np.maximum(0., e00200 - AMEDT_ec[MARS - 1]) +
                           np.maximum(0., line8 - line11))
    payrolltax += ptax_amc
    return (ptax_amc, payrolltax)




def StdDed(DSI, earned, age_head, age_spouse, MARS, MIDR,
           blind_head, blind_spouse, standard, c19700,
           STD, STD_Aged, STD_Dep, STD_allow_charity_ded_nonitemizers,
           STD_charity_ded_nonitemizers_max):
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
        Filing (marital) status. (1=single, 2=joint, 3=separate, 4=household-head, 5=widow(er))
    MIDR: int
        1 if separately filing spouse itemizes, 0 otherwise
    blind_head: int
        1 if taxpayer is blind, 0 otherwise
    blind_spouse: int
        1 if spouse is blind, 0 otherwise
    standard: float
        Standard deduction (zero for itemizers)
    c19700: float
        Schedule A: charity contributions deducted
    STD_allow_charity_ded_nonitemizers: bool
        Allow standard deduction filers to take the charitable contributions deduction
    STD_charity_ded_nonitemizers_max: float
        Ceiling amount (in dollars) for charitable deductions for non-itemizers

    Returns
    -------
    standard: float
        Standard deduction (zero for itemizers)
    """
    # calculate deduction for dependents
    c15100 = np.where(DSI == 1, np.maximum(350. + earned, STD_Dep), 0.)
    condlist = [DSI == 1, np.logical_and(DSI != 1, MIDR == 1), np.logical_and(DSI != 1, MIDR != 1)]
    choicelist = [np.minimum(STD[MARS - 1], c15100), 0., STD[MARS - 1]]
    basic_stded = np.select(condlist, choicelist)
    # calculate extra standard deduction for aged and blind
    num_extra_stded = blind_head + blind_spouse
    num_extra_stded = np.where(age_head >= 65, num_extra_stded + 1, num_extra_stded)
    num_extra_stded = np.where(np.logical_and(MARS == 2, age_spouse >= 65), num_extra_stded + 1, num_extra_stded)
    extra_stded = num_extra_stded * STD_Aged[MARS - 1]
    # calculate the total standard deduction
    standard = basic_stded + extra_stded
    standard = np.where(np.logical_and(MARS == 3, MIDR == 1), 0., standard)
    if STD_allow_charity_ded_nonitemizers:
        standard += np.minimum(c19700, STD_charity_ded_nonitemizers_max)

    return standard




@np.vectorize
def TaxInc(c00100, standard, c04470, c04600, MARS, e00900, e26270,
           e02100, e27200, e00650, c01000, e02300, PT_SSTB_income,
           PT_binc_w2_wages, PT_ubia_property, PT_qbid_rt,
           PT_qbid_taxinc_thd, PT_qbid_taxinc_gap, PT_qbid_w2_wages_rt,
           PT_qbid_alt_w2_wages_rt, PT_qbid_alt_property_rt,
           PT_qbid_ps, PT_qbid_prt, PT_qbid_limit_switch,
           UI_em, UI_thd):
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
        Filing (marital) status. (1=single, 2=joint, 3=separate, 4=household-head, 5=widow(er))
    e00900: float
        Schedule C business net profit/loss for filing unit
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
    PT_SSTB_income: int
        Value of one implies business income is from a specified service trade or business (SSTB)
        Value of zero implies business income is from a qualified trade or business
    PT_binc_w2_wages: float
        Filing unit's share of total W-2 wages paid by the pass-through business
    PT_ubia_property: float
        Filing unit's share of total business property owned by the pass-through business
    PT_qbid_rt: float
        Pass-through qualified business income deduction rate
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
    c04800: float
        Regular taxable income
    PT_qbid_ps: list
        QBID phaseout taxable income start
    PT_qbid_prt: float
        QBID phaseout rate
    qbided: float
        Qualified Business Income (QBI) deduction
    PT_qbid_limit_switch: bool
        QBID wage and capital limitations switch

    Returns
    -------
    c04800: float
        Regular taxable income
    qbided: float
        Qualified Busixness Income (QBI) deduction
    """
    # calculate UI excluded from taxable income
    if (c00100 - e02300) <= UI_thd:
        ui_excluded = min(e02300, UI_em)
    else:
        ui_excluded = 0.
    # calculate taxable income before qualified business income deduction
    pre_qbid_taxinc = max(0., c00100 - max(c04470, standard) - c04600 -
                          ui_excluded)
    # calculate qualified business income deduction
    qbided = 0.
    qbinc = max(0., e00900 + e26270 + e02100 + e27200)
    if qbinc > 0. and PT_qbid_rt > 0.:
        qbid_before_limits = qbinc * PT_qbid_rt
        lower_thd = PT_qbid_taxinc_thd
        if pre_qbid_taxinc <= lower_thd:
            qbided = qbid_before_limits
        else:
            pre_qbid_taxinc_gap = PT_qbid_taxinc_gap
            upper_thd = lower_thd + pre_qbid_taxinc_gap
            if PT_SSTB_income == 1 and pre_qbid_taxinc >= upper_thd:
                qbided = 0.
            # if PT_qbid_limit_switch is True, apply wage/capital
            # limitations.
            elif PT_qbid_limit_switch:
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
            # if PT_qbid_limit_switch is False, assume all taxpayers
            # have sufficient wage expenses and capital income to avoid
            # QBID limitations.
            else:
                qbided = qbid_before_limits
        # apply taxinc cap (assuning cap rate is equal to PT_qbid_rt)
        net_cg = e00650 + c01000  # per line 34 in 2018 Pub 535 Worksheet 12-A
        taxinc_cap = PT_qbid_rt * max(0., pre_qbid_taxinc - net_cg)
        qbided = min(qbided, taxinc_cap)

        # apply qbid phaseout
        if qbided > 0. and pre_qbid_taxinc > PT_qbid_ps:
            excess = pre_qbid_taxinc - PT_qbid_ps
            qbided = max(0., qbided - PT_qbid_prt * excess)

    # calculate taxable income after qualified business income deduction
    c04800 = max(0., pre_qbid_taxinc - qbided)
    return (c04800, qbided)


def SchXYZ(taxable_income, MARS, e00900, e26270, e02000, e00200,
           PT_rt1, PT_rt2, PT_rt3, PT_rt4, PT_rt5,
           PT_rt6, PT_rt7, PT_rt8,
           PT_brk1, PT_brk2, PT_brk3, PT_brk4, PT_brk5,
           PT_brk6, PT_brk7,
           II_rt1, II_rt2, II_rt3, II_rt4, II_rt5,
           II_rt6, II_rt7, II_rt8,
           II_brk1, II_brk2, II_brk3, II_brk4, II_brk5,
           II_brk6, II_brk7, PT_EligibleRate_active,
           PT_EligibleRate_passive, PT_wages_active_income,
           PT_top_stacking):
    """
    Returns Schedule X, Y, Z tax amount for specified taxable_income.

    Parameters
    ----------
    taxable_income: float
        Taxable income
    MARS: int
        Filing (marital) status. (1=single, 2=joint, 3=separate, 4=household-head, 5=widow(er))
    e00900: float
        Schedule C business net profit/loss for filing unit
    e26270: float
        Schedule E: combined partnership and S-corporation net income/loss
    e02000: float
        Schedule E total rental, royalty, parternship, S-corporation, etc, income/loss
    e00200: float
        Wages, salaries, and tips for filing unit net of pension contributions
    PT_rt1: float
        Pass through income tax rate 1
    PT_rt2: float
        Pass through income tax rate 2
    PT_rt3: float
        Pass through income tax rate 3
    PT_rt4: float
        Pass through income tax rate 4
    PT_rt5: float
        Pass through income tax rate 5
    PT_rt6: float
        Pass through income tax rate 6
    PT_rt7: float
        Pass through income tax rate 7
    PT_rt8: float
        Pass through income tax rate 8
    PT_brk1: list
        Pass through income tax bracket (upper threshold) 1
    PT_brk2: list
        Pass through income tax bracket (upper threshold) 2
    PT_brk3: list
        Pass through income tax bracket (upper threshold) 3
    PT_brk4: list
        Pass through income tax bracket (upper threshold) 4
    PT_brk5: list
        Pass through income tax bracket (upper threshold) 5
    PT_brk6: list
        Pass through income tax bracket (upper threshold) 6
    PT_brk7: list
        Pass through income tax bracket (upper threshold) 7
    II_rt1: float
        Personal income (regular/non-AMT/non-pass-through) tax rate 1
    II_rt2: float
        Personal income (regular/non-AMT/non-pass-through) tax rate 2
    II_rt3: float
        Personal income (regular/non-AMT/non-pass-through) tax rate 3
    II_rt4: float
        Personal income (regular/non-AMT/non-pass-through) tax rate 4
    II_rt5: float
        Personal income (regular/non-AMT/non-pass-through) tax rate 5
    II_rt6: float
        Personal income (regular/non-AMT/non-pass-through) tax rate 6
    II_rt7: float
        Personal income (regular/non-AMT/non-pass-through) tax rate 7
    II_rt8: float
        Personal income (regular/non-AMT/non-pass-through) tax rate 8
    II_brk1: list
        Personal income (regular/non-AMT/non-pass/through) tax bracket (upper threshold) 1
    II_brk2: list
        Personal income (regular/non-AMT/non-pass/through) tax bracket (upper threshold) 2
    II_brk3: list
        Personal income (regular/non-AMT/non-pass/through) tax bracket (upper threshold) 3
    II_brk4: list
        Personal income (regular/non-AMT/non-pass/through) tax bracket (upper threshold) 4
    II_brk5: list
        Personal income (regular/non-AMT/non-pass/through) tax bracket (upper threshold) 5
    II_brk6: list
        Personal income (regular/non-AMT/non-pass/through) tax bracket (upper threshold) 6
    II_brk7: list
        Personal income (regular/non-AMT/non-pass/through) tax bracket (upper threshold) 7
    PT_EligibleRate_active: float
        Share of active business income eligible for PT rate schedule
    PT_EligibleRate_passive: float
        Share of passive business income eligible for PT rate schedule
    PT_wages_active_income: bool
        Wages included in (positive) active business eligible for PT rates
    PT_top_stacking: bool
        PT taxable income stacked on top of regular taxable income

    Returns
    -------
    reg_tax: float
        Individual income tax liability on non-pass-through income
    pt_tax: float
        Individual income tax liability from pass-through income
    """
    # separate non-negative taxable income into two non-negative components,
    # doing this in a way so that the components add up to taxable income
    # define pass-through income eligible for PT schedule
    pt_passive = PT_EligibleRate_passive * (e02000 - e26270)
    pt_active_gross = e00900 + e26270
    pt_active_gross = np.where(np.logical_and(pt_active_gross > 0, PT_wages_active_income),
                                pt_active_gross + e00200,
                                pt_active_gross)
    pt_active = PT_EligibleRate_active * pt_active_gross
    pt_active = np.minimum(pt_active, e00900 + e26270)
    pt_taxinc = np.maximum(0., pt_passive + pt_active)
    pt_taxinc = np.where(pt_taxinc >= taxable_income, taxable_income, pt_taxinc)
    reg_taxinc = np.where(pt_taxinc >= taxable_income, 0., taxable_income - pt_taxinc)
    # determine stacking order
    if PT_top_stacking:
        reg_tbase = 0.
        pt_tbase = reg_taxinc
    else:
        reg_tbase = pt_taxinc
        pt_tbase = 0.
    # compute Schedule X,Y,Z tax using the two components of taxable income
    reg_tax = np.where(reg_taxinc > 0.,
                       Taxes(reg_taxinc, MARS, reg_tbase,
                       II_rt1, II_rt2, II_rt3, II_rt4,
                       II_rt5, II_rt6, II_rt7, II_rt8, II_brk1, II_brk2,
                       II_brk3, II_brk4, II_brk5, II_brk6, II_brk7),
                       0.)
    pt_tax = np.where(pt_taxinc > 0.,
                      Taxes(pt_taxinc, MARS, pt_tbase,
                      PT_rt1, PT_rt2, PT_rt3, PT_rt4,
                      PT_rt5, PT_rt6, PT_rt7, PT_rt8, PT_brk1, PT_brk2,
                      PT_brk3, PT_brk4, PT_brk5, PT_brk6, PT_brk7),
                      0.)
    return reg_tax + pt_tax



def SchXYZTax(c04800, MARS, e00900, e26270, e02000, e00200,
              PT_rt1, PT_rt2, PT_rt3, PT_rt4, PT_rt5,
              PT_rt6, PT_rt7, PT_rt8,
              PT_brk1, PT_brk2, PT_brk3, PT_brk4, PT_brk5,
              PT_brk6, PT_brk7,
              II_rt1, II_rt2, II_rt3, II_rt4, II_rt5,
              II_rt6, II_rt7, II_rt8,
              II_brk1, II_brk2, II_brk3, II_brk4, II_brk5,
              II_brk6, II_brk7, PT_EligibleRate_active,
              PT_EligibleRate_passive, PT_wages_active_income,
              PT_top_stacking):
    """
    SchXYZTax calls SchXYZ function and sets c05200 to returned amount.

    Parameters
    ----------
    c04800: float
        Regular taxable income
    MARS: int
        Filing (marital) status. (1=single, 2=joint, 3=separate, 4=household-head, 5=widow(er))
    e00900: float
        Schedule C business net profit/loss for filing unit
    e26270: float
        Schedule E: combined partnership and S-corporation net income/loss
    e02000: float
        Farm net income/loss for filing unit from Schedule F
    e00200: float
        Farm net income/loss for filing unit from Schedule F
    PT_rt1: float
        Pass through income tax rate 1
    PT_rt2: float
        Pass through income tax rate 2
    PT_rt3: float
        Pass through income tax rate 3
    PT_rt4: float
        Pass through income tax rate 4
    PT_rt5: float
        Pass through income tax rate 5
    PT_rt6: float
        Pass through income tax rate 6
    PT_rt7: float
        Pass through income tax rate 7
    PT_rt8: float
        Pass through income tax rate 8
    PT_brk1: list
        Pass through income tax bracket (upper threshold) 1
    PT_brk2: list
        Pass through income tax bracket (upper threshold) 2
    PT_brk3: list
        Pass through income tax bracket (upper threshold) 3
    PT_brk4: list
        Pass through income tax bracket (upper threshold) 4
    PT_brk5: list
        Pass through income tax bracket (upper threshold) 5
    PT_brk6: list
        Pass through income tax bracket (upper threshold) 6
    PT_brk7: list
        Pass through income tax bracket (upper threshold) 7
    II_rt1: float
        Personal income (regular/non-AMT/non-pass-through) tax rate 1
    II_rt2: float
        Personal income (regular/non-AMT/non-pass-through) tax rate 2
    II_rt3: float
        Personal income (regular/non-AMT/non-pass-through) tax rate 3
    II_rt4: float
        Personal income (regular/non-AMT/non-pass-through) tax rate 4
    II_rt5: float
        Personal income (regular/non-AMT/non-pass-through) tax rate 5
    II_rt6: float
        Personal income (regular/non-AMT/non-pass-through) tax rate 6
    II_rt7: float
        Personal income (regular/non-AMT/non-pass-through) tax rate 7
    II_rt8: float
        Personal income (regular/non-AMT/non-pass-through) tax rate 8
    II_brk1: list
        Personal income (regular/non-AMT/non-pass/through) tax bracket (upper threshold) 1
    II_brk2: list
        Personal income (regular/non-AMT/non-pass/through) tax bracket (upper threshold) 2
    II_brk3: list
        Personal income (regular/non-AMT/non-pass/through) tax bracket (upper threshold) 3
    II_brk4: list
        Personal income (regular/non-AMT/non-pass/through) tax bracket (upper threshold) 4
    II_brk5: list
        Personal income (regular/non-AMT/non-pass/through) tax bracket (upper threshold) 5
    II_brk6: list
        Personal income (regular/non-AMT/non-pass/through) tax bracket (upper threshold) 6
    II_brk7: list
        Personal income (regular/non-AMT/non-pass/through) tax bracket (upper threshold) 7
    PT_EligibleRate_active: float
        Share of active business income eligible for PT rate schedule
    PT_EligibleRate_passive: float
        Share of passive business income eligible for PT rate schedule
    PT_wages_active_income: bool
        Wages included in (positive) active business eligible for PT rates
    PT_top_stacking: bool
        PT taxable income stacked on top of regular taxable income
    c05200: float
        Tax amount from Schedule X,Y,Z tables

    Returns
    -------
    c05200: float
        Tax aount from Schedule X, Y, Z tables
    """
    c05200 = SchXYZ(c04800, MARS, e00900, e26270, e02000, e00200,
                    PT_rt1, PT_rt2, PT_rt3, PT_rt4, PT_rt5,
                    PT_rt6, PT_rt7, PT_rt8,
                    PT_brk1, PT_brk2, PT_brk3, PT_brk4, PT_brk5,
                    PT_brk6, PT_brk7,
                    II_rt1, II_rt2, II_rt3, II_rt4, II_rt5,
                    II_rt6, II_rt7, II_rt8,
                    II_brk1, II_brk2, II_brk3, II_brk4, II_brk5,
                    II_brk6, II_brk7, PT_EligibleRate_active,
                    PT_EligibleRate_passive, PT_wages_active_income,
                    PT_top_stacking)
    return c05200


def GainsTax(e00650, c01000, c23650, p23250, e01100, e58990, e00200,
             e24515, e24518, MARS, c04800, c05200, e00900, e26270, e02000,
             II_rt1, II_rt2, II_rt3, II_rt4, II_rt5, II_rt6, II_rt7, II_rt8,
             II_brk1, II_brk2, II_brk3, II_brk4, II_brk5, II_brk6, II_brk7,
             PT_rt1, PT_rt2, PT_rt3, PT_rt4, PT_rt5, PT_rt6, PT_rt7, PT_rt8,
             PT_brk1, PT_brk2, PT_brk3, PT_brk4, PT_brk5, PT_brk6, PT_brk7,
             CG_nodiff, PT_EligibleRate_active, PT_EligibleRate_passive,
             PT_wages_active_income, PT_top_stacking,
             CG_rt1, CG_rt2, CG_rt3, CG_rt4, CG_brk1, CG_brk2, CG_brk3):
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
    e00200: float
        Wages, salaries, and tips for filing unit net of pension contributions
    e24515: float
        Schedule D: un-recaptured section 1250 Gain
    e24518: float
        Schedule D: 28% rate gain or loss
    MARS: int
        Filing (marital) status. (1=single, 2=joint, 3=separate, 4=household-head, 5=widow(er))
    c04800: float
        Regular taxable income
    c05200: float
        Tax amount from Schedule X,Y,Z tables
    e00900: float
        Schedule C business net profit/loss for filing unit
    e26270: float
        Schedule E: combined partnership and S-corporation net income/loss
    e02000: float
        Schedule E total rental, royalty, partnership, S-corporation, etc, income/loss
    II_rt1: float
        Personal income (regular/non-AMT/non-pass-through) tax rate 1
    II_rt2: float
        Personal income (regular/non-AMT/non-pass-through) tax rate 2
    II_rt3: float
        Personal income (regular/non-AMT/non-pass-through) tax rate 3
    II_rt4: float
        Personal income (regular/non-AMT/non-pass-through) tax rate 4
    II_rt5: float
        Personal income (regular/non-AMT/non-pass-through) tax rate 5
    II_rt6: float
        Personal income (regular/non-AMT/non-pass-through) tax rate 6
    II_rt7: float
        Personal income (regular/non-AMT/non-pass-through) tax rate 7
    II_rt8: float
        Personal income (regular/non-AMT/non-pass-through) tax rate 8
    II_brk1: list
        Personal income (regular/non-AMT/non-pass/through) tax bracket (upper threshold) 1
    II_brk2: list
        Personal income (regular/non-AMT/non-pass/through) tax bracket (upper threshold) 2
    II_brk3: list
        Personal income (regular/non-AMT/non-pass/through) tax bracket (upper threshold) 3
    II_brk4: list
        Personal income (regular/non-AMT/non-pass/through) tax bracket (upper threshold) 4
    II_brk5: list
        Personal income (regular/non-AMT/non-pass/through) tax bracket (upper threshold) 5
    II_brk6: list
        Personal income (regular/non-AMT/non-pass/through) tax bracket (upper threshold) 6
    II_brk7: list
        Personal income (regular/non-AMT/non-pass/through) tax bracket (upper threshold) 7
    PT_rt1: float
        Pass through income tax rate 1
    PT_rt2: float
        Pass through income tax rate 2
    PT_rt3: float
        Pass through income tax rate 3
    PT_rt4: float
        Pass through income tax rate 4
    PT_rt5: float
        Pass through income tax rate 5
    PT_rt6: float
        Pass through income tax rate 6
    PT_rt7: float
        Pass through income tax rate 7
    PT_rt8: float
        Pass through income tax rate 8
    PT_brk1: list
        Pass through income tax bracket (upper threshold) 1
    PT_brk2: list
        Pass through income tax bracket (upper threshold) 2
    PT_brk3: list
        Pass through income tax bracket (upper threshold) 3
    PT_brk4: list
        Pass through income tax bracket (upper threshold) 4
    PT_brk5: list
        Pass through income tax bracket (upper threshold) 5
    PT_brk6: list
        Pass through income tax bracket (upper threshold) 6
    PT_brk7: list
        Pass through income tax bracket (upper threshold) 7
    CG_nodiff: bool
        Long term capital gains and qualified dividends taxed no differently than regular taxable income
    PT_EligibleRate_active: float
        Share of active business income eligible for PT rate schedule
    PT_EligibleRate_passive: float
        Share of passive business income eligible for PT rate schedule
    PT_wages_active_income: bool
        Wages included in (positive) active business eligible for PT rates
    PT_top_stacking: bool
        PT taxable income stacked on top of regular taxable income
    CG_rt1: float
        Long term capital gain and qualified dividends (regular/non-AMT) rate 1
    CG_rt2: float
        Long term capital gain and qualified dividends (regular/non-AMT) rate 2
    CG_rt3: float
        Long term capital gain and qualified dividends (regular/non-AMT) rate 3
    CG_rt4: float
        Long term capital gain and qualified dividends (regular/non-AMT) rate 4
    CG_brk1: list
        Top of long-term capital gains and qualified dividends (regular/non-AMT) tax bracket 1
    CG_brk2: list
        Top of long-term capital gains and qualified dividends (regular/non-AMT) tax bracket 2
    CG_brk3: list
        Top of long-term capital gains and qualified dividends (regular/non-AMT) tax bracket 3
    dwks10: float
        Sum of dwks6 + dwks9
    dwks13: float
        Difference of dwks10 - dwks12
    dwks14: float
        Maximum of 0 and dwks1 - dwks13
    dwks19: float
        Maximum of dwks17 and dwks16
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
    c05700: float
        Lump sum distributions
    taxbc: float
        Regular tax on regular taxable income before credits
    """
    # pylint: disable=too-many-statements
    
    cond = np.any([c01000 > 0., c23650 > 0., p23250 > 0.,
                   e01100 > 0., e00650 > 0.], axis=0)
    hasqdivltcg = np.where(cond, 1, 0)

    if CG_nodiff:
        hasqdivltcg = 0.  # no special taxation of qual divids and l-t cap gains

    dwks1 = np.where(hasqdivltcg == 1, c04800, 0.)
    dwks2 = np.where(hasqdivltcg == 1, e00650, 0.)
    dwks3 = np.where(hasqdivltcg == 1, e58990, 0.)
    dwks4 = 0.  # always assumed to be zero
    dwks5 = np.where(hasqdivltcg == 1, np.maximum(0., dwks3 - dwks4), 0.)
    dwks6 = np.where(hasqdivltcg == 1, np.maximum(0., dwks2 - dwks5), 0.)
    dwks7 = np.where(hasqdivltcg == 1, np.minimum(p23250, c23650), 0.)  # SchD lines 15 and 16, respectively
    # dwks8 = np.where(hasqdivltcg == 1, np.minimum(dwks3, dwks4), 0.)
    # dwks9 = np.where(hasqdivltcg == 1, np.maximum(0., dwks7 - dwks8), 0.)
    # BELOW TWO STATEMENTS ARE UNCLEAR IN LIGHT OF dwks9=... COMMENT
    condlist = [np.logical_and(hasqdivltcg == 1, e01100 > 0.), np.logical_and(hasqdivltcg == 1, e01100 <= 0.)]
    choicelist = [e01100, np.maximum(0., dwks7) + e01100]
    c24510 = np.select(condlist, choicelist)
    dwks9 = np.where(hasqdivltcg == 1, np.maximum(0., c24510 - np.minimum(0., e58990)), 0.)
    # ABOVE TWO STATEMENTS ARE UNCLEAR IN LIGHT OF dwks9=... COMMENT
    dwks10 = np.where(hasqdivltcg == 1, dwks6 + dwks9, np.maximum(0., np.minimum(p23250, c23650)) + e01100)
    dwks11 = np.where(hasqdivltcg == 1, e24515 + e24518, 0.)  # SchD lines 18 and 19, respectively
    dwks12 = np.where(hasqdivltcg == 1, np.minimum(dwks9, dwks11), 0.)
    dwks13 = np.where(hasqdivltcg == 1, dwks10 - dwks12, 0.)
    dwks14 = np.where(hasqdivltcg == 1, np.maximum(0., dwks1 - dwks13), 0.)
    dwks16 = np.where(hasqdivltcg == 1, np.minimum(CG_brk1[MARS - 1], dwks1), 0.)
    dwks17 = np.where(hasqdivltcg == 1, np.minimum(dwks14, dwks16), 0.)
    dwks18 = np.where(hasqdivltcg == 1, np.maximum(0., dwks1 - dwks10), 0.)
    dwks19 = np.where(hasqdivltcg == 1, np.maximum(dwks17, dwks18), 0.)
    dwks20 = np.where(hasqdivltcg == 1, dwks16 - dwks17, 0.)
    lowest_rate_tax = np.where(hasqdivltcg == 1, CG_rt1 * dwks20, 0.)
    # break in worksheet lines
    dwks21 = np.where(hasqdivltcg == 1, np.minimum(dwks1, dwks13), 0.)
    dwks22 = np.where(hasqdivltcg == 1, dwks20, 0.)
    dwks23 = np.where(hasqdivltcg == 1, np.maximum(0., dwks21 - dwks22), 0.)
    dwks25 = np.where(hasqdivltcg == 1, np.minimum(CG_brk2[MARS - 1], dwks1), 0.)
    dwks26 = np.where(hasqdivltcg == 1, dwks19 + dwks20, 0.)
    dwks27 = np.where(hasqdivltcg == 1, np.maximum(0., dwks25 - dwks26), 0.)
    dwks28 = np.where(hasqdivltcg == 1, np.minimum(dwks23, dwks27), 0.)
    dwks29 = np.where(hasqdivltcg == 1, CG_rt2 * dwks28, 0.)
    dwks30 = np.where(hasqdivltcg == 1, dwks22 + dwks28, 0.)
    dwks31 = np.where(hasqdivltcg == 1, dwks21 - dwks30, 0.)
    dwks32 = np.where(hasqdivltcg == 1, CG_rt3 * dwks31, 0.)
    # compute total taxable CG for additional top bracket
    cg_all = np.where(hasqdivltcg == 1, dwks20 + dwks28 + dwks31, 0.)
    hi_base = np.where(hasqdivltcg == 1, np.maximum(0., cg_all - CG_brk3[MARS - 1]), 0.)
    hi_incremental_rate = np.where(hasqdivltcg == 1, CG_rt4 - CG_rt3, 0.)
    highest_rate_incremental_tax = np.where(hasqdivltcg == 1, hi_incremental_rate * hi_base, 0.)
    # break in worksheet lines
    dwks33 = np.where(hasqdivltcg == 1, np.minimum(dwks9, e24515), 0.)
    dwks34 = np.where(hasqdivltcg == 1, dwks10 + dwks19, 0.)
    dwks36 = np.where(hasqdivltcg == 1, np.maximum(0., dwks34 - dwks1), 0.)
    dwks37 = np.where(hasqdivltcg == 1, np.maximum(0., dwks33 - dwks36), 0.)
    dwks38 = np.where(hasqdivltcg == 1, 0.25 * dwks37, 0.)
    # break in worksheet lines
    dwks39 = np.where(hasqdivltcg == 1, dwks19 + dwks20 + dwks28 + dwks31 + dwks37, 0.)
    dwks40 = np.where(hasqdivltcg == 1, dwks1 - dwks39, 0.)
    dwks41 = np.where(hasqdivltcg == 1, 0.28 * dwks40, 0.)
    dwks42 = np.where(hasqdivltcg == 1,
                    SchXYZ(dwks19, MARS, e00900, e26270, e02000, e00200,
                    PT_rt1, PT_rt2, PT_rt3, PT_rt4, PT_rt5,
                    PT_rt6, PT_rt7, PT_rt8,
                    PT_brk1, PT_brk2, PT_brk3, PT_brk4, PT_brk5,
                    PT_brk6, PT_brk7,
                    II_rt1, II_rt2, II_rt3, II_rt4, II_rt5,
                    II_rt6, II_rt7, II_rt8,
                    II_brk1, II_brk2, II_brk3, II_brk4, II_brk5,
                    II_brk6, II_brk7, PT_EligibleRate_active,
                    PT_EligibleRate_passive, PT_wages_active_income,
                    PT_top_stacking),
                    0.)
    dwks43 = np.where(hasqdivltcg == 1,
                    (dwks29 + dwks32 + dwks38 + dwks41 + dwks42 +
                    lowest_rate_tax + highest_rate_incremental_tax),
                    0.)
    dwks44 = np.where(hasqdivltcg == 1, c05200, 0.)
    dwks45 = np.where(hasqdivltcg == 1, np.minimum(dwks43, dwks44), 0.)
    c24580 = np.where(hasqdivltcg == 1, dwks45, c05200)

    # final calculations done no matter what the value of hasqdivltcg
    c05100 = c24580  # because foreign earned income exclusion is assumed zero
    c05700 = 0.  # no Form 4972, Lump Sum Distributions
    taxbc = c05700 + c05100

    return (dwks10, dwks13, dwks14, dwks19, c05700, taxbc)



def AGIsurtax(c00100, MARS, taxbc, surtax, AGI_surtax_trt, AGI_surtax_thd):
    """
    Computes surtax on AGI above some threshold.

    Parameters
    ----------
    c00100: float
        Adjusted Gross Income (AGI)
    MARS: int
        Filing (marital) status. (1=single, 2=joint, 3=separate, 4=household-head, 5=widow(er))
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
        hiAGItax = AGI_surtax_trt * np.maximum(c00100 - AGI_surtax_thd[MARS - 1], 0.)
        taxbc += hiAGItax
        surtax += hiAGItax
    return (taxbc, surtax)


def AMT(e07300, dwks13, standard, f6251, c00100, c18300, taxbc,
        c04470, c17000, c20800, c21040, e24515, MARS, sep, dwks19,
        dwks14, c05700, e62900, e00700, dwks10, age_head, age_spouse,
        earned, cmbtp,
        AMT_child_em_c_age, AMT_brk1,
        AMT_em, AMT_prt, AMT_rt1, AMT_rt2,
        AMT_child_em, AMT_em_ps, AMT_em_pe,
        AMT_CG_brk1, AMT_CG_brk2, AMT_CG_brk3, AMT_CG_rt1, AMT_CG_rt2,
        AMT_CG_rt3, AMT_CG_rt4):
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
        Itemized deductions after phase-out (zero for non itemizers)
    c17000: float
        Schedule A: Medical expenses deducted
    c20800: float
        Schedule A: net limited miscellaneous deductions deducted
    c21040: float
        Itemized deductiosn that are phased out
    e24515: float
        Schedule D: Un-Recaptured Section 1250 Gain
    MARS: int
        Filing (marital) status. (1=single, 2=joint, 3=separate, 4=household-head, 5=widow(er))
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
        Schedule C business net profit/loss for filing unit
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
        AMT exemption phaseout ending AMT taxable income for Married Filing Separately
    AMT_CG_brk1: list
        Top of long-term capital gains and qualified dividends (AMT) tax bracket 1
    AMT_CG_brk2: list
        Top of long-term capital gains and qualified dividends (AMT) tax bracket 2
    AMT_CG_brk3: list
        Top of long-term capital gains and qualified dividends (AMT) tax bracket 3
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
    c62100 = np.where(standard == 0.0,
                      (c00100 - e00700 - c04470 +
                       np.maximum(0., np.minimum(c17000, 0.025 * c00100)) +
                       c18300 + c20800 - c21040),
                      0.)
    c62100 = np.where(standard > 0.0, c00100 - e00700, c62100)
    c62100 += cmbtp  # add income not in AGI but considered income for AMT
    amtsepadd = np.where(MARS == 3,
                         np.maximum(0.,
                             np.minimum(AMT_em[MARS - 1], AMT_prt * (c62100 - AMT_em_pe))),
                         0.)
    c62100 = c62100 + amtsepadd  # AMT taxable income, which is line28
    # Form 6251, Part II top
    line29 = np.maximum(0., AMT_em[MARS - 1] - AMT_prt *
                 np.maximum(0., c62100 - AMT_em_ps[MARS - 1]))
    young_head = np.logical_and(age_head != 0, age_head < AMT_child_em_c_age)
    no_or_young_spouse = np.where(age_spouse < AMT_child_em_c_age, True, False)
    line29 = np.where(np.logical_and(young_head, no_or_young_spouse),
                      np.minimum(line29, earned + AMT_child_em),
                      line29)
    line30 = np.maximum(0., c62100 - line29)
    line3163 = (AMT_rt1 * line30 +
                AMT_rt2 * np.maximum(0., (line30 - (AMT_brk1 / sep))))
    cond = np.any([dwks10 > 0., dwks13 > 0., dwks14 > 0., dwks19 > 0., e24515 > 0.], axis=0)
    # complete Form 6251, Part III (line36 is equal to line30)
    line37 = np.where(cond, dwks13, 0.)
    line38 = np.where(cond, e24515, 0.)
    line39 = np.where(cond, np.minimum(line37 + line38, dwks10), 0.)
    line40 = np.where(cond, np.minimum(line30, line39), 0.)
    line41 = np.where(cond, np.maximum(0., line30 - line40), 0.)
    line42 = np.where(cond,
                     (AMT_rt1 * line41 +
                     AMT_rt2 * np.maximum(0., (line41 - (AMT_brk1 / sep)))),
                     0.)
    line44 = np.where(cond, dwks14, 0.)
    line45 = np.where(cond, np.maximum(0., AMT_CG_brk1[MARS - 1] - line44), 0.)
    line46 = np.where(cond, np.minimum(line30, line37), 0.)
    line47 = np.where(cond, np.minimum(line45, line46), 0.)  # line47 is amount taxed at AMT_CG_rt1
    cgtax1 = np.where(cond, line47 * AMT_CG_rt1, 0.)
    line48 = np.where(cond, line46 - line47, 0.)
    line51 = np.where(cond, dwks19, 0.)
    line52 = np.where(cond, line45 + line51, 0.)
    line53 = np.where(cond, np.maximum(0., AMT_CG_brk2[MARS - 1] - line52), 0.)
    line54 = np.where(cond, np.minimum(line48, line53), 0.)  # line54 is amount taxed at AMT_CG_rt2
    cgtax2 = np.where(cond, line54 * AMT_CG_rt2, 0.)
    line56 = np.where(cond, line47 + line54, 0.)  # total amount in lower two brackets

    condlist = [np.logical_and(cond, line41 == line56), np.logical_and(cond, line41 != line56)]
    line57 = np.select(condlist, [0., line46 - line56])
    linex1 = np.select(condlist, [0., np.minimum(line48,
                                      np.maximum(0., AMT_CG_brk3[MARS - 1] - line44 - line45))]
                                      )
    linex2 = np.select(condlist, [0., np.maximum(0., line54 - linex1)])
    cgtax3 = np.where(cond, line57 * AMT_CG_rt3, 0.)
    cgtax4 = np.where(cond, linex2 * AMT_CG_rt4, 0.)

    condlist = [np.logical_and(cond, line38 == 0.), np.logical_and(cond, line38 != 0.)]
    line61 = np.select(condlist, [0., 0.25 * np.maximum(0., line30 - line41 - line56 - line57 - linex2)])
    line62 = np.where(cond, line42 + cgtax1 + cgtax2 + cgtax3 + cgtax4 + line61, 0.)
    line64 = np.where(cond, np.minimum(line3163, line62), 0.)
    line31 = np.where(cond, line64, line3163) # if not completing Form 6251, Part III
    # Form 6251, Part II bottom
    line32 = np.where(f6251 == 1, e62900, e07300)
    line33 = line31 - line32
    c09600 = np.maximum(0., line33 - np.maximum(0., taxbc - e07300 - c05700))
    c05800 = taxbc + c09600
    return (c62100, c09600, c05800)



def NetInvIncTax(e00300, e00600, e02000, e26270, c01000,
                 c00100, MARS, niit, NIIT_thd, NIIT_PT_taxed, NIIT_rt):
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
        Schedule E total rental, royalty, parternship, S-corporation, etc, income/loss
    e26270: float
        Schedule E: combined partnership and S-corporation net income/loss
    c01000: float
        Limitation on capital losses
    c00100: float
        Adjusted Gross Income (AGI)
    NIIT_thd: list
        Net Investment Income Tax modified AGI threshold
    MARS: int
        Filing (marital) status. (1=single, 2=joint, 3=separate, 4=household-head, 5=widow(er))
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
        NII = np.maximum(0., e00300 + e00600 + c01000 + e02000 - e26270)
    else:  # do not subtract e26270 from e02000
        NII = np.maximum(0., e00300 + e00600 + c01000 + e02000)
    niit = NIIT_rt * np.minimum(NII, np.maximum(0., modAGI - NIIT_thd[MARS - 1]))
    return niit



@np.vectorize
def F2441(MARS, earned_p, earned_s, f2441, e32800, exact, c00100, 
          c05800, e07300, c07180, CDCC_refund, CDCC_c, CDCC_ps, CDCC_ps2,
          CDCC_crt, CDCC_frt, CDCC_prt, CDCC_refundable):
    """
    Calculates Form 2441 child and dependent care expense credit, c07180.

    Parameters
    ----------
    MARS: int
        Filing (marital) status. (1=single, 2=joint, 3=separate, 4=household-head, 5=widow(er))
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
    CDCC_ps: float
        Child/dependent care credit phaseout start
    CDCC_crt: float
        Child/dependent care credit phaseout percentage rate ceiling
    c05800: float
        Total (regular + AMT) income tax liability before credits
    e07300: float
        Foreign tax credit from Form 1116
    c07180: float
        Credit for child and dependent care expenses from Form 2441

    Returns
    -------
    c07180: float
        Credit for child and dependent care expenses from Form 2441
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
    c33000 = max(0., min(c32800, min(c32880, c32890)))
    # credit is limited by AGI-related fraction
    if exact == 1:  # exact calculation as on tax forms
        # first phase-down from 35 to 20 percent
        tratio1 = math.ceil(max(((c00100 - CDCC_ps) * CDCC_prt), 0.))
        crate = max(CDCC_frt, CDCC_crt - min(CDCC_crt - CDCC_frt, tratio1))
        # second phase-down from 20 percent to zero
        if c00100 > CDCC_ps2:
            tratio2 = math.ceil(max(((c00100 - CDCC_ps2) * CDCC_prt), 0.))
            crate = max(0., CDCC_frt - min(CDCC_frt, tratio2))
    else:
        crate = max(CDCC_frt, CDCC_crt -
                    max(((c00100 - CDCC_ps) * CDCC_prt), 0.))
        if c00100 > CDCC_ps2:
            crate = max(0., CDCC_frt -
                        max(((c00100 - CDCC_ps2) * CDCC_prt), 0.))
    c33200 = c33000 * 0.01 * crate
    # credit is limited by tax liability if not refundable
    if CDCC_refundable:
        c07180 = 0.
        CDCC_refund = c33200
    else:
        c07180 = min(max(0., c05800 - e07300), c33200)
        CDCC_refund = 0.
    return (c07180, CDCC_refund)


def EITCamount(basic_frac, phasein_rate, earnings, max_amount,
               phaseout_start, agi, phaseout_rate):
    """
    Returns EITC amount given specified parameters.
    English parameter names are used in this function because the
    EITC formula is not available on IRS forms or in IRS instructions;
    the extensive IRS EITC look-up table does not reveal the formula.

    Parameters
    ----------
    basic_frac: list
        Fraction of maximum earned income credit paid at zero earnings
    phasein_rate: list
        Earned income credit phasein rate
    earnings: float
        Earned income for filing unit
    max_amount: list
        Maximum earned income credit
    phaseout_start: list
        Earned income credit phaseout start AGI
    agi: float
        Adjusted Gross Income (AGI)
    phaseout_rate: list
        Earned income credit phaseout rate

    Returns
    -------
    eitc: float
        Earned Income Credit
    """
    eitc = np.minimum((basic_frac * max_amount +
                (1.0 - basic_frac) * phasein_rate * earnings), max_amount)
    eitcx = np.where(np.logical_or(earnings > phaseout_start, agi > phaseout_start),
                    np.maximum(0., (max_amount - phaseout_rate *
                         np.maximum(0., np.maximum(earnings, agi) - phaseout_start))),
                    0.)
    eitc = np.where(np.logical_or(earnings > phaseout_start, agi > phaseout_start),
                    np.minimum(eitc, eitcx),
                    eitc)
    return eitc



@np.vectorize
def EITC(MARS, DSI, EIC, c00100, e00300, e00400, e00600, c01000,
         e02000, e26270, age_head, age_spouse, earned, earned_p, earned_s,
         EITC_ps, EITC_MinEligAge, EITC_MaxEligAge, EITC_ps_MarriedJ,
         EITC_rt, EITC_c, EITC_prt, EITC_basic_frac,
         EITC_InvestIncome_c, EITC_excess_InvestIncome_rt,
         EITC_indiv, EITC_sep_filers_elig):
    """
    Computes EITC amount, c59660.

    Parameters
    ----------
    MARS: int
        Filing (marital) status. (1=single, 2=joint, 3=separate, 4=household-head, 5=widow(er))
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
        Schedule E total rental, royalty, partnership, S-corporation, etc, income/loss
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
        Extra earned income credit phaseout start AGI for married filling jointly
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
                          EITC_rt, earned, EITC_c,
                          EITC_ps, c00100, EITC_prt)
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
        po_start = EITC_ps + EITC_ps_MarriedJ
        if not EITC_indiv:
            # filing unit EITC rather than individual EITC
            eitc = EITCamount(EITC_basic_frac,
                              EITC_rt, earned, EITC_c,
                              po_start, c00100, EITC_prt)
        if EITC_indiv:
            # individual EITC rather than a filing-unit EITC
            eitc_p = EITCamount(EITC_basic_frac,
                                EITC_rt, earned_p, EITC_c,
                                po_start, earned_p, EITC_prt)
            eitc_s = EITCamount(EITC_basic_frac,
                                EITC_rt, earned_s, EITC_c,
                                po_start, earned_s, EITC_prt)
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



def RefundablePayrollTaxCredit(was_plus_sey_p, was_plus_sey_s,
                               RPTC_c, RPTC_rt):
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
    rptc_p = np.minimum(was_plus_sey_p * RPTC_rt, RPTC_c)
    rptc_s = np.minimum(was_plus_sey_s * RPTC_rt, RPTC_c)
    rptc = rptc_p + rptc_s
    return (rptc_p, rptc_s, rptc)



@np.vectorize
def ChildDepTaxCredit(n24, MARS, c00100, XTOT, num, c05800,
                      e07260, e07300, c07180, c07230, e07240,
                      c07200, n21, n1820, exact, nu06,
                      CTC_c, CTC_ps, CTC_prt, ODC_c, CR_ForeignTax_hc,
                      CR_ResidentialEnergy_hc, CTC_c_under6_bonus,
                      CTC_refundable, CTC_include17, CR_RetirementSavings_hc):
    """
    Computes amounts on "Child Tax Credit and Credit for Other Dependents
    Worksheet" in 2018 Publication 972, which pertain to these two
    nonrefundable tax credits.

    Parameters
    ----------
    n24: int
        Number of children who are Child-Tax-Credit eligible, one condition for which is being under age 17
    MARS: int
        Filing (marital) status. (1=single, 2=joint, 3=separate, 4=household-head, 5=widow(er))
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
        childnum = n24 + max(0, XTOT - n21 - n1820 - n24 - num)
    else:
        childnum = n24
    line1 = CTC_c * childnum + CTC_c_under6_bonus * nu06
    line2 = ODC_c * max(0, XTOT - childnum - num)
    line3 = line1 + line2
    modAGI = c00100  # no foreign earned income exclusion to add to AGI (line6)
    if line3 > 0. and modAGI > CTC_ps:
        excess = modAGI - CTC_ps
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
        if CTC_refundable:
            c07220 = line10 * line1 / line3
            odc = min(max(0., line10 - c07220), line15)
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



def PersonalTaxCredit(MARS, c00100, XTOT,
                      II_credit, II_credit_ps, II_credit_prt,
                      II_credit_nr, II_credit_nr_ps, II_credit_nr_prt,
                      RRC_c, RRC_ps, RRC_pe):
    """
    Computes personal_refundable_credit and personal_nonrefundable_credit,
    neither of which are part of current-law policy.

    Parameters
    ----------
    MARS: int
        Filing (marital) status. (1=single, 2=joint, 3=separate, 4=household-head, 5=widow(er))
    c00100: float
        Adjusted Gross Income (AGI)
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
    """
    # calculate personal refundable credit amount with phase-out
    personal_refundable_credit = II_credit[MARS - 1]
    cond = np.logical_and(II_credit_prt > 0., c00100 > II_credit_ps[MARS - 1])
    pout = np.where(cond,
                    II_credit_prt * (c00100 - II_credit_ps[MARS - 1]), 0.)
    fully_phasedout = np.where(cond, personal_refundable_credit - pout, 0.)
    personal_refundable_credit = np.where(cond, np.maximum(0., fully_phasedout), personal_refundable_credit)
    # calculate personal nonrefundable credit amount with phase-out
    personal_nonrefundable_credit = II_credit_nr[MARS - 1]
    cond = np.logical_and(II_credit_nr_prt > 0., c00100 > II_credit_nr_ps[MARS - 1])
    pout = np.where(cond,
                    II_credit_nr_prt * (c00100 - II_credit_nr_ps[MARS - 1]), 0.)
    fully_phasedout = np.where(cond, personal_nonrefundable_credit - pout, 0.)
    personal_nonrefundable_credit = np.where(cond, np.maximum(0., fully_phasedout), personal_nonrefundable_credit)
    # calculate Recovery Rebate Credit from ARPA 2021
    prt = np.where(c00100 < RRC_pe[MARS - 1],
                  ((c00100 - RRC_ps[MARS - 1]) /
                     (RRC_pe[MARS - 1] - RRC_ps[MARS - 1])),
                  0.)

    condlist = [c00100 < RRC_ps[MARS - 1], c00100 < RRC_pe[MARS - 1],
                  np.logical_and(c00100 >= RRC_ps[MARS - 1], c00100 >= RRC_pe[MARS - 1])]
    choicelist = [RRC_c * XTOT, RRC_c * XTOT * (1 - prt), 0.]
    recovery_rebate_credit = np.select(condlist, choicelist)

    return (personal_refundable_credit, personal_nonrefundable_credit,
            recovery_rebate_credit)


def AmOppCreditParts(exact, e87521, num, c00100, CR_AmOppRefundable_hc,
                     CR_AmOppNonRefundable_hc):
    """
    Applies a phaseout to the Form 8863, line 1, American Opportunity Credit
    amount, e87521, and then applies the 0.4 refundable rate.
    Logic corresponds to Form 8863, Part I.

    Parameters
    ----------
    exact: int
        Whether or not to do rounding of phaseout fraction
    e87521: float
        Total tentative AmOppCredit amount for all students.  From Form 8863, line 1.
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
    # Ignore bad division

    c87658 = np.where(e87521 > 0., np.maximum(0., 90000. * num - c00100), 0.)
    c87660 = np.where(e87521 > 0., 10000. * num, 0.)

    divide_quantity = np.divide(c87658, c87660, out=np.zeros_like(c87658), where=c87660!=0)
    condlist = [np.logical_and(e87521 > 0., exact == 1), np.logical_and(e87521 > 0., exact != 1)]
    choicelist = [1000. * np.minimum(1., np.around(divide_quantity, 3)),
                  1000. * np.minimum(1., divide_quantity)]
    c87662 = np.select(condlist, choicelist)

    c87664 = np.where(e87521 > 0., c87662 * e87521 / 1000., 0.)
    c10960 = np.where(e87521 > 0., 0.4 * c87664 * (1. - CR_AmOppRefundable_hc), 0.)
    c87668 = np.where(e87521 > 0., c87664 - c10960 * (1. - CR_AmOppNonRefundable_hc), 0.)

    return (c10960, c87668)



@np.vectorize
def SchR(age_head, age_spouse, MARS, c00100,
         c05800, e07300, c07180, e02400, c02500,
         e01500, e01700, CR_SchR_hc):
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
        Filing (marital) status. (1=single, 2=joint, 3=separate, 4=household-head, 5=widow(er))
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



def EducationTaxCredit(exact, e87530, MARS, c00100, num, c05800,
                       e07300, c07180, c07200, c87668,
                       LLC_Expense_c, ETC_pe_Single, ETC_pe_Married,
                       CR_Education_hc):
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
        Filing (marital) status. (1=single, 2=joint, 3=separate, 4=household-head, 5=widow(er))
    c00100: float
        Adjusted Gross Income (AGI)
    num: int
        2 when MARS is 2 (married filing jointly), otherwise 1
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
    """
    c87560 = 0.2 * np.minimum(e87530, LLC_Expense_c)
    c87570 = np.where(MARS == 2, ETC_pe_Married * 1000., ETC_pe_Single * 1000.)
    c87590 = np.maximum(0., c87570 - c00100)
    c87600 = 10000. * num
    c87610 = np.where(exact == 1, np.minimum(1., np.around(c87590 / c87600, 3)), np.minimum(1., c87590 / c87600))
    c87620 = c87560 * c87610
    xline4 = np.maximum(0., c05800 - (e07300 + c07180 + c07200))
    xline5 = np.minimum(c87620, xline4)
    xline9 = np.maximum(0., c05800 - (e07300 + c07180 + c07200 + xline5))
    xline10 = np.minimum(c87668, xline9)
    c87680 = xline5 + xline10
    c07230 = c87680 * (1. - CR_Education_hc)
    return c07230


def CharityCredit(e19800, e20100, c00100, MARS,
                  CR_Charity_rt, CR_Charity_f,
                  CR_Charity_frt):
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
        Filing (marital) status. (1=single, 2=joint, 3=separate, 4=household-head, 5=widow(er))
    charity_credit: float
        Credit for charitable giving

    Returns
    -------
    charity_credit: float
        Credit for charitable giving
    """
    total_charity = e19800 + e20100
    floor = np.maximum(CR_Charity_frt * c00100, CR_Charity_f[MARS - 1])
    charity_cr_floored = np.maximum(total_charity - floor, 0)
    charity_credit = CR_Charity_rt * (charity_cr_floored)
    return charity_credit



def NonrefundableCredits(c07300, c07180, c07230, c07240, c07220,
                         c07260, c07400, c07600, c07200, c08000,
                         c05800, e07240, e07260, e07300, e07400,
                         e07600, p08000, odc,
                         personal_nonrefundable_credit, charity_credit,
                         CTC_refundable,
                         CR_RetirementSavings_hc, CR_ForeignTax_hc,
                         CR_ResidentialEnergy_hc, CR_GeneralBusiness_hc,
                         CR_MinimumTax_hc, CR_OtherCredits_hc):
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
    CTC_refundable: bool
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
    c07300 = np.minimum(e07300 * (1. - CR_ForeignTax_hc), avail)
    avail = avail - c07300
    # Child & dependent care expense credit
    c07180 = np.minimum(c07180, avail)
    avail = avail - c07180
    # Education tax credit
    c07230 = np.minimum(c07230, avail)
    avail = avail - c07230
    # Retirement savings credit - Form 8880
    c07240 = np.minimum(e07240 * (1. - CR_RetirementSavings_hc), avail)
    avail = avail - c07240
    # Child tax credit
    if not CTC_refundable:
        c07220 = np.minimum(c07220, avail)
        avail = avail - c07220
    # Other dependent credit
    odc = np.minimum(odc, avail)
    avail = avail - odc
    # Residential energy credit - Form 5695
    c07260 = np.minimum(e07260 * (1. - CR_ResidentialEnergy_hc), avail)
    avail = avail - c07260
    # General business credit - Form 3800
    c07400 = np.minimum(e07400 * (1. - CR_GeneralBusiness_hc), avail)
    avail = avail - c07400
    # Prior year minimum tax credit - Form 8801
    c07600 = np.minimum(e07600 * (1. - CR_MinimumTax_hc), avail)
    avail = avail - c07600
    # Schedule R credit
    c07200 = np.minimum(c07200, avail)
    avail = avail - c07200
    # Other credits
    c08000 = np.minimum(p08000 * (1. - CR_OtherCredits_hc), avail)
    avail = avail - c08000
    charity_credit = np.minimum(charity_credit, avail)
    avail = avail - charity_credit
    # Personal nonrefundable credit
    personal_nonrefundable_credit = np.minimum(personal_nonrefundable_credit, avail)
    avail = avail - personal_nonrefundable_credit
    return (c07180, c07200, c07220, c07230, c07240, odc,
            c07260, c07300, c07400, c07600, c08000, charity_credit,
            personal_nonrefundable_credit)



@np.vectorize
def AdditionalCTC(codtc_limited, nu06, n24, earned, XTOT, n21, n1820, num,
                  ptax_was, c03260, e09800, c59660, e11200, ACTC_c, ACTC_Income_thd,
                  ACTC_rt, ACTC_rt_bonus_under6family, ACTC_ChildNum,
                  CTC_refundable, CTC_include17):
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
        Number of children who are Child-Tax-Credit eligible, one condition for which is being under age 17
    earned: float
        Earned income for filing unit
    ACTC_Income_thd: float
        Additional Child Tax Credit income threshold
    ACTC_rt: float
        Additional Child Tax Credit rate
    nu06: int
        Number of dependents under 6 years old
    ACTC_rt_bonus_under6family: float
        Bonus additional child tax credit rate for families with qualifying children under 6
    ACTC_ChildNum: float
        Additional Child Tax Credit minimum number of qualified children for different formula
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

    if CTC_refundable:
        line4 = 0.
    else:
        if CTC_include17:
            childnum = n24 + max(0, XTOT - n21 - n1820 - n24 - num)
        else:
            childnum = n24
        line4 = ACTC_c * childnum
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



def C1040(c05800, c07180, c07200, c07220, c07230, c07240, c07260, c07300,
          c07400, c07600, c08000, e09700, e09800, e09900, niit, othertaxes,
          c07100, c09200, odc, charity_credit,
          personal_nonrefundable_credit, CTC_refundable):
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
    othertaxes: float
        Sum of niit, e09700, e09800, and e09900
    c07100: float
        Total non-refundable credits used to reduce positive tax liability
    c09200: float
        Income tax liabilities (including othertaxes) after non-refundable credits are used, but before refundable credits are applied
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
        Income tax liabilities (including othertaxes) after non-refundable credits are used, but before refundable credits are applied
    """
    # total used nonrefundable credits (as computed in NonrefundableCredits)
    c07100 = (c07180 + c07200 + c07600 + c07300 + c07400 +
              c07220 * (1. - CTC_refundable) + c08000 +
              c07230 + c07240 + c07260 + odc + charity_credit +
              personal_nonrefundable_credit)
    # tax after credits (2016 Form 1040, line 56)
    tax_net_nonrefundable_credits = np.maximum(0., c05800 - c07100)
    # tax (including othertaxes) before refundable credits
    othertaxes = e09700 + e09800 + e09900 + niit
    c09200 = othertaxes + tax_net_nonrefundable_credits
    return (c07100, othertaxes, c09200)



@np.vectorize
def CTC_new(payrolltax, n24, nu06, XTOT, n21, n1820, num, c00100, MARS, ptax_oasdi,
            c09200, CTC_new_c, CTC_new_rt, CTC_new_c_under6_bonus,
            CTC_new_ps, CTC_new_prt, CTC_new_for_all, CTC_include17,
            CTC_new_refund_limited, CTC_new_refund_limit_payroll_rt,
            CTC_new_refund_limited_all_payroll):
    """
    Computes new refundable child tax credit using specified parameters.

    Parameters
    ----------
    CTC_new_c: float
        New refundable child tax credit maximum amount per child
    CTC_new_rt: float
        New refundalbe child tax credit amount phasein rate
    CTC_new_c_under6_bonus: float
        Bonus new refundable child tax credit maximum for qualifying children under six
    CTC_new_ps: list
        New refundable child tax credit phaseout starting AGI
    CTC_new_prt: float
        New refundable child tax credit amount phaseout rate
    CTC_new_for_all: bool
        Whether or not maximum amount of the new refundable child tax credit is available to all
    CTC_new_refund_limited: bool
        New child tax credit refund limited to a decimal fraction of payroll taxes
    CTC_new_refund_limit_payroll_rt: float
        New child tax credit refund limit rate (decimal fraction of payroll taxes)
    CTC_new_refund_limited_all_payroll: bool
        New child tax credit refund limit applies to all FICA taxes, not just OASDI
    payrolltax: float
        Total (employee + employer) payroll tax liability
    n24: int
        Number of children who are Child-Tax-Credit eligible, one condition for which is being under age 17
    nu06: int
        Number of dependents under 6 years old
    c00100: float
        Adjusted Gross Income (AGI)
    MARS: int
        Filing (marital) status. (1=single, 2=joint, 3=separate, 4=household-head, 5=widow(er))
    ptax_oasdi: float
        Employee and employer OASDI FICA tax plus self employment tax
        Excludes HI FICA so positive ptax_oasdi is less than ptax_was + setax
    c09200: float
        Income tax liabilities (including othertaxes) after non-refundable credits are used, but before refundable credits are applied
    ctc_new: float
        New refundable child tax credit

    Returns
    -------
    ctc_new: float
        New refundable child tax credit
    """
    if CTC_include17:
        childnum = n24 + max(0., XTOT - n21 - n1820 - n24 - num)
    else:
        childnum = n24
    if childnum > 0:
        posagi = max(c00100, 0.)
        ctc_new = CTC_new_c * childnum + CTC_new_c_under6_bonus * nu06
        if not CTC_new_for_all:
            ctc_new = min(CTC_new_rt * posagi, ctc_new)
        ymax = CTC_new_ps
        if posagi > ymax:
            ctc_new_reduced = max(0.,
                                  ctc_new - CTC_new_prt * (posagi - ymax))
            ctc_new = min(ctc_new, ctc_new_reduced)
        if ctc_new > 0. and CTC_new_refund_limited:
            refund_new = max(0., ctc_new - c09200)
            if not CTC_new_refund_limited_all_payroll:
                limit_new = CTC_new_refund_limit_payroll_rt * ptax_oasdi
            if CTC_new_refund_limited_all_payroll:
                limit_new = CTC_new_refund_limit_payroll_rt * payrolltax
            limited_new = max(0., refund_new - limit_new)
            ctc_new = max(0., ctc_new - limited_new)
    else:
        ctc_new = 0.
    return ctc_new



def IITAX(c59660, c11070, c10960, personal_refundable_credit, ctc_new, rptc,
          c09200, payrolltax, recovery_rebate_credit, eitc, c07220,
          refund, iitax, combined, CDCC_refund, CTC_refundable):
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
        Income tax liabilities (including othertaxes) after non-refundable credits are used, but before refundable credits are applied
    payrolltax: float
        Total (employee + employer) payroll tax liability
    eitc: float
        Earned Income Credit
    refund: float
        Total refundable income tax credits
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
    iitax: float
        Total federal individual income tax liability
    combined: float
        Sum of iitax and payrolltax and lumpsum_tax
    """
    eitc = c59660
    if CTC_refundable:
        ctc_refund = c07220
    else:
        ctc_refund = 0.
    refund = (eitc + c11070 + c10960 + CDCC_refund + recovery_rebate_credit +
              personal_refundable_credit + ctc_new + rptc + ctc_refund)
    iitax = c09200 - refund
    combined = iitax + payrolltax
    return (eitc, refund, iitax, combined)

def Taxes(income, MARS, tbrk_base,
          rate1, rate2, rate3, rate4, rate5, rate6, rate7, rate8,
          tbrk1, tbrk2, tbrk3, tbrk4, tbrk5, tbrk6, tbrk7):
    """
    Taxes function returns tax amount given the progressive tax rate
    schedule specified by the rate* and (upper) tbrk* parameters and
    given income, filing status (MARS), and tax bracket base (tbrk_base).

    Parameters
    ----------
    income: float
        Taxable income
    MARS: int
        Filing (marital) status. (1=single, 2=joint, 3=separate, 4=household-head, 5=widow(er))
    tbrk_base: float
        Amount of income used to determine the braket the filer is in
    rate1: list
        Income tax rate 1
    rate2: list
        Income tax rate 2
    rate3: list
        Income tax rate 3
    rate4: list
        Income tax rate 4
    rate5: list
        Income tax rate 5
    rate6: list
        Income tax rate 6
    rate7: list
        Income tax rate 7
    rate8: list
        Income tax rate 8
    tbrk1: list
        Income tax bracket (upper threshold) 1
    tbrk2: list
        Income tax bracket (upper threshold) 2
    tbrk3: list
        Income tax bracket (upper threshold) 3
    tbrk4: list
        Income tax bracket (upper threshold) 4
    tbrk5: list
        Income tax bracket (upper threshold) 5
    tbrk6: list
        Income tax bracket (upper threshold) 6
    tbrk7: list
        Income tax bracket (upper threshold) 7

    Returns
    -------
    None
    """
    brk1 = np.where(tbrk_base > 0., np.maximum(tbrk1[MARS - 1] - tbrk_base, 0.), tbrk1[MARS - 1])
    brk2 = np.where(tbrk_base > 0., np.maximum(tbrk2[MARS - 1] - tbrk_base, 0.), tbrk2[MARS - 1])
    brk3 = np.where(tbrk_base > 0., np.maximum(tbrk3[MARS - 1] - tbrk_base, 0.), tbrk3[MARS - 1])
    brk4 = np.where(tbrk_base > 0., np.maximum(tbrk4[MARS - 1] - tbrk_base, 0.), tbrk4[MARS - 1])
    brk5 = np.where(tbrk_base > 0., np.maximum(tbrk5[MARS - 1] - tbrk_base, 0.), tbrk5[MARS - 1])
    brk6 = np.where(tbrk_base > 0., np.maximum(tbrk6[MARS - 1] - tbrk_base, 0.), tbrk6[MARS - 1])
    brk7 = np.where(tbrk_base > 0., np.maximum(tbrk7[MARS - 1] - tbrk_base, 0.), tbrk7[MARS - 1])
    
    return (rate1 * np.minimum(income, brk1) +
            rate2 * np.minimum(brk2 - brk1, np.maximum(0., income - brk1)) +
            rate3 * np.minimum(brk3 - brk2, np.maximum(0., income - brk2)) +
            rate4 * np.minimum(brk4 - brk3, np.maximum(0., income - brk3)) +
            rate5 * np.minimum(brk5 - brk4, np.maximum(0., income - brk4)) +
            rate6 * np.minimum(brk6 - brk5, np.maximum(0., income - brk5)) +
            rate7 * np.minimum(brk7 - brk6, np.maximum(0., income - brk6)) +
            rate8 * np.maximum(0., income - brk7))


def ComputeBenefit(calc, ID_switch):
    """
    Calculates the value of the benefits accrued from itemizing.

    Parameters
    ----------
    calc: Calculator object
        calc represents the reform while self represents the baseline
    ID_switch: list
        Deductions subject to the surtax on itemized deduction benefits

    Returns
    -------
    benefit: float
        Imputed benefits from itemizing deductions
    """
    # compute income tax liability with no itemized deductions allowed for
    # the types of itemized deductions covered under the BenefitSurtax
    no_ID_calc = copy.deepcopy(calc)
    if ID_switch[0]:
        no_ID_calc.policy_param('ID_Medical_hc', [1.])
    if ID_switch[1]:
        no_ID_calc.policy_param('ID_StateLocalTax_hc', [1.])
    if ID_switch[2]:
        no_ID_calc.policy_param('ID_RealEstate_hc', [1.])
    if ID_switch[3]:
        no_ID_calc.policy_param('ID_Casualty_hc', [1.])
    if ID_switch[4]:
        no_ID_calc.policy_param('ID_Miscellaneous_hc', [1.])
    if ID_switch[5]:
        no_ID_calc.policy_param('ID_InterestPaid_hc', [1.])
    if ID_switch[6]:
        no_ID_calc.policy_param('ID_Charity_hc', [1.])
    no_ID_calc._calc_one_year()  # pylint: disable=protected-access
    diff_iitax = no_ID_calc.array('iitax') - calc.array('iitax')
    benefit = np.where(diff_iitax > 0., diff_iitax, 0.)
    return benefit


def BenefitSurtax(calc):
    """
    Computes itemized-deduction-benefit surtax and adds the surtax amount
    to income tax, combined tax, and surtax liabilities.

    Parameters
    ----------
    calc: Calculator object
        calc represents the reform while self represents the baseline

    Returns
    -------
    None:
        The function modifies calc
    """
    if calc.policy_param('ID_BenefitSurtax_crt') != 1.:
        ben = ComputeBenefit(calc,
                             calc.policy_param('ID_BenefitSurtax_Switch'))
        agi = calc.array('c00100')
        ben_deduct = calc.policy_param('ID_BenefitSurtax_crt') * agi
        ben_exempt_array = calc.policy_param('ID_BenefitSurtax_em')
        ben_exempt = ben_exempt_array[calc.array('MARS') - 1]
        ben_dedem = ben_deduct + ben_exempt
        ben_surtax = (calc.policy_param('ID_BenefitSurtax_trt') *
                      np.where(ben > ben_dedem, ben - ben_dedem, 0.))
        # add ben_surtax to income & combined taxes and to surtax subtotal
        calc.incarray('iitax', ben_surtax)
        calc.incarray('combined', ben_surtax)
        calc.incarray('surtax', ben_surtax)


def BenefitLimitation(calc):
    """
    Limits the benefits of select itemized deductions to a fraction of
    deductible expenses.

    Parameters
    ----------
    calc: Calculator object
        calc represents the reform while self represents the baseline

    Returns
    -------
    None:
        The function modifies calc
    """
    if calc.policy_param('ID_BenefitCap_rt') != 1.:
        benefit = ComputeBenefit(calc,
                                 calc.policy_param('ID_BenefitCap_Switch'))
        # Calculate total deductible expenses under the cap
        deduct_exps = 0.
        if calc.policy_param('ID_BenefitCap_Switch')[0]:  # medical
            deduct_exps += calc.array('c17000')
        if calc.policy_param('ID_BenefitCap_Switch')[1]:  # statelocal
            one_minus_hc = 1. - calc.policy_param('ID_StateLocalTax_hc')
            deduct_exps += (one_minus_hc *
                            np.maximum(calc.array('e18400_capped'), 0.))
        if calc.policy_param('ID_BenefitCap_Switch')[2]:  # realestate
            one_minus_hc = 1. - calc.policy_param('ID_RealEstate_hc')
            deduct_exps += one_minus_hc * calc.array('e18500_capped')
        if calc.policy_param('ID_BenefitCap_Switch')[3]:  # casualty
            deduct_exps += calc.array('c20500')
        if calc.policy_param('ID_BenefitCap_Switch')[4]:  # misc
            deduct_exps += calc.array('c20800')
        if calc.policy_param('ID_BenefitCap_Switch')[5]:  # interest
            deduct_exps += calc.array('c19200')
        if calc.policy_param('ID_BenefitCap_Switch')[6]:  # charity
            deduct_exps += calc.array('c19700')
        # Calculate cap value for itemized deductions
        benefit_limit = deduct_exps * calc.policy_param('ID_BenefitCap_rt')
        # Add the difference between the actual benefit and capped benefit
        # to income tax and combined tax liabilities.
        excess_benefit = np.maximum(benefit - benefit_limit, 0)
        calc.incarray('iitax', excess_benefit)
        calc.incarray('surtax', excess_benefit)
        calc.incarray('combined', excess_benefit)


@np.vectorize
def FairShareTax(c00100, MARS, ptax_was, setax, ptax_amc, iitax, combined, surtax,
                 FST_AGI_trt, FST_AGI_thd_lo, FST_AGI_thd_hi):
    """
    Computes Fair Share Tax, or "Buffet Rule", types of reforms.

    Parameters
    ----------
    c00100: float
        Adjusted Gross Income (AGI)
    MARS: int
        Filing (marital) status. (1=single, 2=joint, 3=separate, 4=household-head, 5=widow(er))
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
    
    if FST_AGI_trt > 0. and c00100 >= FST_AGI_thd_lo:
        employee_share = 0.5 * ptax_was + 0.5 * setax + ptax_amc
        fstax = max(c00100 * FST_AGI_trt - iitax - employee_share, 0.)
        thd_gap = max(FST_AGI_thd_hi - FST_AGI_thd_lo, 0.)
        if thd_gap > 0. and c00100 < FST_AGI_thd_hi:
            fstax *= (c00100 - FST_AGI_thd_lo) / thd_gap
        iitax += fstax
        combined += fstax
        surtax += fstax
    else:
        fstax = 0.
    return (fstax, iitax, combined, surtax)



def LumpSumTax(DSI, num, XTOT, combined,
               LST):
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
    lumpsum_tax = np.where(np.logical_or(LST == 0.0, DSI == 1), 0., LST * np.maximum(num, XTOT))
    combined += lumpsum_tax

    return (lumpsum_tax, combined)



def ExpandIncome(e00200, pencon_p, pencon_s, e00300, e00400, e00600,
                 e00700, e00800, e00900, e01100, e01200, e01400, e01500,
                 e02000, e02100, p22250, p23250, cmbtp, ptax_was,
                 benefit_value_total):
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
        Schedule E total rental, royalty, partnership, S-corporation, etc, income/loss
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
        Consumption value of all benefits received by tax unit, which is included in expanded income
    expanded_income: float
        Broad income measure that includes benefit_value_total

    Returns
    -------
    expanded_income: float
        Broad income measure that includes benefit_value_total
    """
    expanded_income = np.sum([
        e00200,  # wage and salary income net of DC pension contributions
        pencon_p,  # tax-advantaged DC pension contributions for taxpayer
        pencon_s,  # tax-advantaged DC pension contributions for spouse
        e00300,  # taxable interest income
        e00400,  # non-taxable interest income
        e00600,  # dividends
        e00700,  # state and local income tax refunds
        e00800,  # alimony received
        e00900,  # Sch C business net income/loss
        e01100,  # capital gain distributions not reported on Sch D
        e01200,  # Form 4797 other net gain/loss
        e01400,  # taxable IRA distributions
        e01500,  # total pension & annuity income (including DB-plan benefits)
        e02000,  # Sch E total rental, ..., partnership, S-corp income/loss
        e02100,  # Sch F farm net income/loss
        p22250,  # Sch D: net short-term capital gain/loss
        p23250,  # Sch D: net long-term capital gain/loss
        cmbtp,  # other AMT taxable income items from Form 6251
        0.5 * ptax_was,  # employer share of FICA taxes on wages/salaries
        benefit_value_total  # consumption value of all benefits received;
        # see the BenefitPrograms function in this file for details on
        # exactly how the benefit_value_total variable is computed
    ], axis=0)
    return expanded_income


def AfterTaxIncome(combined, expanded_income):
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
