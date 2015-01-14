import pandas as pd
from pandas import DataFrame
import math
import numpy as np
from .utils import *

from .parameters import *

DEFAULT_YR = 2013

class Calculator(object):

    def __init__(self, data, default_year=2013):
        self.tax_data = data
        self.DEFAULT_YR = default_year


def update_globals_from_calculator(calc):
    globals().update(vars(calc))


def update_calculator_from_module(calc, mod):
    calc_vals_overwrite = dict(list(vars(mod).items()) +
                               list(calc.__dict__.items()))
    calc.__dict__.update(calc_vals_overwrite)


def calculator(data, mods="", **kwargs):
    if mods:
        import json
        dd = json.loads(mods)
        dd = {k:np.array(v) for k,v in dd.items() if type(v) == list}
        kwargs.update(dd)

    calc = Calculator(data)
    if kwargs:
        calc.__dict__.update(kwargs)
    return calc


@vectorize('int64(int64)', nopython=True)
def filing_status_sep(MARS):
    if MARS == 3 or MARS == 6:
        return 2
    return 1


def FilingStatus(p):
    # Filing based on marital status
    # TODO: get rid of _txp in tests
    p._sep = filing_status_sep(MARS)
    return DataFrame(data=p._sep,
                     columns=['_sep', ])


@vectorize('float64(float64, float64, float64)', nopython=True)
def feided_vec(e35300_0, e35600_0, e35910_0):
    return max(e35300_0, e35600_0 + e35910_0)


def Adj():
    # Adjustments
    global _feided, c02900
    _feided = feided_vec(e35300_0, e35600_0, e35910_0)  # Form 2555

    c02900 = (e03150 + e03210 + e03600 + e03260 + e03270 + e03300
              + e03400 + e03500 + e03280 + e03900 + e04000 + e03700
              + e03220 + e03230
              + e03240
              + e03290)

    return DataFrame(data=np.column_stack((_feided, c02900)),
                     columns=['_feided', 'c02900'])


def CapGains(p):
    # Capital Gains
    global _ymod
    global _ymod1
    global c02700
    global c23650
    global c01000
    c23650 = e23250 + e22250 + e23660
    c01000 = np.maximum(-3000 / p._sep, c23650)
    c02700 = np.minimum(_feided, p._feimax[FLPDYR - p.DEFAULT_YR] * f2555)
    _ymod1 = (e00200 + e00300 + e00600
            + e00700 + e00800 + e00900
            + c01000 + e01100 + e01200
            + e01400 + e01700 + e02000
            + e02100 + e02300 + e02600
            + e02610 + e02800 - e02540)
    _ymod2 = e00400 + (0.50 * e02400) - c02900
    _ymod3 = e03210 + e03230 + e03240 + e02615
    _ymod = _ymod1 + _ymod2 + _ymod3

    return DataFrame(data=np.column_stack((c23650, c01000, c02700, _ymod1,
                                           _ymod2, _ymod3, _ymod)),
                     columns=['c23650', 'c01000', 'c02700', '_ymod1', '_ymod2',
                               '_ymod3', '_ymod'])

@jit('void(float64[:], int64[:], int64[:], float64[:], int64[:], int64[:], int64[:], float64[:])', nopython=True)
def SSBenefits_c02500(SSIND, MARS, e02500, _ymod, e02400, _ssb50, _ssb85, c02500):

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


def SSBenefits(p):
    # Social Security Benefit Taxation
    global c02500
    c02500 = np.zeros(len(e02500))
    SSBenefits_c02500(SSIND, MARS, e02500, _ymod, e02400, p._ssb50, p._ssb85, c02500)
    return DataFrame(data=np.column_stack((c02500,e02500)),
                     columns=['c02500', 'e02500'])


@vectorize('float64(float64, float64, float64)', nopython=True)
def conditional_agi(fixup, c00100, agierr):
    if fixup >= 1:
        return c00100 + agierr
    return c00100


def AGI(p):
    # Adjusted Gross Income
    global _posagi
    global c00100
    global c04600
    c02650 = _ymod1 + c02500 - c02700 + e02615  # Gross Income

    c00100 = c02650 - c02900
    _agierr = e00100 - c00100  # Adjusted Gross Income
    c00100 = conditional_agi(_fixup, c00100, _agierr)

    _posagi = np.maximum(c00100, 0)
    _ywossbe = e00100 - e02500
    _ywossbc = c00100 - c02500

    _prexmp = XTOT * p._amex[FLPDYR - p.DEFAULT_YR]
    # Personal Exemptions (_phaseout smoothed)

    _dispc_numer = 0.02 * (_posagi - p._exmpb[FLPDYR - p.DEFAULT_YR, MARS - 1])
    _dispc_denom = (2500 / p._sep)
    _dispc = np.minimum(1, np.maximum(0, _dispc_numer / _dispc_denom ))

    c04600 = _prexmp * (1 - _dispc)

    return DataFrame(data=np.column_stack((c02650, c00100, _agierr, _posagi,
                                           _ywossbe, _ywossbc, _prexmp,
                                           c04600)),
                     columns=['c02650', 'c00100', '_agierr', '_posagi',
                              '_ywossbe', '_ywossbc', '_prexmp', 'c04600'])


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


@vectorize('float64(float64, float64, float64, float64, float64)', nopython=True)
def item_ded_limit(c21060, c00100, nonlimited, limitratio, posagi):
    if c21060 > nonlimited and c00100 > limitratio:
        dedmin = 0.8 * (c21060 - nonlimited)
        dedpho = 0.03 * max(0, posagi - limitratio)
        return min(dedmin, dedpho)
    return 0.0


@vectorize('float64(float64, float64, float64, float64, float64)')
def item_ded_vec(c21060, c00100, nonlimited, limitratio, c21040):
    if c21060 > nonlimited and c00100 > limitratio:
        return c21060 - c21040
    return c21060


def ItemDed(puf, p):
    # Itemized Deductions
    global c04470
    global c21060
    global c21040
    global c17000
    global c18300
    global c20800
    global _sit

    # Medical #
    c17750 = 0.075 * _posagi
    c17000 = np.maximum(0, e17500 - c17750)

    # State and Local Income Tax, or Sales Tax #
    _sit1 = np.maximum(e18400, e18425)
    _sit = np.maximum(_sit1, 0)
    _statax = np.maximum(_sit, e18450)

    # Other Taxes #
    c18300 = _statax + e18500 + e18800 + e18900

    # Casulty #
    c37703 = casulty(e20500, e20500, _posagi)
    c20500 = casulty(e20500, c37703, _posagi)

    # Miscellaneous #
    c20750 = 0.02 * _posagi
    if puf == True:
        c20400 = e20400
        c19200 = e19200
    else:
        c20400 = e20550 + e20600 + e20950
        c19200 = e19500 + e19570 + e19400 + e19550
    c20800 = np.maximum(0, c20400 - c20750)

    # Charity (assumes carryover is non-cash)
    c19700 = charity(e19800, e20100, e20200, _posagi)
    # temporary fix!??

    # Gross Itemized Deductions #
    c21060 = (e20900 + c17000 + c18300 + c19200 + c19700
              + c20500 + c20800 + e21000 + e21010)

    # Itemized Deduction Limitation
    _phase2 = p._phase2[FLPDYR-p.DEFAULT_YR, MARS-1] # Eventually, get rid of _phase2

    _nonlimited = c17000 + c20500 + e19570 + e21010 + e20900
    _limitratio = _phase2/p._sep

    c21040 = item_ded_limit(c21060, c00100, _nonlimited, _limitratio, _posagi)
    c04470 = item_ded_vec(c21060, c00100, _nonlimited, _limitratio, c21040)

    outputs = (c17750, c17000, _sit1, _sit, _statax, c18300, c37703, c20500,
               c20750, c20400, c19200, c20800, c19700, c21060,
               _phase2, _nonlimited, _limitratio, c04470, c21040)

    header= ['c17750', 'c17000', '_sit1', '_sit', '_statax', 'c18300', 'c37703',
             'c20500', 'c20750', 'c20400', 'c19200', 'c20800', 'c19700',
             'c21060', '_phase2',
             '_nonlimited', '_limitratio', 'c04470', 'c21040']

    return DataFrame(data=np.column_stack(outputs), columns=header)


def EI_FICA(p):
    global _sey
    global _setax
    # Earned Income and FICA #
    global _earned
    _sey = e00900 + e02100
    _fica = np.maximum(0, .153 * np.minimum(p._ssmax[FLPDYR - p.DEFAULT_YR],
                                            e00200 + np.maximum(0, _sey) * 0.9235))
    _setax = np.maximum(0, _fica - 0.153 * e00200)
    _seyoff = np.where(_setax <= 14204, 0.5751 * _setax, 0.5 * _setax + 10067)

    c11055 = e11055

    _earned = np.maximum(0, e00200 + e00250 + e11055 + e30100 + _sey - _seyoff)

    outputs = (_sey, _fica, _setax, _seyoff, c11055, _earned)
    header = ['_sey', '_fica', '_setax', '_seyoff', 'c11055', '_earned']

    return DataFrame(data=np.column_stack(outputs), columns=header), _earned


@jit("void(float64[:], int64[:], int64[:], int64, int64[:,:], float64[:])", nopython=True)
def StdDed_c15100(_earned, DSI, FLPDYR, default_yr, _stded, c15100):
    for i in range(0, FLPDYR.shape[0]):
        if DSI[i] == 1:
            c15100[i] = np.maximum(300 + _earned[i], _stded[FLPDYR[i] - default_yr, 6])
        else:
            c15100[i] = 0


@jit("void(int64[:], int64[:], float64[:], int64[:], int64[:], float64[:], int64[:], int64, int64[:,:], float64[:])", nopython=True)
def StdDed_c04100(DSI, MARS, c15100, FLPDYR, MIdR, _earned, _compitem, default_yr, _stded, c04100):
    for i in range(0, MARS.shape[0]):
        if (DSI[i] == 1):
            c04100[i] = np.minimum( _stded[FLPDYR[i] - default_yr, MARS[i]-1], c15100[i])
        elif _compitem[i] == 1 or (3 <= MARS[i] and MARS[i] <=6 and MIdR[i] == 1):
            c04100[i] = 0
        else:
            c04100[i] = _stded[FLPDYR[i] - default_yr, MARS[i] - 1]


@vectorize(["int64(int64)"], nopython=True)
def StdDed_txpyers(MARS):
    if MARS == 2 or MARS == 3:
        return 2
    else:
        return 1


@jit("void(float64[:], int64[:], float64[:], float64[:], float64[:], int64[:], int64, int64[:], int64[:,:])", nopython=True)
def StdDed_c04200(c04200, MARS, e04200, _numextra, _exact, _txpyers, DEFAULT_YR, FLPDYR, _aged):
    for i in range(MARS.shape[0]):
        if _exact[i] == 1 and MARS[i] == 3 or MARS[i] == 5:
            c04200[i] = e04200[i]
        else:
            c04200[i] = _numextra[i] * _aged[FLPDYR[i] - DEFAULT_YR, _txpyers[i] - 1]


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


def StdDed(p):
    # Standard Deduction with Aged, Sched L and Real Estate #
    global c04800
    global c60000
    global _taxinc
    global _feitax
    global _standard


    c15100 = np.zeros((dim,))
    StdDed_c15100(_earned, DSI, FLPDYR, p.DEFAULT_YR, p._stded, c15100)

    _compitem = np.where(np.logical_and(e04470 > 0, e04470 < p._stded[FLPDYR-p.DEFAULT_YR, MARS-1]), 1, 0)

    c04100 = np.zeros((dim,))
    StdDed_c04100(DSI, MARS, c15100, FLPDYR, MIdR, _earned, _compitem,
                          p.DEFAULT_YR, p._stded, c04100)

    c04100 = c04100 + e15360
    _numextra = AGEP + AGES + PBI + SBI
    _txpyers = StdDed_txpyers(MARS)

    c04200 = np.zeros((dim,))
    StdDed_c04200(c04200, MARS, e04200, _numextra, _exact, _txpyers, p.DEFAULT_YR, FLPDYR, p._aged)

    c15200 = c04200

    _standard = StdDed_standard(MARS, c04100, c04470, c04200)

    _othded = np.where(FDED == 1, e04470 - c04470, 0)
    c04100 = np.where(FDED == 1, 0, c04100)
    c04200 = np.where(FDED == 1, 0, c04200)
    _standard = np.where(FDED == 1, 0, _standard)

    c04500 = c00100 - np.maximum(c21060 - c21040,
                                 np.maximum(c04100, _standard + e37717))
    c04800 = np.maximum(0, c04500 - c04600 - e04805)

    c60000 = np.where(_standard > 0, c00100, c04500)
    c60000 = c60000 - e04805

    # Some taxpayers iteimize only for AMT, not regular tax
    _amtstd = np.zeros((dim,))
    c60000 = StdDed_c60000(e04470, t04470, _amtstd, f6251, _exact, c00100, c60000)
    _taxinc = StdDed_taxinc(c04800, _feided, c02700)

    _feitax = np.zeros((dim,))
    _oldfei = np.zeros((dim,))

    taxer1 = Taxer(inc_in=_feided, inc_out=_feitax, MARS=MARS, p=p)
    _feitax = StdDed_feitax(c04800, _feided, taxer1, _feitax)

    taxer2 = Taxer(inc_in=c04800, inc_out=_oldfei, MARS=MARS, p=p)
    _oldfei = StdDed_oldfei(c04800, _feided, taxer2, _oldfei)


    SDoutputs = (c15100, _numextra, _txpyers, c15200,
                 _othded, c04100, c04200, _standard, c04500,
                 c04800, c60000, _amtstd, _taxinc, _feitax, _oldfei)

    header = ['c15100', '_numextra', '_txpyers', 'c15200',
              '_othded', 'c04100', 'c04200', '_standard',
              'c04500', 'c04800', 'c60000', '_amtstd', '_taxinc', '_feitax',
              '_oldfei']

    return DataFrame(data=np.column_stack(SDoutputs),
                     columns=header)


def XYZD(p):
    global c24580
    global _xyztax

    _xyztax = np.zeros((dim,))
    c05200 = np.zeros((dim,))
    _xyztax = Taxer(inc_in=_taxinc, inc_out=_xyztax, MARS=MARS, p=p)
    c05200 = Taxer(inc_in=c04800, inc_out=c05200, MARS=MARS, p=p)

    return DataFrame(data=np.column_stack((_xyztax, c05200)),
                     columns=['_xyztax', 'c05200'])


def NonGain():
    _cglong = np.minimum(c23650, e23250) + e01100
    _noncg = np.zeros((dim,))

    return DataFrame(data=np.column_stack((_cglong, _noncg)),
                     columns=['_cglong', '_noncg'])


def TaxGains(p):
    global c05750
    global c24517
    global _taxbc
    global c24516
    global c24520
    global c05700
    c24517 = np.zeros((dim,))
    c24520 = np.zeros((dim,))
    c24530 = np.zeros((dim,))
    c24540 = np.zeros((dim,))
    _dwks16 = np.zeros((dim,))

    _hasgain = np.zeros((dim,))

    _hasgain = np.where(np.logical_or(e01000 > 0, c23650 > 0), 1, _hasgain)
    _hasgain = np.where(np.logical_or(e23250 > 0, e01100 > 0), 1, _hasgain)
    _hasgain = np.where(e00650 > 0, 1, _hasgain)

    _dwks5 = np.where(
        np.logical_and(_taxinc > 0, _hasgain == 1), np.maximum(0, e58990 - e58980), 0)

    c00650 = e00650
    c24505 = np.where(
        np.logical_and(_taxinc > 0, _hasgain == 1), np.maximum(0, c00650 - _dwks5), 0)
    c24510 = np.where(np.logical_and(_taxinc > 0, _hasgain == 1), np.maximum(
        0, np.minimum(c23650, e23250)) + e01100, 0)
    # gain for tax computation

    c24510 = np.where(np.logical_and(
        _taxinc > 0, np.logical_and(_hasgain == 1, e01100 > 0)), e01100, c24510)
    # from app f 2008 drf

    _dwks9 = np.where(np.logical_and(_taxinc > 0, _hasgain == 1), np.maximum(
        0, c24510 - np.minimum(e58990, e58980)), 0)
    # e24516 gain less invest y

    c24516 = np.maximum(0, np.minimum(e23250, c23650)) + e01100
    c24580 = _xyztax

    c24516 = np.where(
        np.logical_and(_taxinc > 0, _hasgain == 1), c24505 + _dwks9, c24516)
    _dwks12 = np.where(np.logical_and(
        _taxinc > 0, _hasgain == 1), np.minimum(_dwks9, e24515 + e24518), 0)
    c24517 = np.where(
        np.logical_and(_taxinc > 0, _hasgain == 1), c24516 - _dwks12, 0)
    # gain less 25% and 28%

    c24520 = np.where(
        np.logical_and(_taxinc > 0, _hasgain == 1), np.maximum(0, _taxinc - c24517), 0)
    # tentative TI less schD gain

    c24530 = np.where(np.logical_and(_taxinc > 0, _hasgain == 1), np.minimum(
        p._brk2[FLPDYR - p.DEFAULT_YR, MARS - 1], _taxinc), 0)
    # minimum TI for bracket

    _dwks16 = np.where(
        np.logical_and(_taxinc > 0, _hasgain == 1), np.minimum(c24520, c24530), 0)
    _dwks17 = np.where(
        np.logical_and(_taxinc > 0, _hasgain == 1), np.maximum(0, _taxinc - c24516), 0)
    c24540 = np.where(
        np.logical_and(_taxinc > 0, _hasgain == 1), np.maximum(_dwks16, _dwks17), 0)

    c24534 = np.where(
        np.logical_and(_taxinc > 0, _hasgain == 1), c24530 - _dwks16, 0)
    _dwks21 = np.where(
        np.logical_and(_taxinc > 0, _hasgain == 1), np.minimum(_taxinc, c24517), 0)
    c24597 = np.where(
        np.logical_and(_taxinc > 0, _hasgain == 1), np.maximum(0, _dwks21 - c24534), 0)
    # income subject to 15% tax

    c24598 = 0.15 * c24597  # actual 15% tax

    _dwks25 = np.where(
        np.logical_and(_taxinc > 0, _hasgain == 1), np.minimum(_dwks9, e24515), 0)
    _dwks26 = np.where(
        np.logical_and(_taxinc > 0, _hasgain == 1), c24516 + c24540, 0)
    _dwks28 = np.where(
        np.logical_and(_taxinc > 0, _hasgain == 1), np.maximum(0, _dwks26 - _taxinc), 0)
    c24610 = np.where(
        np.logical_and(_taxinc > 0, _hasgain == 1), np.maximum(0, _dwks25 - _dwks28), 0)
    c24615 = np.where(
        np.logical_and(_taxinc > 0, _hasgain == 1), 0.25 * c24610, 0)
    _dwks31 = np.where(np.logical_and(
        _taxinc > 0, _hasgain == 1), c24540 + c24534 + c24597 + c24610, 0)
    c24550 = np.where(
        np.logical_and(_taxinc > 0, _hasgain == 1), np.maximum(0, _taxinc - _dwks31), 0)
    c24570 = np.where(
        np.logical_and(_taxinc > 0, _hasgain == 1), 0.28 * c24550, 0)
    _addtax = np.zeros((dim,))
    _addtax = np.where(np.logical_and(_taxinc > 0, np.logical_and(
        _hasgain == 1, c24540 > p._brk6[FLPDYR - p.DEFAULT_YR, MARS - 1])), 0.05 * c24517, _addtax)
    _addtax = np.where(np.logical_and(np.logical_and(_taxinc > 0, _hasgain == 1), np.logical_and(c24540 <= p._brk6[
                       FLPDYR - p.DEFAULT_YR, MARS - 1], _taxinc > p._brk6[FLPDYR - p.DEFAULT_YR, MARS - 1])), 0.05 * np.minimum(c04800 - p._brk6[FLPDYR - p.DEFAULT_YR, MARS - 1], c24517), _addtax)

    c24560 = np.zeros((dim,))
    c24560 = np.where(np.logical_and(_taxinc > 0, _hasgain == 1), Taxer(
        inc_in=c24540, inc_out=c24560, MARS=MARS, p=p), c24560)

    _taxspecial = np.where(np.logical_and(
        _taxinc > 0, _hasgain == 1), c24598 + c24615 + c24570 + c24560 + _addtax, 0)

    c24580 = np.where(np.logical_and(_taxinc > 0, _hasgain == 1), np.minimum(
        _taxspecial, _xyztax), c24580)
    # e24580 schedule D tax

    c05100 = c24580
    c05100 = np.where(np.logical_and(
        c04800 > 0, _feided > 0), np.maximum(0, c05100 - _feitax), c05100)

    # Form 4972 - Lump Sum Distributions
    c05700 = np.zeros((dim,))

    c59430 = np.where(_cmp == 1, np.maximum(0, e59410 - e59420), 0)
    c59450 = np.where(_cmp == 1, c59430 + e59440, 0)  # income plus lump sum
    c59460 = np.where(_cmp == 1, np.maximum(
        0, np.minimum(0.5 * c59450, 10000)) - 0.2 * np.maximum(0, c59450 - 20000), 0)
    _line17 = np.where(_cmp == 1, c59450 - c59460, 0)
    _line19 = np.where(_cmp == 1, c59450 - c59460 - e59470, 0)
    _line22 = np.where(np.logical_and(_cmp == 1, c59450 > 0), np.maximum(
        0, e59440 - e59440 * c59460 / c59450), 0)

    _line30 = np.where(
        _cmp == 1, 0.1 * np.maximum(0, c59450 - c59460 - e59470), 0)

    _line31 = np.where(_cmp == 1,
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

    _line32 = np.where(_cmp == 1, 10 * _line31, 0)
    _line36 = np.where(np.logical_and(_cmp == 1, e59440 == 0), _line32, 0)
    _line33 = np.where(np.logical_and(_cmp == 1, e59440 > 0), 0.1 * _line22, 0)
    _line34 = np.where(np.logical_and(_cmp == 1, e59440 > 0),
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
    _line35 = np.where(np.logical_and(_cmp == 1, e59440 > 0), 10 * _line34, 0)
    _line36 = np.where(
        np.logical_and(_cmp == 1, e59440 > 0), np.maximum(0, _line32 - _line35), 0)
    # tax saving from 10 yr option
    c59485 = np.where(_cmp == 1, _line36, 0)
    c59490 = np.where(_cmp == 1, c59485 + 0.2 * np.maximum(0, e59400), 0)
    # pension gains tax plus

    c05700 = np.where(_cmp == 1, c59490, 0)

    _s1291 = e10105
    _parents = e83200_0
    c05750 = np.maximum(c05100 + _parents + c05700, e74400)
    _taxbc = c05750

    outputs = (e00650, _hasgain, _dwks5, c24505, c24510, _dwks9, c24516,
               c24580, _dwks12, c24517, c24520, c24530, _dwks16,
               _dwks17, c24540, c24534, _dwks21, c24597, c24598, _dwks25,
               _dwks26, _dwks28, c24610, c24615, _dwks31, c24550, c24570,
               _addtax, c24560, _taxspecial, c05100, c05700, c59430,
               c59450, c59460, _line17, _line19, _line22, _line30, _line31,
               _line32, _line36, _line33, _line34, _line35, c59485, c59490,
               _s1291, _parents, c05750, _taxbc)

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
                     columns=header) , c05750


def MUI(c05750, p):
    # Additional Medicare tax on unearned Income
    c05750 = c05750
    c05750 = np.where(c00100 > p._thresx[MARS - 1], c05750 + 0.038 * np.minimum(
        e00300 + e00600 + np.maximum(0, c01000) + np.maximum(0, e02000), c00100 - p._thresx[MARS - 1]), c05750)

    return DataFrame(data=np.column_stack((c05750,)),
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
    #_agep = np.where(
    #    DOBYR > 0, np.ceil((12 * (FLPDYR - DOBYR) - DOBMD / 100) / 12), 0)
    if DOBYR > 0:
        return np.ceil((12 * (FLPDYR - DOBYR) - DOBMD / 100) / 12)
    else:
        return 0


@vectorize('float64(' + 2*'float64, ' + 'float64)', nopython=True)
def AMTI_ages(SDOBYR, FLPDYR, SDOBMD):
    #_ages = np.where(
    #    SDOBYR > 0, np.ceil((12 * (FLPDYR - SDOBYR) - SDOBMD / 100) / 12), 0)
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


def AMTI(puf, p):
    global c05800
    global _othtax
    global _agep
    global _ages
    c62720 = c24517 + x62720
    c60260 = e00700 + x60260
    c63100 = np.maximum(0, _taxbc - e07300)
    c60200 = np.minimum(c17000, 0.025 * _posagi)
    c60240 = c18300 + x60240
    c60220 = c20800 + x60220
    c60130 = c21040 + x60130
    c62730 = e24515 + x62730

    _amtded = AMTI_amtded(c60200, c60220, c60240, c60000)
    _addamt = AMTI_addamt(_exact, e60290, c60130, _amtded)

    c62100 = AMTI_c62100(_addamt, e60300, e60860, e60100, e60840, e60630, e60550,
                e60720, e60430, e60500, e60340, e60680, e60600, e60405,
                e60440, e60420, e60410, e61400, e60660, c60260, e60480,
                e62000, c60000, _cmp, e60250)


    _edical = AMTI_edical(puf, _standard, _exact, e04470, e17500, e00100)

    _cmbtp = AMTI_cmbtp(puf, _standard, _exact, e04470, f6251, _edical, e00100,
              e62100, c60260, e21040, _sit, e18500, e20800)

    c62100 = AMTI_c62100_2(puf, _standard, _exact, e04470, c00100, c04470, c17000,
                  e18500, c60260, c20800, c21040, _cmbtp, c62100, _sit)

    _cmbtp = AMTI_cmbtp_2(puf, _standard, f6251, e62100, e00100, c60260, _cmbtp)
    c62100 = AMTI_c62100_3(puf, _standard, c00100, c60260, _cmbtp, c62100)

    #TODO
    _amtsepadd = np.where(np.logical_and(c62100 > p._amtsep[FLPDYR - p.DEFAULT_YR], np.logical_or(MARS == 3, MARS == 6)), np.maximum(
        0, np.minimum(p._almsep[FLPDYR - p.DEFAULT_YR], 0.25 * (c62100 - p._amtsep[FLPDYR - p.DEFAULT_YR]))), 0)

    #TODO
    c62100 = np.where(np.logical_and(c62100 > p._amtsep[
                      FLPDYR - p.DEFAULT_YR], np.logical_or(MARS == 3, MARS == 6)), c62100 + _amtsepadd, c62100)

    #TODO
    c62600 = np.maximum(0, p._amtex[
                        FLPDYR - p.DEFAULT_YR, MARS - 1] - 0.25 * np.maximum(0, c62100 - p._amtys[FLPDYR - p.DEFAULT_YR, MARS - 1]))

    _agep = AMTI_agep(DOBYR, FLPDYR, DOBMD)

    _ages = AMTI_ages(SDOBYR, FLPDYR, SDOBMD)

    c62600 = AMTI_c62600(_cmp, f6251, _exact, e62600, c62600)

    #TODO
    c62600 = np.where(np.logical_and(np.logical_and(_cmp == 1, _exact == 0), np.logical_and(
        _agep < p._amtage[FLPDYR - p.DEFAULT_YR], _agep != 0)), np.minimum(c62600, _earned + p._almdep[FLPDYR - p.DEFAULT_YR]), c62600)

    c62700 = np.maximum(0, c62100 - c62600)

    _alminc = c62700
    _amtfei = np.zeros((dim,))

    _alminc = AMTI_alminc(c62100, c62600, c02700, _alminc)

    #TODO
    _amtfei = np.where(c02700 > 0, 0.26 * c02700 + 0.02 *
                       np.maximum(0, c02700 - p._almsp[FLPDYR - p.DEFAULT_YR] / p._sep), _amtfei)

    #TODO
    c62780 = 0.26 * _alminc + 0.02 * \
        np.maximum(0, _alminc - p._almsp[FLPDYR - p.DEFAULT_YR] / p._sep) - _amtfei

    c62900 = np.where(f6251 != 0, e62900, e07300)
    c63000 = c62780 - c62900

    c62740 = np.minimum(np.maximum(0, c24516 + x62740), c62720 + c62730)
    c62740 = np.where(c24516 == 0, c62720 + c62730, c62740)

    _ngamty = np.maximum(0, _alminc - c62740)

    c62745 = 0.26 * _ngamty + 0.02 * \
        np.maximum(0, _ngamty - p._almsp[FLPDYR - p.DEFAULT_YR] / p._sep)
    y62745 = p._almsp[FLPDYR - p.DEFAULT_YR] / p._sep
    _tamt2 = np.zeros((dim,))

    _amt5pc = np.zeros((dim,))
    #TODO
    _amt15pc = np.minimum(_alminc, c62720) - _amt5pc - np.minimum(np.maximum(
        0, p._brk2[FLPDYR - p.DEFAULT_YR, MARS - 1] - c24520), np.minimum(_alminc, c62720))
    #TODO
    _amt15pc = np.where(c04800 == 0, np.maximum(
        0, np.minimum(_alminc, c62720) - p._brk2[FLPDYR - p.DEFAULT_YR, MARS - 1]), _amt15pc)
    _amt25pc = np.minimum(_alminc, c62740) - np.minimum(_alminc, c62720)

    _amt25pc = np.where(c62730 == 0, 0, _amt25pc)
    c62747 = p._cgrate1[FLPDYR - p.DEFAULT_YR] * _amt5pc
    c62755 = p._cgrate2[FLPDYR - p.DEFAULT_YR] * _amt15pc
    c62770 = 0.25 * _amt25pc
    _tamt2 = c62747 + c62755 + c62770

    _amt = np.zeros((dim,))
    #TODO
    _amt = np.where(_ngamty > p._brk6[
                    FLPDYR - p.DEFAULT_YR, MARS - 1], 0.05 * np.minimum(_alminc, c62740), _amt)
    #TODO
    _amt = np.where(np.logical_and(_ngamty <= p._brk6[FLPDYR - p.DEFAULT_YR, MARS - 1], _alminc > p._brk6[
                    FLPDYR - p.DEFAULT_YR, MARS - 1]), 0.05 * np.minimum(_alminc - p._brk6[FLPDYR - p.DEFAULT_YR, MARS - 1], c62740), _amt)

    _tamt2 = _tamt2 + _amt

    c62800 = np.minimum(c62780, c62745 + _tamt2 - _amtfei)
    c63000 = c62800 - c62900
    c63100 = _taxbc - e07300 - c05700
    c63100 = c63100 + e10105

    c63100 = np.maximum(0, c63100)
    c63200 = np.maximum(0, c63000 - c63100)
    c09600 = c63200
    _othtax = e05800 - (e05100 + e09600)

    c05800 = _taxbc + c63200

    outputs = (c62720, c60260, c63100, c60200, c60240, c60220, c60130,
               c62730, _addamt, c62100, _cmbtp, _edical, _amtsepadd,
               _agep, _ages, c62600, c62700, _alminc, _amtfei, c62780,
               c62900, c63000, c62740, _ngamty, c62745, y62745, _tamt2,
               _amt5pc, _amt15pc, _amt25pc, c62747, c62755, c62770, _amt,
               c62800, c09600, _othtax, c05800)

    header = ['c62720', 'c60260', 'c63100', 'c60200', 'c60240', 'c60220',
              'c60130', 'c62730', '_addamt', 'c62100', '_cmbtp', '_edical',
              '_amtsepadd', '_agep', '_ages', 'c62600', 'c62700',
              '_alminc', '_amtfei', 'c62780', 'c62900', 'c63000', 'c62740',
              '_ngamty', 'c62745', 'y62745', '_tamt2', '_amt5pc', '_amt15pc',
              '_amt25pc', 'c62747', 'c62755', 'c62770', '_amt', 'c62800',
              'c09600', '_othtax', 'c05800']

    return DataFrame(data=np.column_stack(outputs),
                     columns=header), c05800


def F2441(puf, _earned, p):
    global c32880
    global c32890
    global c32800
    global _dclim
    _earned = _earned
    _earned = np.where(_fixeic == 1, e59560, _earned)
    c32880 = np.where(np.logical_and(MARS == 2, puf == True), 0.5 * _earned, 0)
    c32890 = np.where(np.logical_and(MARS == 2, puf == True), 0.5 * _earned, 0)
    c32880 = np.where(
        np.logical_and(MARS == 2, puf == False), np.maximum(0, e32880), c32880)
    c32890 = np.where(
        np.logical_and(MARS == 2, puf == False), np.maximum(0, e32890), c32890)
    c32880 = np.where(MARS != 2, _earned, c32880)
    c32890 = np.where(MARS != 2, _earned, c32890)

    _ncu13 = np.zeros((dim,))
    _ncu13 = np.where(puf == True, f2441, _ncu13)
    _ncu13 = np.where(
        np.logical_and(puf == False, CDOB1 > 0), _ncu13 + 1, _ncu13)
    _ncu13 = np.where(
        np.logical_and(puf == False, CDOB2 > 0), _ncu13 + 1, _ncu13)

    _dclim = np.minimum(_ncu13, 2) * p._dcmax[FLPDYR - p.DEFAULT_YR]
    c32800 = np.minimum(np.maximum(e32800, e32750 + e32775), _dclim)

    outputs = (_earned, c32880, c32890, _ncu13, _dclim, c32800)
    header = ['_earned', 'c32880', 'c32890', '_ncu13', '_dclim', 'c32800']

    return DataFrame(data=np.column_stack(outputs), columns=header), c32800


def DepCareBen(c32800, p):
    global c33000
    c32800 = c32800
    # Part III ofdependent care benefits
    _seywage = np.where(np.logical_and(_cmp == 1, MARS == 2), np.minimum(
        c32880, np.minimum(c32890, np.minimum(e33420 + e33430 - e33450, e33460))), 0)
    _seywage = np.where(np.logical_and(_cmp == 1, MARS != 2), np.minimum(
        c32880, np.minimum(e33420 + e33430 - e33450, e33460)), _seywage)

    c33465 = np.where(_cmp == 1, e33465, 0)
    c33470 = np.where(_cmp == 1, e33470, 0)
    c33475 = np.where(
        _cmp == 1, np.maximum(0, np.minimum(_seywage, 5000 / p._sep) - c33470), 0)
    c33480 = np.where(
        _cmp == 1, np.maximum(0, e33420 + e33430 - e33450 - c33465 - c33475), 0)
    c32840 = np.where(_cmp == 1, c33470 + c33475, 0)
    c32800 = np.where(_cmp == 1, np.minimum(
        np.maximum(0, _dclim - c32840), np.maximum(0, e32750 + e32775 - c32840)), c32800)

    c33000 = np.where(
        MARS == 2, np.maximum(0, np.minimum(c32800, np.minimum(c32880, c32890))), 0)
    c33000 = np.where(
        MARS != 2, np.maximum(0, np.minimum(c32800, _earned)), c33000)

    outputs = (_seywage, c33465, c33470, c33475, c33480, c32840, c32800,
               c33000)
    header = ['_seywage', 'c33465', 'c33470', 'c33475', 'c33480', 'c32840',
              'c32800', 'c33000']

    return DataFrame(data=np.column_stack(outputs),
                     columns=header)


def ExpEarnedInc(p):
    global c07180
    # Expenses limited to earned income

    _tratio = np.where(_exact == 1, np.ceil(
        np.maximum((c00100 - p._agcmax[FLPDYR - p.DEFAULT_YR]) / 2000, 0)), 0)
    c33200 = np.where(_exact == 1, c33000 * 0.01 * np.maximum(20,
                                                              _pcmax[FLPDYR - p.DEFAULT_YR] - np.minimum(15, _tratio)), 0)
    c33200 = np.where(_exact != 1, c33000 * 0.01 * np.maximum(20, _pcmax[
                      FLPDYR - p.DEFAULT_YR] - np.maximum((c00100 - p._agcmax[FLPDYR - p.DEFAULT_YR]) / 2000, 0)), c33200)

    c33400 = np.minimum(np.maximum(0, c05800 - e07300), c33200)
    # amount of the credit

    c07180 = np.where(e07180 == 0, 0, c33400)

    return DataFrame(data=np.column_stack((_tratio, c33200, c33400, c07180)),
                     columns=['_tratio', 'c33200', 'c33400', 'c07180'])

def RateRed(c05800):
    global c59560
    global c07970
    # rate reduction credit for 2001 only, is this needed?
    c05800 = c05800
    c07970 = np.zeros((dim,))

    c05800 = np.where(_fixup >= 3, c05800 + _othtax, c05800)

    c59560 = np.where(_exact == 1, x59560, _earned)

    return DataFrame(data=np.column_stack((c07970, c05800, c59560)),
                     columns=['c07970', 'c05800', 'c59560'])


def NumDep(puf, p):
    global c59660
    # Number of dependents for EIC

    _ieic = np.zeros((dim,))

    EICYB1_1 = np.where(EICYB1 < 0, 0.0, EICYB1)
    EICYB2_2 = np.where(EICYB2 < 0, 0.0, EICYB2)
    EICYB3_3 = np.where(EICYB3 < 0, 0.0, EICYB3)

    _ieic = np.where(puf == True, EIC, EICYB1_1 + EICYB2_2 + EICYB3_3)

    _ieic = _ieic.astype(int)

    # Modified AGI only through 2002

    _modagi = c00100 + e00400
    c59660 = np.zeros((dim,))

    _val_ymax = np.where(np.logical_and(MARS == 2, _modagi > 0), p._ymax[
                         _ieic, FLPDYR - p.DEFAULT_YR] + p._joint[FLPDYR - p.DEFAULT_YR, _ieic], 0)
    _val_ymax = np.where(np.logical_and(_modagi > 0, np.logical_or(MARS == 1, np.logical_or(
        MARS == 4, np.logical_or(MARS == 5, MARS == 7)))), p._ymax[_ieic, FLPDYR - p.DEFAULT_YR], _val_ymax)
    c59660 = np.where(np.logical_and(_modagi > 0, np.logical_or(MARS == 1, np.logical_or(MARS == 4, np.logical_or(MARS == 5, np.logical_or(
        MARS == 2, MARS == 7))))), np.minimum(p._rtbase[FLPDYR - p.DEFAULT_YR, _ieic] * c59560, p._crmax[FLPDYR - p.DEFAULT_YR, _ieic]), c59660)
    _preeitc = np.where(np.logical_and(_modagi > 0, np.logical_or(MARS == 1, np.logical_or(
        MARS == 4, np.logical_or(MARS == 5, np.logical_or(MARS == 2, MARS == 7))))), c59660, 0)

    c59660 = np.where(np.logical_and(np.logical_and(MARS != 3, MARS != 6), np.logical_and(_modagi > 0, np.logical_or(
        _modagi > _val_ymax, c59560 > _val_ymax))), np.maximum(0, c59660 - p._rtless[FLPDYR - p.DEFAULT_YR, _ieic] * (np.maximum(_modagi, c59560) - _val_ymax)), c59660)
    _val_rtbase = np.where(np.logical_and(np.logical_and(
        MARS != 3, MARS != 6), _modagi > 0), p._rtbase[FLPDYR - p.DEFAULT_YR, _ieic] * 100, 0)
    _val_rtless = np.where(np.logical_and(np.logical_and(
        MARS != 3, MARS != 6), _modagi > 0), p._rtless[FLPDYR - p.DEFAULT_YR, _ieic] * 100, 0)

    _dy = np.where(np.logical_and(np.logical_and(MARS != 3, MARS != 6), _modagi > 0), e00400 + e83080 + e00300 + e00600
                   +
                   np.maximum(0, np.maximum(0, e01000) - np.maximum(0, e40223))
                   + np.maximum(0, np.maximum(0, e25360) -
                                e25430 - e25470 - e25400 - e25500)
                   + np.maximum(0, e26210 + e26340 + e27200 - np.absolute(e26205) - np.absolute(e26320)), 0)

    c59660 = np.where(np.logical_and(np.logical_and(MARS != 3, MARS != 6), np.logical_and(
        _modagi > 0, _dy > p._dylim[FLPDYR - p.DEFAULT_YR])), 0, c59660)

    c59660 = np.where(np.logical_and(np.logical_and(_cmp == 1, _ieic == 0), np.logical_and(np.logical_and(
        SOIYR - DOBYR >= 25, SOIYR - DOBYR < 65), np.logical_and(SOIYR - SDOBYR >= 25, SOIYR - SDOBYR < 65))), 0, c59660)
    c59660 = np.where(np.logical_and(_ieic == 0, np.logical_or(np.logical_or(
        _agep < 25, _agep >= 65), np.logical_or(_ages < 25, _ages >= 65))), 0, c59660)

    outputs = (_ieic, EICYB1, EICYB2, EICYB3, _modagi, c59660,
               _val_ymax, _preeitc, _val_rtbase, _val_rtless, _dy)
    header = ['_ieic', 'EICYB1', 'EICYB2', 'EICYB3', '_modagi',
              'c59660', '_val_ymax', '_preeitc', '_val_rtbase',
              '_val_rtless', '_dy']

    return DataFrame(data=np.column_stack(outputs), columns=header)

def ChildTaxCredit(p):
    global _num
    global c07230
    global _precrd
    global _nctcr
    global c07220
    # Child Tax Credit

    c11070 = np.zeros((dim,))
    c07220 = np.zeros((dim,))
    c07230 = np.zeros((dim,))
    _precrd = np.zeros((dim,))

    _num = np.ones((dim,))
    _num = np.where(MARS == 2, 2, _num)

    _nctcr = np.zeros((dim,))
    _nctcr = np.where(SOIYR >= 2002, n24, _nctcr)
    _nctcr = np.where(
        np.logical_and(SOIYR < 2002, p._chmax[FLPDYR - p.DEFAULT_YR] > 0), xtxcr1xtxcr10, _nctcr)
    _nctcr = np.where(
        np.logical_and(SOIYR < 2002, p._chmax[FLPDYR - p.DEFAULT_YR] <= 0), XOCAH, _nctcr)

    _precrd = p._chmax[FLPDYR - p.DEFAULT_YR] * _nctcr
    _ctcagi = c00100 + _feided

    _precrd = np.where(np.logical_and(_ctcagi > p._cphase[MARS - 1], _exact == 1), np.maximum(
        0, _precrd - 50 * np.ceil(_ctcagi - p._cphase[MARS - 1]) / 1000), _precrd)
    _precrd = np.where(np.logical_and(_ctcagi > p._cphase[MARS - 1], _exact != 1), np.maximum(
        0, _precrd - 50 * (np.maximum(0, _ctcagi - p._cphase[MARS - 1]) + 500) / 1000), _precrd)

    outputs = (c11070, c07220, c07230, _num, _nctcr, _precrd, _ctcagi)
    header = ['c11070', 'c07220', 'c07230', '_num', '_nctcr',
              '_precrd', '_ctcagi']

    return DataFrame(data=np.column_stack(outputs), columns=header)


# def HopeCredit():
    # W/o congressional action, Hope Credit will replace 
    # American opportunities credit in 2018. NEED TO ADD LOGIC!!!


def AmOppCr():
    global c87521
    # American Opportunity Credit 2009+
    c87482 = np.where(_cmp == 1, np.maximum(0, np.minimum(e87482, 4000)), 0)
    c87487 = np.where(_cmp == 1, np.maximum(0, np.minimum(e87487, 4000)), 0)
    c87492 = np.where(_cmp == 1, np.maximum(0, np.minimum(e87492, 4000)), 0)
    c87497 = np.where(_cmp == 1, np.maximum(0, np.minimum(e87497, 4000)), 0)

    c87483 = np.where(np.maximum(0, c87482 - 2000) == 0,
                      c87482, 2000 + 0.25 * np.maximum(0, c87482 - 2000))
    c87488 = np.where(np.maximum(0, c87487 - 2000) == 0,
                      c87487, 2000 + 0.25 * np.maximum(0, c87487 - 2000))
    c87493 = np.where(np.maximum(0, c87492 - 2000) == 0,
                      c87492, 2000 + 0.25 * np.maximum(0, c87492 - 2000))
    c87498 = np.where(np.maximum(0, c87497 - 2000) == 0,
                      c87497, 2000 + 0.25 * np.maximum(0, c87497 - 2000))

    c87521 = c87483 + c87488 + c87493 + c87498

    outputs = (c87482, c87487, c87492, c87497,
               c87483, c87488, c87493, c87498, c87521)
    header = ['c87482', 'c87487', 'c87492', 'c87497', 'c87483', 'c87488',
              'c87493', 'c87498', 'c87521']

    return DataFrame(data=np.column_stack(outputs), columns=header)


def LLC(puf, p):
    # Lifetime Learning Credit
    global c87550

    c87540 = np.where(
        puf == True, np.minimum(e87530, p._learn[FLPDYR - p.DEFAULT_YR]), 0)
    c87550 = np.where(puf == True, 0.2 * c87540, 0)

    c87530 = np.where(puf == False, e87526 + e87522 + e87524 + e87528, 0)
    c87540 = np.where(
        puf == False, np.minimum(c87530, p._learn[FLPDYR - p.DEFAULT_YR]), c87540)
    c87550 = np.where(puf == False, 0.2 * c87540, c87550)

    outputs = (c87540, c87550, c87530)
    header = ['c87540', 'c87550', 'c87530']
    return DataFrame(data=np.column_stack(outputs), columns=header), c87550


def RefAmOpp():
    # Refundable American Opportunity Credit 2009+

    c87668 = np.zeros((dim,))

    c87654 = np.where(np.logical_and(_cmp == 1, c87521 > 0), 90000 * _num, 0)
    c87656 = np.where(np.logical_and(_cmp == 1, c87521 > 0), c00100, 0)
    c87658 = np.where(
        np.logical_and(_cmp == 1, c87521 > 0), np.maximum(0, c87654 - c87656), 0)
    c87660 = np.where(np.logical_and(_cmp == 1, c87521 > 0), 10000 * _num, 0)
    c87662 = np.where(np.logical_and(_cmp == 1, c87521 > 0),
                      1000 * np.minimum(1, c87658 / c87660), 0)
    c87664 = np.where(
        np.logical_and(_cmp == 1, c87521 > 0), c87662 * c87521 / 1000, 0)
    c87666 = np.where(np.logical_and(
        _cmp == 1, np.logical_and(c87521 > 0, EDCRAGE == 1)), 0, 0.4 * c87664)
    c10960 = np.where(np.logical_and(_cmp == 1, c87521 > 0), c87666, 0)
    c87668 = np.where(
        np.logical_and(_cmp == 1, c87521 > 0), c87664 - c87666, 0)
    c87681 = np.where(np.logical_and(_cmp == 1, c87521 > 0), c87666, 0)

    outputs = (c87654, c87656, c87658, c87660, c87662,
               c87664, c87666, c10960, c87668, c87681)
    header = ['c87654', 'c87656', 'c87658', 'c87660', 'c87662', 'c87664',
              'c87666', 'c10960', 'c87668', 'c87681']
    return DataFrame(data=np.column_stack(outputs), columns=header)


def NonEdCr(c87550, p):
    global c07220
    # Nonrefundable Education Credits

    # Form 8863 Tentative Education Credits
    c87560 = c87550

    # Phase Out
    c87570 = np.where(
        MARS == 2, _edphhm[FLPDYR - p.DEFAULT_YR] * 1000, p._edphhs[FLPDYR - p.DEFAULT_YR] * 1000)
    c87580 = c00100
    c87590 = np.maximum(0, c87570 - c87580)
    c87600 = 10000 * _num
    c87610 = np.minimum(1, c87590 / c87600)
    c87620 = c87560 * c87610

    _ctc1 = c07180 + e07200 + c07230
    _ctc2 = np.zeros((dim,))

    _ctc2 = e07240 + e07960 + e07260 + e07300
    _regcrd = _ctc1 + _ctc2
    _exocrd = e07700 + e07250
    _exocrd = _exocrd + t07950
    _ctctax = c05800 - _regcrd - _exocrd
    c07220 = np.minimum(_precrd, np.maximum(0, _ctctax))
    # lt tax owed

    outputs = (c87560, c87570, c87580, c87590, c87600, c87610,
               c87620, _ctc1, _ctc2, _regcrd, _exocrd, _ctctax, c07220)
    header = ['c87560', 'c87570', 'c87580', 'c87590', 'c87600', 'c87610',
              'c87620', '_ctc1', '_ctc2', '_regcrd', '_exocrd', '_ctctax',
              'c07220']
    return DataFrame(data=np.column_stack(outputs), columns=header)


def AddCTC(puf, p):
    # Additional Child Tax Credit

    c82940 = np.zeros((dim,))

    # Part I of 2005 form 8812
    c82925 = np.where(_nctcr > 0, _precrd, 0)
    c82930 = np.where(_nctcr > 0, c07220, 0)
    c82935 = np.where(_nctcr > 0, c82925 - c82930, 0)
    # CTC not applied to tax

    c82880 = np.where(_nctcr > 0, np.maximum(
        0, e00200 + e82882 + e30100 + np.maximum(0, _sey) - 0.5 * _setax), 0)
    c82880 = np.where(np.logical_and(_nctcr > 0, _exact == 1), e82880, c82880)
    h82880 = np.where(_nctcr > 0, c82880, 0)
    c82885 = np.where(
        _nctcr > 0, np.maximum(0, c82880 - p._ealim[FLPDYR - p.DEFAULT_YR]), 0)
    c82890 = np.where(_nctcr > 0, p._adctcrt[FLPDYR - p.DEFAULT_YR] * c82885, 0)

    # Part II of 2005 form 8812
    c82900 = np.where(np.logical_and(_nctcr > 2, c82890 < c82935),
                      0.0765 * np.minimum(p._ssmax[FLPDYR - p.DEFAULT_YR], c82880), 0)
    c82905 = np.where(
        np.logical_and(_nctcr > 2, c82890 < c82935), e03260 + e09800, 0)
    c82910 = np.where(
        np.logical_and(_nctcr > 2, c82890 < c82935), c82900 + c82905, 0)
    c82915 = np.where(
        np.logical_and(_nctcr > 2, c82890 < c82935), c59660 + e11200, 0)
    c82920 = np.where(
        np.logical_and(_nctcr > 2, c82890 < c82935), np.maximum(0, c82910 - c82915), 0)
    c82937 = np.where(
        np.logical_and(_nctcr > 2, c82890 < c82935), np.maximum(c82890, c82920), 0)

    # Part II of 2005 form 8812
    c82940 = np.where(
        np.logical_and(_nctcr > 2, c82890 >= c82935), c82935, c82940)
    c82940 = np.where(
        np.logical_and(_nctcr > 2, c82890 < c82935), np.minimum(c82935, c82937), c82940)

    c11070 = np.where(_nctcr > 0, c82940, 0)

    e59660 = np.where(
        np.logical_and(puf == True, _nctcr > 0), e59680 + e59700 + e59720, 0)
    _othadd = np.where(_nctcr > 0, e11070 - c11070, 0)

    c11070 = np.where(
        np.logical_and(_nctcr > 0, _fixup >= 4), c11070 + _othadd, c11070)

    outputs = (c82925, c82930, c82935, c82880, h82880, c82885, c82890,
               c82900, c82905, c82910, c82915, c82920, c82937, c82940, c11070,
               e59660, _othadd)

    header = ['c82925', 'c82930', 'c82935', 'c82880', 'h82880',
              'c82885', 'c82890', 'c82900', 'c82905', 'c82910', 'c82915',
              'c82920', 'c82937', 'c82940', 'c11070', 'e59660', '_othadd']

    return DataFrame(data=np.column_stack(outputs), columns=header)


def F5405():
    # Form 5405 First-Time Homebuyer Credit
    #not needed

    c64450 = np.zeros((dim,))
    return DataFrame(data=np.column_stack((c64450,)), columns=['c64450'])

def C1040(puf):
    global c08795
    global c09200
    global c07100
    global _eitc
    # Credits 1040 line 48

    x07400 = e07400
    c07100 = (e07180 + e07200 + c07220 + c07230 + e07250
              + e07600 + e07260 + c07970 + e07300 + x07400
              + e07500 + e07700 + e08000)

    y07100 = c07100

    c07100 = c07100 + e07240
    c07100 = c07100 + e08001
    c07100 = c07100 + e07960 + e07970
    c07100 = np.where(SOIYR >= 2009, c07100 + e07980, c07100)

    x07100 = c07100
    c07100 = np.minimum(c07100, c05800)

    # Tax After credits 1040 line 52

    _eitc = c59660
    c08795 = np.maximum(0, c05800 - c07100)

    c08800 = c08795
    e08795 = np.where(puf == True, e08800, 0)

    # Tax before refundable credits

    c09200 = c08795 + e09900 + e09400 + e09800 + e10000 + e10100
    c09200 = c09200 + e09700
    c09200 = c09200 + e10050
    c09200 = c09200 + e10075
    c09200 = c09200 + e09805
    c09200 = c09200 + e09710 + e09720

    outputs = (c07100, y07100, x07100, c08795, c08800, e08795, c09200)
    header = ['c07100', 'y07100', 'x07100', 'c08795', 'c08800', 'e08795',
              'c09200']
    return DataFrame(data=np.column_stack(outputs), columns=header), _eitc


def DEITC():
    global c59700
    global c10950
    # Decomposition of EITC

    c59680 = np.where(np.logical_and(
        c08795 > 0, np.logical_and(c59660 > 0, c08795 <= c59660)), c08795, 0)
    _comb = np.where(np.logical_and(
        c08795 > 0, np.logical_and(c59660 > 0, c08795 <= c59660)), c59660 - c59680, 0)

    c59680 = np.where(np.logical_and(
        c08795 > 0, np.logical_and(c59660 > 0, c08795 > c59660)), c59660, c59680)
    _comb = np.where(np.logical_and(
        c08795 > 0, np.logical_and(c59660 > 0, c08795 > c59660)), 0, _comb)

    c59700 = np.where(np.logical_and(c08795 > 0, np.logical_and(c59660 > 0, np.logical_and(
        _comb > 0, np.logical_and(c09200 - c08795 > 0, c09200 - c08795 > _comb)))), _comb, 0)
    c59700 = np.where(np.logical_and(c08795 > 0, np.logical_and(c59660 > 0, np.logical_and(
        _comb > 0, np.logical_and(c09200 - c08795 > 0, c09200 - c08795 <= _comb)))), c09200 - c08795, c59700)
    c59720 = np.where(np.logical_and(c08795 > 0, np.logical_and(c59660 > 0, np.logical_and(
        _comb > 0, np.logical_and(c09200 - c08795 > 0, c09200 - c08795 <= _comb)))), c59660 - c59680 - c59700, 0)

    c59680 = np.where(np.logical_and(c08795 == 0, c59660 > 0), 0, c59680)
    c59700 = np.where(np.logical_and(c08795 == 0, np.logical_and(
        c59660 > 0, np.logical_and(c09200 > 0, c09200 > c59660))), c59660, c59700)
    c59700 = np.where(np.logical_and(c08795 == 0, np.logical_and(
        c59660 > 0, np.logical_and(c09200 > 0, c09200 < c59660))), c09200, c59700)
    c59720 = np.where(np.logical_and(c08795 == 0, np.logical_and(
        c59660 > 0, np.logical_and(c09200 > 0, c09200 < c59660))), c59660 - c59700, c59720)
    c59720 = np.where(np.logical_and(
        c08795 == 0, np.logical_and(c59660 > 0, c09200 <= 0)), c59660 - c59700, c59720)

    # Ask dan about this section of code! Line 1231 - 1241

    _compb = np.where(np.logical_or(c08795 < 0, c59660 <= 0), 0, 0)
    c59680 = np.where(np.logical_or(c08795 < 0, c59660 <= 0), 0, c59680)
    c59700 = np.where(np.logical_or(c08795 < 0, c59660 <= 0), 0, c59700)
    c59720 = np.where(np.logical_or(c08795 < 0, c59660 <= 0), 0, c59720)

    c07150 = c07100 + c59680
    c07150 = c07150
    c10950 = np.zeros((dim,))

    outputs = (c59680, c59700, c59720, _comb, c07150, c10950)
    header = ['c59680', 'c59700', 'c59720', '_comb', 'c07150', 'c10950']

    return DataFrame(data=np.column_stack(outputs), columns=header)


def SOIT(_eitc):
    _eitc = _eitc

    # SOI Tax (Tax after non-refunded credits plus tip penalty)
    c10300 = c09200 - e10000 - e59680 - c59700
    c10300 = c10300 - e11070
    c10300 = c10300 - e11550
    c10300 = c10300 - e11580
    c10300 = c10300 - e09710 - e09720 - e11581 - e11582
    c10300 = c10300 - e87900 - e87905 - e87681 - e87682
    c10300 = c10300 - c10300 - c10950 - e11451 - e11452
    c10300 = c09200 - e09710 - e09720 - e10000 - e11601 - e11602
    c10300 = np.maximum(c10300, 0)

    # Ignore refundable partof _eitc to obtain SOI income tax

    _eitc = np.where(c09200 <= _eitc, c09200, _eitc)
    c10300 = np.where(c09200 <= _eitc, 0, c10300)

    outputs = (c10300, _eitc)
    header = ['c10300', '_eitc']
    return DataFrame(data=np.column_stack(outputs), columns=header)


def Taxer(inc_in, inc_out, MARS, p):
    low = np.where(inc_in < 3000, 1, 0)
    med = np.where(np.logical_and(inc_in >= 3000, inc_in < 100000), 1, 0)

    _a1 = inc_in * 0.01
    _a2 = np.floor(_a1)
    _a3 = _a2 * 100
    _a4 = (_a1 - _a2) * 100

    _a5 = np.zeros((dim,))
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

    inc_out = (p._rt1[FLPDYR - p.DEFAULT_YR] * np.minimum(_a6, p._brk1[FLPDYR - p.DEFAULT_YR, MARS - 1])
               + p._rt2[FLPDYR - p.DEFAULT_YR]
               * np.minimum(p._brk2[FLPDYR - p.DEFAULT_YR, MARS - 1] - p._brk1[FLPDYR - p.DEFAULT_YR, MARS - 1],
                            np.maximum(0., _a6 - p._brk1[FLPDYR - p.DEFAULT_YR, MARS - 1]))
               + p._rt3[FLPDYR - p.DEFAULT_YR]
               * np.minimum(p._brk3[FLPDYR - p.DEFAULT_YR, MARS - 1] - p._brk2[FLPDYR - p.DEFAULT_YR, MARS - 1],
                            np.maximum(0., _a6 - p._brk2[FLPDYR - p.DEFAULT_YR, MARS - 1]))
               + p._rt4[FLPDYR - p.DEFAULT_YR]
               * np.minimum(p._brk4[FLPDYR - p.DEFAULT_YR, MARS - 1] - p._brk3[FLPDYR - p.DEFAULT_YR, MARS - 1],
                            np.maximum(0., _a6 - p._brk3[FLPDYR - p.DEFAULT_YR, MARS - 1]))
               + p._rt5[FLPDYR - p.DEFAULT_YR]
               * np.minimum(p._brk5[FLPDYR - p.DEFAULT_YR, MARS - 1] - p._brk4[FLPDYR - p.DEFAULT_YR, MARS - 1],
                            np.maximum(0., _a6 - p._brk4[FLPDYR - p.DEFAULT_YR, MARS - 1]))
               + p._rt6[FLPDYR - p.DEFAULT_YR]
               * np.minimum(p._brk6[FLPDYR - p.DEFAULT_YR, MARS - 1] - p._brk5[FLPDYR - p.DEFAULT_YR, MARS - 1],
                            np.maximum(0., _a6 - p._brk5[FLPDYR - p.DEFAULT_YR, MARS - 1]))
               + p._rt7[FLPDYR - p.DEFAULT_YR] * np.maximum(0., _a6 - p._brk6[FLPDYR - p.DEFAULT_YR, MARS - 1]))

    return inc_out



