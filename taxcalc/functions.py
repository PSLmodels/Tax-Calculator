import pandas as pd
from pandas import DataFrame
import math
import numpy as np
from .utils import *

def FilingStatus(pm, pf):
    # Filing based on marital status
    # TODO: get rid of _txp in tests
    pf._sep = filing_status(pf.MARS)
    return DataFrame(data=pf._sep,
                     columns=['_sep', ])

@vectorize('int64(int64)', nopython=True)
def filing_status(MARS):
    if MARS == 3 or MARS == 6:
        return 2
    return 1


def Adj(pm, pf):
    # Adjustments
    pf._feided = feided_vec(pf.e35300_0, pf.e35600_0, pf.e35910_0)  # Form 2555

    pf.c02900 = (pf.e03150 + pf.e03210 + pf.e03600 + pf.e03260 + pf.e03270 + pf.e03300
              + pf.e03400 + pf.e03500 + pf.e03280 + pf.e03900 + pf.e04000 + pf.e03700
              + pf.e03220 + pf.e03230 + pf.e03240 + pf.e03290)

    return DataFrame(data=np.column_stack((pf._feided, pf.c02900)),
                     columns=['_feided', 'c02900'])

@vectorize('float64(float64, float64, float64)', nopython=True)
def feided_vec(e35300_0, e35600_0, e35910_0):
    return max(e35300_0, e35600_0 + e35910_0)


def CapGains(pm, pf):
    # Capital Gains
    pf.c23650 = pf.e23250 + pf.e22250 + pf.e23660
    pf.c01000 = np.maximum(-3000 / pf._sep, pf.c23650)
    pf.c02700 = np.minimum(pf._feided, pm.feimax * pf.f2555)
    pf._ymod1 = (pf.e00200 + pf.e00300 + pf.e00600
            + pf.e00700 + pf.e00800 + pf.e00900
            + pf.c01000 + pf.e01100 + pf.e01200
            + pf.e01400 + pf.e01700 + pf.e02000
            + pf.e02100 + pf.e02300 + pf.e02600
            + pf.e02610 + pf.e02800 - pf.e02540)
    pf._ymod2 = pf.e00400 + (0.50 * pf.e02400) - pf.c02900
    pf._ymod3 = pf.e03210 + pf.e03230 + pf.e03240 + pf.e02615
    pf._ymod = pf._ymod1 + pf._ymod2 + pf._ymod3

    return DataFrame(data=np.column_stack((pf.c23650, pf.c01000, pf.c02700, pf._ymod1,
                                           pf._ymod2, pf._ymod3, pf._ymod)),
                     columns=['c23650', 'c01000', 'c02700', '_ymod1', '_ymod2',
                               '_ymod3', '_ymod'])


def SSBenefits(pm, pf):
    # Social Security Benefit Taxation
    SSBenefits_calc(pf.SSIND, pf.MARS, pf.e02500, pf._ymod, pf.e02400,
                    pm._ssb50, pm._ssb85, pf.c02500)

    return DataFrame(data=np.column_stack((pf.c02500, pf.e02500)),
                     columns=['c02500', 'e02500'])


@jit('void(float64[:], int64[:], int64[:], float64[:], int64[:], int64[:], int64[:], float64[:])', nopython=True)
def SSBenefits_calc(SSIND, MARS, e02500, _ymod, e02400, _ssb50, _ssb85, c02500):

    for i in range(0, MARS.shape[0]):
        if SSIND[i] !=0 or MARS[i] == 3 or MARS[i] == 6:
            c02500[i] = e02500[i]
        elif _ymod[i] < _ssb50[MARS[i]-1]:
            c02500[i] = 0
        elif _ymod[i] >= _ssb50[MARS[i]-1] and _ymod[i] < _ssb85[MARS[i]-1]:
            c02500[i] = 0.5 * np.minimum(_ymod[i] - _ssb50[MARS[i]-1], e02400[i])
        else:
            c02500[i] = np.minimum(0.85 * (_ymod[i] - _ssb85[MARS[i]-1]) +
                        0.50 * np.minimum(e02400[i], _ssb85[MARS[i]-1] -
                        _ssb50[MARS[i]-1]), 0.85 * e02400[i])



def AGI(pm, pf):
    # Adjusted Gross Income
    pf.c02650 = pf._ymod1 + pf.c02500 - pf.c02700 + pf.e02615  # Gross Income

    pf.c00100 = pf.c02650 - pf.c02900
    pf._agierr = pf.e00100 - pf.c00100  # Adjusted Gross Income
    pf.c00100 = conditional_agi(pf._fixup, pf.c00100, pf._agierr)

    pf._posagi = np.maximum(pf.c00100, 0)
    pf._ywossbe = pf.e00100 - pf.e02500
    pf._ywossbc = pf.c00100 - pf.c02500

    pf._prexmp = pf.XTOT * pm.amex
    # Personal Exemptions (_phaseout smoothed)

    _dispc_numer = 0.02 * (pf._posagi - pm.exmpb[pf.MARS - 1])
    _dispc_denom = (2500 / pf._sep)
    _dispc = np.minimum(1, np.maximum(0, _dispc_numer / _dispc_denom ))

    pf.c04600 = pf._prexmp * (1 - _dispc)

    return DataFrame(data=np.column_stack((pf.c02650, pf.c00100, pf._agierr,
                                           pf._posagi, pf._ywossbe,
                                           pf._ywossbc, pf._prexmp, pf.c04600)),
                     columns=['c02650', 'c00100', '_agierr', '_posagi',
                              '_ywossbe', '_ywossbc', '_prexmp', 'c04600'])


@vectorize('float64(float64, float64, float64)', nopython=True)
def conditional_agi(fixup, c00100, agierr):
    if fixup >= 1:
        return c00100 + agierr
    return c00100


def ItemDed(pm, pf, puf=True):

    # Medical #
    c17750 = 0.075 * pf._posagi
    pf.c17000 = np.maximum(0, pf.e17500 - c17750)

    # State and Local Income Tax, or Sales Tax #
    _sit1 = np.maximum(pf.e18400, pf.e18425)
    pf._sit = np.maximum(_sit1, 0)
    _statax = np.maximum(pf._sit, pf.e18450)

    # Other Taxes #
    pf.c18300 = _statax + pf.e18500 + pf.e18800 + pf.e18900

    # Casulty #
    c37703 = casulty(pf.e20500, pf.e20500, pf._posagi)
    c20500 = casulty(pf.e20500, c37703, pf._posagi)

    # Miscellaneous #
    c20750 = 0.02 * pf._posagi
    if puf == True:
        c20400 = pf.e20400
        c19200 = pf.e19200
    else:
        c20400 = pf.e20550 + pf.e20600 + pf.e20950
        c19200 = pf.e19500 + pf.e19570 + pf.e19400 + pf.e19550
    pf.c20800 = np.maximum(0, c20400 - c20750)

    # Charity (assumes carryover is non-cash)
    c19700 = charity(pf.e19800, pf.e20100, pf.e20200, pf._posagi)
    # temporary fix!??

    # Gross Itemized Deductions #
    pf.c21060 = (pf.e20900 + pf.c17000 + pf.c18300 + c19200 + c19700
              + c20500 + pf.c20800 + pf.e21000 + pf.e21010)

    # Itemized Deduction Limitation
    phase2 = pm.phase2[pf.MARS-1] # Eventually, get rid of _phase2

    _nonlimited = pf.c17000 + c20500 + pf.e19570 + pf.e21010 + pf.e20900
    _limitratio = phase2/pf._sep

    pf.c21040 = item_ded_limit(pf.c21060, pf.c00100, _nonlimited, _limitratio, pf._posagi)
    c04470 = item_ded_vec(pf.c21060, pf.c00100, _nonlimited, _limitratio, pf.c21040)

    outputs = (c17750, pf.c17000, _sit1, pf._sit, _statax, pf.c18300, c37703, c20500,
               c20750, c20400, c19200, pf.c20800, c19700, pf.c21060,
               phase2, _nonlimited, _limitratio, c04470, pf.c21040)

    header= ['c17750', 'c17000', '_sit1', '_sit', '_statax', 'c18300', 'c37703',
             'c20500', 'c20750', 'c20400', 'c19200', 'c20800', 'c19700',
             'c21060', '_phase2',
             '_nonlimited', '_limitratio', 'c04470', 'c21040']

    return DataFrame(data=np.column_stack(outputs), columns=header)


@vectorize('float64(float64, float64, float64)', nopython=True)
def casulty(controller_var, output_var, posagi):
    if controller_var > 0:
        return output_var + 0.1 * posagi
    return 0


@vectorize('float64(float64, float64, float64, float64)', nopython=True)
def charity(e19800, e20100, e20200, posagi):
    base_charity = e19800 + e20100 + e20200
    if base_charity <= 0.2 * posagi:
        return base_charity
    else:
        lim50 = min(0.50 * posagi, e19800)
        lim30 = min(0.30 * posagi, e20100 + e20200)
        return min(0.5 * posagi, lim30 + lim50)


@vectorize('float64(float64, float64, float64, float64, float64)')
def item_ded_vec(c21060, c00100, nonlimited, limitratio, c21040):
    if c21060 > nonlimited and c00100 > limitratio:
        return c21060 - c21040
    return c21060


@vectorize('float64(float64, float64, float64, float64, float64)', nopython=True)
def item_ded_limit(c21060, c00100, nonlimited, limitratio, posagi):
    if c21060 > nonlimited and c00100 > limitratio:
        dedmin = 0.8 * (c21060 - nonlimited)
        dedpho = 0.03 * max(0, posagi - limitratio)
        return min(dedmin, dedpho)
    return 0.0


def EI_FICA(pm, pf):
    pf._sey = pf.e00900 + pf.e02100
    _fica = np.maximum(0, .153 * np.minimum(pm.ssmax,
                                            pf.e00200 + np.maximum(0, pf._sey) * 0.9235))
    pf._setax = np.maximum(0, _fica - 0.153 * pf.e00200)
    _seyoff = np.where(pf._setax <= 14204, 0.5751 * pf._setax, 0.5 * pf._setax + 10067)

    c11055 = pf.e11055

    pf._earned = np.maximum(0, pf.e00200 + pf.e00250 + pf.e11055 + pf.e30100 + pf._sey - _seyoff)

    outputs = (pf._sey, _fica, pf._setax, _seyoff, c11055, pf._earned)
    header = ['_sey', '_fica', '_setax', '_seyoff', 'c11055', '_earned']

    return DataFrame(data=np.column_stack(outputs), columns=header)


def StdDed(pm, pf):
    # Standard Deduction with Aged, Sched L and Real Estate #

    c15100 = np.zeros((pf.dim,))
    StdDed_c15100(pf._earned, pf.DSI, pm.stded, c15100)

    _compitem = np.where(np.logical_and(pf.e04470 > 0, pf.e04470 < pm.stded[pf.MARS-1]), 1, 0)

    c04100 = np.zeros((pf.dim,))
    StdDed_c04100(pf.DSI, pf.MARS, c15100, pf.MIdR, pf._earned, _compitem,
                  pm.stded, c04100)

    c04100 = c04100 + pf.e15360
    _numextra = pf.AGEP + pf.AGES + pf.PBI + pf.SBI
    _txpyers = StdDed_txpyers(pf.MARS)

    c04200 = np.zeros((pf.dim,))
    StdDed_c04200(c04200, pf.MARS, pf.e04200, _numextra, pf._exact, _txpyers, pm.aged)

    c15200 = c04200

    pf._standard = StdDed_standard(pf.MARS, c04100, pf.c04470, c04200)

    _othded = np.where(pf.FDED == 1, pf.e04470 - pf.c04470, 0)
    c04100 = np.where(pf.FDED == 1, 0, c04100)
    c04200 = np.where(pf.FDED == 1, 0, c04200)
    pf._standard = np.where(pf.FDED == 1, 0, pf._standard)

    c04500 = pf.c00100 - np.maximum(pf.c21060 - pf.c21040,
                                 np.maximum(c04100, pf._standard + pf.e37717))
    pf.c04800 = np.maximum(0, c04500 - pf.c04600 - pf.e04805)

    pf.c60000 = np.where(pf._standard > 0, pf.c00100, c04500)
    pf.c60000 = pf.c60000 - pf.e04805

    # Some taxpayers iteimize only for AMT, not regular tax
    _amtstd = np.zeros((pf.dim,))
    pf.c60000 = StdDed_c60000(pf.e04470, pf.t04470, _amtstd, pf.f6251, pf._exact,
                           pf.c00100, pf.c60000)
    pf._taxinc = StdDed_taxinc(pf.c04800, pf._feided, pf.c02700)

    _oldfei = np.zeros((pf.dim,))

    taxer1 = Taxer(inc_in=pf._feided, inc_out=pf._feitax, MARS=pf.MARS, pm=pm, pf=pf)
    pf._feitax = StdDed_feitax(pf.c04800, pf._feided, taxer1, pf._feitax)

    taxer2 = Taxer(inc_in=pf.c04800, inc_out=_oldfei, MARS=pf.MARS, pm=pm, pf=pf)
    _oldfei = StdDed_oldfei(pf.c04800, pf._feided, taxer2, _oldfei)

    SDoutputs = (c15100, _numextra, _txpyers, c15200,
                 _othded, c04100, c04200, pf._standard, c04500,
                  pf.c04800, pf.c60000, _amtstd, pf._taxinc, pf._feitax, _oldfei)

    header = ['c15100', '_numextra', '_txpyers', 'c15200',
              '_othded', 'c04100', 'c04200', '_standard',
              'c04500', 'c04800', 'c60000', '_amtstd', '_taxinc', '_feitax',
               '_oldfei']

    return DataFrame(data=np.column_stack(SDoutputs),
                     columns=header)

@jit("void(float64[:], int64[:], int64[:], float64[:])", nopython=True)
def StdDed_c15100(_earned, DSI, stded, c15100):
    for i in range(0, _earned.shape[0]):
        if DSI[i] == 1:
            c15100[i] = np.maximum(300 + _earned[i], stded[6])
        else:
            c15100[i] = 0


@jit("void(int64[:], int64[:], float64[:], int64[:], float64[:], int64[:], int64[:], float64[:])", nopython=True)
def StdDed_c04100(DSI, MARS, c15100, MIdR, _earned, _compitem, stded, c04100):
    for i in range(0, MARS.shape[0]):
        if (DSI[i] == 1):
            c04100[i] = np.minimum( stded[MARS[i]-1], c15100[i])
        elif _compitem[i] == 1 or (3 <= MARS[i] and MARS[i] <=6 and MIdR[i] == 1):
            c04100[i] = 0
        else:
            c04100[i] = stded[MARS[i] - 1]




@vectorize(["int64(int64)"], nopython=True)
def StdDed_txpyers(MARS):
    if MARS == 2 or MARS == 3:
        return 2
    else:
        return 1


@jit("void(float64[:], int64[:], float64[:], float64[:], float64[:], int64[:], int64[:])", nopython=True)
def StdDed_c04200(c04200, MARS, e04200, _numextra, _exact, _txpyers, aged):
    for i in range(MARS.shape[0]):
        if _exact[i] == 1 and MARS[i] == 3 or MARS[i] == 5:
            c04200[i] = e04200[i]
        else:
            c04200[i] = _numextra[i] * aged[_txpyers[i] - 1]


@vectorize(["float64(int64, float64, float64, float64)"], nopython=True)
def StdDed_standard(MARS, c04100, c04470, c04200):
    if (MARS == 3 or MARS == 6) and (c04470 > 0):
        return 0
    else:
        return c04100 + c04200


@vectorize(["float64(float64, float64, float64, int64, float64, float64, float64)"], nopython=True)
def StdDed_c60000(e04470, t04470, _amtstd, f6251, _exact, c00100, c60000):
    if (e04470 == 0 and (t04470 > _amtstd) and f6251 == 1 and _exact == 1):
        return c00100 - t04470
    else:
        return c60000


@vectorize(["float64(float64, float64, float64)"], nopython=True)
def StdDed_taxinc(c04800, _feided, c02700):

    if (c04800 > 0 and _feided > 0):
        return c04800 + c02700
    else:
        return c04800


@vectorize(["float64(float64, float64, float64, float64)"], nopython=True)
def StdDed_feitax(c04800, _feided, taxer, _feitax):
    if (c04800 > 0 and _feided > 0):
        return taxer
    else:
        return _feitax

@vectorize(["float64(float64, float64, float64, float64)"], nopython=True)
def StdDed_oldfei(c04800, _feided, taxer, _oldfei):
    if (c04800 > 0 and _feided > 0):
        return taxer
    else:
        return _oldfei


def Taxer(inc_in, inc_out, MARS, pm, pf):
    low = np.where(inc_in < 3000, 1, 0)
    med = np.where(np.logical_and(inc_in >= 3000, inc_in < 100000), 1, 0)

    _a1 = inc_in * 0.01
    _a2 = np.floor(_a1)
    _a3 = _a2 * 100
    _a4 = (_a1 - _a2) * 100

    _a5 = np.zeros((pf.dim,))
    _a5 = np.where(np.logical_and(low == 1, _a4 < 25), 13, _a5)
    _a5 = np.where(
        np.logical_and(low == 1, np.logical_and(_a4 >= 25, _a4 < 50)), 38, _a5)
    _a5 = np.where(
        np.logical_and(low == 1, np.logical_and(_a4 >= 50, _a4 < 75)), 63, _a5)
    _a5 = np.where(np.logical_and(low == 1, _a4 >= 75), 88, _a5)

    _a5 = np.where(np.logical_and(med == 1, _a4 < 50), 25, _a5)
    _a5 = np.where(np.logical_and(med == 1, _a4 >= 50), 75, _a5)

    _a5 = np.where(inc_in == 0, 0, _a5)

    _a6 = np.where(np.logical_or(low == 1, med == 1), _a3 + _a5, inc_in)

    _a6 = inc_in

    inc_out = (pm.rt1 * np.minimum(_a6, pm.brk1[MARS - 1])
               + pm.rt2
               * np.minimum(pm.brk2[MARS - 1] - pm.brk1[MARS - 1],
                            np.maximum(0., _a6 - pm.brk1[MARS - 1]))
               + pm.rt3
               * np.minimum(pm.brk3[MARS - 1] - pm.brk2[MARS - 1],
                            np.maximum(0., _a6 - pm.brk2[MARS - 1]))
               + pm.rt4
               * np.minimum(pm.brk4[MARS - 1] - pm.brk3[MARS - 1],
                            np.maximum(0., _a6 - pm.brk3[MARS - 1]))
               + pm.rt5
               * np.minimum(pm.brk5[MARS - 1] - pm.brk4[MARS - 1],
                            np.maximum(0., _a6 - pm.brk4[MARS - 1]))
               + pm.rt6
               * np.minimum(pm.brk6[MARS - 1] - pm.brk5[MARS - 1],
                            np.maximum(0., _a6 - pm.brk5[MARS - 1]))
               + pm.rt7 * np.maximum(0., _a6 - pm.brk6[MARS - 1]))

    return inc_out


def XYZD(pm, pf):

    c05200 = np.zeros((pf.dim,))
    pf._xyztax = Taxer(inc_in=pf._taxinc, inc_out=pf._xyztax, MARS=pf.MARS, pm=pm, pf=pf)
    c05200 = Taxer(inc_in=pf.c04800, inc_out=c05200, MARS=pf.MARS, pm=pm, pf=pf)

    return DataFrame(data=np.column_stack((pf._xyztax, c05200)),
                     columns=['_xyztax', 'c05200'])


def NonGain(pm, pf):
    _cglong = np.minimum(pf.c23650, pf.e23250) + pf.e01100
    _noncg = np.zeros((pf.dim,))

    return DataFrame(data=np.column_stack((_cglong, _noncg)),
                     columns=['_cglong', '_noncg'])


def TaxGains(pm, pf):
    c24530 = np.zeros((pf.dim,))
    c24540 = np.zeros((pf.dim,))
    _dwks16 = np.zeros((pf.dim,))

    _hasgain = np.zeros((pf.dim,))

    _hasgain = np.where(np.logical_or(pf.e01000 > 0, pf.c23650 > 0), 1, _hasgain)
    _hasgain = np.where(np.logical_or(pf.e23250 > 0, pf.e01100 > 0), 1, _hasgain)
    _hasgain = np.where(pf.e00650 > 0, 1, _hasgain)

    _dwks5 = np.where(
        np.logical_and(pf._taxinc > 0, _hasgain == 1), np.maximum(0, pf.e58990 - pf.e58980), 0)

    c00650 = pf.e00650
    c24505 = np.where(
        np.logical_and(pf._taxinc > 0, _hasgain == 1), np.maximum(0, pf.c00650 - _dwks5), 0)
    c24510 = np.where(np.logical_and(pf._taxinc > 0, _hasgain == 1), np.maximum(
        0, np.minimum(pf.c23650, pf.e23250)) + pf.e01100, 0)
    # gain for tax computation

    c24510 = np.where(np.logical_and(
        pf._taxinc > 0, np.logical_and(_hasgain == 1, pf.e01100 > 0)), pf.e01100, c24510)
    # from app f 2008 drf

    _dwks9 = np.where(np.logical_and(pf._taxinc > 0, _hasgain == 1), np.maximum(
        0, c24510 - np.minimum(pf.e58990, pf.e58980)), 0)
    # e24516 gain less invest y

    pf.c24516 = np.maximum(0, np.minimum(pf.e23250, pf.c23650)) + pf.e01100
    c24580 = pf._xyztax

    pf.c24516 = np.where(
        np.logical_and(pf._taxinc > 0, _hasgain == 1), c24505 + _dwks9, pf.c24516)
    _dwks12 = np.where(np.logical_and(
        pf._taxinc > 0, _hasgain == 1), np.minimum(_dwks9, pf.e24515 + pf.e24518), 0)
    pf.c24517 = np.where(
        np.logical_and(pf._taxinc > 0, _hasgain == 1), pf.c24516 - _dwks12, 0)
    # gain less 25% and 28%

    pf.c24520 = np.where(
        np.logical_and(pf._taxinc > 0, _hasgain == 1), np.maximum(0, pf._taxinc - pf.c24517), 0)
    # tentative TI less schD gain

    c24530 = np.where(np.logical_and(pf._taxinc > 0, _hasgain == 1), np.minimum(
        pm.brk2[pf.MARS - 1], pf._taxinc), 0)
    # minimum TI for bracket

    _dwks16 = np.where(
        np.logical_and(pf._taxinc > 0, _hasgain == 1), np.minimum(pf.c24520, c24530), 0)
    _dwks17 = np.where(
        np.logical_and(pf._taxinc > 0, _hasgain == 1), np.maximum(0, pf._taxinc - pf.c24516), 0)
    c24540 = np.where(
        np.logical_and(pf._taxinc > 0, _hasgain == 1), np.maximum(_dwks16, _dwks17), 0)

    c24534 = np.where(
        np.logical_and(pf._taxinc > 0, _hasgain == 1), c24530 - _dwks16, 0)
    _dwks21 = np.where(
        np.logical_and(pf._taxinc > 0, _hasgain == 1), np.minimum(pf._taxinc, pf.c24517), 0)
    c24597 = np.where(
        np.logical_and(pf._taxinc > 0, _hasgain == 1), np.maximum(0, _dwks21 - c24534), 0)
    # income subject to 15% tax

    c24598 = 0.15 * c24597  # actual 15% tax

    _dwks25 = np.where(
        np.logical_and(pf._taxinc > 0, _hasgain == 1), np.minimum(_dwks9, pf.e24515), 0)
    _dwks26 = np.where(
        np.logical_and(pf._taxinc > 0, _hasgain == 1), pf.c24516 + c24540, 0)
    _dwks28 = np.where(
        np.logical_and(pf._taxinc > 0, _hasgain == 1), np.maximum(0, _dwks26 - pf._taxinc), 0)
    c24610 = np.where(
        np.logical_and(pf._taxinc > 0, _hasgain == 1), np.maximum(0, _dwks25 - _dwks28), 0)
    c24615 = np.where(
        np.logical_and(pf._taxinc > 0, _hasgain == 1), 0.25 * c24610, 0)
    _dwks31 = np.where(np.logical_and(
        pf._taxinc > 0, _hasgain == 1), c24540 + c24534 + c24597 + c24610, 0)
    c24550 = np.where(
        np.logical_and(pf._taxinc > 0, _hasgain == 1), np.maximum(0, pf._taxinc - _dwks31), 0)
    c24570 = np.where(
        np.logical_and(pf._taxinc > 0, _hasgain == 1), 0.28 * c24550, 0)
    _addtax = np.zeros((pf.dim,))
    _addtax = np.where(np.logical_and(pf._taxinc > 0, np.logical_and(
        _hasgain == 1, c24540 > pm.brk6[pf.MARS - 1])), 0.05 * pf.c24517, _addtax)
    _addtax = np.where(np.logical_and(np.logical_and(pf._taxinc > 0, _hasgain == 1), np.logical_and(c24540 <= pm.brk6[
                       pf.MARS - 1], pf._taxinc > pm.brk6[pf.MARS - 1])), 0.05 * np.minimum(pf.c04800 - pm.brk6[pf.MARS - 1], pf.c24517), _addtax)

    c24560 = np.zeros((pf.dim,))
    c24560 = np.where(np.logical_and(pf._taxinc > 0, _hasgain == 1), Taxer(
        inc_in=c24540, inc_out=c24560, MARS=pf.MARS, pm=pm, pf=pf), c24560)

    _taxspecial = np.where(np.logical_and(
        pf._taxinc > 0, _hasgain == 1), c24598 + c24615 + c24570 + c24560 + _addtax, 0)

    c24580 = np.where(np.logical_and(pf._taxinc > 0, _hasgain == 1), np.minimum(
        _taxspecial, pf._xyztax), c24580)
    # e24580 schedule D tax

    c05100 = c24580
    c05100 = np.where(np.logical_and(
        pf.c04800 > 0, pf._feided > 0), np.maximum(0, c05100 - pf._feitax), c05100)

    # Form 4972 - Lump Sum Distributions

    c59430 = np.where(pf._cmp == 1, np.maximum(0, pf.e59410 - pf.e59420), 0)
    c59450 = np.where(pf._cmp == 1, c59430 + pf.e59440, 0)  # income plus lump sum
    c59460 = np.where(pf._cmp == 1, np.maximum(
        0, np.minimum(0.5 * c59450, 10000)) - 0.2 * np.maximum(0, c59450 - 20000), 0)
    _line17 = np.where(pf._cmp == 1, c59450 - c59460, 0)
    _line19 = np.where(pf._cmp == 1, c59450 - c59460 - pf.e59470, 0)
    _line22 = np.where(np.logical_and(pf._cmp == 1, c59450 > 0), np.maximum(
        0, pf.e59440 - pf.e59440 * c59460 / c59450), 0)

    _line30 = np.where(
        pf._cmp == 1, 0.1 * np.maximum(0, c59450 - c59460 - pf.e59470), 0)

    _line31 = np.where(pf._cmp == 1,
                       0.11 * np.minimum(_line30, 1190)
                       + 0.12 *
                       np.minimum(2270 - 1190, np.maximum(0, _line30 - 1190))
                       + 0.14 *
                       np.minimum(4530 - 2270, np.maximum(0, _line30 - 2270))
                       + 0.15 *
                       np.minimum(6690 - 4530, np.maximum(0, _line30 - 4530))
                       + 0.16 *
                       np.minimum(9170 - 6690, np.maximum(0, _line30 - 6690))
                       + 0.18 *
                       np.minimum(11440 - 9170, np.maximum(0, _line30 - 9170))
                       + 0.20 *
                       np.minimum(
                           13710 - 11440, np.maximum(0, _line30 - 11440))
                       + 0.23 *
                       np.minimum(
                           17160 - 13710, np.maximum(0, _line30 - 13710))
                       + 0.26 *
                       np.minimum(
                           22880 - 17160, np.maximum(0, _line30 - 17160))
                       + 0.30 *
                       np.minimum(
                           28600 - 22880, np.maximum(0, _line30 - 22880))
                       + 0.34 *
                       np.minimum(
                           34320 - 28600, np.maximum(0, _line30 - 28600))
                       + 0.38 *
                       np.minimum(
                           42300 - 34320, np.maximum(0, _line30 - 34320))
                       + 0.42 *
                       np.minimum(
                           57190 - 42300, np.maximum(0, _line30 - 42300))
                       + 0.48 *
                       np.minimum(
                           85790 - 57190, np.maximum(0, _line30 - 57190)),
                       0)

    _line32 = np.where(pf._cmp == 1, 10 * _line31, 0)
    _line36 = np.where(np.logical_and(pf._cmp == 1, pf.e59440 == 0), _line32, 0)
    _line33 = np.where(np.logical_and(pf._cmp == 1, pf.e59440 > 0), 0.1 * _line22, 0)
    _line34 = np.where(np.logical_and(pf._cmp == 1, pf.e59440 > 0),
                       0.11 * np.minimum(_line30, 1190)
                       + 0.12 *
                       np.minimum(2270 - 1190, np.maximum(0, _line30 - 1190))
                       + 0.14 *
                       np.minimum(4530 - 2270, np.maximum(0, _line30 - 2270))
                       + 0.15 *
                       np.minimum(6690 - 4530, np.maximum(0, _line30 - 4530))
                       + 0.16 *
                       np.minimum(9170 - 6690, np.maximum(0, _line30 - 6690))
                       + 0.18 *
                       np.minimum(11440 - 9170, np.maximum(0, _line30 - 9170))
                       + 0.20 *
                       np.minimum(
                           13710 - 11440, np.maximum(0, _line30 - 11440))
                       + 0.23 *
                       np.minimum(
                           17160 - 13710, np.maximum(0, _line30 - 13710))
                       + 0.26 *
                       np.minimum(
                           22880 - 17160, np.maximum(0, _line30 - 17160))
                       + 0.30 *
                       np.minimum(
                           28600 - 22880, np.maximum(0, _line30 - 22880))
                       + 0.34 *
                       np.minimum(
                           34320 - 28600, np.maximum(0, _line30 - 28600))
                       + 0.38 *
                       np.minimum(
                           42300 - 34320, np.maximum(0, _line30 - 34320))
                       + 0.42 *
                       np.minimum(
                           57190 - 42300, np.maximum(0, _line30 - 42300))
                       + 0.48 *
                       np.minimum(
                           85790 - 57190, np.maximum(0, _line30 - 57190)),
                       0)
    _line35 = np.where(np.logical_and(pf._cmp == 1, pf.e59440 > 0), 10 * _line34, 0)
    _line36 = np.where(
        np.logical_and(pf._cmp == 1, pf.e59440 > 0), np.maximum(0, _line32 - _line35), 0)
    # tax saving from 10 yr option
    c59485 = np.where(pf._cmp == 1, _line36, 0)
    c59490 = np.where(pf._cmp == 1, c59485 + 0.2 * np.maximum(0, pf.e59400), 0)
    # pension gains tax plus

    pf.c05700 = np.where(pf._cmp == 1, c59490, 0)

    _s1291 = pf.e10105
    _parents = pf.e83200_0
    pf.c05750 = np.maximum(c05100 + _parents + pf.c05700, pf.e74400)
    pf._taxbc = pf.c05750

    outputs = (pf.e00650, _hasgain, _dwks5, c24505, c24510, _dwks9, pf.c24516,
               c24580, _dwks12, pf.c24517, pf.c24520, c24530, _dwks16,
               _dwks17, c24540, c24534, _dwks21, c24597, c24598, _dwks25,
               _dwks26, _dwks28, c24610, c24615, _dwks31, c24550, c24570,
               _addtax, c24560, _taxspecial, c05100, pf.c05700, c59430,
               c59450, c59460, _line17, _line19, _line22, _line30, _line31,
               _line32, _line36, _line33, _line34, _line35, c59485, c59490,
               _s1291, _parents, pf.c05750, pf._taxbc)

    header = ['e00650', '_hasgain', '_dwks5', 'c24505', 'c24510', '_dwks9',
              'c24516', 'c24580', '_dwks12', 'c24517', 'c24520',
              'c24530', '_dwks16', '_dwks17', 'c24540', 'c24534', '_dwks21',
              'c24597', 'c24598', '_dwks25', '_dwks26', '_dwks28', 'c24610',
              'c24615', '_dwks31', 'c24550', 'c24570', '_addtax', 'c24560',
              '_taxspecial', 'c05100', 'c05700', 'c59430', 'c59450', 'c59460',
              '_line17', '_line19', '_line22', '_line30', '_line31',
              '_line32', '_line36', '_line33', '_line34', '_line35',
              'c59485', 'c59490', '_s1291', '_parents', 'c05750',
              '_taxbc']

    return DataFrame(data=np.column_stack(outputs),
                     columns=header)


def MUI(pm, pf):
    # Additional Medicare tax on unearned Income
    pf.c05750 = np.where(pf.c00100 > pm._thresx[pf.MARS - 1], pf.c05750 + 0.038 * np.minimum(
        pf.e00300 + pf.e00600 + np.maximum(0, pf.c01000) + np.maximum(0, pf.e02000), pf.c00100 - pm._thresx[pf.MARS - 1]), pf.c05750)

    return DataFrame(data=np.column_stack((pf.c05750,)),
                     columns=['c05750'])


@vectorize('float64(float64, float64, float64, float64)', nopython=True)
def AMTI_amtded(c60200, c60220, c60240, c60000):
    amtded = c60200 + c60220 + c60240
    if c60000 <= 0:
        amtded = max(0, amtded + c60000)
    return amtded

@vectorize('float64(float64, float64, float64, float64)', nopython=True)
def AMTI_addamt(_exact, e60290, c60130, _amtded):
    #_addamt = np.where(np.logical_or(_exact == 0, np.logical_and(_exact == 1, _amtded + e60290 > 0)), _amtded + e60290 - c60130, 0)
    if _exact == 0 or (_exact == 1 and ((_amtded + e60290) > 0)):
        return _amtded + e60290 - c60130
    else:
        return 0

@vectorize('float64(' + 24*'float64, ' + 'float64)', nopython=True)
def AMTI_c62100(_addamt, e60300, e60860, e60100, e60840, e60630, e60550,
                e60720, e60430, e60500, e60340, e60680, e60600, e60405,
                e60440, e60420, e60410, e61400, e60660, c60260, e60480,
                e62000, c60000, e60250, _cmp):
    if _cmp == 1:
        return (_addamt + e60300 + e60860 + e60100 + e60840 + e60630 + e60550
               + e60720 + e60430 + e60500 + e60340 + e60680 + e60600 + e60405
               + e60440 + e60420 + e60410 + e61400 + e60660 - c60260 - e60480
               - e62000 + c60000 - e60250)
    else:
        return 0


@vectorize('float64(' + 5*'float64, ' + 'float64)', nopython=True)
def AMTI_edical(puf, _standard, _exact, e04470, e17500, e00100):
    if (puf and (_standard == 0 or (_exact == 1 and e04470 > 0))):
        return max(0, e17500 - max(0, e00100) * 0.075)
    else:
        return 0

@vectorize('float64(' + 12*'float64, ' + 'float64)', nopython=True)
def AMTI_cmbtp(puf, _standard, _exact, e04470, f6251, _edical, e00100,
              e62100, c60260, e21040, _sit, e18500, e20800):
    if (puf and ((_standard == 0 or (_exact == 1 and e04470 > 0))
        and f6251 == 1)):
        return (-1 * min(_edical, 0.025 * max(0, e00100)) + e62100 + c60260
               + e04470 + e21040 - _sit - e00100 - e18500 - e20800)
    else:
        return 0


@vectorize('float64(' + 13*'float64, ' + 'float64)', nopython=True)
def AMTI_c62100_2(puf, _standard, _exact, e04470, c00100, c04470, c17000,
                  e18500, c60260, c20800, c21040, _cmbtp, c62100, _sit):
    if (puf == True and ((_standard == 0 or (_exact == 1 and e04470 > 0)))):
        return (c00100 - c04470 + min(c17000, 0.025 * max(0, c00100)) + _sit
               + e18500 - c60260 + c20800 - c21040 + _cmbtp)
    else:
        return c62100

@vectorize('float64(' + 6*'float64, ' + 'float64)', nopython=True)
def AMTI_cmbtp_2(puf, _standard, f6251, e62100, e00100, c60260, _cmbtp):
    if (puf == True and ((_standard > 0 and f6251 == 1))):
        return e62100 - e00100 + c60260
    else:
        return _cmbtp


@vectorize('float64(' + 5*'float64, ' + 'float64)', nopython=True)
def AMTI_c62100_3(puf, _standard, c00100, c60260, _cmbtp, c62100):
    if (puf == True and _standard > 0):
        return (c00100 - c60260 + _cmbtp)
    else:
        return c62100


@vectorize('float64(' + 2*'float64, ' + 'float64)', nopython=True)
def AMTI_agep(DOBYR, FLPDYR, DOBMD):
    if DOBYR > 0:
        return np.ceil((12 * (FLPDYR - DOBYR) - DOBMD / 100) / 12)
    else:
        return 0


@vectorize('float64(' + 2*'float64, ' + 'float64)', nopython=True)
def AMTI_ages(SDOBYR, FLPDYR, SDOBMD):
    if SDOBYR > 0:
        return np.ceil((12 * (FLPDYR - SDOBYR) - SDOBMD / 100) / 12)
    else:
        return 0

@vectorize('float64(' + 4*'float64, ' + 'float64)', nopython=True)
def AMTI_c62600(_cmp, f6251, _exact, e62600, c62600):
    if (_cmp == 1 and f6251 == 1 and _exact == 1):
        return e62600
    else:
        return c62600


@vectorize('float64(' + 3*'float64, ' + 'float64)', nopython=True)
def AMTI_alminc(c62100, c62600, c02700, _alminc):
    if (c02700 > 0):
        return max(0, c62100 - c62600 + c02700)
    else:
        return _alminc


def AMTI(pm, pf, puf=True):
    c62720 = pf.c24517 + pf.x62720
    c60260 = pf.e00700 + pf.x60260
    c63100 = np.maximum(0, pf._taxbc - pf.e07300)
    c60200 = np.minimum(pf.c17000, 0.025 * pf._posagi)
    c60240 = pf.c18300 + pf.x60240
    c60220 = pf.c20800 + pf.x60220
    c60130 = pf.c21040 + pf.x60130
    c62730 = pf.e24515 + pf.x62730

    _amtded = AMTI_amtded(c60200, c60220, c60240, pf.c60000)
    _addamt = AMTI_addamt(pf._exact, pf.e60290, c60130, _amtded)

    c62100 = AMTI_c62100(_addamt, pf.e60300, pf.e60860, pf.e60100, pf.e60840, pf.e60630, pf.e60550,
                pf.e60720, pf.e60430, pf.e60500, pf.e60340, pf.e60680, pf.e60600, pf.e60405,
                pf.e60440, pf.e60420, pf.e60410, pf.e61400, pf.e60660, c60260, pf.e60480,
                pf.e62000, pf.c60000, pf._cmp, pf.e60250)


    _edical = AMTI_edical(puf, pf._standard, pf._exact, pf.e04470, pf.e17500, pf.e00100)

    _cmbtp = AMTI_cmbtp(puf, pf._standard, pf._exact, pf.e04470, pf.f6251, _edical, pf.e00100,
              pf.e62100, c60260, pf.e21040, pf._sit, pf.e18500, pf.e20800)

    c62100 = AMTI_c62100_2(puf, pf._standard, pf._exact, pf.e04470, pf.c00100, pf.c04470, pf.c17000,
                  pf.e18500, c60260, pf.c20800, pf.c21040, _cmbtp, c62100, pf._sit)

    _cmbtp = AMTI_cmbtp_2(puf, pf._standard, pf.f6251, pf.e62100, pf.e00100, c60260, _cmbtp)
    c62100 = AMTI_c62100_3(puf, pf._standard, pf.c00100, c60260, _cmbtp, c62100)

    #TODO
    _amtsepadd = np.where(np.logical_and(c62100 > pm.amtsep, np.logical_or(pf.MARS == 3, pf.MARS == 6)), np.maximum(
        0, np.minimum(pm.almsep, 0.25 * (c62100 - pm.amtsep))), 0)

    #TODO
    c62100 = np.where(np.logical_and(c62100 > pm.amtsep,
                      np.logical_or(pf.MARS == 3, pf.MARS == 6)), c62100 + _amtsepadd, c62100)

    #TODO
    c62600 = np.maximum(0, pm.amtex[
                        pf.MARS - 1] - 0.25 * np.maximum(0, c62100 - pm.amtys[pf.MARS - 1]))

    pf._agep = AMTI_agep(pf.DOBYR, pf.FLPDYR, pf.DOBMD)

    pf._ages = AMTI_ages(pf.SDOBYR, pf.FLPDYR, pf.SDOBMD)

    c62600 = AMTI_c62600(pf._cmp, pf.f6251, pf._exact, pf.e62600, c62600)

    #TODO
    c62600 = np.where(np.logical_and(np.logical_and(pf._cmp == 1, pf._exact == 0), np.logical_and(
        pf._agep < pm.amtage, pf._agep != 0)), np.minimum(c62600, pf._earned + pm.almdep), c62600)

    c62700 = np.maximum(0, c62100 - c62600)

    _alminc = c62700
    _amtfei = np.zeros((pf.dim,))

    _alminc = AMTI_alminc(c62100, c62600, pf.c02700, _alminc)

    #TODO
    _amtfei = np.where(pf.c02700 > 0, 0.26 * pf.c02700 + 0.02 *
                       np.maximum(0, pf.c02700 - pm.almsp / pf._sep), _amtfei)

    #TODO
    c62780 = 0.26 * _alminc + 0.02 * \
        np.maximum(0, _alminc - pm.almsp / pf._sep) - _amtfei

    c62900 = np.where(pf.f6251 != 0, pf.e62900, pf.e07300)
    c63000 = c62780 - c62900

    c62740 = np.minimum(np.maximum(0, pf.c24516 + pf.x62740), c62720 + c62730)
    c62740 = np.where(pf.c24516 == 0, c62720 + c62730, c62740)

    _ngamty = np.maximum(0, _alminc - c62740)

    c62745 = 0.26 * _ngamty + 0.02 * \
        np.maximum(0, _ngamty - pm.almsp / pf._sep)
    y62745 = pm.almsp / pf._sep
    _tamt2 = np.zeros((pf.dim,))

    _amt5pc = np.zeros((pf.dim,))
    #TODO
    _amt15pc = np.minimum(_alminc, c62720) - _amt5pc - np.minimum(np.maximum(
        0, pm.brk2[pf.MARS - 1] - pf.c24520), np.minimum(_alminc, c62720))
    #TODO
    _amt15pc = np.where(pf.c04800 == 0, np.maximum(
        0, np.minimum(_alminc, c62720) - pm.brk2[pf.MARS - 1]), _amt15pc)
    _amt25pc = np.minimum(_alminc, c62740) - np.minimum(_alminc, c62720)

    _amt25pc = np.where(c62730 == 0, 0, _amt25pc)
    c62747 = pm.cgrate1 * _amt5pc
    c62755 = pm.cgrate2 * _amt15pc
    c62770 = 0.25 * _amt25pc
    _tamt2 = c62747 + c62755 + c62770

    _amt = np.zeros((pf.dim,))
    #TODO
    _amt = np.where(_ngamty > pm.brk6[
                    pf.MARS - 1], 0.05 * np.minimum(_alminc, c62740), _amt)
    #TODO
    _amt = np.where(np.logical_and(_ngamty <= pm.brk6[pf.MARS - 1], _alminc > pm.brk6[
                    pf.MARS - 1]), 0.05 * np.minimum(_alminc - pm.brk6[pf.MARS - 1], c62740), _amt)

    _tamt2 = _tamt2 + _amt

    c62800 = np.minimum(c62780, c62745 + _tamt2 - _amtfei)
    c63000 = c62800 - c62900
    c63100 = pf._taxbc - pf.e07300 - pf.c05700
    c63100 = c63100 + pf.e10105

    c63100 = np.maximum(0, c63100)
    c63200 = np.maximum(0, c63000 - c63100)
    c09600 = c63200
    pf._othtax = pf.e05800 - (pf.e05100 + pf.e09600)

    pf.c05800 = pf._taxbc + c63200

    outputs = (c62720, c60260, c63100, c60200, c60240, c60220, c60130,
               c62730, _addamt, c62100, _cmbtp, _edical, _amtsepadd,
               pf._agep, pf._ages, c62600, c62700, _alminc, _amtfei, c62780,
               c62900, c63000, c62740, _ngamty, c62745, y62745, _tamt2,
               _amt5pc, _amt15pc, _amt25pc, c62747, c62755, c62770, _amt,
               c62800, c09600, pf._othtax, pf.c05800)

    header = ['c62720', 'c60260', 'c63100', 'c60200', 'c60240', 'c60220',
              'c60130', 'c62730', '_addamt', 'c62100', '_cmbtp', '_edical',
              '_amtsepadd', '_agep', '_ages', 'c62600', 'c62700',
              '_alminc', '_amtfei', 'c62780', 'c62900', 'c63000', 'c62740',
              '_ngamty', 'c62745', 'y62745', '_tamt2', '_amt5pc', '_amt15pc',
              '_amt25pc', 'c62747', 'c62755', 'c62770', '_amt', 'c62800',
              'c09600', '_othtax', 'c05800']

    return DataFrame(data=np.column_stack(outputs),
                     columns=header)


def F2441(pm, pf, puf=True):
    pf._earned = np.where(pf._fixeic == 1, pf.e59560, pf._earned)
    pf.c32880 = np.where(np.logical_and(pf.MARS == 2, puf == True), 0.5 * pf._earned, 0)
    pf.c32890 = np.where(np.logical_and(pf.MARS == 2, puf == True), 0.5 * pf._earned, 0)
    pf.c32880 = np.where(
        np.logical_and(pf.MARS == 2, puf == False), np.maximum(0, pf.e32880), pf.c32880)
    pf.c32890 = np.where(
        np.logical_and(pf.MARS == 2, puf == False), np.maximum(0, pf.e32890), pf.c32890)
    pf.c32880 = np.where(pf.MARS != 2, pf._earned, pf.c32880)
    pf.c32890 = np.where(pf.MARS != 2, pf._earned, pf.c32890)

    _ncu13 = np.zeros((pf.dim,))
    _ncu13 = np.where(puf == True, pf.f2441, _ncu13)
    _ncu13 = np.where(
        np.logical_and(puf == False, pf.CDOB1 > 0), _ncu13 + 1, _ncu13)
    _ncu13 = np.where(
        np.logical_and(puf == False, pf.CDOB2 > 0), _ncu13 + 1, _ncu13)

    pf._dclim = np.minimum(_ncu13, 2) * pm.dcmax
    pf.c32800 = np.minimum(np.maximum(pf.e32800, pf.e32750 + pf.e32775), pf._dclim)

    outputs = (pf._earned, pf.c32880, pf.c32890, _ncu13, pf._dclim, pf.c32800)
    header = ['_earned', 'c32880', 'c32890', '_ncu13', '_dclim', 'c32800']

    return DataFrame(data=np.column_stack(outputs), columns=header)


def DepCareBen(pm, pf):
    #c32800 = c32800
    # Part III ofdependent care benefits
    _seywage = np.where(np.logical_and(pf._cmp == 1, pf.MARS == 2), np.minimum(
        pf.c32880, np.minimum(pf.c32890, np.minimum(pf.e33420 + pf.e33430 - pf.e33450, pf.e33460))), 0)
    _seywage = np.where(np.logical_and(pf._cmp == 1, pf.MARS != 2), np.minimum(
        pf.c32880, np.minimum(pf.e33420 + pf.e33430 - pf.e33450, pf.e33460)), _seywage)

    c33465 = np.where(pf._cmp == 1, pf.e33465, 0)
    c33470 = np.where(pf._cmp == 1, pf.e33470, 0)
    c33475 = np.where(
        pf._cmp == 1, np.maximum(0, np.minimum(_seywage, 5000 / pf._sep) - c33470), 0)
    c33480 = np.where(
        pf._cmp == 1, np.maximum(0, pf.e33420 + pf.e33430 - pf.e33450 - c33465 - c33475), 0)
    c32840 = np.where(pf._cmp == 1, c33470 + c33475, 0)
    pf.c32800 = np.where(pf._cmp == 1, np.minimum(
        np.maximum(0, pf._dclim - c32840), np.maximum(0, pf.e32750 + pf.e32775 - c32840)), pf.c32800)

    pf.c33000 = np.where(
        pf.MARS == 2, np.maximum(0, np.minimum(pf.c32800, np.minimum(pf.c32880, pf.c32890))), 0)
    pf.c33000 = np.where(
        pf.MARS != 2, np.maximum(0, np.minimum(pf.c32800, pf._earned)), pf.c33000)

    outputs = (_seywage, c33465, c33470, c33475, c33480, c32840, pf.c32800,
               pf.c33000)
    header = ['_seywage', 'c33465', 'c33470', 'c33475', 'c33480', 'c32840',
              'c32800', 'c33000']

    return DataFrame(data=np.column_stack(outputs),
                     columns=header)


def ExpEarnedInc(pm, pf):
    # Expenses limited to earned income

    _tratio = np.where(pf._exact == 1, np.ceil(
        np.maximum((pf.c00100 - pm.agcmax) / 2000, 0)), 0)
    c33200 = np.where(pf._exact == 1, pf.c33000 * 0.01 * np.maximum(20,
                                                              pm.pcmax - np.minimum(15, _tratio)), 0)
    c33200 = np.where(pf._exact != 1, pf.c33000 * 0.01 * np.maximum(20, pm.pcmax
                      - np.maximum((pf.c00100 - pm.agcmax) / 2000, 0)), c33200)

    c33400 = np.minimum(np.maximum(0, pf.c05800 - pf.e07300), c33200)
    # amount of the credit

    pf.c07180 = np.where(pf.e07180 == 0, 0, c33400)

    return DataFrame(data=np.column_stack((_tratio, c33200, c33400, pf.c07180)),
                     columns=['_tratio', 'c33200', 'c33400', 'c07180'])


def RateRed(pm, pf):
    # rate reduction credit for 2001 only, is this needed?

    pf.c05800 = np.where(pf._fixup >= 3, pf.c05800 + pf._othtax, pf.c05800)

    pf.c59560 = np.where(pf._exact == 1, pf.x59560, pf._earned)

    return DataFrame(data=np.column_stack((pf.c07970, pf.c05800, pf.c59560)),
                     columns=['c07970', 'c05800', 'c59560'])


def NumDep(pm, pf, puf=True):
    # Number of dependents for EIC

    _ieic = np.zeros((pf.dim,))

    EICYB1_1 = np.where(pf.EICYB1 < 0, 0.0, pf.EICYB1)
    EICYB2_2 = np.where(pf.EICYB2 < 0, 0.0, pf.EICYB2)
    EICYB3_3 = np.where(pf.EICYB3 < 0, 0.0, pf.EICYB3)

    _ieic = np.where(puf == True, pf.EIC, EICYB1_1 + EICYB2_2 + EICYB3_3)

    _ieic = _ieic.astype(int)

    # Modified AGI only through 2002

    _modagi = pf.c00100 + pf.e00400

    _val_ymax = np.where(np.logical_and(pf.MARS == 2, _modagi > 0), pm.ymax[
                         _ieic] + pm.joint[_ieic], 0)
    _val_ymax = np.where(np.logical_and(_modagi > 0, np.logical_or(pf.MARS == 1, np.logical_or(
        pf.MARS == 4, np.logical_or(pf.MARS == 5, pf.MARS == 7)))), pm.ymax[_ieic], _val_ymax)
    pf.c59660 = np.where(np.logical_and(_modagi > 0, np.logical_or(pf.MARS == 1, np.logical_or(pf.MARS == 4, np.logical_or(pf.MARS == 5, np.logical_or(
        pf.MARS == 2, pf.MARS == 7))))), np.minimum(pm.rtbase[_ieic] * pf.c59560, pm.crmax[_ieic]), pf.c59660)
    _preeitc = np.where(np.logical_and(_modagi > 0, np.logical_or(pf.MARS == 1, np.logical_or(
        pf.MARS == 4, np.logical_or(pf.MARS == 5, np.logical_or(pf.MARS == 2, pf.MARS == 7))))), pf.c59660, 0)

    pf.c59660 = np.where(np.logical_and(np.logical_and(pf.MARS != 3, pf.MARS != 6), np.logical_and(_modagi > 0, np.logical_or(
        _modagi > _val_ymax, pf.c59560 > _val_ymax))), np.maximum(0, pf.c59660 - pm.rtless[_ieic] * (np.maximum(_modagi, pf.c59560) - _val_ymax)), pf.c59660)
    _val_rtbase = np.where(np.logical_and(np.logical_and(
        pf.MARS != 3, pf.MARS != 6), _modagi > 0), pm.rtbase[_ieic] * 100, 0)
    _val_rtless = np.where(np.logical_and(np.logical_and(
        pf.MARS != 3, pf.MARS != 6), _modagi > 0), pm.rtless[_ieic] * 100, 0)

    _dy = np.where(np.logical_and(np.logical_and(pf.MARS != 3, pf.MARS != 6), _modagi > 0), pf.e00400 + pf.e83080 + pf.e00300 + pf.e00600
                   +
                   np.maximum(0, np.maximum(0, pf.e01000) - np.maximum(0, pf.e40223))
                   + np.maximum(0, np.maximum(0, pf.e25360) -
                                pf.e25430 - pf.e25470 - pf.e25400 - pf.e25500)
                   + np.maximum(0, pf.e26210 + pf.e26340 + pf.e27200 - np.absolute(pf.e26205) - np.absolute(pf.e26320)), 0)

    pf.c59660 = np.where(np.logical_and(np.logical_and(pf.MARS != 3, pf.MARS != 6), np.logical_and(
        _modagi > 0, _dy > pm.dylim)), 0, pf.c59660)

    pf.c59660 = np.where(np.logical_and(np.logical_and(pf._cmp == 1, _ieic == 0), np.logical_and(np.logical_and(
        pf.SOIYR - pf.DOBYR >= 25, pf.SOIYR - pf.DOBYR < 65), np.logical_and(pf.SOIYR - pf.SDOBYR >= 25, pf.SOIYR - pf.SDOBYR < 65))), 0, pf.c59660)
    pf.c59660 = np.where(np.logical_and(_ieic == 0, np.logical_or(np.logical_or(
        pf._agep < 25, pf._agep >= 65), np.logical_or(pf._ages < 25, pf._ages >= 65))), 0, pf.c59660)

    outputs = (_ieic, pf.EICYB1, pf.EICYB2, pf.EICYB3, _modagi, pf.c59660,
               _val_ymax, _preeitc, _val_rtbase, _val_rtless, _dy)
    header = ['_ieic', 'EICYB1', 'EICYB2', 'EICYB3', '_modagi',
              'c59660', '_val_ymax', '_preeitc', '_val_rtbase',
              '_val_rtless', '_dy']

    return DataFrame(data=np.column_stack(outputs), columns=header)


def ChildTaxCredit(pm, pf):
    # Child Tax Credit

    c11070 = np.zeros((pf.dim,))
    pf.c07230 = np.zeros((pf.dim,))
    pf._precrd = np.zeros((pf.dim,))

    pf._num = np.ones((pf.dim,))
    pf._num = np.where(pf.MARS == 2, 2, pf._num)

    pf._nctcr = np.zeros((pf.dim,))
    pf._nctcr = np.where(pf.SOIYR >= 2002, pf.n24, pf._nctcr)
    pf._nctcr = np.where(
        np.logical_and(pf.SOIYR < 2002, pm.chmax > 0), pf.xtxcr1xtxcr10, pf._nctcr)
    pf._nctcr = np.where(
        np.logical_and(pf.SOIYR < 2002, pm.chmax <= 0), pf.XOCAH, pf._nctcr)

    pf._precrd = pm.chmax * pf._nctcr
    _ctcagi = pf.c00100 + pf._feided

    pf._precrd = np.where(np.logical_and(_ctcagi > pm._cphase[pf.MARS - 1], pf._exact == 1), np.maximum(
        0, pf._precrd - 50 * np.ceil(_ctcagi - pm._cphase[pf.MARS - 1]) / 1000), pf._precrd)
    pf._precrd = np.where(np.logical_and(_ctcagi > pm._cphase[pf.MARS - 1], pf._exact != 1), np.maximum(
        0, pf._precrd - 50 * (np.maximum(0, _ctcagi - pm._cphase[pf.MARS - 1]) + 500) / 1000), pf._precrd)

    outputs = (c11070, pf.c07220, pf.c07230, pf._num, pf._nctcr, pf._precrd, _ctcagi)
    header = ['c11070', 'c07220', 'c07230', '_num', '_nctcr',
              '_precrd', '_ctcagi']

    return DataFrame(data=np.column_stack(outputs), columns=header)


def AmOppCr(pm, pf):
    # American Opportunity Credit 2009+
    c87482 = np.where(pf._cmp == 1, np.maximum(0, np.minimum(pf.e87482, 4000)), 0)
    c87487 = np.where(pf._cmp == 1, np.maximum(0, np.minimum(pf.e87487, 4000)), 0)
    c87492 = np.where(pf._cmp == 1, np.maximum(0, np.minimum(pf.e87492, 4000)), 0)
    c87497 = np.where(pf._cmp == 1, np.maximum(0, np.minimum(pf.e87497, 4000)), 0)

    c87483 = np.where(np.maximum(0, c87482 - 2000) == 0,
                      c87482, 2000 + 0.25 * np.maximum(0, c87482 - 2000))
    c87488 = np.where(np.maximum(0, c87487 - 2000) == 0,
                      c87487, 2000 + 0.25 * np.maximum(0, c87487 - 2000))
    c87493 = np.where(np.maximum(0, c87492 - 2000) == 0,
                      c87492, 2000 + 0.25 * np.maximum(0, c87492 - 2000))
    c87498 = np.where(np.maximum(0, c87497 - 2000) == 0,
                      c87497, 2000 + 0.25 * np.maximum(0, c87497 - 2000))

    pf.c87521 = c87483 + c87488 + c87493 + c87498

    outputs = (c87482, c87487, c87492, c87497,
               c87483, c87488, c87493, c87498, pf.c87521)
    header = ['c87482', 'c87487', 'c87492', 'c87497', 'c87483', 'c87488',
              'c87493', 'c87498', 'c87521']

    return DataFrame(data=np.column_stack(outputs), columns=header)


def LLC(pm, pf, puf=True):
    # Lifetime Learning Credit

    c87540 = np.where(
        puf == True, np.minimum(pf.e87530, pm.learn), 0)
    pf.c87550 = np.where(puf == True, 0.2 * c87540, 0)

    c87530 = np.where(puf == False, pf.e87526 + pf.e87522 + pf.e87524 + pf.e87528, 0)
    c87540 = np.where(
        puf == False, np.minimum(c87530, pm.learn), c87540)
    pf.c87550 = np.where(puf == False, 0.2 * c87540, pf.c87550)

    outputs = (c87540, pf.c87550, c87530)
    header = ['c87540', 'c87550', 'c87530']
    return DataFrame(data=np.column_stack(outputs), columns=header)


def RefAmOpp(pm, pf):
    # Refundable American Opportunity Credit 2009+
    c87668 = np.zeros((pf.dim,))

    c87654 = np.where(np.logical_and(pf._cmp == 1, pf.c87521 > 0), 90000 * pf._num, 0)
    c87656 = np.where(np.logical_and(pf._cmp == 1, pf.c87521 > 0), pf.c00100, 0)
    c87658 = np.where(
        np.logical_and(pf._cmp == 1, pf.c87521 > 0), np.maximum(0, c87654 - c87656), 0)
    c87660 = np.where(np.logical_and(pf._cmp == 1, pf.c87521 > 0), 10000 * pf._num, 0)
    c87662 = np.where(np.logical_and(pf._cmp == 1, pf.c87521 > 0),
                      1000 * np.minimum(1, c87658 / c87660), 0)
    c87664 = np.where(
        np.logical_and(pf._cmp == 1, pf.c87521 > 0), c87662 * pf.c87521 / 1000, 0)
    c87666 = np.where(np.logical_and(
        pf._cmp == 1, np.logical_and(pf.c87521 > 0, pf.EDCRAGE == 1)), 0, 0.4 * c87664)
    c10960 = np.where(np.logical_and(pf._cmp == 1, pf.c87521 > 0), c87666, 0)
    c87668 = np.where(
        np.logical_and(pf._cmp == 1, pf.c87521 > 0), c87664 - c87666, 0)
    c87681 = np.where(np.logical_and(pf._cmp == 1, pf.c87521 > 0), c87666, 0)

    outputs = (c87654, c87656, c87658, c87660, c87662,
               c87664, c87666, c10960, c87668, c87681)
    header = ['c87654', 'c87656', 'c87658', 'c87660', 'c87662', 'c87664',
              'c87666', 'c10960', 'c87668', 'c87681']
    return DataFrame(data=np.column_stack(outputs), columns=header)


def NonEdCr(pm, pf):
    # Nonrefundable Education Credits

    # Form 8863 Tentative Education Credits
    c87560 = pf.c87550

    # Phase Out
    c87570 = np.where(
        pf.MARS == 2, pm.edphhm * 1000, pm.edphhs * 1000)
    c87580 = pf.c00100
    c87590 = np.maximum(0, c87570 - c87580)
    c87600 = 10000 * pf._num
    c87610 = np.minimum(1, c87590 / c87600)
    c87620 = c87560 * c87610

    _ctc1 = pf.c07180 + pf.e07200 + pf.c07230
    _ctc2 = np.zeros((pf.dim,))

    _ctc2 = pf.e07240 + pf.e07960 + pf.e07260 + pf.e07300
    _regcrd = _ctc1 + _ctc2
    _exocrd = pf.e07700 + pf.e07250
    _exocrd = _exocrd + pf.t07950
    _ctctax = pf.c05800 - _regcrd - _exocrd
    pf.c07220 = np.minimum(pf._precrd, np.maximum(0, _ctctax))
    # lt tax owed

    outputs = (c87560, c87570, c87580, c87590, c87600, c87610,
               c87620, _ctc1, _ctc2, _regcrd, _exocrd, _ctctax, pf.c07220)
    header = ['c87560', 'c87570', 'c87580', 'c87590', 'c87600', 'c87610',
              'c87620', '_ctc1', '_ctc2', '_regcrd', '_exocrd', '_ctctax',
              'c07220']
    return DataFrame(data=np.column_stack(outputs), columns=header)


def AddCTC(pm, pf, puf=True):
    # Additional Child Tax Credit

    c82940 = np.zeros((pf.dim,))

    # Part I of 2005 form 8812
    c82925 = np.where(pf._nctcr > 0, pf._precrd, 0)
    c82930 = np.where(pf._nctcr > 0, pf.c07220, 0)
    c82935 = np.where(pf._nctcr > 0, c82925 - c82930, 0)
    # CTC not applied to tax

    c82880 = np.where(pf._nctcr > 0, np.maximum(
        0, pf.e00200 + pf.e82882 + pf.e30100 + np.maximum(0, pf._sey) - 0.5 * pf._setax), 0)
    c82880 = np.where(np.logical_and(pf._nctcr > 0, pf._exact == 1), pf.e82880, c82880)
    h82880 = np.where(pf._nctcr > 0, c82880, 0)
    c82885 = np.where(
        pf._nctcr > 0, np.maximum(0, c82880 - pm.ealim), 0)
    c82890 = np.where(pf._nctcr > 0, pm.adctcrt * c82885, 0)

    # Part II of 2005 form 8812
    c82900 = np.where(np.logical_and(pf._nctcr > 2, c82890 < c82935),
                      0.0765 * np.minimum(pm.ssmax, c82880), 0)
    c82905 = np.where(
        np.logical_and(pf._nctcr > 2, c82890 < c82935), pf.e03260 + pf.e09800, 0)
    c82910 = np.where(
        np.logical_and(pf._nctcr > 2, c82890 < c82935), c82900 + c82905, 0)
    c82915 = np.where(
        np.logical_and(pf._nctcr > 2, c82890 < c82935), pf.c59660 + pf.e11200, 0)
    c82920 = np.where(
        np.logical_and(pf._nctcr > 2, c82890 < c82935), np.maximum(0, c82910 - c82915), 0)
    c82937 = np.where(
        np.logical_and(pf._nctcr > 2, c82890 < c82935), np.maximum(c82890, c82920), 0)

    # Part II of 2005 form 8812
    c82940 = np.where(
        np.logical_and(pf._nctcr > 2, c82890 >= c82935), c82935, c82940)
    c82940 = np.where(
        np.logical_and(pf._nctcr > 2, c82890 < c82935), np.minimum(c82935, c82937), c82940)

    c11070 = np.where(pf._nctcr > 0, c82940, 0)

    e59660 = np.where(
        np.logical_and(puf == True, pf._nctcr > 0), pf.e59680 + pf.e59700 + pf.e59720, 0)
    _othadd = np.where(pf._nctcr > 0, pf.e11070 - c11070, 0)

    c11070 = np.where(
        np.logical_and(pf._nctcr > 0, pf._fixup >= 4), c11070 + _othadd, c11070)

    outputs = (c82925, c82930, c82935, c82880, h82880, c82885, c82890,
               c82900, c82905, c82910, c82915, c82920, c82937, c82940, c11070,
               e59660, _othadd)

    header = ['c82925', 'c82930', 'c82935', 'c82880', 'h82880',
              'c82885', 'c82890', 'c82900', 'c82905', 'c82910', 'c82915',
              'c82920', 'c82937', 'c82940', 'c11070', 'e59660', '_othadd']

    return DataFrame(data=np.column_stack(outputs), columns=header)


def F5405(pm, pf):
    # Form 5405 First-Time Homebuyer Credit
    #not needed

    c64450 = np.zeros((pf.dim,))
    return DataFrame(data=np.column_stack((c64450,)), columns=['c64450'])


def C1040(pm, pf, puf=True):
    # Credits 1040 line 48

    x07400 = pf.e07400
    pf.c07100 = (pf.e07180 + pf.e07200 + pf.c07220 + pf.c07230 + pf.e07250
              + pf.e07600 + pf.e07260 + pf.c07970 + pf.e07300 + x07400
              + pf.e07500 + pf.e07700 + pf.e08000)

    y07100 = pf.c07100

    pf.c07100 = pf.c07100 + pf.e07240
    pf.c07100 = pf.c07100 + pf.e08001
    pf.c07100 = pf.c07100 + pf.e07960 + pf.e07970
    pf.c07100 = np.where(pf.SOIYR >= 2009, pf.c07100 + pf.e07980, pf.c07100)

    x07100 = pf.c07100
    pf.c07100 = np.minimum(pf.c07100, pf.c05800)

    # Tax After credits 1040 line 52

    pf._eitc = pf.c59660
    pf.c08795 = np.maximum(0, pf.c05800 - pf.c07100)

    c08800 = pf.c08795
    e08795 = np.where(puf == True, pf.e08800, 0)

    # Tax before refundable credits

    pf.c09200 = pf.c08795 + pf.e09900 + pf.e09400 + pf.e09800 + pf.e10000 + pf.e10100
    pf.c09200 = pf.c09200 + pf.e09700
    pf.c09200 = pf.c09200 + pf.e10050
    pf.c09200 = pf.c09200 + pf.e10075
    pf.c09200 = pf.c09200 + pf.e09805
    pf.c09200 = pf.c09200 + pf.e09710 + pf.e09720

    outputs = (pf.c07100, y07100, x07100, pf.c08795, c08800, e08795, pf.c09200)
    header = ['c07100', 'y07100', 'x07100', 'c08795', 'c08800', 'e08795',
              'c09200']
    return DataFrame(data=np.column_stack(outputs), columns=header)


def DEITC(pm, pf):
    # Decomposition of EITC

    c59680 = np.where(np.logical_and(
        pf.c08795 > 0, np.logical_and(pf.c59660 > 0, pf.c08795 <= pf.c59660)), pf.c08795, 0)
    _comb = np.where(np.logical_and(
        pf.c08795 > 0, np.logical_and(pf.c59660 > 0, pf.c08795 <= pf.c59660)), pf.c59660 - c59680, 0)

    c59680 = np.where(np.logical_and(
        pf.c08795 > 0, np.logical_and(pf.c59660 > 0, pf.c08795 > pf.c59660)), pf.c59660, c59680)
    _comb = np.where(np.logical_and(
        pf.c08795 > 0, np.logical_and(pf.c59660 > 0, pf.c08795 > pf.c59660)), 0, _comb)

    pf.c59700 = np.where(np.logical_and(pf.c08795 > 0, np.logical_and(pf.c59660 > 0, np.logical_and(
        _comb > 0, np.logical_and(pf.c09200 - pf.c08795 > 0, pf.c09200 - pf.c08795 > _comb)))), _comb, 0)
    pf.c59700 = np.where(np.logical_and(pf.c08795 > 0, np.logical_and(pf.c59660 > 0, np.logical_and(
        _comb > 0, np.logical_and(pf.c09200 - pf.c08795 > 0, pf.c09200 - pf.c08795 <= _comb)))), pf.c09200 - pf.c08795, pf.c59700)
    c59720 = np.where(np.logical_and(pf.c08795 > 0, np.logical_and(pf.c59660 > 0, np.logical_and(
        _comb > 0, np.logical_and(pf.c09200 - pf.c08795 > 0, pf.c09200 - pf.c08795 <= _comb)))), pf.c59660 - c59680 - pf.c59700, 0)

    c59680 = np.where(np.logical_and(pf.c08795 == 0, pf.c59660 > 0), 0, c59680)
    pf.c59700 = np.where(np.logical_and(pf.c08795 == 0, np.logical_and(
        pf.c59660 > 0, np.logical_and(pf.c09200 > 0, pf.c09200 > pf.c59660))), pf.c59660, pf.c59700)
    pf.c59700 = np.where(np.logical_and(pf.c08795 == 0, np.logical_and(
        pf.c59660 > 0, np.logical_and(pf.c09200 > 0, pf.c09200 < pf.c59660))), pf.c09200, pf.c59700)
    c59720 = np.where(np.logical_and(pf.c08795 == 0, np.logical_and(
        pf.c59660 > 0, np.logical_and(pf.c09200 > 0, pf.c09200 < pf.c59660))), pf.c59660 - pf.c59700, c59720)
    c59720 = np.where(np.logical_and(
        pf.c08795 == 0, np.logical_and(pf.c59660 > 0, pf.c09200 <= 0)), pf.c59660 - pf.c59700, c59720)

    # Ask dan about this section of code! Line 1231 - 1241

    _compb = np.where(np.logical_or(pf.c08795 < 0, pf.c59660 <= 0), 0, 0)
    c59680 = np.where(np.logical_or(pf.c08795 < 0, pf.c59660 <= 0), 0, c59680)
    pf.c59700 = np.where(np.logical_or(pf.c08795 < 0, pf.c59660 <= 0), 0, pf.c59700)
    c59720 = np.where(np.logical_or(pf.c08795 < 0, pf.c59660 <= 0), 0, c59720)

    c07150 = pf.c07100 + c59680
    c07150 = c07150

    outputs = (c59680, pf.c59700, c59720, _comb, c07150, pf.c10950)
    header = ['c59680', 'c59700', 'c59720', '_comb', 'c07150', 'c10950']

    return DataFrame(data=np.column_stack(outputs), columns=header)

def SOIT(pm, pf):

    # SOI Tax (Tax after non-refunded credits plus tip penalty)
    c10300 = pf.c09200 - pf.e10000 - pf.e59680 - pf.c59700
    c10300 = c10300 - pf.e11070
    c10300 = c10300 - pf.e11550
    c10300 = c10300 - pf.e11580
    c10300 = c10300 - pf.e09710 - pf.e09720 - pf.e11581 - pf.e11582
    c10300 = c10300 - pf.e87900 - pf.e87905 - pf.e87681 - pf.e87682
    c10300 = c10300 - c10300 - pf.c10950 - pf.e11451 - pf.e11452
    c10300 = pf.c09200 - pf.e09710 - pf.e09720 - pf.e10000 - pf.e11601 - pf.e11602
    c10300 = np.maximum(c10300, 0)

    # Ignore refundable partof _eitc to obtain SOI income tax

    pf._eitc = np.where(pf.c09200 <= pf._eitc, pf.c09200, pf._eitc)
    c10300 = np.where(pf.c09200 <= pf._eitc, 0, c10300)

    outputs = (c10300, pf._eitc)
    header = ['c10300', '_eitc']
    return DataFrame(data=np.column_stack(outputs), columns=header)


