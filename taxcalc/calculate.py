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



@jit(nopython=True)
def ItemDed_calc(_posagi, e17500, e18400, e18425, e18450, e18500, e18800, e18900,
                 e20500, e20400, e19200, e20550, e20600, e20950, e19500, e19570,
                 e19400, e19550, e19800, e20100, e20200, e20900, e21000, e21010,
                 MARS, _sep, c00100, puf, _phase2_arr, FLPDYR, DEFAULT_YR):

    # Medical #
    c17750 = 0.075 * _posagi
    c17000 = max(0, e17500 - c17750)

    # State and Local Income Tax, or Sales Tax #
    _sit1 = max(e18400, e18425)
    _sit = max(_sit1, 0)
    _statax =  max(_sit, e18450)

    # Other Taxes #
    c18300 = _statax + e18500 + e18800 + e18900

    # Casulty #
    if e20500 > 0:
        c37703 = e20500 + 0.1 * _posagi
        c20500 = c37703 + 0.1 * _posagi
    else:
        c37703 = 0.
        c20500 = 0.

    # Miscellaneous #
    c20750 = 0.02 * _posagi
    if puf == True:
        c20400 = e20400
        c19200 = e19200
    else:
        c20400 = e20550 + e20600 + e20950
        c19200 = e19500 + e19570 + e19400 + e19550
    c20800 = max(0, c20400 - c20750)

    # Charity (assumes carryover is non-cash)
    base_charity = e19800 + e20100 + e20200
    if base_charity <= 0.2 * _posagi:
        c19700 = base_charity
    else:
        lim50 = min(0.50 * _posagi, e19800)
        lim30 = min(0.30 * _posagi, e20100 + e20200)
        c19700 = min(0.5 * _posagi, lim30 + lim50)
    # temporary fix!??

    # Gross Itemized Deductions #
    c21060 = (e20900 + c17000 + c18300 + c19200 + c19700
              + c20500 + c20800 + e21000 + e21010)

    _phase2_i = _phase2_arr[FLPDYR-DEFAULT_YR, MARS-1]

    _nonlimited = c17000 + c20500 + e19570 + e21010 + e20900
    _limitratio = _phase2_i/_sep

    if c21060 > _nonlimited and c00100 > _limitratio:
        dedmin = 0.8 * (c21060 - _nonlimited)
        dedpho = 0.03 * max(0, _posagi - _limitratio)
        c21040 = min(dedmin, dedpho)
    else:
        c21040 = 0.0


    if c21060 > _nonlimited and c00100 > _limitratio:
        c04470 = c21060 - c21040
    else:
        c04470 = c21060


    # the variables that are casted as floats below can be either floats or ints depending
    # on which if/else branches they follow in the above code. they need to always be the same type
    return (c17750, c17000, _sit1, _sit, _statax, c18300, float(c37703), float(c20500),
            c20750, float(c20400), float(c19200), c20800, c19700, c21060,
            _phase2_i, _nonlimited, _limitratio, c04470, c21040)


@jit(nopython=True)
def ItemDed_apply(_posagi, e17500, e18400, e18425, e18450, e18500, e18800, e18900,
            e20500, e20400, e19200, e20550, e20600, e20950, e19500, e19570,
            e19400, e19550, e19800, e20100, e20200, e20900, e21000, e21010,
            MARS, _sep, c00100, puf, DEFAULT_YR, FLPDYR,
            c17750, c17000, _sit1, _sit, _statax, c18300, c37703, c20500, c20750, c20400, c19200,
            c20800, c19700, c21060, _phase2, _phase2_i, _nonlimited, _limitratio, c04470, c21040):


    for i in range(len(_posagi)):
        (c17750[i], c17000[i], _sit1[i], _sit[i], _statax[i], c18300[i], c37703[i], c20500[i],
        c20750[i], c20400[i], c19200[i], c20800[i], c19700[i], c21060[i], _phase2_i[i],
        _nonlimited[i], _limitratio[i], c04470[i], c21040[i]
        ) = ItemDed_calc(
            _posagi[i], e17500[i], e18400[i], e18425[i], e18450[i], e18500[i], e18800[i], e18900[i],
            e20500[i], e20400[i], e19200[i], e20550[i], e20600[i], e20950[i], e19500[i], e19570[i],
            e19400[i], e19550[i], e19800[i], e20100[i], e20200[i], e20900[i], e21000[i], e21010[i],
            MARS[i], _sep[i], c00100[i], puf, _phase2, FLPDYR[i], DEFAULT_YR
            )


    return (c17750, c17000, _sit1, _sit, _statax, c18300, c37703, c20500,
                c20750, c20400, c19200, c20800, c19700, c21060,
                _phase2_i, _nonlimited, _limitratio, c04470, c21040)


def ItemDed(puf, p):
    global c04470
    global c21060
    global c21040
    global c17000
    global c18300
    global c20800
    global _sit

    outputs = ItemDed_apply(_posagi, e17500, e18400, e18425, e18450, e18500,
            e18800, e18900, e20500, e20400, e19200, e20550, e20600, e20950,
            e19500, e19570, e19400, e19550, e19800, e20100, e20200, e20900,
            e21000, e21010, MARS, p._sep, c00100, puf, p.DEFAULT_YR, FLPDYR,
            p.c17750, c17000, p._sit1, _sit, p._statax, c18300, p.c37703, p.c20500, p.c20750, p.c20400, p.c19200,
            c20800, p.c19700, c21060, p._phase2, p._phase2_i, p._nonlimited, p._limitratio, c04470, c21040)


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

    SDoutputs = (c15100, c04100, _numextra, _txpyers, c04200, c15200,
                 _standard, _othded, c04100, c04200, _standard, c04500,
                 c04800, c60000, _amtstd, _taxinc, _feitax, _oldfei)

    header = ['c15100', 'c04100', '_numextra', '_txpyers', 'c04200', 'c15200',
              '_standard', '_othded', 'c04100', 'c04200', '_standard',
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



# @jit(i8(i8[:,:], i8, i8, i8), nopython = True)
# def bracket(bracket, FLPDYR, DEFAULT_YR, MARS):
#     bracket = bracket[FLPDYR - DEFAULT_YR, MARS - 1]
#     return bracket

# @jit(i8(i8[:], i8, i8), nopython = True)
# def rate(rate, FLPDYR, DEFAULT_YR):
#     rate = rate[FLPDYR - DEFAULT_YR]
#     return rate


@jit(nopython=True)
def TaxGains0_jit(e00650, c04800, e01000, c23650, e23250, e01100, e58990, e58980, e24515,
    e24518, _brk2, FLPDYR, DEFAULT_YR, MARS, _taxinc, _brk6, _xyztax, _feided, _feitax,
    _cmp, e59410, e59420, e59440, e59470, e59400, e83200_0, e10105, e74400):

    c00650 = e00650
    _addtax = 0.

    if e01000 > 0 or c23650 > 0. or e23250 > 0. or e01100 > 0. or e00650 > 0.:
        _hasgain = 1.
    else:
        _hasgain = 0.

    if _taxinc > 0. and _hasgain == 1.:
        #if/else 1
        _dwks5 = max(0., e58990 - e58980)
        c24505 = max(0., c00650 - _dwks5)

        # gain for tax computation
        if e01100 > 0.:
            c24510 = float(e01100)
        else:
            c24510 = max(0., min(c23650, e23250)) + e01100

        _dwks9 = max(0, c24510 - min(e58990, e58980))
        c24516 = c24505 + _dwks9

        #if/else 2
        _dwks12 = min(_dwks9, e24515 + e24518)
        c24517 = c24516 - _dwks12
        c24520 = max(0., _taxinc - c24517)
        # tentative TI less schD gain
        c24530 = min(_brk2[FLPDYR - DEFAULT_YR, MARS - 1], _taxinc)

        #if/else 3
        _dwks16 = min(c24520, c24530)
        _dwks17 = max(0., _taxinc - c24516)
        c24540 = max(_dwks16, _dwks17)
        c24534 = c24530 - _dwks16
        _dwks21 = min(_taxinc, c24517)
        c24597 = max(0., _dwks21 - c24534)

        #if/else 4
        # income subject to 15% tax
        c24598 = 0.15 * c24597  # actual 15% tax
        _dwks25 = min(_dwks9, e24515)
        _dwks26 = c24516 + c24540
        _dwks28 = max(0., _dwks26 - _taxinc)
        c24610 = max(0., _dwks25 - _dwks28)
        c24615 = 0.25 * c24610
        _dwks31 = c24540 + c24534 + c24597 + c24610
        c24550 = max(0., _taxinc - _dwks31)
        c24570 = 0.28 * c24550

        if c24540 > _brk6[FLPDYR - DEFAULT_YR, MARS - 1]:
            _addtax = 0.05 * c24517

        elif c24540<= _brk6[FLPDYR - DEFAULT_YR, MARS - 1] and _taxinc > _brk6[FLPDYR - DEFAULT_YR, MARS - 1]:
            _addtax = 0.05 * min(c24517, c04800 - _brk6[FLPDYR - DEFAULT_YR, MARS - 1])

        c24560 = Taxer_i(c24540, MARS, FLPDYR, DEFAULT_YR)

        _taxspecial = c24598 + c24615 + c24570 + c24560 + _addtax
        c24580 = min(_taxspecial, _xyztax)

    else:
        ## these variables only be used to check accuracy? unused in calcs. (except c24580)
        _dwks5 = 0.
        _dwks9 = 0.
        c24505 = 0.
        c24510 = 0.
        c24516 = max(0., min(e23250, c23650)) + e01100

        _dwks12 = 0.
        c24517 = 0.
        c24520 = 0.
        c24530 = 0.

        _dwks16 = 0.
        _dwks17 = 0.
        c24540 = 0.
        c24534 = 0.
        _dwks21 = 0.
        c24597 = 0.

        c24598 = 0.
        _dwks25 = 0.
        _dwks26 = 0.
        _dwks28 = 0.
        c24610 = 0.
        c24615 = 0.
        _dwks31 = 0.
        c24550 = 0.
        c24570 = 0.
        _addtax = 0.
        c24560 = 0.
        _taxspecial = 0.
        c24580 = _xyztax


    if c04800 > 0. and _feided > 0.:
        c05100 = max(0., c24580 - _feitax)
    else:
        c05100 = c24580


    # Form 4972 - Lump Sum Distributions
    if _cmp == 1.:
        c59430 = max(0., e59410 - e59420)
        c59450 = c59430 + e59440 # income plus lump sum
        c59460 = max(0., min(0.5 * c59450, 10000.)) - 0.2 * max(0., 59450. - 20000.)
        _line17 = c59450 - c59460
        _line19 = c59450 - c59460 - e59470

        if c59450 > 0.:
            _line22 = max(0., e59440 - e59440*c59460/c59450)
        else:
            _line22 = 0.

        _line30 = 0.1 * max(0., c59450 - c59460 - e59470)

        _line31 = 0.11 * min(_line30, 1190.)\
                + 0.12 * min(2270. - 1190., max(0, _line30 - 1190.))\
                + 0.14 * min(4530. - 2270., max(0., _line30 - 2270.))\
                + 0.15 * min(6690. - 4530., max(0., _line30 - 4530.))\
                + 0.16 * min(9170. - 6690., max(0., _line30 - 6690.))\
                + 0.18 * min(11440. - 9170., max(0., _line30 - 9170.))\
                + 0.20 * min(13710. - 11440., max(0., _line30 - 11440.))\
                + 0.23 * min(17160. - 13710., max(0., _line30 - 13710.))\
                + 0.26 * min(22880. - 17160., max(0., _line30 - 17160.))\
                + 0.30 * min(28600. - 22880., max(0., _line30 - 22880.))\
                + 0.34 * min(34320. - 28600., max(0., _line30 - 28600.))\
                + 0.38 * min(42300. - 34320., max(0., _line30 - 34320.))\
                + 0.42 * min(57190. - 42300., max(0., _line30 - 42300.))\
                + 0.48 * min(85790. - 57190., max(0., _line30 - 57190.))

        _line32 = 10. * _line31

        if e59440 == 0.:
            _line36 = _line32
            ## below are unused in calcs
            _line33 = 0.
            _line34 = 0.
            _line35 = 0.

        elif e59440 > 0.:
            _line33 = 0.1 * _line22

            _line34 = 0.11 * min(_line30, 1190.)\
                    + 0.12 * min(2270. - 1190., max(0., _line30 - 1190.))\
                    + 0.14 * min(4530. - 2270., max(0., _line30 - 2270.))\
                    + 0.15 * min(6690. - 4530., max(0., _line30 - 4530.))\
                    + 0.16 * min(9170. - 6690., max(0., _line30 - 6690.))\
                    + 0.18 * min(11440. - 9170., max(0., _line30 - 9170.))\
                    + 0.20 * min(13710. - 11440., max(0., _line30 - 11440.))\
                    + 0.23 * min(17160. - 13710., max(0., _line30 - 13710.))\
                    + 0.26 * min(22880. - 17160., max(0., _line30 - 17160.))\
                    + 0.30 * min(28600. - 22880., max(0., _line30 - 22880.))\
                    + 0.34 * min(34320. - 28600., max(0., _line30 - 28600.))\
                    + 0.38 * min(42300. - 34320., max(0., _line30 - 34320.))\
                    + 0.42 * min(57190. - 42300., max(0., _line30 - 42300.))\
                    + 0.48 * min(85790. - 57190., max(0., _line30 - 57190.))

            _line35 = 10. * _line34
            _line36 = max(0., _line32 - _line35)

        else:
            _line33 = 0.
            _line34 = 0.
            _line35 = 0.
            _line36 = 0.

        # tax saving from 10 yr option
        c59485 = _line36

        c59490 = c59485 + 0.2 * max(0., e59400)
        # pension gains tax plus
        c05700 = c59490

    else:
        # all but one unused in calcs
        c59430 = 0.
        c59450 = 0.
        c59460 = 0.
        _line17 = 0.
        _line19 = 0.
        _line22 = 0.
        _line30 = 0.
        _line31 = 0.
        _line32 = 0.
        _line33 = 0.
        _line34 = 0.
        _line35 = 0.
        _line36 = 0.

    _parents = e83200_0
    _s1291 = e10105
    c05750 = max(c05100 + _parents + c05700, e74400)
    _taxbc = c05750

    return (c00650, _hasgain, _dwks5, c24505, c24510, _dwks9, c24516,
            c24580, c24516, _dwks12, c24517, c24520, c24530, _dwks16,
            _dwks17, c24540, c24534, _dwks21, c24597, c24598, _dwks25,
            _dwks26, _dwks28, c24610, c24615, _dwks31, c24550, c24570,
            _addtax, c24560, _taxspecial, c05100, c05700, c59430,
            c59450, c59460, _line17, _line19, _line22, _line30, _line31,
            _line32, _line36, _line33, _line34, _line35, c59485, c59490,
            c05700, _s1291, _parents, _taxbc, c05750)


@jit(nopython=True)
def apply_TaxGains0(e00650, c04800, e01000, c23650, e23250, e01100, e58990, 
    e58980, e24515, e24518, _brk2, FLPDYR, DEFAULT_YR, MARS, _taxinc, _brk6,  _xyztax, _feided, _feitax, _cmp,
    e59410, e59420, e59440, e59470, e59400, e83200_0, e10105, e74400,
    c00650, _hasgain, _dwks5, c24505, c24510, _dwks9, c24516, _dwks12,
    c24517, c24520, c24530, _dwks16, _dwks17 ,c24540 ,c24534,
    _dwks21, c24597 , c24598, _dwks25 , _dwks26 , _dwks28,
    c24610, c24615 , _dwks31 , c24550 , c24570 , _addtax ,
    c24560, _taxspecial , c24580 , c05100 , c05700 , c59430 ,
    c59450, c59460 , _line17, _line19 , _line22 , _line30,
    _line31, _line32, _line36, _line33, _line34, _line35,
    c59485, c59490 , _s1291, _parents, c05750, _taxbc):


    for i in range(len(_taxinc)):
        (c00650[i], _hasgain[i], _dwks5[i], c24505[i], c24510[i], _dwks9[i], c24516[i],
        c24580[i], c24516[i], _dwks12[i], c24517[i], c24520[i], c24530[i], _dwks16[i],
        _dwks17[i], c24540[i], c24534[i], _dwks21[i], c24597[i], c24598[i], _dwks25[i],
        _dwks26[i], _dwks28[i], c24610[i], c24615[i], _dwks31[i], c24550[i], c24570[i],
        _addtax[i], c24560[i], _taxspecial[i], c05100[i], c05700[i], c59430[i],
        c59450[i], c59460[i], _line17[i], _line19[i], _line22[i], _line30[i], _line31[i],
        _line32[i], _line36[i], _line33[i], _line34[i], _line35[i], c59485[i], c59490[i],
        c05700[i], _s1291[i], _parents[i], _taxbc[i], c05750[i]) = \
        TaxGains0_jit(e00650[i], c04800[i], e01000[i], c23650[i], e23250[i], e01100[i],
        e58990[i], e58980[i], e24515[i], e24518[i], _brk2, FLPDYR[i], DEFAULT_YR,
        MARS[i], _taxinc[i], _brk6,  _xyztax[i], _feided[i], _feitax[i],
        _cmp[i], e59410[i], e59420[i], e59440[i], e59470[i], e59400[i], e83200_0[i],
        e10105[i], e74400[i])



    return  (c00650, _hasgain, _dwks5, c24505, c24510, _dwks9, c24516,
            c24580, c24516, _dwks12, c24517, c24520, c24530, _dwks16,
            _dwks17, c24540, c24534, _dwks21, c24597, c24598, _dwks25,
            _dwks26, _dwks28, c24610, c24615, _dwks31, c24550, c24570,
            _addtax, c24560, _taxspecial, c05100, c05700, c59430,
            c59450, c59460, _line17, _line19, _line22, _line30, _line31,
            _line32, _line36, _line33, _line34, _line35, c59485, c59490,
            c05700, _s1291, _parents, c05750, _taxbc)



def TaxGains(p):
    global c05750
    global c24517
    global _taxbc
    global c24516
    global c24520
    global c05700

    outputs = apply_TaxGains0(
                e00650, c04800, e01000, c23650, e23250, e01100, e58990,
                e58980, e24515, e24518, p._brk2, FLPDYR, p.DEFAULT_YR, MARS, 
                _taxinc, p._brk6,  _xyztax, _feided, _feitax, _cmp,
                e59410, e59420, e59440, e59470, e59400, e83200_0, e10105, 
                e74400, p.c00650 , p._hasgain, p._dwks5, p.c24505, p.c24510, 
                p._dwks9, p.c24516, p._dwks12, p.c24517 , p.c24520, p.c24530, 
                p._dwks16, p._dwks17, p.c24540, p.c24534, p._dwks21 , p.c24597, 
                p.c24598, p._dwks25, p._dwks26, p._dwks28, p.c24610, p.c24615,
                p._dwks31 , p.c24550 , p.c24570 , p._addtax ,p.c24560 , p._taxspecial , p.c24580 , p.c05100 , p.c05700 , p.c59430 ,
                p.c59450 , p.c59460 , p._line17, p._line19 , p._line22 , p._line30,
                p._line31 , p._line32 , p._line36 ,p._line33 , p._line34 , p._line35,
                p.c59485 , p.c59490, p._s1291, p._parents, p.c05750, p._taxbc)


    ## Note var c24516 is being printed twice. On purpose? e00650 should be c00650?
    header = ['e00650', '_hasgain', '_dwks5', 'c24505', 'c24510', '_dwks9', #Note weirdness w e00650
              'c24516', 'c24580', 'c24516', '_dwks12', 'c24517', 'c24520',
              'c24530', '_dwks16', '_dwks17', 'c24540', 'c24534', '_dwks21',
              'c24597', 'c24598', '_dwks25', '_dwks26', '_dwks28', 'c24610',
              'c24615', '_dwks31', 'c24550', 'c24570', '_addtax', 'c24560',
              '_taxspecial', 'c05100', 'c05700', 'c59430', 'c59450', 'c59460',
              '_line17', '_line19', '_line22', '_line30', '_line31',
              '_line32', '_line36', '_line33', '_line34', '_line35',
              'c59485', 'c59490', 'c05700', '_s1291', '_parents',
              'c05750', '_taxbc']


    return DataFrame(data=np.column_stack(outputs),
                     columns=header) 


def MUI_calc(c00100, _thresx, MARS, c05750, e00300, e00600, c01000, e02000):
    # Additional Medicare tax on unearned Income
    if c00100 > _thresx[MARS - 1]:
        c05750  = (c05750 + 0.038 * min(e00300 + e00600 + max(0, c01000)
                + max(0, e02000), c00100 - _thresx[MARS - 1]))
    return c05750

def MUI_apply(c00100, _thresx, MARS, c05750, e00300, e00600, c01000, e02000):
    
    for i in range(len(_taxinc)):
        c05750[i] = MUI_calc(c00100[i], _thresx, MARS[i], c05750[i], e00300[i], 
                    e00600[i], c01000[i], e02000[i])
    return c05750

def MUI(c05750, p):
    # Additional Medicare tax on unearned Income
    outputs = MUI_apply(c00100, p._thresx, MARS, c05750, e00300, e00600, c01000, 
                        e02000)

    header = ['c05750']

    return DataFrame(data=outputs,
                     columns=header) 


# @vectorize('float64(float64, float64, float64, float64)', nopython=True)
# def AMTI_amtded(c60200, c60220, c60240, c60000):
#     amtded = c60200 + c60220 + c60240
#     if c60000 <= 0:
#         amtded = max(0, amtded + c60000)
#     return amtded

# @vectorize('float64(float64, float64, float64, float64)', nopython=True)
# def AMTI_addamt(_exact, e60290, c60130, _amtded):
#     #_addamt = np.where(np.logical_or(_exact == 0, np.logical_and(_exact == 1, _amtded + e60290 > 0)), _amtded + e60290 - c60130, 0)
#     if _exact == 0 or (_exact == 1 and ((_amtded + e60290) > 0)):
#         return _amtded + e60290 - c60130
#     else:
#         return 0



# @vectorize('float64(' + 24*'float64, ' + 'float64)', nopython=True)
# def AMTI_c62100(_addamt, e60300, e60860, e60100, e60840, e60630, e60550,
#                 e60720, e60430, e60500, e60340, e60680, e60600, e60405,
#                 e60440, e60420, e60410, e61400, e60660, c60260, e60480,
#                 e62000, c60000, e60250, _cmp):
#     if _cmp == 1:
#         return (_addamt + e60300 + e60860 + e60100 + e60840 + e60630 + e60550
#                + e60720 + e60430 + e60500 + e60340 + e60680 + e60600 + e60405
#                + e60440 + e60420 + e60410 + e61400 + e60660 - c60260 - e60480
#                - e62000 + c60000 - e60250)
#     else:
#         return 0


# @vectorize('float64(' + 5*'float64, ' + 'float64)', nopython=True)
# def AMTI_edical(puf, _standard, _exact, e04470, e17500, e00100):
#     if (puf and (_standard == 0 or (_exact == 1 and e04470 > 0))):
#         return max(0, e17500 - max(0, e00100) * 0.075)
#     else:
#         return 0

# @vectorize('float64(' + 12*'float64, ' + 'float64)', nopython=True)
# def AMTI_cmbtp(puf, _standard, _exact, e04470, f6251, _edical, e00100,
#               e62100, c60260, e21040, _sit, e18500, e20800):
#     if (puf and ((_standard == 0 or (_exact == 1 and e04470 > 0))
#         and f6251 == 1)):
#         return (-1 * min(_edical, 0.025 * max(0, e00100)) + e62100 + c60260
#                + e04470 + e21040 - _sit - e00100 - e18500 - e20800)
#     else:
#         return 0


# @vectorize('float64(' + 13*'float64, ' + 'float64)', nopython=True)
# def AMTI_c62100_2(puf, _standard, _exact, e04470, c00100, c04470, c17000,
#                   e18500, c60260, c20800, c21040, _cmbtp, c62100, _sit):
#     if (puf == True and ((_standard == 0 or (_exact == 1 and e04470 > 0)))):
#         return (c00100 - c04470 + min(c17000, 0.025 * max(0, c00100)) + _sit
#                + e18500 - c60260 + c20800 - c21040 + _cmbtp)
#     else:
#         return c62100

# @vectorize('float64(' + 6*'float64, ' + 'float64)', nopython=True)
# def AMTI_cmbtp_2(puf, _standard, f6251, e62100, e00100, c60260, _cmbtp):
#     if (puf == True and ((_standard > 0 and f6251 == 1))):
#         return e62100 - e00100 + c60260
#     else:
#         return _cmbtp


# @vectorize('float64(' + 5*'float64, ' + 'float64)', nopython=True)
# def AMTI_c62100_3(puf, _standard, c00100, c60260, _cmbtp, c62100):
#     if (puf == True and _standard > 0):
#         return (c00100 - c60260 + _cmbtp)
#     else:
#         return c62100


# @vectorize('float64(' + 2*'float64, ' + 'float64)', nopython=True)
# def AMTI_agep(DOBYR, FLPDYR, DOBMD):
#     #_agep = np.where(
#     #    DOBYR > 0, np.ceil((12 * (FLPDYR - DOBYR) - DOBMD / 100) / 12), 0)
#     if DOBYR > 0:
#         return np.ceil((12 * (FLPDYR - DOBYR) - DOBMD / 100) / 12)
#     else:
#         return 0


# @vectorize('float64(' + 2*'float64, ' + 'float64)', nopython=True)
# def AMTI_ages(SDOBYR, FLPDYR, SDOBMD):
#     #_ages = np.where(
#     #    SDOBYR > 0, np.ceil((12 * (FLPDYR - SDOBYR) - SDOBMD / 100) / 12), 0)
#     if SDOBYR > 0:
#         return np.ceil((12 * (FLPDYR - SDOBYR) - SDOBMD / 100) / 12)
#     else:
#         return 0

# @vectorize('float64(' + 4*'float64, ' + 'float64)', nopython=True)
# def AMTI_c62600(_cmp, f6251, _exact, e62600, c62600):
#     if (_cmp == 1 and f6251 == 1 and _exact == 1):
#         return e62600
#     else:
#         return c62600


# @vectorize('float64(' + 3*'float64, ' + 'float64)', nopython=True)
# def AMTI_alminc(c62100, c62600, c02700, _alminc):
#     if (c02700 > 0):
#         return max(0, c62100 - c62600 + c02700)
#     else:
#         return _alminc


def AMTI_calc(  c60000, _exact, e60290, _posagi, e07300, x60260, c24517,
                e60300, e60860, e60100, e60840, e60630, e60550,
                e60720, e60430, e60500, e60340, e60680, e60600, e60405,
                e60440, e60420, e60410, e61400, e60660, e60480,
                e62000,  e60250, _cmp, puf, _standard,  e04470, e17500, 
                f6251,  e62100, e21040, _sit, e20800, c00100, 
                c04470, c17000, e18500, c20800, c21040,   
                DOBYR, FLPDYR, DOBMD, SDOBYR, SDOBMD,  c02700, 
                e00100,  e24515, x62730, x60130, 
                x60220, x60240, c18300, _taxbc, DEFAULT_YR, _almsp, 
                _brk6, MARS, _sep, _brk2, _almdep, _cgrate1,
                _cgrate2, _amtys, _amtsep, x62720, e00700, c24516, 
                c24520, c04800, e10105, c05700, e05800, e05100, e09600, 
                _amtage, x62740, e62900, _almsep):

    c62720 = c24517 + x62720
    c60260 = e00700 + x60260
    c63100 = max(0, _taxbc - e07300)
    c60200 = min(c17000, 0.025 * _posagi)
    c60240 = c18300 + x60240
    c60220 = c20800 + x60220
    c60130 = c21040 + x60130
    c62730 = e24515 + x62730 

    _amtded = c60200 + c60220 + c60240
    if c60000 <= 0:
        _amtded = max(0, _amtded + c60000)
   
    if _exact == 0 or (_exact == 1 and ((_amtded + e60290) > 0)):
        _addamt = _amtded + e60290 - c60130


    if _cmp == 1:
        c62100 = (_addamt + e60300 + e60860 + e60100 + e60840 + e60630 + e60550
               + e60720 + e60430 + e60500 + e60340 + e60680 + e60600 + e60405
               + e60440 + e60420 + e60410 + e61400 + e60660 - c60260 - e60480
               - e62000 + c60000 - e60250)


    if (puf and (_standard == 0 or (_exact == 1 and e04470 > 0))):
        _edical = max(0, e17500 - max(0, e00100) * 0.075)
    else: _edical = 0

    if (puf and ((_standard == 0 or (_exact == 1 and e04470 > 0))
        and f6251 == 1)):
        _cmbtp = (-1 * min(_edical, 0.025 * max(0, e00100)) + e62100 + c60260
               + e04470 + e21040 - _sit - e00100 - e18500 - e20800)
    else: _cmbtp = 0

    if (puf == True and ((_standard == 0 or (_exact == 1 and e04470 > 0)))):
        c62100 = (c00100 - c04470 + min(c17000, 0.025 * max(0, c00100)) + _sit
               + e18500 - c60260 + c20800 - c21040 + _cmbtp)


    if (puf == True and ((_standard > 0 and f6251 == 1))):
        _cmbtp = e62100 - e00100 + c60260


    if (puf == True and _standard > 0):
        c62100 = (c00100 - c60260 + _cmbtp)
 

    if (c62100 > _amtsep[FLPDYR - DEFAULT_YR]) and (MARS == 3 or MARS == 6):
        _amtsepadd = max(0, min(_almsep[FLPDYR-DEFAULT_YR], 0.25 * (c62100 - _amtsep[FLPDYR - DEFAULT_YR])))
    else: _amtsepadd = 0
    c62100 = c62100 + _amtsepadd

    c62600 = max(0, _amtex[FLPDYR - DEFAULT_YR, MARS - 1] - 0.25 * max(0, c62100 - _amtys[FLPDYR - DEFAULT_YR, MARS - 1]))

    if DOBYR > 0:
        _agep = math.ceil((12 * (FLPDYR - DOBYR) - DOBMD / 100) / 12)
    else:
        _agep = 0.

    if SDOBYR > 0:
        _ages = np.ceil((12 * (FLPDYR - SDOBYR) - SDOBMD / 100) / 12)
    else: _ages = 0

    if (_cmp == 1 and f6251 == 1 and _exact == 1):
        c62600 = e62600

    if _cmp == 1 and _exact == 0 and _agep < _amtage[FLPDYR-DEFAULT_YR] and _agep != 0:
        c62600 = min(c62600, _earned + _almdep[FLPDYR - DEFAULT_YR])
  
    c62700 = max(0., c62100 - c62600)

    _alminc = c62700

    if (c02700 > 0):
        _alminc = max(0., c62100 - c62600 + c02700)

        _amtfei = 0.26 * c02700 + 0.02 * max(0, c02700 - _almsp[FLPDYR - DEFAULT_YR] / _sep)
    else:
        _alminc = c62700

        _amtfei = 0.


    c62780 = 0.26 * _alminc + 0.02 * \
        max(0, _alminc - _almsp[FLPDYR - DEFAULT_YR] / _sep) - _amtfei

    if f6251 != 0:
        c62900 = e62900
    else: 
        c62900 = e07300
    
    c63000 = c62780 - c62900

    if c24516 == 0:
        c62740 = c62720 + c62730
    else: 
        c62740 = min(max(0, c24516 + x62740), c62720 + c62730)
    
    
    _ngamty = max(0, _alminc - c62740)

    c62745 = 0.26 * _ngamty + 0.02 * \
        max(0, _ngamty - _almsp[FLPDYR - DEFAULT_YR] / _sep)

    y62745 = _almsp[FLPDYR - DEFAULT_YR] / _sep

    _tamt2 = 0.

    _amt5pc = 0.0

  
    _amt15pc = min(_alminc, c62720) - _amt5pc - min(max(
        0., _brk2[FLPDYR - DEFAULT_YR, MARS - 1] - c24520), min(_alminc, c62720))
    if c04800 == 0:
        _amt15pc = max(0, min(_alminc, c62720) - _brk2[FLPDYR - DEFAULT_YR, MARS - 1])
    
   
    _amt25pc = min(_alminc, c62740) - min(_alminc, c62720)
    
    if c62730 == 0:
        _amt25pc = 0.
    else: 
        _amt25pc = min(_alminc, c62740) - min(_alminc, c62720)
  
    c62747 = _cgrate1[FLPDYR - DEFAULT_YR] * _amt5pc

    
    c62755 = _cgrate2[FLPDYR - DEFAULT_YR] * _amt15pc
    
    c62770 = 0.25 * _amt25pc
    
    _tamt2 = c62747 + c62755 + c62770
 

    _amt = 0.
  
    if _ngamty > _brk6[FLPDYR - DEFAULT_YR, MARS - 1]:
        _amt = 0.05 * min(_alminc, c62740)
    else: 
        _amt = 0.
    
    if _ngamty <= _brk6[FLPDYR - DEFAULT_YR, MARS - 1] and _alminc > _brk6[FLPDYR - DEFAULT_YR, MARS - 1]:
        _amt = 0.05 * min(_alminc - _brk6[FLPDYR - DEFAULT_YR, MARS - 1], c62740)


    _tamt2 = _tamt2 + _amt


    c62800 = min(c62780, c62745 + _tamt2 - _amtfei)
    c63000 = c62800 - c62900
    c63100 = _taxbc - e07300 - c05700
    c63100 = c63100 + e10105
    c63100 = max(0., c63100)

    c63200 = max(0., c63000 - c63100)
    c09600 = c63200
    _othtax = e05800 - (e05100 + e09600)

    c05800 = _taxbc + c63200

    return   (c62720, c60260, c63100, c60200, c60240, c60220,
              c60130, c62730, _addamt, c62100, _cmbtp, _edical,
              _amtsepadd, c62600, _agep, _ages,  c62700,
              _alminc, _amtfei, c62780, c62900, c63000, c62740,
              _ngamty, c62745, y62745, _tamt2, _amt5pc, _amt15pc,
              _amt25pc, c62747, c62755, c62770, _amt, c62800,
              c09600, _othtax, c05800)    


def AMTI_apply( c62720, c60260, c63100, c60200, c60240, c60220,
                c60130, c62730, _addamt, c62100, _cmbtp, _edical,
                _amtsepadd, c62600, _agep, _ages, c62700,
                _alminc, _amtfei, c62780, c62900, c63000, c62740,
                _ngamty, c62745, y62745, _tamt2, _amt5pc, _amt15pc,
                _amt25pc, c62747, c62755, c62770, _amt, c62800,
                c09600, _othtax, c05800, c60000, _exact, e60290, _posagi, 
                e07300, x60260, c24517, e60300, e60860, e60100, e60840, e60630, 
                e60550, e60720, e60430, e60500, e60340, e60680, e60600, e60405,
                e60440, e60420, e60410, e61400, e60660, e60480,
                e62000,  e60250, _cmp, puf, _standard,  e04470, e17500, 
                f6251,  e62100, e21040, _sit, e20800, c00100, 
                c04470, c17000, e18500, c20800, c21040,   
                DOBYR, FLPDYR, DOBMD, SDOBYR, SDOBMD,  c02700, 
                e00100,  e24515, x62730, x60130, 
                x60220, x60240, c18300, _taxbc, DEFAULT_YR, _almsp, 
                _brk6, MARS, _sep, _brk2, _almdep, _cgrate1,
                _cgrate2, _amtys, _amtsep, x62720, e00700, c24516, 
                c24520, c04800, e10105, c05700, e05800, e05100, e09600, _amtage, 
                x62740, e62900, _almsep):


    for i in range(len(_taxinc)):  
        (   c62720[i], c60260[i], c63100[i], c60200[i], c60240[i], c60220[i], 
            c60130[i], c62730[i], _addamt[i], c62100[i], _cmbtp[i], _edical[i], 
            _amtsepadd[i], c62600[i], _agep[i], _ages[i], c62700[i], _alminc[i], 
            _amtfei[i], c62780[i], c62900[i], c63000[i], c62740[i], _ngamty[i], 
            c62745[i], y62745[i], _tamt2[i], _amt5pc[i], _amt15pc[i], 
            _amt25pc[i], c62747[i], c62755[i], c62770[i], _amt[i],
            c62800[i], c09600[i], _othtax[i], c05800[i]) = AMTI_calc(
            c60000[i], _exact[i], e60290[i], _posagi[i], e07300[i], x60260[i], 
            c24517[i], e60300[i], e60860[i], e60100[i], e60840[i], e60630[i], 
            e60550[i], e60720[i], e60430[i], e60500[i], e60340[i], e60680[i], 
            e60600[i], e60405[i], e60440[i], e60420[i], e60410[i], e61400[i], 
            e60660[i],  e60480[i], e62000[i], e60250[i], _cmp[i], puf, 
            _standard[i],  e04470[i], e17500[i], f6251[i], e62100[i], e21040[i],
            _sit[i], e20800[i], c00100[i], c04470[i], c17000[i], e18500[i], 
            c20800[i], c21040[i], DOBYR[i], FLPDYR[i], DOBMD[i], SDOBYR[i], 
            SDOBMD[i], c02700[i], e00100[i], e24515[i], x62730[i], x60130[i], 
            x60220[i], x60240[i], c18300[i], _taxbc[i], DEFAULT_YR, _almsp, 
            _brk6, MARS[i], _sep[i], _brk2, _almdep, _cgrate1, _cgrate2, _amtys,
            _amtsep, x62720[i], e00700[i], c24516[i], c24520[i], c04800[i], 
            e10105[i], c05700[i], e05800[i], e05100[i], e09600[i], _amtage, 
            x62740[i], e62900[i], _almsep)
     
    return   (c62720, c60260, c63100, c60200, c60240, c60220,
              c60130, c62730, _addamt, c62100, _cmbtp, _edical,
              _amtsepadd, c62600, _agep, _ages,  c62700,
              _alminc, _amtfei, c62780, c62900, c63000, c62740,
              _ngamty, c62745, y62745, _tamt2, _amt5pc, _amt15pc,
              _amt25pc, c62747, c62755, c62770, _amt, c62800,
              c09600, _othtax, c05800)

def AMTI(puf, p):
    global c05800
    global _othtax
    global _agep
    global _ages


    outputs = AMTI_apply( p.c62720, p.c60260, p.c63100, p.c60200, p.c60240, 
                p.c60220,
                p.c60130, p.c62730, p._addamt, p.c62100, p._cmbtp, p._edical,
                p._amtsepadd, p.c62600, p._agep, p._ages,  p.c62700, p._alminc, 
                p._amtfei, p.c62780, p.c62900, p.c63000, p.c62740, p._ngamty, 
                p.c62745, p.y62745, p._tamt2, p._amt5pc, p._amt15pc, p._amt25pc,
                p.c62747, p.c62755, p.c62770, p._amt, p.c62800, p.c09600, 
                p._othtax, p.c05800, c60000, _exact, e60290, _posagi, e07300, 
                x60260, c24517, e60300, e60860, e60100, e60840, e60630, e60550,
                e60720, e60430, e60500, e60340, e60680, e60600, e60405, e60440, 
                e60420, e60410, e61400, e60660, e60480, e62000, e60250, _cmp, 
                puf, _standard,  e04470, e17500, f6251,  e62100, e21040, _sit, 
                e20800, c00100, c04470, c17000, e18500, c20800, c21040,   
                DOBYR, FLPDYR, DOBMD, SDOBYR, SDOBMD,  c02700, e00100,  e24515, 
                x62730, x60130, x60220, x60240, c18300, p._taxbc, DEFAULT_YR, 
                p._almsp, p._brk6, MARS, p._sep, p._brk2, p._almdep, p._cgrate1,
                p._cgrate2, p._amtys, p._amtsep, x62720, e00700, c24516, 
                c24520, c04800, e10105, c05700, e05800, e05100, e09600, 
                p._amtage, x62740, e62900, p._almsep)

    header = ['c62720', 'c60260', 'c63100', 'c60200', 'c60240', 'c60220',
              'c60130', 'c62730', '_addamt', 'c62100', '_cmbtp', '_edical',
              '_amtsepadd', 'c62600', '_agep', '_ages', 'c62700',
              '_alminc', '_amtfei', 'c62780', 'c62900', 'c63000', 'c62740',
              '_ngamty', 'c62745', 'y62745', '_tamt2', '_amt5pc', '_amt15pc',
              '_amt25pc', 'c62747', 'c62755', 'c62770', '_amt', 'c62800',
              'c09600', '_othtax', 'c05800'] 

    return DataFrame(data=np.column_stack(outputs),
                     columns=header), c05800






def F2441_calc(_earned, _fixeic, e59560, MARS, puf, f2441, _dcmax, FLPDYR, 
    DEFAULT_YR, e32800, e32750 , e32775 ):
    _earned = _earned

    if _fixeic == 1: 
        _earned = e59560

    if MARS == 2 and puf == True:
        c32880 = 0.5 * _earned
        c32890 = 0.5 * _earned
    else: c32880, c32890 = 0, 0 

    if MARS == 2 and puf == False:
        c32880 = max(0, e32880)
        c32890 = max(0, e32890)

    if MARS != 2:
        c32880 = _earned
        c32890 = _earned

    _ncu13 = 0.
    if puf == True:
        _ncu13 = f2441

    if puf == False and CDOB1 > 0:
        _ncu13 += 1

    if puf == False and CDOB2 > 0:
        _ncu13 += 1    

    _dclim = min(_ncu13, 2) * _dcmax[FLPDYR - DEFAULT_YR]
    
    c32800 = min(max(e32800, e32750 + e32775), _dclim)

    return _earned, c32880, c32890, _ncu13, _dclim, c32800

def F2441_apply(c32880, c32890, _ncu13, _dclim, c32800, 
                _earned, _fixeic, e59560, MARS, puf, f2441, _dcmax, FLPDYR, 
                DEFAULT_YR, e32800, e32750, e32775):
    
    for i in range(len(_taxinc)):
        (_earned[i], c32880[i], c32890[i], _ncu13[i], _dclim[i], 
        c32800[i]) = F2441_calc(_earned[i], _fixeic[i], e59560[i], MARS[i], 
        puf, f2441[i], _dcmax, FLPDYR[i], DEFAULT_YR, e32800[i], e32750[i], 
        e32775[i] )

    return _earned, c32880, c32890, _ncu13, _dclim, c32800
    

def F2441(puf, _earned, p):
    global c32880
    global c32890
    global c32800
    global _dclim


    outputs = F2441_apply(p.c32880, p.c32890, p._ncu13, p._dclim, p.c32800, 
                _earned, _fixeic, e59560, MARS, puf, f2441, p._dcmax, FLPDYR, 
                p.DEFAULT_YR, e32800, e32750, e32775)
    header = ['_earned', 'c32880', 'c32890', '_ncu13', '_dclim', 'c32800']

    return DataFrame(data=np.column_stack(outputs), columns=header), c32800

def DepCareBen_calc(c32800, _cmp, MARS, c32880, c32890, e33420, e33430, e33450, 
                    e33460, e33465, e33470, _sep, _dclim, e32750, e32775, 
                    _earned):

    c32800 = c32800
    # Part III ofdependent care benefits
    if _cmp == 1  and MARS == 2:
        _seywage = min(c32880, c32890, e33420 + e33430 - e33450, e33460)
    else: 
        _seywage = 0 

    if _cmp == 1 and MARS != 2:  #this is same as above, why?
        _seywage = min(c32880, c32890, e33420 + e33430 - e33450, e33460)
   
    if _cmp == 1:
        c33465 = e33465
        c33470 = e33470
        c33475 = max(0., min(_seywage, 5000 / _sep) - c33470)
        c33480 = max(0., e33420 + e33430 - e33450 - c33465 - c33475)
        c32840 = c33470 + c33475
        c32800 = min(max(0., _dclim - c32840), max(0, e32750 + e32775 - c32840))

    else: 
        c33465, c33470, c33475, c33480, c32840 = 0.,0.,0.,0.,0.
        c32800 = c32800

    if MARS == 2:
        c33000 = max(0, min(c32800, min(c32880, c32890)))
    else: 
        c33000 = max(0, min(c32800, _earned))

    return _seywage, c33465, c33470, c33475, c33480, c32840, c32800, c33000

def DepCareBen_apply(   _seywage, c33465, c33470, c33475, c33480, c32840, 
                        c33000, c32800, _cmp, MARS, c32880, c32890, 
                        e33420, e33430, e33450, e33460, e33465, e33470, _sep, 
                        _dclim, e32750, e32775, _earned):
    
    for i in range(len(_taxinc)): 
        (_seywage[i], c33465[i], c33470[i], c33475[i], c33480[i], c32840[i], 
        c32800[i], c33000[i]) = DepCareBen_calc(c32800[i], _cmp[i], MARS[i], 
        c32880[i], c32890[i], e33420[i], e33430[i], e33450[i], e33460[i], 
        e33465[i], e33470[i], _sep, _dclim[i], e32750[i], e32775[i], _earned[i])

    return _seywage, c33465, c33470, c33475, c33480, c32840, c32800, c33000



def DepCareBen(c32800, p):
    global c33000

    outputs = DepCareBen_apply( p._seywage, p.c33465, p.c33470, p.c33475, 
                                p.c33480, p.c32840, p.c33000, c32800, _cmp, 
                                MARS, c32880, c32890, e33420, e33430, e33450, 
                                e33460, e33465, e33470, p._sep, _dclim, e32750, 
                                e32775, _earned)

    header = ['_seywage', 'c33465', 'c33470', 'c33475', 'c33480', 'c32840',
              'c32800', 'c33000']

    return DataFrame(data=np.column_stack(outputs),
                     columns=header)


def ExpEarnedInc_calc(  _exact, c00100, _agcmax, _pcmax, FLPDYR, DEFAULT_YR, 
                        c33000, c05800, e07300, e07180):
    # Expenses limited to earned income

    if _exact == 1: 

        _tratio = math.ceil(max((c00100 - _agcmax[FLPDYR - DEFAULT_YR]) 
                / 2000, 0))

        c33200 = c33000 * 0.01 * max(20, _pcmax[FLPDYR - DEFAULT_YR] 
                - min(15, _tratio))
    
    else: 
        _tratio = 0

        c33200 = c33000 * 0.01 * max(20, _pcmax[FLPDYR - DEFAULT_YR] 
                - max((c00100 - _agcmax[FLPDYR - DEFAULT_YR]) / 2000, 0))

    c33400 = min(max(0, c05800 - e07300), c33200)

    # amount of the credit

    if e07180 == 0:
        c07180 = 0
    else: 
        c07180 = c33400

    return _tratio, c33200, c33400, c07180

def ExpEarnedInc_apply( _tratio, c33200, c33400, c07180, _exact, c00100, 
                        _agcmax, _pcmax, FLPDYR, DEFAULT_YR, 
                        c33000, c05800, e07300, e07180):
    
    for i in range(len(_taxinc)):
        _tratio[i], c33200[i], c33400[i], c07180[i] = ExpEarnedInc_calc( 
        _exact[i], c00100[i], _agcmax, _pcmax, FLPDYR[i], DEFAULT_YR, c33000[i],
        c05800[i], e07300[i], e07180[i])

    return _tratio, c33200, c33400, c07180


def ExpEarnedInc(p):
    global c07180


    outputs = ExpEarnedInc_apply(   p._tratio, p.c33200, p.c33400, p.c07180, 
                                    _exact, c00100, p._agcmax, p._pcmax, FLPDYR, 
                                    p.DEFAULT_YR, c33000, c05800, e07300, 
                                    e07180)

    header = ['_tratio', 'c33200', 'c33400', 'c07180']

    return DataFrame(data=np.column_stack((outputs)),
                     columns=header)

def RateRed_calc(c05800, _fixup, _othtax, _exact, x59560, _earned):

    # rate reduction credit for 2001 only, is this needed?
    c05800 = c05800
    c07970 = 0.

    if _fixup >= 3:
        c05800 = c05800 + _othtax

    if _exact == 1:
        c59560 = x59560
    else:
        c59560 = _earned 

    return c07970, c05800, c59560

def RateRed_apply(  c07970, c59560, c05800, _fixup, _othtax, _exact, x59560, 
                    _earned ):

    for i in range(len(_taxinc)):
        c07970[i], c05800[i], c59560[i] = RateRed_calc(c05800[i], _fixup[i], 
        _othtax[i], _exact[i], x59560[i], _earned[i])
 
    return c07970, c05800, c59560

def RateRed(c05800, p):
    global c59560
    global c07970

    outputs = RateRed_apply(p.c07970, p.c59560, c05800, _fixup, _othtax, 
                            _exact, x59560, _earned )

    header = ['c07970', 'c05800', 'c59560']

    return DataFrame(data=np.column_stack((outputs)),
                     columns=header)

def NumDep_calc(EICYB1, EICYB2, EICYB3, puf, EIC, c00100, e00400, MARS, 
                _ymax, FLPDYR, DEFAULT_YR, _joint, _rtbase, c59560, _crmax,
                _rtless, e83080, e00300, e00600, e01000, e40223, e25360, e25430,
                e25470, e25400, e25500, e26210, e26340, e27200, e26205,
                e26320, _dylim, _cmp, SOIYR, DOBYR, SDOBYR, _agep, _ages ):

    # Number of dependents for EIC

    _ieic = 0

    EICYB1_1 = max(0.0, EICYB1)
    EICYB2_2 = max(0.0, EICYB2)
    EICYB3_3 = max(0.0, EICYB3)

    if puf == True:
        _ieic = EIC
    else: 
        _ieic = EICYB1_1 + EICYB2_2 + EICYB3_3


    # Modified AGI only through 2002

    _modagi = c00100 + e00400


    if MARS == 2 and _modagi > 0:
        _val_ymax = (_ymax[_ieic, FLPDYR - DEFAULT_YR] 
                    + _joint[FLPDYR - DEFAULT_YR, _ieic])
    else: _val_ymax = 0

    if (MARS == 1 or MARS == 4 or MARS == 5 or MARS == 7) and _modagi > 0:
        _val_ymax = _ymax[_ieic, FLPDYR - DEFAULT_YR]

    if (MARS == 1 or MARS == 4 or MARS == 5 or 
        MARS == 2 or MARS == 7) and _modagi>0:
        
        c59660 = min(_rtbase[FLPDYR - DEFAULT_YR, _ieic] * c59560, 
                _crmax[FLPDYR - DEFAULT_YR, _ieic])

        _preeitc = c59660 
    else: 
        c59660, _preeitc = 0, 0

    if (MARS != 3 and MARS != 6 and _modagi > 0 and 
        (_modagi > _val_ymax or c59560 > _val_ymax)):
        c59660 = max(0, c59660 - _rtless[FLPDYR - DEFAULT_YR, _ieic] 
                * (max(_modagi, c59560) - _val_ymax))

    if MARS != 3 and MARS != 6 and _modagi > 0:
        _val_rtbase = _rtbase[FLPDYR - DEFAULT_YR, _ieic] * 100
        _val_rtless = _rtless[FLPDYR - DEFAULT_YR, _ieic] * 100
        _dy = (e00400 + e83080 + e00300 + e00600
                   + max(0, max(0, e01000) - max(0, e40223))
                   + max(0, max(0, e25360) - e25430 - e25470 - e25400 - e25500)
                   + max(0, e26210 + e26340 + e27200 
                        - math.fabs(e26205) - math.fabs(e26320)))
    else:
        _val_rtbase = 0
        _val_rtless = 0
        _dy = 0

    if (MARS != 3 and MARS != 6 and _modagi > 0 
        and _dy > _dylim[FLPDYR - DEFAULT_YR]):
        c59660 = 0

    if (_cmp == 1 and _ieic == 0 and SOIYR - DOBYR >= 25 and SOIYR - DOBYR < 65
        and SOIYR - SDOBYR >= 25 and SOIYR - SDOBYR < 65):
        c59660 = 0 
    
    if _ieic == 0 and (_agep < 25 or _agep >=65 or _ages <25 or _ages >= 65):
        c59660 = 0

    return (_ieic, EICYB1, EICYB2, EICYB3, _modagi, c59660,
               _val_ymax, _preeitc, _val_rtbase, _val_rtless, _dy)

def NumDep_apply(_ieic, EICYB1_1, EICYB2_2, EICYB3_3, _modagi, c59660,
               _val_ymax, _preeitc, _val_rtbase, _val_rtless, _dy, 
               EICYB1, EICYB2, EICYB3, puf, EIC, c00100, e00400, MARS, 
                _ymax, FLPDYR, DEFAULT_YR, _joint, _rtbase, c59560, _crmax,
                _rtless, e83080, e00300, e00600, e01000, e40223, e25360, e25430,
                e25470, e25400, e25500, e26210, e26340, e27200, e26205,
                e26320, _dylim, _cmp, SOIYR, DOBYR, SDOBYR, _agep, _ages):
    
    for i in range(len(_taxinc)):
        (_ieic[i], EICYB1[i], EICYB2[i], EICYB3[i], _modagi[i], c59660[i],
        _val_ymax[i], _preeitc[i], _val_rtbase[i], 
        _val_rtless[i], _dy[i]) =  NumDep_calc(EICYB1[i], EICYB2[i], EICYB3[i], 
        puf, EIC[i], c00100[i], e00400[i], MARS[i], 
        _ymax, FLPDYR[i], DEFAULT_YR, _joint, _rtbase, c59560[i], _crmax,
        _rtless, e83080[i], e00300[i], e00600[i], e01000[i], e40223[i], 
        e25360[i], e25430[i], e25470[i], e25400[i], e25500[i], e26210[i],
        e26340[i], e27200[i], e26205[i], e26320[i], _dylim, _cmp[i], SOIYR[i], 
        DOBYR[i], SDOBYR[i], _agep[i], _ages[i] )   
    
    return (_ieic, EICYB1, EICYB2, EICYB3, _modagi, c59660,
               _val_ymax, _preeitc, _val_rtbase, _val_rtless, _dy)

def NumDep(puf, p):
    global c59660

    outputs = NumDep_apply( p._ieic, p.EICYB1_1, p.EICYB2_2, p.EICYB3_3, 
                            p._modagi, p.c59660, p._val_ymax, p._preeitc, 
                            p._val_rtbase, p._val_rtless, p._dy, EICYB1, EICYB2,
                            EICYB3, puf, EIC, c00100, e00400, MARS,  p._ymax, 
                            FLPDYR, p.DEFAULT_YR, p._joint, p._rtbase, c59560, 
                            p._crmax, p._rtless, e83080, e00300, e00600, e01000, 
                            e40223, e25360, e25430, e25470, e25400, e25500, 
                            e26210, e26340, e27200, e26205, e26320, p._dylim, 
                            _cmp, SOIYR, DOBYR, SDOBYR, _agep, _ages)

    header = ['_ieic', 'EICYB1', 'EICYB2', 'EICYB3', '_modagi',
              'c59660', '_val_ymax', '_preeitc', '_val_rtbase',
              '_val_rtless', '_dy']

    return DataFrame(data=np.column_stack(outputs), columns=header)

def ChildTaxCredit_calc(n24, MARS, _chmax, FLPDYR, DEFAULT_YR, c00100, _feided,
                        _cphase, _exact  ):

    # Child Tax Credit

    c11070 = 0
    c07220 = 0
    c07230 = 0
    _precrd = 0

    _num = 1

    if MARS == 2:
        _num = 2

    _nctcr = n24
    

    _precrd = _chmax[FLPDYR - DEFAULT_YR] * _nctcr

    _ctcagi = c00100 + _feided

    if _ctcagi > _cphase[MARS - 1] and _exact == 1:
        _precrd = max(0, _precrd - 50 
            * math.ceil(_ctcagi - _cphase[MARS - 1]) / 1000)

    if _ctcagi > _cphase[MARS - 1] and _exact != 1:
        _precrd = max(0, _precrd 
                - 50 * (max(0, _ctcagi - _cphase[MARS - 1]) + 500) / 1000)


    return (c11070, c07220, c07230, _num, _nctcr, _precrd, _ctcagi)


def ChildTaxCredit_apply(   c11070, c07220, c07230,  _num, _nctcr, 
                            _precrd, _ctcagi, n24, MARS, _chmax, FLPDYR, 
                            DEFAULT_YR, c00100, _feided, _cphase, _exact ):

    for i in range(len(_taxinc)):

        (c11070[i], c07220[i], c07230[i], _num[i], _nctcr[i], 
        _precrd[i], _ctcagi[i]) = ChildTaxCredit_calc(n24[i], MARS[i], _chmax, 
        FLPDYR[i], DEFAULT_YR, c00100[i], _feided[i], _cphase, _exact[i]) 

    return (c11070, c07220, c07230,  _num, _nctcr, _precrd, _ctcagi)

def ChildTaxCredit(p):
    global _num
    global c07230
    global _precrd
    global _nctcr
    global c07220


    outputs = ChildTaxCredit_apply( p.c11070, p.c07220, p.c07230, 
                                    p._num, p._nctcr, p._precrd, p._ctcagi, 
                                    n24, MARS, p._chmax, FLPDYR, p.DEFAULT_YR, 
                                    c00100, _feided, p._cphase, _exact )


    header = ['c11070', 'c07220', 'c07230', '_num', '_nctcr',
              '_precrd', '_ctcagi']

    return DataFrame(data=np.column_stack(outputs), columns=header)


# def HopeCredit():
    # W/o congressional action, Hope Credit will replace 
    # American opportunities credit in 2018. NEED TO ADD LOGIC!!!


def AmOppCr_calc(_cmp, e87482, e87487, e87492, e87497):
    # American Opportunity Credit 2009+

    if _cmp == 1:
        c87482 = max(0, min(e87482, 4000))
        c87487 = max(0, min(e87487, 4000))
        c87492 = max(0, min(e87492, 4000))
        c87497 = max(0, min(e87497, 4000))
    else: 
        c87482, c87487, c87492, c87497 = 0,0,0,0

    if max(0, c87482 - 2000) == 0:
        c87483 = c87482
    else: 
        c87483 = 2000 + 0.25 * max(0, c87482 - 2000)

    if max(0, c87487 - 2000) == 0:
        c87488 = c87487
    else: 
        c87488 = 2000 + 0.25 * max(0, c87487 - 2000)

    if max(0, c87492 - 2000) == 0:
        c87493 = c87492
    else: 
        c87493 = 2000 + 0.25 * max(0, c87492 - 2000)

    if max(0, c87497 - 2000) == 0:
        c87498 = c87497
    else: 
        c87498 = 2000 + 0.25 * max(0, c87497 - 2000)


    c87521 = c87483 + c87488 + c87493 + c87498

    return (c87482, c87487, c87492, c87497,
               c87483, c87488, c87493, c87498, c87521)

def AmOppCr_apply(  c87482, c87487, c87492, c87497, c87483, c87488, c87493, 
                    c87498, c87521, _cmp, e87482, e87487, e87492, e87497):
    for i in range(len(_taxinc)):
        (   c87482[i], c87487[i], c87492[i], c87497[i], c87483[i], c87488[i], 
        c87493[i], c87498[i], c87521[i]) = AmOppCr_calc(_cmp[i], e87482[i], 
                                            e87487[i], e87492[i], e87497[i])
    
    return (c87482, c87487, c87492, c87497,
               c87483, c87488, c87493, c87498, c87521)

def AmOppCr(calc):

    global c87521
    

    outputs = AmOppCr_apply(c87482, c87487, c87492, c87497, c87483, c87488, 
                            c87493, c87498, c87521, _cmp, e87482, e87487, 
                            e87492, e87497)


    header = ['c87482', 'c87487', 'c87492', 'c87497', 'c87483', 'c87488',
              'c87493', 'c87498', 'c87521']

    return DataFrame(data=np.column_stack(outputs), columns=header)


def LLC_calc(puf, e87530, _learn, FLPDYR, DEFAULT_YR,
        e87526, e87522, e87524, e87528):

    # Lifetime Learning Credit

    if puf == True:
        c87540 = min(e87530, _learn[FLPDYR - DEFAULT_YR])
        c87530 = 0
    else:
        c87530 = e87526 + e87522 + e87524 + e87528
        c87540 = min(c87530, _learn[FLPDYR - DEFAULT_YR])


    c87550 = 0.2 * c87540

    return (c87540, c87550, c87530)

def LLC_apply(c87540, c87550, c87530, puf, e87530, _learn, FLPDYR, DEFAULT_YR,
        e87526, e87522, e87524, e87528):

    for i in range(len(_taxinc)):
        (c87540[i], c87550[i], c87530[i]) = LLC_calc(puf, e87530[i], _learn, 
            FLPDYR[i], DEFAULT_YR, e87526[i], e87522[i], e87524[i], e87528[i])

    return (c87540, c87550, c87530)

def LLC(puf, p):
    # Lifetime Learning Credit
    global c87550

    outputs = LLC_apply(p.c87540, p.c87550, p.c87530, puf, e87530, p._learn, 
                FLPDYR, p.DEFAULT_YR, e87526, e87522, e87524, e87528)

    header = ['c87540', 'c87550', 'c87530']
    return DataFrame(data=np.column_stack(outputs), columns=header), c87550


def RefAmOpp_calc(_cmp, c87521, _num, c00100, EDCRAGE):
    # Refundable American Opportunity Credit 2009+

    c87668 = 0

    if _cmp == 1 and c87521 > 0: 
        c87654 = 90000 * _num 
        c87656 = c00100
        c87658 = np.maximum(0, c87654 - c87656)
        c87660 = 10000 * _num
        c87662 = 1000 * np.minimum(1, c87658 / c87660)
        c87664 = c87662 * c87521 / 1000
    else: 
        c87654, c87656, c87658, c87660, c87662, c87664 = 0, 0, 0, 0, 0, 0

    if _cmp == 1 and c87521 > 0 and EDCRAGE == 1: 
        c87666 = 0 
    else: 
        c87666 = 0.4 * c87664

    if c87521 > 0 and _cmp == 1:
        c10960 = c87666
        c87668 = c87664 - c87666
        c87681 = c87666
    else: c10960, c87668, c87681 = 0, 0, 0

    return (c87654, c87656, c87658, c87660, c87662,
               c87664, c87666, c10960, c87668, c87681)

def RefAmOpp_apply( c87654, c87656, c87658, c87660, c87662, c87664, c87666, 
                    c10960, c87668, c87681, _cmp, c87521, _num, c00100, 
                    EDCRAGE): 
    
    for i in range(len(_taxinc)):

        (   c87654[i], c87656[i], c87658[i], c87660[i], c87662[i], c87664[i], 
            c87666[i], c10960[i], c87668[i], c87681[i]) = RefAmOpp_calc(_cmp[i], 
            c87521[i], _num[i], c00100[i], EDCRAGE[i])    
    
    return (c87654, c87656, c87658, c87660, c87662,
               c87664, c87666, c10960, c87668, c87681)

def RefAmOpp(p):

    outputs = RefAmOpp_apply(   p.c87654, p.c87656, p.c87658, p.c87660, 
                                p.c87662, p.c87664, p.c87666, p.c10960, 
                                p.c87668, p.c87681, _cmp, c87521, _num, 
                                c00100, EDCRAGE)

    header = ['c87654', 'c87656', 'c87658', 'c87660', 'c87662', 'c87664',
              'c87666', 'c10960', 'c87668', 'c87681']
    return DataFrame(data=np.column_stack(outputs), columns=header)


def NonEdCr_calc(c87550, MARS, _edphhm, FLPDYR, DEFAULT_YR, c00100, _num, 
    c07180, e07200, c07230, e07240, e07960, e07260, e07300,
    e07700, e07250, t07950, c05800, _precrd, _edphhs):

    # Nonrefundable Education Credits

    # Form 8863 Tentative Education Credits
    c87560 = c87550

    # Phase Out
    if MARS == 2:
        c87570 = _edphhm[FLPDYR - DEFAULT_YR] * 1000
    else:
        c87570 = _edphhs[FLPDYR - DEFAULT_YR] * 1000

    c87580 = c00100

    c87590 = max(0, c87570 - c87580)

    c87600 = 10000 * _num

    c87610 = min(1, c87590 / c87600)

    c87620 = c87560 * c87610

    _ctc1 = c07180 + e07200 + c07230

    _ctc2 = e07240 + e07960 + e07260 + e07300

    _regcrd = _ctc1 + _ctc2

    _exocrd = e07700 + e07250

    _exocrd = _exocrd + t07950

    _ctctax = c05800 - _regcrd - _exocrd

    c07220 = min(_precrd, max(0, _ctctax))
    # lt tax owed
    return (c87560, c87570, c87580, c87590, c87600, c87610,
               c87620, _ctc1, _ctc2, _regcrd, _exocrd, _ctctax, c07220)



def NonEdCr_apply(  c87560, c87570, c87580, c87590, c87600, c87610,
                    c87620, _ctc1, _ctc2, _regcrd, _exocrd, _ctctax, c07220,
                    c87550, MARS, _edphhm, FLPDYR, DEFAULT_YR, c00100, _num, 
                    c07180, e07200, c07230, e07240, e07960, e07260, e07300,
                    e07700, e07250, t07950, c05800, _precrd, _edphhs ):

    for i in range(len(_taxinc)):

        (   c87560[i], c87570[i], c87580[i], c87590[i], c87600[i], c87610[i], 
            c87620[i], _ctc1[i], _ctc2[i], _regcrd[i], _exocrd[i], _ctctax[i], 
            c07220[i]) = NonEdCr_calc(c87550[i], MARS[i], _edphhm, FLPDYR[i], 
            DEFAULT_YR, c00100[i], _num[i], c07180[i], e07200[i], c07230[i], 
            e07240[i], e07960[i], e07260[i], e07300[i], e07700[i], e07250[i], 
            t07950[i], c05800[i], _precrd[i], _edphhs)

    return (c87560, c87570, c87580, c87590, c87600, c87610,
               c87620, _ctc1, _ctc2, _regcrd, _exocrd, _ctctax, c07220)    

def NonEdCr(c87550, p):
    global c07220

    outputs = NonEdCr_apply(  p.c87560, p.c87570, p.c87580, p.c87590, p.c87600, 
                p.c87610, p.c87620, p._ctc1, p._ctc2, p._regcrd, p._exocrd, 
                p._ctctax, p.c07220, c87550, MARS, p._edphhm, FLPDYR, 
                p.DEFAULT_YR, c00100, _num, c07180, e07200, c07230, e07240, 
                e07960, e07260, e07300, e07700, e07250, t07950, c05800, _precrd,
                p._edphhs )

    header = ['c87560', 'c87570', 'c87580', 'c87590', 'c87600', 'c87610',
              'c87620', '_ctc1', '_ctc2', '_regcrd', '_exocrd', '_ctctax',
              'c07220']

    return DataFrame(data=np.column_stack(outputs), columns=header)


def AddCTC_calc(_nctcr, _precrd, c07220, e00200, e82882, e30100, _sey, _setax, 
                _exact, e82880, _ealim, FLPDYR, DEFAULT_YR, _adctcrt, _ssmax,
                e03260, e09800, c59660, e11200, puf, e59680, e59700, e59720,
                _fixup, e11070):

    # Additional Child Tax Credit

    c82940 = 0

    # Part I of 2005 form 8812
    if _nctcr > 0:
        c82925 = _precrd

        c82930 = c07220

        c82935 = c82925 - c82930

        # CTC not applied to tax

        c82880 = max( 0, e00200 + e82882 + e30100 
                        + max(0, _sey) - 0.5 * _setax)
        if _exact == 1:
            c82880 = e82880

        h82880 = c82880

        c82885 = max(0, c82880 - _ealim[FLPDYR - DEFAULT_YR])

        c82890 = _adctcrt[FLPDYR - DEFAULT_YR] * c82885
    else:
        c82925, c82930, c82935, c82880, h82880, c82885, c82890 = (0, 0, 0, 
            0, 0, 0, 0)

    # Part II of 2005 form 8812

    if _nctcr > 2 and c82890 < c82935:
        c82900 = 0.0765 * min(_ssmax[FLPDYR - DEFAULT_YR], c82880)

        c82905 = e03260 + e09800

        c82910 = c82900 + c82905
        
        c82915 = c59660 + e11200

        c82920 = max(0, c82910 - c82915)

        c82937 = max(c82890, c82920)


    else:
        c82900, c82905, c82910, c82915, c82920, c82937 = 0, 0, 0, 0, 0, 0

    # Part II of 2005 form 8812
    if _nctcr > 2 and c82890 >= c82935:
        c82940 = c82935

    if _nctcr > 2 and c82890 < c82935:
        c82940 = min(c82935, c82937)

    if _nctcr > 0:
        c11070 = c82940
    else: 
        c11070 = 0

                #WHY ARE WE SETTING AN 'E' VALUE HERE?     
    if puf == True and _nctcr > 0:
        e59660 = e59680 + e59700 + e59720
    else:
        e59660 = 0

    if _nctcr > 0:
        _othadd = e11070 - c11070
    else:
        _othadd = 0

    if _nctcr  > 0 and _fixup >= 4:
        c11070 = c11070 + _othadd


    return ( c82925, c82930, c82935, c82880, h82880, c82885, c82890,
            c82900, c82905, c82910, c82915, c82920, c82937, c82940, c11070,
            e59660, _othadd)

def AddCTC_apply(c82925, c82930, c82935, c82880, h82880, c82885, c82890,
            c82900, c82905, c82910, c82915, c82920, c82937, c82940, c11070,
            e59660, _othadd, _nctcr, _precrd, c07220, e00200, e82882, e30100, 
            _sey, _setax, _exact, e82880, _ealim, FLPDYR, DEFAULT_YR, _adctcrt, 
            _ssmax, e03260, e09800, c59660, e11200, puf, e59680, e59700, e59720,
            _fixup, e11070 ):

    for i in range(len(_taxinc)):
        (   c82925[i], c82930[i], c82935[i], c82880[i], h82880[i], 
            c82885[i], c82890[i], c82900[i], c82905[i], c82910[i], c82915[i], 
            c82920[i], c82937[i], c82940[i], c11070[i], e59660[i], 
            _othadd[i]) = AddCTC_calc(_nctcr[i], _precrd[i], c07220[i], 
            e00200[i], e82882[i], e30100[i], _sey[i], _setax[i], _exact[i], 
            e82880[i], _ealim, FLPDYR[i], DEFAULT_YR, _adctcrt, _ssmax, 
            e03260[i], e09800[i], c59660[i], e11200[i], puf, e59680[i], 
            e59700[i], e59720[i], _fixup[i], e11070[i])



    return (c82925, c82930, c82935, c82880, h82880, c82885, c82890,
            c82900, c82905, c82910, c82915, c82920, c82937, c82940, c11070,
            e59660, _othadd)

def AddCTC(puf, p):

    outputs = AddCTC_apply( p.c82925, p.c82930, p.c82935, p.c82880, 
                            p.h82880, p.c82885, p.c82890, p.c82900, p.c82905, 
                            p.c82910, p.c82915, p.c82920, p.c82937, p.c82940, 
                            p.c11070, p.e59660, p._othadd, _nctcr, _precrd, 
                            c07220, e00200, e82882, e30100, _sey, _setax, 
                            _exact, e82880, p._ealim, FLPDYR, p.DEFAULT_YR, 
                            p._adctcrt, p._ssmax, e03260, e09800, c59660, 
                            e11200, puf, e59680, e59700, e59720, _fixup, e11070)

    header = ['c82925', 'c82930', 'c82935', 'c82880', 'h82880',
              'c82885', 'c82890', 'c82900', 'c82905', 'c82910', 'c82915',
              'c82920', 'c82937', 'c82940', 'c11070', 'e59660', '_othadd']

    return DataFrame(data=np.column_stack(outputs), columns=header)


def F5405():
    # Form 5405 First-Time Homebuyer Credit
    #not needed

    c64450 = np.zeros((dim,))
    return DataFrame(data=np.column_stack((c64450,)), columns=['c64450'])

def C1040_calc( e07400, e07180, e07200, c07220, c07230, e07250,
                e07600, e07260, c07970, e07300, x07400, e09720,
                e07500, e07700, e08000, e07240, e08001, e07960, e07970,
                SOIYR, e07980, c05800, puf, e08800, e09900, e09400, e09800, 
                e10000, e10100, e09700, e10050, e10075, e09805, e09710, c59660 ):

    # Credits 1040 line 48

    x07400 = e07400
    c07100 = (e07180 + e07200 + c07220 + c07230 + e07250
              + e07600 + e07260 + c07970 + e07300 + x07400
              + e07500 + e07700 + e08000)

    y07100 = c07100

    c07100 = c07100 + e07240
    c07100 = c07100 + e08001
    c07100 = c07100 + e07960 + e07970

    if SOIYR >= 2009:
        c07100 = c07100 + e07980
 
    x07100 = c07100
    c07100 = min(c07100, c05800)

    # Tax After credits 1040 line 52

    _eitc = c59660
    c08795 = max(0, c05800 - c07100)

    c08800 = c08795

    if puf == True:
        e08795 = e08800
    else:
        e08795 = 0

    # Tax before refundable credits

    c09200 = c08795 + e09900 + e09400 + e09800 + e10000 + e10100
    c09200 = c09200 + e09700
    c09200 = c09200 + e10050
    c09200 = c09200 + e10075
    c09200 = c09200 + e09805
    c09200 = c09200 + e09710 + e09720

    return (c07100, y07100, x07100, c08795, c08800, e08795, c09200, _eitc)

def C1040_apply(c07100, y07100, x07100, c08795, c08800, e08795, c09200, _eitc, 
                e07400, e07180, e07200, c07220, c07230, e07250,
                e07600, e07260, c07970, e07300, x07400, e09720,
                e07500, e07700, e08000, e07240, e08001, e07960, e07970,
                SOIYR, e07980, c05800, puf, e08800, e09900, e09400, e09800, 
                e10000, e10100, e09700, e10050, e10075, e09805, e09710, c59660): 
    
    for i in range(len(_taxinc)):



        (   c07100[i], y07100[i], x07100[i], c08795[i], c08800[i], e08795[i], 
            c09200[i], _eitc[i]) = C1040_calc( e07400[i], e07180[i], e07200[i], 
            c07220[i], c07230[i], e07250[i], e07600[i], e07260[i], c07970[i], 
            e07300[i], x07400[i], e09720[i], e07500[i], e07700[i], e08000[i], 
            e07240[i], e08001[i], e07960[i], e07970[i], SOIYR[i], e07980[i], 
            c05800[i], puf, e08800[i], e09900[i], e09400[i], e09800[i], 
            e10000[i], e10100[i], e09700[i], e10050[i], e10075[i], e09805[i], 
            e09710[i], c59660[i])

    return (c07100, y07100, x07100, c08795, c08800, e08795, c09200, _eitc)

def C1040(puf, p):
    global c08795
    global c09200
    global c07100
    global _eitc

    outputs = C1040_apply(  p.c07100, p.y07100, p.x07100, p.c08795, p.c08800, 
                            p.e08795, p.c09200, p._eitc, e07400, e07180, e07200, 
                            c07220, c07230, e07250, e07600, e07260, c07970, e07300, 
                            p.x07400, e09720, e07500, e07700, e08000, e07240, 
                            e08001, e07960, e07970, SOIYR, e07980, c05800, puf, 
                            e08800, e09900, e09400, e09800, e10000, e10100, 
                            e09700, e10050, e10075, e09805, e09710, c59660)

    header = ['c07100', 'y07100', 'x07100', 'c08795', 'c08800', 'e08795',
              'c09200', '_eitc']
    return DataFrame(data=np.column_stack(outputs), columns=header), _eitc


def DEITC_calc(c08795, c59660, c09200, c07100 ):

    # Decomposition of EITC


    if c08795 > 0 and c59660 > 0 and c08795 <= c59660:
       c59680 = c08795

       _comb = c59660 - c59680

    else:   
        c59680 = 0
        _comb = 0

    if c08795 > 0 and c59660 > 0 and c08795 > c59660: 
        c59680 = c59660


    if (c08795 > 0 and c59660 > 0 and _comb > 0 and c09200 - c08795 > 0 and c09200 - c08795 > _comb): 
        c59700 = _comb
    else:
        c59700 = 0

    if (c08795 > 0 and c59660 > 0 and _comb > 0 and c09200 - c08795 > 0 and c09200 - c08795 <= _comb):  
        c59700 = c59700 = c09200 - c08795
        c59720 = c59660 - c59680 - c59700
    else: c59720 = 0

    if c08795 == 0 and c59660 > 0:
        c59680 = 0 

    if c08795 == 0 and c59660 > 0 and c09200 > 0 and c09200 > c59660:
        c59700 = c59660

    if c08795 == 0 and c59660 > 0 and c09200 > 0 and c09200 < c59660:
        c59700 = c09200
        c59720 = c59660 - c59700

    if c08795 == 0 and c59660 > 0 and c09200 <= 0:
        c59720 = c59660 - c59700

    # Ask dan about this section of code! e.g., Compb goes to zero

    if c08795 < 0 or c59660 <= 0: 
        _compb = 0
        c59680 = 0
        c59700 = 0
        c59720 = 0

    else: 
        _compb = 0


    c07150 = c07100 + c59680
    c07150 = c07150
    c10950 = 0

    return (c59680, c59700, c59720, _comb, c07150, c10950)

def DEITC_apply(c59680, c59700, c59720, _comb, c07150, c10950, c08795, c59660, 
                c09200, c07100 ):



    for i in range(len(_taxinc)):   
        (   c59680[i], c59700[i], c59720[i], _comb[i], c07150[i], 
            c10950[i]) = DEITC_calc(c08795[i], c59660[i], c09200[i], c07100[i])


    return (c59680, c59700, c59720, _comb, c07150, c10950)


def DEITC(p):
    global c59700
    global c10950

    outputs = DEITC_apply(  p.c59680, p.c59700, p.c59720, p._comb, p.c07150, 
                            p.c10950, c08795, c59660, c09200, c07100 )

    header = ['c59680', 'c59700', 'c59720', '_comb', 'c07150', 'c10950']

    return DataFrame(data=np.column_stack(outputs), columns=header)




def SOIT_calc(   c09200, e10000, e59680, c59700,e11070, e11550, e11580,e09710, 
            e09720, e11581, e11582, e87900, e87905, e87681, e87682, c10950, 
            e11451, e11452, e11601, e11602, _eitc ):

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
    c10300 = max(c10300, 0)

    # Ignore refundable partof _eitc to obtain SOI income tax

    if c09200 <= _eitc:
        _eitc = c09200
        c10300 = 0


    return (c10300, _eitc)

def SOIT_apply( c10300, c09200, e10000, e59680, c59700, e11070, e11550, 
                e11580, e09710, e09720, e11581, e11582, e87900, e87905, e87681, 
                e87682, c10950, e11451, e11452, e11601, e11602, _eitc):

    for i in range(len(_taxinc)): 
        (   c10300[i], _eitc[i]) = SOIT_calc(c09200[i], e10000[i], e59680[i], 
            c59700[i],e11070[i], e11550[i], e11580[i],e09710[i], e09720[i], 
            e11581[i], e11582[i], e87900[i], e87905[i], e87681[i], e87682[i], 
            c10950[i], e11451[i], e11452[i], e11601[i], e11602[i], _eitc[i] )

    return (c10300, _eitc)

def SOIT(_eitc, p):

    outputs = SOIT_apply(   p.c10300, c09200, e10000, e59680, c59700, 
                            e11070, e11550, e11580, e09710, e09720, e11581, 
                            e11582, e87900, e87905, e87681, e87682, c10950, 
                            e11451, e11452, e11601, e11602, _eitc)

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

@jit('float64(float64, int64, int64, int64)', nopython = True)
def Taxer_i(inc_in, MARS, FLPDYR, DEFAULT_YR):
    ## note still should pass in all globals being used, including _rt1-_rt7 and _brk1-_brk6

    # low = 0 
    # med = 0

    # if inc_in < 3000:
    #     low = 1 

    # elif inc_in >=3000 and inc_in < 100000:
    #     med = 1 

    # _a1 = inc_in * 0.01

    # # if _a1 < 0:
    # #     _a2 = math.floor(_a1) - 1 
    # # else: _a2 = math.floor(_a1)
    # _a2 = math.floor(_a1)

    # _a3 = _a2 * 100

    # _a4 = (_a1 - _a2) * 100

    # _a5 = 0

    # if low == 1 and _a4 < 25:
    #     _a5 = 13
    # elif low == 1 and (25 <= _a4 < 50):
    #     _a5 = 38
    # elif low == 1 and (50 <= _a4 < 75):
    #     _a5 = 63
    # elif low == 1 and _a4 >= 75:
    #     _a5 = 88
    # elif med == 1 and _a4 < 50:
    #     _a5 = 25
    # elif med == 1 and _a4 >= 50: 
    #     _a5 = 75
    # if inc_in == 0:
    #     _a5 = 0

    # if low == 1 or med == 1:
    #     _a6 = _a3 + _a5 
    # else: _a6 = inc_in

    _a6 = inc_in

    inc_out = (_rt1[FLPDYR - DEFAULT_YR] * min(_a6, _brk1[FLPDYR - DEFAULT_YR, MARS - 1])
               + _rt2[FLPDYR - DEFAULT_YR]
               * min(_brk2[FLPDYR - DEFAULT_YR, MARS - 1] - _brk1[FLPDYR - DEFAULT_YR, MARS - 1],
                            max(0., _a6 - _brk1[FLPDYR - DEFAULT_YR, MARS - 1]))
               + _rt3[FLPDYR - DEFAULT_YR]
               * min(_brk3[FLPDYR - DEFAULT_YR, MARS - 1] - _brk2[FLPDYR - DEFAULT_YR, MARS - 1],
                            max(0., _a6 - _brk2[FLPDYR - DEFAULT_YR, MARS - 1]))
               + _rt4[FLPDYR - DEFAULT_YR]
               * min(_brk4[FLPDYR - DEFAULT_YR, MARS - 1] - _brk3[FLPDYR - DEFAULT_YR, MARS - 1],
                            max(0., _a6 - _brk3[FLPDYR - DEFAULT_YR, MARS - 1]))
               + _rt5[FLPDYR - DEFAULT_YR]
               * min(_brk5[FLPDYR - DEFAULT_YR, MARS - 1] - _brk4[FLPDYR - DEFAULT_YR, MARS - 1],
                            max(0., _a6 - _brk4[FLPDYR - DEFAULT_YR, MARS - 1]))
               + _rt6[FLPDYR - DEFAULT_YR]
               * min(_brk6[FLPDYR - DEFAULT_YR, MARS - 1] - _brk5[FLPDYR - DEFAULT_YR, MARS - 1],
                            max(0., _a6 - _brk5[FLPDYR - DEFAULT_YR, MARS - 1]))
               + _rt7[FLPDYR - DEFAULT_YR] * max(0., _a6 - _brk6[FLPDYR - DEFAULT_YR, MARS - 1]))

    return inc_out

#export('Taxer_i f8(f8, f8, i8, i8, i8)')(Taxer_i)


