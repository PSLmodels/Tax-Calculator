"""
Private utility functions used only by public functions in the tbi.py file.
"""
# CODING-STYLE CHECKS:
# pep8 --ignore=E402 tbi_utils.py
# pylint --disable=locally-disabled tbi_utils.py

import copy
import hashlib
import numpy as np
import pandas as pd
from taxcalc import (Policy, Records, Calculator,
                     Consumption, Behavior, Growfactors, Growdiff)
from taxcalc.utils import (add_income_bins, add_quantile_bins, results,
                           create_difference_table, create_distribution_table,
                           STATS_COLUMNS, DIST_TABLE_COLUMNS,
                           WEBAPP_INCOME_BINS)


def check_years(start_year, year_n):
    """
    Ensure start_year and year_n values are consistent with Policy constants.
    """
    if start_year < Policy.JSON_START_YEAR:
        msg = 'start_year={} < Policy.JSON_START_YEAR={}'
        raise ValueError(msg.format(start_year, Policy.JSON_START_YEAR))
    if year_n < 0:
        msg = 'year_n={} < 0'
        raise ValueError(msg.format(year_n))
    if (start_year + year_n) > Policy.LAST_BUDGET_YEAR:
        msg = '(start_year={} + year_n={}) > Policy.LAST_BUDGET_YEAR={}'
        raise ValueError(msg.format(start_year, year_n,
                                    Policy.LAST_BUDGET_YEAR))


def check_user_mods(user_mods):
    """
    Ensure specified user_mods is properly structured.
    """
    if not isinstance(user_mods, dict):
        raise ValueError('user_mods is not a dictionary')
    actual_keys = set(list(user_mods.keys()))
    expected_keys = set(['policy', 'consumption', 'behavior',
                         'growdiff_baseline', 'growdiff_response',
                         'gdp_elasticity'])
    missing_keys = expected_keys - actual_keys
    if len(missing_keys) > 0:
        raise ValueError('user_mods has missing keys: {}'.format(missing_keys))
    extra_keys = actual_keys - expected_keys
    if len(extra_keys) > 0:
        raise ValueError('user_mods has extra keys: {}'.format(extra_keys))


def calculate(year_n, start_year,
              taxrec_df, user_mods,
              behavior_allowed, mask_computed):
    """
    The calculate function assumes specified user_mods is
      a dictionary returned by the Calculator.read_json_parameter_files()
      function with an extra key:value pair that is specified as
      'gdp_elasticity': {'value': <float_value>}.
    The function returns (calc1, calc2, mask) where
      calc1 is pre-reform Calculator object calculated for year_n,
      calc2 is post-reform Calculator object calculated for year_n, and
      mask is boolean array if compute_mask=True or None otherwise
    """
    # pylint: disable=too-many-arguments,too-many-locals,too-many-statements

    check_years(start_year, year_n)
    check_user_mods(user_mods)

    # specify Consumption instance
    consump = Consumption()
    consump_assumptions = user_mods['consumption']
    consump.update_consumption(consump_assumptions)

    # specify growdiff_baseline and growdiff_response
    growdiff_baseline = Growdiff()
    growdiff_response = Growdiff()
    growdiff_base_assumps = user_mods['growdiff_baseline']
    growdiff_resp_assumps = user_mods['growdiff_response']
    growdiff_baseline.update_growdiff(growdiff_base_assumps)
    growdiff_response.update_growdiff(growdiff_resp_assumps)

    # create pre-reform and post-reform Growfactors instances
    growfactors_pre = Growfactors()
    growdiff_baseline.apply_to(growfactors_pre)
    growfactors_post = Growfactors()
    growdiff_baseline.apply_to(growfactors_post)
    growdiff_response.apply_to(growfactors_post)

    # create pre-reform Calculator instance using PUF input data & weights
    recs1 = Records(data=copy.deepcopy(taxrec_df),
                    gfactors=growfactors_pre)
    policy1 = Policy(gfactors=growfactors_pre)
    calc1 = Calculator(policy=policy1, records=recs1, consumption=consump)
    while calc1.current_year < start_year:
        calc1.increment_year()
    calc1.calc_all()
    assert calc1.current_year == start_year

    # optionally compute mask
    if mask_computed:
        # create pre-reform Calculator instance with extra income using
        # PUF input data & weights
        recs1p = Records(data=copy.deepcopy(taxrec_df),
                         gfactors=growfactors_pre)
        # add one dollar to the income of each filing unit to determine
        # which filing units undergo a resulting change in tax liability
        recs1p.e00200 += 1.0  # pylint: disable=no-member
        recs1p.e00200p += 1.0  # pylint: disable=no-member
        policy1p = Policy(gfactors=growfactors_pre)
        # create Calculator with recs1p and calculate for start_year
        calc1p = Calculator(policy=policy1p, records=recs1p,
                            consumption=consump)
        while calc1p.current_year < start_year:
            calc1p.increment_year()
        calc1p.calc_all()
        assert calc1p.current_year == start_year
        # compute mask showing which of the calc1 and calc1p results differ;
        # mask is true if a filing unit's income tax liability changed after
        # a dollar was added to the filing unit's wage and salary income
        res1 = results(calc1.records)
        res1p = results(calc1p.records)
        mask = np.logical_not(  # pylint: disable=no-member
            np.isclose(res1.iitax, res1p.iitax, atol=0.001, rtol=0.0)
        )
    else:
        mask = None

    # specify Behavior instance
    behv = Behavior()
    behavior_assumps = user_mods['behavior']
    behv.update_behavior(behavior_assumps)

    # always prevent both behavioral response and growdiff response
    if behv.has_any_response() and growdiff_response.has_any_response():
        msg = 'BOTH behavior AND growdiff_response HAVE RESPONSE'
        raise ValueError(msg)

    # optionally prevent behavioral response
    if behv.has_any_response() and not behavior_allowed:
        msg = 'A behavior RESPONSE IS NOT ALLOWED'
        raise ValueError(msg)

    # create post-reform Calculator instance using PUF input data & weights
    recs2 = Records(data=copy.deepcopy(taxrec_df),
                    gfactors=growfactors_post)
    policy2 = Policy(gfactors=growfactors_post)
    policy_reform = user_mods['policy']
    policy2.implement_reform(policy_reform)
    calc2 = Calculator(policy=policy2, records=recs2,
                       consumption=consump, behavior=behv)
    while calc2.current_year < start_year:
        calc2.increment_year()
    calc2.calc_all()
    assert calc2.current_year == start_year

    # increment Calculator objects for year_n years and calculate
    for _ in range(0, year_n):
        calc1.increment_year()
        calc2.increment_year()
    calc1.calc_all()
    if calc2.behavior.has_response():
        calc2 = Behavior.response(calc1, calc2)
    else:
        calc2.calc_all()

    # return calculated Calculator objects and mask
    return (calc1, calc2, mask)


def random_seed(user_mods):
    """
    Compute random seed based on specified user_mods, which is a
    dictionary returned by the Calculator.read_json_parameter_files()
    function with an extra key:value pair that is specified as
    'gdp_elasticity': {'value': <float_value>}.
    """
    ans = 0
    for subdict_name in user_mods:
        if subdict_name != 'gdp_elasticity':
            ans += random_seed_from_subdict(user_mods[subdict_name])
    return ans % np.iinfo(np.uint32).max  # pylint: disable=no-member


def random_seed_from_subdict(subdict):
    """
    Compute random seed from one user_mods subdictionary.
    """
    assert isinstance(subdict, dict)
    all_vals = []
    for year in sorted(subdict.keys()):
        all_vals.append(str(year))
        params = subdict[year]
        for param in sorted(params.keys()):
            try:
                tple = tuple(params[param])
            except TypeError:
                # params[param] is not an iterable value; make it so
                tple = tuple((params[param],))
            all_vals.append(str((param, tple)))
    txt = u''.join(all_vals).encode('utf-8')
    hsh = hashlib.sha512(txt)
    seed = int(hsh.hexdigest(), 16)
    return seed % np.iinfo(np.uint32).max  # pylint: disable=no-member


NUM_TO_FUZZ = 3


def chooser(agg):
    """
    This is a transformation function that should be called on each group
    (that is, each cell in a table).  It is assumed that the chunk 'agg' is
    a chunk of the 'mask' column.  This chooser selects NUM_TO_FUZZ of those
    mask indices with the output for those NUM_TO_FUZZ indices being zero and
    the output for all the other indices being one.
    """
    # select indices of records with change in tax liability after
    # a one dollar increase in income
    indices = np.where(agg)
    if len(indices[0]) >= NUM_TO_FUZZ:
        choices = np.random.choice(indices[0],  # pylint: disable=no-member
                                   size=NUM_TO_FUZZ, replace=False)
    else:
        msg = ('Not enough differences in income tax when adding '
               'one dollar for chunk with name: {}')
        raise ValueError(msg.format(agg.name))
    # mark the records chosen to be fuzzed
    ans = [1] * len(agg)
    for idx in choices:
        ans[idx] = 0
    return ans


def fuzz_df2_records(df1, df2, mask):
    """
    Modify df2 by adding random fuzz for data privacy.

    Parameters
    ----------
    df1: Pandas DataFrame
        contains results for the baseline plan

    df2: Pandas DataFrame
        contains results for the reform plan

    mask: boolean numpy array
        contains info about whether or not each row might be fuzzed

    Returns
    -------
    fuzzed df2: Pandas DataFrame

    Notes
    -----
    This function groups both DataFrames based on the web application's
    income groupings (both decile and income bins), and then randomly
    selects NUM_TO_FUZZ records to fuzz within each bin.  The fuzzing
    involves overwriting df2 columns in cols_to_fuzz with df1 values.
    """
    # nested function that does the fuzzing
    def fuzz(df1, df2, bin_type, imeasure, suffix, cols_to_fuzz):
        """
        Fuzz some df2 records in each bin defined by bin_type and imeasure.
        The fuzzed records have their post-reform tax results (in df2)
        set to their pre-reform tax results (in df1).
        """
        # pylint: disable=too-many-arguments
        assert bin_type == 'dec' or bin_type == 'bin' or bin_type == 'agg'
        if bin_type == 'dec':
            df2 = add_quantile_bins(df2, imeasure, 10)
        elif bin_type == 'bin':
            df2 = add_income_bins(df2, imeasure, bins=WEBAPP_INCOME_BINS)
        else:
            df2 = add_quantile_bins(df2, imeasure, 1)
        gdf2 = df2.groupby('bins')
        df2['nofuzz'] = gdf2['mask'].transform(chooser)
        for col in cols_to_fuzz:
            df2[col + suffix] = (df2[col] * df2['nofuzz'] -
                                 df1[col] * df2['nofuzz'] + df1[col])
    # main logic of fuzz_df2_records
    skips = set(['num_returns_ItemDed',
                 'num_returns_StandardDed',
                 'num_returns_AMT',
                 's006'])
    columns_to_fuzz = (set(DIST_TABLE_COLUMNS) | set(STATS_COLUMNS)) - skips
    df2['mask'] = mask
    # always use expanded income in df1 baseline to groupby into bins
    df2['expanded_income_baseline'] = df1['expanded_income']
    fuzz(df1, df2, 'dec', 'expanded_income_baseline', '_xdec', columns_to_fuzz)
    fuzz(df1, df2, 'bin', 'expanded_income_baseline', '_xbin', columns_to_fuzz)
    fuzz(df1, df2, 'agg', 'expanded_income_baseline', '_agg', columns_to_fuzz)
    df2['c00100_baseline'] = df1['c00100']  # c00100 is AGI
    fuzz(df1, df2, 'dec', 'c00100_baseline', '_adec', columns_to_fuzz)
    fuzz(df1, df2, 'bin', 'c00100_baseline', '_abin', columns_to_fuzz)
    return df2


AGGR_ROW_NAMES = ['ind_tax', 'payroll_tax', 'combined_tax']


def summary(df1, df2, mask):
    """
    df1 contains raw results for baseline plan
    df2 contains raw results for reform plan
    mask is the boolean array specifying which records might be fuzzed
    returns dictionary of summary results DataFrames
    """
    # pylint: disable=too-many-statements,too-many-locals

    df2 = fuzz_df2_records(df1, df2, mask)

    summ = dict()

    # tax difference totals between reform and baseline
    tdiff = df2['iitax_agg'] - df1['iitax']
    aggr_itax_d = (tdiff * df2['s006']).sum()
    tdiff = df2['payrolltax_agg'] - df1['payrolltax']
    aggr_ptax_d = (tdiff * df2['s006']).sum()
    tdiff = df2['combined_agg'] - df1['combined']
    aggr_comb_d = (tdiff * df2['s006']).sum()
    aggrd = [aggr_itax_d, aggr_ptax_d, aggr_comb_d]
    summ['aggr_d'] = pd.DataFrame(data=aggrd, index=AGGR_ROW_NAMES)

    # totals for baseline
    aggr_itax_1 = (df1['iitax'] * df1['s006']).sum()
    aggr_ptax_1 = (df1['payrolltax'] * df1['s006']).sum()
    aggr_comb_1 = (df1['combined'] * df1['s006']).sum()
    aggr1 = [aggr_itax_1, aggr_ptax_1, aggr_comb_1]
    summ['aggr_1'] = pd.DataFrame(data=aggr1, index=AGGR_ROW_NAMES)

    # totals for reform
    aggr_itax_2 = (df2['iitax_agg'] * df2['s006']).sum()
    aggr_ptax_2 = (df2['payrolltax_agg'] * df2['s006']).sum()
    aggr_comb_2 = (df2['combined_agg'] * df2['s006']).sum()
    aggr2 = [aggr_itax_2, aggr_ptax_2, aggr_comb_2]
    summ['aggr_2'] = pd.DataFrame(data=aggr2, index=AGGR_ROW_NAMES)

    # create difference tables grouped by xdec
    df2['iitax'] = df2['iitax_xdec']
    summ['diff_itax_xdec'] = \
        create_difference_table(df1, df2,
                                groupby='weighted_deciles',
                                income_measure='expanded_income',
                                tax_to_diff='iitax')

    df2['payrolltax'] = df2['payrolltax_xdec']
    summ['diff_ptax_xdec'] = \
        create_difference_table(df1, df2,
                                groupby='weighted_deciles',
                                income_measure='expanded_income',
                                tax_to_diff='payrolltax')

    df2['combined'] = df2['combined_xdec']
    summ['diff_comb_xdec'] = \
        create_difference_table(df1, df2,
                                groupby='weighted_deciles',
                                income_measure='expanded_income',
                                tax_to_diff='combined')

    # create difference tables grouped by xbin (removing negative-income bin)
    df2['iitax'] = df2['iitax_xbin']
    diff_itax_xbin = \
        create_difference_table(df1, df2,
                                groupby='webapp_income_bins',
                                income_measure='expanded_income',
                                tax_to_diff='iitax')
    diff_itax_xbin.drop(diff_itax_xbin.index[0], inplace=True)
    summ['diff_itax_xbin'] = diff_itax_xbin

    df2['payrolltax'] = df2['payrolltax_xbin']
    diff_ptax_xbin = \
        create_difference_table(df1, df2,
                                groupby='webapp_income_bins',
                                income_measure='expanded_income',
                                tax_to_diff='payrolltax')
    diff_ptax_xbin.drop(diff_ptax_xbin.index[0], inplace=True)
    summ['diff_ptax_xbin'] = diff_ptax_xbin

    df2['combined'] = df2['combined_xbin']
    diff_comb_xbin = \
        create_difference_table(df1, df2,
                                groupby='webapp_income_bins',
                                income_measure='expanded_income',
                                tax_to_diff='combined')
    diff_comb_xbin.drop(diff_comb_xbin.index[0], inplace=True)
    summ['diff_comb_xbin'] = diff_comb_xbin

    # create distribution tables grouped by xdec
    summ['dist1_xdec'] = \
        create_distribution_table(df1, groupby='weighted_deciles',
                                  income_measure='expanded_income',
                                  result_type='weighted_sum')

    suffix = '_xdec'
    df2_cols_with_suffix = [c for c in list(df2) if c.endswith(suffix)]
    for col in df2_cols_with_suffix:
        root_col_name = col.replace(suffix, '')
        df2[root_col_name] = df2[col]
    df2['expanded_income_baseline'] = df1['expanded_income']
    summ['dist2_xdec'] = \
        create_distribution_table(df2, groupby='weighted_deciles',
                                  income_measure='expanded_income_baseline',
                                  result_type='weighted_sum')

    # create distribution tables grouped by xbin (removing negative-income bin)
    dist1_xbin = \
        create_distribution_table(df1, groupby='webapp_income_bins',
                                  income_measure='expanded_income',
                                  result_type='weighted_sum')
    dist1_xbin.drop(dist1_xbin.index[0], inplace=True)
    summ['dist1_xbin'] = dist1_xbin

    suffix = '_xbin'
    df2_cols_with_suffix = [c for c in list(df2) if c.endswith(suffix)]
    for col in df2_cols_with_suffix:
        root_col_name = col.replace(suffix, '')
        df2[root_col_name] = df2[col]
    df2['expanded_income_baseline'] = df1['expanded_income']
    dist2_xbin = \
        create_distribution_table(df2, groupby='webapp_income_bins',
                                  income_measure='expanded_income_baseline',
                                  result_type='weighted_sum')
    dist2_xbin.drop(dist2_xbin.index[0], inplace=True)
    summ['dist2_xbin'] = dist2_xbin

    # create difference tables grouped by adec
    df2['iitax'] = df2['iitax_adec']
    summ['diff_itax_adec'] = \
        create_difference_table(df1, df2,
                                groupby='weighted_deciles',
                                income_measure='c00100',
                                tax_to_diff='iitax')

    df2['payrolltax'] = df2['payrolltax_adec']
    summ['diff_ptax_adec'] = \
        create_difference_table(df1, df2,
                                groupby='weighted_deciles',
                                income_measure='c00100',
                                tax_to_diff='payrolltax')

    df2['combined'] = df2['combined_adec']
    summ['diff_comb_adec'] = \
        create_difference_table(df1, df2,
                                groupby='weighted_deciles',
                                income_measure='c00100',
                                tax_to_diff='combined')

    # create difference tables grouped by abin (removing negative-income bin)
    df2['iitax'] = df2['iitax_abin']
    diff_itax_abin = \
        create_difference_table(df1, df2,
                                groupby='webapp_income_bins',
                                income_measure='c00100',
                                tax_to_diff='iitax')
    diff_itax_abin.drop(diff_itax_abin.index[0], inplace=True)
    summ['diff_itax_abin'] = diff_itax_abin

    df2['payrolltax'] = df2['payrolltax_abin']
    diff_ptax_abin = \
        create_difference_table(df1, df2,
                                groupby='webapp_income_bins',
                                income_measure='c00100',
                                tax_to_diff='payrolltax')
    diff_ptax_abin.drop(diff_ptax_abin.index[0], inplace=True)
    summ['diff_ptax_abin'] = diff_ptax_abin

    df2['combined'] = df2['combined_abin']
    diff_comb_abin = \
        create_difference_table(df1, df2,
                                groupby='webapp_income_bins',
                                income_measure='c00100',
                                tax_to_diff='combined')
    diff_comb_abin.drop(diff_comb_abin.index[0], inplace=True)
    summ['diff_comb_abin'] = diff_comb_abin

    # create distribution tables grouped by adec
    summ['dist1_adec'] = \
        create_distribution_table(df1, groupby='weighted_deciles',
                                  income_measure='c00100',
                                  result_type='weighted_sum')

    suffix = '_adec'
    df2_cols_with_suffix = [c for c in list(df2) if c.endswith(suffix)]
    for col in df2_cols_with_suffix:
        root_col_name = col.replace(suffix, '')
        df2[root_col_name] = df2[col]
    df2['c00100_baseline'] = df1['c00100']
    summ['dist2_adec'] = \
        create_distribution_table(df2, groupby='weighted_deciles',
                                  income_measure='c00100_baseline',
                                  result_type='weighted_sum')

    # create distribution tables grouped by abin (removing negative-income bin)
    dist1_abin = \
        create_distribution_table(df1, groupby='webapp_income_bins',
                                  income_measure='c00100',
                                  result_type='weighted_sum')
    dist1_abin.drop(dist1_abin.index[0], inplace=True)
    summ['dist1_abin'] = dist1_abin

    suffix = '_abin'
    df2_cols_with_suffix = [c for c in list(df2) if c.endswith(suffix)]
    for col in df2_cols_with_suffix:
        root_col_name = col.replace(suffix, '')
        df2[root_col_name] = df2[col]
    df2['c00100_baseline'] = df1['c00100']
    dist2_abin = \
        create_distribution_table(df2, groupby='webapp_income_bins',
                                  income_measure='c00100_baseline',
                                  result_type='weighted_sum')
    dist2_abin.drop(dist2_abin.index[0], inplace=True)
    summ['dist2_abin'] = dist2_abin

    # return dictionary of summary results
    return summ
