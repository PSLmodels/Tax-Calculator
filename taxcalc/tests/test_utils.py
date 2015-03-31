import os
import sys
cur_path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(cur_path, "../../"))
sys.path.append(os.path.join(cur_path, "../"))
import numpy as np
import pandas as pd
import pytest
from pandas import DataFrame, Series
from pandas.util.testing import assert_frame_equal
from pandas.util.testing import assert_series_equal
from numba import jit, vectorize, guvectorize
from taxcalc import *


data = [[1.0, 2, 'a'],
        [-1.0, 4, 'a'],
        [3.0, 6, 'a'],
        [2.0, 4, 'b'],
        [3.0, 6, 'b']]

irates = {1991:0.015, 1992:0.020, 1993:0.022, 1994:0.020, 1995:0.021,
          1996:0.022, 1997:0.023, 1998:0.024, 1999:0.024, 2000:0.024,
          2001:0.024, 2002:0.024}

def test_expand_1D_short_array():
    x = np.array([4, 5, 9], dtype='i4')
    exp2 = np.array([9.0 * math.pow(1.02, i) for i in range(1, 8)])
    exp1 = np.array([4, 5, 9])
    exp = np.zeros(10)
    exp[:3] = exp1
    exp[3:] = exp2
    res = expand_1D(x, inflate=True, inflation_rates=[0.02]*10, num_years=10)
    assert(np.allclose(exp.astype(x.dtype, casting='unsafe'), res))

def test_expand_1D_variable_rates():
    x = np.array([4, 5, 9], dtype='f4')
    irates = [0.02, 0.02, 0.02, 0.03, 0.035]
    exp2 = []
    cur = 9.0
    for i in range(1, 3):
        idx = i + len(x) - 1
        cur *= (1.0 + irates[idx])
        exp2.append(cur)

    exp1 = np.array([4, 5, 9])
    exp = np.zeros(5)
    exp[:3] = exp1
    exp[3:] = exp2
    res = expand_1D(x, inflate=True, inflation_rates=irates, num_years=5)
    assert(np.allclose(exp.astype(x.dtype, casting='unsafe'), res))


def test_expand_1D_scalar():
    x = 10.0
    exp = np.array([10.0 * math.pow(1.02, i) for i in range(0, 10)])
    res = expand_1D(x, inflate=True, inflation_rates=[0.02]*10, num_years=10)
    assert(np.allclose(exp, res))


def test_expand_2D_short_array():
    x = np.array([[1, 2, 3]], dtype='f8')
    val = np.array([1, 2, 3], dtype='f8')
    exp2 = np.array([val * math.pow(1.02, i) for i in range(1, 5)])
    exp1 = np.array([1, 2, 3], dtype='f8')
    exp = np.zeros((5, 3))
    exp[:1] = exp1
    exp[1:] = exp2
    res = expand_2D(x, inflate=True, inflation_rates=[0.02]*5, num_years=5)
    assert(np.allclose(exp, res))


def test_expand_2D_variable_rates():
    x = np.array([[1, 2, 3]], dtype='f8')
    cur = np.array([1, 2, 3], dtype='f8')
    irates = [0.02, 0.02, 0.02, 0.03, 0.035]

    exp2 = []
    for i in range(1, 5):
        idx = i + len(x) - 1
        cur = np.array(cur*(1.0 + irates[idx]))
        print("cur is ", cur)
        exp2.append(cur)

    #exp2 = np.array([val * math.pow(1.02, i) for i in range(1, 5)])
    exp1 = np.array([1, 2, 3], dtype='f8')
    exp = np.zeros((5, 3))
    exp[:1] = exp1
    exp[1:] = exp2
    res = expand_2D(x, inflate=True, inflation_rates=irates, num_years=5)
    assert(np.allclose(exp, res))



def test_create_tables():
    # Default Plans
    #Create a Public Use File object
    cur_path = os.path.abspath(os.path.dirname(__file__))
    tax_dta_path = os.path.join(cur_path, "../../tax_all1991_puf.gz")
    # Create a default Parameters object
    params1 = Parameters(start_year=1991, inflation_rates=irates)
    records1 = Records(tax_dta_path)
    # Create a Calculator
    calc1 = Calculator(parameters=params1, records=records1)
    calc1.calc_all()

    # User specified Plans
    user_mods = '{"1991": {"_II_rt4": [0.56]}}'
    params2 = Parameters(start_year=1991, inflation_rates=irates)
    records2 = Records(tax_dta_path)
    # Create a Calculator
    calc2 = calculator(parameters=params2, records=records2, mods=user_mods)

    calc2.calc_all()

    t2 = create_distribution_table(calc2, groupby="small_agi_bins", result_type = "weighted_sum")
    tdiff = create_difference_table(calc1, calc2, groupby="large_agi_bins")


def test_weighted_count_lt_zero():
    df = DataFrame(data=data, columns=['tax_diff', 's006', 'label'])
    grped = df.groupby('label')
    diffs = grped.apply(weighted_count_lt_zero, 'tax_diff')
    exp = Series(data=[4, 0], index=['a', 'b'])
    assert_series_equal(exp, diffs)


def test_weighted_count_gt_zero():
    df = DataFrame(data=data, columns=['tax_diff', 's006', 'label'])
    grped = df.groupby('label')
    diffs = grped.apply(weighted_count_gt_zero, 'tax_diff')
    exp = Series(data=[8, 10], index=['a', 'b'])
    assert_series_equal(exp, diffs)
 

def test_weighted_count():
    df = DataFrame(data=data, columns=['tax_diff', 's006', 'label'])
    grped = df.groupby('label')
    diffs = grped.apply(weighted_count)
    exp = Series(data=[12, 10], index=['a', 'b'])
    assert_series_equal(exp, diffs)
 

def test_weighted_mean():
    df = DataFrame(data=data, columns=['tax_diff', 's006', 'label'])
    grped = df.groupby('label')
    diffs = grped.apply(weighted_mean, 'tax_diff')
    exp = Series(data=[16.0/12.0, 26.0/10.0], index=['a', 'b'])
    assert_series_equal(exp, diffs)
 

def test_weighted_sum():
    df = DataFrame(data=data, columns=['tax_diff', 's006', 'label'])
    grped = df.groupby('label')
    diffs = grped.apply(weighted_sum, 'tax_diff')
    exp = Series(data=[16.0, 26.0], index=['a', 'b'])
    assert_series_equal(exp, diffs)
 

def test_weighted_perc_inc():
    df = DataFrame(data=data, columns=['tax_diff', 's006', 'label'])
    grped = df.groupby('label')
    diffs = grped.apply(weighted_perc_inc, 'tax_diff')
    exp = Series(data=[8./12., 1.0], index=['a', 'b'])
    assert_series_equal(exp, diffs)


def test_weighted_perc_dec():
    df = DataFrame(data=data, columns=['tax_diff', 's006', 'label'])
    grped = df.groupby('label')
    diffs = grped.apply(weighted_perc_dec, 'tax_diff')
    exp = Series(data=[4./12., 0.0], index=['a', 'b'])
    assert_series_equal(exp, diffs)


def test_weighted_share_of_total():
    df = DataFrame(data=data, columns=['tax_diff', 's006', 'label'])
    grped = df.groupby('label')
    diffs = grped.apply(weighted_share_of_total, 'tax_diff', 42.0)
    exp = Series(data=[16.0/42., 26.0/42.0], index=['a', 'b'])
    assert_series_equal(exp, diffs)


def test_add_income_bins():
    data = np.arange(1,1e6, 5000)
    df = DataFrame(data=data, columns=['c00100'])
    bins = [-1e14, 0, 9999, 19999, 29999, 39999, 49999, 74999, 99999,
            200000, 1e14]
    df = add_income_bins(df, compare_with ="tpc", bins=None)
    grpd = df.groupby('bins')
    grps = [grp for grp in grpd]

    for g, num in zip(grps, bins[1:-1]):
        assert g[0].endswith(str(num) + "]")

    grpdl = add_income_bins(df, compare_with ="tpc", bins=None, right=False)
    grpdl = grpdl.groupby('bins')
    grps = [grp for grp in grpdl]

    for g, num in zip(grps, bins[1:-1]):
        assert g[0].endswith(str(num) + ")")


def test_add_income_bins_soi():
    data = np.arange(1,1e6, 5000)
    df = DataFrame(data=data, columns=['c00100'])

    bins = [-1e14, 0, 4999, 9999, 14999, 19999, 24999, 29999, 39999,
            49999, 74999, 99999, 199999, 499999, 999999, 1499999,
            1999999, 4999999, 9999999, 1e14]

    df = add_income_bins(df, compare_with ="soi", bins=None)
    grpd = df.groupby('bins')
    grps = [grp for grp in grpd]

    for g, num in zip(grps, bins[1:-1]):
        assert g[0].endswith(str(num) + "]")

    grpdl = add_income_bins(df, compare_with ="soi", bins=None, right=False)
    grpdl = grpdl.groupby('bins')
    grps = [grp for grp in grpdl]

    for g, num in zip(grps, bins[1:-1]):
        assert g[0].endswith(str(num) + ")")


def test_add_income_bins_specify_bins():
    data = np.arange(1,1e6, 5000)
    df = DataFrame(data=data, columns=['c00100'])

    bins = [-1e14, 0, 4999, 9999, 14999, 19999, 29999, 32999, 43999,
            1e14]

    df = add_income_bins(df, bins=bins)
    grpd = df.groupby('bins')
    grps = [grp for grp in grpd]

    for g, num in zip(grps, bins[1:-1]):
        assert g[0].endswith(str(num) + "]")

    grpdl = add_income_bins(df, bins=bins, right=False)
    grpdl = grpdl.groupby('bins')
    grps = [grp for grp in grpdl]

    for g, num in zip(grps, bins[1:-1]):
        assert g[0].endswith(str(num) + ")")


def test_add_income_bins_raises():
    data = np.arange(1,1e6, 5000)
    df = DataFrame(data=data, columns=['c00100'])

    with pytest.raises(ValueError):
        df = add_income_bins(df, compare_with ="stuff")

def test_add_weighted_decile_bins():

    df = DataFrame(data=data, columns=['c00100', 's006', 'label'])
    df = add_weighted_decile_bins(df)
    assert 'bins' in df
