"""
Utility functions used by functions in dropq.py file.
"""
# CODING-STYLE CHECKS:
# pep8 --ignore=E402 dropq_utils.py
# pylint --disable=locally-disabled dropq_utils.py

import hashlib
import numpy as np
import pandas as pd
from taxcalc import (Policy, Records, Calculator,
                     Consumption, Behavior, Growfactors, Growdiff)
from taxcalc.utils import (add_income_bins, add_weighted_income_bins,
                           means_and_comparisons, get_sums,
                           weighted, weighted_avg_allcols,
                           create_distribution_table, results,
                           STATS_COLUMNS, TABLE_COLUMNS, WEBAPP_INCOME_BINS)


EPSILON = 1e-3


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


def dropq_calculate(year_n, start_year,
                    taxrec_df, user_mods,
                    behavior_allowed, mask_computed):
    """
    The dropq_calculate function assumes specified user_mods is
      a dictionary returned by the Calculator.read_json_parameter_files()
      function with an extra key:value pair that is specified as
      'gdp_elasticity': {'value': <float_value>}.
    The function returns (calc1, calc2, mask) where
      calc1 is pre-reform Calculator object calculated for year_n,
      calc2 is post-reform Calculator object calculated for year_n, and
      mask is boolean array if compute_mask=True or None otherwise
    """
    # pylint: disable=too-many-arguments,too-many-locals,too-many-statements

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

    # create pre-reform Calculator instance
    recs1 = Records(data=taxrec_df.copy(deep=True),
                    gfactors=growfactors_pre)
    policy1 = Policy(gfactors=growfactors_pre)
    calc1 = Calculator(policy=policy1, records=recs1, consumption=consump)
    while calc1.current_year < start_year:
        calc1.increment_year()
    calc1.calc_all()
    assert calc1.current_year == start_year

    # optionally compute mask
    if mask_computed:
        # create pre-reform Calculator instance with extra income
        recs1p = Records(data=taxrec_df.copy(deep=True),
                         gfactors=growfactors_pre)
        # add one dollar to total wages and salaries of each filing unit
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
        # compute mask that shows which of the calc1 and calc1p results differ
        res1 = results(calc1.records)
        res1p = results(calc1p.records)
        mask = (res1.iitax != res1p.iitax)
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

    # create post-reform Calculator instance
    recs2 = Records(data=taxrec_df.copy(deep=True),
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


def chooser(agg):
    """
    This is a transformation function that should be called on each group.
    It is assumed that the chunk 'agg' is a chunk of the 'mask' column.
    This chooser selects three of those mask indices with the output for
    those three indices being zero and the output for all the other indices
    being one.
    """
    indices = np.where(agg)
    three = 3
    if len(indices[0]) >= three:
        choices = np.random.choice(indices[0],  # pylint: disable=no-member
                                   size=three, replace=False)
    else:
        msg = ('Not enough differences in income tax when adding '
               'one dollar for chunk with name: {}')
        raise ValueError(msg.format(agg.name))
    ans = [1] * len(agg)
    for idx in choices:
        ans[idx] = 0
    return ans


def drop_records(df1, df2, mask):
    """
    Modify df1 and df2 by adding statistical fuzz for data privacy.

    Parameters
    ----------
    df1: Pandas DataFrame
        contains results for the standard plan X and X'.

    df2: Pandas DataFrame
        contains results for the user-specified plan (Plan Y).

    mask: boolean numpy array
        contains info about whether or not each element of X and X' are same

    Returns
    -------
    fuzzed_df1: Pandas DataFrame

    fuzzed_df2: Pandas DataFrame

    Notes
    -----
    This function groups both DataFrames based on the web application's
    income groupings (both weighted decile and income bins), and then
    pseudo-randomly picks three records to 'drop' within each bin.
    We keep track of the three dropped records in both group-by
    strategies and then use these 'flag' columns to modify all
    columns of interest, creating new '_dec' columns for
    statistics based on weighted deciles and '_bin' columns for
    statitistics based on income bins.  Lastly we calculate
    individual income tax differences, payroll tax differences, and
    combined tax differences between the baseline and reform
    for the two groupings.
    """
    # perform all statistics on (Y + X') - X

    # Group first
    df2['mask'] = mask
    df1['mask'] = mask

    df2 = add_weighted_income_bins(df2)
    df1 = add_weighted_income_bins(df1)
    gp2_dec = df2.groupby('bins')

    income_bins = WEBAPP_INCOME_BINS

    df2 = add_income_bins(df2, bins=income_bins)
    df1 = add_income_bins(df1, bins=income_bins)
    gp2_bin = df2.groupby('bins')

    # Transform to get the 'flag' column (3 choices to drop in each bin)
    df2['flag_dec'] = gp2_dec['mask'].transform(chooser)
    df2['flag_bin'] = gp2_bin['mask'].transform(chooser)

    # first calculate all of X'
    columns_to_make_noisy = set(TABLE_COLUMNS) | set(STATS_COLUMNS)
    # these don't exist yet
    columns_to_make_noisy.remove('num_returns_ItemDed')
    columns_to_make_noisy.remove('num_returns_StandardDed')
    columns_to_make_noisy.remove('num_returns_AMT')
    for col in columns_to_make_noisy:
        df2[col + '_dec'] = (df2[col] * df2['flag_dec'] -
                             df1[col] * df2['flag_dec'] + df1[col])
        df2[col + '_bin'] = (df2[col] * df2['flag_bin'] -
                             df1[col] * df2['flag_bin'] + df1[col])

    # Difference in plans
    # Positive values are the magnitude of the tax increase
    # Negative values are the magnitude of the tax decrease
    df2['tax_diff_dec'] = df2['iitax_dec'] - df1['iitax']
    df2['tax_diff_bin'] = df2['iitax_bin'] - df1['iitax']
    df2['payrolltax_diff_dec'] = df2['payrolltax_dec'] - df1['payrolltax']
    df2['payrolltax_diff_bin'] = df2['payrolltax_bin'] - df1['payrolltax']
    df2['combined_diff_dec'] = df2['combined_dec'] - df1['combined']
    df2['combined_diff_bin'] = df2['combined_bin'] - df1['combined']

    return df1, df2


def dropq_summary(df1, df2, mask):
    """
    df1 contains raw results for the standard plan X and X'
    df2 contains raw results the user-specified plan (Plan Y)
    mask is the boolean mask where X and X' match
    """
    # pylint: disable=too-many-locals

    df1, df2 = drop_records(df1, df2, mask)

    # Totals for diff between baseline and reform
    dec_sum = (df2['tax_diff_dec'] * df2['s006']).sum()
    bin_sum = (df2['tax_diff_bin'] * df2['s006']).sum()
    pr_dec_sum = (df2['payrolltax_diff_dec'] * df2['s006']).sum()
    pr_bin_sum = (df2['payrolltax_diff_bin'] * df2['s006']).sum()
    combined_dec_sum = (df2['combined_diff_dec'] * df2['s006']).sum()
    combined_bin_sum = (df2['combined_diff_bin'] * df2['s006']).sum()

    # Totals for baseline
    sum_baseline = (df1['iitax'] * df1['s006']).sum()
    pr_sum_baseline = (df1['payrolltax'] * df1['s006']).sum()
    combined_sum_baseline = (df1['combined'] * df1['s006']).sum()

    # Totals for reform
    sum_reform = (df2['iitax_dec'] * df2['s006']).sum()
    pr_sum_reform = (df2['payrolltax_dec'] * df2['s006']).sum()
    combined_sum_reform = (df2['combined_dec'] * df2['s006']).sum()

    # Create difference tables, grouped by deciles and bins
    diffs_dec = dropq_diff_table(df1, df2,
                                 groupby='weighted_deciles',
                                 res_col='tax_diff',
                                 diff_col='iitax',
                                 suffix='_dec', wsum=dec_sum)

    diffs_bin = dropq_diff_table(df1, df2,
                                 groupby='webapp_income_bins',
                                 res_col='tax_diff',
                                 diff_col='iitax',
                                 suffix='_bin', wsum=bin_sum)

    pr_diffs_dec = dropq_diff_table(df1, df2,
                                    groupby='weighted_deciles',
                                    res_col='payrolltax_diff',
                                    diff_col='payrolltax',
                                    suffix='_dec', wsum=pr_dec_sum)

    pr_diffs_bin = dropq_diff_table(df1, df2,
                                    groupby='webapp_income_bins',
                                    res_col='payrolltax_diff',
                                    diff_col='payrolltax',
                                    suffix='_bin', wsum=pr_bin_sum)

    comb_diffs_dec = dropq_diff_table(df1, df2,
                                      groupby='weighted_deciles',
                                      res_col='combined_diff',
                                      diff_col='combined',
                                      suffix='_dec', wsum=combined_dec_sum)

    comb_diffs_bin = dropq_diff_table(df1, df2,
                                      groupby='webapp_income_bins',
                                      res_col='combined_diff',
                                      diff_col='combined',
                                      suffix='_bin', wsum=combined_bin_sum)

    m1_dec = create_distribution_table(df1, groupby='weighted_deciles',
                                       result_type='weighted_sum')

    m2_dec = dropq_dist_table(df2, groupby='weighted_deciles',
                              result_type='weighted_sum', suffix='_dec')

    m1_bin = create_distribution_table(df1, groupby='webapp_income_bins',
                                       result_type='weighted_sum')

    m2_bin = dropq_dist_table(df2, groupby='webapp_income_bins',
                              result_type='weighted_sum', suffix='_bin')

    return (m2_dec, m1_dec, diffs_dec, pr_diffs_dec, comb_diffs_dec,
            m2_bin, m1_bin, diffs_bin, pr_diffs_bin, comb_diffs_bin,
            dec_sum, pr_dec_sum, combined_dec_sum,
            sum_baseline, pr_sum_baseline, combined_sum_baseline,
            sum_reform, pr_sum_reform, combined_sum_reform)


def dropq_diff_table(df1, df2, groupby, res_col, diff_col, suffix, wsum):
    """
    Create and return dropq difference table.
    """
    # pylint: disable=too-many-arguments,too-many-locals
    if groupby == "weighted_deciles":
        gdf = add_weighted_income_bins(df2, num_bins=10)
    elif groupby == "small_income_bins":
        gdf = add_income_bins(df2, compare_with="soi")
    elif groupby == "large_income_bins":
        gdf = add_income_bins(df2, compare_with="tpc")
    elif groupby == "webapp_income_bins":
        gdf = add_income_bins(df2, compare_with="webapp")
    else:
        err = ("groupby must be either 'weighted_deciles' or "
               "'small_income_bins' or 'large_income_bins' or "
               "'webapp_income_bins'")
        raise ValueError(err)
    # Difference in plans
    # Positive values are the magnitude of the tax increase
    # Negative values are the magnitude of the tax decrease
    df2[res_col + suffix] = df2[diff_col + suffix] - df1[diff_col]
    diffs = means_and_comparisons(res_col + suffix,
                                  gdf.groupby('bins', as_index=False),
                                  wsum + EPSILON)
    sum_row = get_sums(diffs)[diffs.columns]
    diffs = diffs.append(sum_row)  # pylint: disable=redefined-variable-type
    pd.options.display.float_format = '{:8,.0f}'.format
    srs_inc = ["{0:.2f}%".format(val * 100) for val in diffs['perc_inc']]
    diffs['perc_inc'] = pd.Series(srs_inc, index=diffs.index)
    srs_cut = ["{0:.2f}%".format(val * 100) for val in diffs['perc_cut']]
    diffs['perc_cut'] = pd.Series(srs_cut, index=diffs.index)
    srs_change = ["{0:.2f}%".format(val * 100) for val in
                  diffs['share_of_change']]
    diffs['share_of_change'] = pd.Series(srs_change, index=diffs.index)
    # columns containing weighted values relative to the binning mechanism
    non_sum_cols = [x for x in diffs.columns if 'mean' in x or 'perc' in x]
    for col in non_sum_cols:
        diffs.loc['sums', col] = 'n/a'
    return diffs


def dropq_dist_table(resdf, groupby, result_type, suffix):
    """
    Create and return dropq distribution table.
    """
    # pylint: disable=too-many-locals
    res = resdf
    c04470_s = 'c04470' + suffix
    c00100_s = 'c00100' + suffix
    c09600_s = 'c09600' + suffix
    standard_s = 'standard' + suffix
    s006_s = 's006' + suffix
    returns_ided_s = 'num_returns_ItemDed' + suffix
    returns_sded_s = 'num_returns_StandardDed' + suffix
    returns_amt_s = 'num_returns_AMT' + suffix
    res[c04470_s] = res[c04470_s].where(((res[c00100_s] > 0) &
                                         (res[c04470_s] > res[standard_s])), 0)
    res[returns_ided_s] = res[s006_s].where(((res[c00100_s] > 0) &
                                             (res[c04470_s] > 0)), 0)
    res[returns_sded_s] = res[s006_s].where(((res[c00100_s] > 0) &
                                             (res[standard_s] > 0)), 0)
    res[returns_amt_s] = res[s006_s].where(res[c09600_s] > 0, 0)
    if groupby == "weighted_deciles":
        dframe = add_weighted_income_bins(res, num_bins=10)
    elif groupby == "small_income_bins":
        dframe = add_income_bins(res, compare_with="soi")
    elif groupby == "large_income_bins":
        dframe = add_income_bins(res, compare_with="tpc")
    elif groupby == "webapp_income_bins":
        dframe = add_income_bins(res, compare_with="webapp")
    else:
        err = ("groupby must be either 'weighted_deciles' or "
               "'small_income_bins' or 'large_income_bins' or "
               "'webapp_income_bins'")
        raise ValueError(err)
    pd.options.display.float_format = '{:8,.0f}'.format
    if result_type == "weighted_sum":
        dframe = weighted(dframe, [col + suffix for col in STATS_COLUMNS])
        gby_bins = dframe.groupby('bins', as_index=False)
        gp_mean = gby_bins[[col + suffix for col in TABLE_COLUMNS]].sum()
        gp_mean.drop('bins', axis=1, inplace=True)
        sum_row = get_sums(dframe)[[col + suffix for col in TABLE_COLUMNS]]
    elif result_type == "weighted_avg":
        gp_mean = weighted_avg_allcols(dframe,
                                       [col + suffix for col in TABLE_COLUMNS])
        all_sums = get_sums(dframe, not_available=True)
        sum_row = all_sums[[col + suffix for col in TABLE_COLUMNS]]
    else:
        err = ("result_type must be either 'weighted_sum' or "
               "'weighted_avg'")
        raise ValueError(err)
    return gp_mean.append(sum_row)
