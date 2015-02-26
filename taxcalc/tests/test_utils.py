import os
import sys
cur_path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(cur_path, "../../"))
sys.path.append(os.path.join(cur_path, "../"))
import numpy as np
import pandas as pd
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


def test_expand_1D_short_array():
    x = np.array([4, 5, 9], dtype='i4')
    exp2 = np.array([9.0 * math.pow(1.02, i) for i in range(1, 8)])
    exp1 = np.array([4, 5, 9])
    exp = np.zeros(10)
    exp[:3] = exp1
    exp[3:] = exp2
    res = expand_1D(x, inflate=True, inflation_rate=0.02, num_years=10)
    assert(np.allclose(exp.astype(x.dtype, casting='unsafe'), res))


def test_expand_1D_scalar():
    x = 10.0
    exp = np.array([10.0 * math.pow(1.02, i) for i in range(0, 10)])
    res = expand_1D(x, inflate=True, inflation_rate=0.02, num_years=10)
    assert(np.allclose(exp, res))


def test_expand_2D_short_array():
    x = np.array([[1, 2, 3]], dtype='f8')
    val = np.array([1, 2, 3], dtype='f8')
    exp2 = np.array([val * math.pow(1.02, i) for i in range(1, 5)])
    exp1 = np.array([1, 2, 3], dtype='f8')
    exp = np.zeros((5, 3))
    exp[:1] = exp1
    exp[1:] = exp2
    res = expand_2D(x, inflate=True, inflation_rate=0.02, num_years=5)
    assert(np.allclose(exp, res))


def test_create_tables():
    # Default Plans
    #Create a Public Use File object
    cur_path = os.path.abspath(os.path.dirname(__file__))
    tax_dta_path = os.path.join(cur_path, "../../tax_all91_puf.gz")
    # Create a default Parameters object
    params1 = Parameters(start_year=91)
    records1 = Records(tax_dta_path)
    # Create a Calculator
    calc1 = Calculator(parameters=params1, records=records1)
    calc1.calc_all()

    # User specified Plans
    user_mods = '{"_rt4": [0.56]}'
    params2 = Parameters(start_year=91)
    records2 = Records(tax_dta_path)
    # Create a Calculator
    calc2 = calculator(parameters=params2, records=records2, mods=user_mods)
    calc2.calc_all()

    t2 = create_distribution_table(calc2, groupby="agi_bins")
    tdiff = create_difference_table(calc1, calc2, groupby="agi_bins")


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
 
