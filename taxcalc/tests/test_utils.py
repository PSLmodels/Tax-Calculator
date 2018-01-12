"""
Tests of Tax-Calculator utility functions.
"""
# CODING-STYLE CHECKS:
# pep8 --ignore=E402 test_utils.py
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
                           create_distribution_table, create_difference_table,
                           weighted_count_lt_zero, weighted_count_gt_zero,
                           weighted_count, weighted_sum, weighted_mean,
                           wage_weighted, agi_weighted,
                           expanded_income_weighted,
                           weighted_perc_inc, weighted_perc_cut,
                           add_income_bins, add_quantile_bins,
                           mtr_graph_data, atr_graph_data,
                           xtr_graph_plot, write_graph_file,
                           read_egg_csv, read_egg_json, delete_file,
                           bootstrap_se_ci,
                           certainty_equivalent,
                           ce_aftertax_expanded_income,
                           nonsmall_diffs)


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
    assert set(DIST_VARIABLES).issubset(Records.CALCULATED_VARS | {'s006'})


def test_create_tables(cps_subsample):
    # pylint: disable=too-many-statements
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

    # test creating various difference tables

    diff = create_difference_table(calc1.dataframe(DIFF_VARIABLES),
                                   calc2.dataframe(DIFF_VARIABLES),
                                   groupby='large_income_bins',
                                   income_measure='expanded_income',
                                   tax_to_diff='combined')
    assert isinstance(diff, pd.DataFrame)
    expected = [0.00,
                0.01,
                0.41,
                0.76,
                0.85,
                1.06,
                1.14,
                1.04,
                0.76,
                0.19,
                0.70]
    assert np.allclose(diff['perc_aftertax'].values, expected,
                       atol=0.005, rtol=0.0, equal_nan=True)

    diff = create_difference_table(calc1.dataframe(DIFF_VARIABLES),
                                   calc2.dataframe(DIFF_VARIABLES),
                                   groupby='webapp_income_bins',
                                   income_measure='expanded_income',
                                   tax_to_diff='iitax')
    assert isinstance(diff, pd.DataFrame)
    expected = [0.00,
                0.01,
                0.41,
                0.76,
                0.85,
                1.06,
                1.14,
                1.04,
                0.76,
                0.26,
                0.08,
                0.06,
                0.70]
    assert np.allclose(diff['perc_aftertax'].values, expected,
                       atol=0.005, rtol=0.0, equal_nan=True)

    diff = create_difference_table(calc1.dataframe(DIFF_VARIABLES),
                                   calc2.dataframe(DIFF_VARIABLES),
                                   groupby='small_income_bins',
                                   income_measure='expanded_income',
                                   tax_to_diff='iitax')
    assert isinstance(diff, pd.DataFrame)
    expected = [0.00,
                0.01,
                0.02,
                0.15,
                0.58,
                0.73,
                0.78,
                0.85,
                1.06,
                1.14,
                1.04,
                0.76,
                0.26,
                0.08,
                0.08,
                0.07,
                0.04,
                0.02,
                np.nan,
                0.70]
    assert np.allclose(diff['perc_aftertax'].values, expected,
                       atol=0.005, rtol=0.0, equal_nan=True)

    diff = create_difference_table(calc1.dataframe(DIFF_VARIABLES),
                                   calc2.dataframe(DIFF_VARIABLES),
                                   groupby='weighted_deciles',
                                   income_measure='expanded_income',
                                   tax_to_diff='combined')
    assert isinstance(diff, pd.DataFrame)
    expected = [14931,
                276555,
                7728872,
                22552703,
                34008512,
                50233787,
                76811377,
                111167087,
                123226970,
                111414038,
                537434832,
                66560891,
                39571078,
                5282069]
    assert np.allclose(diff['tot_change'].values, expected,
                       atol=0.5, rtol=0.0)
    expected = [0.00,
                0.05,
                1.44,
                4.20,
                6.33,
                9.35,
                14.29,
                20.68,
                22.93,
                20.73,
                100.00,
                12.38,
                7.36,
                0.98]
    assert np.allclose(diff['share_of_change'].values, expected,
                       atol=0.005, rtol=0.0)
    expected = [0.01,
                0.02,
                0.33,
                0.70,
                0.81,
                0.91,
                1.07,
                1.18,
                0.91,
                0.37,
                0.70,
                0.69,
                0.34,
                0.06]
    assert np.allclose(diff['perc_aftertax'].values, expected,
                       atol=0.005, rtol=0.0, equal_nan=True)
    expected = [-0.01,
                -0.02,
                -0.33,
                -0.70,
                -0.81,
                -0.91,
                -1.07,
                -1.18,
                -0.91,
                -0.37,
                -0.70,
                -0.69,
                -0.34,
                -0.06]
    assert np.allclose(diff['pc_aftertaxinc'].values, expected,
                       atol=0.005, rtol=0.0, equal_nan=True)

    # test creating various distribution tables

    dist = create_distribution_table(calc2.dataframe(DIST_VARIABLES),
                                     groupby='weighted_deciles',
                                     income_measure='expanded_income',
                                     result_type='weighted_sum')
    assert isinstance(dist, pd.DataFrame)

    expected = [-8851215,
                -99666120,
                -123316561,
                -85895787,
                -47357458,
                207462144,
                443391189,
                978487989,
                1709504845,
                7631268907,
                10605027933,
                1655597977,
                2537684742,
                3437986189]
    assert np.allclose(dist['iitax'].values, expected,
                       atol=0.5, rtol=0.0)
    expected = [1202,
                1688,
                13506,
                18019,
                30130,
                48244,
                80994,
                112788,
                131260,
                146001,
                583832,
                70258,
                59834,
                15909]
    assert np.allclose(dist['num_returns_ItemDed'].tolist(), expected,
                       atol=0.5, rtol=0.0)
    expected = [158456013,
                1351981790,
                2383726863,
                3408544081,
                4569232020,
                6321944661,
                8520304098,
                11817197884,
                17299173380,
                41117720202,
                96948280992,
                12723790026,
                15769741079,
                12624189098]
    assert np.allclose(dist['expanded_income'].tolist(), expected,
                       atol=0.5, rtol=0.0)
    expected = [147367698,
                1354827269,
                2351611947,
                3192405234,
                4157431713,
                5454468907,
                7125788590,
                9335613303,
                13417244946,
                29691084873,
                76227844481,
                9546216325,
                11603328920,
                8541539628]
    assert np.allclose(dist['aftertax_income'].tolist(), expected,
                       atol=0.5, rtol=0.0)

    dist = create_distribution_table(calc2.dataframe(DIST_VARIABLES),
                                     groupby='webapp_income_bins',
                                     income_measure='expanded_income',
                                     result_type='weighted_sum')
    assert isinstance(dist, pd.DataFrame)
    expected = [-103274,
                -83144506,
                -152523834,
                -129881470,
                85802556,
                255480678,
                832529135,
                1066963515,
                3023956558,
                2876331264,
                1008672459,
                1820944852,
                10605027933]
    assert np.allclose(dist['iitax'], expected,
                       atol=0.5, rtol=0.0)
    expected = [0,
                1202,
                22654,
                31665,
                30547,
                49851,
                124786,
                97349,
                160147,
                56806,
                5803,
                3023,
                583832]
    assert np.allclose(dist['num_returns_ItemDed'].tolist(), expected,
                       atol=0.5, rtol=0.0)


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

    WEBAPP BINS:
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

    WEBAPP bin 10 ($500-1000 thousand) has weighted count of 1179 thousand;
                  weighted count of units with tax increase is 32 thousand.

    So, the mean weight for all units in WEBAPP bin 10 is 111.5421 and the
    unweighted number with a tax increase is 287 assuming all units in that
    bin have the same weight.  (Note that 287 * 111.5421 is about 32,012.58,
    which rounds to the 32 thousand shown in the TaxBrain difference table.)

    WEBAPP bin 11 ($1000+ thousand) has weighted count of 636 thousand;
              weighted count of units with tax increase is 27 thousand.

    So, the mean weight for all units in WEBAPP bin 11 is about 27.517 and the
    unweighted number with a tax increase is 981 assuming all units in that
    bin have the same weight.  (Note that 981 * 27.517 is about 26,994.18,
    which rounds to the 27 thousand shown in the TaxBrain difference table.)
    """
    dump = False  # setting to True implies results printed and test fails
    seed = 123456789
    bs_samples = 1000
    alpha = 0.025  # implies 95% confidence interval
    # compute stderr and confidence interval for WEBAPP bin 10 increase count
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
            res.format('WEBAPP-BIN10: ',
                       data_estimate, bs_samples, alpha, stderr, cilo, cihi)
        )
    assert abs((stderr / 1.90) - 1) < 0.0008
    # NOTE: a se of 1.90 thousand implies that when comparing the difference
    #       in the weighted number of filing units in WEBAPP bin 10 with a
    #       tax increase, the difference statistic has a bigger se (because
    #       the variance of the difference is the sum of the variances of the
    #       two point estimates).  So, in WEBAPP bin 10 if the point estimates
    #       both had se = 1.90, then the difference in the point estimates has
    #       has a se = 2.687.  This means that the difference would have to be
    #       over 5 thousand in order for there to be high confidence that the
    #       difference was different from zero in a statistically significant
    #       manner.
    #       Or put a different way, a difference of 1 thousand cannot be
    #       accurately detected while a difference of 10 thousand can be
    #       accurately detected.
    assert abs((cilo / 28.33) - 1) < 0.0012
    assert abs((cihi / 35.81) - 1) < 0.0012
    # compute stderr and confidence interval for WEBAPP bin 11 increase count
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
            res.format('WEBAPP-BIN11: ',
                       data_estimate, bs_samples, alpha, stderr, cilo, cihi)
        )
    assert abs((stderr / 0.85) - 1) < 0.0040
    # NOTE: a se of 0.85 thousand implies that when comparing the difference
    #       in the weighted number of filing units in WEBAPP bin 11 with a
    #       tax increase, the difference statistic has a bigger se (because
    #       the variance of the difference is the sum of the variances of the
    #       two point estimates).  So, in WEBAPP bin 11 if the point estimates
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


def test_weighted_perc_inc():
    dfx = pd.DataFrame(data=DATA, columns=['tax_diff', 's006', 'label'])
    grouped = dfx.groupby('label')
    diffs = grouped.apply(weighted_perc_inc, 'tax_diff')
    exp = pd.Series(data=[8. / 12., 1.0], index=['a', 'b'])
    exp.index.name = 'label'
    pd.util.testing.assert_series_equal(exp, diffs)


def test_weighted_perc_cut():
    dfx = pd.DataFrame(data=DATA, columns=['tax_diff', 's006', 'label'])
    grouped = dfx.groupby('label')
    diffs = grouped.apply(weighted_perc_cut, 'tax_diff')
    exp = pd.Series(data=[4. / 12., 0.0], index=['a', 'b'])
    exp.index.name = 'label'
    pd.util.testing.assert_series_equal(exp, diffs)


EPSILON = 1e-5


def test_add_income_bins():
    dta = np.arange(1, 1e6, 5000)
    dfx = pd.DataFrame(data=dta, columns=['expanded_income'])
    bins = [-9e99, 0, 9999, 19999, 29999, 39999, 49999, 74999, 99999,
            200000, 9e99]
    dfr = add_income_bins(dfx, 'expanded_income', bin_type='tpc', bins=None,
                          right=True)
    groupedr = dfr.groupby('bins')
    idx = 1
    for name, _ in groupedr:
        assert name.closed == 'right'
        assert abs(name.right - bins[idx]) < EPSILON
        idx += 1
    dfl = add_income_bins(dfx, 'expanded_income', bin_type='tpc', bins=None,
                          right=False)
    groupedl = dfl.groupby('bins')
    idx = 1
    for name, _ in groupedl:
        assert name.closed == 'left'
        assert abs(name.right - bins[idx]) < EPSILON
        idx += 1


def test_add_income_bins_soi():
    dta = np.arange(1, 1e6, 5000)
    dfx = pd.DataFrame(data=dta, columns=['expanded_income'])
    bins = [-9e99, 0, 4999, 9999, 14999, 19999, 24999, 29999, 39999,
            49999, 74999, 99999, 199999, 499999, 999999, 1499999,
            1999999, 4999999, 9999999, 9e99]
    dfr = add_income_bins(dfx, 'expanded_income', bin_type='soi', right=True)
    groupedr = dfr.groupby('bins')
    idx = 1
    for name, _ in groupedr:
        assert name.closed == 'right'
        assert abs(name.right - bins[idx]) < EPSILON
        idx += 1
    dfl = add_income_bins(dfx, 'expanded_income', bin_type='soi', right=False)
    groupedl = dfl.groupby('bins')
    idx = 1
    for name, _ in groupedl:
        assert name.closed == 'left'
        assert abs(name.right - bins[idx]) < EPSILON
        idx += 1


def test_add_exp_income_bins():
    dta = np.arange(1, 1e6, 5000)
    dfx = pd.DataFrame(data=dta, columns=['expanded_income'])
    bins = [-9e99, 0, 4999, 9999, 14999, 19999, 29999, 32999, 43999, 9e99]
    dfr = add_income_bins(dfx, 'expanded_income', bins=bins, right=True)
    groupedr = dfr.groupby('bins')
    idx = 1
    for name, _ in groupedr:
        assert name.closed == 'right'
        assert abs(name.right - bins[idx]) < EPSILON
        idx += 1
    dfl = add_income_bins(dfx, 'expanded_income', bins=bins, right=False)
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
        dfx = add_income_bins(dfx, 'expanded_income', bin_type='stuff')


def test_add_quantile_bins():
    dfx = pd.DataFrame(data=DATA, columns=['expanded_income', 's006', 'label'])
    dfb = add_quantile_bins(dfx, 'expanded_income', 100,
                            weight_by_income_measure=False)
    bin_labels = dfb['bins'].unique()
    default_labels = set(range(1, 101))
    for lab in bin_labels:
        assert lab in default_labels
    # custom labels
    dfb = add_quantile_bins(dfx, 'expanded_income', 100,
                            weight_by_income_measure=True)
    assert 'bins' in dfb
    custom_labels = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j']
    dfb = add_quantile_bins(dfx, 'expanded_income', 10,
                            labels=custom_labels)
    assert 'bins' in dfb
    bin_labels = dfb['bins'].unique()
    for lab in bin_labels:
        assert lab in custom_labels


def test_dist_table_sum_row(cps_subsample):
    rec = Records.cps_constructor(data=cps_subsample)
    calc = Calculator(policy=Policy(), records=rec)
    calc.calc_all()
    tb1 = create_distribution_table(calc.dataframe(DIST_VARIABLES),
                                    groupby='small_income_bins',
                                    income_measure='expanded_income',
                                    result_type='weighted_sum')
    tb2 = create_distribution_table(calc.dataframe(DIST_VARIABLES),
                                    groupby='large_income_bins',
                                    income_measure='expanded_income',
                                    result_type='weighted_sum')
    assert np.allclose(tb1[-1:], tb2[-1:])
    tb3 = create_distribution_table(calc.dataframe(DIST_VARIABLES),
                                    groupby='small_income_bins',
                                    income_measure='expanded_income',
                                    result_type='weighted_avg')
    assert isinstance(tb3, pd.DataFrame)


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
                                     groupby='small_income_bins',
                                     income_measure='expanded_income',
                                     tax_to_diff='iitax')
    tdiff2 = create_difference_table(calc1.dataframe(DIFF_VARIABLES),
                                     calc2.dataframe(DIFF_VARIABLES),
                                     groupby='large_income_bins',
                                     income_measure='expanded_income',
                                     tax_to_diff='iitax')
    non_digit_cols = ['perc_inc', 'perc_cut']
    digit_cols = [c for c in list(tdiff1) if c not in non_digit_cols]
    assert np.allclose(tdiff1[digit_cols][-1:],
                       tdiff2[digit_cols][-1:])
    np.testing.assert_array_equal(tdiff1[non_digit_cols][-1:],
                                  tdiff2[non_digit_cols][-1:])


def test_mtr_graph_data(cps_subsample):
    calc = Calculator(policy=Policy(),
                      records=Records.cps_constructor(data=cps_subsample))
    year = calc.current_year,
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
    calc = Calculator(policy=Policy(),
                      records=Records.cps_constructor(data=cps_subsample),
                      behavior=Behavior())
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
    calc = Calculator(policy=Policy(),
                      records=Records.cps_constructor(data=cps_subsample))
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


def test_dec_graph_plot(cps_subsample):
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


def test_nonsmall_diffs():
    assert nonsmall_diffs(['AAA'], ['AAA', 'BBB'])
    assert nonsmall_diffs(['AaA'], ['AAA'])
    assert not nonsmall_diffs(['AAA'], ['AAA'])
    assert nonsmall_diffs(['12.3'], ['12.2'])
    assert not nonsmall_diffs(['12.3 AAA'], ['12.2 AAA'], small=0.1)
    assert nonsmall_diffs(['12.3'], ['AAA'])
