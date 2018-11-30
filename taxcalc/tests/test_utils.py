"""
Tests of Tax-Calculator utility functions.
"""
# CODING-STYLE CHECKS:
# pycodestyle test_utils.py
# pylint --disable=locally-disabled test_utils.py
#
# pylint: disable=missing-docstring,no-member,protected-access,too-many-lines

import os
import math
import random
import numpy as np
import pandas as pd
import pytest
# pylint: disable=import-error
from taxcalc import Policy, Records, Behavior, Calculator
from taxcalc.utils import (DIST_VARIABLES,
                           DIST_TABLE_COLUMNS, DIST_TABLE_LABELS,
                           DIFF_VARIABLES,
                           DIFF_TABLE_COLUMNS, DIFF_TABLE_LABELS,
                           SOI_AGI_BINS,
                           create_distribution_table, create_difference_table,
                           weighted_count_lt_zero, weighted_count_gt_zero,
                           weighted_count, weighted_sum, weighted_mean,
                           wage_weighted, agi_weighted,
                           expanded_income_weighted,
                           add_income_table_row_variable,
                           add_quantile_table_row_variable,
                           mtr_graph_data, atr_graph_data, dec_graph_data,
                           xtr_graph_plot, write_graph_file,
                           read_egg_csv, read_egg_json, delete_file,
                           bootstrap_se_ci,
                           certainty_equivalent,
                           ce_aftertax_expanded_income,
                           nonsmall_diffs,
                           quantity_response)


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


def test_validity_of_name_lists():
    assert len(DIST_TABLE_COLUMNS) == len(DIST_TABLE_LABELS)
    Records.read_var_info()
    assert set(DIST_VARIABLES).issubset(Records.CALCULATED_VARS | {'s006'})
    extra_vars_set = set(['num_returns_StandardDed',
                          'num_returns_ItemDed',
                          'num_returns_AMT'])
    assert (set(DIST_TABLE_COLUMNS) - set(DIST_VARIABLES)) == extra_vars_set


def test_create_tables(cps_subsample):
    # pylint: disable=too-many-statements,too-many-branches
    # create a current-law Policy object and Calculator object calc1
    rec = Records.cps_constructor(data=cps_subsample)
    pol = Policy()
    calc1 = Calculator(policy=pol, records=rec)
    calc1.calc_all()
    # create a policy-reform Policy object and Calculator object calc2
    reform = {2013: {'_II_rt1': [0.15]}}
    pol.implement_reform(reform)
    calc2 = Calculator(policy=pol, records=rec)
    calc2.calc_all()

    test_failure = False

    # test creating various difference tables

    diff = create_difference_table(calc1.dataframe(DIFF_VARIABLES),
                                   calc2.dataframe(DIFF_VARIABLES),
                                   'standard_income_bins', 'combined')
    assert isinstance(diff, pd.DataFrame)
    tabcol = 'pc_aftertaxinc'
    expected = [np.nan,
                np.nan,
                -0.2,
                -0.8,
                -0.8,
                -0.5,
                -0.8,
                -0.7,
                -0.7,
                -0.7,
                -0.3,
                -0.1,
                -0.1,
                -0.6]
    if not np.allclose(diff[tabcol].values, expected,
                       atol=0.1, rtol=0.0, equal_nan=True):
        test_failure = True
        print('diff xbin', tabcol)
        for val in diff[tabcol].values:
            print('{:.1f},'.format(val))

    diff = create_difference_table(calc1.dataframe(DIFF_VARIABLES),
                                   calc2.dataframe(DIFF_VARIABLES),
                                   'weighted_deciles', 'combined')
    assert isinstance(diff, pd.DataFrame)
    tabcol = 'tot_change'
    expected = [0.0,
                0.0,
                0.3,
                2.5,
                2.8,
                2.5,
                4.4,
                5.2,
                6.3,
                8.1,
                10.6,
                10.3,
                53.0,
                6.2,
                3.5,
                0.6]
    if not np.allclose(diff[tabcol].values, expected,
                       atol=0.1, rtol=0.0):
        test_failure = True
        print('diff xdec', tabcol)
        for val in diff[tabcol].values:
            print('{:.1f},'.format(val))

    tabcol = 'share_of_change'
    expected = [0.0,
                0.0,
                0.5,
                4.8,
                5.3,
                4.8,
                8.3,
                9.9,
                11.8,
                15.2,
                19.9,
                19.4,
                100.0,
                11.7,
                6.6,
                1.1]
    if not np.allclose(diff[tabcol].values, expected,
                       atol=0.1, rtol=0.0):
        test_failure = True
        print('diff xdec', tabcol)
        for val in diff[tabcol].values:
            print('{:.1f},'.format(val))

    tabcol = 'pc_aftertaxinc'
    expected = [np.nan,
                np.nan,
                -0.3,
                -1.0,
                -0.7,
                -0.5,
                -0.7,
                -0.7,
                -0.7,
                -0.7,
                -0.7,
                -0.3,
                -0.6,
                -0.6,
                -0.3,
                -0.1]
    if not np.allclose(diff[tabcol].values, expected,
                       atol=0.1, rtol=0.0, equal_nan=True):
        test_failure = True
        print('diff xdec', tabcol)
        for val in diff[tabcol].values:
            print('{:.1f},'.format(val))

    # test creating various distribution tables

    dist, _ = calc2.distribution_tables(None, 'weighted_deciles')
    assert isinstance(dist, pd.DataFrame)
    tabcol = 'iitax'
    expected = [0.0,
                0.0,
                -1.8,
                2.0,
                5.0,
                6.7,
                18.0,
                26.1,
                35.2,
                82.7,
                148.8,
                734.1,
                1056.9,
                152.4,
                234.7,
                347.1]
    if not np.allclose(dist[tabcol].values, expected,
                       atol=0.1, rtol=0.0):
        test_failure = True
        print('dist xdec', tabcol)
        for val in dist[tabcol].values:
            print('{:.1f},'.format(val))

    tabcol = 'num_returns_ItemDed'
    expected = [0.0,
                0.0,
                0.4,
                1.5,
                2.5,
                2.6,
                4.5,
                5.3,
                6.3,
                7.7,
                11.0,
                13.1,
                54.9,
                6.2,
                5.5,
                1.4]
    if not np.allclose(dist[tabcol].tolist(), expected,
                       atol=0.1, rtol=0.0):
        test_failure = True
        print('dist xdec', tabcol)
        for val in dist[tabcol].values:
            print('{:.1f},'.format(val))

    tabcol = 'expanded_income'
    expected = [0.0,
                0.0,
                105.9,
                294.0,
                417.1,
                528.4,
                658.9,
                818.2,
                1037.8,
                1324.7,
                1788.1,
                4047.6,
                11020.7,
                1286.6,
                1511.9,
                1249.2]
    if not np.allclose(dist[tabcol].tolist(), expected,
                       atol=0.1, rtol=0.0):
        test_failure = True
        print('dist xdec', tabcol)
        for val in dist[tabcol].values:
            print('{:.1f},'.format(val))

    tabcol = 'aftertax_income'
    expected = [0.0,
                0.0,
                97.7,
                261.9,
                378.1,
                485.6,
                586.2,
                723.2,
                919.6,
                1130.7,
                1474.0,
                2994.5,
                9051.5,
                1002.5,
                1147.6,
                844.4]
    if not np.allclose(dist[tabcol].tolist(), expected,
                       atol=0.1, rtol=0.0):
        test_failure = True
        print('dist xdec', tabcol)
        for val in dist[tabcol].values:
            print('{:.1f},'.format(val))

    dist, _ = calc2.distribution_tables(None, 'standard_income_bins')
    assert isinstance(dist, pd.DataFrame)
    tabcol = 'iitax'
    expected = [0.0,
                0.0,
                -0.5,
                -0.1,
                3.4,
                9.3,
                18.5,
                54.6,
                89.3,
                298.0,
                290.2,
                99.5,
                194.9,
                1056.9]
    if not np.allclose(dist[tabcol], expected,
                       atol=0.1, rtol=0.0):
        test_failure = True
        print('dist xbin', tabcol)
        for val in dist[tabcol].values:
            print('{:.1f},'.format(val))

    tabcol = 'num_returns_ItemDed'
    expected = [0.0,
                0.0,
                0.1,
                1.1,
                2.4,
                3.5,
                4.8,
                10.1,
                8.8,
                17.0,
                6.2,
                0.5,
                0.3,
                54.9]
    if not np.allclose(dist[tabcol].tolist(), expected,
                       atol=0.1, rtol=0.0):
        test_failure = True
        print('dist xbin', tabcol)
        for val in dist[tabcol].values:
            print('{:.1f},'.format(val))

    if test_failure:
        assert 1 == 2


def test_diff_count_precision():
    """
    Estimate bootstrap standard error and confidence interval for count
    statistics ('tax_cut' and 'tax_inc') in difference table generated
    using puf.csv input data taking no account of tbi privacy fuzzing and
    assuming all filing units in each bin have the same weight.  These
    assumptions imply that the estimates produced here are likely to
    over-estimate the precision of the count statistics.

    Background information on unweighted number of filing units by bin:

    DECILE BINS:
    0   16268
    1   14897
    2   13620
    3   15760
    4   16426
    5   18070
    6   18348
    7   19352
    8   21051
    9   61733 <--- largest unweighted bin count
    A  215525

    STANDARD BINS:
    0    7081 <--- negative income bin is dropped in TaxBrain display
    1   19355
    2   22722
    3   20098
    4   17088
    5   14515
    6   24760
    7   15875
    8   25225
    9   15123
    10  10570 <--- smallest unweighted bin count
    11  23113 <--- second largest unweighted WEBAPP bin count
    A  215525

    Background information on Trump2017.json reform used in TaxBrain run 16649:

    STANDARD bin 10 ($500-1000 thousand) has weighted count of 1179 thousand;
                    weighted count of units with tax increase is 32 thousand.

    So, the mean weight for all units in STANDARD bin 10 is 111.5421 and the
    unweighted number with a tax increase is 287 assuming all units in that
    bin have the same weight.  (Note that 287 * 111.5421 is about 32,012.58,
    which rounds to the 32 thousand shown in the TaxBrain difference table.)

    STANDARD bin 11 ($1000+ thousand) has weighted count of 636 thousand;
                    weighted count of units with tax increase is 27 thousand.

    So, the mean weight for all units in STANDARD bin 11 is about 27.517 and
    the unweighted number with a tax increase is 981 assuming all units in
    that bin have the same weight.  (Note that 981 * 27.517 is about 26,994.18,
    which rounds to the 27 thousand shown in the TaxBrain difference table.)
    """
    dump = False  # setting to True implies results printed and test fails
    seed = 123456789
    bs_samples = 1000
    alpha = 0.025  # implies 95% confidence interval
    # compute stderr and confidence interval for STANDARD bin 10 increase count
    data_list = [111.5421] * 287 + [0.0] * (10570 - 287)
    assert len(data_list) == 10570
    data = np.array(data_list)
    assert (data > 0).sum() == 287
    data_estimate = np.sum(data) * 1e-3
    assert abs((data_estimate / 32) - 1) < 0.0005
    bsd = bootstrap_se_ci(data, seed, bs_samples, np.sum, alpha)
    stderr = bsd['se'] * 1e-3
    cilo = bsd['cilo'] * 1e-3
    cihi = bsd['cihi'] * 1e-3
    if dump:
        res = '{}EST={:.1f} B={} alpha={:.3f} se={:.2f} ci=[ {:.2f} , {:.2f} ]'
        print(
            res.format('STANDARD-BIN10: ',
                       data_estimate, bs_samples, alpha, stderr, cilo, cihi)
        )
    assert abs((stderr / 1.90) - 1) < 0.0008
    # NOTE: a se of 1.90 thousand implies that when comparing the difference
    #       in the weighted number of filing units in STANDARD bin 10 with a
    #       tax increase, the difference statistic has a bigger se (because
    #       the variance of the difference is the sum of the variances of the
    #       two point estimates).  So, in STANDARD bin 10 if the point
    #       estimates both had se = 1.90, then the difference in the point
    #       estimates has has a se = 2.687.  This means that the difference
    #       would have to be over 5 thousand in order for there to be high
    #       confidence that the difference was different from zero in a
    #       statistically significant manner.
    #       Or put a different way, a difference of 1 thousand cannot be
    #       accurately detected while a difference of 10 thousand can be
    #       accurately detected.
    assert abs((cilo / 28.33) - 1) < 0.0012
    assert abs((cihi / 35.81) - 1) < 0.0012
    # compute stderr and confidence interval for STANDARD bin 11 increase count
    data_list = [27.517] * 981 + [0.0] * (23113 - 981)
    assert len(data_list) == 23113
    data = np.array(data_list)
    assert (data > 0).sum() == 981
    data_estimate = np.sum(data) * 1e-3
    assert abs((data_estimate / 27) - 1) < 0.0005
    bsd = bootstrap_se_ci(data, seed, bs_samples, np.sum, alpha)
    stderr = bsd['se'] * 1e-3
    cilo = bsd['cilo'] * 1e-3
    cihi = bsd['cihi'] * 1e-3
    if dump:
        res = '{}EST={:.1f} B={} alpha={:.3f} se={:.2f} ci=[ {:.2f} , {:.2f} ]'
        print(
            res.format('STANDARD-BIN11: ',
                       data_estimate, bs_samples, alpha, stderr, cilo, cihi)
        )
    assert abs((stderr / 0.85) - 1) < 0.0040
    # NOTE: a se of 0.85 thousand implies that when comparing the difference
    #       in the weighted number of filing units in STANDARD bin 11 with a
    #       tax increase, the difference statistic has a bigger se (because
    #       the variance of the difference is the sum of the variances of the
    #       two point estimates).  So, in STANDARD bin 11 if point estimates
    #       both had se = 0.85, then the difference in the point estimates has
    #       has a se = 1.20.  This means that the difference would have to be
    #       over 2.5 thousand in order for there to be high confidence that the
    #       difference was different from zero in a statistically significant
    #       manner.
    #       Or put a different way, a difference of 1 thousand cannot be
    #       accurately detected while a difference of 10 thousand can be
    #       accurately detected.
    assert abs((cilo / 25.37) - 1) < 0.0012
    assert abs((cihi / 28.65) - 1) < 0.0012
    # fail if doing dump
    assert not dump


def test_weighted_count_lt_zero():
    df1 = pd.DataFrame(data=DATA, columns=['tax_diff', 's006', 'label'])
    grped = df1.groupby('label')
    diffs = grped.apply(weighted_count_lt_zero, 'tax_diff')
    exp = pd.Series(data=[4, 0], index=['a', 'b'])
    exp.index.name = 'label'
    pd.util.testing.assert_series_equal(exp, diffs)
    df2 = pd.DataFrame(data=DATA_FLOAT, columns=['tax_diff', 's006', 'label'])
    grped = df2.groupby('label')
    diffs = grped.apply(weighted_count_lt_zero, 'tax_diff')
    exp = pd.Series(data=[4, 0], index=['a', 'b'])
    exp.index.name = 'label'
    pd.util.testing.assert_series_equal(exp, diffs)


def test_weighted_count_gt_zero():
    df1 = pd.DataFrame(data=DATA, columns=['tax_diff', 's006', 'label'])
    grped = df1.groupby('label')
    diffs = grped.apply(weighted_count_gt_zero, 'tax_diff')
    exp = pd.Series(data=[8, 10], index=['a', 'b'])
    exp.index.name = 'label'
    pd.util.testing.assert_series_equal(exp, diffs)
    df2 = pd.DataFrame(data=DATA, columns=['tax_diff', 's006', 'label'])
    grped = df2.groupby('label')
    diffs = grped.apply(weighted_count_gt_zero, 'tax_diff')
    exp = pd.Series(data=[8, 10], index=['a', 'b'])
    exp.index.name = 'label'
    pd.util.testing.assert_series_equal(exp, diffs)


def test_weighted_count():
    dfx = pd.DataFrame(data=DATA, columns=['tax_diff', 's006', 'label'])
    grouped = dfx.groupby('label')
    diffs = grouped.apply(weighted_count)
    exp = pd.Series(data=[12, 10], index=['a', 'b'])
    exp.index.name = 'label'
    pd.util.testing.assert_series_equal(exp, diffs)


def test_weighted_mean():
    dfx = pd.DataFrame(data=DATA, columns=['tax_diff', 's006', 'label'])
    grouped = dfx.groupby('label')
    diffs = grouped.apply(weighted_mean, 'tax_diff')
    exp = pd.Series(data=[16.0 / 12.0, 26.0 / 10.0], index=['a', 'b'])
    exp.index.name = 'label'
    pd.util.testing.assert_series_equal(exp, diffs)


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
    pd.util.testing.assert_series_equal(exp, diffs)


EPSILON = 1e-5


def test_add_income_trow_var():
    dta = np.arange(1, 1e6, 5000)
    vdf = pd.DataFrame(data=dta, columns=['expanded_income'])
    vdf = add_income_table_row_variable(vdf, 'expanded_income', SOI_AGI_BINS)
    gdf = vdf.groupby('table_row')
    idx = 1
    for name, _ in gdf:
        assert name.closed == 'left'
        assert abs(name.right - SOI_AGI_BINS[idx]) < EPSILON
        idx += 1


def test_add_quantile_trow_var():
    dfx = pd.DataFrame(data=DATA, columns=['expanded_income', 's006', 'label'])
    dfb = add_quantile_table_row_variable(dfx, 'expanded_income',
                                          100, decile_details=False,
                                          weight_by_income_measure=False)
    bin_labels = dfb['table_row'].unique()
    default_labels = set(range(1, 101))
    for lab in bin_labels:
        assert lab in default_labels
    dfb = add_quantile_table_row_variable(dfx, 'expanded_income',
                                          100, decile_details=False)
    assert 'table_row' in dfb
    with pytest.raises(ValueError):
        dfb = add_quantile_table_row_variable(dfx, 'expanded_income',
                                              100, decile_details=True)


def test_dist_table_sum_row(cps_subsample):
    rec = Records.cps_constructor(data=cps_subsample)
    calc = Calculator(policy=Policy(), records=rec)
    calc.calc_all()
    tb1 = create_distribution_table(calc.distribution_table_dataframe(),
                                    'standard_income_bins', 'expanded_income')
    tb2 = create_distribution_table(calc.distribution_table_dataframe(),
                                    'soi_agi_bins', 'expanded_income')
    assert np.allclose(tb1[-1:], tb2[-1:])


def test_diff_table_sum_row(cps_subsample):
    rec = Records.cps_constructor(data=cps_subsample)
    # create a current-law Policy object and Calculator calc1
    pol = Policy()
    calc1 = Calculator(policy=pol, records=rec)
    calc1.calc_all()
    # create a policy-reform Policy object and Calculator calc2
    reform = {2013: {'_II_rt4': [0.56]}}
    pol.implement_reform(reform)
    calc2 = Calculator(policy=pol, records=rec)
    calc2.calc_all()
    # create two difference tables and compare their content
    tdiff1 = create_difference_table(calc1.dataframe(DIFF_VARIABLES),
                                     calc2.dataframe(DIFF_VARIABLES),
                                     'standard_income_bins', 'iitax')
    tdiff2 = create_difference_table(calc1.dataframe(DIFF_VARIABLES),
                                     calc2.dataframe(DIFF_VARIABLES),
                                     'soi_agi_bins', 'iitax')
    non_digit_cols = ['perc_inc', 'perc_cut']
    digit_cols = [c for c in list(tdiff1) if c not in non_digit_cols]
    assert np.allclose(tdiff1[digit_cols][-1:],
                       tdiff2[digit_cols][-1:])
    np.allclose(tdiff1[non_digit_cols][-1:],
                tdiff2[non_digit_cols][-1:])


def test_mtr_graph_data(cps_subsample):
    recs = Records.cps_constructor(data=cps_subsample)
    calc = Calculator(policy=Policy(), records=recs)
    year = calc.current_year
    with pytest.raises(ValueError):
        mtr_graph_data(None, year, mars='bad',
                       income_measure='agi',
                       dollar_weighting=True)
    with pytest.raises(ValueError):
        mtr_graph_data(None, year, mars=0,
                       income_measure='expanded_income',
                       dollar_weighting=True)
    with pytest.raises(ValueError):
        mtr_graph_data(None, year, mars=list())
    with pytest.raises(ValueError):
        mtr_graph_data(None, year, mars='ALL', mtr_variable='e00200s')
    with pytest.raises(ValueError):
        mtr_graph_data(None, year, mtr_measure='badtax')
    with pytest.raises(ValueError):
        mtr_graph_data(None, year, income_measure='badincome')
    mtr = 0.20 * np.ones_like(cps_subsample['e00200'])
    vdf = calc.dataframe(['s006', 'MARS', 'e00200'])
    vdf['mtr1'] = mtr
    vdf['mtr2'] = mtr
    vdf = vdf[vdf['MARS'] == 1]
    gdata = mtr_graph_data(vdf, year, mars=1,
                           mtr_wrt_full_compen=True,
                           income_measure='wages',
                           dollar_weighting=True)
    assert isinstance(gdata, dict)


def test_atr_graph_data(cps_subsample):
    pol = Policy()
    rec = Records.cps_constructor(data=cps_subsample)
    calc = Calculator(policy=pol, records=rec)
    year = calc.current_year
    with pytest.raises(ValueError):
        atr_graph_data(None, year, mars='bad')
    with pytest.raises(ValueError):
        atr_graph_data(None, year, mars=0)
    with pytest.raises(ValueError):
        atr_graph_data(None, year, mars=list())
    with pytest.raises(ValueError):
        atr_graph_data(None, year, atr_measure='badtax')
    calc.calc_all()
    vdf = calc.dataframe(['s006', 'MARS', 'expanded_income'])
    tax = 0.20 * np.ones_like(vdf['expanded_income'])
    vdf['tax1'] = tax
    vdf['tax2'] = tax
    gdata = atr_graph_data(vdf, year, mars=1, atr_measure='combined')
    gdata = atr_graph_data(vdf, year, atr_measure='itax')
    gdata = atr_graph_data(vdf, year, atr_measure='ptax')
    assert isinstance(gdata, dict)


def test_xtr_graph_plot(cps_subsample):
    recs = Records.cps_constructor(data=cps_subsample)
    calc = Calculator(policy=Policy(), records=recs, behavior=Behavior())
    mtr = 0.20 * np.ones_like(cps_subsample['e00200'])
    vdf = calc.dataframe(['s006', 'MARS', 'c00100'])
    vdf['mtr1'] = mtr
    vdf['mtr2'] = mtr
    gdata = mtr_graph_data(vdf, calc.current_year, mtr_measure='ptax',
                           income_measure='agi',
                           dollar_weighting=False)
    gplot = xtr_graph_plot(gdata)
    assert gplot
    vdf = calc.dataframe(['s006', 'expanded_income'])
    vdf['mtr1'] = mtr
    vdf['mtr2'] = mtr
    gdata = mtr_graph_data(vdf, calc.current_year, mtr_measure='itax',
                           alt_e00200p_text='Taxpayer Earnings',
                           income_measure='expanded_income',
                           dollar_weighting=False)
    assert isinstance(gdata, dict)


def temporary_filename(suffix=''):
    # Return string containing the temporary filename.
    return 'tmp{}{}'.format(random.randint(10000000, 99999999), suffix)


def test_write_graph_file(cps_subsample):
    recs = Records.cps_constructor(data=cps_subsample)
    calc = Calculator(policy=Policy(), records=recs)
    mtr = 0.20 * np.ones_like(cps_subsample['e00200'])
    vdf = calc.dataframe(['s006', 'e00200', 'c00100'])
    vdf['mtr1'] = mtr
    vdf['mtr2'] = mtr
    gdata = mtr_graph_data(vdf, calc.current_year, mtr_measure='ptax',
                           alt_e00200p_text='Taxpayer Earnings',
                           income_measure='agi',
                           dollar_weighting=False)
    gplot = xtr_graph_plot(gdata)
    assert gplot
    htmlfname = temporary_filename(suffix='.html')
    try:
        write_graph_file(gplot, htmlfname, 'title')
    except Exception:  # pylint: disable=broad-except
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


def test_ce_aftertax_income(cps_subsample):
    # test certainty_equivalent() function with con>cmin
    con = 5000
    cmin = 1000
    assert con == round(certainty_equivalent(con, 0, cmin), 6)
    assert con > round(certainty_equivalent((math.log(con) - 0.1), 1, cmin), 6)
    # test certainty_equivalent() function with con<cmin
    con = 500
    cmin = 1000
    assert con == round(certainty_equivalent(con, 0, cmin), 6)
    # test with require_no_agg_tax_change equal to False
    rec = Records.cps_constructor(data=cps_subsample)
    cyr = 2020
    # specify calc1 and calc_all() for cyr
    pol = Policy()
    calc1 = Calculator(policy=pol, records=rec)
    calc1.advance_to_year(cyr)
    calc1.calc_all()
    # specify calc2 and calc_all() for cyr
    reform = {2019: {'_II_em': [1000]}}
    pol.implement_reform(reform)
    calc2 = Calculator(policy=pol, records=rec)
    calc2.advance_to_year(cyr)
    calc2.calc_all()
    df1 = calc1.dataframe(['s006', 'combined', 'expanded_income'])
    df2 = calc2.dataframe(['s006', 'combined', 'expanded_income'])
    cedict = ce_aftertax_expanded_income(df1, df2,
                                         require_no_agg_tax_change=False)
    assert isinstance(cedict, dict)
    np.allclose(cedict['ceeu1'], [55641, 27167, 5726, 2229, 1565],
                atol=0.5, rtol=0.0)
    np.allclose(cedict['ceeu2'], [54629, 26698, 5710, 2229, 1565],
                atol=0.5, rtol=0.0)
    # test with require_no_agg_tax_change equal to True
    with pytest.raises(ValueError):
        ce_aftertax_expanded_income(df1, df2, require_no_agg_tax_change=True)
    # test with require_no_agg_tax_change equal to False and custom_params
    params = {'crra_list': [0, 2], 'cmin_value': 2000}
    with pytest.raises(ValueError):
        ce_aftertax_expanded_income(df1, df2, require_no_agg_tax_change=True,
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


def test_bootstrap_se_ci():
    # Use treated mouse data from Table 2.1 and
    # results from Table 2.2 and Table 13.1 in
    # Bradley Efron and Robert Tibshirani,
    # "An Introduction to the Bootstrap"
    # (Chapman & Hall, 1993).
    data = np.array([94, 197, 16, 38, 99, 141, 23], dtype=np.float64)
    assert abs(np.mean(data) - 86.86) < 0.005  # this is just rounding error
    bsd = bootstrap_se_ci(data, 123456789, 1000, np.mean, alpha=0.025)
    # following comparisons are less precise because of r.n. stream differences
    assert abs(bsd['se'] / 23.02 - 1) < 0.02
    assert abs(bsd['cilo'] / 45.9 - 1) < 0.02
    assert abs(bsd['cihi'] / 135.4 - 1) < 0.03


def test_table_columns_labels():
    # check that length of two lists are the same
    assert len(DIST_TABLE_COLUMNS) == len(DIST_TABLE_LABELS)
    assert len(DIFF_TABLE_COLUMNS) == len(DIFF_TABLE_LABELS)


def test_dec_graph_plots(cps_subsample):
    pol = Policy()
    rec = Records.cps_constructor(data=cps_subsample)
    calc1 = Calculator(policy=pol, records=rec)
    year = 2020
    calc1.advance_to_year(year)
    reform = {
        year: {
            '_SS_Earnings_c': [9e99],  # OASDI FICA tax on all earnings
            '_FICA_ss_trt': [0.107484]  # lower rate to keep revenue unchanged

        }
    }
    pol.implement_reform(reform)
    calc2 = Calculator(policy=pol, records=rec)
    calc2.advance_to_year(year)
    assert calc1.current_year == calc2.current_year
    calc1.calc_all()
    calc2.calc_all()
    fig = calc1.decile_graph(calc2)
    assert fig
    dt1, dt2 = calc1.distribution_tables(calc2, 'weighted_deciles')
    dta = dec_graph_data(dt1, dt2, year,
                         include_zero_incomes=True,
                         include_negative_incomes=False)
    assert isinstance(dta, dict)
    dta = dec_graph_data(dt1, dt2, year,
                         include_zero_incomes=False,
                         include_negative_incomes=True)
    assert isinstance(dta, dict)
    dta = dec_graph_data(dt1, dt2, year,
                         include_zero_incomes=False,
                         include_negative_incomes=False)
    assert isinstance(dta, dict)


def test_nonsmall_diffs():
    assert nonsmall_diffs(['AAA'], ['AAA', 'BBB'])
    assert nonsmall_diffs(['AaA'], ['AAA'])
    assert not nonsmall_diffs(['AAA'], ['AAA'])
    assert nonsmall_diffs(['12.3'], ['12.2'])
    assert not nonsmall_diffs(['12.3 AAA'], ['12.2 AAA'], small=0.1)
    assert nonsmall_diffs(['12.3'], ['AAA'])


def test_quantity_response():
    quantity = np.array([1.0] * 10)
    res = quantity_response(quantity,
                            price_elasticity=0,
                            aftertax_price1=None,
                            aftertax_price2=None,
                            income_elasticity=0,
                            aftertax_income1=None,
                            aftertax_income2=None)
    assert np.allclose(res, np.zeros(quantity.shape))
    one = np.ones(quantity.shape)
    res = quantity_response(quantity,
                            price_elasticity=-0.2,
                            aftertax_price1=one,
                            aftertax_price2=one,
                            income_elasticity=0.1,
                            aftertax_income1=one,
                            aftertax_income2=(one + one))
    assert not np.allclose(res, np.zeros(quantity.shape))
