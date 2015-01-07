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
    #global _feided, c02900
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


