"""
Tests of Tax-Calculator utility functions.
"""
# CODING-STYLE CHECKS:
# pep8 --ignore=E402 test_utils.py
# pylint --disable=locally-disabled test_utils.py
#
# pylint: disable=missing-docstring,no-member,protected-access

import os
import math
import filecmp
import tempfile
import numpy as np
from numpy.testing import assert_equal, assert_almost_equal, assert_array_equal
import pandas as pd
from pandas.util.testing import assert_series_equal
import pytest
# pylint: disable=import-error
from taxcalc import Policy, Records, Behavior, Calculator, ParametersBase
from taxcalc.utils import (TABLE_COLUMNS, TABLE_LABELS, STATS_COLUMNS,
                           create_distribution_table,
                           create_difference_table,
                           count_lt_zero, weighted_count_lt_zero,
                           count_gt_zero, weighted_count_gt_zero,
                           weighted_count, weighted_sum, weighted_mean,
                           wage_weighted, agi_weighted,
                           expanded_income_weighted,
                           weighted_perc_inc, weighted_perc_dec,
                           add_income_bins, add_weighted_income_bins,
                           multiyear_diagnostic_table,
                           mtr_graph_data, atr_graph_data,
                           xtr_graph_plot, write_graph_file,
                           temporary_filename, ascii_output, delete_file,
                           write_json_to_file, read_json_from_file,
                           read_egg_csv, read_egg_json,
                           certainty_equivalent, ce_aftertax_income)


DATA = [[1.0, 2, 'a'],
        [-1.0, 4, 'a'],
        [3.0, 6, 'a'],
        [2.0, 4, 'b'],
        [3.0, 6, 'b']]

WEIGHT_DATA = [[1.0, 2.0, 10.0],
               [2.0, 4.0, 20.0],
               [3.0, 6.0, 30.0]]

DATA_FLOAT = [[1.0, 2, 'a'],
              [-1.0, 4, 'a'],
              [0.0000000001, 3, 'a'],
              [-0.0000000001, 1, 'a'],
              [3.0, 6, 'a'],
              [2.0, 4, 'b'],
              [0.0000000001, 3, 'b'],
              [-0.0000000001, 1, 'b'],
              [3.0, 6, 'b']]


def test_expand_1d_short_array():
    ary = np.array([4, 5, 9], dtype='i4')
    exp2 = np.array([9.0 * math.pow(1.02, i) for i in range(1, 8)])
    exp1 = np.array([4, 5, 9])
    exp = np.zeros(10)
    exp[:3] = exp1
    exp[3:] = exp2
    res = ParametersBase._expand_1D(ary, inflate=True,
                                    inflation_rates=[0.02] * 10, num_years=10)
    assert np.allclose(exp, res, atol=0.0, rtol=1.0E-7)


def test_expand_1d_variable_rates():
    irates = [0.02, 0.02, 0.03, 0.035]
    ary = np.array([4, 5, 9], dtype='f4')
    res = ParametersBase._expand_1D(ary, inflate=True,
                                    inflation_rates=irates, num_years=5)
    exp = np.array([4, 5, 9, 9 * 1.03, 9 * 1.03 * 1.035])
    assert np.allclose(exp.astype('f4', casting='unsafe'), res)


def test_expand_1d_scalar():
    val = 10.0
    exp = np.array([val * math.pow(1.02, i) for i in range(0, 10)])
    res = ParametersBase._expand_1D(val, inflate=True,
                                    inflation_rates=[0.02] * 10, num_years=10)
    assert np.allclose(exp, res)


def test_expand_1d_accept_none():
    lst = [4., 5., None]
    irates = [0.02, 0.02, 0.03, 0.035]
    exp = []
    cur = 5.0 * 1.02
    exp = [4., 5., cur]
    cur *= 1.03
    exp.append(cur)
    cur *= 1.035
    exp.append(cur)
    exp = np.array(exp)
    res = ParametersBase._expand_array(lst, inflate=True,
                                       inflation_rates=irates, num_years=5)
    assert np.allclose(exp.astype('f4', casting='unsafe'), res)


def test_expand_2d_short_array():
    ary = np.array([[1, 2, 3]], dtype=np.float64)
    val = np.array([1, 2, 3], dtype=np.float64)
    exp2 = np.array([val * math.pow(1.02, i) for i in range(1, 5)])
    exp1 = np.array([1, 2, 3], dtype=np.float64)
    exp = np.zeros((5, 3))
    exp[:1] = exp1
    exp[1:] = exp2
    res = ParametersBase._expand_2D(ary, inflate=True,
                                    inflation_rates=[0.02] * 5, num_years=5)
    assert np.allclose(exp, res)


def test_expand_2d_variable_rates():
    ary = np.array([[1, 2, 3]], dtype=np.float64)
    cur = np.array([1, 2, 3], dtype=np.float64)
    irates = [0.02, 0.02, 0.02, 0.03, 0.035]
    exp2 = []
    for i in range(0, 4):
        idx = i + len(ary) - 1
        cur = np.array(cur * (1.0 + irates[idx]))
        print('cur is ', cur)
        exp2.append(cur)
    exp1 = np.array([1, 2, 3], dtype=np.float64)
    exp = np.zeros((5, 3), dtype=np.float64)
    exp[:1] = exp1
    exp[1:] = exp2
    res = ParametersBase._expand_2D(ary, inflate=True,
                                    inflation_rates=irates, num_years=5)
    assert np.allclose(exp, res)


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
    assert isinstance(dt1, pd.DataFrame)
    dt2 = create_difference_table(calc1.records, calc2.records,
                                  groupby='webapp_income_bins')
    assert isinstance(dt2, pd.DataFrame)
    with pytest.raises(ValueError):
        create_difference_table(calc1.records, calc2.records,
                                groupby='bad_bins')
    with pytest.raises(ValueError):
        create_distribution_table(calc2.records,
                                  groupby='small_income_bins',
                                  result_type='bad_result_type')
    with pytest.raises(ValueError):
        create_distribution_table(calc2.records,
                                  groupby='bad_bins',
                                  result_type='weighted_sum')
    dt3 = create_distribution_table(calc2.records,
                                    groupby='small_income_bins',
                                    result_type='weighted_sum',
                                    baseline_obj=calc1.records, diffs=True)
    assert isinstance(dt3, pd.DataFrame)
    calc1.increment_year()
    with pytest.raises(ValueError):
        create_difference_table(calc1.records, calc2.records,
                                groupby='large_income_bins')
    with pytest.raises(ValueError):
        create_distribution_table(calc2.records,
                                  groupby='small_income_bins',
                                  result_type='weighted_sum',
                                  baseline_obj=calc1.records, diffs=True)


def test_weighted_count_lt_zero():
    assert count_lt_zero([0.0, 1, -1, 0, -2.2, 1.1]) == 2
    df1 = pd.DataFrame(data=DATA, columns=['tax_diff', 's006', 'label'])
    grped = df1.groupby('label')
    diffs = grped.apply(weighted_count_lt_zero, 'tax_diff')
    exp = pd.Series(data=[4, 0], index=['a', 'b'])
    exp.index.name = 'label'
    assert_series_equal(exp, diffs)
    df2 = pd.DataFrame(data=DATA_FLOAT, columns=['tax_diff', 's006', 'label'])
    grped = df2.groupby('label')
    diffs = grped.apply(weighted_count_lt_zero, 'tax_diff')
    exp = pd.Series(data=[4, 0], index=['a', 'b'])
    exp.index.name = 'label'
    assert_series_equal(exp, diffs)


def test_weighted_count_gt_zero():
    assert count_gt_zero([0.0, 1, -1, 0, -2.2, 1.1]) == 2
    df1 = pd.DataFrame(data=DATA, columns=['tax_diff', 's006', 'label'])
    grped = df1.groupby('label')
    diffs = grped.apply(weighted_count_gt_zero, 'tax_diff')
    exp = pd.Series(data=[8, 10], index=['a', 'b'])
    exp.index.name = 'label'
    assert_series_equal(exp, diffs)
    df2 = pd.DataFrame(data=DATA, columns=['tax_diff', 's006', 'label'])
    grped = df2.groupby('label')
    diffs = grped.apply(weighted_count_gt_zero, 'tax_diff')
    exp = pd.Series(data=[8, 10], index=['a', 'b'])
    exp.index.name = 'label'
    assert_series_equal(exp, diffs)


def test_weighted_count():
    dfx = pd.DataFrame(data=DATA, columns=['tax_diff', 's006', 'label'])
    grouped = dfx.groupby('label')
    diffs = grouped.apply(weighted_count)
    exp = pd.Series(data=[12, 10], index=['a', 'b'])
    exp.index.name = 'label'
    assert_series_equal(exp, diffs)


def test_weighted_mean():
    dfx = pd.DataFrame(data=DATA, columns=['tax_diff', 's006', 'label'])
    grouped = dfx.groupby('label')
    diffs = grouped.apply(weighted_mean, 'tax_diff')
    exp = pd.Series(data=[16.0 / 12.0, 26.0 / 10.0], index=['a', 'b'])
    exp.index.name = 'label'
    assert_series_equal(exp, diffs)


def test_wage_weighted():
    dfx = pd.DataFrame(data=WEIGHT_DATA, columns=['var', 's006', 'e00200'])
    wvar = wage_weighted(dfx, 'var')
    assert round(wvar, 4) == 2.5714


def test_agi_weighted():
    dfx = pd.DataFrame(data=WEIGHT_DATA, columns=['var', 's006', 'c00100'])
    wvar = agi_weighted(dfx, 'var')
    assert round(wvar, 4) == 2.5714


def test_expanded_income_weighted():
    dfx = pd.DataFrame(data=WEIGHT_DATA,
                       columns=['var', 's006', 'expanded_income'])
    wvar = expanded_income_weighted(dfx, 'var')
    assert round(wvar, 4) == 2.5714


def test_weighted_sum():
    dfx = pd.DataFrame(data=DATA, columns=['tax_diff', 's006', 'label'])
    grouped = dfx.groupby('label')
    diffs = grouped.apply(weighted_sum, 'tax_diff')
    exp = pd.Series(data=[16.0, 26.0], index=['a', 'b'])
    exp.index.name = 'label'
    assert_series_equal(exp, diffs)


def test_weighted_perc_inc():
    dfx = pd.DataFrame(data=DATA, columns=['tax_diff', 's006', 'label'])
    grouped = dfx.groupby('label')
    diffs = grouped.apply(weighted_perc_inc, 'tax_diff')
    exp = pd.Series(data=[8. / 12., 1.0], index=['a', 'b'])
    exp.index.name = 'label'
    assert_series_equal(exp, diffs)


def test_weighted_perc_dec():
    dfx = pd.DataFrame(data=DATA, columns=['tax_diff', 's006', 'label'])
    grouped = dfx.groupby('label')
    diffs = grouped.apply(weighted_perc_dec, 'tax_diff')
    exp = pd.Series(data=[4. / 12., 0.0], index=['a', 'b'])
    exp.index.name = 'label'
    assert_series_equal(exp, diffs)


EPSILON = 1e-5


def test_add_income_bins():
    dta = np.arange(1, 1e6, 5000)
    dfx = pd.DataFrame(data=dta, columns=['expanded_income'])
    bins = [-1e99, 0, 9999, 19999, 29999, 39999, 49999, 74999, 99999,
            200000, 1e99]
    dfr = add_income_bins(dfx, compare_with='tpc', bins=None)
    groupedr = dfr.groupby('bins')
    idx = 1
    for name, _ in groupedr:
        assert name.closed == 'right'
        assert abs(name.right - bins[idx]) < EPSILON
        idx += 1
    dfl = add_income_bins(dfx, compare_with='tpc', bins=None, right=False)
    groupedl = dfl.groupby('bins')
    idx = 1
    for name, _ in groupedl:
        assert name.closed == 'left'
        assert abs(name.right - bins[idx]) < EPSILON
        idx += 1


def test_add_income_bins_soi():
    dta = np.arange(1, 1e6, 5000)
    dfx = pd.DataFrame(data=dta, columns=['expanded_income'])
    bins = [-1e99, 0, 4999, 9999, 14999, 19999, 24999, 29999, 39999,
            49999, 74999, 99999, 199999, 499999, 999999, 1499999,
            1999999, 4999999, 9999999, 1e99]
    dfr = add_income_bins(dfx, compare_with='soi', bins=None)
    groupedr = dfr.groupby('bins')
    idx = 1
    for name, _ in groupedr:
        assert name.closed == 'right'
        assert abs(name.right - bins[idx]) < EPSILON
        idx += 1
    dfl = add_income_bins(dfx, compare_with='soi', bins=None, right=False)
    groupedl = dfl.groupby('bins')
    idx = 1
    for name, _ in groupedl:
        assert name.closed == 'left'
        assert abs(name.right - bins[idx]) < EPSILON
        idx += 1


def test_add_exp_income_bins():
    dta = np.arange(1, 1e6, 5000)
    dfx = pd.DataFrame(data=dta, columns=['expanded_income'])
    bins = [-1e99, 0, 4999, 9999, 14999, 19999, 29999, 32999, 43999, 1e99]
    dfr = add_income_bins(dfx, bins=bins)
    groupedr = dfr.groupby('bins')
    idx = 1
    for name, _ in groupedr:
        assert name.closed == 'right'
        assert abs(name.right - bins[idx]) < EPSILON
        idx += 1
    dfl = add_income_bins(dfx, bins=bins, right=False)
    groupedl = dfl.groupby('bins')
    idx = 1
    for name, _ in groupedl:
        assert name.closed == 'left'
        assert abs(name.right - bins[idx]) < EPSILON
        idx += 1


def test_add_income_bins_raises():
    dta = np.arange(1, 1e6, 5000)
    dfx = pd.DataFrame(data=dta, columns=['expanded_income'])
    with pytest.raises(ValueError):
        dfx = add_income_bins(dfx, compare_with='stuff')


def test_add_weighted_income_bins():
    dfx = pd.DataFrame(data=DATA, columns=['expanded_income', 's006', 'label'])
    dfb = add_weighted_income_bins(dfx, num_bins=100)
    bin_labels = dfb['bins'].unique()
    default_labels = set(range(1, 101))
    for lab in bin_labels:
        assert lab in default_labels
    # custom labels
    dfb = add_weighted_income_bins(dfx, weight_by_income_measure=True)
    assert 'bins' in dfb
    custom_labels = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j']
    dfb = add_weighted_income_bins(dfx, labels=custom_labels)
    assert 'bins' in dfb
    bin_labels = dfb['bins'].unique()
    for lab in bin_labels:
        assert lab in custom_labels


def test_dist_table_sum_row(records_2009):
    # Create a default Policy object
    policy1 = Policy()
    # Create a Calculator
    calc1 = Calculator(policy=policy1, records=records_2009)
    calc1.calc_all()
    tb1 = create_distribution_table(calc1.records,
                                    groupby='small_income_bins',
                                    result_type='weighted_sum')
    tb2 = create_distribution_table(calc1.records,
                                    groupby='large_income_bins',
                                    result_type='weighted_sum')
    assert np.allclose(tb1[-1:], tb2[-1:])
    tb3 = create_distribution_table(calc1.records,
                                    groupby='small_income_bins',
                                    result_type='weighted_avg')
    assert isinstance(tb3, pd.DataFrame)


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
    non_digit_cols = ['mean', 'perc_inc', 'perc_cut', 'share_of_change',
                      'aftertax_perc']
    digit_cols = [x for x in tdiff1.columns.tolist() if
                  x not in non_digit_cols]
    assert np.allclose(tdiff1[digit_cols][-1:], tdiff2[digit_cols][-1:])
    assert_array_equal(tdiff1[non_digit_cols][-1:],
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
    assert_array_equal(calc1_s006, calc2_s006)


def test_expand_2d_already_filled():
    # pylint doesn't like caps in var name, so  pylint: disable=invalid-name
    _II_brk2 = [[36000, 72250, 36500, 48600, 72500, 36250],
                [38000, 74000, 36900, 49400, 73800, 36900],
                [40000, 74900, 37450, 50200, 74900, 37450]]
    res = ParametersBase._expand_2D(_II_brk2, inflate=True,
                                    inflation_rates=[0.02] * 5, num_years=3)
    assert_equal(res, np.array(_II_brk2))


def test_expand_2d_partial_expand():
    # pylint doesn't like caps in var name, so  pylint: disable=invalid-name
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
    res = ParametersBase._expand_2D(_II_brk2, inflate=True,
                                    inflation_rates=inf_rates, num_years=4)
    assert_equal(res, exp)


def test_strip_nones():
    lst = [None, None]
    assert Policy._strip_nones(lst) == []
    lst = [1, 2, None]
    assert Policy._strip_nones(lst) == [1, 2]
    lst = [[1, 2, 3], [4, None, None]]
    assert Policy._strip_nones(lst) == [[1, 2, 3], [4, -1, -1]]


def test_expand_2d_accept_none():
    # pylint doesn't like caps in var name, so  pylint: disable=invalid-name
    _II_brk2 = [[36000, 72250, 36500, 48600, 72500],
                [38000, 74000, 36900, 49400, 73800],
                [40000, 74900, 37450, 50200, 74900],
                [41000, None, None, None, None]]
    exp1 = 74900 * 1.02
    exp2 = 37450 * 1.02
    exp3 = 50200 * 1.02
    exp4 = 74900 * 1.02
    exp = [[36000, 72250, 36500, 48600, 72500],
           [38000, 74000, 36900, 49400, 73800],
           [40000, 74900, 37450, 50200, 74900],
           [41000, exp1, exp2, exp3, exp4]]
    exp = np.array(exp).astype('i4', casting='unsafe')
    res = ParametersBase._expand_array(_II_brk2, inflate=True,
                                       inflation_rates=[0.02] * 5, num_years=4)
    assert_equal(res, exp)

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
    assert_equal(pol.II_brk2, exp_2019)


def test_expand_2d_accept_none_add_row():
    # pylint doesn't like caps in var name, so  pylint: disable=invalid-name
    _II_brk2 = [[36000, 72250, 36500, 48600, 72500],
                [38000, 74000, 36900, 49400, 73800],
                [40000, 74900, 37450, 50200, 74900],
                [41000, None, None, None, None],
                [43000, None, None, None, None]]
    exx = [0.0]
    exx.append(74900 * 1.02)  # exx[1]
    exx.append(37450 * 1.02)  # exx[2]
    exx.append(50200 * 1.02)  # exx[3]
    exx.append(74900 * 1.02)  # exx[4]
    exx.append(0.0)
    exx.append(exx[1] * 1.03)  # exx[6]
    exx.append(exx[2] * 1.03)  # exx[7]
    exx.append(exx[3] * 1.03)  # exx[8]
    exx.append(exx[4] * 1.03)  # exx[9]
    exp = [[36000, 72250, 36500, 48600, 72500],
           [38000, 74000, 36900, 49400, 73800],
           [40000, 74900, 37450, 50200, 74900],
           [41000, exx[1], exx[2], exx[3], exx[4]],
           [43000, exx[6], exx[7], exx[8], exx[9]]]
    inflation_rates = [0.015, 0.02, 0.02, 0.03]
    res = ParametersBase._expand_array(_II_brk2, inflate=True,
                                       inflation_rates=inflation_rates,
                                       num_years=5)
    assert_equal(res, exp)
    user_mods = {2016: {'_II_brk2': _II_brk2}}
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
    assert np.allclose(pol.II_brk2, exp_2020)


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
        gdata = mtr_graph_data(calc, calc, mars='ALL', mtr_variable='e00200s')
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
    assert isinstance(gdata, dict)


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
    assert isinstance(gdata, dict)


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
    assert isinstance(gdata, dict)


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
    assert isinstance(adt, pd.DataFrame)
    behv.update_behavior({2013: {'_BE_sub': [0.3]}})
    assert calc.behavior.has_response()
    adt = multiyear_diagnostic_table(calc, 3)
    assert isinstance(adt, pd.DataFrame)


def test_myr_diag_table_wo_behv(records_2009):
    pol = Policy()
    reform = {
        2013: {
            '_II_rt7': [0.33],
            '_PT_rt7': [0.33],
        }}
    pol.implement_reform(reform)
    calc = Calculator(policy=pol, records=records_2009)
    calc.calc_all()
    liabilities_x = (calc.records.combined *
                     calc.records.s006).sum()
    adt = multiyear_diagnostic_table(calc, 1)
    # extract combined liabilities as a float and
    # adopt units of the raw calculator data in liabilities_x
    liabilities_y = adt.iloc[19].tolist()[0] * 1000000000
    assert_almost_equal(liabilities_x, liabilities_y, 2)


def test_myr_diag_table_w_behv(records_2009):
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
    liabilities_x = (calc_behv.records.combined *
                     calc_behv.records.s006).sum()
    adt = multiyear_diagnostic_table(calc_behv, 1)
    # extract combined liabilities as a float and
    # adopt units of the raw calculator data in liabilities_x
    liabilities_y = adt.iloc[19].tolist()[0] * 1000000000
    assert_almost_equal(liabilities_x, liabilities_y, 2)


@pytest.yield_fixture
def csvfile():
    txt = ('A,B,C,D,EFGH\n'
           '1,2,3,4,0\n'
           '5,6,7,8,0\n'
           '9,10,11,12,0\n'
           '100,200,300,400,500\n'
           '123.45,678.912,000.000,87,92')
    csvf = tempfile.NamedTemporaryFile(mode='a', delete=False)
    csvf.write(txt + '\n')
    csvf.close()
    # Must close and then yield for Windows platform
    yield csvf
    os.remove(csvf.name)


@pytest.yield_fixture
def asciifile():
    txt = (
        'A              \t1              \t100            \t123.45         \n'
        'B              \t2              \t200            \t678.912        \n'
        'C              \t3              \t300            \t000.000        \n'
        'D              \t4              \t400            \t87             \n'
        'EFGH           \t0              \t500            \t92             '
    )
    ascf = tempfile.NamedTemporaryFile(mode='a', delete=False)
    ascf.write(txt + '\n')
    ascf.close()
    # Must close and then yield for Windows platform
    yield ascf
    os.remove(ascf.name)


def test_ascii_output(csvfile,  # pylint: disable=redefined-outer-name
                      asciifile):  # pylint: disable=redefined-outer-name
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


def test_ce_aftertax_income(puf_1991, weights_1991):
    # test certainty_equivalent() function
    con = 10000
    cmin = 1000
    assert con == round(certainty_equivalent(con, 0, cmin), 6)
    assert con > round(certainty_equivalent((math.log(con) - 0.1), 1, cmin), 6)
    # test with require_no_agg_tax_change equal to False
    cyr = 2020
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
        read_egg_csv('bad_filename')


def test_read_egg_json():
    with pytest.raises(ValueError):
        read_egg_json('bad_filename')


def test_create_delete_temp_file():
    # test temporary_filename() and delete_file() functions
    fname = temporary_filename()
    with open(fname, 'w') as tmpfile:
        tmpfile.write('any content will do')
    assert os.path.isfile(fname) is True
    delete_file(fname)
    assert os.path.isfile(fname) is False
