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
import random
import numpy as np
import pandas as pd
import pytest
# pylint: disable=import-error
from taxcalc import Policy, Records, Behavior, Calculator
from taxcalc.utils import (STATS_COLUMNS,
                           DIST_TABLE_COLUMNS, DIST_TABLE_LABELS,
                           create_distribution_table, create_difference_table,
                           weighted_count_lt_zero, weighted_count_gt_zero,
                           weighted_count, weighted_sum, weighted_mean,
                           wage_weighted, agi_weighted,
                           expanded_income_weighted,
                           weighted_perc_inc, weighted_perc_cut,
                           add_income_bins, add_quantile_bins,
                           multiyear_diagnostic_table,
                           mtr_graph_data, atr_graph_data,
                           xtr_graph_plot, write_graph_file,
                           read_egg_csv, read_egg_json, delete_file,
                           bootstrap_se_ci,
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


def test_validity_of_name_lists():
    assert len(DIST_TABLE_COLUMNS) == len(DIST_TABLE_LABELS)
    assert set(STATS_COLUMNS).issubset(Records.CALCULATED_VARS | {'s006'})


def test_create_tables(cps_subsample):
    # create a current-law Policy object and Calculator object calc1
    policy1 = Policy()
    records1 = Records.cps_constructor(data=cps_subsample)
    calc1 = Calculator(policy=policy1, records=records1)
    calc1.calc_all()
    # create a policy-reform Policy object and Calculator object calc2
    reform = {2013: {'_II_rt1': [0.15]}}
    policy2 = Policy()
    policy2.implement_reform(reform)
    records2 = Records.cps_constructor(data=cps_subsample)
    calc2 = Calculator(policy=policy2, records=records2)
    calc2.calc_all()

    # test creating various difference tables
    diff = create_difference_table(calc1.records, calc2.records,
                                   groupby='large_income_bins',
                                   income_measure='expanded_income',
                                   tax_to_diff='combined')
    assert isinstance(diff, pd.DataFrame)
    expected = ['0.00%',
                '0.01%',
                '0.41%',
                '0.84%',
                '0.92%',
                '1.10%',
                '1.15%',
                '1.04%',
                '0.78%',
                '0.27%',
                'n/a']
    assert np.array_equal(diff['perc_aftertax'], expected)

    diff = create_difference_table(calc1.records, calc2.records,
                                   groupby='webapp_income_bins',
                                   income_measure='expanded_income',
                                   tax_to_diff='iitax')
    assert isinstance(diff, pd.DataFrame)
    expected = ['0.00%',
                '0.01%',
                '0.41%',
                '0.84%',
                '0.92%',
                '1.10%',
                '1.15%',
                '1.04%',
                '0.78%',
                '0.30%',
                '0.08%',
                '0.07%',
                'n/a']
    assert np.array_equal(diff['perc_aftertax'], expected)

    diff = create_difference_table(calc1.records, calc2.records,
                                   groupby='small_income_bins',
                                   income_measure='expanded_income',
                                   tax_to_diff='iitax')
    assert isinstance(diff, pd.DataFrame)
    expected = ['0.00%',
                '0.01%',
                '0.02%',
                '0.16%',
                '0.64%',
                '0.82%',
                '0.87%',
                '0.92%',
                '1.10%',
                '1.15%',
                '1.04%',
                '0.78%',
                '0.30%',
                '0.08%',
                '0.09%',
                '0.07%',
                '0.05%',
                '0.02%',
                '0.00%',
                'n/a']
    assert np.array_equal(diff['perc_aftertax'], expected)

    diff = create_difference_table(calc1.records, calc2.records,
                                   groupby='weighted_deciles',
                                   income_measure='expanded_income',
                                   tax_to_diff='combined')
    assert isinstance(diff, pd.DataFrame)
    expected = ['0.00%',
                '0.02%',
                '0.35%',
                '0.79%',
                '0.89%',
                '0.97%',
                '1.11%',
                '1.18%',
                '0.91%',
                '0.50%',
                'n/a']
    assert np.array_equal(diff['perc_aftertax'], expected)

    with pytest.raises(ValueError):
        create_difference_table(calc1.records, calc2.records,
                                groupby='bad_bins',
                                income_measure='expanded_income',
                                tax_to_diff='iitax')

    # test creating various distribution tables
    dist = create_distribution_table(calc2.records,
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
                10605027933]
    assert np.allclose(dist['iitax'], expected,
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
                583832]
    assert np.allclose(dist['num_returns_ItemDed'].tolist(), expected,
                       atol=0.5, rtol=0.0)

    dist = create_distribution_table(calc2.records,
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

    setattr(calc2.records, 'expanded_income_baseline',
            getattr(calc2.records, 'expanded_income'))
    dist = create_distribution_table(calc2.records,
                                     groupby='webapp_income_bins',
                                     income_measure='expanded_income_baseline',
                                     result_type='weighted_sum')
    assert isinstance(dist, pd.DataFrame)

    with pytest.raises(ValueError):
        create_distribution_table(calc2.records,
                                  groupby='small_income_bins',
                                  income_measure='expanded_income',
                                  result_type='bad_result_type')

    with pytest.raises(ValueError):
        create_distribution_table(calc2.records,
                                  groupby='bad_bins',
                                  income_measure='expanded_income',
                                  result_type='weighted_sum')


def test_diff_count_precision():
    """
    Estimate bootstrap standard error and confidence interval for count
    statistics ('tax_cut' and 'tax_inc') in difference table generated
    using puf.csv input data taking no account of dropq fuzzing and
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
    recs = Records.cps_constructor(data=cps_subsample)
    calc = Calculator(policy=Policy(), records=recs)
    calc.calc_all()
    tb1 = create_distribution_table(calc.records,
                                    groupby='small_income_bins',
                                    income_measure='expanded_income',
                                    result_type='weighted_sum')
    tb2 = create_distribution_table(calc.records,
                                    groupby='large_income_bins',
                                    income_measure='expanded_income',
                                    result_type='weighted_sum')
    assert np.allclose(tb1[-1:], tb2[-1:])
    tb3 = create_distribution_table(calc.records,
                                    groupby='small_income_bins',
                                    income_measure='expanded_income',
                                    result_type='weighted_avg')
    assert isinstance(tb3, pd.DataFrame)


def test_diff_table_sum_row(cps_subsample):
    # create a current-law Policy object and Calculator calc1
    policy1 = Policy()
    records1 = Records.cps_constructor(data=cps_subsample)
    calc1 = Calculator(policy=policy1, records=records1)
    calc1.calc_all()
    # create a policy-reform Policy object and Calculator calc2
    reform = {2013: {'_II_rt4': [0.56]}}
    policy2 = Policy()
    policy2.implement_reform(reform)
    records2 = Records.cps_constructor(data=cps_subsample)
    calc2 = Calculator(policy=policy2, records=records2)
    calc2.calc_all()
    # create two difference tables and compare their content
    tdiff1 = create_difference_table(calc1.records, calc2.records,
                                     groupby='small_income_bins',
                                     income_measure='expanded_income',
                                     tax_to_diff='iitax')
    tdiff2 = create_difference_table(calc1.records, calc2.records,
                                     groupby='large_income_bins',
                                     income_measure='expanded_income',
                                     tax_to_diff='iitax')
    non_digit_cols = ['mean', 'perc_inc', 'perc_cut', 'share_of_change',
                      'perc_aftertax']
    digit_cols = [c for c in list(tdiff1) if c not in non_digit_cols]
    assert np.allclose(tdiff1[digit_cols][-1:],
                       tdiff2[digit_cols][-1:])
    np.testing.assert_array_equal(tdiff1[non_digit_cols][-1:],
                                  tdiff2[non_digit_cols][-1:])


def test_mtr_graph_data(cps_subsample):
    calc = Calculator(policy=Policy(),
                      records=Records.cps_constructor(data=cps_subsample))
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
    gdata = mtr_graph_data(calc, calc, mars=1,
                           mtr_wrt_full_compen=True,
                           income_measure='wages',
                           dollar_weighting=True)
    assert isinstance(gdata, dict)


def test_atr_graph_data(cps_subsample):
    calc = Calculator(policy=Policy(),
                      records=Records.cps_constructor(data=cps_subsample))
    with pytest.raises(ValueError):
        gdata = atr_graph_data(calc, calc, mars='bad')
    with pytest.raises(ValueError):
        gdata = atr_graph_data(calc, calc, mars=0)
    with pytest.raises(ValueError):
        gdata = atr_graph_data(calc, calc, mars=list())
    with pytest.raises(ValueError):
        gdata = atr_graph_data(calc, calc, atr_measure='badtax')
    gdata = atr_graph_data(calc, calc, mars=1, atr_measure='combined')
    gdata = atr_graph_data(calc, calc, atr_measure='itax')
    gdata = atr_graph_data(calc, calc, atr_measure='ptax')
    assert isinstance(gdata, dict)
    with pytest.raises(ValueError):
        calcx = Calculator(policy=Policy(),
                           records=Records.cps_constructor(data=cps_subsample))
        calcx.advance_to_year(2020)
        gdata = atr_graph_data(calcx, calc)


def test_xtr_graph_plot(cps_subsample):
    calc = Calculator(policy=Policy(),
                      records=Records.cps_constructor(data=cps_subsample),
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


def temporary_filename(suffix=''):
    # Return string containing the temporary filename.
    return 'tmp{}{}'.format(random.randint(10000000, 99999999), suffix)


def test_write_graph_file(cps_subsample):
    calc = Calculator(policy=Policy(),
                      records=Records.cps_constructor(data=cps_subsample))
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


def test_multiyear_diagnostic_table(cps_subsample):
    behv = Behavior()
    calc = Calculator(policy=Policy(),
                      records=Records.cps_constructor(data=cps_subsample),
                      behavior=behv)
    with pytest.raises(ValueError):
        adt = multiyear_diagnostic_table(calc, 0)
    with pytest.raises(ValueError):
        adt = multiyear_diagnostic_table(calc, 20)
    adt = multiyear_diagnostic_table(calc, 3)
    assert isinstance(adt, pd.DataFrame)
    behv.update_behavior({2013: {'_BE_sub': [0.3]}})
    calc = Calculator(policy=Policy(),
                      records=Records.cps_constructor(data=cps_subsample),
                      behavior=behv)
    assert calc.behavior.has_response()
    adt = multiyear_diagnostic_table(calc, 3)
    assert isinstance(adt, pd.DataFrame)


def test_myr_diag_table_wo_behv(cps_subsample):
    pol = Policy()
    reform = {
        2013: {
            '_II_rt7': [0.33],
            '_PT_rt7': [0.33],
        }}
    pol.implement_reform(reform)
    calc = Calculator(policy=pol,
                      records=Records.cps_constructor(data=cps_subsample))
    calc.calc_all()
    liabilities_x = (calc.records.combined *
                     calc.records.s006).sum()
    adt = multiyear_diagnostic_table(calc, 1)
    # extract combined liabilities as a float and
    # adopt units of the raw calculator data in liabilities_x
    liabilities_y = adt.iloc[19].tolist()[0] * 1e9
    assert np.allclose(liabilities_x, liabilities_y, atol=0.01, rtol=0.0)


def test_myr_diag_table_w_behv(cps_subsample):
    pol = Policy()
    rec = Records.cps_constructor(data=cps_subsample)
    year = rec.current_year
    beh = Behavior()
    calc = Calculator(policy=pol, records=rec, behavior=beh)
    assert calc.current_year == year
    reform = {year: {'_II_rt7': [0.33], '_PT_rt7': [0.33]}}
    pol.implement_reform(reform)
    reform_behav = {year: {'_BE_sub': [0.4], '_BE_cg': [-3.67]}}
    beh.update_behavior(reform_behav)
    calc_clp = calc.current_law_version()
    calc_beh = Behavior.response(calc_clp, calc)
    calc_beh.calc_all()
    liabilities_x = (calc_beh.records.combined *
                     calc_beh.records.s006).sum()
    adt = multiyear_diagnostic_table(calc_beh, 1)
    # extract combined liabilities as a float and
    # adopt units of the raw calculator data in liabilities_x
    liabilities_y = adt.iloc[19].tolist()[0] * 1e9
    assert np.allclose(liabilities_x, liabilities_y, atol=0.01, rtol=0.0)


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
    cyr = 2020
    # specify calc1 and calc_all() for cyr
    pol1 = Policy()
    rec1 = Records.cps_constructor(data=cps_subsample)
    calc1 = Calculator(policy=pol1, records=rec1)
    calc1.advance_to_year(cyr)
    calc1.calc_all()
    # specify calc2 and calc_all() for cyr
    pol2 = Policy()
    reform = {2018: {'_II_em': [0.0]}}
    pol2.implement_reform(reform)
    rec2 = Records.cps_constructor(data=cps_subsample)
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
