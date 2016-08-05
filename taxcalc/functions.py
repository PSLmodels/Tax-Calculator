"""
Tax-Calculator functions that calculate FICA and individual income taxes.
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
import numpy as np
from .decorators import iterate_jit, jit
import copy


@iterate_jit(nopython=True)
def EI_FICA(SS_Earnings_c, e00200, e00200p, e00200s,
            FICA_ss_trt, FICA_mc_trt,
            e00900p, e00900s, e02100p, e02100s,
            _fica, _fica_was, c03260, c09400,
            _sey, _earned, _earned_p, _earned_s):
    """
    EI_FICA function: computes total earned income and regular FICA taxes.
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

    # compute OASDI FICA taxes for was and sey taxable earnings separately
    fica_ss_was_p = FICA_ss_trt * txearn_was_p
    fica_ss_was_s = FICA_ss_trt * txearn_was_s
    fica_ss_sey_p = FICA_ss_trt * txearn_sey_p
    fica_ss_sey_s = FICA_ss_trt * txearn_sey_s

    # compute regular HI FICA taxes for all was and sey earnings separately
    fica_mc_was_p = FICA_mc_trt * e00200p
    fica_mc_was_s = FICA_mc_trt * e00200s
    fica_mc_sey_p = FICA_mc_trt * max(0., sey_p * sey_frac)
    fica_mc_sey_s = FICA_mc_trt * max(0., sey_s * sey_frac)

    # compute total regular FICA taxes for filing unit
    fica_ss = fica_ss_was_p + fica_ss_was_s + fica_ss_sey_p + fica_ss_sey_s
    fica_mc = fica_mc_was_p + fica_mc_was_s + fica_mc_sey_p + fica_mc_sey_s
    _fica = fica_ss + fica_mc

    # compute regular FICA taxes on wage-and-salary income
    _fica_was = fica_ss_was_p + fica_ss_was_s + fica_mc_was_p + fica_mc_was_s

    # compute AGI deduction for "employer share" of self-employment FICA taxes
    c09400 = fica_ss_sey_p + fica_ss_sey_s + fica_mc_sey_p + fica_mc_sey_s
    c03260 = 0.5 * c09400  # half of c09400 represents the "employer share"

    # compute _earned and its individual components
    _earned = max(0., e00200 + _sey - c03260)
    _earned_p = max(0., e00200p + sey_p -
                    0.5 * (fica_ss_sey_p + fica_mc_sey_p))
    _earned_s = max(0., e00200s + sey_s -
                    0.5 * (fica_ss_sey_s + fica_mc_sey_s))

    return (_sey, _fica, _fica_was, c09400, c03260,
            _earned, _earned_p, _earned_s)


@iterate_jit(nopython=True)
def Adj(e03150, e03210, c03260,
        e03270, e03300, e03400, e03500,
        e03220, e03230, e03240, e03290, ALD_StudentLoan_HC,
        ALD_SelfEmploymentTax_HC, ALD_SelfEmp_HealthIns_HC, ALD_KEOGH_SEP_HC,
        ALD_EarlyWithdraw_HC, ALD_Alimony_HC,
        _feided, c02900):
    """
    Adj function:

    Adjustments: Form 1040, Form 2555.
    Calculates foreign earned income and total adjustments

    Notes
    -----
    Taxpayer characteristics:
        e03210 : Student loan interst deduction

        e03220 : Education Expense deduction

        e03150 : Total deduction IRA contributions

        e03230 : Education credit adjustments

        e03240 : Domestic Production Activity Deduction

        c03260 : Self employed payroll tax deduction

        e03270 : Self employed health insurance deduction

        e03290 : HSA deduction computer amount

        e03300 : Payments to a KEOGH plan and SEP deduction

        e03400 : Forfeited interest penalty early withdraw

        e03500 : Alimony withdraw

    Tax law parameters:
        ALD_StudentLoan_HC : Deduction for student loan interest haircut

        ALD_SelfEmploymentTax_HC : Deduction for self-employment tax haircut

        ALD_SelfEmp_HealthIns_HC :
        Deduction for self employed health insurance haircut

        ALD_KEOGH_SEP_HC :
        Deduction for payment to either KEOGH or SEP plan haircut

        ALD_EarlyWithdraw_HC : Deduction for forfeited interest penalty haricut

        ALD_Alimony_HC : Deduction for alimony payment haircut

    Returns
    -------
    _feided : foreign earned income deduction

    c02900 : total Form 1040 adjustments
    """
    # Form 2555: foreign earned income deduction
    _feided = 0.
    # Form 1040: adjustments
    c02900 = (e03150 + (1 - ALD_StudentLoan_HC) * e03210 +
              (1 - ALD_SelfEmploymentTax_HC) * c03260 +
              (1 - ALD_SelfEmp_HealthIns_HC) * e03270 +
              (1 - ALD_KEOGH_SEP_HC) * e03300 + (1 - ALD_EarlyWithdraw_HC) *
              e03400 + (1 - ALD_Alimony_HC) * e03500 +
              e03220 + e03230 + e03240 + e03290)
    return (_feided, c02900)


@iterate_jit(nopython=True)
def CapGains(p23250, p22250, _sep, _feided, FEI_ec_c, ALD_Interest_ec,
             ALD_StudentLoan_HC, f2555, e00200, e00300, e00600, e00700, e00800,
             e00900, e01100, e01200, e01400, e01700, e02000, e02100,
             e02300, e00400, e02400, c02900, e03210, e03230, e03240,
             c01000, c02700, c23650, ymod, ymod1):
    """
    CapGains function: ...
    """
    # Net capital gain (long term + short term) before exclusion
    c23650 = p23250 + p22250
    # Limitation for capital loss
    c01000 = max((-3000. / _sep), c23650)
    # Foreign earned income exclusion
    c02700 = min(_feided, FEI_ec_c * f2555)
    # compute ymod* variables
    ymod1 = (e00200 + (1 - ALD_Interest_ec) * e00300 + e00600 + e00700 +
             e00800 + e00900 + c01000 + e01100 + e01200 + e01400 + e01700 +
             e02000 + e02100 + e02300)
    ymod2 = e00400 + (0.50 * e02400) - c02900
    ymod3 = (1 - ALD_StudentLoan_HC) * e03210 + e03230 + e03240
    ymod = ymod1 + ymod2 + ymod3
    return (c23650, c01000, c02700, ymod1, ymod)


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
def AGI(ymod1, c02500, c02700, c02900, XTOT, MARS, _sep, DSI,
        II_em, II_em_ps, II_prt,
        c00100, _posagi, _prexmp, c04600):
    """
    AGI function: compute Adjusted Gross Income, c00100
    """
    c00100 = ymod1 + c02500 - c02700 - c02900
    _posagi = max(c00100, 0.)
    _prexmp = XTOT * II_em
    if DSI:
        _prexmp = 0.
    # Personal Exemptions (_phaseout smoothed)
    _dispc_numer = II_prt * (_posagi - II_em_ps[MARS - 1])
    _dispc_denom = 2500. / _sep
    _dispc = min(1., max(0., _dispc_numer / _dispc_denom))
    c04600 = _prexmp * (1. - _dispc)
    return (c00100, _posagi, _prexmp, c04600)


@iterate_jit(nopython=True)
def ItemDed(_posagi, e17500, e18400, e18500,
            e20500, e20400, e19200, e19800, e20100,
            MARS, age_head, age_spouse,
            c00100, c04470, c17000, c18300, c20800, c21040, c21060,
            ID_ps, ID_Medical_frt, ID_Medical_frt_add4aged, ID_Medical_HC,
            ID_Casualty_frt_in_pufcsv_year,
            ID_Casualty_frt, ID_Casualty_HC, ID_Miscellaneous_frt,
            ID_Miscellaneous_HC, ID_Charity_crt_all, ID_Charity_crt_noncash,
            ID_prt, ID_crt, ID_StateLocalTax_HC, ID_Charity_frt,
            ID_Charity_HC, ID_InterestPaid_HC, ID_RealEstate_HC):
    """
    ItemDed function: itemized deductions, Form 1040, Schedule A

    Notes
    -----
    Tax Law Parameters:
        ID_ps : Itemized deduction phaseout AGI start (Pease)

        ID_crt : Itemized deduction maximum phaseout
        as a decimal fraction of total itemized deduction (Pease)

        ID_prt : Itemized deduction phaseout rate (Pease)

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
    # Medical
    medical_frt = ID_Medical_frt
    if age_head >= 65 or (MARS == 2 and age_spouse >= 65):
        medical_frt += ID_Medical_frt_add4aged
    c17750 = medical_frt * _posagi
    c17000 = max(0., e17500 - c17750) * (1. - ID_Medical_HC)
    # State and local taxes
    c18300 = ((1. - ID_StateLocalTax_HC) * max(e18400, 0.) +
              (1. - ID_RealEstate_HC) * e18500)
    # Interest paid
    c19200 = e19200 * (1. - ID_InterestPaid_HC)
    # Charity
    lim30 = min(ID_Charity_crt_noncash * _posagi, e20100)
    c19700 = min(ID_Charity_crt_all * _posagi, lim30 + e19800)
    charity_floor = ID_Charity_frt * _posagi  # floor is zero in present law
    c19700 = max(0., c19700 - charity_floor) * (1. - ID_Charity_HC)
    # Casualty
    if e20500 > 0.0:  # add back to e20500 the PUFCSV_YEAR disregard amount
        c37703 = e20500 + ID_Casualty_frt_in_pufcsv_year * _posagi
    else:  # small pre-disregard e20500 values are assumed to be zero
        c37703 = 0.
    c20500 = (max(0., c37703 - ID_Casualty_frt * _posagi) *
              (1. - ID_Casualty_HC))
    # Miscellaneous
    c20400 = e20400
    c20750 = ID_Miscellaneous_frt * _posagi
    c20800 = max(0., c20400 - c20750) * (1. - ID_Miscellaneous_HC)
    # Gross Itemized Deductions
    c21060 = c17000 + c18300 + c19200 + c19700 + c20500 + c20800
    # Limitation on total itemized deductions
    nonlimited = c17000 + c20500
    limitstart = ID_ps[MARS - 1]
    if c21060 > nonlimited and c00100 > limitstart:
        dedmin = ID_crt * (c21060 - nonlimited)
        dedpho = ID_prt * max(0., _posagi - limitstart)
        c21040 = min(dedmin, dedpho)
        c04470 = c21060 - c21040
    else:
        c21040 = 0.
        c04470 = c21060
    return (c17000, c18300, c20800, c21040, c21060, c04470)


@iterate_jit(nopython=True)
def AMED(_fica, e00200, MARS, AMED_thd, _sey, AMED_trt,
         FICA_mc_trt, FICA_ss_trt):
    """
    AMED function: computes additional Medicare Tax as a part of FICA

    Notes
    -----
    Tax Law Parameters:
        AMED_thd : Additional medicare threshold

        AMED_trt : Additional medicare tax rate

        FICA_ss_trt : FICA social security tax rate

        FICA_mc_trt : FICA medicare tax rate

    Taxpayer Charateristics:
        e00200 : Wages and salaries

        _sey : Self-employment income

    Returns
    -------
    _fica : OASDHI payroll tax augmented by the additional Medicare tax, amed

    """
    # ratio of income subject to AMED tax = (1 - 0.5*(FICA_mc_trt+FICA_ss_trt)
    amed = AMED_trt * (max(0., e00200 - AMED_thd[MARS - 1]) +
                       max(0., max(0., _sey) *
                           (1. - 0.5 * (FICA_mc_trt + FICA_ss_trt)) -
                           max(0., AMED_thd[MARS - 1] - e00200)))
    _fica = _fica + amed
    return _fica


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
    # Calculate deduction for dependents
    if DSI == 1:
        c15100 = max(350. + _earned, STD[6])
        c04100 = min(STD[MARS - 1], c15100)
    else:
        c15100 = 0.
        if MIDR == 1:
            c04100 = 0.
        else:
            c04100 = STD[MARS - 1]
    # Calculate extra standard deduction for aged and blind
    _extrastd = blind_head + blind_spouse
    if age_head >= 65:
        _extrastd += 1
    if MARS == 2 and age_spouse >= 65:
        _extrastd += 1
    c15200 = _extrastd * STD_Aged[MARS - 1]
    # Compute the total standard deduction
    _standard = c04100 + c15200
    if (MARS == 3 or MARS == 6) and (MIDR == 1):
        _standard = 0.
    return _standard


@iterate_jit(nopython=True)
def Personal_Credit(c04500, MARS,
                    II_credit, II_credit_ps, II_credit_prt,
                    personal_credit):
    """
    Personal_Credit function: ...
    """
    # full amount as defined in the parameter
    personal_credit = II_credit[MARS - 1]
    # phaseout using taxable income
    if c04500 > II_credit_ps[MARS - 1]:
        credit_phaseout = II_credit_prt * (c04500 - II_credit_ps[MARS - 1])
    else:
        credit_phaseout = 0.
    personal_credit = max(0., personal_credit - credit_phaseout)
    return personal_credit


@iterate_jit(nopython=True)
def TaxInc(c00100, _standard, c21060, c21040, c04500, c04600, c02700,
           _feided, c04800, MARS, _feitax, _taxinc,
           II_rt1, II_rt2, II_rt3, II_rt4, II_rt5, II_rt6, II_rt7, II_rt_xtr,
           II_brk1, II_brk2, II_brk3, II_brk4, II_brk5, II_brk6, II_brk_xtr):
    """
    TaxInc function: ...
    """
    c04500 = max(0., c00100 - max(c21060 - c21040, _standard))
    c04800 = max(0., c04500 - c04600)
    # Some taxpayers iteimize only for AMT, not regular tax
    if c04800 > 0. and _feided > 0.:
        _taxinc = c04800 + c02700
    else:
        _taxinc = c04800
    if c04800 > 0. and _feided > 0.:
        _feitax = Taxer_i(_feided, MARS, II_rt1, II_rt2, II_rt3, II_rt4,
                          II_rt5, II_rt6, II_rt7, II_rt_xtr, II_brk1, II_brk2,
                          II_brk3, II_brk4, II_brk5, II_brk6, II_brk_xtr)
    else:
        _feitax = 0.
    return (c04500, c04800, _taxinc, _feitax, _standard)


@iterate_jit(nopython=True)
def XYZD(_taxinc, c04800, MARS, _xyztax, c05200,
         II_rt1, II_rt2, II_rt3, II_rt4, II_rt5, II_rt6, II_rt7, II_rt_xtr,
         II_brk1, II_brk2, II_brk3, II_brk4, II_brk5, II_brk6, II_brk_xtr):
    """
    XYZD function: ...
    """
    _xyztax = Taxer_i(_taxinc, MARS, II_rt1, II_rt2, II_rt3, II_rt4, II_rt5,
                      II_rt6, II_rt7, II_rt_xtr, II_brk1, II_brk2, II_brk3,
                      II_brk4, II_brk5, II_brk6, II_brk_xtr)
    c05200 = Taxer_i(c04800, MARS, II_rt1, II_rt2, II_rt3, II_rt4, II_rt5,
                     II_rt6, II_rt7, II_rt_xtr, II_brk1, II_brk2, II_brk3,
                     II_brk4, II_brk5, II_brk6, II_brk_xtr)
    return (_xyztax, c05200)


@iterate_jit(nopython=True)
def TaxGains(e00650, c01000, c04800, c23650, p23250, e01100, e58990,
             e24515, e24518, MARS, _taxinc, _xyztax, _feided,
             _feitax, c00650, c05700, _taxbc,
             c24516, c24517, c24520,
             II_rt1, II_rt2, II_rt3, II_rt4, II_rt5, II_rt6, II_rt7, II_rt_xtr,
             II_brk1, II_brk2, II_brk3, II_brk4, II_brk5, II_brk6, II_brk_xtr,
             CG_rt1, CG_rt2, CG_rt3, CG_thd1, CG_thd2):
    """
    TaxGains function: ...
    """
    # pylint: disable=too-many-statements,too-many-branches
    c00650 = e00650
    if c01000 > 0. or c23650 > 0. or p23250 > 0. or e01100 > 0. or e00650 > 0.:
        hasqdivltcg = 1  # has qualified dividends or long-term capital gains
    else:
        hasqdivltcg = 0  # no qualified dividends or long-term capital gains

    if hasqdivltcg == 1:

        # if/else 1
        _dwks5 = max(0., e58990)
        c24505 = max(0., c00650 - _dwks5)
        # gain for tax computation
        if e01100 > 0.:
            c24510 = e01100
        else:
            c24510 = max(0., min(c23650, p23250)) + e01100
        _dwks9 = max(0., c24510 - min(0., e58990))
        c24516 = c24505 + _dwks9

        # if/else 2
        _dwks12 = min(_dwks9, e24515 + e24518)
        c24517 = c24516 - _dwks12
        c24520 = max(0., _taxinc - c24517)
        # tentative TI less schD gain
        c24530 = min(CG_thd1[MARS - 1], _taxinc)

        # if/else 3
        _dwks16 = min(c24520, c24530)
        _dwks17 = max(0., _taxinc - c24516)
        c24540 = max(_dwks16, _dwks17)
        c24534 = c24530 - _dwks16
        lowest_rate_tax = CG_rt1 * c24534
        _dwks21 = min(_taxinc, c24517)
        c24597 = max(0., _dwks21 - c24534)

        # if/else 4
        # income subject to 15% tax
        c24598 = CG_rt2 * c24597  # actual 15% tax
        _dwks25 = min(_dwks9, e24515)
        _dwks26 = c24516 + c24540
        _dwks28 = max(0., _dwks26 - _taxinc)
        c24610 = max(0., _dwks25 - _dwks28)
        c24615 = 0.25 * c24610
        _dwks31 = c24540 + c24534 + c24597 + c24610
        c24550 = max(0., _taxinc - _dwks31)
        c24570 = 0.28 * c24550

        if c24540 > CG_thd2[MARS - 1]:
            addtax = (CG_rt3 - CG_rt2) * c24517
        elif c24540 <= CG_thd2[MARS - 1] and _taxinc > CG_thd2[MARS - 1]:
            addtax = (CG_rt3 - CG_rt2) * min(_dwks21,
                                             _taxinc - CG_thd2[MARS - 1])
        else:
            addtax = 0.

        c24560 = Taxer_i(c24540, MARS, II_rt1, II_rt2, II_rt3, II_rt4, II_rt5,
                         II_rt6, II_rt7, II_rt_xtr, II_brk1, II_brk2, II_brk3,
                         II_brk4, II_brk5, II_brk6, II_brk_xtr)

        tspecial = lowest_rate_tax + c24598 + c24615 + c24570 + c24560 + addtax

        c24580 = min(tspecial, _xyztax)

    else:  # if hasqdivltcg is zero

        c24516 = max(0., min(p23250, c23650)) + e01100
        c24517 = 0.
        c24520 = 0.
        c24580 = _xyztax

    # final calculations done no matter what the value of hasqdivltcg
    if c04800 > 0. and _feided > 0.:
        c05100 = max(0., c24580 - _feitax)
    else:
        c05100 = c24580

    # Form 4972, Lump Sum Distributions
    c05700 = 0.

    _taxbc = c05700 + c05100
    return (c00650, c24516, c24517, c24520, c05700, _taxbc)


@iterate_jit(nopython=True)
def AMTI(e07300, c24517, _standard, f6251, c00100, c18300, _taxbc,
         c04470, c17000, c20800, c21040, c02700, e24515, MARS, _sep,
         c24520, c05700, e62900, e00700, c24516, age_head, _earned,
         cmbtp_itemizer, cmbtp_standard,
         KT_c_Age, AMT_tthd, AMT_thd_MarriedS,
         AMT_em, AMT_prt, AMT_trt1, AMT_trt2,
         AMT_Child_em, AMT_em_ps, AMT_em_pe,
         AMT_CG_thd1, AMT_CG_thd2, AMT_CG_rt1, AMT_CG_rt2, AMT_CG_rt3,
         c05800, c09600, c62100):

    """
    AMTI function: AMT taxable income
    """
    # pylint: disable=too-many-statements,too-many-branches
    c62720 = c24517
    c60260 = e00700
    c62730 = e24515
    if _standard == 0.0:
        if f6251 == 1:
            cmbtp = cmbtp_itemizer
        else:
            cmbtp = 0.
        c62100 = (c00100 - c04470 +
                  max(0., min(c17000, 0.025 * c00100)) +
                  c18300 -
                  c60260 + c20800 - c21040)
        c62100 += cmbtp
    if _standard > 0.0:
        if f6251 == 1:
            cmbtp = cmbtp_standard
        else:
            cmbtp = 0.
        c62100 = c00100 - c60260
        c62100 += cmbtp
    if MARS == 3 or MARS == 6:
        amtsepadd = max(0.,
                        min(AMT_thd_MarriedS, 0.25 * (c62100 - AMT_em_pe)))
    else:
        amtsepadd = 0.
    c62100 = c62100 + amtsepadd
    c62600 = max(0., AMT_em[MARS - 1] - AMT_prt *
                 max(0., c62100 - AMT_em_ps[MARS - 1]))
    if age_head != 0 and age_head < KT_c_Age:
        c62600 = min(c62600, _earned + AMT_Child_em)
    c62700 = max(0., c62100 - c62600)
    if c02700 > 0.:
        alminc = max(0., c62100 - c62600)
        amtfei = (AMT_trt1 * c02700 + AMT_trt2 *
                  max(0., (c02700 - (AMT_tthd / _sep))))
    else:
        alminc = c62700
        amtfei = 0.
    c62780 = (AMT_trt1 * alminc + AMT_trt2 *
              max(0., (alminc - (AMT_tthd / _sep) - amtfei)))
    if f6251 == 1:
        c62900 = e62900
    else:
        c62900 = e07300
    if c24516 == 0.:
        c62740 = c62720 + c62730
    else:
        c62740 = min(max(0., c24516), c62720 + c62730)
    ngamty = max(0., alminc - c62740)
    c62745 = (AMT_trt1 * ngamty +
              AMT_trt2 * max(0., (ngamty - (AMT_tthd / _sep))))
    # Capital Gain for AMT
    tamt2 = 0.
    amt5pc = 0.
    line45 = max(0., AMT_CG_thd1[MARS - 1] - c24520)
    line46 = min(alminc, c62720)
    line47 = min(line45, line46)
    line48 = min(alminc, c62720) - line47
    amt15pc = min(line48, max(0., AMT_CG_thd2[MARS - 1] - c24520 - line45))
    if ngamty != (amt15pc + line47):
        amt20pc = line46 - amt15pc - line47
    else:
        amt20pc = 0.
    if c62740 != 0.:
        amt25pc = max(0., alminc - ngamty - line46)
    else:
        amt25pc = 0.
    c62747 = AMT_CG_rt1 * amt5pc
    c62755 = AMT_CG_rt2 * amt15pc
    c62760 = AMT_CG_rt3 * amt20pc
    c62770 = 0.25 * amt25pc  # tax rate on "Unrecaptured Schedule E Gain"
    tamt2 = c62747 + c62755 + c62760 + c62770  # line62 without 42 being added
    c62800 = min(c62780, c62745 + tamt2 - amtfei)
    c63000 = c62800 - c62900
    c63100 = _taxbc - e07300 - c05700
    c63100 = max(0., c63100)
    c63200 = max(0., c63000 - c63100)
    c09600 = c63200
    c05800 = _taxbc + c63200
    return (c62100, c09600, c05800)


@iterate_jit(nopython=True)
def MUI(c00100, NIIT_thd, MARS, e00300, e00600, c01000, e02000, NIIT_trt,
        NIIT, e26270):
    """
    MUI function: ...
    """
    NIIT = NIIT_trt * min(e00300 + e00600 + max(0., c01000) +
                          max(0., e02000 - e26270),
                          max(0., c00100 - NIIT_thd[MARS - 1]))
    return NIIT


@iterate_jit(nopython=True)
def F2441(MARS, _earned_p, _earned_s, f2441, DCC_c, e32800,
          _exact, c00100, CDCC_ps, CDCC_crt, c05800, e07300, c07180):
    """
    Form 2441 calculation of child & dependent care expense credit, c07180
    """
    c32880 = _earned_p  # earned income of taxpayer
    if MARS == 2:
        c32890 = _earned_s  # earned income of spouse, if present
    else:
        c32890 = _earned_p
    dclim = min(f2441, 2) * DCC_c
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


@iterate_jit(nopython=True)
def NumDep(EIC, c00100, c01000, e00400, MARS, EITC_ps, EITC_MinEligAge, DSI,
           age_head, EITC_MaxEligAge, EITC_ps_MarriedJ, EITC_rt, c59560,
           EITC_c, age_spouse, EITC_prt, e00300, e00600,
           p25470, e27200,
           EITC_InvestIncome_c, _earned, c59660):
    """
    NumDep function: ...
    """
    # pylint: disable=too-many-branches
    preeitc = 0.
    c59560 = _earned
    modagi = c00100 + e00400
    if MARS == 2:
        val_ymax = EITC_ps[EIC] + EITC_ps_MarriedJ[EIC]
    elif MARS == 1 or MARS == 4 or MARS == 5 or MARS == 7:
        val_ymax = EITC_ps[EIC]
    else:
        val_ymax = 0.
    if MARS == 1 or MARS == 4 or MARS == 5 or MARS == 2 or MARS == 7:
        c59660 = min(EITC_rt[EIC] * c59560, EITC_c[EIC])
        preeitc = c59660
    if (MARS != 3 and MARS != 6 and
            (modagi > val_ymax or c59560 > val_ymax)):
        preeitc = max(0., EITC_c[EIC] - EITC_prt[EIC] *
                      (max(0., max(modagi, c59560) - val_ymax)))
        preeitc = min(preeitc, c59660)
    if MARS != 3 and MARS != 6:
        dy = (e00400 + e00300 + e00600 +
              max(0., c01000) + max(0., 0. - p25470) + max(0., e27200))
    else:
        dy = 0.
    if MARS != 3 and MARS != 6 and dy > EITC_InvestIncome_c:
        preeitc = 0.

    if DSI == 1:
        preeitc = 0.

    if EIC == 0:
        # enforce age eligibility rule for those with no EITC-eligible children
        # (assume that an unknown age_* value implies EITC age eligibility)
        # pylint: disable=bad-continuation
        if MARS == 2:
            if (age_head >= EITC_MinEligAge and
                age_head <= EITC_MaxEligAge) or \
               (age_spouse >= EITC_MinEligAge and
                age_spouse <= EITC_MaxEligAge) or \
               age_head == 0 or \
               age_spouse == 0:
                c59660 = preeitc
            else:
                c59660 = 0.
        else:
            if (age_head >= EITC_MinEligAge and
                age_head <= EITC_MaxEligAge) or \
               age_head == 0:
                c59660 = preeitc
            else:
                c59660 = 0.
    else:
        c59660 = preeitc

    if c59660 == 0:
        c59560 = 0.
    return (c59560, c59660)


@iterate_jit(nopython=True)
def ChildTaxCredit(n24, MARS, c00100, _feided, _exact,
                   CTC_c, CTC_ps, CTC_prt, _precrd):
    """
    ChildTaxCredit function: ...
    """
    _precrd = CTC_c * n24
    ctcagi = c00100 + _feided
    if ctcagi > CTC_ps[MARS - 1]:
        excess = ctcagi - CTC_ps[MARS - 1]
        if _exact == 1:
            excess = 1000. * math.ceil(excess / 1000.)
        _precrd = max(0., _precrd - CTC_prt * excess)
    return _precrd


@iterate_jit(nopython=True)
def AmOppCr(p87482, e87487, e87492, e87497, p87521, c87521):
    """
    American Opportunity Credit 2009+; Form 8863

    This function calculates American Opportunity Credit
    for up to four eligible students.
    """
    # Expense should not exceed the cap of $4000.
    c87482 = max(0., min(p87482, 4000.))
    c87487 = max(0., min(e87487, 4000.))
    c87492 = max(0., min(e87492, 4000.))
    c87497 = max(0., min(e87497, 4000.))
    # Credit calculated as 100% of the first $2000 expense plus
    # 25% of amount exceeding $2000.
    if max(0., c87482 - 2000.) == 0.:
        c87483 = c87482
    else:
        c87483 = 2000. + 0.25 * max(0., c87482 - 2000.)
    if max(0., c87487 - 2000.) == 0.:
        c87488 = c87487
    else:
        c87488 = 2000 + 0.25 * max(0., c87487 - 2000)
    if max(0., c87492 - 2000.) == 0.:
        c87493 = c87492
    else:
        c87493 = 2000. + 0.25 * max(0., c87492 - 2000.)
    if max(0., c87497 - 2000.) == 0.:
        c87498 = c87497
    else:
        c87498 = 2000. + 0.25 * max(0., c87497 - 2000.)
    # Sum of credits of all four students.
    c87521 = c87483 + c87488 + c87493 + c87498
    # Return larger of p87521 and c87521.
    if p87521 > c87521:
        c87521 = p87521
    return c87521


@iterate_jit(nopython=True)
def LLC(e87530, LLC_Expense_c, c87550):
    """
    Lifetime Learning Credit; Form 8863

    Notes
    -----
    Tax Law Parameters that are not parameterized:

        0.2 : Lifetime Learning Credit ratio against expense:

    Tax Law Parameters that are parameterized:

        LLC_Expense_c : Lifetime Learning Credit expense limit

    Taxpayer Charateristics:

        e87530 : Lifetime Learning Credit total qualified expenses

    Returns
    -------
        c87550 : Lifetime Learning Credit amount
    """
    c87550 = 0.2 * min(e87530, LLC_Expense_c)
    return c87550


@iterate_jit(nopython=True)
def RefAmOpp(c87521, _num, c00100, c10960, c87668):
    """
    Refundable American Opportunity Credit 2009+; Form 8863

    This function checks the previously calculated American Opportunity Credit
    with the phaseout range and then applies the 0.4 refundable rate.

    Notes
    -----
    Tax Law Parameters that are not parameterized:

        90000 : American Opportunity Credit phaseout income base

        10000 : American Opportunity Credit phaseout income range length

        1/1000 : American Opportunity Credit phaseout rate

        0.4 : American Opportunity Credit refundable rate

    Parameters
    ----------
        c87521 : gross American Opportunity Credit

        _num : number of people filing jointly

        c00100 : AGI

    Returns
    -------
        c10960 : Refundable part of American Opportunity Credit

        c87668 : Nonrefundable part of American Opportunity Credit
    """
    if c87521 > 0:
        c87658 = max(0., 90000. * _num - c00100)
        c87660 = 10000. * _num
        c87662 = 1000. * min(1., c87658 / c87660)
        c87664 = c87662 * c87521 / 1000.
        c10960 = 0.4 * c87664
        c87668 = c87664 - c10960
    else:
        c10960 = 0.
        c87668 = 0.
    return (c10960, c87668)


@iterate_jit(nopython=True)
def SchR(_calc_schR, age_head, age_spouse, MARS, c00100,
         c05800, e07300, c07180, e02400, c02500, e01500, e01700,
         c07200):
    """
    Calculate Schedule R credit for the elderly and the disabled, c07200
    """
    if _calc_schR and (age_head >= 65 or (MARS == 2 and age_spouse >= 65)):
        # calculate credit assuming nobody is disabled
        # (note that all Schedule R policy parameters are hard-coded)
        # Part I and first line in Part III
        if MARS == 2:
            if age_head >= 65 and age_spouse >= 65:
                c28300 = 7500.
            else:
                c28300 = 5000.
        elif MARS == 3:
            c28300 = 3750.
        elif MARS == 1 or MARS == 4:
            c28300 = 5000.
        else:
            c28300 = 0.
        # nontaxable OASDI benefit plus nontaxable pension benefits
        c28400 = max(0., (e02400 - c02500) + (e01500 - e01700))
        # one-half of adjusted AGI
        if MARS == 2:
            c28500 = max(0., c00100 - 10000.)
        elif MARS == 3:
            c28500 = max(0., c00100 - 5000.)
        elif MARS == 1 or MARS == 4:
            c28500 = max(0., c00100 - 7500.)
        else:
            c28500 = 0.
        c28600 = 0.5 * c28500
        # compute credit amount, c07200
        c28700 = c28400 + c28600
        c28800 = max(0., c28300 - c28700)
        c07200 = min(0.15 * c28800,
                     max(0., (c05800 - e07300 - c07180)))
    else:  # if not calculating Schedule R credit
        c07200 = 0.
    return c07200


@iterate_jit(nopython=True)
def NonEdCr(c87550, MARS, ETC_pe_Single, ETC_pe_Married, c00100, _num,
            c07180, c07230,
            e07600, e07240, e07260, e07300,
            c05800, _precrd, c87668, c07200,
            c07220, c07240, c07300, c07600, _avail):
    """
    NonEdCr function: ...
    """
    # Nonrefundable Education Credits
    # Form 8863 Tentative Education Credits
    c87560 = c87550
    # Phase Out
    if MARS == 2:
        c87570 = ETC_pe_Married * 1000.
    else:
        c87570 = ETC_pe_Single * 1000.
    c87580 = c00100
    c87590 = max(0., c87570 - c87580)
    c87600 = 10000. * _num
    c87610 = min(1., c87590 / c87600)
    c87620 = c87560 * c87610
    _xlin4 = max(0., c05800 - (e07300 + c07180 + c07200))
    _xlin5 = min(c87620, _xlin4)
    _xlin9 = max(0., c05800 - (e07300 + c07180 + c07200 + _xlin5))
    _xlin10 = min(c87668, _xlin9)
    c87680 = _xlin5 + _xlin10
    c07230 = c87680
    ctc1 = c07180 + c07200 + c07230
    ctc2 = e07240 + e07260 + e07300
    ctctax = c05800 - ctc1 - ctc2
    c07220 = min(_precrd, max(0., ctctax))
    # lt tax owed
    _avail = c05800
    c07180 = min(c07180, _avail)
    _avail = _avail - c07180
    c07200 = min(c07200, _avail)
    _avail = _avail - c07200
    c07300 = min(e07300, _avail)
    _avail = _avail - c07300
    c07230 = min(c07230, _avail)
    _avail = _avail - c07230
    c07240 = min(e07240, _avail)
    _avail = _avail - c07240
    c07260 = min(e07260, _avail)
    _avail = _avail - c07260
    c07600 = min(e07600, _avail)
    _avail = _avail - c07600
    c07220 = min(c07220, _avail)
    _avail = _avail - c07220
    # Allocate credits to tax in order on the tax form
    return (c07300, c07600, c07240, c07220, c07230, _avail)


@iterate_jit(nopython=True)
def AddCTC(n24, _precrd, _earned, c07220, _fica_was,
           ACTC_Income_thd, ACTC_rt, ACTC_ChildNum, ALD_SelfEmploymentTax_HC,
           c03260, e09800, c59660, e11200, c11070):

    """
    AddCTC function: calculates Additional Child Tax Credit
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
    # Part I of 2005 form 8812
    if n24 > 0:
        c82925 = _precrd
        c82930 = c07220
        c82935 = c82925 - c82930
        # CTC not applied to tax
        c82880 = max(0., _earned)
        c82885 = max(0., c82880 - ACTC_Income_thd)
        c82890 = ACTC_rt * c82885
    # Part II of 2005 form 8812
    if n24 >= ACTC_ChildNum and c82890 < c82935:
        c82900 = 0.5 * _fica_was
        c82905 = (1. - ALD_SelfEmploymentTax_HC) * c03260 + e09800
        c82910 = c82900 + c82905
        c82915 = c59660 + e11200
        c82920 = max(0., c82910 - c82915)
        c82937 = max(c82890, c82920)
    # Part II of 2005 form 8812
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
def F5405(e11580, c11580):
    """
    Form 5405, First-Time Homebuyer Credit
    """
    c11580 = e11580
    return c11580


@iterate_jit(nopython=True)
def C1040(e07400, c07200, c07220, c07230, c07300, c07240,
          e07260, c07600, p08000, c05800, e09900, c09400, e09800,
          e09700, c07180, NIIT, _othertax, c07100, c09200):
    """
    C1040 function: ...
    """
    # Credits 1040 line 48
    c07100 = (c07180 + c07200 + c07600 + c07300 + e07400 + c07220 + p08000 +
              c07230 + c07240 + e07260)
    c07100 = min(c07100, c05800)
    # Tax After credits 1040 line 52
    c08795 = max(0., c05800 - c07100)
    # Tax before refundable credits
    _othertax = e09900 + c09400 + e09800 + NIIT
    c09200 = _othertax + c08795
    c09200 += e09700  # assuming year tax year is after 2009
    return (c07100, c09200, _othertax)


@iterate_jit(nopython=True)
def DEITC(c59660, c07100, c08800, c05800, _avail, _othertax):
    """
    DEITC function: decomposition of EITC
    """
    c59680 = min(c59660, _avail)
    _avail = max(0., _avail - c59680) + _othertax
    c07150 = min(c07100 + c59680, c05800)
    c08800 = c05800 - c07150
    return (c08800, _avail)


@iterate_jit(nopython=True)
def IITAX(c09200, c59660, c11070, c10960, _eitc, c11580,
          _fica, personal_credit, n24, _iitax, _combined, _refund,
          CTC_additional, CTC_additional_ps, CTC_additional_prt, c00100,
          _sep, MARS):
    """
    IITAX function: ...
    """
    _refund = c59660 + c11070 + c10960 + c11580 + personal_credit
    _iitax = c09200 - _refund
    _combined = _iitax + _fica
    potential_add_CTC = max(0., min(_combined, CTC_additional * n24))
    phaseout = (c00100 -
                CTC_additional_ps[MARS - 1]) * (CTC_additional_prt / _sep)
    final_add_CTC = max(0., potential_add_CTC - max(0., phaseout))

    _iitax = _iitax - final_add_CTC
    # updated combined tax liabilities after applying the credit
    _combined = _iitax + _fica
    _refund = _refund + final_add_CTC
    _eitc = c59660
    return (_eitc, _refund, _iitax, _combined)


@jit(nopython=True)
def Taxer_i(inc_in, MARS,
            II_rt1, II_rt2, II_rt3, II_rt4, II_rt5, II_rt6, II_rt7, II_rt_xtr,
            II_brk1, II_brk2, II_brk3, II_brk4, II_brk5, II_brk6, II_brk_xtr):
    """
    Taxer_i function: ...
    """
    return (II_rt1 * min(inc_in, II_brk1[MARS - 1]) + II_rt2 *
            min(II_brk2[MARS - 1] - II_brk1[MARS - 1],
                max(0., inc_in - II_brk1[MARS - 1])) + II_rt3 *
            min(II_brk3[MARS - 1] - II_brk2[MARS - 1],
                max(0., inc_in - II_brk2[MARS - 1])) + II_rt4 *
            min(II_brk4[MARS - 1] - II_brk3[MARS - 1],
                max(0., inc_in - II_brk3[MARS - 1])) + II_rt5 *
            min(II_brk5[MARS - 1] - II_brk4[MARS - 1],
                max(0., inc_in - II_brk4[MARS - 1])) + II_rt6 *
            min(II_brk6[MARS - 1] - II_brk5[MARS - 1],
                max(0., inc_in - II_brk5[MARS - 1])) + II_rt7 *
            min(II_brk7[MARS - 1] - II_brk6[MARS - 1],
                max(0., inc_in - II_brk6[MARS - 1])) + II_rt_xtr *
            max(0., inc_in - II_brk_xtr[MARS - 1]))


@iterate_jit(nopython=True)
def ExpandIncome(_fica_was, e02400, c02500, c00100, e00400, _expanded_income):
    """
    ExpandIncome function: calculates and returns _expanded_income.

    Note: if behavioral responses to a policy reform are specified, then be
    sure this function is called after the behavioral responses are calculated.
    """
    employer_share_fica = 0.5 * _fica_was
    non_taxable_ss_benefits = e02400 - c02500
    _expanded_income = (c00100 +  # adjusted gross income
                        e00400 +  # non-taxable interest income
                        non_taxable_ss_benefits +
                        employer_share_fica)
    return _expanded_income


def BenefitSurtax(calc):
    """
    BenefitSurtax function: computes itemized-deduction-benefit surtax and
    adds the surtax amount to income tax and combined tax liabilities.
    """
    if calc.policy.ID_BenefitSurtax_crt != 1.:
        # compute income tax liability with no itemized deductions allowed for
        # the types of itemized deductions covered under the BenefitSurtax
        no_ID_calc = copy.deepcopy(calc)
        if calc.policy.ID_BenefitSurtax_Switch[0]:
            no_ID_calc.policy.ID_Medical_HC = 1.
        if calc.policy.ID_BenefitSurtax_Switch[1]:
            no_ID_calc.policy.ID_StateLocalTax_HC = 1.
        if calc.policy.ID_BenefitSurtax_Switch[2]:
            no_ID_calc.policy.ID_RealEstate_HC = 1.
        if calc.policy.ID_BenefitSurtax_Switch[3]:
            no_ID_calc.policy.ID_Casualty_HC = 1.
        if calc.policy.ID_BenefitSurtax_Switch[4]:
            no_ID_calc.policy.ID_Miscellaneous_HC = 1.
        if calc.policy.ID_BenefitSurtax_Switch[5]:
            no_ID_calc.policy.ID_InterestPaid_HC = 1.
        if calc.policy.ID_BenefitSurtax_Switch[6]:
            no_ID_calc.policy.ID_Charity_HC = 1.
        no_ID_calc.calc_one_year()
        # compute surtax amount and add to income and combined taxes
        # pylint: disable=protected-access
        benefit_amount = np.where(
            no_ID_calc.records._iitax - calc.records._iitax > 0.,
            no_ID_calc.records._iitax - calc.records._iitax, 0.)
        benefit_deduction = (calc.policy.ID_BenefitSurtax_crt *
                             calc.records.c00100)
        calc.records._surtax[:] = calc.policy.ID_BenefitSurtax_trt * np.where(
            benefit_amount > benefit_deduction,
            benefit_amount - benefit_deduction, 0.)
        calc.records._iitax += calc.records._surtax
        calc.records._combined += calc.records._surtax
