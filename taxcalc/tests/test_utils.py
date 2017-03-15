import os
import sys
import math
import filecmp
import tempfile
import numpy as np
import pandas as pd
import pytest
import numpy.testing as npt
from pandas import DataFrame, Series
from pandas.util.testing import assert_series_equal
from taxcalc import Policy, Records, Behavior, Calculator
from taxcalc.utils import *

data = [[1.0, 2, 'a'],
        [-1.0, 4, 'a'],
        [3.0, 6, 'a'],
        [2.0, 4, 'b'],
        [3.0, 6, 'b']]

weight_data = [[1.0, 2.0, 10.0],
               [2.0, 4.0, 20.0],
               [3.0, 6.0, 30.0]]

data_float = [[1.0, 2, 'a'],
              [-1.0, 4, 'a'],
              [0.0000000001, 3, 'a'],
              [-0.0000000001, 1, 'a'],
              [3.0, 6, 'a'],
              [2.0, 4, 'b'],
              [0.0000000001, 3, 'b'],
              [-0.0000000001, 1, 'b'],
              [3.0, 6, 'b']]


def test_expand_1D_short_array():
    x = np.array([4, 5, 9], dtype='i4')
    exp2 = np.array([9.0 * math.pow(1.02, i) for i in range(1, 8)])
    exp1 = np.array([4, 5, 9])
    exp = np.zeros(10)
    exp[:3] = exp1
    exp[3:] = exp2
    res = Policy.expand_1D(x, inflate=True, inflation_rates=[0.02] * 10,
                           num_years=10)
    npt.assert_allclose(exp, res, atol=0.0, rtol=1.0E-7)


def test_expand_1D_variable_rates():
    x = np.array([4, 5, 9], dtype='f4')
    irates = [0.02, 0.02, 0.03, 0.035]
    exp2 = []
    cur = 9.0
    exp = np.array([4, 5, 9, 9 * 1.03, 9 * 1.03 * 1.035])
    res = Policy.expand_1D(x, inflate=True, inflation_rates=irates,
                           num_years=5)
    npt.assert_allclose(exp.astype('f4', casting='unsafe'), res)


def test_expand_1D_scalar():
    x = 10.0
    exp = np.array([10.0 * math.pow(1.02, i) for i in range(0, 10)])
    res = Policy.expand_1D(x, inflate=True, inflation_rates=[0.02] * 10,
                           num_years=10)
    npt.assert_allclose(exp, res)


def test_expand_1D_accept_None():
    x = [4., 5., None]
    irates = [0.02, 0.02, 0.03, 0.035]
    exp = []
    cur = 5.0 * 1.02
    exp = [4., 5., cur]
    cur *= 1.03
    exp.append(cur)
    cur *= 1.035
    exp.append(cur)
    exp = np.array(exp)
    res = Policy.expand_array(x, inflate=True, inflation_rates=irates,
                              num_years=5)
    npt.assert_allclose(exp.astype('f4', casting='unsafe'), res)


def test_expand_2D_short_array():
    x = np.array([[1, 2, 3]], dtype=np.float64)
    val = np.array([1, 2, 3], dtype=np.float64)
    exp2 = np.array([val * math.pow(1.02, i) for i in range(1, 5)])
    exp1 = np.array([1, 2, 3], dtype=np.float64)
    exp = np.zeros((5, 3))
    exp[:1] = exp1
    exp[1:] = exp2
    res = Policy.expand_2D(x, inflate=True, inflation_rates=[0.02] * 5,
                           num_years=5)
    npt.assert_allclose(exp, res)


def test_expand_2D_variable_rates():
    x = np.array([[1, 2, 3]], dtype=np.float64)
    cur = np.array([1, 2, 3], dtype=np.float64)
    irates = [0.02, 0.02, 0.02, 0.03, 0.035]
    exp2 = []
    for i in range(0, 4):
        idx = i + len(x) - 1
        cur = np.array(cur * (1.0 + irates[idx]))
        print('cur is ', cur)
        exp2.append(cur)
    exp1 = np.array([1, 2, 3], dtype=np.float64)
    exp = np.zeros((5, 3), dtype=np.float64)
    exp[:1] = exp1
    exp[1:] = exp2
    res = Policy.expand_2D(x, inflate=True, inflation_rates=irates,
                           num_years=5)
    npt.assert_allclose(exp, res)


def test_validity_of_name_lists():
    assert len(TABLE_COLUMNS) == len(TABLE_LABELS)
    assert set(STATS_COLUMNS).issubset(Records.CALCULATED_VARS | {'s006'})


def test_create_tables(puf_1991, weights_1991):
    # create a current-law Policy object and Calculator object calc1
    policy1 = Policy()
    records1 = Records(data=puf_1991, weights=weights_1991, start_year=2009)
    calc1 = Calculator(policy=policy1, records=records1)
    calc1.calc_all()
    # create a policy-reform Policy object and Calculator object calc2
    reform = {2013: {'_II_rt4': [0.56]}}
    policy2 = Policy()
    policy2.implement_reform(reform)
    records2 = Records(data=puf_1991, weights=weights_1991, start_year=2009)
    calc2 = Calculator(policy=policy2, records=records2)
    calc2.calc_all()
    # test creating various distribution tables
    dt1 = create_difference_table(calc1.records, calc2.records,
                                  groupby='large_income_bins')
    dt2 = create_difference_table(calc1.records, calc2.records,
                                  groupby='webapp_income_bins')
    with pytest.raises(ValueError):
        dt = create_difference_table(calc1.records, calc2.records,
                                     groupby='bad_bins')
    with pytest.raises(ValueError):
        dt = create_distribution_table(calc2.records,
                                       groupby='small_income_bins',
                                       result_type='bad_result_type')
    with pytest.raises(ValueError):
        dt = create_distribution_table(calc2.records,
                                       groupby='bad_bins',
                                       result_type='weighted_sum')
    dt3 = create_distribution_table(calc2.records,
                                    groupby='small_income_bins',
                                    result_type='weighted_sum',
                                    baseline_obj=calc1.records, diffs=True)
    calc1.increment_year()
    with pytest.raises(ValueError):
        dt = create_difference_table(calc1.records, calc2.records,
                                     groupby='large_income_bins')
    with pytest.raises(ValueError):
        dt = create_distribution_table(calc2.records,
                                       groupby='small_income_bins',
                                       result_type='weighted_sum',
                                       baseline_obj=calc1.records, diffs=True)


def test_weighted_count_lt_zero():
    assert count_lt_zero([0.0, 1, -1, 0, -2.2, 1.1]) == 2
    df1 = DataFrame(data=data, columns=['tax_diff', 's006', 'label'])
    grped = df1.groupby('label')
    diffs = grped.apply(weighted_count_lt_zero, 'tax_diff')
    exp = Series(data=[4, 0], index=['a', 'b'])
    exp.index.name = 'label'
    assert_series_equal(exp, diffs)
    df2 = DataFrame(data=data_float, columns=['tax_diff', 's006', 'label'])
    grped = df2.groupby('label')
    diffs = grped.apply(weighted_count_lt_zero, 'tax_diff')
    exp = Series(data=[4, 0], index=['a', 'b'])
    exp.index.name = 'label'
    assert_series_equal(exp, diffs)


def test_weighted_count_gt_zero():
    assert count_gt_zero([0.0, 1, -1, 0, -2.2, 1.1]) == 2
    df1 = DataFrame(data=data, columns=['tax_diff', 's006', 'label'])
    grped = df1.groupby('label')
    diffs = grped.apply(weighted_count_gt_zero, 'tax_diff')
    exp = Series(data=[8, 10], index=['a', 'b'])
    exp.index.name = 'label'
    assert_series_equal(exp, diffs)
    df2 = DataFrame(data=data, columns=['tax_diff', 's006', 'label'])
    grped = df2.groupby('label')
    diffs = grped.apply(weighted_count_gt_zero, 'tax_diff')
    exp = Series(data=[8, 10], index=['a', 'b'])
    exp.index.name = 'label'
    assert_series_equal(exp, diffs)


def test_weighted_count():
    df = DataFrame(data=data, columns=['tax_diff', 's006', 'label'])
    grped = df.groupby('label')
    diffs = grped.apply(weighted_count)
    exp = Series(data=[12, 10], index=['a', 'b'])
    exp.index.name = 'label'
    assert_series_equal(exp, diffs)


def test_weighted_mean():
    df = DataFrame(data=data, columns=['tax_diff', 's006', 'label'])
    grped = df.groupby('label')
    diffs = grped.apply(weighted_mean, 'tax_diff')
    exp = Series(data=[16.0 / 12.0, 26.0 / 10.0], index=['a', 'b'])
    exp.index.name = 'label'
    assert_series_equal(exp, diffs)


def test_wage_weighted():
    df = DataFrame(data=weight_data, columns=['var', 's006', 'e00200'])
    wvar = wage_weighted(df, 'var')
    assert round(wvar, 4) == 2.5714


def test_agi_weighted():
    df = DataFrame(data=weight_data, columns=['var', 's006', 'c00100'])
    wvar = agi_weighted(df, 'var')
    assert round(wvar, 4) == 2.5714


def test_expanded_income_weighted():
    df = DataFrame(data=weight_data,
                   columns=['var', 's006', '_expanded_income'])
    wvar = expanded_income_weighted(df, 'var')
    assert round(wvar, 4) == 2.5714


def test_weighted_sum():
    df = DataFrame(data=data, columns=['tax_diff', 's006', 'label'])
    grped = df.groupby('label')
    diffs = grped.apply(weighted_sum, 'tax_diff')
    exp = Series(data=[16.0, 26.0], index=['a', 'b'])
    exp.index.name = 'label'
    assert_series_equal(exp, diffs)


def test_weighted_perc_inc():
    df = DataFrame(data=data, columns=['tax_diff', 's006', 'label'])
    grped = df.groupby('label')
    diffs = grped.apply(weighted_perc_inc, 'tax_diff')
    exp = Series(data=[8. / 12., 1.0], index=['a', 'b'])
    exp.index.name = 'label'
    assert_series_equal(exp, diffs)


def test_weighted_perc_dec():
    df = DataFrame(data=data, columns=['tax_diff', 's006', 'label'])
    grped = df.groupby('label')
    diffs = grped.apply(weighted_perc_dec, 'tax_diff')
    exp = Series(data=[4. / 12., 0.0], index=['a', 'b'])
    exp.index.name = 'label'
    assert_series_equal(exp, diffs)


def test_weighted_share_of_total():
    df = DataFrame(data=data, columns=['tax_diff', 's006', 'label'])
    grped = df.groupby('label')
    diffs = grped.apply(weighted_share_of_total, 'tax_diff', 42.0)
    exp = Series(data=[16.0 / (42. + EPSILON), 26.0 / (42.0 + EPSILON)],
                 index=['a', 'b'])
    exp.index.name = 'label'
    assert_series_equal(exp, diffs)


def test_add_income_bins():
    data = np.arange(1, 1e6, 5000)
    df = DataFrame(data=data, columns=['_expanded_income'])
    bins = [-1e14, 0, 9999, 19999, 29999, 39999, 49999, 74999, 99999,
            200000, 1e14]
    df = add_income_bins(df, compare_with='tpc', bins=None)
    grpd = df.groupby('bins')
    grps = [grp for grp in grpd]
    for g, num in zip(grps, bins[1:-1]):
        assert g[0].endswith(str(num) + ']')
    grpdl = add_income_bins(df, compare_with='tpc', bins=None, right=False)
    grpdl = grpdl.groupby('bins')
    grps = [grp for grp in grpdl]
    for g, num in zip(grps, bins[1:-1]):
        assert g[0].endswith(str(num) + ')')


def test_add_income_bins_soi():
    data = np.arange(1, 1e6, 5000)
    df = DataFrame(data=data, columns=['_expanded_income'])
    bins = [-1e14, 0, 4999, 9999, 14999, 19999, 24999, 29999, 39999,
            49999, 74999, 99999, 199999, 499999, 999999, 1499999,
            1999999, 4999999, 9999999, 1e14]
    df = add_income_bins(df, compare_with='soi', bins=None)
    grpd = df.groupby('bins')
    grps = [grp for grp in grpd]
    for g, num in zip(grps, bins[1:-1]):
        assert g[0].endswith(str(num) + ']')
    grpdl = add_income_bins(df, compare_with='soi', bins=None, right=False)
    grpdl = grpdl.groupby('bins')
    grps = [grp for grp in grpdl]
    for g, num in zip(grps, bins[1:-1]):
        assert g[0].endswith(str(num) + ')')


def test_add_income_bins_specify_bins():
    data = np.arange(1, 1e6, 5000)
    df = DataFrame(data=data, columns=['_expanded_income'])
    bins = [-1e14, 0, 4999, 9999, 14999, 19999, 29999, 32999, 43999,
            1e14]
    df = add_income_bins(df, bins=bins)
    grpd = df.groupby('bins')
    grps = [grp for grp in grpd]
    for g, num in zip(grps, bins[1:-1]):
        assert g[0].endswith(str(num) + ']')
    grpdl = add_income_bins(df, bins=bins, right=False)
    grpdl = grpdl.groupby('bins')
    grps = [grp for grp in grpdl]
    for g, num in zip(grps, bins[1:-1]):
        assert g[0].endswith(str(num) + ')')


def test_add_income_bins_raises():
    data = np.arange(1, 1e6, 5000)
    df = DataFrame(data=data, columns=['_expanded_income'])
    with pytest.raises(ValueError):
        df = add_income_bins(df, compare_with='stuff')


def test_add_weighted_income_bins():
    df = DataFrame(data=data, columns=['_expanded_income', 's006', 'label'])
    df = add_weighted_income_bins(df, num_bins=100)
    bin_labels = df['bins'].unique()
    default_labels = set(range(1, 101))
    for lab in bin_labels:
        assert lab in default_labels
    # Custom labels
    df = add_weighted_income_bins(df, weight_by_income_measure=True)
    assert 'bins' in df
    custom_labels = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j']
    df = add_weighted_income_bins(df, labels=custom_labels)
    assert 'bins' in df
    bin_labels = df['bins'].unique()
    for lab in bin_labels:
        assert lab in custom_labels


def test_add_columns():
    cols = [[1000, 40, -10, 0, 10],
            [100, 8, 9, 100, 20],
            [-1000, 38, 90, 800, 30]]
    df = DataFrame(data=cols,
                   columns=['c00100', 'c04470', '_standard', 'c09600', 's006'])
    add_columns(df)
    npt.assert_array_equal(df.c04470, np.array([40, 0, 0]))
    npt.assert_array_equal(df.num_returns_ItemDed, np.array([10, 0, 0]))
    npt.assert_array_equal(df.num_returns_StandardDed, np.array([0, 20, 0]))
    npt.assert_array_equal(df.num_returns_AMT, np.array([0, 20, 30]))


def test_dist_table_sum_row(records_2009):
    # Create a default Policy object
    policy1 = Policy()
    # Create a Calculator
    calc1 = Calculator(policy=policy1, records=records_2009)
    calc1.calc_all()
    t1 = create_distribution_table(calc1.records,
                                   groupby='small_income_bins',
                                   result_type='weighted_sum')
    t2 = create_distribution_table(calc1.records,
                                   groupby='large_income_bins',
                                   result_type='weighted_sum')
    npt.assert_allclose(t1[-1:], t2[-1:])
    t3 = create_distribution_table(calc1.records,
                                   groupby='small_income_bins',
                                   result_type='weighted_avg')


def test_diff_table_sum_row(puf_1991, weights_1991):
    # create a current-law Policy object and Calculator calc1
    policy1 = Policy()
    records1 = Records(data=puf_1991, weights=weights_1991, start_year=2009)
    calc1 = Calculator(policy=policy1, records=records1)
    calc1.calc_all()
    # create a policy-reform Policy object and Calculator calc2
    reform = {2013: {'_II_rt4': [0.56]}}
    policy2 = Policy()
    policy2.implement_reform(reform)
    records2 = Records(data=puf_1991, weights=weights_1991, start_year=2009)
    calc2 = Calculator(policy=policy2, records=records2)
    calc2.calc_all()
    # create two difference tables and compare their content
    tdiff1 = create_difference_table(calc1.records, calc2.records,
                                     groupby='small_income_bins')
    tdiff2 = create_difference_table(calc1.records, calc2.records,
                                     groupby='large_income_bins')
    non_digit_cols = ['mean', 'perc_inc', 'perc_cut', 'share_of_change']
    digit_cols = [x for x in tdiff1.columns.tolist() if
                  x not in non_digit_cols]
    npt.assert_allclose(tdiff1[digit_cols][-1:], tdiff2[digit_cols][-1:])
    assert np.array_equal(tdiff1[non_digit_cols][-1:],
                          tdiff2[non_digit_cols][-1:])


def test_row_classifier(puf_1991, weights_1991):
    # create a current-law Policy object and Calculator calc1
    policy1 = Policy()
    records1 = Records(data=puf_1991, weights=weights_1991, start_year=2009)
    calc1 = Calculator(policy=policy1, records=records1)
    calc1.calc_all()
    calc1_s006 = create_distribution_table(calc1.records,
                                           groupby='webapp_income_bins',
                                           result_type='weighted_sum').s006
    # create a policy-reform Policy object and Calculator calc2
    reform = {2013: {'_ALD_StudentLoan_hc': [1]}}
    policy2 = Policy()
    policy2.implement_reform(reform)
    records2 = Records(data=puf_1991, weights=weights_1991, start_year=2009)
    calc2 = Calculator(policy=policy2, records=records2)
    calc2.calc_all()
    calc2_s006 = create_distribution_table(calc2.records,
                                           groupby='webapp_income_bins',
                                           result_type='weighted_sum',
                                           baseline_obj=calc1.records).s006
    # use weighted sum of weights in each cell to check classifer
    npt.assert_array_equal(calc1_s006, calc2_s006)


def test_expand_2D_already_filled():
    _II_brk2 = [[36000, 72250, 36500, 48600, 72500, 36250],
                [38000, 74000, 36900, 49400, 73800, 36900],
                [40000, 74900, 37450, 50200, 74900, 37450]]
    res = Policy.expand_2D(_II_brk2, inflate=True, inflation_rates=[0.02] * 5,
                           num_years=3)
    npt.assert_array_equal(res, np.array(_II_brk2))


def test_expand_2D_partial_expand():
    _II_brk2 = [[36000, 72250, 36500, 48600, 72500, 36250],
                [38000, 74000, 36900, 49400, 73800, 36900],
                [40000, 74900, 37450, 50200, 74900, 37450]]
    # We have three years worth of data, need 4 years worth,
    # but we only need the inflation rate for year 3 to go
    # from year 3 -> year 4
    inf_rates = [0.02, 0.02, 0.03]
    exp1 = 40000 * 1.03
    exp2 = 74900 * 1.03
    exp3 = 37450 * 1.03
    exp4 = 50200 * 1.03
    exp5 = 74900 * 1.03
    exp6 = 37450 * 1.03
    exp = [[36000, 72250, 36500, 48600, 72500, 36250],
           [38000, 74000, 36900, 49400, 73800, 36900],
           [40000, 74900, 37450, 50200, 74900, 37450],
           [exp1, exp2, exp3, exp4, exp5, exp6]]
    res = Policy.expand_2D(_II_brk2, inflate=True, inflation_rates=inf_rates,
                           num_years=4)
    npt.assert_array_equal(res, exp)


def test_strip_Nones():
    x = [None, None]
    assert Policy.strip_Nones(x) == []
    x = [1, 2, None]
    assert Policy.strip_Nones(x) == [1, 2]
    x = [[1, 2, 3], [4, None, None]]
    assert Policy.strip_Nones(x) == [[1, 2, 3], [4, -1, -1]]


def test_expand_2D_accept_None():
    _II_brk2 = [[36000, 72250, 36500, 48600, 72500, 36250],
                [38000, 74000, 36900, 49400, 73800, 36900],
                [40000, 74900, 37450, 50200, 74900, 37450],
                [41000, None, None, None, None, None]]
    exp1 = 74900 * 1.02
    exp2 = 37450 * 1.02
    exp3 = 50200 * 1.02
    exp4 = 74900 * 1.02
    exp5 = 37450 * 1.02
    exp = [[36000, 72250, 36500, 48600, 72500, 36250],
           [38000, 74000, 36900, 49400, 73800, 36900],
           [40000, 74900, 37450, 50200, 74900, 37450],
           [41000, exp1, exp2, exp3, exp4, exp5]]
    exp = np.array(exp).astype('i4', casting='unsafe')
    res = Policy.expand_array(_II_brk2, inflate=True,
                              inflation_rates=[0.02] * 5,
                              num_years=4)
    npt.assert_array_equal(res, exp)

    syr = 2013
    pol = Policy(start_year=syr)
    irates = pol.inflation_rates()
    reform = {2016: {u'_II_brk2': _II_brk2}}
    pol.implement_reform(reform)
    pol.set_year(2019)
    # The 2019 policy should be the combination of the user-defined
    # value and CPI-inflated values from 2018
    exp_2019 = [41000.] + [(1.0 + irates[2018 - syr]) * i
                           for i in _II_brk2[2][1:]]
    exp_2019 = np.array(exp_2019)
    npt.assert_array_equal(pol.II_brk2, exp_2019)


def test_expand_2D_accept_None_additional_row():
    _II_brk2 = [[36000, 72250, 36500, 48600, 72500, 36250],
                [38000, 74000, 36900, 49400, 73800, 36900],
                [40000, 74900, 37450, 50200, 74900, 37450],
                [41000, None, None, None, None, None],
                [43000, None, None, None, None, None]]
    exp1 = 74900 * 1.02
    exp2 = 37450 * 1.02
    exp3 = 50200 * 1.02
    exp4 = 74900 * 1.02
    exp5 = 37450 * 1.02
    exp6 = exp1 * 1.03
    exp7 = exp2 * 1.03
    exp8 = exp3 * 1.03
    exp9 = exp4 * 1.03
    exp10 = exp5 * 1.03
    exp = [[36000, 72250, 36500, 48600, 72500, 36250],
           [38000, 74000, 36900, 49400, 73800, 36900],
           [40000, 74900, 37450, 50200, 74900, 37450],
           [41000, exp1, exp2, exp3, exp4, exp5],
           [43000, exp6, exp7, exp8, exp9, exp10]]
    inflation_rates = [0.015, 0.02, 0.02, 0.03]
    res = Policy.expand_array(_II_brk2, inflate=True,
                              inflation_rates=inflation_rates, num_years=5)
    npt.assert_array_equal(res, exp)

    user_mods = {2016: {u'_II_brk2': _II_brk2}}
    syr = 2013
    pol = Policy(start_year=syr)
    irates = pol.inflation_rates()
    pol.implement_reform(user_mods)
    pol.set_year(2020)
    irates = pol.inflation_rates()
    # The 2020 policy should be the combination of the user-defined
    # value and CPI-inflated values from 2018
    exp_2020 = [43000.] + [(1 + irates[2019 - syr]) *
                           (1 + irates[2018 - syr]) * i
                           for i in _II_brk2[2][1:]]
    exp_2020 = np.array(exp_2020)
    npt.assert_allclose(pol.II_brk2, exp_2020)


def test_mtr_graph_data(records_2009):
    calc = Calculator(policy=Policy(), records=records_2009)
    with pytest.raises(ValueError):
        gdata = mtr_graph_data(calc, calc, mars='bad',
                               income_measure='agi',
                               dollar_weighting=True)
    with pytest.raises(ValueError):
        gdata = mtr_graph_data(calc, calc, mars=0,
                               income_measure='expanded_income',
                               dollar_weighting=True)
    with pytest.raises(ValueError):
        gdata = mtr_graph_data(calc, calc, mars=list())
    with pytest.raises(ValueError):
        gdata = mtr_graph_data(calc, calc, mtr_measure='badtax')
    with pytest.raises(ValueError):
        gdata = mtr_graph_data(calc, calc, income_measure='badincome')
    with pytest.raises(ValueError):
        calcx = Calculator(policy=Policy(), records=records_2009)
        calcx.advance_to_year(2020)
        gdata = mtr_graph_data(calcx, calc)
    gdata = mtr_graph_data(calc, calc, mars=1,
                           mtr_wrt_full_compen=True,
                           income_measure='wages',
                           dollar_weighting=True)
    assert type(gdata) == dict


def test_atr_graph_data(records_2009):
    calc = Calculator(policy=Policy(), records=records_2009)
    with pytest.raises(ValueError):
        gdata = atr_graph_data(calc, calc, mars='bad')
    with pytest.raises(ValueError):
        gdata = atr_graph_data(calc, calc, mars=0)
    with pytest.raises(ValueError):
        gdata = atr_graph_data(calc, calc, mars=list())
    with pytest.raises(ValueError):
        gdata = atr_graph_data(calc, calc, atr_measure='badtax')
    with pytest.raises(ValueError):
        calcx = Calculator(policy=Policy(), records=records_2009)
        calcx.advance_to_year(2020)
        gdata = atr_graph_data(calcx, calc)
    gdata = atr_graph_data(calc, calc, mars=1, atr_measure='combined')
    gdata = atr_graph_data(calc, calc, atr_measure='itax')
    gdata = atr_graph_data(calc, calc, atr_measure='ptax')
    assert type(gdata) == dict


def test_xtr_graph_plot(records_2009):
    calc = Calculator(policy=Policy(),
                      records=records_2009,
                      behavior=Behavior())
    gdata = mtr_graph_data(calc, calc, mtr_measure='ptax',
                           income_measure='agi',
                           dollar_weighting=False)
    gplot = xtr_graph_plot(gdata)
    assert gplot
    gdata = mtr_graph_data(calc, calc, mtr_measure='itax',
                           alt_e00200p_text='Taxpayer Earnings',
                           income_measure='expanded_income',
                           dollar_weighting=False)
    assert type(gdata) == dict


def test_xtr_graph_plot_no_bokeh(records_2009):
    import taxcalc
    taxcalc.utils.BOKEH_AVAILABLE = False
    calc = Calculator(policy=Policy(),
                      records=records_2009,
                      behavior=Behavior())
    gdata = mtr_graph_data(calc, calc)
    with pytest.raises(RuntimeError):
        gplot = xtr_graph_plot(gdata)
    taxcalc.utils.BOKEH_AVAILABLE = True


def test_write_graph_file(records_2009):
    calc = Calculator(policy=Policy(), records=records_2009)
    gdata = mtr_graph_data(calc, calc, mtr_measure='ptax',
                           alt_e00200p_text='Taxpayer Earnings',
                           income_measure='agi',
                           dollar_weighting=False)
    gplot = xtr_graph_plot(gdata)
    assert gplot
    htmlfname = temporary_filename(suffix='.html')
    try:
        write_graph_file(gplot, htmlfname, 'title')
    except:  # pylint: disable=bare-except
        if os.path.isfile(htmlfname):
            try:
                os.remove(htmlfname)
            except OSError:
                pass  # sometimes we can't remove a generated temporary file
        assert 'write_graph_file()_ok' == 'no'
    # if try was successful, try to remove the file
    if os.path.isfile(htmlfname):
        try:
            os.remove(htmlfname)
        except OSError:
            pass  # sometimes we can't remove a generated temporary file


def test_multiyear_diagnostic_table(records_2009):
    behv = Behavior()
    calc = Calculator(policy=Policy(), records=records_2009, behavior=behv)
    with pytest.raises(ValueError):
        adt = multiyear_diagnostic_table(calc, 0)
    with pytest.raises(ValueError):
        adt = multiyear_diagnostic_table(calc, 20)
    adt = multiyear_diagnostic_table(calc, 3)
    assert isinstance(adt, DataFrame)
    behv.update_behavior({2013: {'_BE_sub': [0.3]}})
    assert calc.behavior.has_response()
    adt = multiyear_diagnostic_table(calc, 3)
    assert isinstance(adt, DataFrame)


def test_multiyear_diagnostic_table_wo_behv(records_2009):
    pol = Policy()
    reform = {
        2013: {
            '_II_rt7': [0.33],
            '_PT_rt7': [0.33],
        }}
    pol.implement_reform(reform)
    calc = Calculator(policy=pol, records=records_2009)
    calc.calc_all()
    liabilities_x = (calc.records._combined *
                     calc.records.s006).sum()
    adt = multiyear_diagnostic_table(calc, 1)
    # extract combined liabilities as a float and
    # adopt units of the raw calculator data in liabilities_x
    liabilities_y = adt.iloc[18].tolist()[0] * 1000000000
    npt.assert_almost_equal(liabilities_x, liabilities_y, 2)


def test_multiyear_diagnostic_table_w_behv(records_2009):
    pol = Policy()
    behv = Behavior()
    calc = Calculator(policy=pol, records=records_2009, behavior=behv)
    assert calc.current_year == 2013
    reform = {
        2013: {
            '_II_rt7': [0.33],
            '_PT_rt7': [0.33],
        }}
    pol.implement_reform(reform)
    reform_be = {2013: {'_BE_sub': [0.4],
                        '_BE_cg': [-3.67]}}
    behv.update_behavior(reform_be)
    calc_clp = calc.current_law_version()
    calc_behv = Behavior.response(calc_clp, calc)
    calc_behv.calc_all()
    liabilities_x = (calc_behv.records._combined *
                     calc_behv.records.s006).sum()
    adt = multiyear_diagnostic_table(calc_behv, 1)
    # extract combined liabilities as a float and
    # adopt units of the raw calculator data in liabilities_x
    liabilities_y = adt.iloc[18].tolist()[0] * 1000000000
    npt.assert_almost_equal(liabilities_x, liabilities_y, 2)


@pytest.yield_fixture
def csvfile():
    txt = ('A,B,C,D,EFGH\n'
           '1,2,3,4,0\n'
           '5,6,7,8,0\n'
           '9,10,11,12,0\n'
           '100,200,300,400,500\n'
           '123.45,678.912,000.000,87,92')
    f = tempfile.NamedTemporaryFile(mode='a', delete=False)
    f.write(txt + '\n')
    f.close()
    # Must close and then yield for Windows platform
    yield f
    os.remove(f.name)


@pytest.yield_fixture
def asciifile():
    x = (
        'A              \t1              \t100            \t123.45         \n'
        'B              \t2              \t200            \t678.912        \n'
        'C              \t3              \t300            \t000.000        \n'
        'D              \t4              \t400            \t87             \n'
        'EFGH           \t0              \t500            \t92             '
    )
    f = tempfile.NamedTemporaryFile(mode='a', delete=False)
    f.write(x + '\n')
    f.close()
    # Must close and then yield for Windows platform
    yield f
    os.remove(f.name)


def test_ascii_output_function(csvfile, asciifile):
    output_test = tempfile.NamedTemporaryFile(mode='a', delete=False)
    ascii_output(csv_filename=csvfile.name, ascii_filename=output_test.name)
    assert filecmp.cmp(output_test.name, asciifile.name)
    output_test.close()
    os.remove(output_test.name)


def test_json_read_write():
    test_file = tempfile.NamedTemporaryFile(mode='a', delete=False)
    test_dict = {1: 1, 'b': 'b', 3: '3'}
    write_json_to_file(test_dict, test_file.name)
    assert read_json_from_file(test_file.name) == {'1': 1, 'b': 'b', '3': '3'}
    test_file.close()
    os.remove(test_file.name)


def test_string_to_number():
    assert string_to_number(None) == 0
    assert string_to_number('') == 0
    assert string_to_number('1') == 1
    assert string_to_number('1.') == 1.
    assert string_to_number('1.23') == 1.23


def test_ce_aftertax_income(puf_1991, weights_1991):
    # test certainty_equivalent() function
    con = 10000
    cmin = 1000
    assert con == round(certainty_equivalent(con, 0, cmin), 6)
    assert con > round(certainty_equivalent((math.log(con) - 0.1), 1, cmin), 6)
    # test with require_no_agg_tax_change equal to False
    cyr = 2020
    crra = 1
    # specify calc1 and calc_all() for cyr
    pol1 = Policy()
    rec1 = Records(data=puf_1991, weights=weights_1991, start_year=2009)
    calc1 = Calculator(policy=pol1, records=rec1)
    calc1.advance_to_year(cyr)
    calc1.calc_all()
    # specify calc2 and calc_all() for cyr
    pol2 = Policy()
    reform = {2018: {'_II_em': [0.0]}}
    pol2.implement_reform(reform)
    rec2 = Records(data=puf_1991, weights=weights_1991, start_year=2009)
    calc2 = Calculator(policy=pol2, records=rec2)
    calc2.advance_to_year(cyr)
    calc2.calc_all()
    cedict = ce_aftertax_income(calc1, calc2, require_no_agg_tax_change=False)
    assert cedict['year'] == cyr
    # test with require_no_agg_tax_change equal to True
    with pytest.raises(ValueError):
        ce_aftertax_income(calc1, calc2, require_no_agg_tax_change=True)
    # test with require_no_agg_tax_change equal to False and custom_params
    params = {'crra_list': [0, 2], 'cmin_value': 2000}
    with pytest.raises(ValueError):
        ce_aftertax_income(calc1, calc2, require_no_agg_tax_change=True,
                           custom_params=params)


def test_read_egg_csv():
    with pytest.raises(ValueError):
        vdf = read_egg_csv('bad_filename')


def test_read_egg_json():
    with pytest.raises(ValueError):
        pdict = read_egg_json('bad_filename')


def test_create_and_delete_temporary_file():
    # test temporary_filename() and delete_file() functions
    fname = temporary_filename()
    with open(fname, 'w') as tmpfile:
        tmpfile.write('any content will do')
    assert os.path.isfile(fname) is True
    delete_file(fname)
    assert os.path.isfile(fname) is False
