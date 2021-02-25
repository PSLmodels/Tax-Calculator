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
from taxcalc.decorators import iterate_jit, JIT


def BenefitPrograms(calc):
    """
    Calculate total government cost and consumption value of benefits
    delivered by non-repealed benefit programs.
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
                  FICA_ss_trt, FICA_mc_trt, ALD_SelfEmploymentTax_hc,
                  SS_Earnings_thd, e00900p, e00900s, e02100p, e02100s, k1bx14p,
                  k1bx14s, payrolltax, ptax_was, setax, c03260, ptax_oasdi,
                  sey, earned, earned_p, earned_s,
                  was_plus_sey_p, was_plus_sey_s):
    """
    Compute part of total OASDI+HI payroll taxes and earned income variables.
    """
    # compute sey and its individual components
    sey_p = e00900p + e02100p + k1bx14p
    sey_s = e00900s + e02100s + k1bx14s
    sey = sey_p + sey_s  # total self-employment income for filing unit

    # compute gross wage and salary income ('was' denotes 'wage and salary')
    gross_was_p = e00200p + pencon_p
    gross_was_s = e00200s + pencon_s

    # compute taxable gross earnings for OASDI FICA
    txearn_was_p = min(SS_Earnings_c, gross_was_p)
    txearn_was_s = min(SS_Earnings_c, gross_was_s)

    # compute OASDI and HI payroll taxes on wage-and-salary income, FICA
    ptax_ss_was_p = FICA_ss_trt * txearn_was_p
    ptax_ss_was_s = FICA_ss_trt * txearn_was_s
    ptax_mc_was_p = FICA_mc_trt * gross_was_p
    ptax_mc_was_s = FICA_mc_trt * gross_was_s
    ptax_was = ptax_ss_was_p + ptax_ss_was_s + ptax_mc_was_p + ptax_mc_was_s

    # compute taxable self-employment income for OASDI SECA
    sey_frac = 1.0 - 0.5 * (FICA_ss_trt + FICA_mc_trt)
    txearn_sey_p = min(max(0., sey_p * sey_frac), SS_Earnings_c - txearn_was_p)
    txearn_sey_s = min(max(0., sey_s * sey_frac), SS_Earnings_c - txearn_was_s)

    # compute self-employment tax on taxable self-employment income, SECA
    setax_ss_p = FICA_ss_trt * txearn_sey_p
    setax_ss_s = FICA_ss_trt * txearn_sey_s
    setax_mc_p = FICA_mc_trt * max(0., sey_p * sey_frac)
    setax_mc_s = FICA_mc_trt * max(0., sey_s * sey_frac)
    setax_p = setax_ss_p + setax_mc_p
    setax_s = setax_ss_s + setax_mc_s
    setax = setax_p + setax_s

    # compute extra OASDI payroll taxes on the portion of the sum
    # of wage-and-salary income and taxable self employment income
    # that exceeds SS_Earnings_thd
    sey_frac = 1.0 - 0.5 * FICA_ss_trt
    was_plus_sey_p = gross_was_p + max(0., sey_p * sey_frac)
    was_plus_sey_s = gross_was_s + max(0., sey_s * sey_frac)
    extra_ss_income_p = max(0., was_plus_sey_p - SS_Earnings_thd)
    extra_ss_income_s = max(0., was_plus_sey_s - SS_Earnings_thd)
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
    nu13: Number of dependents under 13 years old
    elderly_dependents: number of elderly dependents
    earned: Form 2441 earned income amount
    MARS: Marital Status
    ALD_Dependents_thd: Maximum income to qualify for deduction
    ALD_Dependents_hc: Deduction for dependent care haircut
    ALD_Dependents_Child_c: National weighted average cost of childcare
    ALD_Dependents_Elder_c: Eldercare deduction ceiling

    Returns
    -------
    care_deduction: Total above the line deductions for dependent care.
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
        c02900):
    """
    Adj calculates Form 1040 AGI adjustments (i.e., Above-the-Line Deductions).

    Notes
    -----
    Taxpayer characteristics:

        e03210 : Student loan interest paid

        e03220 : Educator expenses

        e03150 : Total deductible IRA plan contributions

        e03230 : Tuition and fees (Form 8917)

        e03240 : Domestic production activity deduction (Form 8903)

        c03260 : Self-employment tax deduction (after haircut)

        e03270 : Self-employed health insurance premiums

        e03290 : HSA deduction (Form 8889)

        e03300 : Total deductible KEOGH/SEP/SIMPLE/etc. plan contributions

        e03400 : Penalty on early withdrawal of savings deduction

        e03500 : Alimony paid

        e00800 : Alimony received

        care_deduction : Dependent care expense deduction

    Tax law parameters:

        ALD_StudentLoan_hc : Student loan interest deduction haircut

        ALD_SelfEmp_HealthIns_hc : Self-employed h.i. deduction haircut

        ALD_KEOGH_SEP_hc : KEOGH/etc. plan contribution deduction haircut

        ALD_EarlyWithdraw_hc : Penalty on early withdrawal deduction haricut

        ALD_AlimonyPaid_hc : Alimony paid deduction haircut

        ALD_AlimonyReceived_hc : Alimony received deduction haircut

        ALD_EducatorExpenses_hc: Eductor expenses haircut

        ALD_HSADeduction_hc: HSA Deduction haircut

        ALD_IRAContributions_hc: IRA Contribution haircut

        ALD_DomesticProduction_hc: Domestic production haircut

        ALD_Tuition_hc: Tuition and fees haircut

    Returns
    -------
    c02900 : total Form 1040 adjustments, which are not included in AGI
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


@iterate_jit(nopython=True)
def ALD_InvInc_ec_base(p22250, p23250, sep,
                       e00300, e00600, e01100, e01200,
                       invinc_ec_base):
    """
    Computes invinc_ec_base.
    """
    # limitation on net short-term and long-term capital losses
    cgain = max((-3000. / sep), p22250 + p23250)
    # compute exclusion of investment income from AGI
    invinc_ec_base = e00300 + e00600 + cgain + e01100 + e01200
    return invinc_ec_base


@iterate_jit(nopython=True)
def CapGains(p23250, p22250, sep, ALD_StudentLoan_hc,
             ALD_InvInc_ec_rt, invinc_ec_base,
             e00200, e00300, e00600, e00650, e00700, e00800,
             CG_nodiff, CG_ec, CG_reinvest_ec_rt,
             ALD_BusinessLosses_c, MARS,
             e00900, e01100, e01200, e01400, e01700, e02000, e02100,
             e02300, e00400, e02400, c02900, e03210, e03230, e03240,
             c01000, c23650, ymod, ymod1, invinc_agi_ec):
    """
    CapGains function: ...
    """
    # net capital gain (long term + short term) before exclusion
    c23650 = p23250 + p22250
    # limitation on capital losses
    c01000 = max((-3000. / sep), c23650)
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
def SSBenefits(MARS, ymod, e02400, SS_thd50, SS_thd85,
               SS_percentage1, SS_percentage2, c02500):
    """
    Calculates OASDI benefits included in AGI, c02500.
    """
    if ymod < SS_thd50[MARS - 1]:
        c02500 = 0.
    elif ymod < SS_thd85[MARS - 1]:
        c02500 = SS_percentage1 * min(ymod - SS_thd50[MARS - 1], e02400)
    else:
        c02500 = min(SS_percentage2 * (ymod - SS_thd85[MARS - 1]) +
                     SS_percentage1 *
                     min(e02400, SS_thd85[MARS - 1] -
                         SS_thd50[MARS - 1]), SS_percentage2 * e02400)
    return c02500


@iterate_jit(nopython=True)
def UBI(nu18, n1820, n21, UBI_u18, UBI_1820, UBI_21, UBI_ecrt,
        ubi, taxable_ubi, nontaxable_ubi):
    """
    Calculates total and taxable Universal Basic Income (UBI) amount.

    Parameters
    ----------
    nu18: Number of people in the tax unit under 18

    n1820: Number of people in the tax unit age 18-20

    n21: Number of people in the tax unit age 21+

    UBI_u18: UBI benefit for those under 18

    UBI_1820: UBI benefit for those between 18 to 20

    UBI_21: UBI benefit for those 21 or more

    UBI_ecrt: Fraction of UBI benefits that are not included in AGI

    Returns
    -------
    ubi: total UBI received by the tax unit (is included in expanded_income)

    taxable_ubi: amount of UBI that is taxable (is added to AGI)

    nontaxable_ubi: amount of UBI that is nontaxable
    """
    ubi = nu18 * UBI_u18 + n1820 * UBI_1820 + n21 * UBI_21
    taxable_ubi = ubi * (1. - UBI_ecrt)
    nontaxable_ubi = ubi - taxable_ubi
    return ubi, taxable_ubi, nontaxable_ubi


@iterate_jit(nopython=True)
def AGI(ymod1, c02500, c02900, XTOT, MARS, sep, DSI, exact, nu18, taxable_ubi,
        II_em, II_em_ps, II_prt, II_no_em_nu18,
        c00100, pre_c04600, c04600):
    """
    Computes Adjusted Gross Income (AGI), c00100, and
    compute personal exemption amount, c04600.

    Parameters
    ----------
    ymod1: float

    c02500: float

    c02900: float

    XTOT: float

    MARS: int
        filing status
    sep: float

    DSI: float

    exact: int
        exact == 1 means do exact calculation, else do smoothed calculation
        which is used for marginal tax rates
    nu18: int
        number of dependents under age 18
    taxable_ubi: float
        taxable UBI amount
    II_em: 

    II_em_ps:

    II_prt:

    II_no_em_nu18,

    c00100: float
        AGI
    pre_c04600: float

    c04600: float
        exemption amount

    Returns
    -------
    tuple
        returns AGI (c00100), (pre_c04600), exemption amount (c04600)
    """
    # calculate AGI assuming no foreign earned income exclusion
    c00100 = ymod1 + c02500 - c02900 + taxable_ubi
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
        line7 = II_prt * line6
        c04600 = max(0., pre_c04600 * (1. - line7))
    else:  # smoothed calculation needed for sensible mtr calculation
        dispc_numer = II_prt * (c00100 - II_em_ps[MARS - 1])
        dispc_denom = 2500. / sep
        dispc = min(1., max(0., dispc_numer / dispc_denom))
        c04600 = pre_c04600 * (1. - dispc)
    return (c00100, pre_c04600, c04600)


@iterate_jit(nopython=True)
def ItemDedCap(e17500, e18400, e18500, e19200, e19800, e20100, e20400, g20500,
               c00100, ID_AmountCap_rt, ID_AmountCap_Switch, e17500_capped,
               e18400_capped, e18500_capped, e19200_capped, e19800_capped,
               e20100_capped, e20400_capped, g20500_capped):
    """
    Applies a cap to gross itemized deductions.

    Notes
    -----
    Tax Law Parameters:
        ID_AmountCap_Switch : Indicator for which itemized deductions are
                              capped
        ID_AmountCap_rt : Cap on itemized deductions; decimal fraction of AGI

    Taxpayer Characteristics:
        e17500 : Medical expenses

        e18400 : State and local taxes

        e18500 : Real-estate taxes

        e19200 : Interest paid

        e19800 : Charity cash contributions

        e20100 : Charity noncash contributions

        e20400 : Total miscellaneous expenses

        g20500 : Gross casualty or theft loss (before disregard)

        c00100: Adjusted Gross Income

    Returns
    -------
        e17500_capped: Medical expenses, capped by ItemDedCap

        e18400_capped: State and local taxes, capped by ItemDedCap

        e18500_capped : Real-estate taxes, capped by ItemDedCap

        e19200_capped : Interest paid, capped by ItemDedCap

        e19800_capped : Charity cash contributions, capped by ItemDedCap

        e20100_capped : Charity noncash contributions, capped by ItemDedCap

        e20400_capped : Total miscellaneous expenses, capped by ItemDedCap

        g20500_capped : Gross casualty or theft loss (before disregard),
                        capped by ItemDedCap
    """
    # pylint: disable=too-many-branches

    cap = max(0., ID_AmountCap_rt * c00100)

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

    overage = max(0., gross_ded_amt - cap)

    e17500_capped = e17500
    e18400_capped = e18400
    e18500_capped = e18500
    g20500_capped = g20500
    e20400_capped = e20400
    e19200_capped = e19200
    e19800_capped = e19800
    e20100_capped = e20100

    if overage > 0. and c00100 > 0.:
        if ID_AmountCap_Switch[0]:  # medical
            e17500_capped -= (e17500 / gross_ded_amt) * overage
        if ID_AmountCap_Switch[1]:  # statelocal
            e18400_capped -= (e18400 / (gross_ded_amt) * overage)
        if ID_AmountCap_Switch[2]:  # realestate
            e18500_capped -= (e18500 / gross_ded_amt) * overage
        if ID_AmountCap_Switch[3]:  # casualty
            g20500_capped -= (g20500 / gross_ded_amt) * overage
        if ID_AmountCap_Switch[4]:  # misc
            e20400_capped -= (e20400 / gross_ded_amt) * overage
        if ID_AmountCap_Switch[5]:  # interest
            e19200_capped -= (e19200 / gross_ded_amt) * overage
        if ID_AmountCap_Switch[6]:  # charity
            e19800_capped -= (e19800 / gross_ded_amt) * overage
            e20100_capped -= (e20100 / gross_ded_amt) * overage

    return (e17500_capped, e18400_capped, e18500_capped, g20500_capped,
            e20400_capped, e19200_capped, e19800_capped, e20100_capped)


@iterate_jit(nopython=True)
def ItemDed(e17500_capped, e18400_capped, e18500_capped, e19200_capped,
            e19800_capped, e20100_capped, e20400_capped, g20500_capped,
            MARS, age_head, age_spouse, c00100, c04470, c21040, c21060,
            c17000, c18300, c19200, c19700, c20500, c20800,
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

    Notes
    -----
    Tax Law Parameters:
        ID_ps : Itemized deduction phaseout AGI start (Pease)

        ID_crt : Itemized deduction maximum phaseout
                 as a decimal fraction of total itemized deduction (Pease)

        ID_prt : Itemized deduction phaseout rate (Pease)

        ID_c: Dollar limit on itemized deductions

        ID_Medical_frt : Deduction for medical expenses;
                         floor as a decimal fraction of AGI

        ID_Medical_frt_add4aged : Addon for medical expenses deduction for
                                  elderly; addon as a decimal fraction of AGI

        ID_Casualty_frt : Deduction for casualty loss;
                          floor as a decimal fraction of AGI

        ID_Miscellaneous_frt : Deduction for miscellaneous expenses;
                               floor as a decimal fraction of AGI

        ID_Charity_crt_all : Deduction for all charitable contributions;
                             ceiling as a decimal fraction of AGI

        ID_Charity_crt_noncash : Deduction for noncash charitable
                                 contributions; ceiling as a decimal
                                 fraction of AGI

        ID_Charity_frt : Disregard for charitable contributions;
                         floor as a decimal fraction of AGI

        ID_Medical_c : Ceiling on medical expense deduction

        ID_StateLocalTax_c : Ceiling on state and local tax deduction

        ID_RealEstate_c : Ceiling on real estate tax deduction

        ID_AllTaxes_c: Ceiling combined state and local income/sales and
                       real estate tax deductions

        ID_InterestPaid_c : Ceiling on interest paid deduction

        ID_Charity_c : Ceiling on charity expense deduction

        ID_Charity_f: Floor on charity expense deduction

        ID_Casualty_c : Ceiling on casuality expense deduction

        ID_Miscellaneous_c : Ceiling on miscellaneous expense deduction

        ID_StateLocalTax_crt : Deduction for state and local taxes;
                               ceiling as a decimal fraction of AGI

        ID_RealEstate_crt : Deduction for real estate taxes;
                            ceiling as a decimal fraction of AGI

    Taxpayer Characteristics:
        e17500_capped : Medical expenses, capped by ItemDedCap

        e18400_capped : State and local taxes, capped by ItemDedCap

        e18500_capped : Real-estate taxes, capped by ItemDedCap

        e19200_capped : Interest paid, capped by ItemDedCap

        e19800_capped : Charity cash contributions, capped by ItemDedCap

        e20100_capped : Charity noncash contributions, capped by ItemDedCap

        e20400_capped : Total miscellaneous expenses, capped by ItemDedCap

        g20500_capped : Gross casualty or theft loss (before disregard),
                        capped by ItemDedCap

    Returns
    -------
    c04470 : total itemized deduction amount (and other intermediate variables)
    """
    posagi = max(c00100, 0.)
    # Medical
    medical_frt = ID_Medical_frt
    if age_head >= 65 or (MARS == 2 and age_spouse >= 65):
        medical_frt += ID_Medical_frt_add4aged
    c17750 = medical_frt * posagi
    c17000 = max(0., e17500_capped - c17750) * (1. - ID_Medical_hc)
    c17000 = min(c17000, ID_Medical_c[MARS - 1])
    # State and local taxes
    c18400 = min((1. - ID_StateLocalTax_hc) * max(e18400_capped, 0.),
                 ID_StateLocalTax_c[MARS - 1])
    c18500 = min((1. - ID_RealEstate_hc) * e18500_capped,
                 ID_RealEstate_c[MARS - 1])
    # following two statements implement a cap on c18400 and c18500 in a way
    # that those with negative AGI, c00100, are not capped under current law,
    # hence the 0.0001 rather than zero
    c18400 = min(c18400, ID_StateLocalTax_crt * max(c00100, 0.0001))
    c18500 = min(c18500, ID_RealEstate_crt * max(c00100, 0.0001))
    c18300 = (c18400 + c18500) * (1. - ID_AllTaxes_hc)
    c18300 = min(c18300, ID_AllTaxes_c[MARS - 1])
    # Interest paid
    c19200 = e19200_capped * (1. - ID_InterestPaid_hc)
    c19200 = min(c19200, ID_InterestPaid_c[MARS - 1])
    # Charity
    lim30 = min(ID_Charity_crt_noncash * posagi, e20100_capped)
    c19700 = min(ID_Charity_crt_all * posagi, lim30 + e19800_capped)
    # charity floor is zero in present law
    charity_floor = max(ID_Charity_frt * posagi, ID_Charity_f[MARS - 1])
    c19700 = max(0., c19700 - charity_floor) * (1. - ID_Charity_hc)
    c19700 = min(c19700, ID_Charity_c[MARS - 1])
    # Casualty
    c20500 = (max(0., g20500_capped - ID_Casualty_frt * posagi) *
              (1. - ID_Casualty_hc))
    c20500 = min(c20500, ID_Casualty_c[MARS - 1])
    # Miscellaneous
    c20400 = e20400_capped
    c20750 = ID_Miscellaneous_frt * posagi
    c20800 = max(0., c20400 - c20750) * (1. - ID_Miscellaneous_hc)
    c20800 = min(c20800, ID_Miscellaneous_c[MARS - 1])
    # Gross total itemized deductions
    c21060 = c17000 + c18300 + c19200 + c19700 + c20500 + c20800
    # Limitations on total itemized deductions
    # (no attempt to adjust c04470 components for limitations)
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
    c04470 = min(c04470, ID_c[MARS - 1])
    # Return total itemized deduction amounts and components
    return (c17000, c18300, c19200, c19700, c20500, c20800,
            c21040, c21060, c04470)


@iterate_jit(nopython=True)
def AdditionalMedicareTax(e00200, MARS,
                          AMEDT_ec, sey, AMEDT_rt,
                          FICA_mc_trt, FICA_ss_trt,
                          ptax_amc, payrolltax):
    """
    Computes Additional Medicare Tax (Form 8959) included in payroll taxes.

    Notes
    -----
    Tax Law Parameters:
        AMEDT_ec : Additional Medicare Tax earnings exclusion

        AMEDT_rt : Additional Medicare Tax rate

        FICA_ss_trt : FICA Social Security tax rate

        FICA_mc_trt : FICA Medicare tax rate

    Taxpayer Charateristics:
        e00200 : Wages and salaries

        sey : Self-employment income

    Returns
    -------
    ptax_amc : Additional Medicare Tax

    payrolltax : payroll tax augmented by Additional Medicare Tax
    """
    line8 = max(0., sey) * (1. - 0.5 * (FICA_mc_trt + FICA_ss_trt))
    line11 = max(0., AMEDT_ec[MARS - 1] - e00200)
    ptax_amc = AMEDT_rt * (max(0., e00200 - AMEDT_ec[MARS - 1]) +
                           max(0., line8 - line11))
    payrolltax += ptax_amc
    return (ptax_amc, payrolltax)


@iterate_jit(nopython=True)
def StdDed(DSI, earned, STD, age_head, age_spouse, STD_Aged, STD_Dep,
           MARS, MIDR, blind_head, blind_spouse, standard, c19700,
           STD_allow_charity_ded_nonitemizers,
           STD_charity_ded_nonitemizers_max):
    """
    Calculates standard deduction, including standard deduction for
    dependents, aged and bind.

    Notes
    -----
    Tax Law Parameters:
        STD : Standard deduction amount, filing status dependent

        STD_Dep : Standard deduction for dependents

        STD_Aged : Additional standard deduction for blind and aged

    Taxpayer Characteristics:
        earned : Form 2441 earned income amount

        e02400 : Gross Social Security Benefit

        DSI : Dependent Status Indicator:
            0 - not being claimed as a dependent
            1 - claimed as a dependent

        MIDR : Married filing separately itemized deductions
        requirement indicator:
            0 - not necessary to itemize because of filing status
            1 - necessary to itemize when filing separately

    Returns
    -------
    standard : the standard deduction amount for filing unit
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
    if STD_allow_charity_ded_nonitemizers:
        standard += min(c19700, STD_charity_ded_nonitemizers_max)
    return standard


@iterate_jit(nopython=True)
def TaxInc(c00100, standard, c04470, c04600, MARS, e00900, e26270,
           e02100, e27200, e00650, c01000, PT_SSTB_income,
           PT_binc_w2_wages, PT_ubia_property, PT_qbid_rt,
           PT_qbid_taxinc_thd, PT_qbid_taxinc_gap, PT_qbid_w2_wages_rt,
           PT_qbid_alt_w2_wages_rt, PT_qbid_alt_property_rt, c04800,
           PT_qbid_ps, PT_qbid_prt, qbided, PT_qbid_limit_switch):
    """
    Calculates taxable income, c04800, and
    qualified business income deduction, qbided.
    """
    # calculate taxable income before qualified business income deduction
    pre_qbid_taxinc = max(0., c00100 - max(c04470, standard) - c04600)
    # calculate qualified business income deduction
    qbided = 0.
    qbinc = max(0., e00900 + e26270 + e02100 + e27200)
    if qbinc > 0. and PT_qbid_rt > 0.:
        qbid_before_limits = qbinc * PT_qbid_rt
        lower_thd = PT_qbid_taxinc_thd[MARS - 1]
        if pre_qbid_taxinc <= lower_thd:
            qbided = qbid_before_limits
        else:
            pre_qbid_taxinc_gap = PT_qbid_taxinc_gap[MARS - 1]
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
        if qbided > 0. and pre_qbid_taxinc > PT_qbid_ps[MARS - 1]:
            excess = pre_qbid_taxinc - PT_qbid_ps[MARS - 1]
            qbided = max(0., qbided - PT_qbid_prt * excess)

    # calculate taxable income after qualified business income deduction
    c04800 = max(0., pre_qbid_taxinc - qbided)
    return (c04800, qbided)


@JIT(nopython=True)
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
    """
    # separate non-negative taxable income into two non-negative components,
    # doing this in a way so that the components add up to taxable income
    # define pass-through income eligible for PT schedule
    pt_passive = PT_EligibleRate_passive * (e02000 - e26270)
    pt_active_gross = e00900 + e26270
    if (pt_active_gross > 0) and PT_wages_active_income:
        pt_active_gross = pt_active_gross + e00200
    pt_active = PT_EligibleRate_active * pt_active_gross
    pt_active = min(pt_active, e00900 + e26270)
    pt_taxinc = max(0., pt_passive + pt_active)
    if pt_taxinc >= taxable_income:
        pt_taxinc = taxable_income
        reg_taxinc = 0.
    else:
        # pt_taxinc is unchanged
        reg_taxinc = taxable_income - pt_taxinc
    # determine stacking order
    if PT_top_stacking:
        reg_tbase = 0.
        pt_tbase = reg_taxinc
    else:
        reg_tbase = pt_taxinc
        pt_tbase = 0.
    # compute Schedule X,Y,Z tax using the two components of taxable income
    if reg_taxinc > 0.:
        reg_tax = Taxes(reg_taxinc, MARS, reg_tbase,
                        II_rt1, II_rt2, II_rt3, II_rt4,
                        II_rt5, II_rt6, II_rt7, II_rt8, II_brk1, II_brk2,
                        II_brk3, II_brk4, II_brk5, II_brk6, II_brk7)
    else:
        reg_tax = 0.
    if pt_taxinc > 0.:
        pt_tax = Taxes(pt_taxinc, MARS, pt_tbase,
                       PT_rt1, PT_rt2, PT_rt3, PT_rt4,
                       PT_rt5, PT_rt6, PT_rt7, PT_rt8, PT_brk1, PT_brk2,
                       PT_brk3, PT_brk4, PT_brk5, PT_brk6, PT_brk7)
    else:
        pt_tax = 0.
    return reg_tax + pt_tax


@iterate_jit(nopython=True)
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
              PT_top_stacking, c05200):
    """
    SchXYZTax calls SchXYZ function and sets c05200 to returned amount.
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


@iterate_jit(nopython=True)
def GainsTax(e00650, c01000, c23650, p23250, e01100, e58990, e00200,
             e24515, e24518, MARS, c04800, c05200, e00900, e26270, e02000,
             II_rt1, II_rt2, II_rt3, II_rt4, II_rt5, II_rt6, II_rt7, II_rt8,
             II_brk1, II_brk2, II_brk3, II_brk4, II_brk5, II_brk6, II_brk7,
             PT_rt1, PT_rt2, PT_rt3, PT_rt4, PT_rt5, PT_rt6, PT_rt7, PT_rt8,
             PT_brk1, PT_brk2, PT_brk3, PT_brk4, PT_brk5, PT_brk6, PT_brk7,
             CG_nodiff, PT_EligibleRate_active, PT_EligibleRate_passive,
             PT_wages_active_income, PT_top_stacking,
             CG_rt1, CG_rt2, CG_rt3, CG_rt4, CG_brk1, CG_brk2, CG_brk3,
             dwks10, dwks13, dwks14, dwks19, c05700, taxbc):
    """
    GainsTax function implements (2015) Schedule D Tax Worksheet logic for
    the special taxation of long-term capital gains and qualified dividends
    if CG_nodiff is false.
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
        dwks42 = SchXYZ(dwks19, MARS, e00900, e26270, e02000, e00200,
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

    # final calculations done no matter what the value of hasqdivltcg
    c05100 = c24580  # because foreign earned income exclusion is assumed zero
    c05700 = 0.  # no Form 4972, Lump Sum Distributions
    taxbc = c05700 + c05100
    return (dwks10, dwks13, dwks14, dwks19, c05700, taxbc)


@iterate_jit(nopython=True)
def AGIsurtax(c00100, MARS, AGI_surtax_trt, AGI_surtax_thd, taxbc, surtax):
    """
    Computes surtax on AGI above some threshold.
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
        earned, cmbtp,
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
    """
    # pylint: disable=too-many-statements,too-many-branches
    # Form 6251, Part I
    if standard == 0.0:
        c62100 = (c00100 - e00700 - c04470 +
                  max(0., min(c17000, 0.025 * c00100)) +
                  c18300 + c20800 - c21040)
    if standard > 0.0:
        c62100 = c00100 - e00700
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
    """
    modAGI = c00100  # no foreign earned income exclusion to add
    if not NIIT_PT_taxed:
        NII = max(0., e00300 + e00600 + c01000 + e02000 - e26270)
    else:  # do not subtract e26270 from e02000
        NII = max(0., e00300 + e00600 + c01000 + e02000)
    niit = NIIT_rt * min(NII, max(0., modAGI - NIIT_thd[MARS - 1]))
    return niit


@iterate_jit(nopython=True)
def F2441(MARS, earned_p, earned_s, f2441, CDCC_c, e32800,
          exact, c00100, CDCC_ps, CDCC_crt, c05800, e07300, c07180):
    """
    Calculates Form 2441 child and dependent care expense credit, c07180.
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
        tratio = math.ceil(max(((c00100 - CDCC_ps) / 2000.), 0.))
        c33200 = c33000 * 0.01 * max(20., CDCC_crt - min(15., tratio))
    else:
        c33200 = c33000 * 0.01 * max(20., CDCC_crt -
                                     max(((c00100 - CDCC_ps) / 2000.), 0.))
    # credit is limited by tax liability
    c07180 = min(max(0., c05800 - e07300), c33200)
    return c07180


@JIT(nopython=True)
def EITCamount(basic_frac, phasein_rate, earnings, max_amount,
               phaseout_start, agi, phaseout_rate):
    """
    Returns EITC amount given specified parameters.
    English parameter names are used in this function because the
    EITC formula is not available on IRS forms or in IRS instructions;
    the extensive IRS EITC look-up table does not reveal the formula.
    """
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
         EITC_indiv, EITC_sep_filers_elig,
         c59660):
    """
    Computes EITC amount, c59660.
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
    """
    rptc_p = min(was_plus_sey_p * RPTC_rt, RPTC_c)
    rptc_s = min(was_plus_sey_s * RPTC_rt, RPTC_c)
    rptc = rptc_p + rptc_s
    return (rptc_p, rptc_s, rptc)


@iterate_jit(nopython=True)
def ChildDepTaxCredit(n24, MARS, c00100, XTOT, num, c05800,
                      e07260, CR_ResidentialEnergy_hc,
                      e07300, CR_ForeignTax_hc,
                      c07180,
                      c07230,
                      e07240, CR_RetirementSavings_hc,
                      c07200,
                      CTC_c, CTC_ps, CTC_prt, exact, ODC_c,
                      CTC_c_under6_bonus, nu06,
                      c07220, odc, codtc_limited):
    """
    Computes amounts on "Child Tax Credit and Credit for Other Dependents
    Worksheet" in 2018 Publication 972, which pertain to these two
    nonrefundable tax credits.
    """
    # Worksheet Part 1
    line1 = CTC_c * n24 + CTC_c_under6_bonus * nu06
    line2 = ODC_c * max(0, XTOT - n24 - num)
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
        line16 = min(line10, line15)  # credit is capped by tax liability
    else:
        line16 = 0.
    # separate the CTC and ODTC amounts
    c07220 = 0.  # nonrefundable CTC amount
    odc = 0.  # nonrefundable ODTC amount
    if line16 > 0.:
        if line1 > 0.:
            c07220 = line16 * line1 / line3
        odc = max(0., line16 - c07220)
    # compute codtc_limited for use in AdditionalCTC function
    codtc_limited = max(0., line10 - line16)
    return (c07220, odc, codtc_limited)


@iterate_jit(nopython=True)
def PersonalTaxCredit(MARS, c00100,
                      II_credit, II_credit_ps, II_credit_prt,
                      II_credit_nr, II_credit_nr_ps, II_credit_nr_prt,
                      personal_refundable_credit,
                      personal_nonrefundable_credit):
    """
    Computes personal_refundable_credit and personal_nonrefundable_credit,
    neither of which are part of current-law policy.
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
    return (personal_refundable_credit, personal_nonrefundable_credit)


@iterate_jit(nopython=True)
def AmOppCreditParts(exact, e87521, num, c00100, CR_AmOppRefundable_hc,
                     CR_AmOppNonRefundable_hc, c10960, c87668):
    """
    Applies a phaseout to the Form 8863, line 1, American Opportunity Credit
    amount, e87521, and then applies the 0.4 refundable rate.
    Logic corresponds to Form 8863, Part I.

    Notes
    -----
    Tax Law Parameters that are not parameterized:

        90000 : American Opportunity Credit phaseout income base

        10000 : American Opportunity Credit phaseout income range length

        1/1000 : American Opportunity Credit phaseout rate

        0.4 : American Opportunity Credit refundable rate

    Parameters
    ----------
        exact : whether or not to do rounding of phaseout fraction

        e87521 : total tentative American Opportunity Credit for all students,
                 Form 8863, line 1

        num : number of people filing jointly

        c00100 : AGI

        CR_AmOppRefundable_hc: haircut for the refundable portion of the
                               American Opportunity Credit

        CR_AmOppNonRefundable_hc: haircut for the nonrefundable portion of the
                                  American Opportunity Credit

    Returns
    -------
        c10960 : Refundable part of American Opportunity Credit

        c87668 : Tentative nonrefundable part of American Opportunity Credit
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
def EducationTaxCredit(exact, e87530, MARS, c00100, num, c05800,
                       e07300, c07180, c07200, c87668,
                       LLC_Expense_c, ETC_pe_Single, ETC_pe_Married,
                       CR_Education_hc,
                       c07230):
    """
    Computes Education Tax Credits (Form 8863) nonrefundable amount, c07230.
    Logic corresponds to Form 8863, Part II.

    Notes
    -----
    Tax Law Parameters that are not parameterized:

        0.2 : Lifetime Learning Credit ratio against expense

    Tax Law Parameters that are parameterized:

        LLC_Expense_c : Lifetime Learning Credit expense limit

        ETC_pe_Married : Education Tax Credit phaseout end for married

        ETC_pe_Single : Education Tax Credit phaseout end for single

    Taxpayer Charateristics:

        exact : whether or not to do rounding of phaseout fraction

        e87530 : Lifetime Learning Credit total qualified expenses,
                 Form 8863, line 10

        e07300 : Foreign tax credit - Form 1116

        c07180 : Child/dependent care expense credit - Form 2441

        c07200 : Schedule R credit

    Returns
    -------
    c07230 : Education Tax Credits (Form 8863) nonrefundable amount
    """
    c87560 = 0.2 * min(e87530, LLC_Expense_c)
    if MARS == 2:
        c87570 = ETC_pe_Married * 1000.
    else:
        c87570 = ETC_pe_Single * 1000.
    c87590 = max(0., c87570 - c00100)
    c87600 = 10000. * num
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
                         CR_RetirementSavings_hc, CR_ForeignTax_hc,
                         CR_ResidentialEnergy_hc, CR_GeneralBusiness_hc,
                         CR_MinimumTax_hc, CR_OtherCredits_hc, charity_credit,
                         c07180, c07200, c07220, c07230, c07240,
                         c07260, c07300, c07400, c07600, c08000):
    """
    NonRefundableCredits function sequentially limits credits to tax liability.

    Parameters
    ----------
    CR_RetirementSavings_hc: Retirement savings credit haircut
    CR_ForeignTax_hc: Foreign tax credit haircut
    CR_ResidentialEnergy_hc: Residential energy credit haircut
    CR_GeneralBusiness_hc: General business credit haircut
    CR_MinimumTax_hc: Minimum tax credit haircut
    CR_OtherCredits_hc: Other credits haircut
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
                  ptax_was, c03260, e09800, c59660, e11200,
                  c11070):
    """
    Calculates refundable Additional Child Tax Credit (ACTC), c11070,
    following 2018 Form 8812 logic.
    """
    # Part I
    line3 = codtc_limited
    line4 = ACTC_c * n24
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
        if n24 < ACTC_ChildNum:
            if line8 > 0.:
                c11070 = min(line5, line8)
        else:  # if n24 >= ACTC_ChildNum
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
          c07400, c07600, c08000, e09700, e09800, e09900, niit, othertaxes,
          c07100, c09200, odc, charity_credit,
          personal_nonrefundable_credit):
    """
    Computes total used nonrefundable credits, c07100, othertaxes, and
    income tax before refundable credits, c09200.
    """
    # total used nonrefundable credits (as computed in NonrefundableCredits)
    c07100 = (c07180 + c07200 + c07600 + c07300 + c07400 + c07220 + c08000 +
              c07230 + c07240 + c07260 + odc + charity_credit +
              personal_nonrefundable_credit)
    # tax after credits (2016 Form 1040, line 56)
    tax_net_nonrefundable_credits = max(0., c05800 - c07100)
    # tax (including othertaxes) before refundable credits
    othertaxes = e09700 + e09800 + e09900 + niit
    c09200 = othertaxes + tax_net_nonrefundable_credits
    return (c07100, othertaxes, c09200)


@iterate_jit(nopython=True)
def CTC_new(CTC_new_c, CTC_new_rt, CTC_new_c_under6_bonus,
            CTC_new_ps, CTC_new_prt, CTC_new_for_all,
            CTC_new_refund_limited, CTC_new_refund_limit_payroll_rt,
            CTC_new_refund_limited_all_payroll, payrolltax,
            n24, nu06, c00100, MARS, ptax_oasdi, c09200,
            ctc_new):
    """
    Computes new refundable child tax credit using specified parameters.
    """
    if n24 > 0:
        posagi = max(c00100, 0.)
        ctc_new = CTC_new_c * n24 + CTC_new_c_under6_bonus * nu06
        if not CTC_new_for_all:
            ctc_new = min(CTC_new_rt * posagi, ctc_new)
        ymax = CTC_new_ps[MARS - 1]
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


@iterate_jit(nopython=True)
def IITAX(c59660, c11070, c10960, personal_refundable_credit, ctc_new, rptc,
          c09200, payrolltax,
          eitc, refund, iitax, combined):
    """
    Computes final taxes.
    """
    eitc = c59660
    refund = (eitc + c11070 + c10960 +
              personal_refundable_credit + ctc_new + rptc)
    iitax = c09200 - refund
    combined = iitax + payrolltax
    return (eitc, refund, iitax, combined)


@JIT(nopython=True)
def Taxes(income, MARS, tbrk_base,
          rate1, rate2, rate3, rate4, rate5, rate6, rate7, rate8,
          tbrk1, tbrk2, tbrk3, tbrk4, tbrk5, tbrk6, tbrk7):
    """
    Taxes function returns tax amount given the progressive tax rate
    schedule specified by the rate* and (upper) tbrk* parameters and
    given income, filing status (MARS), and tax bracket base (tbrk_base).
    """
    if tbrk_base > 0.:
        brk1 = max(tbrk1[MARS - 1] - tbrk_base, 0.)
        brk2 = max(tbrk2[MARS - 1] - tbrk_base, 0.)
        brk3 = max(tbrk3[MARS - 1] - tbrk_base, 0.)
        brk4 = max(tbrk4[MARS - 1] - tbrk_base, 0.)
        brk5 = max(tbrk5[MARS - 1] - tbrk_base, 0.)
        brk6 = max(tbrk6[MARS - 1] - tbrk_base, 0.)
        brk7 = max(tbrk7[MARS - 1] - tbrk_base, 0.)
    else:
        brk1 = tbrk1[MARS - 1]
        brk2 = tbrk2[MARS - 1]
        brk3 = tbrk3[MARS - 1]
        brk4 = tbrk4[MARS - 1]
        brk5 = tbrk5[MARS - 1]
        brk6 = tbrk6[MARS - 1]
        brk7 = tbrk7[MARS - 1]
    return (rate1 * min(income, brk1) +
            rate2 * min(brk2 - brk1, max(0., income - brk1)) +
            rate3 * min(brk3 - brk2, max(0., income - brk2)) +
            rate4 * min(brk4 - brk3, max(0., income - brk3)) +
            rate5 * min(brk5 - brk4, max(0., income - brk4)) +
            rate6 * min(brk6 - brk5, max(0., income - brk5)) +
            rate7 * min(brk7 - brk6, max(0., income - brk6)) +
            rate8 * max(0., income - brk7))


def ComputeBenefit(calc, ID_switch):
    """
    Calculates the value of the benefits accrued from itemizing.
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


@iterate_jit(nopython=True)
def FairShareTax(c00100, MARS, ptax_was, setax, ptax_amc,
                 FST_AGI_trt, FST_AGI_thd_lo, FST_AGI_thd_hi,
                 fstax, iitax, combined, surtax):
    """
    Computes Fair Share Tax, or "Buffet Rule", types of reforms.

    Taxpayer Characteristics
    ------------------------

    c00100 : AGI

    MARS : filing (marital) status

    ptax_was : payroll tax on wages and salaries

    setax : self-employment tax

    ptax_amc : Additional Medicare Tax on high earnings

    Returns
    -------

    fstax : Fair Share Tax amount

    iitax : individual income tax augmented by fstax

    combined : individual income tax plus payroll taxes augmented by fstax

    surtax : individual income tax subtotal augmented by fstax
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
    combined: combined tax liability
    expanded_income: expanded income

    Returns
    -------
    aftertax_income: expanded_income minus combined
    """
    aftertax_income = expanded_income - combined
    return aftertax_income
