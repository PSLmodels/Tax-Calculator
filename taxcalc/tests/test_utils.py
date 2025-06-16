"""
Tests of Tax-Calculator utility functions.
"""
# CODING-STYLE CHECKS:
# pycodestyle test_utils.py
# pylint --disable=locally-disabled test_utils.py

import os
import math
import random
import numpy as np
import pandas as pd
import pytest
from taxcalc.policy import Policy
from taxcalc.records import Records
from taxcalc.calculator import Calculator
from taxcalc.utils import (
    DIST_VARIABLES,
    DIST_TABLE_COLUMNS, DIST_TABLE_LABELS,
    DIFF_VARIABLES,
    DIFF_TABLE_COLUMNS, DIFF_TABLE_LABELS,
    SOI_AGI_BINS,
    create_difference_table,
    weighted_sum, weighted_mean,
    wage_weighted, agi_weighted,
    expanded_income_weighted,
    add_income_table_row_variable,
    add_quantile_table_row_variable,
    mtr_graph_data, atr_graph_data,
    xtr_graph_plot, write_graph_file,
    read_egg_csv, read_egg_json, delete_file,
    bootstrap_se_ci,
    certainty_equivalent,
    ce_aftertax_expanded_income,
    json_to_dict
)


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
    """Test docstring"""
    assert len(DIST_TABLE_COLUMNS) == len(DIST_TABLE_LABELS)
    records_varinfo = Records(data=None)
    assert set(DIST_VARIABLES).issubset(records_varinfo.CALCULATED_VARS |
                                        {'s006', 'XTOT'})
    extra_vars_set = set(['count',
                          'count_StandardDed',
                          'count_ItemDed',
                          'count_AMT'])
    assert (set(DIST_TABLE_COLUMNS) - set(DIST_VARIABLES)) == extra_vars_set


def test_create_tables(cps_subsample):
    """Test docstring"""
    # pylint: disable=too-many-statements,too-many-branches

    # create a current-law Policy object and Calculator object calc1
    rec = Records.cps_constructor(data=cps_subsample)
    pol = Policy()
    calc1 = Calculator(policy=pol, records=rec)
    calc1.calc_all()
    # create a policy-reform Policy object and Calculator object calc2
    reform = {'II_rt1': {2013: 0.15}}
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
    expected = [0.0,
                np.nan,
                -0.1,
                -0.5,
                -0.8,
                -0.8,
                -0.9,
                -0.7,
                -0.7,
                -0.7,
                -0.3,
                -0.1,
                -0.0,
                -0.6]
    if not np.allclose(diff[tabcol].values.astype('float'), expected,
                       atol=0.1, rtol=0.0, equal_nan=True):
        test_failure = True
        print('diff xbin', tabcol)
        for val in diff[tabcol].values:
            print(f'{val:.1f},')

    diff = create_difference_table(calc1.dataframe(DIFF_VARIABLES),
                                   calc2.dataframe(DIFF_VARIABLES),
                                   'weighted_deciles', 'combined')
    assert isinstance(diff, pd.DataFrame)
    tabcol = 'tot_change'
    expected = [0.0,
                0.0,
                0.0,
                0.6,
                2.9,
                4.1,
                4.9,
                6.6,
                7.1,
                9.1,
                12.3,
                13.6,
                61.2,
                7.7,
                5.0,
                0.9]
    if not np.allclose(diff[tabcol].values.astype('float'), expected,
                       atol=0.1, rtol=0.0):
        test_failure = True
        print('diff xdec', tabcol)
        for val in diff[tabcol].values:
            print(f'{val:.1f},')

    tabcol = 'share_of_change'
    expected = [0.0,
                0.0,
                0.0,
                0.9,
                4.8,
                6.7,
                8.0,
                10.7,
                11.6,
                14.8,
                20.1,
                22.3,
                100.0,
                12.6,
                8.2,
                1.5]
    if not np.allclose(diff[tabcol].values.astype('float'), expected,
                       atol=0.1, rtol=0.0):
        test_failure = True
        print('diff xdec', tabcol)
        for val in diff[tabcol].values:
            print(f'{val:.1f},')

    tabcol = 'pc_aftertaxinc'
    expected = [np.nan,
                0.0,
                -0.0,
                -0.3,
                -0.8,
                -0.8,
                -0.8,
                -0.9,
                -0.7,
                -0.7,
                -0.8,
                -0.4,
                -0.6,
                -0.7,
                -0.4,
                -0.1]
    if not np.allclose(diff[tabcol].values.astype('float'), expected,
                       atol=0.1, rtol=0.0, equal_nan=True):
        test_failure = True
        print('diff xdec', tabcol)
        for val in diff[tabcol].values:
            print(f'{val:.1f},')

    # test creating various distribution tables

    dist, _ = calc2.distribution_tables(None, 'weighted_deciles')
    assert isinstance(dist, pd.DataFrame)
    tabcol = 'iitax'
    expected = [0.0,
                0.0,
                -0.3,
                -3.8,
                -5.3,
                15.4,
                22.3,
                34.8,
                33.6,
                76.1,
                159.7,
                931.0,
                1263.5,
                163.0,
                278.2,
                489.8]
    if not np.allclose(dist[tabcol].values.astype('float'), expected,
                       atol=0.1, rtol=0.0):
        test_failure = True
        print('dist xdec', tabcol)
        for val in dist[tabcol].values:
            print(f'{val:.1f},')

    tabcol = 'count_ItemDed'
    expected = [0.0,
                0.0,
                0.0,
                1.1,
                2.6,
                3.9,
                4.7,
                6.3,
                6.5,
                7.4,
                11.3,
                16.3,
                60.3,
                7.4,
                7.2,
                1.7]
    if not np.allclose(dist[tabcol].tolist(), expected,
                       atol=0.1, rtol=0.0):
        test_failure = True
        print('dist xdec', tabcol)
        for val in dist[tabcol].values:
            print(f'{val:.1f},')

    tabcol = 'expanded_income'
    expected = [0.0,
                -1.4,
                30.7,
                209.8,
                388.8,
                541.2,
                679.1,
                847.6,
                1097.1,
                1430.7,
                1978.3,
                5007.6,
                12209.4,
                1410.9,
                1765.5,
                1831.2]
    if not np.allclose(dist[tabcol].tolist(), expected,
                       atol=0.1, rtol=0.0):
        test_failure = True
        print('dist xdec', tabcol)
        for val in dist[tabcol].values:
            print(f'{val:.1f},')

    tabcol = 'aftertax_income'
    expected = [0.0,
                -1.4,
                29.0,
                195.5,
                363.0,
                490.4,
                611.7,
                746.6,
                980.0,
                1247.7,
                1629.9,
                3741.0,
                10033.4,
                1100.9,
                1338.8,
                1301.3]
    if not np.allclose(dist[tabcol].tolist(), expected,
                       atol=0.1, rtol=0.0):
        test_failure = True
        print('dist xdec', tabcol)
        for val in dist[tabcol].values:
            print(f'{val:.1f},')

    dist, _ = calc2.distribution_tables(None, 'standard_income_bins')
    assert isinstance(dist, pd.DataFrame)
    tabcol = 'iitax'
    expected = [0.0,
                0.0,
                -1.2,
                -7.1,
                3.5,
                26.7,
                33.4,
                55.2,
                101.4,
                335.2,
                335.4,
                65.6,
                315.5,
                1263.5]
    if not np.allclose(dist[tabcol].values.astype('float'), expected,
                       atol=0.1, rtol=0.0):
        test_failure = True
        print('dist xbin', tabcol)
        for val in dist[tabcol].values:
            print(f'{val:.1f},')

    tabcol = 'count_ItemDed'
    expected = [0.0,
                0.0,
                0.2,
                1.8,
                3.6,
                5.9,
                5.7,
                10.2,
                8.1,
                17.7,
                6.7,
                0.3,
                0.1,
                60.3]
    if not np.allclose(dist[tabcol].tolist(), expected,
                       atol=0.1, rtol=0.0):
        test_failure = True
        print('dist xbin', tabcol)
        for val in dist[tabcol].values:
            print(f'{val:.1f},')

    if test_failure:
        assert False, 'ERROR: test failure'


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
    0    7081 <--- negative income bin was dropped in TaxBrain display
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
        res = (
            f'EST={data_estimate:.1f} B={bs_samples} alpha={alpha:.3f} '
            f'se={stderr:.2f} ci=[ {cilo:.2f} , {cihi:.2f} ]'
        )
        print(f'STANDARD-BIN10: {res}')
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
        res = (
            f'EST={data_estimate:.1f} B={bs_samples} alpha={alpha:.3f} '
            f'se={stderr:.2f} ci=[ {cilo:.2f} , {cihi:.2f} ]'
        )
        print(f'STANDARD-BIN11: {res}')
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


def test_weighted_mean():
    """Test docstring"""
    dfx = pd.DataFrame(data=DATA, columns=['tax_diff', 's006', 'label'])
    grouped = dfx.groupby('label')
    diffs = grouped.apply(weighted_mean, 'tax_diff', include_groups=False)
    exp = pd.Series(data=[16.0 / 12.0, 26.0 / 10.0], index=['a', 'b'])
    exp.index.name = 'label'
    pd.testing.assert_series_equal(exp, diffs)


def test_wage_weighted():
    """Test docstring"""
    dfx = pd.DataFrame(data=WEIGHT_DATA, columns=['var', 's006', 'e00200'])
    wvar = wage_weighted(dfx, 'var')
    assert round(wvar, 4) == 2.5714


def test_agi_weighted():
    """Test docstring"""
    dfx = pd.DataFrame(data=WEIGHT_DATA, columns=['var', 's006', 'c00100'])
    wvar = agi_weighted(dfx, 'var')
    assert round(wvar, 4) == 2.5714


def test_expanded_income_weighted():
    """Test docstring"""
    dfx = pd.DataFrame(data=WEIGHT_DATA,
                       columns=['var', 's006', 'expanded_income'])
    wvar = expanded_income_weighted(dfx, 'var')
    assert round(wvar, 4) == 2.5714


def test_weighted_sum():
    """Test docstring"""
    dfx = pd.DataFrame(data=DATA, columns=['tax_diff', 's006', 'label'])
    grouped = dfx.groupby('label')
    diffs = grouped.apply(weighted_sum, 'tax_diff', include_groups=False)
    exp = pd.Series(data=[16.0, 26.0], index=['a', 'b'])
    exp.index.name = 'label'
    pd.testing.assert_series_equal(exp, diffs)


EPSILON = 1e-5


def test_add_income_trow_var():
    """Test docstring"""
    dta = np.arange(1, 1e6, 5000)
    vdf = pd.DataFrame(data=dta, columns=['expanded_income'])
    vdf = add_income_table_row_variable(vdf, 'expanded_income', SOI_AGI_BINS)
    gdf = vdf.groupby('table_row', observed=False)
    idx = 1
    for name, _ in gdf:
        assert name.closed == 'left'
        assert abs(name.right - SOI_AGI_BINS[idx]) < EPSILON
        idx += 1


def test_add_quantile_trow_var():
    """Test docstring"""
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
    """Test docstring"""
    rec = Records.cps_constructor(data=cps_subsample)
    calc = Calculator(policy=Policy(), records=rec)
    calc.calc_all()
    # create three distribution tables and compare the ALL row contents
    tb1, _ = calc.distribution_tables(None, 'standard_income_bins')
    tb2, _ = calc.distribution_tables(None, 'soi_agi_bins')
    tb3, _ = calc.distribution_tables(None, 'weighted_deciles')
    tb4, _ = calc.distribution_tables(None, 'weighted_deciles',
                                      pop_quantiles=True)
    assert np.allclose(tb1.loc['ALL'].values.astype('float'),
                       tb2.loc['ALL'].values.astype('float'))
    assert np.allclose(tb1.loc['ALL'].values.astype('float'),
                       tb3.loc['ALL'].values.astype('float'))
    # make sure population count is larger than filing-unit count
    assert tb4.at['ALL', 'count'] > tb1.at['ALL', 'count']
    # make sure population table has same ALL row values as filing-unit table
    for col in ['count', 'count_StandardDed', 'count_ItemDed', 'count_AMT']:
        tb4.at['ALL', col] = tb1.at['ALL', col]
    assert np.allclose(tb1.loc['ALL'].values.astype('float'),
                       tb4.loc['ALL'].values.astype('float'))
    # make sure population table has same ALL tax liabilities as diagnostic tbl
    dgt = calc.diagnostic_table(1)
    assert np.allclose([tb4.at['ALL', 'iitax'],
                        tb4.at['ALL', 'payrolltax']],
                       [dgt.at['Ind Income Tax ($b)', calc.current_year],
                        dgt.at['Payroll Taxes ($b)', calc.current_year]])


def test_diff_table_sum_row(cps_subsample):
    """Test docstring"""
    rec = Records.cps_constructor(data=cps_subsample)
    # create a current-law Policy object and Calculator calc1
    pol = Policy()
    calc1 = Calculator(policy=pol, records=rec)
    calc1.calc_all()
    # create a policy-reform Policy object and Calculator calc2
    reform = {'II_rt4': {2013: 0.56}}
    pol.implement_reform(reform)
    calc2 = Calculator(policy=pol, records=rec)
    calc2.calc_all()
    # create three difference tables and compare their content
    dv1 = calc1.dataframe(DIFF_VARIABLES)
    dv2 = calc2.dataframe(DIFF_VARIABLES)
    dt1 = create_difference_table(
        dv1, dv2, 'standard_income_bins', 'iitax')
    dt2 = create_difference_table(dv1, dv2, 'soi_agi_bins', 'iitax')
    dt3 = create_difference_table(
        dv1, dv2, 'weighted_deciles', 'iitax', pop_quantiles=False)
    dt4 = create_difference_table(
        dv1, dv2, 'weighted_deciles', 'iitax', pop_quantiles=True)
    assert np.allclose(dt1.loc['ALL'].values.astype('float'),
                       dt2.loc['ALL'].values.astype('float'))
    assert np.allclose(dt1.loc['ALL'].values.astype('float'),
                       dt3.loc['ALL'].values.astype('float'))
    # make sure population count is larger than filing-unit count
    assert dt4.at['ALL', 'count'] > dt1.at['ALL', 'count']


def test_mtr_graph_data(cps_subsample):
    """Test docstring"""
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
        mtr_graph_data(None, year, mars=[])
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
    """Test docstring"""
    pol = Policy()
    rec = Records.cps_constructor(data=cps_subsample)
    calc = Calculator(policy=pol, records=rec)
    year = calc.current_year
    with pytest.raises(ValueError):
        atr_graph_data(None, year, mars='bad')
    with pytest.raises(ValueError):
        atr_graph_data(None, year, mars=0)
    with pytest.raises(ValueError):
        atr_graph_data(None, year, mars=[])
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
    """Test docstring"""
    recs = Records.cps_constructor(data=cps_subsample)
    calc = Calculator(policy=Policy(), records=recs)
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
    """Function docstring"""
    # Return string containing the temporary filename.
    rint = random.randint(10000000, 99999999)
    return f'tmp{rint}{suffix}'


def test_write_graph_file(cps_subsample):
    """Test docstring"""
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
        assert False, 'ERROR: write_graph_file() failed'
    # if try was successful, try to remove the file
    if os.path.isfile(htmlfname):
        try:
            os.remove(htmlfname)
        except OSError:
            pass  # sometimes we can't remove a generated temporary file


def test_ce_aftertax_income(cps_subsample):
    """Test docstring"""
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
    reform = {'II_em': {2019: 1000}}
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
    """Test docstring"""
    with pytest.raises(ValueError):
        read_egg_csv('bad_filename')


def test_read_egg_json():
    """Test docstring"""
    with pytest.raises(ValueError):
        read_egg_json('bad_filename')


def test_create_delete_temp_file():
    """Test docstring"""
    # test temporary_filename() and delete_file() functions
    fname = temporary_filename()
    with open(fname, 'w', encoding='utf-8') as tmpfile:
        tmpfile.write('any content will do')
    assert os.path.isfile(fname) is True
    delete_file(fname)
    assert os.path.isfile(fname) is False


def test_bootstrap_se_ci():
    """Test docstring"""
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
    """Test docstring"""
    # check that length of two lists are the same
    assert len(DIST_TABLE_COLUMNS) == len(DIST_TABLE_LABELS)
    assert len(DIFF_TABLE_COLUMNS) == len(DIFF_TABLE_LABELS)


def test_invalid_json_to_dict():
    """Test docstring"""
    with pytest.raises(ValueError):
        json_to_dict('invalid_json_text')
