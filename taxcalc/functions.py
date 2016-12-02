"""
Tax-Calculator functions that calculate payroll and individual income taxes.
"""
# CODING-STYLE CHECKS:
# pep8 --ignore=E402 functions.py
# pylint --disable=locally-disabled --extension-pkg-whitelist=numpy function.py
# (when importing numpy, add "--extension-pkg-whitelist=numpy" pylint option)
#
# pylint: disable=too-many-lines
# pylint: disable=invalid-name
# pylint: disable=too-many-arguments
# pylint: disable=too-many-locals


import math
import copy
import numpy as np
from .decorators import iterate_jit, jit


@iterate_jit(nopython=True)
def EI_PayrollTax(SS_Earnings_c, e00200, e00200p, e00200s,
                  FICA_ss_trt, FICA_mc_trt, ALD_SelfEmploymentTax_hc,
                  e00900p, e00900s, e02100p, e02100s,
                  _payrolltax, ptax_was, setax, c03260, ptax_oasdi,
                  _sey, _earned, _earned_p, _earned_s):
    """
    Compute part of total OASDI+HI payroll taxes and earned income variables.
    """
    # compute _sey and its individual components
    sey_p = e00900p + e02100p
    sey_s = e00900s + e02100s
    _sey = sey_p + sey_s  # total self-employment income for filing unit

    # compute taxable earnings for OASDI FICA ('was' denotes 'wage and salary')
    sey_frac = 1.0 - 0.5 * (FICA_ss_trt + FICA_mc_trt)
    txearn_was_p = min(SS_Earnings_c, e00200p)
    txearn_was_s = min(SS_Earnings_c, e00200s)
    txearn_sey_p = min(max(0., sey_p * sey_frac), SS_Earnings_c - txearn_was_p)
    txearn_sey_s = min(max(0., sey_s * sey_frac), SS_Earnings_c - txearn_was_s)

    # compute OASDI and HI payroll taxes on wage-and-salary income
    ptax_ss_was_p = FICA_ss_trt * txearn_was_p
    ptax_ss_was_s = FICA_ss_trt * txearn_was_s
    ptax_mc_was_p = FICA_mc_trt * e00200p
    ptax_mc_was_s = FICA_mc_trt * e00200s
    ptax_was = ptax_ss_was_p + ptax_ss_was_s + ptax_mc_was_p + ptax_mc_was_s

    # compute self-employment tax on taxable self-employment income
    setax_ss_p = FICA_ss_trt * txearn_sey_p
    setax_ss_s = FICA_ss_trt * txearn_sey_s
    setax_mc_p = FICA_mc_trt * max(0., sey_p * sey_frac)
    setax_mc_s = FICA_mc_trt * max(0., sey_s * sey_frac)
    setax_p = setax_ss_p + setax_mc_p
    setax_s = setax_ss_s + setax_mc_s
    setax = setax_p + setax_s

    # compute part of total regular payroll taxes for filing unit
    _payrolltax = ptax_was + setax

    # compute OASDI part of payroll taxes
    ptax_oasdi = ptax_ss_was_p + ptax_ss_was_s + setax_ss_p + setax_ss_s

    # compute self-employment tax on taxable self-employment income
    setax_ss_p = FICA_ss_trt * txearn_sey_p
    setax_ss_s = FICA_ss_trt * txearn_sey_s

    # compute _earned* variables and AGI deduction for
    # "employer share" of self-employment tax, c03260
    # Note: c03260 is the amount on 2015 Form 1040, line 27
    c03260 = (1. - ALD_SelfEmploymentTax_hc) * 0.5 * setax
    _earned = max(0., e00200 + _sey - c03260)
    _earned_p = max(0., (e00200p + sey_p -
                         (1. - ALD_SelfEmploymentTax_hc) * 0.5 * setax_p))
    _earned_s = max(0., (e00200s + sey_s -
                         (1. - ALD_SelfEmploymentTax_hc) * 0.5 * setax_s))
    return (_sey, _payrolltax, ptax_was, setax, c03260, ptax_oasdi,
            _earned, _earned_p, _earned_s)


@iterate_jit(nopython=True)
def DependentCare(nu13, elderly_dependent, _earned,
                  MARS, ALD_Dependents_thd, ALD_Dependents_hc,
                  ALD_Dependents_Child_c, ALD_Dependents_Elder_c,
                  care_deduction):
    """

    Parameters
    ----------
    nu13: Number of dependents under 13 years old
    elderly_dependent: 1 if unit has an elderly dependent; 0 otherwise
    _earned: Form 2441 earned income amount
    MARS: Marital Status
    ALD_Dependents_thd: Maximum income to qualify for deduction
    ALD_Dependents_hc: Deduction for dependent care haircut
    ALD_Dependents_Child_c: National weighted average cost of childcare
    ALD_Dependents_Elder_c: Eldercare deduction ceiling

    Returns
    -------
    care_deduction: Total above the line deductions for dependent care.

    """

    if _earned <= ALD_Dependents_thd[MARS - 1]:
        care_deduction = (((1. - ALD_Dependents_hc) * nu13 *
                           ALD_Dependents_Child_c) +
                          ((1. - ALD_Dependents_hc) * elderly_dependent *
                           ALD_Dependents_Elder_c))
    else:
        care_deduction = 0.
    return care_deduction


@iterate_jit(nopython=True)
def Adj(e03150, e03210, c03260,
        e03270, e03300, e03400, e03500,
        e03220, e03230, e03240, e03290, care_deduction,
        ALD_StudentLoan_hc, ALD_SelfEmp_HealthIns_hc, ALD_KEOGH_SEP_hc,
        ALD_EarlyWithdraw_hc, ALD_Alimony_hc,
        c02900, c02900_in_ei):
    """
    Adj calculates Form 1040 AGI adjustments (i.e., Above-the-Line Deductions)

    Notes
    -----
    Taxpayer characteristics:

        e03210 : Student loan interest deduction

        e03220 : Educator expense deduction

        e03150 : Total deductible IRA plan contributions

        e03230 : Tuition and fees (Form 8917)

        e03240 : Domestic production activity deduction (Form 8903)

        c03260 : Self-employment tax deduction (after haircut)

        e03270 : Self-employed health insurance deduction

        e03290 : HSA deduction (Form 8889)

        e03300 : Total deductible KEOGH/SEP/SIMPLE/etc. plan contributions

        e03400 : Penalty on early withdrawal of savings deduction

        e03500 : Alimony paid deduction

        care_deduction : Dependent care expense deduction

    Tax law parameters:

        ALD_StudentLoan_hc : Student loan interest deduction haircut

        ALD_SelfEmp_HealthIns_hc : Self-employed h.i. deduction haircut

        ALD_KEOGH_SEP_hc : KEOGH/etc. plan contribution deduction haircut

        ALD_EarlyWithdraw_hc : Penalty on early withdrawal deduction haricut

        ALD_Alimony_hc : Alimony paid deduction haircut

    Returns
    -------
    c02900 : total Form 1040 adjustments, which are not included in AGI

    c02900_in_ei : total adjustments included in expanded income
    """
    # Form 2555 foreign earned income deduction is assumed to be zero
    # Form 1040 adjustments that are included in expanded income:
    c02900_in_ei = ((1. - ALD_StudentLoan_hc) * e03210 +
                    c03260 +
                    (1. - ALD_EarlyWithdraw_hc) * e03400 +
                    (1. - ALD_Alimony_hc) * e03500 +
                    e03220 + e03230 + e03240 + e03290 + care_deduction)
    # add in Form 1040 adjustments that are not included in expanded income:
    c02900 = c02900_in_ei + ((1. - ALD_SelfEmp_HealthIns_hc) * e03270 +
                             e03150 +  # deductible IRA contributions
                             (1. - ALD_KEOGH_SEP_hc) * e03300)
    # TODO: move e03270 term into c02900_in_ei after health-insurance-premium
    #       imputations are available
    # TODO: move e03150 and e03300 term into c02900_in_ei after pension-
    #       contribution imputations are available
    return (c02900, c02900_in_ei)


@iterate_jit(nopython=True)
def CapGains(p23250, p22250, _sep, ALD_StudentLoan_hc,
             ALD_Investment_ec_rt, ALD_Investment_ec_base_all,
             e00200, e00300, e00600, e00650, e00700, e00800,
             CG_nodiff, CG_ec, CG_reinvest_ec_rt,
             e00900, e01100, e01200, e01400, e01700, e02000, e02100,
             e02300, e00400, e02400, c02900, e03210, e03230, e03240,
             c01000, c23650, ymod, ymod1, invinc_agi_ec):
    """
    CapGains function: ...
    """
    # net capital gain (long term + short term) before exclusion
    c23650 = p23250 + p22250
    # limitation on capital losses
    c01000 = max((-3000. / _sep), c23650)
    # compute exclusion of investment income from AGI
    invinc = e00300 + e00600 + c01000 + e01100 + e01200
    if ALD_Investment_ec_base_all:
        invinc_ec_base = invinc
    else:
        invinc_ec_base = e00300 + e00650 + p23250
    invinc_agi_ec = ALD_Investment_ec_rt * max(0., invinc_ec_base)
    # compute ymod1 variable that is included in AGI
    ymod1 = (e00200 + e00700 + e00800 + e00900 + e01400 + e01700 +
             invinc - invinc_agi_ec +
             e02000 + e02100 + e02300)
    if CG_nodiff:
        # apply QDIV+CG exclusion if QDIV+LTCG receive no special tax treatment
        qdcg_pos = max(0., e00650 + c01000)
        qdcg_exclusion = (max(CG_ec, qdcg_pos) +
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
    SSBenefits function calculates OASDI benefits included in AGI, c02500.
    """
    if ymod < SS_thd50[MARS - 1]:
        c02500 = 0.
    elif ymod >= SS_thd50[MARS - 1] and ymod < SS_thd85[MARS - 1]:
        c02500 = SS_percentage1 * min(ymod - SS_thd50[MARS - 1], e02400)
    else:
        c02500 = min(SS_percentage2 * (ymod - SS_thd85[MARS - 1]) +
                     SS_percentage1 *
                     min(e02400, SS_thd85[MARS - 1] -
                         SS_thd50[MARS - 1]), SS_percentage2 * e02400)
    return c02500


@iterate_jit(nopython=True)
def AGI(ymod1, c02500, c02900, XTOT, MARS, _sep, DSI, _exact,
        II_em, II_em_ps, II_prt,
        II_credit, II_credit_ps, II_credit_prt,
        c00100, pre_c04600, c04600, personal_credit):
    """
    AGI function: compute Adjusted Gross Income, c00100,
                  compute personal exemption amount, c04600, and
                  compute personal_credit amount
    """
    # calculate AGI assuming no foreign earned income exclusion
    c00100 = ymod1 + c02500 - c02900
    # calculate personal exemption amount
    pre_c04600 = XTOT * II_em
    if DSI:
        pre_c04600 = 0.
    # phase-out personal exemption amount
    if _exact == 1:  # exact calculation as on tax forms
        line5 = max(0., c00100 - II_em_ps[MARS - 1])
        line6 = math.ceil(line5 / (2500. / _sep))
        line7 = II_prt * line6
        c04600 = max(0., pre_c04600 * (1. - line7))
    else:  # smoothed calculation needed for sensible mtr calculation
        dispc_numer = II_prt * (c00100 - II_em_ps[MARS - 1])
        dispc_denom = 2500. / _sep
        dispc = min(1., max(0., dispc_numer / dispc_denom))
        c04600 = pre_c04600 * (1. - dispc)
    # calculate personal credit amount
    personal_credit = II_credit[MARS - 1]
    # phase-out personal credit amount
    if II_credit_prt > 0. and c00100 > II_credit_ps[MARS - 1]:
        credit_phaseout = II_credit_prt * (c00100 - II_credit_ps[MARS - 1])
        personal_credit = max(0., personal_credit - credit_phaseout)
    return (c00100, pre_c04600, c04600, personal_credit)


@iterate_jit(nopython=True)
def ItemDed(e17500, e18400, e18500,
            e20500, e20400, e19200, e19800, e20100,
            MARS, age_head, age_spouse,
            c00100, c04470, c17000, c18300, c20500, c19200,
            c20800, c21040, c21060, c19700,
            ID_ps, ID_Medical_frt, ID_Medical_frt_add4aged, ID_Medical_hc,
            ID_Casualty_frt_in_pufcsv_year,
            ID_Casualty_frt, ID_Casualty_hc, ID_Miscellaneous_frt,
            ID_Miscellaneous_hc, ID_Charity_crt_all, ID_Charity_crt_noncash,
            ID_prt, ID_crt, ID_cap, ID_StateLocalTax_hc, ID_Charity_frt,
            ID_Charity_hc, ID_InterestPaid_hc, ID_RealEstate_hc):
    """
    ItemDed function: itemized deductions, Form 1040, Schedule A

    Notes
    -----
    Tax Law Parameters:
        ID_ps : Itemized deduction phaseout AGI start (Pease)

        ID_crt : Itemized deduction maximum phaseout
        as a decimal fraction of total itemized deduction (Pease)

        ID_prt : Itemized deduction phaseout rate (Pease)
        
        ID_cap: Dollar limit on itemized deductions

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
        contributions; ceiling as a decimal fraction of AGI

        ID_Charity_frt : Disregard for charitable contributions;
        floor as a decimal fraction of AGI

    Taxpayer Characteristics:
        e17500 : Medical expenses

        e18400 : State and local taxes

        e18500 : Real-estate taxes

        e19200 : Interest paid

        e19800 : Charity cash contributions

        e20100 : Charity noncash contributions

        e20400 : Total miscellaneous expenses

        e20500 : Net [of disregard] casualty or theft loss

    Returns
    -------
    c04470 : Itemized deduction amount (and other intermediate variables)
    """
    posagi = max(c00100, 0.)
    # Medical
    medical_frt = ID_Medical_frt
    if age_head >= 65 or (MARS == 2 and age_spouse >= 65):
        medical_frt += ID_Medical_frt_add4aged
    c17750 = medical_frt * posagi
    c17000 = max(0., e17500 - c17750) * (1. - ID_Medical_hc)
    # State and local taxes
    c18300 = ((1. - ID_StateLocalTax_hc) * max(e18400, 0.) +
              (1. - ID_RealEstate_hc) * e18500)
    # Interest paid
    c19200 = e19200 * (1. - ID_InterestPaid_hc)
    # Charity
    lim30 = min(ID_Charity_crt_noncash * posagi, e20100)
    c19700 = min(ID_Charity_crt_all * posagi, lim30 + e19800)
    charity_floor = ID_Charity_frt * posagi  # floor is zero in present law
    c19700 = max(0., c19700 - charity_floor) * (1. - ID_Charity_hc)
    # Casualty
    if e20500 > 0.0:  # add back to e20500 the PUFCSV_YEAR disregard amount
        c37703 = e20500 + ID_Casualty_frt_in_pufcsv_year * posagi
    else:  # small pre-disregard e20500 values are assumed to be zero
        c37703 = 0.
    c20500 = (max(0., c37703 - ID_Casualty_frt * posagi) *
              (1. - ID_Casualty_hc))
    # Miscellaneous
    c20400 = e20400
    c20750 = ID_Miscellaneous_frt * posagi
    c20800 = max(0., c20400 - c20750) * (1. - ID_Miscellaneous_hc)
    # Gross Itemized Deductions
    c21060 = c17000 + c18300 + c19200 + c19700 + c20500 + c20800
    # Limitation on total itemized deductions
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
    c04470 = min(c04470, ID_cap[MARS - 1])
    return (c17000, c18300, c19200, c20500, c20800, c21040, c21060, c04470,
            c19700)


@iterate_jit(nopython=True)
def AdditionalMedicareTax(e00200, MARS,
                          AMEDT_ec, _sey, AMEDT_rt,
                          FICA_mc_trt, FICA_ss_trt,
                          ptax_amc, _payrolltax):
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

        _sey : Self-employment income

    Returns
    -------
    ptax_amc : Additional Medicare Tax

    _payrolltax : payroll tax augmented by Additional Medicare Tax
    """
    line8 = max(0., _sey) * (1. - 0.5 * (FICA_mc_trt + FICA_ss_trt))
    line11 = max(0., AMEDT_ec[MARS - 1] - e00200)
    ptax_amc = AMEDT_rt * (max(0., e00200 - AMEDT_ec[MARS - 1]) +
                           max(0., line8 - line11))
    _payrolltax = _payrolltax + ptax_amc
    return (ptax_amc, _payrolltax)


@iterate_jit(nopython=True)
def StdDed(DSI, _earned, STD, age_head, age_spouse, STD_Aged,
           MARS, MIDR, blind_head, blind_spouse, _standard):
    """
    StdDed function:

    Standard Deduction; Form 1040

    This function calculates standard deduction,
    including standard deduction for dependents, aged and bind.

    Notes
    -----
    Tax Law Parameters:
        STD : Standard deduction amount, filing status dependent

        STD_Aged : Additional standard deduction for blind and aged

    Taxpayer Characteristics:
        _earned : Form 2441 earned income amount

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
    _standard
        Standard deduction amount for each taxpayer
        who files standard deduction. Otherwise value is zero.
    """
    # calculate deduction for dependents
    if DSI == 1:
        c15100 = max(350. + _earned, STD[6])
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
    _standard = basic_stded + extra_stded
    if (MARS == 3 or MARS == 6) and (MIDR == 1):
        _standard = 0.
    return _standard


@iterate_jit(nopython=True)
def TaxInc(c00100, _standard, c04470, c04600, c04800):
    """
    TaxInc function: ...
    """
    c04800 = max(0., c00100 - max(c04470, _standard) - c04600)
    return c04800


@jit(nopython=True)
def SchXYZ(taxable_income, MARS, e00900, e26270,
           PT_rt1, PT_rt2, PT_rt3, PT_rt4, PT_rt5,
           PT_rt6, PT_rt7, PT_rt8,
           PT_brk1, PT_brk2, PT_brk3, PT_brk4, PT_brk5,
           PT_brk6, PT_brk7,
           II_rt1, II_rt2, II_rt3, II_rt4, II_rt5,
           II_rt6, II_rt7, II_rt8,
           II_brk1, II_brk2, II_brk3, II_brk4, II_brk5,
           II_brk6, II_brk7):
    """
    Return Schedule X, Y, Z tax amount for specified taxable_income.
    """
    # separate non-negative taxable income into two non-negative components,
    # doing this in a way so that the components add up to taxable income
    pt_taxinc = max(0., e00900 + e26270)  # non-negative pass-through income
    if pt_taxinc >= taxable_income:
        pt_taxinc = taxable_income
        reg_taxinc = 0.
    else:
        # pt_taxinc is unchanged
        reg_taxinc = taxable_income - pt_taxinc
    # compute Schedule X,Y,Z tax using the two components of taxable income,
    # stacking pass-through taxable income on top of regular taxable income
    if reg_taxinc > 0.:
        reg_tax = Taxes(reg_taxinc, MARS, 0.0,
                        II_rt1, II_rt2, II_rt3, II_rt4,
                        II_rt5, II_rt6, II_rt7, II_rt8, II_brk1, II_brk2,
                        II_brk3, II_brk4, II_brk5, II_brk6, II_brk7)
    else:
        reg_tax = 0.
    if pt_taxinc > 0.:
        pt_tax = Taxes(pt_taxinc, MARS, reg_taxinc,
                       PT_rt1, PT_rt2, PT_rt3, PT_rt4,
                       PT_rt5, PT_rt6, PT_rt7, PT_rt8, PT_brk1, PT_brk2,
                       PT_brk3, PT_brk4, PT_brk5, PT_brk6, PT_brk7)
    else:
        pt_tax = 0.
    return reg_tax + pt_tax


@iterate_jit(nopython=True)
def SchXYZTax(c04800, MARS, e00900, e26270,
              PT_rt1, PT_rt2, PT_rt3, PT_rt4, PT_rt5,
              PT_rt6, PT_rt7, PT_rt8,
              PT_brk1, PT_brk2, PT_brk3, PT_brk4, PT_brk5,
              PT_brk6, PT_brk7,
              II_rt1, II_rt2, II_rt3, II_rt4, II_rt5,
              II_rt6, II_rt7, II_rt8,
              II_brk1, II_brk2, II_brk3, II_brk4, II_brk5,
              II_brk6, II_brk7,
              c05200):
    """
    SchXYZTax calls SchXYZ function and sets c05200 to returned amount.
    """
    c05200 = SchXYZ(c04800, MARS, e00900, e26270,
                    PT_rt1, PT_rt2, PT_rt3, PT_rt4, PT_rt5,
                    PT_rt6, PT_rt7, PT_rt8,
                    PT_brk1, PT_brk2, PT_brk3, PT_brk4, PT_brk5,
                    PT_brk6, PT_brk7,
                    II_rt1, II_rt2, II_rt3, II_rt4, II_rt5,
                    II_rt6, II_rt7, II_rt8,
                    II_brk1, II_brk2, II_brk3, II_brk4, II_brk5,
                    II_brk6, II_brk7)
    return c05200


@iterate_jit(nopython=True)
def GainsTax(e00650, c01000, c23650, p23250, e01100, e58990,
             e24515, e24518, MARS, c04800, c05200, e00900, e26270,
             II_rt1, II_rt2, II_rt3, II_rt4, II_rt5, II_rt6, II_rt7, II_rt8,
             II_brk1, II_brk2, II_brk3, II_brk4, II_brk5, II_brk6, II_brk7,
             PT_rt1, PT_rt2, PT_rt3, PT_rt4, PT_rt5, PT_rt6, PT_rt7, PT_rt8,
             PT_brk1, PT_brk2, PT_brk3, PT_brk4, PT_brk5, PT_brk6, PT_brk7,
             CG_nodiff,
             CG_rt1, CG_rt2, CG_rt3, CG_rt4, CG_brk1, CG_brk2, CG_brk3,
             dwks10, dwks13, dwks14, dwks19, c05700, _taxbc):
    """
    GainsTax function implements (2015) Schedule D Tax Worksheet logic for
    the special taxation of long-term capital gains and qualified dividends
    if CG_nodiff is false
    """
    # pylint: disable=too-many-statements,too-many-branches
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
        hi_base = max(0., dwks31 - CG_brk3[MARS - 1])
        hi_incremental_rate = CG_rt4 - CG_rt3
        highest_rate_incremental_tax = hi_incremental_rate * hi_base
        # break in worksheet lines
        dwks33 = min(dwks9, e24518)
        dwks34 = dwks10 + dwks19
        dwks36 = max(0., dwks34 - dwks1)
        dwks37 = max(0., dwks33 - dwks36)
        dwks38 = 0.25 * dwks37
        # break in worksheet lines
        dwks39 = dwks19 + dwks20 + dwks28 + dwks31 + dwks37
        dwks40 = dwks1 - dwks39
        dwks41 = 0.28 * dwks40
        dwks42 = SchXYZ(dwks19, MARS, e00900, e26270,
                        PT_rt1, PT_rt2, PT_rt3, PT_rt4, PT_rt5,
                        PT_rt6, PT_rt7, PT_rt8,
                        PT_brk1, PT_brk2, PT_brk3, PT_brk4, PT_brk5,
                        PT_brk6, PT_brk7,
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

    # final calculations done no matter what the value of hasqdivltcg
    c05100 = c24580  # because no foreign earned income deduction
    c05700 = 0.  # no Form 4972, Lump Sum Distributions
    _taxbc = c05700 + c05100
    return (dwks10, dwks13, dwks14, dwks19, c05700, _taxbc)


@iterate_jit(nopython=True)
def AGIsurtax(c00100, MARS, AGI_surtax_trt, AGI_surtax_thd, _taxbc, _surtax):
    """
    AGIsurtax computes surtax on AGI above some threshold
    """
    if AGI_surtax_trt > 0.:
        hiAGItax = AGI_surtax_trt * max(c00100 - AGI_surtax_thd[MARS - 1], 0.)
        _taxbc += hiAGItax
        _surtax += hiAGItax
    return (_taxbc, _surtax)


@iterate_jit(nopython=True)
def AMT(e07300, dwks13, _standard, f6251, c00100, c18300, _taxbc,
        c04470, c17000, c20800, c21040, e24515, MARS, _sep, dwks19,
        dwks14, c05700, e62900, e00700, dwks10, age_head, _earned, cmbtp,
        KT_c_Age, AMT_brk1, AMT_thd_MarriedS,
        AMT_em, AMT_prt, AMT_rt1, AMT_rt2,
        AMT_Child_em, AMT_em_ps, AMT_em_pe,
        AMT_CG_brk1, AMT_CG_brk2, AMT_CG_brk3, AMT_CG_rt1, AMT_CG_rt2,
        AMT_CG_rt3, AMT_CG_rt4, c05800, c09600, c62100):
    """
    AMT function computes Alternative Minimum Tax taxable income and liability:
    c62100 is AMT taxable income
    c09600 is AMT tax liability
    c05800 is total (reg + AMT) income tax liability before credits

    Note that line-number variable names refer to (2015) Form 6251.
    """
    # pylint: disable=too-many-statements,too-many-branches
    # Form 6251, Part I
    if _standard == 0.0:
        c62100 = (c00100 - e00700 - c04470 +
                  max(0., min(c17000, 0.025 * c00100)) +
                  c18300 + c20800 - c21040)
    if _standard > 0.0:
        c62100 = c00100 - e00700
    c62100 += cmbtp  # add income not in AGI but considered income for AMT
    if MARS == 3 or MARS == 6:
        amtsepadd = max(0.,
                        min(AMT_thd_MarriedS, 0.25 * (c62100 - AMT_em_pe)))
    else:
        amtsepadd = 0.
    c62100 = c62100 + amtsepadd  # AMT taxable income, which is line28
    # Form 6251, Part II top
    line29 = max(0., AMT_em[MARS - 1] - AMT_prt *
                 max(0., c62100 - AMT_em_ps[MARS - 1]))
    if age_head != 0 and age_head < KT_c_Age:
        line29 = min(line29, _earned + AMT_Child_em)
    line30 = max(0., c62100 - line29)
    line3163 = (AMT_rt1 * line30 +
                AMT_rt2 * max(0., (line30 - (AMT_brk1 / _sep))))
    if dwks10 > 0. or dwks13 > 0. or dwks14 > 0. or dwks19 > 0. or e24515 > 0.:
        # complete Form 6251, Part III (line36 is equal to line30)
        line37 = dwks13
        line38 = e24515
        line39 = min(line37 + line38, dwks10)
        line40 = min(line30, line39)
        line41 = max(0., line30 - line40)
        line42 = (AMT_rt1 * line41 +
                  AMT_rt2 * max(0., (line41 - (AMT_brk1 / _sep))))
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
    c09600 = max(0., line33 - max(0., _taxbc - e07300 - c05700))
    c05800 = _taxbc + c09600
    return (c62100, c09600, c05800)


@iterate_jit(nopython=True)
def NetInvIncTax(e00300, e00600, e02000, e26270, c01000,
                 c00100, NIIT_thd, MARS, NIIT_PT_taxed, NIIT_rt, NIIT):
    """
    NetInvIncTax function computes Net Investment Income Tax amount
    (assume all annuity income is excluded from net investment income)
    """
    modAGI = c00100  # no deducted foreign earned income to add
    if not NIIT_PT_taxed:
        NII = max(0., e00300 + e00600 + c01000 + e02000 - e26270)
    else:  # do not subtract e26270 from e02000
        NII = max(0., e00300 + e00600 + c01000 + e02000)
    NIIT = NIIT_rt * min(NII, max(0., modAGI - NIIT_thd[MARS - 1]))
    return NIIT


@iterate_jit(nopython=True)
def F2441(MARS, _earned_p, _earned_s, f2441, CDCC_c, e32800,
          _exact, c00100, CDCC_ps, CDCC_crt, c05800, e07300, c07180):
    """
    Form 2441 calculation of child and dependent care expense credit, c07180
    """
    c32880 = _earned_p  # earned income of taxpayer
    if MARS == 2:
        c32890 = _earned_s  # earned income of spouse, if present
    else:
        c32890 = _earned_p
    dclim = min(f2441, 2) * CDCC_c
    # care expenses are limited by policy
    c32800 = max(0., min(e32800, dclim))
    # credit is limited to minimum of individuals' earned income
    c33000 = max(0., min(c32800, min(c32880, c32890)))
    # credit is limited by AGI-related fraction
    if _exact == 1:
        tratio = math.ceil(max(((c00100 - CDCC_ps) / 2000.), 0.))
        c33200 = c33000 * 0.01 * max(20., CDCC_crt - min(15., tratio))
    else:
        c33200 = c33000 * 0.01 * max(20., CDCC_crt -
                                     max(((c00100 - CDCC_ps) / 2000.), 0.))
    # credit is limited by tax liability
    c07180 = min(max(0., c05800 - e07300), c33200)
    return c07180


@jit(nopython=True)
def EITCamount(phasein_rate, earnings, max_amount,
               phaseout_start, eitc_agi, phaseout_rate):
    """
    Return EITC amount given specified parameters
    """
    eitc = min(phasein_rate * earnings, max_amount)
    if earnings > phaseout_start or eitc_agi > phaseout_start:
        eitcx = max(0., (max_amount - phaseout_rate *
                         max(0., max(earnings, eitc_agi) - phaseout_start)))
        eitc = min(eitc, eitcx)
    return eitc


@iterate_jit(nopython=True)
def EITC(MARS, DSI, EIC, c00100, e00300, e00400, e00600, c01000,
         p25470, e27200, age_head, age_spouse, _earned, _earned_p, _earned_s,
         EITC_ps, EITC_MinEligAge, EITC_MaxEligAge, EITC_ps_MarriedJ,
         EITC_rt, EITC_c, EITC_prt, EITC_InvestIncome_c, EITC_indiv,
         c59660):
    """
    EITC function computes EITC amount, c59660
    """
    # pylint: disable=too-many-branches
    if not EITC_indiv:
        # filing-unit and number-of-kids based EITC (rather than indiv EITC)
        invinc = (e00400 + e00300 + e00600 +
                  max(0., c01000) + max(0., (0. - p25470)) + max(0., e27200))
        if MARS == 3 or MARS == 6 or DSI == 1 or invinc > EITC_InvestIncome_c:
            c59660 = 0.
        else:
            po_start = EITC_ps[EIC]
            if MARS == 2:
                po_start += EITC_ps_MarriedJ[EIC]
            eitc_agi = c00100 + e00400
            eitc = EITCamount(EITC_rt[EIC], _earned, EITC_c[EIC],
                              po_start, eitc_agi, EITC_prt[EIC])
            if EIC == 0:
                # enforce age eligibility rule for those with no EITC-eligible
                # kids assuming that an unknown age_* value implies EITC age
                # eligibility
                # pylint: disable=bad-continuation,too-many-boolean-expressions
                if MARS == 2:
                    if (age_head == 0 or age_spouse == 0 or
                        (age_head >= EITC_MinEligAge and
                         age_head <= EITC_MaxEligAge) or
                        (age_spouse >= EITC_MinEligAge and
                         age_spouse <= EITC_MaxEligAge)):
                        c59660 = eitc
                    else:
                        c59660 = 0.
                else:  # if MARS != 2
                    if (age_head == 0 or
                        (age_head >= EITC_MinEligAge and
                         age_head <= EITC_MaxEligAge)):
                        c59660 = eitc
                    else:
                        c59660 = 0.
            else:  # if EIC != 0
                c59660 = eitc
    else:
        # individual EITC rather than a filing-unit EITC
        # .. calculate eitc amount for taxpayer
        eitc_p = EITCamount(EITC_rt[EIC], _earned_p, EITC_c[EIC],
                            EITC_ps[EIC], _earned_p, EITC_prt[EIC])
        # .. calculate eitc amount for spouse
        if MARS == 2:
            eitc_s = EITCamount(EITC_rt[EIC], _earned_s, EITC_c[EIC],
                                EITC_ps[EIC], _earned_s, EITC_prt[EIC])
        else:
            eitc_s = 0.
        # .. combine taxpayer and spouse individual EITC amounts
        c59660 = eitc_p + eitc_s
    return c59660


@iterate_jit(nopython=True)
def ChildTaxCredit(n24, MARS, c00100, _exact,
                   CTC_c, CTC_ps, CTC_prt, prectc, nu05,
                   CTC_c_under5_bonus, XTOT, _num,
                   DependentCredit_c, dep_credit):
    """
    ChildTaxCredit function computes prectc amount and dependent credit
    """
    # calculate prectc amount
    prectc = CTC_c * n24 + CTC_c_under5_bonus * nu05
    modAGI = c00100  # no deducted foreign earned income to add
    if modAGI > CTC_ps[MARS - 1]:
        excess = modAGI - CTC_ps[MARS - 1]
        if _exact == 1:
            excess = 1000. * math.ceil(excess / 1000.)
        prectc = max(0., prectc - CTC_prt * excess)
    # calculate and phase-out dependent credit
    dep_credit = DependentCredit_c * max(0, XTOT - _num)
    if CTC_prt > 0. and c00100 > CTC_ps[MARS - 1]:
        thresh = CTC_ps[MARS - 1] + n24 * CTC_c / CTC_prt
        excess = c00100 - thresh
        if _exact == 1:
            excess = 1000. * math.ceil(excess / 1000.)
        dep_phaseout = CTC_prt * (c00100 - excess)
        dep_credit = max(0., dep_credit - dep_phaseout)
    return (prectc, dep_credit)


@iterate_jit(nopython=True)
def AmOppCreditParts(p87521, _num, c00100, c10960, c87668):
    """
    American Opportunity Credit (Form 8863) nonrefundable (c87668) and
                                            refundable (c10960) parts
    Logic corresponds to Form 8863, Part I

    This function applies a phaseout to the Form 8863, line 1,
    American Opportunity Credit amount, p87521, and then applies
    the 0.4 refundable rate.

    Notes
    -----
    Tax Law Parameters that are not parameterized:

        90000 : American Opportunity Credit phaseout income base

        10000 : American Opportunity Credit phaseout income range length

        1/1000 : American Opportunity Credit phaseout rate

        0.4 : American Opportunity Credit refundable rate

    Parameters
    ----------
        p87521 : total tentative American Opportunity Credit for all students,
                 Form 8863, line 1

        _num : number of people filing jointly

        c00100 : AGI

    Returns
    -------
        c10960 : Refundable part of American Opportunity Credit

        c87668 : Tentative nonrefundable part of American Opportunity Credit
    """
    if p87521 > 0.:
        c87658 = max(0., 90000. * _num - c00100)
        c87660 = 10000. * _num
        c87662 = 1000. * min(1., c87658 / c87660)
        c87664 = c87662 * p87521 / 1000.
        c10960 = 0.4 * c87664
        c87668 = c87664 - c10960
    else:
        c10960 = 0.
        c87668 = 0.
    return (c10960, c87668)


@iterate_jit(nopython=True)
def SchR(age_head, age_spouse, MARS, c00100,
         c05800, e07300, c07180, e02400, c02500, e01500, e01700,
         c07200):
    """
    Calculate Schedule R credit for the elderly and the disabled, c07200

    Note that all Schedule R policy parameters are not inflation indexed.

    Note that all Schedule R policy parameters are hard-coded, and therefore,
    are not able to be changed using Policy class parameters.
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
        elif MARS == 1 or MARS == 4:
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
        c07200 = min(schr20, schr21)
    else:  # if not calculating Schedule R credit
        c07200 = 0.
    return c07200


@iterate_jit(nopython=True)
def EducationTaxCredit(e87530, MARS, c00100, _num, c05800,
                       e07300, c07180, c07200, c87668,
                       LLC_Expense_c, ETC_pe_Single, ETC_pe_Married,
                       c07230):
    """
    Education Tax Credit (Form 8863) nonrefundable amount, c07230
    Logic corresponds to Form 8863, Part II

    Notes
    -----
    Tax Law Parameters that are not parameterized:

        0.2 : Lifetime Learning Credit ratio against expense

    Tax Law Parameters that are parameterized:

        LLC_Expense_c : Lifetime Learning Credit expense limit

        ETC_pe_Married : Education Tax Credit phaseout end for married

        ETC_pe_Single : Education Tax Credit phaseout end for single

    Taxpayer Charateristics:

        e87530 : Lifetime Learning Credit total qualified expenses,
                 Form 8863, line 10

        e07300 : Foreign tax credit - Form 1116

        c07180 : Child/dependent care expense credit - Form 2441

        c07200 : Schedule R credit

    Returns
    -------
    c07230 : Education Tax Credit (Form 8863) nonrefundable amount
    """
    c87560 = 0.2 * min(e87530, LLC_Expense_c)
    if MARS == 2:
        c87570 = ETC_pe_Married * 1000.
    else:
        c87570 = ETC_pe_Single * 1000.
    c87590 = max(0., c87570 - c00100)
    c87600 = 10000. * _num
    c87610 = min(1., c87590 / c87600)
    c87620 = c87560 * c87610
    xline4 = max(0., c05800 - (e07300 + c07180 + c07200))
    xline5 = min(c87620, xline4)
    xline9 = max(0., c05800 - (e07300 + c07180 + c07200 + xline5))
    xline10 = min(c87668, xline9)
    c87680 = xline5 + xline10
    c07230 = c87680
    return c07230


@iterate_jit(nopython=True)
def NonrefundableCredits(c05800, e07240, e07260, e07300, e07400,
                         e07600, p08000, prectc, dep_credit,
                         c07180, c07200, c07220, c07230, c07240,
                         c07260, c07300, c07400, c07600, c08000):
    """
    NonRefundableCredits function sequentially limits credits to tax liability
    """
    # limit tax credits to tax liability in order they are on 2015 1040 form
    avail = c05800
    c07300 = min(e07300, avail)  # Foreign tax credit - Form 1116
    avail = avail - c07300
    c07180 = min(c07180, avail)  # Child & dependent care expense credit
    avail = avail - c07180
    c07230 = min(c07230, avail)  # Education tax credit
    avail = avail - c07230
    c07240 = min(e07240, avail)  # Retirement savings credit - Form 8880
    avail = avail - c07240
    c07220 = min(prectc, avail)  # Child tax credit
    avail = avail - c07220
    c07260 = min(e07260, avail)  # Residential energy credit - Form 5695
    avail = avail - c07260
    c07400 = min(e07400, avail)  # General business credit - Form 3800
    avail = avail - c07400
    c07600 = min(e07600, avail)  # Prior year minimum tax credit - Form 8801
    avail = avail - c07600
    c07200 = min(c07200, avail)  # Schedule R credit
    avail = avail - c07200
    dep_credit = min(avail, dep_credit)  # Dependent credit
    avail = avail - dep_credit
    c08000 = min(p08000, avail)  # Other credits
    avail = avail - c08000
    return (c07180, c07200, c07220, c07230, c07240, dep_credit,
            c07260, c07300, c07400, c07600, c08000)


@iterate_jit(nopython=True)
def AdditionalCTC(n24, prectc, _earned, c07220, ptax_was,
                  ACTC_Income_thd, ACTC_rt, ACTC_ChildNum,
                  c03260, e09800, c59660, e11200, c11070, nu05,
                  ACTC_rt_bonus_under5family):
    """
    Calculates Additional (refundable) Child Tax Credit, c11070
    """
    c82925 = 0.
    c82930 = 0.
    c82935 = 0.
    c82880 = 0.
    c82885 = 0.
    c82890 = 0.
    c82900 = 0.
    c82905 = 0.
    c82910 = 0.
    c82915 = 0.
    c82920 = 0.
    c82937 = 0.
    c82940 = 0.
    c11070 = 0.
    # Part I of 2005 Form 8812
    if n24 > 0:
        c82925 = prectc
        c82930 = c07220
        c82935 = c82925 - c82930
        # CTC not applied to tax
        c82880 = max(0., _earned)
        c82885 = max(0., c82880 - ACTC_Income_thd)
        # Accomodate ACTC rate bonus for families with children under 5
        if nu05 == 0:
            ACTC_rate = ACTC_rt
        else:
            ACTC_rate = ACTC_rt + ACTC_rt_bonus_under5family
        c82890 = ACTC_rate * c82885
    # Part II of 2005 Foreignorm 8812
    if n24 >= ACTC_ChildNum and c82890 < c82935:
        c82900 = 0.5 * ptax_was
        c82905 = c03260 + e09800
        c82910 = c82900 + c82905
        c82915 = c59660 + e11200
        c82920 = max(0., c82910 - c82915)
        c82937 = max(c82890, c82920)
    # Part II of 2005 Form 8812
    if n24 > 0 and n24 <= 2 and c82890 > 0:
        c82940 = min(c82890, c82935)
    if n24 > 2:
        if c82890 >= c82935:
            c82940 = c82935
        else:
            c82940 = min(c82935, c82937)
    c11070 = c82940
    return c11070


@iterate_jit(nopython=True)
def C1040(c05800, c07180, c07200, c07220, c07230, c07240, c07260, c07300,
          c07400, c07600, c08000, e09700, e09800, e09900, NIIT,
          c07100, c09200, dep_credit):
    """
    C1040 function computes total nonrefundable credits, c07100, and
                            income tax before refundable credits, c09200
    """
    # total nonrefundable credits (2015 Form 1040, line 55)
    c07100 = (c07180 + c07200 + c07600 + c07300 + c07400 + c07220 + c08000 +
              c07230 + c07240 + c07260 + dep_credit)
    # tax after credits (2015 Form 1040, line 56)
    tax_net_nonrefundable_credits = max(0., c05800 - c07100)
    # tax before refundable credits
    othertaxes = e09700 + e09800 + e09900 + NIIT
    c09200 = othertaxes + tax_net_nonrefundable_credits
    return (c07100, c09200)


@iterate_jit(nopython=True)
def IITAX(c59660, c11070, c10960, personal_credit,
          c09200, _payrolltax, nu05,
          CTC_new_c, CTC_new_rt, CTC_new_c_under5_bonus,
          n24, c00100, MARS, ptax_oasdi, CTC_new_refund_limited,
          CTC_new_ps, CTC_new_prt, CTC_new_refund_limit_payroll_rt,
          ctc_new, _eitc, _refund, _iitax, _combined):
    """
    Compute final taxes including new refundable child tax credit
    """
    # compute new refundable child tax credit
    if n24 > 0:
        posagi = max(c00100, 0.)
        ctc_new = min(CTC_new_rt * posagi,
                      CTC_new_c * n24 + CTC_new_c_under5_bonus * nu05)
        ymax = CTC_new_ps[MARS - 1]
        if posagi > ymax:
            ctc_new_reduced = max(0.,
                                  ctc_new - CTC_new_prt * (posagi - ymax))
            ctc_new = min(ctc_new, ctc_new_reduced)
        if ctc_new > 0. and CTC_new_refund_limited:
            refund_new = max(0., ctc_new - c09200)
            limit_new = CTC_new_refund_limit_payroll_rt * ptax_oasdi
            limited_new = max(0., refund_new - limit_new)
            ctc_new = max(0., ctc_new - limited_new)
    else:
        ctc_new = 0.
    # compute final taxes
    _eitc = c59660
    _refund = _eitc + c11070 + c10960 + personal_credit + ctc_new
    _iitax = c09200 - _refund
    _combined = _iitax + _payrolltax
    return (ctc_new, _eitc, _refund, _iitax, _combined)


@jit(nopython=True)
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
        no_ID_calc.policy.ID_Medical_hc = 1.
    if ID_switch[1]:
        no_ID_calc.policy.ID_StateLocalTax_hc = 1.
    if ID_switch[2]:
        no_ID_calc.policy.ID_RealEstate_hc = 1.
    if ID_switch[3]:
        no_ID_calc.policy.ID_Casualty_hc = 1.
    if ID_switch[4]:
        no_ID_calc.policy.ID_Miscellaneous_hc = 1.
    if ID_switch[5]:
        no_ID_calc.policy.ID_InterestPaid_hc = 1.
    if ID_switch[6]:
        no_ID_calc.policy.ID_Charity_hc = 1.
    no_ID_calc.calc_one_year()
    # pylint: disable=protected-access
    benefit = np.where(
        no_ID_calc.records._iitax - calc.records._iitax > 0.,
        no_ID_calc.records._iitax - calc.records._iitax, 0.)
    return benefit


def BenefitSurtax(calc):
    """
    BenefitSurtax function: computes itemized-deduction-benefit surtax and
    adds the surtax amount to income tax, combined tax, and surtax liabilities.
    """
    if calc.policy.ID_BenefitSurtax_crt != 1.:
        ben = ComputeBenefit(calc, calc.policy.ID_BenefitSurtax_Switch)
        ben_deduct = (calc.policy.ID_BenefitSurtax_crt * calc.records.c00100)
        ben_exempt = calc.policy.ID_BenefitSurtax_em[calc.records.MARS - 1]
        ben_surtax = calc.policy.ID_BenefitSurtax_trt * np.where(
            ben > (ben_deduct + ben_exempt),
            ben - (ben_deduct + ben_exempt), 0.)
        # add ben_surtax to income & combined taxes and to surtax subtotal
        calc.records._iitax += ben_surtax
        calc.records._combined += ben_surtax
        calc.records._surtax += ben_surtax


def BenefitLimitation(calc):
    """
    BenefitLimitation function: limits the benefits of select itemized
    deductions to a fraction of deductible expenses.
    """
    if calc.policy.ID_BenefitCap_rt != 1.:
        benefit = ComputeBenefit(calc, calc.policy.ID_BenefitCap_Switch)
    # Calculate total deductible expenses under the cap.
        deductible_expenses = 0.
        if calc.policy.ID_BenefitCap_Switch[0]:  # Medical
            deductible_expenses += calc.records.c17000
        if calc.policy.ID_BenefitCap_Switch[1]:  # StateLocal
            deductible_expenses += ((1. - calc.policy.ID_StateLocalTax_hc) *
                                    np.maximum(calc.records.e18400, 0.))
        if calc.policy.ID_BenefitCap_Switch[2]:
            deductible_expenses += ((1. - calc.policy.ID_RealEstate_hc) *
                                    calc.records.e18500)
        if calc.policy.ID_BenefitCap_Switch[3]:  # Casualty
            deductible_expenses += calc.records.c20500
        if calc.policy.ID_BenefitCap_Switch[4]:  # Miscellaneous
            deductible_expenses += calc.records.c20800
        if calc.policy.ID_BenefitCap_Switch[5]:   # Mortgage and interest paid
            deductible_expenses += calc.records.c19200
        if calc.policy.ID_BenefitCap_Switch[6]:  # Charity
            deductible_expenses += calc.records.c19700
        # Calculate cap value for itemized deductions
        benefit_limit = deductible_expenses * calc.policy.ID_BenefitCap_rt
        # Add the difference between the actual benefit and capped benefit
        # to income tax and combined tax liabilities.
        excess_benefit = np.maximum(benefit - benefit_limit, 0)
        calc.records._iitax += excess_benefit
        calc.records._surtax += excess_benefit
        calc.records._combined += excess_benefit


@iterate_jit(nopython=True)
def FairShareTax(c00100, MARS, ptax_was, setax, ptax_amc,
                 FST_AGI_trt, FST_AGI_thd_lo, FST_AGI_thd_hi,
                 fstax, _iitax, _combined, _surtax):
    """
    Computes Fair Share Tax, or "Buffet Rule", types of reforms

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

    _iitax : individual income tax augmented by fstax

    _combined : individual income tax plus payroll taxes augmented by fstax

    _surtax : individual income tax subtotal augmented by fstax
    """
    if FST_AGI_trt > 0. and c00100 >= FST_AGI_thd_lo[MARS - 1]:
        employee_share = 0.5 * ptax_was + 0.5 * setax + ptax_amc
        fstax = max(c00100 * FST_AGI_trt - _iitax - employee_share, 0.)
        thd_gap = max(FST_AGI_thd_hi[MARS - 1] - FST_AGI_thd_lo[MARS - 1], 0.)
        if thd_gap > 0. and c00100 < FST_AGI_thd_hi[MARS - 1]:
            fstax *= (c00100 - FST_AGI_thd_lo[MARS - 1]) / thd_gap
        _iitax += fstax
        _combined += fstax
        _surtax += fstax
    else:
        fstax = 0.
    return (fstax, _iitax, _combined, _surtax)


@iterate_jit(nopython=True)
def LumpSumTax(DSI, _num, XTOT,
               LST,
               lumpsum_tax, _combined):
    """
    Compute lump-sum tax and add it to combined taxes.
    """
    if LST == 0.0 or DSI == 1:
        lumpsum_tax = 0.
    else:
        lumpsum_tax = LST * max(_num, XTOT)
    _combined += lumpsum_tax
    return (lumpsum_tax, _combined)


@iterate_jit(nopython=True)
def ExpandIncome(c00100, ptax_was, e02400, c02500,
                 c02900_in_ei, e00400, invinc_agi_ec, cmbtp,
                 _expanded_income):
    """
    ExpandIncome function calculates and returns _expanded_income.
    """
    # compute employer share of OASDI+HI payroll tax on wages and salaries
    employer_fica_share = 0.5 * ptax_was
    # compute OASDI benefits not included in AGI
    non_taxable_ss_benefits = e02400 - c02500
    # compute expanded income as AGI plus several additional amounts
    _expanded_income = (c00100 +  # adjusted gross income
                        c02900_in_ei +  # ajustments to AGI
                        e00400 +  # non-taxable interest income
                        invinc_agi_ec +  # AGI-excluded taxable invest income
                        cmbtp +  # AMT taxable income items from Form 6251
                        non_taxable_ss_benefits +
                        employer_fica_share)
    return _expanded_income
